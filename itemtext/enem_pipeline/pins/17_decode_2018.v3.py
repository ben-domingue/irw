#!/usr/bin/env python3
"""Decode the 2018 ENEM booklet PDFs, whose text extracts as a byte-shifted cipher.

=============================================================================
THE DEFECT, DIAGNOSED FROM THE PDF OBJECTS (not guessed from the text)
=============================================================================

2018's P1 booklets set most of their body text in a *second* copy of Arial that
is embedded as a **Type0 / Identity-H CID font with no /ToUnicode**:

    155 0 obj << /Subtype /Type0 /BaseFont /ArialMT-Identity-H
                 /Encoding /Identity-H /DescendantFonts [181 0 R] >>
    181 0 obj << /Subtype /CIDFontType0 /BaseFont /ANGFDB+ArialMT ... >>

With /Identity-H the byte pairs in the content stream ARE glyph ids (CIDs), and
with no /ToUnicode there is nothing in the file that says what those glyphs
mean. The embedded CFF is CID-keyed with ROS (Adobe, Identity, 0) and a charset
of bare `cid00003`, `cid00004`, ... -- i.e. it carries no glyph names either.
The TrueType-flavoured subsets have had their `cmap` table stripped entirely.

    ==> The PDF contains NO glyph->Unicode information whatsoever.

That is why pypdf, pymupdf AND Ghostscript txtwrite all produce the same
garbling: every one of them falls back to treating the CID as a character code.
The defect is in the PDF. It cannot be fixed by changing extractor.

The CIDs are Arial's *native* glyph ids. Arial's glyph order is the standard
Macintosh glyph ordering (fontTools.ttLib.standardGlyphOrder), so:

    CID   3        -> space          (hence the tell-tale \\x03 for every space)
    CID  19.. 28   -> '0'..'9'
    CID  36.. 61   -> 'A'..'Z'
    CID  68.. 93   -> 'a'..'z'

Over CID 3..97 that ordering is exactly ASCII shifted by 29, which is the
"uniform +29 offset" the first diagnosis reported:  chr(cid + 29).
Above CID 97 the glyphs are accents/ligatures/punctuation and the relation is
NOT arithmetic -- it needs the table below.

Independent corroboration from the PDF's own /W (width) array, which is keyed
by CID and needs no font knowledge at all:

    /W [ 3 4 278 ... 20 28 556 ... 36 37 667 ... 68 69 556 ... ]
        CID 3   width 278 = Arial space
        CID 19-28 width 556 = Arial digits
        CID 36  width 667 = Arial 'A'
        CID 68  width 556 = Arial 'a'

=============================================================================
THE ONE DEVIATION: +1 FROM CID 172 ONWARD
=============================================================================

Arial's glyph order tracks the standard Macintosh ordering up to index 171 and
then runs one *behind* it -- Arial has no `nonbreakingspace` glyph at Mac index
172, so everything above it slides down by one. Both halves of that claim are
forced by the booklet text; nothing here is assumed:

  Below 172, CID == Mac index (no offset):
    CID 131 -> degree          "tem medida de 170°."            (day 2 p22)
    CID 135 -> bullet          "• " list markers                (day 1 p3)
    CID 158 -> ordmasculine    "LC - 1º dia | Caderno 9 ..."    (running head)
    CID 162 -> questiondown    "¿Qué es la X Solidaria?"        (day 1 p3, ES)
    CID 168 -> Delta           "O (l)      ∆"                   (day 2 p7)

  From 172 up, CID == Mac index - 1 (the +1 offset applies on decode):
    CID 172 -> Agrave          "Às segundas-feiras..."      Mac 173
    CID 173 -> Atilde          "CARTÃO-RESPOSTA"            Mac 174
    CID 174 -> Otilde          "QUESTÕES" (&$'(512 '( 48(67®(6)  Mac 175
    CID 177 -> endash          "...sem parar – "            Mac 178
    CID 178 -> emdash          "populações — denominadas"    Mac 179
    CID 179 -> quotedblleft    "simply “sit-and-get”"       Mac 180
    CID 180 -> quotedblright   "simply “sit-and-get”"       Mac 181
    CID 181 -> quoteleft       "eu falo de ‘acué’"          Mac 182
    CID 182 -> quoteright      "they say it’s time"         Mac 183
    CID 191 -> fi (ligature)   "Confira" (&RQ¿UD)           Mac 192
    CID 192 -> fl (ligature)   "influentes" (LQÀXHQWHV)     Mac 193
    CID 200 -> Aacute          "Árido, com déficit hídrico" Mac 201
    CID 203 -> Iacute          "Pacífico, Índico"           Mac 204

Note CID 191 = `fi` is the mapping the first diagnosis reported; it is the
observation that pins the deviation, because the plain Mac ordering puts
`guilsinglright` there and `fi` one slot later.

The accent mappings the first diagnosis reported all fall in the un-offset
region and are reproduced exactly by the Mac ordering (re-verified here, not
assumed):

    CID 109 atilde ã | 111 ccedilla ç | 112 eacute é | 114 ecircumflex ê
    CID 116 iacute í | 120 ntilde  ñ | 125 otilde  õ | 191 fi (see above)

Worked end-to-end checks against the three strings in the original diagnosis:

    'SomR\\x03HVSDQKRO\\x0c'                  -> 'pção espanhol)'
    'G*DPDPHQRUTXHG%HWDPHQRUTXHG$OSKD' -> 'dGamamenorquedBetamenorquedAlpha'
    '&RQ¿UD\\x03VH\\x03D\\x03TXDQWLGDGH'      -> 'Confira se a quantidade'

(The middle one prints without spaces because that span sets its inter-word
gaps with positioning operators rather than a space glyph; the letters are
right, and the extractor re-inserts the gaps from geometry.)

=============================================================================
HOW WE DETECT WHICH SPANS ARE SHIFTED  --  we don't guess, we ask the PDF
=============================================================================

The shift applies to SOME runs only, and the boundary falls *mid-word*:
"(opção espanhol)" extracts as '(o' + 'SomR\\x03HVSDQKRO\\x0c', clean '(o'
followed by a shifted tail. That is because the page switches font resource
the instant it needs a glyph outside the non-embedded WinAnsi Arial's coverage.
No character-class or word-level rule on the extracted *text* can place that
boundary reliably, because the shifted alphabet overlaps the clean one (a
shifted lowercase letter is an uppercase 'D'-']', and shifted accents are
lowercase letters).

So the primary path does not work on text at all. `repair_pdf()` walks the PDF
object graph, finds every Type0 font whose /Encoding is /Identity-H and which
has no /ToUnicode, and injects a /ToUnicode CMap built from the tables below.
The detector is therefore the PDF's own font object: exact, per-span, by
construction, with no heuristic. After repair, pypdf (and pymupdf, and gs) all
extract 2018 the same way they extract every other year, so the PINNED parser
12_parse_booklet_pdf.v2.py runs over it unmodified and its line and item
boundaries cannot drift.

`decode_text()` is the secondary, text-level path required by the brief for
already-extracted text. It is a heuristic (see its docstring) and its measured
accuracy is reported separately by 18_validate_decode.py; prefer repair_pdf().

=============================================================================
NOT RECOVERABLE FROM THE STANDARD ORDERING
=============================================================================

Three of the six Identity-H base fonts are not Arial and do not share its glyph
order. They carry 17 CIDs between them, all mathematical notation in MT/CN.
Those resolved by context are tabled below; SYMBOL CID 32 and the two
EuclidExtra CIDs are flagged UNRESOLVED and left as U+FFFD so they are visible
rather than silently wrong.  See the report.

Usage:
    # primary: rewrite the PDF with ToUnicode CMaps injected
    python3 17_decode_2018.py repair <in.pdf> <out.pdf>
    # secondary: decode already-extracted text
    python3 17_decode_2018.py text <in.txt> [-o out.txt]
    # show the table
    python3 17_decode_2018.py table
"""
import re
import sys
import unicodedata

