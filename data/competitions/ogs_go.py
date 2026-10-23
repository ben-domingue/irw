"""Online-Go.com (OGS) ranked and unranked Go games, 2005 to October 2021 (#2710).

Source: https://archive.org/details/ogs2021, "OGS 2021 collection of Go games",
uploaded 2021-10-22 by Zachary Vance (za3k@za3k.com). File read:
ogs_games_2013_to_2021-08.json.gz (19.6 GB gzipped), one JSON object per line, each
the OGS API record for one game. The item also holds the same games as SGF files and
a 100k-game sample; neither is used. The file name understates its span: the games
actually run 2005-11-05 to 2021-10-12, with 357,057 of them before 2013 (171,922
before 2010), so the table is named for the range the data has, not the one the file
claims.

Licence: two rights-holders, and this table rests on both. The item's readme.txt says it
plainly: "I (Zachary Vance) release anything I have rights to into the public domain" and
"anoek (as an OGS representative) has said it's fine to use this for research", with the
crawl itself run "with permission of OGS". anoek is Akita Noek, the OGS developer IRW
wrote to on 2026-10-22 asking for that permission to be written down as terms on the site
(oneoff/email-drafts-2026-10-22/ogs_noek_draft.txt); no reply as of 2026-10-23. So the
basis is the PD release plus a representative's research-use statement, not a licence,
and the dictionary row records it as Custom on both sides. The dumper adds that he never
asked the individual players and that "it's unclear what the legal status of a collection
of public games would even be".

Privacy: the dump already omits games the players marked private (readme.txt), which is
why no row is dropped for that below, and this script drops usernames, ranks, move
records, chat and reviews on top of that.

What is published, and why so little. The letter to OGS promised "a player identifier,
an opponent identifier, and a result", no usernames, no profile text and no move
records, plus an offer to re-code the identifiers so they cannot be joined back to OGS
accounts. This script honours the stronger version of that promise without waiting to be
asked: the OGS numeric player ids are re-keyed to 1..n in order of first appearance, and
the mapping is not kept. The usernames, ranks, move lists, chat, reviews, clocks and
everything else in the source records are dropped. The only fields kept beyond the two
agents and the result are the ones a result cannot be read without: the date, the board
size, the handicap, the komi, the rule set and whether the game was ranked.

Columns beyond the standard (comps_standard.qmd): board_size (the square board's side;
non-square boards are dropped, see below), handicap (stones given to black, 0 for an even
game), komi (points given to white in compensation), rules (japanese, chinese, korean,
aga, nz, ing), ranked (1/0), outcome (as recorded: Resignation, Timeout, "6.5 points",
Disconnection, Moderator Decision, ...) and margin_points (the winner's margin when the
game was counted, else blank).

Choices:
- agent_a is black, agent_b is white, in every row. homefield is "agent_a" throughout,
  because black moves first; that advantage is what komi and handicap compensate for, so
  read homefield together with those two columns rather than on its own.
- winner is "agent_a"/"agent_b", resolved from the source `winner` player id. The source
  has no draw outcome: a counted tie would appear as a 0-point margin and none occurs, so
  `winner` is never "draw".
- date is the game's start_time (Unix seconds), falling back to end_time.
- Dropped: games not in phase "finished"; games whose outcome is a cancellation (not a
  decided game); games with no winner, or whose winner is neither player; games missing a
  player id or with the same id on both sides; games flagged private; non-square boards
  and boards other than 5, 7, 9, 13, 15, 17, 19 (a handful of oddities among millions);
  duplicate game_id (the dump holds each game once, but this is checked rather than
  assumed); and games with no usable timestamp.
- Outcome strings are kept as recorded rather than tidied, because the dump mixes OGS's
  own wording with text from imported games ("r", "resign", "time", "?"). margin_points
  normalises the countable ones.

Counts, 2026-10-23 run: 25,492,142 games between 690,746 players, 1.9 GB of CSV. The
gzip holds 27,086,430 lines with no repeated game_id; readme.txt says 27,086,420 games,
ten fewer, and the difference is not reconciled. The readme also says the games stop
2021-08-29 while the latest start_time here is 2021-10-12, which the crawl window
(2021-08-29 to 2021-10-15) explains.
Dropped 1,373,831 cancellations, 157,798 games not in phase "finished", 59,145 games on
a non-square or unusual board, 3,267 whose recorded winner is neither player and 247 with
a missing or shared player id; no duplicate game_id, no unparsable line and no game
flagged private. 28% of the kept games were counted out and carry a margin; the rest
ended by resignation, timeout or another event. White (agent_b) wins 59% of games, which
is what handicap play does to the colour balance -- read `winner` with `handicap`.
Board sizes: 19x19 11,862,667, 9x9 10,299,207, 13x13 3,263,148, and 5x5/7x7/15x15/17x17
together 67,120. 19,331,247 games are ranked.

Usage: python3 ogs_go.py <dir holding ogs_games_2013_to_2021-08.json.gz> <output dir>
Streams the gzip: it never holds more than one game in memory, and writes one CSV.
"""
import csv
import gzip
import json
import re
import sys
from pathlib import Path

