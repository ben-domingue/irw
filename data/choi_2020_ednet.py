"""choi_2020_ednet_{listening,reading} (+ _nom companions) -- issue #1949.

Source: EdNet KT1 (Santa, a Korean TOEIC tutoring app, run by Riiid).
Choi, Y., Lee, Y., Shin, D., Cho, J., Park, S., Lee, S., Baek, J., Bae, C.,
Kim, B., & Heo, J. (2020). EdNet: A large-scale hierarchical dataset in
education. In Artificial Intelligence in Education (AIED 2020), LNCS 12164,
69-73. https://doi.org/10.1007/978-3-030-52240-7_13
Documentation: https://github.com/riiid/ednet (the README is the spec).
Downloads (Google Drive via the README's bit.ly links, fetched 2026-09-30):
  KT1.zip       bit.ly/ednet_kt1     -> 784,309 files KT1/u<id>.csv
  contents.zip  bit.ly/ednet-content -> contents/questions.csv (13,169 rows)
Both are cached in ~/.cache/irw_ednet; this script reads them from there.

Licence: CC BY-NC 4.0 ("for research purposes", README). Taken as an approved
exception to the no-NC rule (#1590, #1949); Derived_License stays CC BY-NC 4.0.

KT1 columns: timestamp (Unix ms), solving_id, question_id, user_answer (a-d),
elapsed_time (ms). The student id appears only in the file name.

Mapping
- id            = the number in the file name (u246317.csv -> 246317)
- item          = question_id
- resp          = user_answer == correct_answer (questions.csv), 0/1
- resp_raw      = user_answer, the letter picked
- rt            = elapsed_time / 1000 (seconds); values <= 0 set missing
- date          = timestamp // 1000 (Unix seconds)
- item_family   = bundle_id (questions sharing a passage or audio clip)
- itemcov_part  = part, 1-7 (TOEIC section)
Split, per #1949 (Ben, 2026-09-08): listening = parts 1-4, reading = parts
5-7, one table each.

Dropped, and counted in the printed summary:
- rows whose question_id is not in questions.csv (cannot be scored)
- rows with an empty user_answer (non-response)
Repeated id-item rows are real (students re-solve questions) and are kept;
`date` orders them.

The _nom companions are the same frames with resp_raw renamed to `text`
(datastandard.md, "The raw response and the nominal tranche"), written by
renaming the header line of the finished core file.

Every chunk of students is passed through run_qc before it is written, so the
validator sees every row without holding the ~131M rows in memory at once.
"""
import csv
import io
import re
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

CACHE = Path.home() / ".cache" / "irw_ednet"
KT1 = CACHE / "KT1.zip"
QUESTIONS = CACHE / "contents" / "questions.csv"
NAMES = {"listening": "choi_2020_ednet_listening", "reading": "choi_2020_ednet_reading"}
COLS = ["id", "item", "resp", "resp_raw", "rt", "date", "item_family", "itemcov_part"]
CHUNK = 25_000  # students per validated chunk

q = pd.read_csv(QUESTIONS, dtype=str)
KEY = dict(zip(q.question_id, q.correct_answer))
PART = dict(zip(q.question_id, q.part.astype(int)))
BUNDLE = dict(zip(q.question_id, q.bundle_id))
LETTERS = {"a", "b", "c", "d"}

stats = Counter()
outs = {k: open(f"{v}.csv", "w", newline="") for k, v in NAMES.items()}
writers = {k: csv.writer(f) for k, f in outs.items()}
for w in writers.values():
    w.writerow(COLS)


def flush(rows):
    """Validate one chunk and append it to the two core files."""
    if not rows:
        return
    df = pd.DataFrame(rows, columns=COLS)
    df["rt"] = df["rt"].astype(float)
    checks = run_qc(df, permitted_values={i: {0, 1} for i in df["item"].unique()})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    listening = df["itemcov_part"] <= 4
    for key, part in (("listening", df[listening]), ("reading", df[~listening])):
        part.to_csv(outs[key], header=False, index=False, na_rep="")
        stats[f"rows_{key}"] += len(part)


rows = []
with zipfile.ZipFile(KT1) as z:
    members = [m for m in z.namelist() if re.fullmatch(r"KT1/u\d+\.csv", m)]
    stats["files"] = len(members)
    for n, m in enumerate(members, 1):
        sid = int(m[len("KT1/u"):-len(".csv")])
        text = z.read(m).decode("utf-8")
        reader = csv.reader(io.StringIO(text))
        header = next(reader)
        assert header == ["timestamp", "solving_id", "question_id", "user_answer", "elapsed_time"], (m, header)
        for ts, _solving, qid, ans, elapsed in reader:
            stats["source_rows"] += 1
            if qid not in KEY:
                stats["dropped_unknown_question"] += 1
                continue
            if ans == "":
                stats["dropped_blank_answer"] += 1
                continue
            if ans not in LETTERS:
                stats[f"odd_answer_{ans}"] += 1
            e = int(elapsed)
            rows.append((sid, qid, int(ans == KEY[qid]), ans,
                         e / 1000 if e > 0 else np.nan, int(ts) // 1000,
                         BUNDLE[qid], PART[qid]))
            if e <= 0:
                stats["rt_nonpositive"] += 1
        if n % CHUNK == 0:
            flush(rows)
            rows = []
            print(f"{n:,}/{len(members):,} files", dict(stats), flush=True)
    flush(rows)

for f in outs.values():
    f.close()

# _nom companions: identical rows, resp_raw -> text in the header only.
for name in NAMES.values():
    with open(f"{name}.csv") as src, open(f"{name}_nom.csv", "w") as dst:
        head = src.readline()
        assert head.strip() == ",".join(COLS)
        dst.write(head.replace("resp_raw", "text"))
        shutil.copyfileobj(src, dst, length=16 * 1024 * 1024)

print("done", dict(stats))