from fontTools.agl import toUnicode
from fontTools.ttLib.standardGlyphOrder import standardGlyphOrder as _MAC

# --------------------------------------------------------------------------
# THE DECODE TABLE.  One place, as the brief requires.
# --------------------------------------------------------------------------
# Arial family (ArialMT, Arial-BoldMT, Arial-ItalicMT, Arial-BoldItalicMT).
# Built from the standard Macintosh glyph ordering with the +1-from-172 rule
# evidenced in the module docstring.  Generated rather than hand-typed so the
# ASCII range cannot drift from chr(cid+29).
_MAC_SKIP_AT = 172          # Arial lacks Mac index 172 (nonbreakingspace)


def _arial_table():
    t = {}
    for cid in range(1, 258):
        mac = cid + 1 if cid >= _MAC_SKIP_AT else cid
        if mac >= len(_MAC):
            continue
        name = _MAC[mac]
        if name in (".notdef", ".null", "nonmarkingreturn"):
            continue
        u = toUnicode(name)
        if u:
            t[cid] = u
    # Sanity: over CID 3..97 the Mac ordering must be exactly ASCII+29.
    for cid in range(3, 98):
        assert t[cid] == chr(cid + 29), (cid, t[cid])
    return t


def _delig(t):
    """Decompose the f-ligatures ONLY.

    AGL resolves the glyph names `fi`/`fl` to the single codepoints U+FB01/
    U+FB02. Those are typographic renderings of two letters, not letters, and
    leaving them in place makes "confira" extract as "conﬁra" -- which fails
    every word list, breaks search, and would ship a non-word into item_text.
    The validation harness caught exactly this: `conﬁra`, `ﬁnais`, `deﬁnitivo`,
    `caligraﬁa`, `ﬂexão` were the five commonest unknown tokens.

    Only U+FB00..U+FB06 are touched. A blanket NFKC would also destroy real
    distinctions the booklets rely on -- º -> o (the "1º dia" running head),
    ¹ -> 1, ½ -> 1/2, µ -> Greek mu -- so it is not used.
    """
    return {c: (unicodedata.normalize("NFKD", u) if len(u) == 1 and
                "\ufb00" <= u <= "\ufb06" else u) for c, u in t.items()}


