#!/usr/bin/env python3
"""16_verify_gabarito.py's check, run off INEP's own key strings instead of a
gabarito PDF -- so it also covers the ACCESSIBILITY booklet.

WHY. 16_verify_gabarito.py is the only check that can catch a position offset,
and it needs the printed gabarito PDF. INEP is currently resetting the TLS
handshake on every request to download.inep.gov.br, so three of the four
gabaritos could not be fetched. But the same information is already on disk:
RESULTADOS_<YEAR>.csv carries TX_GABARITO_CN/CH/LC/MT, INEP's answer key as a
45-character string indexed by the item's PRINTED POSITION WITHIN ITS AREA,
recorded per CO_PROVA. That is exactly the "printed position -> letter" table
the PDF provides.

It is also STRICTLY STRONGER than the PDF route in two ways:
  - 16_verify_gabarito.py restricts its candidates to `standard_prova_codes`,
    so it can never look at the accessibility CO_PROVA that the DOSVOX text
    actually comes from. These strings exist for every CO_PROVA, accessibility
    included, so the booklet we parsed is checked directly.
  - It covers all four areas of both days from one file, rather than needing a
    separate PDF per day.

The comparison: for the k-th item of an area (k = 1..45), the `continuous`
convention says its CO_POSICAO is printed_lo + k - 1 (LC 1, CH 46, CN 91,
MT 136); `per_area` says it is k. Agreement across ~45 effectively random
5-way letters is decisive, and a wrong convention lands at chance.

LC's positions 1-5 exist twice, once per foreign language, and a candidate's
string carries the keys for the language they sat -- so those five are compared
against the ITENS_PROVA rows with the matching TP_LINGUA, which also
cross-checks that TP_LINGUA 0=Inglês / 1=Espanhol is not reversed (trap 6).

'X' in a key string is INEP's marker for an item with no scorable key (R3);
those positions are skipped, as they are in ITENS_PROVA.

INPUT. gab_strings_<YEAR>.txt, one "area;CO_PROVA;TP_LINGUA;key;n" line per
distinct combination, built by streaming RESULTADOS (awk, not read.csv -- the
file is 1.7-2.1 GB, and this keeps nothing but the distinct strings in memory):

    awk -F';' 'NR>1 {
      if ($19!="" && $32!="") k["CN;"$19";"$31";"$32]++;
      if ($20!="" && $33!="") k["CH;"$20";"$31";"$33]++;
      if ($21!="" && $34!="") k["LC;"$21";"$31";"$34]++;
      if ($22!="" && $35!="") k["MT;"$22";"$31";"$35]++;
    } END { for (x in k) print x";"k[x] }' \
      ~/enem/extracted_<YEAR>/microdados_enem_<YEAR>/DADOS/RESULTADOS_<YEAR>.csv \
      > /scratch/users/<user>/itemtext_years/gab_strings_<YEAR>.txt

Fields 19-22 are CO_PROVA_{CN,CH,LC,MT}, 31 is TP_LINGUA, 32-35 are
TX_GABARITO_{CN,CH,LC,MT}.

A CO_PROVA with no candidates in RESULTADOS has no key string and is reported
as such rather than counted: RESULTADOS_2024 contains no candidate at all for
the LC and CN accessibility provas (1401, 1425), though it does for CH (1390)
and MT (1414).
"""
import csv, glob, json, sys, collections

ENEM = "/home/users/mazzafe/enem"
W = "/scratch/users/mazzafe/itemtext_years"
PRINTED_LO = {"LC": 1, "CH": 46, "CN": 91, "MT": 136}
KEYS = set("ABCDE")


def itens(year):
    # 2016 ships this file lowercase; 13_join.py already tries both spellings
    # and this script did not, so 2016 died on an IndexError instead of running.
    cands = (glob.glob(f"{ENEM}/extracted_{year}/**/ITENS_PROVA_{year}.csv", recursive=True)
             + glob.glob(f"{ENEM}/extracted_{year}/**/itens_prova_{year}.csv", recursive=True))
    if not cands:
        sys.exit(f"no ITENS_PROVA for {year}")
    p = cands[0]
    return list(csv.DictReader(open(p, encoding="latin-1"), delimiter=";"))


