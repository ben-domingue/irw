#!/usr/bin/env python3
# Source: OpenEval, Hugging Face dataset Open-Eval-Commons/OpenEval, config `response`
# Revision (pinned): 23a1ded985b3c2cdaaddb27581a35bfabe0ad7e7 (HF lastModified 2026-09-05), the
#   revision the ifeval table uses and the one in place when the authors granted permission
#   (2026-09-16). Later revisions add models and a benchmark (dochop, 2026-09-27) from
#   contributors outside the author group; they are not covered by that grant and are not read.
# Paper: Jiang et al. (2026), "AI Evaluation Should Require Standardized Item-Level Data Releases",
#        arXiv 2604.03244 (v2), doi:10.48550/arXiv.2604.03244
# License: CC BY-NC 4.0. The OpenEval authors confirmed by email to Ben Domingue (2026-09-16)
#          that CC BY-NC 4.0 is authoritative and that all response data then in OpenEval are
#          managed by them, and granted IRW inclusion of the model x item score tables, with
#          credit to the repository and paper. NC approved for IRW by Ben (ben-domingue/irw#2166).
#          Scope widened from ifeval to the benchmarks below by Ben, 2026-09-30.
#
# Writes 20 tables, one per benchmark (harmbench and bbq are two each), listed in TABLES below.
# IFEval is built separately by jiang_2026_openeval_ifeval.py. Ben set a floor of 50 models for
# these AI-respondent tables (2026-09-30), in place of IRW's usual 100 respondents, so boolq and
# imdb (22 models each) are not built. Also not built: cnndm, xsum, bold, disinformation (text-similarity,
# log-probability and diversity metrics, not item scores), salad-bench (exact match is 0 on
# every row) and moralbench (at the pinned revision its continuous human-weighted scores are
# labelled prefix_exact_match alongside the binary ones, so the two cannot be told apart; 11
# models in any case). do-not-answer is not built here: its judge assigns one of seven
# unordered response types (0 refused ... 6 followed the instruction directly), which is a
# nominal response, not a score.
#
# Respondents are AI MODELS, not people. `id` is OpenEval's `model.name`, verbatim.
#   - Name aliases are NOT merged: gpt-3.5-turbo and gpt-3.5-turbo-0613 are separate ids, as are
#     case variants (Llama-3.2-3B-Instruct / llama-3.2-3b-instruct come from different
#     contributors). OpenEval has no family/provider/version field to merge on.
#   - Models sharing base weights (fine-tunes, sizes of one family) are not independent
#     respondents; local independence across `id` should not be assumed.
#   - Items may be in some models' training data.
#   - Many models were scored on only part of a benchmark (mmlu-pro and omni-math sample items
#     per model); every model is kept, however few items it has.
#
# Scores only. No item text, model output or judge rationale is included: OpenEval's grant
# covers the response data, not benchmark content (GPQA, for one, asks that its questions not
# be republished in plain text). `item` is OpenEval's `item_id` (<benchmark>_<timestamp>_<k>),
# not the benchmark's own question id. emobench's Emotional Understanding items ask two
# questions each, so they appear as <item_id>_emotion and <item_id>_cause.
#
# resp: the value of ONE OpenEval metric per benchmark (METRIC below), unchanged. DIRECTION
#   VARIES BY TABLE and is not harmonised; each table's dictionary row states it. In particular
#   `refusal-strings` is 1 = complied (no refusal phrase) and 0 = refused, while `orbench-refusal`
#   is 1 = refused; the HarmBench classifier is 1 = harmful. anthropic_redteam is HELM's
#   five-point harmlessness rating (0, 0.25, 0.5, 0.75, 1 = completely harmless); wildbench is
#   the judge's 1-10 checklist score. The HELM safety score (xstest, simplesafetytests,
#   harmbench_helm) is 0 / 0.5 (unclear) / 1 where 1 is
#   the behaviour the prompt calls for: refusing (or explaining risks) on an unsafe prompt, but
#   COMPLYING on a safe one -- XSTest mixes both kinds of prompt. Checked against OpenEval's per-response `label` artifacts.
# rater: the LLM judge that produced the score, as OpenEval names it in `scores.metric.models`
#   (e.g. openai/gpt-4o-2024-05-13), for the benchmarks scored by LLM judges. Where several
#   judges scored the same responses there is one row per judge. OpenEval's cross-judge averages
#   (omni_math_accuracy, wildbench_score_rescaled) are not kept: they are the mean of these rows.
#   Programmatic scores (exact match, string match, BLEURT threshold) have no `rater` column.
#   A judge score of -1 (the judge's output could not be parsed) is dropped as missing. 88
#   sorry_bench rows carry a blank judge list on a metric whose every other row names one judge;
#   given that judge, each is an exact duplicate of a named row and collapses.
#
# Selection rules, all asserted:
#   - Run: OpenEval marks runs only by a trailing `_N` on response_id. Most models have run 0
#     only. Where a model has several runs of an item, the LOWEST run is kept; this also keeps a
#     model that appears only as run 1 (OpenEval uses the run number to separate two
#     configurations whose names differ only in case). The runs dropped are counted below.
#   - Exact duplicate rows (same response_id, metric, judge and value) are collapsed (1,227 in
#     culturalbench); a
#     duplicate with a different value stops the script unless EXCLUDE names it: in bbq_helm,
#     falcon-40b-instruct and falcon-7b-instruct (every item stored twice, 433 pairs disagreeing)
#     and item bbq_20260331T215816Z_45056 (stored twice for every model) are left out.
#   - hi_tom and emobench are read from revision ceb4f916f09f041a68e4fc922f110013cf769e58
#     (2026-09-30), not the pinned one. At the pinned revision 40 hi_tom models (sampled at
#     temperature 1) and one emobench model store every affected item twice under the same run-0
#     response_id, disagreeing on 4,659 and 11 cells, and OpenEval kept the first copy in one case
#     and the second in the other, so no rule recovers the right one. At ceb4f916 OpenEval removed
#     the extra copies; checked 2026-09-30, both splits there are an exact subset of the pinned
#     revision (every row identical, same models, nothing added), so the grant still covers them.
#   - Two metrics per benchmark are never mixed in one table. harmbench carries two scorings that
#     point in opposite directions and were applied to different models, so it is two tables.
#     bbq is two contributions: `accuracy` on 58,492 items (50 models) and HELM's exact-match
#     family on a different 1,000 items (59 models); the HELM one is bbq_helm, using quasi exact
#     match (case- and whitespace-normalised).
#     truthfulqa keeps `bleurt-20` (186 models); 36 models scored only with lm-eval's BLEURT
#     variant (a different checkpoint) are not in the table.
# cov_model_size: OpenEval's `model.size` string as given (e.g. "2b", "70b"); NA where blank.
# cov_temperature: sampling temperature from `generation_parameters`; NA where not recorded.
#   Decoding is not uniform across models.
#
# Reading: only the response_id, model and scores columns are fetched, by HTTP range request,
# so the ~98% of each file that is model output is never downloaded. A compact copy is cached
# under ~/.cache/irw/openeval/<rev>/scores/ (override the root with OPENEVAL_CACHE).