ARIAL_CID = _delig(_arial_table())
# Beyond the 258-glyph standard ordering, resolved by context:
# CID 237: the +1 rule gives Mac 238 = `thorn` (th), but every occurrence in
# the four booklets is a MINUS. So a SECOND glyph is missing from Arial's order
# somewhere between Mac 204 -- the highest anchor verified above, CID 203 =
# Iacute in "Pacifico, Indico" -- and Mac 239, making the offset +2 by here.
# Rather than guess which glyph, CID 237 is overridden explicitly. Evidence:
#     "... iguais a -0,44 volt"                        (day 2 LEDOR p11)
#     "Densidade (g mL-1)"  "Calor de combustao (kcal g-1)"  (day 2 AZUL p1)
#     "e-", "I-", "I3-" in the solar-cell diagram      (day 2 AZUL p8)
# It is the plain minus, not a superscript form: the raising in "g mL-1" is
# done by the PDF text state (size + rise) and the "1" beside it is an
# ordinary digit, while "iguais a -0,44 volt" sits on the baseline.
#
# This override is SUFFICIENT, not a partial patch: CID 237 is the ONLY CID
# above 203 that occurs anywhere in the four P1 booklets. The full inventory,
# read out of each embedded CFF charset rather than guessed, is
#   1, 3..97, 100, 101, 105..107, 109, 111..114, 116, 117, 120, 121, 123..126,
#   129, 131, 135, 143, 158, 162, 168, 172..174, 177..182, 191, 192, 200, 203,
#   237, 314, 525   (plus the non-Arial fonts, tabled separately below).
# Every other used CID lies inside the region pinned by evidence.
ARIAL_CID[237] = "\u2212"   # minus -- see the note above
ARIAL_CID[525] = "Ω"   # Omega. Evidence: a table header "R (Ω)" repeated
                            # five times, day 2 AZUL p6 -- resistance in ohms.
