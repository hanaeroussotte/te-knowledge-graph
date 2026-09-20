#!/usr/bin/env python3
"""
extract_lit.py — rule-based gene -> transposable-element relation extraction from abstracts.

Deterministic, no LLM, no network. Written so the literature tier can be rebuilt on any
machine at any time, and so its behaviour is auditable line by line rather than being a
model's opinion. Concordance against an LLM-labelled subset is reported separately.

Design:
  gene dictionary   protein-coding symbols from GENCODE, minus an English-word blocklist
  TE dictionary     RepeatMasker subfamily/family names plus the aliases the literature
                    actually uses (LINE-1, L1, HERV-K, ERV, Alu, SVA, ...)
  candidate         gene symbol and TE term co-occurring in the SAME sentence
  direction         nearest directional cue in that sentence, mapped to the loss frame
  species gate      abstract must look human and must not look like a fly/plant/yeast paper

Output: one row per (pmid, gene, te_term) with direction, cue, and the sentence as evidence.
"""
from __future__ import annotations
import json, re, sys, collections
from pathlib import Path

# --- symbols that are also ordinary words, abbreviations, or units. Case-sensitive match
#     is not enough: abstracts shout acronyms. These would otherwise dominate the output.
BLOCK = {
    "DNA","RNA","MRNA","CDNA","PCR","QPCR","RT","ATP","GTP","ADP","NAD","CAN","SET","MAX",
    "REST","AIR","TIP","ICE","MASS","CAMP","ACE","CAT","COPE","SHE","MET","WAS","APP","ARC",
    "BAD","BID","CAP","CAR","CASK","CHIP","CS","DDT","FACT","FAT","GAN","HR","IMPACT","LARGE",
    "LIME","LINE","MICE","MIR","MS","NHS","NODAL","PIGS","PLAN","POLE","RAN","SARS","SDS",
    "SPARC","STAR","TANK","TEC","TRAP","US","WARS","AGO","AS","AT","BY","IN","IS","IT","NO",
    "ON","OR","SO","TO","UP","WE","ALL","AND","FOR","NOT","THE","VS","ELISA","SIRNA","SHRNA",
    "CRISPR","CAS9","GFP","HIV","HTLV","EBV","HBV","HCV","SIV","MMTV","MLV","IAP","LTR","ORF",
    "GAG","POL","ENV","TE","TES","SINE","SINES","LINES","ERV","ERVS","HERV","HERVS","ALU",
    "SVA","L1","L1S","AID","COX","CRP","ER","PR","HR","OS","PFS","CI","OR","RR","HR",
}
# --- TE vocabulary. Keys are canonical graph nodes; values are surface forms in text.
TE_ALIASES = {
    "L1":        [r"LINE-?1", r"\bL1\b", r"\bL1s\b", r"long interspersed (?:nuclear )?element-?1?",
                  r"\bL1HS\b", r"\bL1PA\d\b"],
    "Alu":       [r"\bAlu\b", r"\bAlus\b", r"\bAluY[a-z0-9]*\b", r"\bAluS[a-z0-9]*\b"],
    "SVA":       [r"\bSVA\b", r"\bSVA_[A-F]\b"],
    "HERV-K":    [r"HERV-?K", r"\bHML-?2\b", r"\bLTR5_?Hs\b", r"\bERVK\b"],
    "HERV-W":    [r"HERV-?W", r"\bsyncytin-?1?\b", r"\bMSRV\b"],
    "HERV-H":    [r"HERV-?H", r"\bLTR7\b"],
    "HERV-E":    [r"HERV-?E"],
    "HERV-L":    [r"HERV-?L", r"\bMLT2\b"],
    "HERV":      [r"\bHERVs?\b", r"human endogenous retrovirus(?:es)?"],
    "ERV":       [r"\bERVs?\b", r"endogenous retrovirus(?:es)?"],
    "LTR":       [r"\bLTR retrotransposons?\b"],
    "TE_generic":[r"\btransposable elements?\b", r"\bretrotransposons?\b", r"\bretroelements?\b",
                  r"\btransposons?\b", r"\brepetitive elements?\b"],
}
# --- directional cues, expressed in the LOSS frame used by the graph schema.
#     "up"   : losing the gene raises TE expression (the gene silences the TE)
#     "down" : losing the gene lowers TE expression (the gene is required for TE expression)
CUES_UP = [r"silenc\w*", r"repress\w*", r"restrict\w*", r"suppress\w*", r"inhibit\w*",
           r"represses", r"downregulat\w*", r"down-regulat\w*", r"limits?", r"restrain\w*",
           r"guards? against", r"protects? against", r"controls?"]
CUES_DOWN = [r"required for", r"necessary for", r"activat\w*", r"promot\w*", r"induc\w*",
             r"upregulat\w*", r"up-regulat\w*", r"drives?", r"enhanc\w*", r"facilitat\w*",
             r"stimulat\w*", r"needed for"]