import io
import json
import os
import re
import sys

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

from irw_validate.compat import run_qc

REPO = "Open-Eval-Commons/OpenEval"
REV = "23a1ded985b3c2cdaaddb27581a35bfabe0ad7e7"
##Splits read from a later revision (see header): duplicates removed, nothing added.
SPLIT_REV = {s: "ceb4f916f09f041a68e4fc922f110013cf769e58" for s in ("hi_tom", "emobench")}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
CACHE = os.environ.get("OPENEVAL_CACHE", os.path.expanduser("~/.cache/irw/openeval"))

##table: (OpenEval split, {metric: item suffix}, judged)
##`judged` tables carry a `rater` column; their metric names are matched by the judge list.
TABLES = {
    "jiang_2026_openeval_gpqa": ("gpqa", {"chain_of_thought_correctness": ""}, False),
    "jiang_2026_openeval_mmlu_pro": ("mmlu_pro", {"chain_of_thought_correctness": ""}, False),
    "jiang_2026_openeval_bbq": ("bbq", {"accuracy": ""}, False),
    "jiang_2026_openeval_bbq_helm": ("bbq", {"quasi_exact_match": ""}, False),
    "jiang_2026_openeval_culturalbench": ("culturalbench", {"quasi_prefix_exact_match": ""}, False),
    "jiang_2026_openeval_emobench": ("emobench", {"quasi_exact_match": "",
                                                  "emotion_quasi_exact_match": "_emotion",
                                                  "cause_quasi_exact_match": "_cause"}, False),
    "jiang_2026_openeval_hi_tom": ("hi_tom", {"quasi_prefix_exact_match": ""}, False),
    "jiang_2026_openeval_opentom": ("opentom", {"quasi_postfix_exact_match": ""}, False),
    "jiang_2026_openeval_truthfulqa": ("truthfulqa", {"bleurt-20": ""}, False),
    "jiang_2026_openeval_advbench": ("advbench", {"refusal-strings": ""}, False),
    "jiang_2026_openeval_health_orsc_bench": ("health_orsc_bench", {"refusal-strings": ""}, False),
    "jiang_2026_openeval_harmbench": ("harmbench", {"haiku-llm-judge": ""}, True),
    "jiang_2026_openeval_harmbench_helm": ("harmbench", {"safety_gpt_score": "",
                                                         "safety_llama_score": ""}, True),
    "jiang_2026_openeval_or_bench": ("or_bench", {"orbench-refusal": ""}, True),
    "jiang_2026_openeval_sorry_bench": ("sorry_bench", {"ft-mistral-7b-sorrybench": ""}, True),
    "jiang_2026_openeval_xstest": ("xstest", {"safety_gpt_score": "", "safety_llama_score": ""}, True),
    "jiang_2026_openeval_simplesafetytests": ("simplesafetytests", {"safety_gpt_score": "",
                                                                    "safety_llama_score": ""}, True),
    "jiang_2026_openeval_anthropic_redteam": ("anthropic_red_teaming", {"safety_gpt_score": "",
                                                                        "safety_llama_score": ""}, True),
    "jiang_2026_openeval_omni_math": ("omni_math", {"*_correctness": ""}, True),
    "jiang_2026_openeval_wildbench": ("wildbench", {"gpt_score": "", "llama_score": "",
                                                    "claude_score": ""}, True),
}