ARIAL_CID[314] = "\u2192"  # rightarrow. RESOLVED: all 5 occurrences are the
                            # arrow of a chemical equation --
                            #   "C6H12O6 (s) + 6 O2 (g) -> 6 CO2 (g) + ..."
                            #   "TiO2|S + hv -> TiO2|S* (1)"
                            #   "TiO2|S* -> TiO2|S+ + e-"
                            #   "1/2 I3- + e- -> ... I-"
                            #   "TiO2|S+ + I- -> TiO2|S + ..."
                            # all day 2 AZUL pp.1/8. Beyond the 258-glyph
                            # standard ordering, so context is the only
                            # evidence available -- but 5/5 are reaction
                            # arrows and nothing else fits.
ARIAL_CID.pop(1, None)      # Mac 1 = .null; never a character.

# SymbolMT. Its glyph order mirrors the Symbol character set, which over the
# low range coincides with ASCII+29 the same way Arial's does. Every entry
# below is pinned by a printed formula, quoted in the comment.
SYMBOL_CID = {
    3:   " ",        # inter-word space, e.g. "0 ≤ y ≤ 10"
    14:  "+",        # "0 ≤ x + y ≤ 10"                     (day 2 AZUL p20 opt D)
    16:  "−",   # minus: "−6", "−5"                    (day 2 AZUL p16)
    19:  "0",        # "≤ 10"  (CID 20 then CID 19)         (day 2 AZUL p20)
    20:  "1",        # ditto
    17:  ".",        # period, used as a multiplication dot in stacked fractions.
                     # RESOLVED (ENEM 2016 day 2, the sound-intensity item):
                     #   A: 500 . 81 / A . D2     B: 500 . A / D2
                     #   C: 500 . D2 / A          D: 500 . A . D2 / 81
                     # Pinned three ways: (a) it sits between two CIDs evidenced
                     # in 2018 -- 16 = minus ("-6","-5") and 19 = zero -- so the
                     # Symbol order fixes 17; (b) the font's own /W array reads
                     # `16 [549 250]`, and Symbol's minus is 549 while its period
                     # is 250; (c) the same GID->code rule reproduces all 13 of
                     # the 2018 SymbolMT entries and all 13 of 2022's opaque
                     # /gNNN names. Not present in 2018; carried here because the
                     # table is shared across years.
    31:  "<",
    33:  ">",        # "X > 1 500."                         (day 2 AZUL p26 opt A)
    83:  "π",   # pi: "Considere o valor de π com aproximação"; "4π"
    100: "≤",   # ≤ : "0 ≤ x ≤ 10"                     (day 2 AZUL p20 opt C)
    116: "≥",   # ≥ : "com n ≥ 2"                      (day 2 AZUL p21)
    117: "×",   # × : "n × n", "6 × 6", "9 × 9"         (day 2 AZUL p21)
    143: "∈",   # ∈ : "(x ; y) ∈ ℝ × ℝ"                (day 2 AZUL p20)
    32:  "=",        # equal. RESOLVED: all 11 occurrences in the corpus read
                     # as '=' and there is no counterexample --
                     #   "ligacoes N=N"  (azo double bond, CN options B and E)
                     #   "A VA = 0; VB > 0"        "matriz A = [aij]"
                     #   "aii = 0"                 "FC = FA < FB"
                     #   "r = 2"                   "Inclinacao = 20%"
                     #   "no tempo t = 0"          "entre t = 0 e tf"
                     # all in day 2 AZUL. This is the plain Symbol glyph order
                     # (index 32 = equal) with NO offset: unlike Arial,
                     # SymbolMT does not deviate. An earlier reading of this
                     # CID as a math thin space came from pymupdf attributing
                     # adjacent spans differently; pypdf, which is what the
                     # parser actually uses, shows '=' in all 11 cases and the
                     # other three booklets use the CID not at all.
}

