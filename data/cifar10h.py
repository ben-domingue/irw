"""cifar10h (+ cifar10h_nom): CIFAR-10H human labels of the CIFAR-10 test set (#2655).

Source: Peterson, J. C., Battleday, R. M., Griffiths, T. L., & Russakovsky, O.
(2019). Human uncertainty makes classification more robust. Proceedings of the
IEEE/CVF International Conference on Computer Vision (ICCV), 9617-9626,
doi:10.1109/ICCV.2019.00971. Data: https://github.com/jcpeterson/cifar-10h,
data/cifar10h-raw.zip at commit 389f22d9 (pinned by sha256).

Licence: LICENSE.txt, "made available under Creative Commons BY-NC-SA 4.0
license" (checked 2026-10-01). Ruled hostable 10-01 (non-commercial; NC and
ShareAlike carried into Derived License).

The raw file has one row per trial: 2,571 Mechanical Turk annotators, each
shown 200 CIFAR-10 test images plus 10 attention checks, choosing one of the
ten CIFAR-10 classes. Ruled 10-01 (#2655): build a keyed core + _nom pair.

Mapping
- id       = annotator_id (the repo's own integer, not the MTurk worker id)
- item     = img_<cifar10_test_set_idx> (the image's index in the CIFAR-10
             test set, 0-9999)
- resp     = 1 if the chosen class is the image's CIFAR-10 label, else 0
             (the source's own correct_guess; asserted equal)
- resp_raw = the chosen class name (airplane ... truck)
- rt       = reaction_time / 1000 (seconds); missing for the 12 trials whose
             recorded reaction_time is negative
- itemcov_true_category = the CIFAR-10 label of the image (the key)
- itemcov_subcategory   = the source's subordinate class (from the filename)
- trial_index           = the trial's position in the annotator's session

Attention-check trials (is_attn_check == 1; test index -99999) are dropped:
they are not images of the test set. The nominal companion is the same table
with resp_raw renamed to `text` (datastandard.md, "The raw response and the
nominal tranche").
"""
import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

URL = ("https://github.com/jcpeterson/cifar-10h/raw/"
       "389f22d9d300ec71a4c44735d46f550c94b957ab/data/cifar10h-raw.zip")
SHA256 = "4b0283f9b2ae72a616eeb4a2a38474cc2a238eb041bfb8df5ead3a8a47f35aa3"
CACHE = Path.home() / ".cache" / "irw-nominal" / "cifar10h" / "cifar10h-raw.zip"
CLASSES = ["airplane", "automobile", "bird", "cat", "deer",
           "dog", "frog", "horse", "ship", "truck"]

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

with zipfile.ZipFile(CACHE) as z, z.open("cifar10h-raw.csv") as f:
    x = pd.read_csv(f)
assert x["annotator_id"].nunique() == 2571
assert (x.groupby("annotator_id")["is_attn_check"].sum() == 10).all()

x = x[x["is_attn_check"] == 0].copy()
assert len(x) == 514200 and x["cifar10_test_test_idx"].between(0, 9999).all()
assert x["cifar10_test_test_idx"].nunique() == 10000
assert set(x["chosen_category"]) == set(CLASSES) == set(x["true_category"])
## class names and integer labels agree (README mapping)
assert (x["true_category"].map(CLASSES.index) == x["true_label"]).all()
assert (x["chosen_category"].map(CLASSES.index) == x["chosen_label"]).all()
resp = (x["chosen_category"] == x["true_category"]).astype(int)
assert (resp == x["correct_guess"]).all()
## each image has one true label and one subcategory
img = x.groupby("cifar10_test_test_idx")
assert (img["true_category"].nunique() == 1).all() and (img["subcategory"].nunique() == 1).all()

df = pd.DataFrame({
    "id": x["annotator_id"],
    "item": "img_" + x["cifar10_test_test_idx"].astype(str),
    "resp": resp,
    "resp_raw": x["chosen_category"],
    "rt": x["reaction_time"] / 1000,
    "itemcov_true_category": x["true_category"],
    "itemcov_subcategory": x["subcategory"],
    "trial_index": x["trial_index"],
}).sort_values(["id", "trial_index"], kind="stable")
assert not df.duplicated(["id", "item"]).any()
## 12 trials carry a negative reaction_time (a logging error); rt is left missing there
neg = df["rt"] <= 0
assert int(neg.sum()) == 12
df.loc[neg, "rt"] = float("nan")

pv = {i: {0, 1} for i in df["item"].unique()}
checks = run_qc(df, permitted_values=pv)
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails

df.to_csv("cifar10h.csv", index=False)
rep = irw_validate.validate_file("cifar10h.csv", profile="upload",
                                 context={"permitted_values": pv})
assert rep.conforms and not rep.errors, [(f.check, f.message) for f in rep.errors]
for f in rep.findings:
    print(f"    [{f.severity}] {f.check}: {f.message}")

df.rename(columns={"resp_raw": "text"}).to_csv("cifar10h_nom.csv", index=False)
print(len(df), df["id"].nunique(), df["item"].nunique(), round(df["resp"].mean(), 4))
