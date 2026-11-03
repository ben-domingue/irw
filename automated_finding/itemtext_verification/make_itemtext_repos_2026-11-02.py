#!/usr/bin/env python3
"""Item text for lochmannova_2026_spa_environment and nurmalita_2026_{financial_literacy,
self_control,paylater_use,financial_stability} (repos sweep 2026-11-02).

    python3 make_itemtext_repos_2026-11-02.py <lochmannova_dir> <nurmalita_dir> <resp_dir> <out_dir>

lochmannova_2026_spa_environment (Harvard Dataverse 10.7910/DVN/38ZOKO, CC BY 4.0).
  Czech administration. master_codebook.xlsx has one row per data column, keyed by the
  column name ("Variable (EN)", e.g. O45_nature_calmness), with the Czech question as
  administered, the depositors' own English, and the response options in both languages
  as "1 = ...; 2 = ...". data/lochmannova_2026_spa.py renames each column to its leading
  question number (O45_nature_calmness -> O45), so the tie is by name, not position.
  The "<n> = " prefixes in the option strings are stripped. English in *_translated is
  the depositors' own (translation_source = study_supplied).

nurmalita_2026_* (Zenodo 10.5281/zenodo.22135733, CC BY 4.0). Indonesian administration.
  Kuesioner.pdf prints each statement beside its code (LK1..SK4); the codes are the
  Dataset.xlsx column names, kept unchanged by data/nurmalita_2026_paylater.py. The
  statements below are transcribed from `pdftotext -layout Kuesioner.pdf` (wrapped lines
  joined with one space, the hyphenated line break in SC4 "benar-/benar" rejoined as
  "benar-benar"), and this script asserts each one occurs in that text after whitespace
  is collapsed. Anchors are Codebook.pdf's "Skala Pengukuran" (1 Sangat Tidak Setuju ..
  5 Sangat Setuju), with the bracketed abbreviations (STS, TS, RG, S, SS) dropped. The
  English in *_translated was written by IRW (translation_source = machine_translation);
  it owes an itemtext_issues.qmd entry.
"""
import csv
import os
import re
import subprocess
import sys

import pandas as pd

COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]


def row(table, item, instrument, language, resp, item_text, option_text, item_tr, option_tr):
    return {"table": table, "section_id": f"{table}_1", "item": item, "instrument": instrument,
            "language": language, "instructions": "", "section_prompt": "", "item_text": item_text,
            "correct_response": "", "option_text": option_text, "resp": resp,
            "instructions_translated": "", "section_prompt_translated": "",
            "item_text_translated": item_tr, "option_text_translated": option_tr}


def write(table, rows, resp_dir, out_dir):
    resp = pd.read_csv(os.path.join(resp_dir, f"{table}.csv"))
    assert {r["item"] for r in rows} == set(resp["item"]), table
    assert {r["resp"] for r in rows} == set(resp["resp"].unique()), table
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, f"{table}__items.csv")
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{os.path.basename(p)}: {len(rows)} rows, {len({r['item'] for r in rows})} items")


def options(s):
    out = {}
    for part in s.split(";"):
        m = re.fullmatch(r"\s*(\d+)\s*=\s*(.+?)\s*", part)
        assert m, part
        out[int(m.group(1))] = m.group(2)
    return out


def lochmannova(src, resp_dir, out_dir):
    table = "lochmannova_2026_spa_environment"
    cb = pd.read_excel(os.path.join(src, "master_codebook.xlsx"), sheet_name="Codebook")
    rows = []
    for n in range(45, 53):
        hit = cb[cb["Variable (EN)"].str.match(rf"O{n}_")]
        assert len(hit) == 1, n
        r = hit.iloc[0]
        assert r["Instrument"] == "Nature Connectedness and Spa Environment (Non-standardized items)"
        cz, en = options(r["Response Options (CZ)"]), options(r["Response Options (EN)"])
        assert sorted(cz) == sorted(en) == [1, 2, 3, 4, 5]
        for k in range(1, 6):
            rows.append(row(table, f"O{n}",
                            "Spa environment items (study-specific, 'Non-standardized items'), "
                            "Lochmannova et al. 2026",
                            "Czech", k, r["Question (CZ)"].strip(), cz[k],
                            r["Question (EN)"].strip(), en[k]))
    write(table, rows, resp_dir, out_dir)