# EuclidExtra: doublestruck math letters. "(x ; y) ∈ ℝ × ℝ" shows CID 96 where
# ℝ belongs, but 96 appears twice against one ℝ-pair and CID 1 once, so the
# pairing is not determined by the one occurrence available. Both UNRESOLVED.
EUCLID_CID = {96: "\u211d",   # doublestruck R. "pares ordenados (x ; y) in R x R"
                              # (day 2 AZUL p20). Mathematically forced, but it
                              # rests on ONE sentence -- flagged in the report.
              1: "�"}      # UNRESOLVED. Appears once, between the two R
                              # glyphs, so its role is not determined by the
                              # single occurrence available.

# TimesNewRomanPS-ItalicMT: a single CID, one occurrence, no usable context.
TIMES_CID = {542: "\u03bd"}   # Greek nu. RESOLVED: "a energia luminosa (hv)"
                              # and "TiO2|S + hv -> TiO2|S*", day 2 AZUL p8 --
                              # h-nu is the photon energy, and the font is the
                              # italic used for maths variables. 2 occurrences.

FAMILY_TABLES = [
    (re.compile(r"Arial", re.I),               ARIAL_CID),
    (re.compile(r"Symbol", re.I),              SYMBOL_CID),
    (re.compile(r"Euclid", re.I),              EUCLID_CID),
    (re.compile(r"Times", re.I),               TIMES_CID),
]

UNRESOLVED = "�"


# --------------------------------------------------------------------------
# THE ASCII OFFSET IS NOT A CONSTANT -- derive it, never assume Arial's 29.
# --------------------------------------------------------------------------
# Over its printable-ASCII run every one of these fonts maps CID -> character
# by a single additive offset, but the offset is a property of the FONT, not of
# the defect: it equals 32 - (the glyph id of `space`), i.e. it counts how many
# glyphs the font puts before `space`.
#
#   Arial / SymbolMT   space at GID 3  (.notdef, .null, nonmarkingreturn) -> 29
#   MyriadPro-Regular  space at GID 1  (.notdef only)                     -> 31
#
# Assuming 29 everywhere is a real bug: it silently shifts MyriadPro text by
# two characters, which still looks like letters. Found in ENEM 2015, whose
# booklets carry a MyriadPro-Regular Identity-H subset alongside the Arial one.
#
# `space` is always the lowest CID in a subset of any text font, because it is
# the first printable glyph in every one of these orders, so min(subset CIDs)
# identifies it without parsing the font program. Corroborated independently in
# 2015 Caderno7_Azul_Dom: the MyriadPro subset's CIDs are
# [1, 13, 14, 15, 34, 36, 38, 45, ...] (min 1 -> offset 31) and the resulting
# text reads correctly --
#     '\x017BDJOF\x0eTF\x01DPOUS' -> ' Vacine-se contr'
#     CID 1 -> space, 55 -> 'V', 66 -> 'a', 14 -> '-', 79 -> 'n'
# whereas Arial's 29 would have produced ' Tacgme-qc apmrq'.
DEFAULT_ASCII_OFFSET = 29