def main(year):
    man = json.load(open(f"{ENEM}/itemtext_run/allyears/manifest.json"))[str(year)]
    rows = itens(year)
    # area -> prova -> lingua -> key string (the most common one; all candidates
    # sitting one CO_PROVA with one TP_LINGUA get the same string)
    strings = collections.defaultdict(lambda: collections.defaultdict(dict))
    best = collections.defaultdict(lambda: collections.defaultdict(dict))
    for ln in open(f"{W}/gab_strings_{year}.txt", encoding="utf-8"):
        parts = ln.rstrip("\n").split(";")
        if len(parts) != 5:
            continue
        area, prova, ling, s, n = parts[0], parts[1], parts[2], parts[3], int(parts[4])
        if n > best[area][prova].get(ling, 0):
            best[area][prova][ling] = n
            strings[area][prova][ling] = s

    acc = {a: man["areas"][a]["accessibility_co_prova"] for a in PRINTED_LO}
    std_label = {}
    for r in rows:
        if r["CO_PROVA"] in set(man["standard_prova_codes"]):
            std_label[r["CO_PROVA"]] = (r["SG_AREA"], (r.get("TX_COR") or "").upper())

    print(f"===== {year}: printed-position keys from RESULTADOS_{year}.csv")
    grand = collections.Counter()
    for area in ("LC", "CH", "CN", "MT"):
        lo = PRINTED_LO[area]
        targets = [(acc[area], "LARANJA (accessibility, the booklet we parsed)")]
        for p, (a, cor) in sorted(std_label.items()):
            if a == area and cor in ("AZUL", "AMARELA"):
                targets.append((p, f"{cor} (standard)"))
        for prova, label in targets:
            sub = [r for r in rows if r["CO_PROVA"] == prova]
            if not sub or prova not in strings[area]:
                print(f"  {area} {prova} {label}: no key string on file")
                continue
            # LC's key string is 50 characters, not 45, and is IDENTICAL for
            # TP_LINGUA 0 and 1: INEP lays both language blocks out inline, so
            # string index j maps to
            #     j 1-5   -> CO_POSICAO 1-5,  TP_LINGUA 0 (Inglês)
            #     j 6-10  -> CO_POSICAO 1-5,  TP_LINGUA 1 (Espanhol)
            #     j 11-50 -> CO_POSICAO 6-45, TP_LINGUA blank
            # Reading it as 45 positions scores ~26%, i.e. chance, which is
            # what a misread index looks like. This also cross-checks trap 6:
            # if 0/1 were reversed the first ten would disagree on their own.
            # Scan EVERY offset instead of testing two named conventions.
            # The old code used a hardcoded 2017+ day order
            # (PRINTED_LO = LC 1, CH 46, CN 91, MT 136). 2013-2016 print
            # CH/CN on day 1 and LC/MT on day 2, so for those years two of
            # the four areas matched NO printed position at all and scored
            # n=0 -- which the summary then dropped from the denominator and
            # reported as "90/90 EXACT". Scanning offsets needs no day-order
            # table, and an area that cannot be scored is now a FAILURE.
            best = None
            for delta in range(-180, 181):
                lut = {}
                for r in sub:
                    cp = int(r["CO_POSICAO"])
                    k = cp + delta
                    lut.setdefault(k, {})[(r.get("TP_LINGUA") or "").strip()] = \
                        (r["TX_GABARITO"] or "").strip()
                    ok = n = 0
                    seen_lc = set()
                    for ling, s in strings[area][prova].items():
                        for j in range(1, len(s) + 1):
                            printed = s[j - 1]
                            if area == "LC" and len(s) == 50:
                                if j <= 5:
                                    k, need = j, "0"
                                elif j <= 10:
                                    k, need = j - 5, "1"
                                else:
                                    k, need = j - 5, ""
                                if (prova, j) in seen_lc:
                                    continue       # the string repeats per TP_LINGUA
                                seen_lc.add((prova, j))
                            else:
                                k, need = j, None
                            if printed not in KEYS:
                                continue           # 'X' -> no scorable key (R3)
                            cell = lut.get(k)
                            if not cell:
                                continue
                            if need is not None:
                                want = cell.get(need)
                            else:
                                want = cell.get(ling) if ling in cell else cell.get("")
                                if want is None:
                                    want = next(iter(cell.values())) if len(cell) == 1 else None
                            if want is None or want not in KEYS:
                                continue
                            n += 1
                            ok += (printed == want)
                if n and (best is None or (ok, n) > (best[1], best[2])):
                    best = (delta, ok, n)
            if best is None:
                print(f"  {area} {prova} {label:52s} NOT SCORABLE (n=0) -- FAILURE")
                grand["untested"] += 1
                continue
            delta, ok, n = best
            pct = 100 * ok / n
            verdict = "EXACT" if ok == n and n >= 40 else "MISMATCH"
            if n < 40:
                verdict = f"TOO FEW (n={n})"
            grand[label.split(" ")[0] + "_ok"] += ok
            grand[label.split(" ")[0] + "_n"] += n
            grand["areas_" + label.split(" ")[0]] += 1
            print(f"  {area} {prova} {label:52s} offset {delta:+4d}  "
                  f"{ok}/{n} ({pct:5.1f}%)  {verdict}")
    print()
    for who in ("LARANJA", "AZUL", "AMARELA"):
        ok, n = grand[who + "_ok"], grand[who + "_n"]
        if not n:
            continue
        areas = grand["areas_" + who]
        # An area that scores n=0 used to vanish from the denominator, so a
        # single passing area printed as a 100% EXACT total. Four areas must
        # be scored for the figure to mean anything.
        if areas < 4:
            print(f"  TOTAL {who:8s}: {ok}/{n} ({100*ok/n:.1f}%) but only "
                  f"{areas} of 4 areas were scored -- NOT VERIFIED")
        else:
            print(f"  TOTAL {who:8s}: {ok}/{n} ({100*ok/n:.1f}%)  "
                  f"{'EXACT' if ok == n else 'MISMATCH'}  [4/4 areas scored]")
    if grand["untested"]:
        print(f"  !! {grand['untested']} booklet-area(s) were NOT SCORABLE -- FAILURE")


if __name__ == "__main__":
    for y in sys.argv[1:]:
        main(y)
