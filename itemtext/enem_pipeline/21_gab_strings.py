#!/usr/bin/env python3
"""Extract INEP's own answer-key strings from the microdata, for any year.

Feeds 20_verify_gabarito_microdata.py. That check is the strongest position
verification available -- stronger than 16_verify_gabarito.py, because the key
strings exist for EVERY CO_PROVA including the accessibility booklet the text is
actually parsed from, while the PDF route is restricted to standard_prova_codes.
It also needs no download, which matters: INEP resets the TLS handshake under
any sustained fetching.

The original extractor hardcoded field positions (19-22, 31, 32-35) from the
2024/2025 RESULTADOS layout. Those positions do NOT hold across years: 2013-2022
ship one MICRODADOS_ENEM_<YEAR>.csv with a different column order, and some years
split into PARTICIPANTES + RESULTADOS. So this resolves every column BY NAME from
the header and reports what it found, rather than trusting an offset -- reading
the wrong column would silently compare against the wrong letters.

Memory: the file is 1.4-2.1 GB, so it streams and keeps only the DISTINCT
(area, CO_PROVA, TP_LINGUA, key) tuples, of which there are a few hundred.

Usage: python3 21_gab_strings.py <year> [<year> ...]
"""
import csv, glob, os, sys

ENEM = os.path.expanduser("~/enem")
OUT = "/scratch/users/mazzafe/itemtext_years"
AREAS = ("CN", "CH", "LC", "MT")


def find_source(year):
    """The file carrying TX_GABARITO_*, whatever the year calls it."""
    pats = [f"{ENEM}/extracted_{year}/**/RESULTADOS_{year}.csv",
            f"{ENEM}/extracted_{year}/**/MICRODADOS_ENEM_{year}.csv",
            f"{ENEM}/extracted_{year}/**/microdados_enem_{year}.csv"]
    for p in pats:
        hits = glob.glob(p, recursive=True)
        if hits:
            return hits[0]
    return None


def main(year):
    src = find_source(year)
    if not src:
        print(f"  {year}: no RESULTADOS/MICRODADOS file found"); return 1
    with open(src, encoding="latin-1", errors="replace") as fh:
        header = fh.readline().rstrip("\n").split(";")
    idx = {h.strip().strip('"'): i for i, h in enumerate(header)}
    need = {a: (idx.get(f"CO_PROVA_{a}"), idx.get(f"TX_GABARITO_{a}")) for a in AREAS}
    ling = idx.get("TP_LINGUA")
    missing = [a for a, (p, g) in need.items() if p is None or g is None]
    if missing:
        print(f"  {year}: {src.split('/')[-1]} has no CO_PROVA/TX_GABARITO for {missing}")
        print(f"       columns present: {[h for h in header if 'GABARITO' in h or 'CO_PROVA' in h]}")
        return 1
    print(f"  {year}: {src.split('/')[-1]}")
    print(f"       resolved by NAME -> " + ", ".join(
        f"{a}:CO_PROVA={need[a][0]}/GAB={need[a][1]}" for a in AREAS) +
        f", TP_LINGUA={ling}")

    counts = {}
    n = 0
    with open(src, encoding="latin-1", errors="replace") as fh:
        fh.readline()
        for line in fh:
            n += 1
            f = line.rstrip("\n").split(";")
            if len(f) < len(header):
                continue
            lg = f[ling].strip().strip('"') if ling is not None else ""
            for a in AREAS:
                pi, gi = need[a]
                prova = f[pi].strip().strip('"')
                key = f[gi].strip().strip('"')
                if prova and key:
                    k = f"{a};{prova};{lg};{key}"
                    counts[k] = counts.get(k, 0) + 1
    os.makedirs(OUT, exist_ok=True)
    dst = f"{OUT}/gab_strings_{year}.txt"
    with open(dst, "w", encoding="utf-8") as fh:
        for k, v in sorted(counts.items()):
            fh.write(f"{k};{v}\n")
    print(f"       {n:,} rows scanned, {len(counts)} distinct key strings -> {dst}")
    return 0


if __name__ == "__main__":
    rc = 0
    for y in sys.argv[1:]:
        rc |= main(y)
    sys.exit(rc)
