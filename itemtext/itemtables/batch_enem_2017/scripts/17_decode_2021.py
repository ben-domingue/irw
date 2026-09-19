#!/usr/bin/env python3
"""Decode the 2021 ENEM booklets, whose body text extracts as /gNNN tokens.

THE DEFECT
----------
Every printed 2021 booklet embeds subset CFF (Type1C) fonts whose
/Encoding /Differences names glyphs by GLYPH ID -- /g70, /g82, /g125 -- while
the /ToUnicode CMap covers only the codes whose Differences name is a real
Adobe glyph name. Page 4 /F2 of the day-1 accessibility booklet declares 189
codes in Differences and 76 in ToUnicode, and the 113 uncovered codes are
EXACTLY the /gNNN ones. So the PDF's own ToUnicode gives literally zero direct
evidence about any /gNNN glyph (verified: 0 of 599 pooled name->unicode
observations across four booklets concern a /gNNN name). pypdf then falls back
to printing the glyph name, which is where the /gNNN litter comes from.

THE DERIVATION, which is document-internal and not a guess
----------------------------------------------------------
The same font family is embedded MANY times over a booklet, with a different
subset tag and a different subset per page group. Some of those subsets carry
REAL glyph names (page 1 /F2 is `GHPNBI+ArialMT` with names A, Atilde, comma,
otilde...). The glyph OUTLINES are identical across subsets of one family
because they come from the same source face. So:

    1. decompile every /FontFile3 (bare CFF) with fontTools
    2. draw every charstring to a RecordingPen and hash the point sequence
       together with the advance width -> an outline signature
    3. for each family, signatures seen under a REAL name give signature -> name
    4. a /gNNN charstring with a matching signature is that named glyph

This yields the Unicode of a glyph id from the booklet's own font programs. It
is checked, not assumed: where a gid is attested by outline in more than one
family/booklet the attestations must agree, and disagreements are reported.

WHY MACINTOSH ORDERING IS ONLY A FALLBACK, AND A NARROW ONE
-----------------------------------------------------------
The ids do follow the standard Macintosh glyph ordering in the low range --
/g3=space, /g15=comma, /g36..61=A-Z, /g68..93=a-z, /g105=aacute,
/g125=otilde -- all independently confirmed here by outline match. But the
ordering DIVERGES higher up, because Arial does not contain every glyph of the
258-glyph standard Mac order. Observed in this very booklet:

    /g191 prints where "fi" belongs ("/g191/g79/g80/g68/g70/g121/g81" is
          "filmacion"), and standard Mac index 191 is guilsinglright; fi is 192
    /g200 prints where "A-acute" belongs ("/g200/g85/g68/g69/g72" = "Arabe"),
          and standard Mac index 200 is Ecircumflex; Aacute is 201

i.e. a -1 shift has accumulated by gid 191. Extrapolating Mac ordering into
that range would silently produce plausible-looking wrong accents, which is
the failure mode the brief forbids. So Mac ordering is applied ONLY up to the
highest gid for which outline evidence exists AND agrees with it
(--mac-ceiling, default: derived), and every remaining gid is left as an
undecoded token and reported. Nothing is invented.

APPLICATION -- and why it is the /ToUnicode stream that gets patched
-------------------------------------------------------------------
The obvious move, rewriting /Differences so /g125 becomes /otilde, is WRONG
here and produces text that looks almost right, which is the worst outcome.
pypdf follows PDF 1.7 s5.9.1: when a /ToUnicode CMap exists, for every code it
covers the encoding is replaced by chr(code) and the CMap is consulted, and
the CMap is then keyed by that character. These booklets name code 0x6c "/J"
and code 0x78 "/question", so map_dict['l'] == 'J' and map_dict['x'] == '?'.
A /g79 patched to /l therefore came out as "J" and /g91 patched to /x came out
as "?" -- observed as "personaJ; Jas RRSS" and "O te?to". Measured before the
fix: every lowercase l and x in the booklet was corrupted.

So decoding instead COMPLETES the incomplete CMap: each font's /ToUnicode is
rebuilt as (its own existing entries) + (one bfchar per /gNNN code, mapping the
code to the Unicode derived above). That is the defect stated in PDF terms and
it leaves /Differences, extraction, layout and ordering untouched, so a parse
of the decoded reader follows the pinned parser exactly.

USAGE
    python3 17_decode_2021.py --report <out.json> <pdf> [<pdf> ...]
    python3 17_decode_2021.py --decode-text <pdf> --page 4
and as a library:
    from importlib import import_module
    dec = import_module("17_decode_2021")
    reader = dec.decoded_reader(pdf, gmap)          # patched PdfReader
"""
from __future__ import annotations
import argparse, collections, hashlib, io, json, logging, os, re, sys, warnings
logging.disable(logging.CRITICAL); warnings.filterwarnings("ignore")
from pypdf import PdfReader
from pypdf.generic import DecodedStreamObject, NameObject, NumberObject
from pypdf._codecs import adobe_glyphs
from fontTools.cffLib import CFFFontSet
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib.standardGlyphOrder import standardGlyphOrder as MAC_ORDER