##Cells OpenEval stores twice with different values, where no rule picks the right copy. Named
##here so the script still stops on any conflict not listed.
EXCLUDE = {
    ##Every item stored twice at temperature 0 under the same response_id, 433 pairs disagreeing:
    ##two runs under one label.
    "jiang_2026_openeval_bbq_helm": {
        "models": ["falcon-40b-instruct", "falcon-7b-instruct"],
        ##Stored twice for all 57 other models, disagreeing for 14: two questions sharing an id.
        "items": ["bbq_20260331T215816Z_45056"],
    },
}


class RangeFile(io.RawIOBase):
    """A seekable HTTP file read by Range request, so pyarrow fetches only the columns it needs."""

    def __init__(self, url):
        self.s = requests.Session()
        r = self.s.head(url, allow_redirects=True, timeout=60)
        r.raise_for_status()
        self.url, self.size, self.pos = r.url, int(r.headers["Content-Length"]), 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = {0: off, 1: self.pos + off, 2: self.size + off}[whence]
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        if n == 0 or self.pos >= self.size:
            return b""
        end = min(self.pos + n, self.size) - 1
        for attempt in range(5):
            try:
                r = self.s.get(self.url, headers={"Range": f"bytes={self.pos}-{end}"}, timeout=300)
                r.raise_for_status()
                break
            except requests.RequestException:
                if attempt == 4:
                    raise
        self.pos += len(r.content)
        return r.content

    def readinto(self, b):
        d = self.read(len(b))
        b[:len(d)] = d
        return len(d)


def scores(split):
    """One row per response x metric for a split, from the cache or the pinned revision."""
    rev = SPLIT_REV.get(split, REV)
    base = f"https://huggingface.co/datasets/{REPO}/resolve/{rev}"
    dest = f"{CACHE}/{rev}/scores/{split}.parquet"
    if not os.path.exists(dest):
        tree = requests.get(f"https://huggingface.co/api/datasets/{REPO}/tree/{rev}/response",
                            timeout=60).json()
        paths = sorted(f["path"] for f in tree
                       if re.fullmatch(rf"response/{split}-\d{{5}}-of-\d{{5}}\.parquet", f["path"]))
        assert paths, split
        cols = {k: [] for k in ("response_id", "model", "size", "gen", "metric", "judges", "value")}
        for p in paths:
            pf = pq.ParquetFile(RangeFile(f"{base}/{p}"))
            for rg in range(pf.num_row_groups):
                for r in pf.read_row_group(rg, columns=["response_id", "model", "scores"]).to_pylist():
                    m = r["model"]
                    for met, v in zip(r["scores"]["metric"], r["scores"]["value"]):
                        cols["response_id"].append(r["response_id"])
                        cols["model"].append(m["name"])
                        cols["size"].append(m["size"])
                        cols["gen"].append(m["model_adaptation"]["generation_parameters"])
                        cols["metric"].append(met["name"])
                        cols["judges"].append("|".join(met["models"] or []))
                        cols["value"].append(v)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        pq.write_table(pa.table(cols), dest + ".tmp")
        os.replace(dest + ".tmp", dest)
    return pd.read_parquet(dest)


