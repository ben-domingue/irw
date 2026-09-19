#!/usr/bin/env python3
# Source: OpenEval, Hugging Face dataset Open-Eval-Commons/OpenEval, config `response`, split `ifeval`
# Revision (pinned): 23a1ded985b3c2cdaaddb27581a35bfabe0ad7e7 (HF lastModified 2026-09-05)
# Paper: Jiang et al. (2026), "AI Evaluation Should Require Standardized Item-Level Data Releases",
#        arXiv 2604.03244 (v2), doi:10.48550/arXiv.2604.03244
# Benchmark: IFEval (Zhou et al. 2023, arXiv 2311.07911), 541 instruction-following prompts
# License: CC BY-NC 4.0. The OpenEval authors confirmed by email to Ben Domingue (2026-09-16)
#          that CC BY-NC 4.0 is authoritative and granted IRW inclusion of the model x item
#          score tables, with credit to the repository and paper. NC approved for IRW by Ben
#          (ben-domingue/irw#2166).
#
# Respondents are AI MODELS, not people. `id` is OpenEval's `model.name`, verbatim.
#   - Name aliases are NOT merged: e.g. gpt-3.5-turbo and gpt-3.5-turbo-0613 are separate ids,
#     as are case variants. OpenEval has no family/provider/version field to merge on.
#   - Models sharing base weights (fine-tunes, sizes of one family) are not independent
#     respondents; local independence across `id` should not be assumed.
#   - Items may be in some models' training data.
#
# Scores only. No item text or model output is included: IFEval prompts are published by
# their authors, but OpenEval's grant covers the response data, not benchmark content.
# `item` is OpenEval's `item_id` (ifeval_20260421T021146Z_<k>, k = 0..540; it is not the
# original IFEval `key`).
#
# resp: the number of the prompt's verifiable instructions the response satisfied, under
#   IFEval's STRICT check. OpenEval stores this as a proportion (metric `ifeval_strict_accuracy`,
#   values 0, 1/3, 1/2, 2/3, 1); resp = proportion x itemcov_n_instructions, which is an exact
#   integer for every row (asserted below). So:
#     resp / itemcov_n_instructions  == OpenEval's ifeval_strict_accuracy (instruction level)
#     resp == itemcov_n_instructions == IFEval's prompt-level strict accuracy (0/1)
#   The loose metric is not in OpenEval. No LLM judge is involved (the check is programmatic),
#   so there is no `rater` column.
# itemcov_n_instructions: number of verifiable instructions in the prompt, the length of
#   `instruction_id_list` in OpenEval's item table (read for that field only; the prompt text
#   is discarded). The instruction ids themselves are not kept.
#
# Selection rules:
#   - Run: OpenEval marks replicate runs only by a trailing `_N` on response_id. At this
#     revision every ifeval response is run 0 and there is exactly one row per model x item;
#     both are asserted, so a later revision with replicates stops here instead of shipping them.
#   - Metric: the only one present (ifeval_strict_accuracy).
#   - Models: all 124 are kept, including the two under 90% item coverage (min 50 items).
# cov_model_size: OpenEval's `model.size` string as given (e.g. "2b", "70b"); NA where blank.
# cov_temperature: sampling temperature from `generation_parameters` (0 for 64,479 rows;
#   1.0 and 0.6 for the rest). Decoding is therefore not uniform across models.

import io
import json
import os
import re

import pandas as pd
import pyarrow.parquet as pq
import requests

REPO = "Open-Eval-Commons/OpenEval"
REV = "23a1ded985b3c2cdaaddb27581a35bfabe0ad7e7"
BASE = f"https://huggingface.co/datasets/{REPO}/resolve/{REV}"
RESPONSE_FILES = [f"response/ifeval-0000{i}-of-00004.parquet" for i in range(4)]
ITEM_FILE = "item/ifeval-00000-of-00001.parquet"
METRIC = "ifeval_strict_accuracy"
TABLE = "jiang_2026_openeval_ifeval"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
##Optional local copy of the pinned revision (same relative paths), to skip ~280 MB of downloads.
CACHE = os.environ.get("OPENEVAL_CACHE",
                       os.path.expanduser(f"~/.cache/irw/openeval/{REV}"))


def read_parquet(path, columns):
    local = os.path.join(CACHE, path)
    if os.path.exists(local):
        return pq.read_table(local, columns=columns)
    r = requests.get(f"{BASE}/{path}", timeout=600)
    r.raise_for_status()
    return pq.read_table(io.BytesIO(r.content), columns=columns)


def convert():
    n_instr = {}
    for r in read_parquet(ITEM_FILE, ["item_id", "item_content"]).to_pylist():
        (content,) = r["item_content"]["input"]
        n_instr[r["item_id"]] = len(json.loads(content)["instruction_id_list"])
    assert len(n_instr) == 541

    rows = []
    for path in RESPONSE_FILES:
        ##response_content is ~98% of the bytes and is never read.
        for r in read_parquet(path, ["response_id", "model", "scores"]).to_pylist():
            model = r["model"]["name"]
            m = re.match(r"^(.*)_" + re.escape(model) + r"_(\d+)$", r["response_id"])
            assert m, r["response_id"]
            item, run = m.group(1), int(m.group(2))
            metrics = r["scores"]["metric"]
            assert [x["name"] for x in metrics] == [METRIC], r["response_id"]
            assert metrics[0]["models"] == [], "unexpected judge model"
            gen = r["model"]["model_adaptation"]["generation_parameters"]
            rows.append({
                "id": model,
                "item": item,
                "run": run,
                "prop": r["scores"]["value"][0],
                "cov_model_size": r["model"]["size"] or None,
                "cov_temperature": json.loads(gen).get("temperature") if gen else None,
                "itemcov_n_instructions": n_instr[item],
            })
    d = pd.DataFrame(rows)

    assert d["item"].isin(n_instr).all()
    assert (d["run"] == 0).all(), "replicate runs present: choose a run rule before shipping"
    assert not d.duplicated(["id", "item"]).any()

    count = d["prop"] * d["itemcov_n_instructions"]
    assert (count - count.round()).abs().max() < 1e-6, "proportion x n is not an integer"
    d["resp"] = count.round().astype(int)
    assert d["resp"].between(0, d["itemcov_n_instructions"]).all()

    d = d[["id", "item", "resp", "cov_model_size", "cov_temperature", "itemcov_n_instructions"]]
    d = d.sort_values(["id", "item"], key=lambda s: s.map(
        lambda v: int(v.rsplit("_", 1)[1]) if s.name == "item" else v)).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"{TABLE}.csv")
    d.to_csv(out, index=False)
    print(f"{TABLE}: {len(d)} rows, {d['id'].nunique()} models, {d['item'].nunique()} items -> {out}")


if __name__ == "__main__":
    convert()