NURMALITA = {
    "nurmalita_2026_financial_literacy": ("Literasi Keuangan (financial literacy), 4 study-authored items, Nurmalita & Seillah 2026", {
        "LK1": ("Saya memahami perbedaan antara kebutuhan dan keinginan dalam mengelola keuangan",
                "I understand the difference between needs and wants in managing finances"),
        "LK2": ("Saya memahami pentingnya menyusun anggaran dalam mengelola keuangan pribadi",
                "I understand the importance of drawing up a budget in managing personal finances"),
        "LK3": ("Saya memahami risiko keterlambatan pembayaran utang atau cicilan",
                "I understand the risks of paying debts or instalments late"),
        "LK4": ("Saya memahami bahwa keputusan pembelian atau pinjaman perlu disesuaikan dengan kemampuan keuangan",
                "I understand that decisions to buy or to borrow need to be matched to financial capacity"),
    }),
    "nurmalita_2026_self_control": ("Self-Control, 4 study-authored items, Nurmalita & Seillah 2026", {
        "SC1": ("Saya mampu menahan diri untuk tidak membeli barang yang tidak direncanakan",
                "I am able to hold myself back from buying things I had not planned to buy"),
        "SC2": ("Saya berusaha membatasi pengeluaran agar tidak melebihi kemampuan keuangan saya",
                "I try to limit my spending so that it does not exceed my financial capacity"),
        "SC3": ("Saya dapat menunda membeli sesuatu apabila kondisi keuangan saya belum memungkinkan",
                "I can put off buying something if my financial situation does not yet allow it"),
        "SC4": ("Sebelum membeli barang, saya mempertimbangkan apakah barang tersebut benar-benar dibutuhkan",
                "Before buying something, I consider whether it is really needed"),
    }),
    "nurmalita_2026_paylater_use": ("Intensitas Penggunaan Paylater (paylater usage intensity), 4 study-authored items, Nurmalita & Seillah 2026", {
        "IP1": ("Saya sering menggunakan paylater saat berbelanja",
                "I often use paylater when shopping"),
        "IP2": ("Saya menggunakan paylater untuk berbagai jenis kebutuhan atau pembelian",
                "I use paylater for many different kinds of needs or purchases"),
        "IP3": ("Saya menjadikan paylater sebagai salah satu metode pembayaran yang digunakan secara rutin",
                "I have made paylater one of the payment methods I use routinely"),
        "IP4": ("Saya cenderung memilih paylater meskipun tersedia metode pembayaran lain",
                "I tend to choose paylater even when other payment methods are available"),
    }),
    "nurmalita_2026_financial_stability": ("Stabilitas Keuangan (financial stability), 4 study-authored items, Nurmalita & Seillah 2026", {
        "SK1": ("Saya mampu membayar tagihan atau cicilan tepat waktu",
                "I am able to pay bills or instalments on time"),
        "SK2": ("Pemasukan saya cukup untuk memenuhi kebutuhan dan pengeluaran rutin",
                "My income is enough to cover my needs and routine expenses"),
        "SK3": ("Saya masih dapat menyisihkan sebagian pendapatan untuk ditabung",
                "I can still set aside part of my income to save"),
        "SK4": ("Saya memiliki cadangan dana untuk menghadapi kebutuhan mendadak",
                "I have reserve funds to deal with sudden needs"),
    }),
}
ANCHORS = {1: ("Sangat Tidak Setuju", "Strongly disagree"), 2: ("Tidak Setuju", "Disagree"),
           3: ("Ragu-ragu", "Undecided"), 4: ("Setuju", "Agree"), 5: ("Sangat Setuju", "Strongly agree")}


def pdf_text(path):
    t = subprocess.run(["pdftotext", "-layout", path, "-"], check=True, capture_output=True,
                       text=True).stdout
    return t


def nurmalita(src, resp_dir, out_dir):
    kues = pdf_text(os.path.join(src, "Kuesioner.pdf"))
    # drop the code column and collapse the wrapped layout into one line of prose
    flat = re.sub(r"\b(LK|SC|IP|SK)[1-4]\b", " ", kues)
    flat = re.sub(r"-\s*\n\s*", "-", flat)
    flat = re.sub(r"\s+", " ", flat)
    for code in [c for _, (_, items) in NURMALITA.items() for c in items]:
        assert re.search(rf"\b{code}\b", kues), code
    cb = re.sub(r"\s+", " ", pdf_text(os.path.join(src, "Codebook.pdf")))
    for k, (idn, _) in ANCHORS.items():
        assert re.search(rf"\b{k} {re.escape(idn)} \(", cb), (k, idn)
    for table, (instrument, items) in NURMALITA.items():
        rows = []
        for code, (idn, en) in items.items():
            assert idn in flat, (code, idn)
            for k, (o_idn, o_en) in ANCHORS.items():
                rows.append(row(table, code, instrument, "Indonesian", k, idn, o_idn, en, o_en))
        write(table, rows, resp_dir, out_dir)


if __name__ == "__main__":
    loch, nurm, resp_dir, out_dir = sys.argv[1:5]
    lochmannova(loch, resp_dir, out_dir)
    nurmalita(nurm, resp_dir, out_dir)
