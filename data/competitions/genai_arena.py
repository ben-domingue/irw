"""GenAI-Arena human preference votes on image and video generation (2024-2025).

Source: https://huggingface.co/datasets/TIGER-Lab/GenAI-Arena-logs, CC BY 4.0 (the
card's `license:` field). GenAI-Arena is TIGER-Lab's arena for generative vision
models: a person writes a prompt, sees two anonymous models' outputs, and votes.

**Where the votes actually are.** The repository's bulk is media: the zips under
`archive/vote_log/images/`, `.../videos/` and `archive/vote_log/{generation,edition}/`
hold nothing but .jpg and .mp4 files, hundreds of MB each, and
`archive_info.json` beside them is a manifest of file hashes, not a vote log. The
votes are in two small zips at the top of each log directory, which hold one
`YYYY-MM-DD-conv.json` of JSON lines per day:

    archive/vote_log/archive_0-331.last.zip       66 MB, 224 day files
    archive/old_vote_log/archive_0-46.last.zip     5 MB,  46 day files

Only four of the eight record types are votes (leftvote, rightvote, tievote,
bothbad_vote); the rest are `chat` generation events, upvote/downvote/flag. The old
log is almost entirely a subset of the new one -- 2,854 votes of which 2,850 recur --
so both are read and deduplicated on (timestamp, model pair, vote type).

**Three tables, because there are three arenas.** The task is encoded in the model
name and nothing else: `*_edition` is image editing, `*_text2video` and
`videogenhub_*` are video generation, everything else (`*_text2image`,
`imagenhub_*_generation`, the bare "Playground v2" entries) is image generation.
Getting that wrong matters: reading `videogenhub_CogVideoX_generation` as an image
model manufactures 1,303 impossible image-vs-video battles. With the rule above,
zero votes cross a task boundary, which is the check this script asserts.

    genai_arena_t2i    8,094 votes, 28 models, 2024-02-12 to 2025-01-07
    genai_arena_edit   1,264 votes, 11 models, 2024-02-12 to 2024-12-17
    genai_arena_t2v    2,622 votes, 17 models, 2024-04-23 to 2025-01-06

Privacy: the source records carry an `ip` field, populated on about a quarter of
rows. It is dropped. Those addresses are private-range (10.x.x.x) load-balancer
addresses rather than user addresses, so they would not identify anyone, but they
are also useless as a rater key for exactly that reason -- many users share one.
This table therefore has no `rater` column. The prompts, also present on every
record, are dropped too.

Columns beyond the standard: outcome (leftvote, rightvote, tievote or bothbad_vote,
as recorded).

Choices:
- `agent_a` is the left model and `agent_b` the right, from `states[0]`/`states[1]`.
  The record's own top-level `models` field is `["", ""]` on every vote and is
  ignored; the model names live in the states.
- `winner` is "agent_a"/"agent_b"/"draw"; both tievote and bothbad_vote become
  "draw" and `outcome` keeps them apart. score_a/score_b are 1/0, 0/1, 0.5/0.5.
- `date` is `tstamp`, truncated to whole seconds.
- No `homefield` column in any of the three. Slot assignment is balanced and the
  left side wins 50.07% (t2i, z = +0.10), 48.33% (edit, z = -0.90) and 49.38%
  (t2v, z = -0.52) of decided votes -- none approaching the z = -3.90 measured on
  `lmarena_text_2025`.
- Dropped: 33 votes that drew the same model on both sides; records whose `states`
  is not exactly two entries or is missing a model name.

Counts, 2026-10-27 run: 12,013 deduplicated votes, of which 33 self-play are dropped
(all of them in t2i) and 0 cross a task boundary.

Usage: python3 genai_arena.py <dir holding the two vote-log zips> <output dir>
"""
import csv
import json
import sys
import zipfile
from pathlib import Path

ZIPS = ("old_vl.zip", "vl.zip")
COLUMNS = ["agent_a", "agent_b", "winner", "date", "score_a", "score_b", "outcome"]

VOTE = {"leftvote": ("agent_a", 1, 0), "rightvote": ("agent_b", 0, 1),
        "tievote": ("draw", 0.5, 0.5), "bothbad_vote": ("draw", 0.5, 0.5)}

TABLES = {"t2i": "genai_arena_t2i", "edit": "genai_arena_edit",
          "t2v": "genai_arena_t2v"}


def task(model):
    """Which arena a model competes in. The name is the only signal there is."""
    if model.endswith("_edition"):
        return "edit"
    if model.endswith("_text2video") or model.startswith("videogenhub_"):
        return "t2v"
    return "t2i"


def read_votes(raw):
    """Deduplicated votes from both log zips, newest file last."""
    votes = {}
    bad = {"states": 0, "name": 0}
    for name in ZIPS:
        z = zipfile.ZipFile(Path(raw) / name)
        for entry in sorted(n for n in z.namelist() if n.endswith(".json")):
            for line in z.read(entry).decode("utf-8", "replace").splitlines():
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("type") not in VOTE:
                    continue
                states = rec.get("states") or []
                if len(states) != 2:
                    bad["states"] += 1
                    continue
                a, b = states[0].get("model_name"), states[1].get("model_name")
                if not a or not b:
                    bad["name"] += 1
                    continue
                ##The same vote appears in both zips; the timestamp has
                ##sub-millisecond resolution, so it keys the record on its own.
                votes[(round(rec["tstamp"], 4), a, b, rec["type"])] = \
                    (a, b, rec["type"], rec["tstamp"])
    return votes, bad


def main(raw, out):
    votes, bad = read_votes(raw)
    writers, files, counts, models = {}, {}, {}, {}
    for key, table in TABLES.items():
        files[key] = open(Path(out) / f"{table}.csv", "w", newline="")
        writers[key] = csv.writer(files[key])
        writers[key].writerow(COLUMNS)
        counts[key] = 0
        models[key] = set()
    selfplay = cross = 0
    for a, b, kind, tstamp in votes.values():
        if a == b:
            selfplay += 1
            continue
        ta, tb = task(a), task(b)
        if ta != tb:
            cross += 1
            continue
        win, sa, sb = VOTE[kind]
        writers[ta].writerow([a, b, win, int(tstamp), sa, sb, kind])
        counts[ta] += 1
        models[ta].update((a, b))
    for f in files.values():
        f.close()
    for key, table in TABLES.items():
        print(f"{table}: {counts[key]} votes, {len(models[key])} models",
              file=sys.stderr)
    print(f"{len(votes)} deduplicated votes; dropped {selfplay} self-play, "
          f"{cross} cross-task, {bad} malformed", file=sys.stderr)
    ##A cross-task vote is impossible in this arena, so a non-zero count means
    ##task() has stopped matching the model naming -- fail rather than silently
    ##drop real votes.
    assert cross == 0, cross
    assert all(counts.values()) and selfplay < len(votes) / 100


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