SIZES = {5, 7, 9, 13, 15, 17, 19}
CANCELLED = {"cancellation", "cancelled", "canceled"}
MARGIN_RE = re.compile(r"^([0-9]+(?:\.[0-9]+)?)(?:\s+points?)?$")
COLUMNS = ["agent_a", "agent_b", "winner", "date", "homefield", "board_size",
           "handicap", "komi", "rules", "ranked", "outcome", "margin_points"]


def margin(outcome):
    m = MARGIN_RE.match(outcome.strip())
    return float(m.group(1)) if m else None


def main(raw, out):
    src = Path(raw) / "ogs_games_2013_to_2021-08.json.gz"
    ids, seen = {}, set()
    drops = {k: 0 for k in ("phase", "cancelled", "winner", "players", "private",
                            "board", "date", "duplicate", "unparsed")}
    kept = 0
    with gzip.open(src, "rt", encoding="utf-8", errors="strict") as f, \
            open(Path(out) / "ogs_go_2005_2021.csv", "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(COLUMNS)
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                drops["unparsed"] += 1
                continue
            gid = d.get("game_id")
            if gid in seen:
                drops["duplicate"] += 1
                continue
            seen.add(gid)
            if d.get("phase") != "finished":
                drops["phase"] += 1
                continue
            if d.get("private") is True:
                drops["private"] += 1
                continue
            outcome = str(d.get("outcome") or "")
            if outcome.strip().lower() in CANCELLED:
                drops["cancelled"] += 1
                continue
            b, wh = d.get("black_player_id"), d.get("white_player_id")
            if b is None or wh is None or b == wh:
                drops["players"] += 1
                continue
            win = d.get("winner")
            if win not in (b, wh):
                drops["winner"] += 1
                continue
            size = d.get("width")
            if size not in SIZES or d.get("height") != size:
                drops["board"] += 1
                continue
            date = d.get("start_time") or d.get("end_time")
            if not isinstance(date, (int, float)):
                drops["date"] += 1
                continue
            for p in (b, wh):
                if p not in ids:
                    ids[p] = len(ids) + 1
            mg = margin(outcome)
            w.writerow([ids[b], ids[wh], "agent_a" if win == b else "agent_b",
                        int(date), "agent_a", size,
                        int(d.get("handicap") or 0), d.get("komi"),
                        str(d.get("rules") or "").lower(),
                        1 if d.get("ranked") in (True, 1, "1", "True") else 0,
                        outcome, "" if mg is None else mg])
            kept += 1
    print(f"kept {kept} games, {len(ids)} players", file=sys.stderr)
    print("dropped " + ", ".join(f"{k}={v}" for k, v in drops.items()), file=sys.stderr)
    assert kept > 0 and not any(v > kept for v in drops.values()), (kept, drops)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
