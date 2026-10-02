"""semeval2013_scientsbank_nom: SemEval-2013 Task 7, SciEntsBank half (#2651).

Source: https://github.com/myrosia/semeval-2013-task7, commit 5157c69f, file
semeval-5way.zip (pinned by sha256) -> sciEntsBank/{train,test-unseen-answers,
test-unseen-questions,test-unseen-domains}/Core/*.xml. The `reliability/` folder
(re-annotation rounds of a few questions) is not used.

Dzikovska, M. O., Nielsen, R., Brew, C., Leacock, C., Giampiccolo, D., Bentivogli,
L., Clark, P., Dagan, I., & Dang, H. T. (2013). SemEval-2013 Task 7: The Joint
Student Response Analysis and 8th Recognizing Textual Entailment Challenge.
SemEval 2013, 263-274. https://aclanthology.org/S13-2045/
Underlying corpus: Nielsen, Ward, Martin & Palmer (2008), Annotating students'
understanding of science concepts, LREC 2008 (https://aclanthology.org/L08-1166/):
written answers of grade 3-6 students to FOSS / ASK science assessments.

Licence: README "It is licensed under the Creative Commons Attribution-Share Alike
License (CC-BY-SA)"; the repo's LICENSE file is CC BY-SA 3.0 Unported. ShareAlike
carries through to this table.

The Beetle half of the task is not built: 35 student ids, under the 100-id floor.

Person id
Each answer id is <module>.<question>.<student>.<n>, e.g. EM.45b.110.1. The
student field is the person. No paper spells the id format out, so it was checked
against the design Nielsen et al. (2008) describe: "random selection of students
was performed at the question level ... in total there were only about 200
children that participated in any individual science module assessment, so there
is still moderate overlap in the students from one question to another within a
given module. On the other hand, each assessment module was given to a different
group of children, so there is no overlap in students between modules." In the
data a student number answers up to 21 questions of its module and never answers
one question twice, and each module has 99-311 distinct numbers. The same numbers
recur across modules, which the paper says are different children, so
id = <module>_<student> (e.g. EM_110). <n> is 1 for every answer.

- 36 answers carry the student field "xx-<k>": no student number, so they cannot
  be linked to a person, and they are dropped. They are every answer to ME_28b,
  so that question drops out (195 items remain).
- 16 student fields carry an a/b suffix (e.g. HB.46.179a): each is a second,
  different answer to a question that the plain number (HB.46.179) also answered,
  i.e. a number shared by two answer sheets. They are kept as their own ids
  (HB_179a), not merged into the plain number.

Mapping
- id     = <module>_<student>, as above
- item   = question id (e.g. EM_45b); question ids are unique across modules
- text   = the 5-way accuracy label: correct / partially_correct_incomplete /
           contradictory / irrelevant / non_domain. This is the nominal category:
           the graders' classification of the free-text answer, not an option
           the student chose.
- resp   = 1 if the label is correct, else 0: the task's own 2-way scheme
           ("correct" vs "incorrect", every non-correct label collapsing to
           incorrect)
- answer_text = the student's written answer as transcribed (spelling fixed by
           the transcribers, per Nielsen et al. 2008)
- itemcov_module = the FOSS module code (EM, EV, FN, HB, II, LF, LP, ME, MS, MX,
           PS, SE, ST, VB, WA)
- split  = train / test-unseen-answers / test-unseen-questions /
           test-unseen-domains, the SemEval partition the answer sits in
"""
import hashlib
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "semeval2013_scientsbank_nom"
COMMIT = "5157c69f914e8c581045c03e98f96398d40a91b8"
URL = f"https://raw.githubusercontent.com/myrosia/semeval-2013-task7/{COMMIT}/semeval-5way.zip"
SHA256 = "57c14e5c260d8cfd774f3fb954985d94bcfa3407029bfe585179650b907dbf9b"
CACHE = Path.home() / ".cache" / "irw-nominal" / "semeval2013" / "semeval-5way.zip"
SPLITS = ["train", "test-unseen-answers", "test-unseen-questions", "test-unseen-domains"]
LABELS = {"correct", "partially_correct_incomplete", "contradictory", "irrelevant", "non_domain"}

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(URL, CACHE)
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

rows = []
with zipfile.ZipFile(CACHE) as z:
    for split in SPLITS:
        names = sorted(n for n in z.namelist()
                       if n.startswith(f"sciEntsBank/{split}/Core/") and n.endswith(".xml"))
        assert names, split
        for n in names:
            q = ET.fromstring(z.read(n))
            for sa in q.iter("studentAnswer"):
                rows.append((split, q.get("module"), q.get("id"), sa.get("id"),
                             sa.get("accuracy"), sa.text))
d = pd.DataFrame(rows, columns=["split", "module", "item", "aid", "label", "answer_text"])
assert len(d) == 10804 and d["item"].nunique() == 196 and not d["aid"].duplicated().any()

parts = d["aid"].str.split(".", expand=True)
assert parts.shape[1] == 4 and (parts[0] == d["module"]).all() and (parts[3] == "1").all()
d["stu"] = parts[2]
assert (d.groupby("item")["module"].nunique() == 1).all()

xx = d["stu"].str.startswith("xx-")
assert int(xx.sum()) == 36 and set(d.loc[xx, "item"]) == {"ME_28b"}
assert (d.loc[d["item"] == "ME_28b", "stu"].str.startswith("xx-")).all()
d = d[~xx]
assert d["stu"].str.fullmatch(r"\d+[ab]?").all()
assert int(d["stu"].str.fullmatch(r"\d+[ab]").sum()) == 16
assert set(d["label"]) == LABELS
assert d["answer_text"].notna().all()

d["answer_text"] = d["answer_text"].str.strip().str.replace(r"\s+", " ", regex=True)
df = pd.DataFrame({
    "id": d["module"] + "_" + d["stu"],
    "item": d["item"],
    "resp": (d["label"] == "correct").astype(int),
    "text": d["label"],
    "answer_text": d["answer_text"],
    "itemcov_module": d["module"],
    "split": d["split"],
}).sort_values(["id", "item"], kind="stable").reset_index(drop=True)
assert not df.duplicated(["id", "item"]).any()
assert df["id"].nunique() >= 100

pv = {i: {0, 1} for i in df["item"].unique()}
checks = run_qc(df.drop(columns=["text", "answer_text"]), permitted_values=pv)
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails

out = Path(f"{TABLE}.csv")
df.to_csv(out, index=False)
rep = irw_validate.validate_file(str(out), profile="upload", context={"permitted_values": pv})
assert rep.conforms and not rep.errors, [(f.check, f.message) for f in rep.errors]
for f in rep.findings:
    print(f"    [{f.severity}] {f.check}: {f.message}")
print(TABLE, "rows", len(df), "ids", df["id"].nunique(), "items", df["item"].nunique(),
      "categories", df["text"].nunique())
print(df["text"].value_counts().to_string())