# --- loss-of-function language: presence raises confidence that a causal test was done
PERTURB = [r"knock-?down", r"knock-?out", r"knock-?ing down", r"\bKD\b", r"\bKO\b", r"depleti\w*",
           r"deplet\w*", r"silencing of", r"siRNA", r"shRNA", r"CRISPR", r"null", r"deficien\w*",
           r"mutant", r"overexpress\w*", r"ectopic expression"]
# --- species gating
HUMAN_HINT = [r"\bhuman\b", r"\bpatients?\b", r"\bHeLa\b", r"\bK562\b", r"\bHepG2\b", r"\bHEK293\b",
              r"\bhESCs?\b", r"\biPSCs?\b", r"\bPBMCs?\b", r"\bHomo sapiens\b", r"\bhuman cells?\b"]
NONHUMAN_HINT = [r"\bDrosophila\b", r"\bmelanogaster\b", r"\bArabidopsis\b", r"\bmaize\b", r"\bZea\b",
                 r"\brice\b", r"\byeast\b", r"\bcerevisiae\b", r"\bC\. elegans\b", r"\bzebrafish\b",
                 r"\bTy1\b", r"\bgypsy\b", r"\bflamenco\b", r"\bIAP\b", r"\bmouse\b", r"\bmurine\b",
                 r"\bmice\b", r"\bmusculus\b", r"\bplant\b", r"\bfungal\b", r"\bbacteri\w*"]

rx = lambda pats: re.compile("|".join(pats), re.I)
RX_UP, RX_DOWN, RX_PERT = rx(CUES_UP), rx(CUES_DOWN), rx(PERTURB)
RX_HUMAN, RX_NONHUMAN = rx(HUMAN_HINT), rx(NONHUMAN_HINT)
TE_RX = {k: re.compile("|".join(v)) for k, v in TE_ALIASES.items()}
SENT = re.compile(r"(?<=[.;])\s+(?=[A-Z0-9])")


def load_gene_symbols(gtf: Path) -> set[str]:
    """Protein-coding gene symbols from a GENCODE GTF."""
    syms, seen = set(), set()
    pat = re.compile(r'gene_name "([^"]+)".*gene_type "([^"]+)"')
    alt = re.compile(r'gene_type "([^"]+)".*gene_name "([^"]+)"')
    with open(gtf) as fh:
        for line in fh:
            if line.startswith("#") or "\tgene\t" not in line:
                continue
            m = pat.search(line) or None
            if m:
                name, typ = m.group(1), m.group(2)
            else:
                m = alt.search(line)
                if not m:
                    continue
                typ, name = m.group(1), m.group(2)
            if typ != "protein_coding":
                continue
            if name in seen:
                continue
            seen.add(name)
            if len(name) >= 3 and name.upper() not in BLOCK and re.fullmatch(r"[A-Z][A-Z0-9\-]{2,}", name):
                syms.add(name)
    return syms


def species_of(abstract: str) -> str:
    h, n = len(RX_HUMAN.findall(abstract)), len(RX_NONHUMAN.findall(abstract))
    if h and h >= n:
        return "human"
    if n > h:
        return "nonhuman"
    return "unclear"


def extract(article: dict, symbols: set[str]) -> list[dict]:
    text = f"{article.get('title') or ''}. {article.get('abstract') or ''}"
    sp = species_of(text)
    out = []
    for sent in SENT.split(text):
        tes = [k for k, r in TE_RX.items() if r.search(sent)]
        if not tes:
            continue
        # candidate gene tokens in this sentence, checked against the dictionary
        toks = set(re.findall(r"\b[A-Z][A-Z0-9\-]{2,}\b", sent))
        genes = sorted(toks & symbols)
        if not genes:
            continue
        up, down = bool(RX_UP.search(sent)), bool(RX_DOWN.search(sent))
        direction = "up" if (up and not down) else "down" if (down and not up) else "unclear"
        cue_m = RX_UP.search(sent) or RX_DOWN.search(sent)
        for g in genes:
            for te in tes:
                out.append({
                    "pmid": article["pmid"], "doi": article.get("doi"),
                    "year": article.get("year"), "gene": g, "te": te,
                    "effect_of_loss": direction,
                    "cue": cue_m.group(0).lower() if cue_m else None,
                    "perturbation_language": bool(RX_PERT.search(sent)),
                    "species": sp,
                    "sentence": sent.strip()[:400],
                })
    return out


def main():
    arts = json.load(open("handoff/pubmed_abstracts.json"))
    symbols = load_gene_symbols(Path("refs/gencode.v44.gtf"))
    print(f"gene dictionary: {len(symbols):,} symbols", file=sys.stderr)
    rows = [r for a in arts for r in extract(a, symbols)]
    json.dump(rows, open("handoff/lit_rule_extractions.json", "w"))
    c = collections.Counter
    print(f"abstracts: {len(arts):,}  raw relations: {len(rows):,}", file=sys.stderr)
    print("species:", dict(c(r["species"] for r in rows)), file=sys.stderr)
    print("direction:", dict(c(r["effect_of_loss"] for r in rows)), file=sys.stderr)


if __name__ == "__main__":
    main()
