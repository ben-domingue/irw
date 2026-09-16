#!/usr/bin/env python3
"""Resolve 2021's surviving [UNDECODED-gNNN] notation, or DESCRIBE what is left.

Two rulings govern this file.

  Mateus, 2026-09-16: "Interpreting equations and so on is not really a font. I
  think there could be some description, analogous to what the accessibility
  booklets do, but make sure it is noted as a description clearly so it does not
  get erroneously computed as item text."

  Ben, #1848 (2026-09-03, applied 2026-09-11): "generated descriptions go in
  `item_text` only, always inline-marked, never in `option_text`" -- because a
  generated `option_text` becomes a label on a response category that someone
  will join to `resp` for distractor analysis.

So: descriptions land in `item_text`, inline-marked. `option_text` markers are
LEFT AS THEY ARE -- neither described nor blanked, since the surrounding option
text is real and blanking it would destroy source content to hide a symbol.

=============================================================================
STEP 1 -- decode what is actually decidable, before describing anything
=============================================================================
17_decode_2021.py already resolved every family whose glyph order was MEASURED
to follow Arial's. What survives as /gNNN is therefore, by construction, from a
family it could NOT map. For most of the surviving gids the only such family in
these four booklets is SymbolMT, and SymbolMT is a solved problem: the rule
derived and cross-validated for 2018 and applied to 2022 is

    code = GID + 29  (GID 3-97)      code = GID + 63  (GID >= 98)

read through the Adobe Symbol encoding (23_decode_symbolmt.py). Every one of
these agrees with what the surrounding text independently requires:

    g3  -> " "   g14 -> "+"   g16 -> "-"   g32 -> "="     (also = Mac order)
    g83 -> "pi"    axis labels pi/2, pi, 3pi/2 where the LEDOR text reads
                   "zero, pi, dois pi e tres pi"          (MT 67990)
    g84 -> "theta" "para o angulo de disparo (θ)"          (CN 85781)
    g111-> "->"    "I2 + 2 e- -> 2 I-"                     (CN 88403)
    g113-> "deg"   "Considere sen 53° = 0,8"               (CN 85781)

THE SCOPING IS MEASURED, NOT ASSUMED (STATUS.md trap 23). This script reads the
/Differences of every font in the booklets and decodes a gid ONLY when the set
of families declaring it, minus the Arial-order families already handled,
is exactly {SymbolMT}. A gid that another unmapped family also declares (g38
is declared by SymbolMT *and* Arial-ItalicMT) is NOT decoded -- it is described.

=============================================================================
STEP 2 -- describe the irreducible remainder, clearly marked
=============================================================================
What is left is MT-Extra, CambriaMath and high Arial gids with no
document-internal evidence anywhere in 46 booklets. Each contiguous run of
markers in `item_text` becomes

    [notação não extraível da fonte original (gerada por IA): <what>]

where <what> is the role the surrounding text forces, or "simbolo nao
identificado" where it forces nothing. The marker is unambiguous, in
Portuguese like the rest of the cell, and states that it is generated -- so it
cannot be mistaken for transcribed item text. Tables touched this way must
carry description_source=partly_generated in provenance.csv.

Usage:
  python3 29_decode_2021_notation.py --items-dir <dir> [--apply]
"""
import argparse, collections, csv, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util
_s = importlib.util.spec_from_file_location("sym", os.path.join(HERE, "23_decode_symbolmt.py"))
sym = importlib.util.module_from_spec(_s); _s.loader.exec_module(sym)

from pypdf import PdfReader

ENEM = os.path.expanduser("~/enem")
BOOKLETS = [
    "ENEM_2021_P1_CAD_09_DIA_1_LARANJA_LEDOR.pdf",
    "ENEM_2021_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf",
    "ENEM_2021_P1_CAD_01_DIA_1_AZUL.pdf",
    "ENEM_2021_P1_CAD_07_DIA_2_AZUL.pdf",
]
# families 17_decode_2021.py measured to follow Arial's order -- it has already
# mapped these, so their gids cannot be what survived
ARIAL_ORDER = {"ArialMT", "Arial-BoldMT"}

MARKER_RUN = re.compile(r"(?:\[UNDECODED-g\d+\]\s*)+")
ONE = re.compile(r"\[UNDECODED-g(\d+)\]")
SCHEMA = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
          "item_text", "correct_response", "option_text", "resp", "item_text_translated",
          "option_text_translated", "instructions_translated", "section_prompt_translated",
          "language", "resp_raw"]