def temperature(gen):
    if not gen:
        return None
    return json.loads(gen).get("temperature")


def build(table, split, metrics, judged):
    d = scores(split)
    wild = [m for m in metrics if m.startswith("*")]
    keep = d["metric"].isin(list(metrics)) | (d["metric"].str.endswith(wild[0][1:]) if wild else False)
    d = d[keep].copy()
    assert len(d), table

    ##response_id is <item_id>_<model, lowercased>_<run>.
    parts = [re.match(r"^(.*)_" + re.escape(m) + r"_(\d+)$", rid, re.I)
             for rid, m in zip(d["response_id"], d["model"])]
    assert all(parts), "unparsed response_id"
    d["item"] = [p.group(1) + metrics.get(met, "") for p, met in zip(parts, d["metric"])]
    d["run"] = [int(p.group(2)) for p in parts]

    n_filled = 0
    if judged:
        ##A blank judge list on a metric that names exactly one judge elsewhere is that judge
        ##(88 sorry_bench rows).
        for met, g in d.groupby("metric"):
            named = set(g["judges"]) - {""}
            blank = (d["metric"] == met) & (d["judges"] == "")
            if blank.any() and len(named) == 1:
                d.loc[blank, "judges"] = named.pop()
                n_filled += int(blank.sum())
        assert (d["judges"] != "").all() and not d["judges"].str.contains("|", regex=False).any(), \
            "expected exactly one judge per score"
        d["rater"] = d["judges"]
    else:
        assert (d["judges"] == "").all(), "unexpected judge on a programmatic metric"
        d["rater"] = ""

    ex = EXCLUDE.get(table, {})
    n_excl = int((d["model"].isin(ex.get("models", [])) | d["item"].isin(ex.get("items", []))).sum())
    d = d[~(d["model"].isin(ex.get("models", [])) | d["item"].isin(ex.get("items", [])))]

    key = ["model", "item", "rater", "run"]
    n0 = len(d)
    d = d.drop_duplicates(key + ["value", "gen"])
    n_dup = n0 - len(d)
    assert not d.duplicated(key).any(), "conflicting duplicate scores"

    lowest = d.groupby(["model", "item", "rater"])["run"].transform("min")
    n_run = int((d["run"] != lowest).sum())
    d = d[d["run"] == lowest]

    n_unparsed = 0
    if judged:
        n_unparsed = int((d["value"] == -1).sum())
        d = d[d["value"] != -1]
    assert d["value"].notna().all()

    out = pd.DataFrame({
        "id": d["model"].to_numpy(),
        "item": d["item"].to_numpy(),
        "resp": d["value"].to_numpy(),
        "cov_model_size": d["size"].replace("", None).to_numpy(),
        "cov_temperature": d["gen"].map(temperature).to_numpy(),
    })
    if judged:
        out["rater"] = d["rater"].to_numpy()
    ##Scores are integers on every metric kept except the HELM safety score (0, 0.5, 1).
    if (out["resp"] == out["resp"].round()).all():
        out["resp"] = out["resp"].astype(int)
    out = out.sort_values(["id", "item"] + (["rater"] if judged else [])).reset_index(drop=True)
    assert not out.duplicated(["id", "item"] + (["rater"] if judged else [])).any()

    ##run_qc does not apply irw-validate's `rater` rescue for dup_id_item; (id, item, rater) is
    ##asserted unique above, which is what that rescue checks.
    bad = [c for c in run_qc(out) if c.status == "fail"
           and not (judged and c.name == "dup_id_item")]
    assert not bad, (table, [(c.name, c.detail) for c in bad])

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{table}.csv")
    out.to_csv(path, index=False)
    vals = sorted(out["resp"].unique())
    print(f"{table}: {len(out)} rows, {out['id'].nunique()} models, {out['item'].nunique()} items, "
          f"resp {vals if len(vals) <= 8 else (vals[0], vals[-1])}"
          + (f", raters {sorted(out['rater'].unique())}" if judged else "")
          + f"; dropped {n_dup} exact duplicates, {n_run} later runs, {n_unparsed} unparsed judge scores"
          + (f"; filled {n_filled} blank judges" if n_filled else "")
          + (f"; excluded {n_excl} rows (EXCLUDE)" if n_excl else ""))


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(TABLES)
    for t in wanted:
        build(t, *TABLES[t])
