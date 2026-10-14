"""ICLR 2024 peer-review scores (OpenReview), one row per review x criterion. irw#2985.

Source: SNOR v1 (Neumann, M., 2025, "Structured and Normalized OpenReview Reviews and Comments",
Zenodo 10.5281/zenodo.15866613, CC BY 4.0), a structured mirror of OpenReview. The review content
itself is released by its authors under CC BY 4.0 through OpenReview's Terms of Use
(https://openreview.net/legal/terms, "Comment ... License"; "ratings" are named as Comments, and the
licence applies retroactively). Files read: normalized_comments.jsonl (rows with conference_id
"iclr2024" and is_review true) and normalized_papers.jsonl (decision per paper).

Shape (rater data): id = submission (OpenReview forum id), rater = the reviewer's anonymous id
within that submission (the Reviewer_xxxx suffix of the signature; OpenReview assigns a fresh id per
submission, so raters do NOT link across submissions), item = criterion, resp = the numeric score:
rating 1-10 (the integer that starts the label, e.g. "6: marginally above the acceptance threshold"),
confidence 1-5 (reviewer's self-rated confidence; kept as an item, see the codebook), soundness,
presentation, contribution 1-4 ("1 poor" .. "4 excellent"). cov_decision = SNOR's normalized decision
for the paper (Oral / Spotlight / Poster / Reject / Withdrawn ...), "" when the paper is not in the
papers file. Review text is not stored. Exact duplicate (id, rater, item) rows are collapsed to one.

    python3 data/iclr_2024_peer_review.py --comments normalized_comments.jsonl \
        --papers normalized_papers.jsonl -o <out>
"""
import argparse
import csv
import json
import pathlib
import re

CONF = "iclr2024"
ITEMS = ("rating", "confidence", "soundness", "presentation", "contribution")
LEAD_INT = re.compile(r"^\s*(\d+)")


def score(v):
    m = LEAD_INT.match(str(v))
    return m.group(1) if m else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--comments", required=True)
    p.add_argument("--papers", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    decision = {}
    with open(a.papers, encoding="utf-8") as fh:
        for line in fh:
            if f'"conf_id":"{CONF}"' not in line and f'"conf_id": "{CONF}"' not in line:
                continue
            o = json.loads(line)
            if o.get("conf_id") == CONF:
                decision[o["id"]] = o.get("normalized_decision") or ""

    seen = set()
    n = dup = bad = 0
    ids, raters = set(), set()
    with open(a.comments, encoding="utf-8") as fh, \
            open(out / "iclr_2024_peer_review.csv", "w", newline="", encoding="utf-8") as oh:
        w = csv.writer(oh)
        w.writerow(["id", "item", "resp", "rater", "cov_decision"])
        for line in fh:
            if f'"conference_id":"{CONF}"' not in line and f'"conference_id": "{CONF}"' not in line:
                continue
            o = json.loads(line)
            if o.get("conference_id") != CONF or not o.get("is_review"):
                continue
            sig = o["signature"].rsplit("/", 1)[-1]
            if not sig.startswith("Reviewer_"):
                bad += 1
                continue
            c = o["content"]
            if isinstance(c, str):
                c = json.loads(c)
            pid = o["paper_id"]
            for item in ITEMS:
                s = score(c.get(item))
                if s is None:
                    continue
                key = (pid, sig, item)
                if key in seen:
                    dup += 1
                    continue
                seen.add(key)
                w.writerow([pid, item, s, sig, decision.get(pid, "")])
                n += 1
                ids.add(pid)
                raters.add((pid, sig))
    print(f"iclr_2024_peer_review: {n} rows, {len(ids)} submissions, {len(raters)} reviews, "
          f"{dup} duplicate rows dropped, {bad} non-reviewer signatures skipped, "
          f"{sum(1 for i in ids if i in decision)} submissions with a decision")


if __name__ == "__main__":
    main()