# What the surrounding text forces, per gid. Evidence in the comment; anything
# the context does not force says so instead of inventing a symbol.
DESCRIBE = {
    237: "sinal negativo de carga ou de expoente",   # SO4 2-, Cl-, 10-3, 2 e-
    314: "seta de reação química",                   # H2 + 2 OH- -> 2 H2O + 2 e-
    307: "letra grega phi",                           # potencias de fi: fi2, fi3 ... "fi elevado a 7"
    1859: "símbolo da aceleração da gravidade",      # "g e igual a 10 m/s2"
    2029: "símbolo do módulo da velocidade",         # "velocidade inicial de disparo (v0)"
    4231: "ligatura tipográfica ff",                 # "di[ff]erent" (LC 111852, ingles)
    38: "seta",                                      # "Excrecao -> Radiacao 400 a 500 nm"
    2288: "índice subscrito",                        # "a intensidade do sinal (V EC )"
    34: "símbolo não identificado",                  # MT-Extra, contexto nao decide
    540: "símbolo não identificado",                 # rotulo de diagrama de cores
    1828: "símbolo não identificado",
    3032: "símbolo não identificado",
}
GENERIC = "símbolo não identificado"


def symbolmt_gids():
    """gids whose ONLY non-Arial-order declaring family is SymbolMT."""
    fam = collections.defaultdict(set)
    src = os.path.join(ENEM, "extracted_2021", "PROVAS E GABARITOS")
    seen_files = 0
    for b in BOOKLETS:
        p = os.path.join(src, b)
        if not os.path.exists(p):
            continue
        seen_files += 1
        r = PdfReader(p)
        seen = set()

        def walk(obj):
            try:
                obj = obj.get_object()
            except Exception:
                return
            if id(obj) in seen:
                return
            seen.add(id(obj))
            if isinstance(obj, dict):
                if obj.get("/Type") == "/Font":
                    base = re.sub(r"^[A-Z]{6}\+", "",
                                  str(obj.get("/BaseFont", "?")).lstrip("/"))
                    enc = obj.get("/Encoding")
                    try:
                        enc = enc.get_object()
                    except Exception:
                        pass
                    if isinstance(enc, dict):
                        for x in (enc.get("/Differences") or []):
                            m = re.fullmatch(r"g(\d+)", str(x).lstrip("/"))
                            if m:
                                fam[int(m.group(1))].add(base)
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    walk(v)

        for pg in r.pages:
            walk(pg)
    ok = {g for g, fs in fam.items() if (fs - ARIAL_ORDER) == {"SymbolMT"}}
    return ok, fam, seen_files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    ok, fam, nfiles = symbolmt_gids()
    print(f"  read /Differences from {nfiles} booklet(s); "
          f"{len(fam)} gid(s) declared, {len(ok)} scoped to SymbolMT alone")

    decoded = collections.Counter()
    described = collections.Counter()
    left_in_options = collections.Counter()

    for p in sorted(glob.glob(os.path.join(a.items_dir, "*__items.csv"))):
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        touched = False
        for r in rows:
            # option_text: Ben's rule -- no generated text here. Count and leave.
            for g in ONE.findall(r.get("option_text") or ""):
                left_in_options[int(g)] += 1

            v = r.get("item_text") or ""
            if "[UNDECODED-" not in v:
                continue

            # step 1: decode the SymbolMT-scoped gids in place
            def dec(m):
                g = int(m.group(1))
                if g not in ok:
                    return m.group(0)
                code = sym.gid_to_code(g)
                ch = sym.SYMBOL.get(code) if code else None
                if ch is None:
                    return m.group(0)
                decoded[g] += 1
                return ch
            v = ONE.sub(dec, v)

            # step 2: describe whatever is still a marker, one note per run
            def desc(m):
                gids = [int(x) for x in ONE.findall(m.group(0))]
                whats = []
                for g in gids:
                    w = DESCRIBE.get(g, GENERIC)
                    if w not in whats:
                        whats.append(w)
                    described[g] += 1
                # The marker token must be EXACTLY "(gerada por IA)":
                # check_provenance.R greps for \((AI-generated|gerada por IA)\)
                # and an inline note that merely contains those words inside a
                # longer parenthetical does not match, so the table fails the
                # #1848 generated-text gate. Same wording as 2023's.
                return ("[notação não extraível da fonte original "
                        "(gerada por IA): " + "; ".join(whats) + "]")
            v2 = MARKER_RUN.sub(desc, v)

            if v2 != (r.get("item_text") or ""):
                r["item_text"] = v2
                touched = True
        if touched:
            print(f"  {os.path.basename(p)}: updated")
            if a.apply:
                with open(p, "w", newline="", encoding="utf-8") as fh:
                    w = csv.DictWriter(fh, SCHEMA)
                    w.writeheader()
                    for r in rows:
                        w.writerow({k: r.get(k, "") for k in SCHEMA})

    print(f"  DECODED   {sum(decoded.values())} marker(s): "
          f"{ {g: f'{sym.SYMBOL.get(sym.gid_to_code(g))!r} x{n}' for g, n in sorted(decoded.items())} }")
    print(f"  DESCRIBED {sum(described.values())} marker(s) over "
          f"{len(described)} gid(s): { {g: n for g, n in sorted(described.items())} }")
    if left_in_options:
        print(f"  left in option_text (Ben's rule; disclose): {dict(left_in_options)}")
    if not a.apply:
        print("  DRY RUN -- nothing written (pass --apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