# ---------------------------------------------------------------- MyriadPro
# The ten CIDs above MyriadPro's ASCII run, which this module used to leave as
# U+FFFD "rather than guessed". They are now RESOLVED, because the words they
# sit inside admit exactly one reading. Every entry below is attested by at
# least one complete Portuguese word from the 2015 day-2 booklet, most by
# several, and the whole set was found together in one public-health poster
# (2015 LC item 6830):
#
#   116 -> bullet    the list marker on "* Use agua tratada", "* Lave SEMPRE"
#   200 -> a-acute   "Egua"=agua, "necessEria"=necessaria, "mEscaras"=mascaras
#   203 -> a-grave   "quanto E restricao" = quanto a restricao
#   205 -> a-tilde   "restriIIo"=restricao, "mIos"=maos, "proteIIo"=protecao
#   206 -> c-cedilla "recomendaIUes", "restriIIo", "proteIIo", "secreIUes"
#   207 -> e-acute   "mIdico" = medico
#   216 -> o-acute   "apOs usar o toalete" = apos
#   220 -> o-tilde   "recomendaIUes"=recomendacoes, "secreIUes"=secrecoes
#   222 -> u-acute   "saUde" = saude
#   246 -> fi        "certiFque-se"=certifique-se, "proFssional"=profissional
#
# WHY THIS MATTERS AND WHY THE OLD DEFAULT WAS WORSE THAN IT LOOKED. Leaving
# them unresolved did not produce a visible gap in a decorative glyph: it
# deleted LETTERS FROM WORDS, so the shipped text read "Use \ufffdgua tratada
# ... recomenda\ufffd\ufffdes quanto \ufffd restri\ufffd\ufffdo". It was
# written up as "decorative bullet glyphs" for three sessions because only the
# bullet was ever looked at. One of the ten (116) is decorative; nine are not.
MYRIAD_CID = {
    116: "\u2022", 200: "\u00e1", 203: "\u00e0", 205: "\u00e3",
    206: "\u00e7", 207: "\u00e9", 216: "\u00f3", 220: "\u00f5",
    222: "\u00fa", 246: "fi",
}



def derive_ascii_offset(cids):
    """32 - GID(space), taken as 32 - min(subset CID). None if undecidable."""
    usable = [c for c in cids if c > 0]
    if not usable:
        return None
    off = 32 - min(usable)
    # A sane offset puts the subset's own CIDs inside printable ASCII or the
    # accent range just above it; anything else means `space` is not the
    # minimum and the caller should fall back rather than shift blindly.
    return off if 20 <= off <= 40 else None


def ascii_table(offset):
    """CID -> char over the printable-ASCII run only, for an untabled font."""
    return {c: chr(c + offset) for c in range(32 - offset, 127 - offset)}


def subset_cids_from_W(w):
    """The CIDs a CIDFont actually carries, read from its /W array.

    /W is [ c_first c_last width | c [w w w ...] ]*. This needs no font-program
    parsing and is present in every one of these fonts.
    """
    out, i = set(), 0
    w = list(w)
    while i < len(w):
        try:
            a = int(w[i])
        except (TypeError, ValueError):
            break
        if i + 1 < len(w) and not isinstance(w[i + 1], (int, float)) and hasattr(w[i + 1], "__iter__"):
            out.update(range(a, a + len(list(w[i + 1]))))
            i += 2
        elif i + 2 < len(w):
            try:
                b = int(w[i + 1])
            except (TypeError, ValueError):
                break
            out.update(range(a, b + 1))
            i += 3
        else:
            break
    return out


def table_for(basefont):
    """Pick the CID->Unicode table for a /BaseFont name (subset tag stripped)."""
    name = basefont.split("+")[-1]
    for rx, tbl in FAMILY_TABLES:
        if rx.search(name):
            return tbl
    return None


# --------------------------------------------------------------------------
# PRIMARY PATH: inject /ToUnicode so every extractor reads 2018 correctly.
# --------------------------------------------------------------------------
_CMAP_HEAD = """/CIDInit /ProcSet findresource begin
12 dict begin
begincmap
/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def
/CMapName /Adobe-Identity-UCS def
/CMapType 2 def
1 begincodespacerange
<0000> <FFFF>
endcodespacerange
"""
_CMAP_TAIL = """endcmap
CMapName currentdict /CMap defineresource pop
end
end
"""