GID = re.compile(r"^/?g(\d+)$")
LIGATURE_EXPANSION = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl",
                      "\ufb03": "ffi", "\ufb04": "ffl"}
MARKER = "[UNDECODED-g%d]"   # never a plausible letter; 18_validate counts these


# ---------------------------------------------------------------- font access
def _family(basefont: str) -> str:
    """Strip the six-letter subset tag: GIDIGI+ArialMT -> ArialMT."""
    return basefont.lstrip("/").split("+", 1)[-1]


def _differences(enc) -> dict:
    d = enc.get("/Differences")
    if not d:
        return {}
    out, cur = {}, None
    for x in d.get_object():
        if isinstance(x, (int, float, NumberObject)):
            cur = int(x)
            continue
        if cur is None:
            continue
        out[cur] = str(x)
        cur += 1
    return out


def _tounicode_entries(data: str) -> dict:
    """Parse an existing ToUnicode CMap into {code: unicode string}."""
    out = {}
    for blk in re.findall(r"beginbfchar(.*?)endbfchar", data, re.S):
        for src, dst in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]*)>", blk):
            if not dst:
                continue
            out[int(src, 16)] = "".join(
                chr(int(dst[i:i + 4], 16)) for i in range(0, len(dst), 4))
    for blk in re.findall(r"beginbfrange(.*?)endbfrange", data, re.S):
        for lo, hi, dst in re.findall(
                r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
            lo, hi, base = int(lo, 16), int(hi, 16), int(dst, 16)
            for k in range(lo, min(hi, 255) + 1):
                out[k] = chr(base + (k - lo))
    return out


def _fonts(reader):
    """Yield (page_index, resource_key, font_dict) for every simple font."""
    for i, pg in enumerate(reader.pages):
        res = pg.get("/Resources")
        if not res:
            continue
        res = res.get_object()
        fonts = res.get("/Font")
        if not fonts:
            continue
        fonts = fonts.get_object()
        for k in list(fonts.keys()):
            try:
                yield i, k, fonts[k].get_object()
            except Exception:
                continue


def _outline_signatures(font) -> dict:
    """glyphname -> outline signature, from the embedded CFF program."""
    fd = font.get("/FontDescriptor")
    if fd is None:
        return {}
    fd = fd.get_object()
    if "/FontFile3" not in fd:
        return {}
    try:
        data = fd["/FontFile3"].get_object().get_data()
        cff = CFFFontSet()
        cff.decompile(io.BytesIO(data), None)
        td = cff[cff.fontNames[0]]
        cs = td.CharStrings
    except Exception:
        return {}
    sig = {}
    for name in cs.keys():
        try:
            g = cs[name]
            pen = RecordingPen()
            g.draw(pen)
            if not pen.value:
                continue          # blank outline (space): width alone is weak
            payload = repr([(op, tuple(round(c, 1) for pt in args for c in pt))
                            for op, args in pen.value])
            w = getattr(g, "width", None)
            sig[name] = hashlib.md5(f"{w}|{payload}".encode()).hexdigest()
        except Exception:
            continue
    return sig


# ---------------------------------------------------------------- derivation
def collect_evidence(pdfs):
    """Outline-match /gNNN glyphs against really-named ones, per family.

    Returns (attested, families, stats) where attested maps
    (family, gid) -> Counter(real glyph name).
    """
    named = collections.defaultdict(dict)     # family -> sig -> set(names)
    unnamed = collections.defaultdict(dict)   # family -> gid -> set(sig)
    stats = collections.Counter()
    for p in pdfs:
        reader = PdfReader(p)
        for _, _, font in _fonts(reader):
            bf = str(font.get("/BaseFont") or "")
            if not bf:
                continue
            fam = _family(bf)
            sigs = _outline_signatures(font)
            if not sigs:
                continue
            stats["subsets"] += 1
            for name, s in sigs.items():
                m = GID.match(name)
                if m:
                    unnamed[fam].setdefault(int(m.group(1)), set()).add(s)
                elif name != ".notdef":
                    named[fam].setdefault(s, set()).add(name)
    attested = collections.defaultdict(collections.Counter)
    for fam, gids in unnamed.items():
        for gid, ss in gids.items():
            stats["gid_glyphs"] += 1
            for s in ss:
                for nm in named.get(fam, {}).get(s, ()):
                    if not GID.match(nm):
                        attested[(fam, gid)][nm] += 1
    return attested, dict(stats)


def glyph_to_unicode(name):
    u = adobe_glyphs.get("/" + name.lstrip("/"))
    return u


def build_map(pdfs, mac_ceiling=None):
    """Return (gmap, meta), where gmap is FAMILY-SCOPED.

    gmap["*"]        the Arial-order map, applied only to families measured to
                     follow it (see meta["arial_order_families"])
    gmap["<family>"] that family's own outline-attested entries

    WHY THE SCOPING IS NOT OPTIONAL. Glyph ids are per FONT, so a map derived
    from Arial is meaningless in another face. In these booklets the /gNNN
    codes are 97.3% Arial (ArialMT 15241 codes, Arial-BoldMT 1882,
    Arial-ItalicMT 75) but SymbolMT declares 425 of them and CambriaMath 52.
    Applying the Arial map to SymbolMT would turn maths symbols into ordinary
    letters -- silently, and into text that reads as words. So a family gets
    the Arial-order tiers only if its OWN outline attestations agree with Mac
    ordering below the ceiling with no disagreement, which is a measurement
    made per booklet set, not a hardcoded allowlist.
    """
    attested, stats = collect_evidence(pdfs)
    # --- 0. which families may use the Arial-order tiers at all?
    fam_u = collections.defaultdict(dict)       # family -> gid -> unicode
    for (fam, gid), c in attested.items():
        nm = c.most_common(1)[0][0]
        u = glyph_to_unicode(nm)
        if u is not None:
            fam_u[fam][gid] = u
    arial_fams, other_fams = [], []
    for fam, gids in fam_u.items():
        low = {g: u for g, u in gids.items() if g < len(MAC_ORDER)}
        agree = sum(1 for g, u in low.items()
                    if glyph_to_unicode(MAC_ORDER[g]) == u)
        # follow Arial ordering only on real evidence: at least 20 attested
        # low-range glyphs and at least 85% of them where Mac ordering holds
        # (ArialMT measures 96 agree / 13 disagree, and every one of the 13 is
        # ABOVE the ceiling; SymbolMT and CambriaMath measure 0 agree).
        if len(low) >= 20 and agree / len(low) >= 0.85:
            arial_fams.append(fam)
        else:
            other_fams.append(fam)
    # --- 1. outline-attested entries, checked for cross-family agreement
    per_gid = collections.defaultdict(collections.Counter)
    where = collections.defaultdict(set)
    for (fam, gid), c in attested.items():
        if fam not in arial_fams:
            continue
        for nm, n in c.items():
            u = glyph_to_unicode(nm)
            if u is None:
                continue
            per_gid[gid][u] += n
            where[gid].add(f"{fam}:{nm}")
    conflicts = {g: dict(c) for g, c in per_gid.items() if len(c) > 1}
    gmap, src = {}, {}
    for gid, c in per_gid.items():
        if len(c) > 1:
            continue                       # never pick a winner on a conflict
        u = next(iter(c))
        gmap[gid] = u
        src[gid] = "outline:" + ",".join(sorted(where[gid]))
    # --- 2. how far does Macintosh ordering actually hold?
    agree, disagree = [], []
    for gid, u in sorted(gmap.items()):
        if gid >= len(MAC_ORDER):
            continue
        mu = glyph_to_unicode(MAC_ORDER[gid])
        (agree if mu == u else disagree).append(gid)
    if mac_ceiling is None:
        # highest gid such that EVERY outline-attested gid at or below it
        # agrees with Mac ordering. Below that line Mac ordering is a measured
        # fact about this font; above it, it is demonstrably wrong.
        bad = min(disagree) if disagree else len(MAC_ORDER)
        mac_ceiling = bad - 1
    for gid in range(len(MAC_ORDER)):
        if gid in gmap or gid > mac_ceiling:
            continue
        u = glyph_to_unicode(MAC_ORDER[gid])
        if u is None:
            continue
        gmap[gid] = u
        src[gid] = f"mac_order<=ceiling({mac_ceiling}):{MAC_ORDER[gid]}"
    # --- 3. bracketed Mac-offset interpolation, above the ceiling
    #
    # Above the ceiling, Arial's glyph order is still standard Mac ORDER with
    # glyphs MISSING, so each attested gid g satisfies  glyph(g) = MAC[g + k]
    # for a shift k that only ever grows. Measured here: k=+1 across
    # g172..g207 and k=+2 across g210..g240. A gid is filled in ONLY when the
    # nearest outline-attested gid below it and the nearest above it agree on
    # k -- interpolation between two measurements, never extrapolation past
    # the last one. This is what recovers the fi/fl ligatures, which no PDF
    # producer ever names with a real Adobe name and which no subset in the
    # entire 2021 corpus therefore attests: 0 of 9164 subsets read.
    offs = {}
    for gid in sorted(g for g in gmap if src[g].startswith("outline")):
        u = gmap[gid]
        for k in range(0, 8):
            j = gid + k
            if j < len(MAC_ORDER) and glyph_to_unicode(MAC_ORDER[j]) == u:
                offs[gid] = k
                break
    keys = sorted(offs)
    above = [g for g in keys if g > mac_ceiling]
    for gid in range(mac_ceiling + 1, max(above) if above else mac_ceiling):
        if gid in gmap:
            continue
        lo = [g for g in above if g < gid]
        hi = [g for g in above if g > gid]
        if not lo or not hi:
            continue
        k_lo, k_hi = offs[max(lo)], offs[min(hi)]
        if k_lo != k_hi:
            continue                      # shift changes across the gap: refuse
        j = gid + k_lo
        if j >= len(MAC_ORDER):
            continue
        u = glyph_to_unicode(MAC_ORDER[j])
        if u is None:
            continue
        gmap[gid] = u
        src[gid] = (f"bracketed_mac_offset(k=+{k_lo} between g{max(lo)} and "
                    f"g{min(hi)}):{MAC_ORDER[j]}")
    # --- 4. ligatures are decomposed on the way out. The booklet's fi/fl are
    # single glyphs (gid 191/192 -> U+FB01/U+FB02); U+FB01 in item_text would
    # make "definitivo" fail a plain string match against the response tables
    # and against every other year, so emit the two letters. Nothing else is
    # normalised: accents stay as composed characters, as in 2019 and 2023.
    for gid, u in list(gmap.items()):
        if u in LIGATURE_EXPANSION:
            gmap[gid] = LIGATURE_EXPANSION[u]
            src[gid] += f" (ligature {hex(ord(u))} expanded)"
    # The Arial-order table is materialised under each family measured to
    # follow it. There is deliberately NO wildcard fallback: a family that was
    # never measured (SymbolMT declares 425 /gNNN codes and attests none of
    # them) decodes NOTHING and its glyphs are reported as undecoded, rather
    # than being handed Arial's letters.
    scoped = {fam: dict(gmap) for fam in arial_fams}
    for fam in other_fams:
        scoped[fam] = {g: (LIGATURE_EXPANSION.get(u, u))
                       for g, u in fam_u[fam].items()}
    meta = {
        "arial_order_families": sorted(arial_fams),
        "own_evidence_only_families": {f: len(fam_u[f]) for f in sorted(other_fams)},
        "pdfs": [os.path.basename(p) for p in pdfs],
        "subsets_read": stats.get("subsets", 0),
        "gid_glyphs_seen": stats.get("gid_glyphs", 0),
        "outline_attested": len([g for g in src if src[g].startswith("outline")]),
        "mac_fallback": len([g for g in src if src[g].startswith("mac")]),
        "bracketed": {str(g): gmap[g] for g in sorted(src) if src[g].startswith("bracketed")},
        "mac_ceiling": mac_ceiling,
        "mac_agree_gids": agree,
        "mac_disagree_gids": {g: {"outline": gmap[g], "mac": MAC_ORDER[g]}
                              for g in disagree},
        "conflicts": conflicts,
        "map": {str(g): gmap[g] for g in sorted(gmap)},
        "source": {str(g): src[g] for g in sorted(src)},
    }
    return scoped, meta


# ---------------------------------------------------------------- application
def _cmap_stream(font_name, entries):
    """Build a complete 1-byte ToUnicode CMap from {code: unicode string}."""
    head = (
        "/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n"
        "/CIDSystemInfo << /Registry (%s) /Ordering (T1UV) /Supplement 0 >> def\n"
        "/CMapName /%s def\n/CMapType 2 def\n"
        "1 begincodespacerange\n<00> <ff>\nendcodespacerange\n" % (font_name, font_name)
    )
    body = []
    items = sorted(entries.items())
    for i in range(0, len(items), 100):
        chunk = items[i:i + 100]
        body.append("%d beginbfchar" % len(chunk))
        for code, u in chunk:
            dst = "".join("%04X" % ord(c) for c in u)
            body.append("<%02X> <%s>" % (code, dst))
        body.append("endbfchar")
    tail = "endcmap\nCMapName currentdict /CMap defineresource pop\nend\nend"
    return head + "\n".join(body) + "\n" + tail


def patch_reader(reader, gmap):
    """Complete every font's /ToUnicode so its /gNNN codes decode.

    Returns (n_codes_decoded, n_codes_left). Leaving a code alone is
    deliberate: an unresolved gid must stay visible as /gNNN in the extracted
    text so 18_validate_decode.py counts it instead of it turning into a
    plausible wrong letter.
    """
    done = left = 0
    patched = {}
    scoped = gmap
    for _, _, font in _fonts(reader):
        if id(font) in patched:
            continue
        fam = _family(str(font.get("/BaseFont") or ""))
        table = scoped.get(fam, {})
        enc = font.get("/Encoding")
        if enc is None:
            continue
        enc = enc.get_object()
        if not hasattr(enc, "get"):
            continue
        diff = _differences(enc)
        if not diff:
            continue
        add = {}
        for code, name in diff.items():
            m = GID.match(name)
            if not m or code > 255:
                continue
            gid = int(m.group(1))
            if gid in table:
                add[code] = table[gid]
            else:
                # An unresolved gid is mapped to an explicit, greppable marker
                # rather than left to leak. Leaking is not neutral: pypdf emits
                # the literal "/g191" and then pushes each of those characters
                # through the SAME broken CMap, so the booklet actually printed
                # "caligra9g191a" and "That9g1hes" -- unreadable AND unparseable
                # back to a gid. The marker keeps the loss countable.
                add[code] = MARKER % gid
                left += 1
        if not add:
            patched[id(font)] = 0
            continue
        existing = {}
        tu = font.get("/ToUnicode")
        if tu is not None:
            try:
                existing = _tounicode_entries(tu.get_object().get_data().decode("latin-1"))
            except Exception:
                existing = {}
        merged = dict(existing)
        merged.update(add)          # our entries win only on codes it lacked
        for c in existing:
            if c in add:
                merged[c] = existing[c]
        name = str(font.get("/BaseFont") or "F").lstrip("/").replace("/", "")
        st = DecodedStreamObject()
        st.set_data(_cmap_stream(name or "F", merged).encode("latin-1"))
        font[NameObject("/ToUnicode")] = st
        done += len(add)
        patched[id(font)] = len(add)
    return done, left


def load_map(path):
    """Load a cached gid->unicode map written by --save-map."""
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    return {fam: {int(g): u for g, u in t.items()} for fam, t in raw.items()}


def decoded_reader(pdf, gmap):
    r = PdfReader(pdf)
    patch_reader(r, gmap)
    return r


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+")
    ap.add_argument("--report", help="write the derived map + provenance here")
    ap.add_argument("--decode-text", metavar="PDF",
                    help="print decoded text of one PDF using the derived map")
    ap.add_argument("--page", type=int, default=None, help="1-based page")
    ap.add_argument("--mac-ceiling", type=int, default=None)
    ap.add_argument("--save-map", help="write just the gid->unicode map here")
    a = ap.parse_args()

    gmap, meta = build_map(a.pdfs, a.mac_ceiling)
    print(f"arial-order families      {meta['arial_order_families']}")
    print(f"own-evidence-only families {meta['own_evidence_only_families']}")
    print(f"subsets read              {meta['subsets_read']}")
    print(f"distinct (family,gid)     {meta['gid_glyphs_seen']}")
    print(f"outline-attested gids     {meta['outline_attested']}")
    print(f"mac-order fallback gids   {meta['mac_fallback']} (ceiling {meta['mac_ceiling']})")
    print(f"bracketed-offset gids     {len(meta['bracketed'])}: "
          f"{ {int(k): v for k, v in meta['bracketed'].items()} }")
    print(f"arial map size            {len(next(iter(gmap.values()), {}))}")
    print(f"cross-family conflicts    {len(meta['conflicts'])}")
    if meta["mac_disagree_gids"]:
        print("gids where Mac ordering is WRONG (outline wins):")
        for g, d in sorted(meta["mac_disagree_gids"].items(), key=lambda x: int(x[0])):
            print(f"  g{g}: outline={d['outline']!r} mac={d['mac']}")
    if a.report:
        with open(a.report, "w", encoding="utf-8") as fh:
            json.dump(meta, fh, ensure_ascii=False, indent=1)
        print("report ->", a.report)
    if a.save_map:
        with open(a.save_map, "w", encoding="utf-8") as fh:
            json.dump({fam: {str(g): u for g, u in sorted(t.items())}
                       for fam, t in sorted(gmap.items())}, fh,
                      ensure_ascii=False, indent=0)
        print("map ->", a.save_map)
    if a.decode_text:
        r = decoded_reader(a.decode_text, gmap)
        pages = [r.pages[a.page - 1]] if a.page else r.pages
        for pg in pages:
            print(pg.extract_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