def build_tounicode(tbl):
    """Build a ToUnicode CMap program for a {cid: str} table."""
    items = sorted(tbl.items())
    out = [_CMAP_HEAD]
    for i in range(0, len(items), 100):
        chunk = items[i:i + 100]
        out.append("%d beginbfchar\n" % len(chunk))
        for cid, s in chunk:
            hexs = "".join("%04X" % o for ch in s for o in (ord(ch),))
            out.append("<%04X> <%s>\n" % (cid, hexs))
        out.append("endbfchar\n")
    out.append(_CMAP_TAIL)
    return "".join(out)


def repair_pdf(src, dst, verbose=True):
    """Inject a /ToUnicode CMap into every Identity-H CID font that lacks one.

    Returns a list of (basefont, n_cids, action) for reporting. This is the
    exact detector: a span is shifted iff its font is one of these objects.
    """
    import pikepdf
    pdf = pikepdf.open(src)
    report = []
    done = set()
    for obj in pdf.objects:
        try:
            if obj.get("/Type") != "/Font" or obj.get("/Subtype") != "/Type0":
                continue
        except (AttributeError, TypeError):
            continue
        enc = obj.get("/Encoding")
        if str(enc) != "/Identity-H":
            continue
        if "/ToUnicode" in obj:
            report.append((str(obj.get("/BaseFont")), 0, "already had ToUnicode"))
            continue
        desc = obj.get("/DescendantFonts")
        base = str(desc[0].get("/BaseFont")) if desc else str(obj.get("/BaseFont"))
        tbl = table_for(base)
        cids = set()
        if desc:
            try:
                cids = subset_cids_from_W(desc[0].get("/W") or [])
            except Exception:
                cids = set()
        off = derive_ascii_offset(cids)
        if tbl is None:
            # An untabled family (e.g. MyriadPro-Regular in 2015). We can still
            # recover its printable-ASCII run exactly, because the offset is
            # derivable; the accents above that run follow the font's own glyph
            # order, for which this module has no evidence, so they are left as
            # U+FFFD rather than guessed.
            if off is None:
                report.append((base, 0, "NO TABLE and offset undecidable - left garbled"))
                continue
            tbl = ascii_table(off)
            # Supply MyriadPro's ten above-run CIDs where we have word-level
            # evidence for them; anything still unknown stays UNRESOLVED.
            if "MyriadPro" in base:
                tbl.update({c: MYRIAD_CID[c] for c in cids if c in MYRIAD_CID})
            tbl.update({c: UNRESOLVED for c in cids if c not in tbl})
            above = [c for c in cids if c not in ascii_table(off)]
            still = [c for c in above if tbl.get(c) == UNRESOLVED]
            report.append((base, len(tbl),
                           "ASCII table derived (offset %d); %d CID(s) above the run, "
                           "%d resolved from word evidence, %d left UNRESOLVED"
                           % (off, len(above), len(above) - len(still), len(still))))
            st = pdf.make_stream(build_tounicode(tbl).encode("latin-1"))
            obj["/ToUnicode"] = pdf.make_indirect(st)
            continue
        # Self-check for the tabled families: their offset must be the 29 the
        # table was built on. If a future year ships an Arial whose `space`
        # sits elsewhere, this says so instead of shifting everything silently.
        if off is not None and off != DEFAULT_ASCII_OFFSET:
            report.append((base, 0, "OFFSET MISMATCH: derived %d, table assumes %d"
                           % (off, DEFAULT_ASCII_OFFSET)))
        key = id(tbl)
        if key not in done:
            done.add(key)
        st = pdf.make_stream(build_tounicode(tbl).encode("latin-1"))
        obj["/ToUnicode"] = pdf.make_indirect(st)
        report.append((base, len(tbl), "ToUnicode injected"))
    pdf.save(dst)
    if verbose:
        for base, n, act in report:
            print("  %-42s %4s  %s" % (base, n or "", act))
    return report


# --------------------------------------------------------------------------
# SECONDARY PATH: decode already-extracted text (heuristic).
# --------------------------------------------------------------------------
# A shifted run is recognised by its HARD MARKER: a byte in 0x03..0x1f. Those
# codes are the shifted forms of space and of ASCII punctuation (CID 3 = space,
# 11/12 = parens, 15 = comma, 17 = period ...), and no correctly-extracted
# Portuguese text contains them. Every shifted run of more than one word
# therefore carries at least one.
#
# Around a hard marker the run is grown over characters that *could* be shifted
# (the shifted alphabet), and the extent is chosen to maximise a Portuguese
# plausibility score. That is how the mid-word '(o' | 'SomR...' boundary is
# placed without font information.
HARD = re.compile(r"[\x03-\x1f]")
_SHIFTABLE = set()
for _c, _u in ARIAL_CID.items():
    if _u != UNRESOLVED:
        _SHIFTABLE.add(chr(_c))

_VOWELS = set("aeiouáàâãéêíóôõúüç")


def _plaus(s):
    """Cheap language-shape score: real words look like alternating CV runs."""
    if not s:
        return 0.0
    sc = 0.0
    for tok in re.findall(r"[^\W\d_]+", s, re.UNICODE):
        low = tok.lower()
        if not (set(low) & _VOWELS):
            sc -= 2.0 * len(tok)          # no vowel at all: garbage
            continue
        sc += len(tok)
        run = 0
        for ch in low:
            if ch in _VOWELS:
                run = 0
            else:
                run += 1
                if run >= 4:
                    sc -= 3.0              # 4+ consonants: garbage
        if low.isupper():
            sc -= 0.0
    sc -= 3.0 * s.count(UNRESOLVED)
    return sc


def decode_cid_string(s, tbl=ARIAL_CID):
    """Map every character of s through the CID table (no detection)."""
    return "".join(tbl.get(ord(c), UNRESOLVED) for c in s)


def _decode_token(tok):
    """Place the shifted span inside one whitespace-delimited token."""
    idx = [m.start() for m in HARD.finditer(tok)]
    if not idx:
        return tok
    lo_lim, hi_lim = idx[0], idx[-1] + 1
    # candidate left edges: from the first hard marker leftwards while shiftable
    lefts = [lo_lim]
    i = lo_lim
    while i > 0 and tok[i - 1] in _SHIFTABLE:
        i -= 1
        lefts.append(i)
    rights = [hi_lim]
    j = hi_lim
    while j < len(tok) and tok[j] in _SHIFTABLE:
        j += 1
        rights.append(j)
    best, bestsc = None, None
    for a in lefts:
        for b in rights:
            cand = tok[:a] + decode_cid_string(tok[a:b]) + tok[b:]
            sc = _plaus(cand)
            if bestsc is None or sc > bestsc:
                best, bestsc = cand, sc
    return best


def decode_text(text):
    """Decode extracted 2018 text, shifting only the runs that are shifted."""
    out = []
    for piece in re.split(r"(\s+)", text):
        out.append(piece if piece.isspace() or not piece else _decode_token(piece))
    return "".join(out)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "table":
        for cid in sorted(ARIAL_CID):
            u = ARIAL_CID[cid]
            print("ARIAL  %4d 0x%02X  %-4r  U+%04X" % (cid, cid, u, ord(u[0])))
        for nm, t in (("SYMBOL", SYMBOL_CID), ("EUCLID", EUCLID_CID), ("TIMES", TIMES_CID)):
            for cid in sorted(t):
                print("%-6s %4d          %-4r" % (nm, cid, t[cid]))
        return 0
    if cmd == "repair":
        if len(argv) < 4:
            print("usage: 17_decode_2018.py repair <in.pdf> <out.pdf>")
            return 2
        print("repairing %s -> %s" % (argv[2], argv[3]))
        repair_pdf(argv[2], argv[3])
        return 0
    if cmd == "text":
        src = argv[2]
        data = open(src, encoding="utf-8", errors="replace").read()
        res = decode_text(data)
        if "-o" in argv:
            open(argv[argv.index("-o") + 1], "w", encoding="utf-8").write(res)
        else:
            sys.stdout.write(res)
        return 0
    print("unknown command %r" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
