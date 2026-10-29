"""StarCraft AI Competitions run by David Churchill: AIIDE 2017-2025 and CoG 2026 (#2680).

Twelve complete round robins of StarCraft: Brood War bots in two tables:

    aiide_starcraft_2017_2025   173,155 games, 55 bot names, eleven competitions
    cog_starcraft_2026           14,425 games, 10 bot names, one competition

A dense near-complete round robin among a stable set of agents is rare in this family
-- most of what it holds is far sparser -- which is what made this worth asking for.
The two are separate tables because they are separate competitions with separate
standings, entered by overlapping but not identical fields of bots; CoG is a second
competition the same organiser took over in 2026 and will have a 2027 sibling.

Licence: Custom, by email. The site carries no terms of use anywhere (checked
2026-10-29), so IRW asked. David Churchill, who runs both competitions, replied
2026-10-23: "That seems fine, I would allow this to be done with the following rules:
- The source is attributed - Anyone else who rehosts the files must cite the original
source - It is not sold for profit - There is a note attached stating that it is not to
be used for the training of LLMs", and closed the thread 2026-10-29 ("Yeah you go ahead
and use it, no worries") after IRW replied that it can publish those rules conspicuously
but cannot enforce them on a downloader, and that it reads the fourth as barring
training on the data rather than analysis of it. Those four rules ARE the licence: they
go in `Custom License (source)` and in the processing notes so that they travel with the
table. He did not take up the ask to post them on the results pages, so this email is
the only record of the terms, which is why it is quoted in full here. No CC licence was
named and none of the four rules is expressible in one.

Source: https://davechurchill.ca/starcraft/results/ indexes every published round robin;
each links a directory holding `results/detailed_results.txt`, one space-padded row per
game, written WINNER FIRST. Cached in ~/.cache/irw-comps/aiide/ (fetched 2026-10-29).
Two layouts: 2017 and 2018 give `Game Round Winner Loser Crash TimeOut Map WScore
LScore EndFrame W55 W1000 W10000 L55 L1000 L10000 WAddress LAddress Start Finish`
(2017 without a header line), and 2019 on insert `Final Frame` and `Game End Type`
before the scores. Fields are split from both ends rather than by position, because a
map name can contain a space -- CoG 2026 plays "(4)Clay Fields1p2(n).scm", and
splitting on whitespace alone shifts every column after the map on 2,385 of its rows.
The addresses are the LAN machines that ran each bot, not a seat, and are dropped; so
are the six timeout-frame counts (W55 ... L10000), which record how often a bot
exceeded 55/1000/10000 ms on a frame -- the `timeout` column already names the bot that
lost a game that way.

**Which games count.** The site's own legend: "Only games in which at least one bot
ended the game 'normally' and counted a final game frame greater than zero ... are
counted in the results summary", and it marks two end types --
GAME_STATE_NOT_UPDATED_60S_BOTH_BOTS and NO_REPORT -- "No (Winner/Loser is arbitrary)".
Those two are dropped outright: these tables carry the outcome in the column ORDER, so
a row whose winner is arbitrary is indistinguishable from a real result once it is in.
There are 90 of them, all from 2019 on; 2017 and 2018 predate the end-type column, so a
game of this kind cannot be identified in those two and a few are presumably in the
table. Games that reached no frame and scored nothing go too (578), which is the site's
"final game frame greater than zero" -- but 2017 needs the disjunction (`end_frame > 0
or score_a > 0`), because 71 of its 253 zero-frame games were scored and the site counts
them; every one of 2017's 182 uncounted games has `WScore` -1. Of 193,348 source rows,
187,580 are kept.

**Two bots are purged from 2018, and this follows the source.** BlueBlueSky and ISAMind
each play 2,600 games in the 2018 detailed file and are absent from the 2018 standings
entirely. The site publishes no explanation, but the 2026 competition's notes.txt
documents the same mechanism: a bot disqualified under the "different enough from a
previous entry" rule had "all of its games purged from the official results and the
rankings recalculated as if it had not competed". Their 5,100 rows (2,600 each, 100 of
them against one another) are excluded, since keeping them would put this table at odds
with the organiser's own published results.

**Validated cell by cell against the organiser's published standings.** Each of the
twelve also publishes `results/results_summary_json.js`, which holds per-bot
Games/Wins/Losses/Crash/Timeout and a full per-pair Wins/Games matrix. The inclusion
rule above reproduces every one of those numbers EXACTLY for 2017, 2019, 2019um, 2020,
2021, 2022, 2025 and CoG 2026. For the other four it is over by 10 games in 9 pairs out
of 187,580 (2018 one pair, 2022x five, 2023 one, 2024 two). In every one of those pairs
the detailed file holds a contiguous rounds 0..N while the published summary counts N,
so the aggregate is a game stale rather than the file wrong, and the surplus is kept.
Nowhere is either table SHORT of a published count. The script asserts all of this,
including the per-year surplus figures, and fails if the agreement degrades.

Deliberately left out:

    AIIDE 2026       Still being run: the schedule says 20 October to 1 November 2026
    and 2026_live    with results presented at the conference on 9-13 November, the file
                     was last modified two days before this build, and no standings JSON
                     exists to check it against. A partial round robin is not the object
                     these tables hold. `2026_live` is a stale copy of the same run,
                     1,651 rows larger because the ShushanKing games disqualified in
                     notes.txt had not yet been purged from it. Worth adding after the
                     conference; CoG 2026 by contrast finished in August and is in.
    AIIDE 2015, 2016 detailed_results.txt exists for both, in the 2017 layout, but
                     neither publishes a standings JSON, so neither can be validated the
                     way all twelve of these were. They also sit outside the scope IRW
                     described when it asked. ~39,600 further games if wanted.
    AIIDE 2010-2014  No detailed_results.txt at all; 2012 has a RawData.txt in a
                     different shape and 2011/2014 only an HTML summary.

Columns beyond the standard: `competition`, `round`, `map`, `end_frame` (game length in
StarCraft frames, roughly 24 a second at the competition's speed), `game_end_type`
(empty for 2017 and 2018, which predate the column), `crashed` / `timeout` naming the
bot that crashed or lost on frame time, and `race_a` / `race_b`.

Choices:
- **`agent_a` is the winner in every row, so `winner` is the constant "agent_a".** The
  source records a game as a winner and a loser, with no seat and no draw, and that is
  the native form; it is how 36 of the family's tables are built (see the ordering
  section of comps_standard.qmd). Unlike most of those this one does carry
  `score_a`/`score_b`, so the page's Elo recipe keyed on `score(score_a, score_b)` runs
  on it. Code that symmetrises or shuffles the pair before fitting destroys the outcome.
- `score_a`/`score_b` are the in-game StarCraft scores of winner and loser. They do NOT
  decide the game except where it hit the frame limit (86,400 frames, about an hour of
  play, where the higher score wins), so `score_a < score_b` in 38,384 AIIDE rows and is
  not an error.
- **No `homefield`.** The competition has no side to hold an advantage: both bots get a
  start location on a shared map and the file records which LAN machine ran each, not
  which start position. A blank column would assert a null result that was never
  measured, so the column is absent, as in acpc_poker.
- `date` is the game's start time. 2019 onward stamp it ISO-8601 with a Z, taken at face
  value. 2017 and 2018 stamp `YYYYMMDD_HHMMSS` with no zone; those are read as UTC,
  which can be a few hours out in absolute terms but is a constant offset within a
  competition, so ordering -- the thing an Elo fit uses -- is exact.
- `race_a`/`race_b` come from each competition's standings JSON, so they are the race
  the bot REGISTERED and not necessarily the one it played: a bot registered "Random"
  picks a race per game and the detailed file does not record which. The same name can
  change race between years (Steamhammer is Zerg in 2017 and Random in 2025), so the
  join is on (competition, bot) and never on bot alone.
- Bot names are kept exactly as the source prints them and are NOT reconciled across
  competitions, so 55 names cover fewer real programs -- McRave and McRaveZ are one
  author's bot renamed. From 2026 the AIIDE competition assigns each bot a random
  in-game alias, which is a reason to expect names to stop being comparable.
- `2019um` is the AIIDE 2019 "Unknown Maps Competition", a second complete round robin
  of ten of that year's entrants on five maps the bots had not seen, run the week after
  the main event. It is its own competition with its own standings, kept beside 2019
  rather than merged into it.
- `2022x` is the competition the results index labels "Physical Hardware Re-run": the
  same eleven 2022 entrants played again three weeks later (last game 2022-11-11 against
  2022-10-23) on different hardware, published with its own standings. Both are kept,
  since `competition` lets a reader drop either, but a fit that pools all eleven AIIDE
  competitions counts those eleven bots twice for 2022 -- and comparing the two is the
  closest thing this family has to a hardware-held-out replication.

Usage: python3 aiide_starcraft.py [cache_dir] [out_dir]
"""

import collections
import csv
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

BASE = "https://davechurchill.ca/starcraft"

# (table, competition label, path under BASE). One row per round robin published.
COMPETITIONS = [
    ("aiide_starcraft_2017_2025", "2017",   "aiide/results/2017"),
    ("aiide_starcraft_2017_2025", "2018",   "aiide/results/2018"),
    ("aiide_starcraft_2017_2025", "2019",   "aiide/results/2019"),
    ("aiide_starcraft_2017_2025", "2019um", "aiide/results/2019/unknown_maps"),
    ("aiide_starcraft_2017_2025", "2020",   "aiide/results/2020"),
    ("aiide_starcraft_2017_2025", "2021",   "aiide/results/2021"),
    ("aiide_starcraft_2017_2025", "2022",   "aiide/results/2022"),
    ("aiide_starcraft_2017_2025", "2022x",  "aiide/results/2022x"),
    ("aiide_starcraft_2017_2025", "2023",   "aiide/results/2023"),
    ("aiide_starcraft_2017_2025", "2024",   "aiide/results/2024"),
    ("aiide_starcraft_2017_2025", "2025",   "aiide/results/2025"),
    ("cog_starcraft_2026",        "2026",   "cog/results/2026"),
]

# "No (Winner/Loser is arbitrary)" in the site's own legend.
ARBITRARY = {"GAME_STATE_NOT_UPDATED_60S_BOTH_BOTS", "NO_REPORT"}

# Absent from the 2018 standings although present in its detailed file; see above.
PURGED = {"2018": {"BlueBlueSky", "ISAMind"}}

# Years whose per-pair counts the inclusion rule reproduces with a surplus, and the
# number of surplus games. Asserted exactly: a change here is a change in the source.
KNOWN_SURPLUS = {"2018": 1, "2022x": 6, "2023": 1, "2024": 2}

# Games and distinct bot names per table, asserted so a silent change in the source
# cannot pass unnoticed.
EXPECTED = {"aiide_starcraft_2017_2025": (173155, 55), "cog_starcraft_2026": (14425, 10)}

COLUMNS = ["agent_a", "agent_b", "winner", "score_a", "score_b", "date",
           "competition", "round", "map", "end_frame", "game_end_type",
           "crashed", "timeout", "race_a", "race_b"]


def fetch(cache, path, label, which):
    local = os.path.join(cache, f"{which}_{label}")
    if not os.path.exists(local):
        suffix = "detailed_results.txt" if which == "dr" else "results_summary_json.js"
        with urllib.request.urlopen(f"{BASE}/{path}/results/{suffix}", timeout=180) as r:
            body = r.read()
        with open(local, "wb") as f:
            f.write(body)
        time.sleep(2)
    with open(local, encoding="utf-8") as f:
        return f.read()


def unix(stamp):
    if stamp.endswith("Z"):
        d = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
    else:
        d = datetime.strptime(stamp, "%Y%m%d_%H%M%S")  # no zone at source, read as UTC
    return int(d.replace(tzinfo=timezone.utc).timestamp())


def parse_games(text, label):
    """One dict per row of detailed_results.txt.

    Fields are split from both ends rather than by position, because a map name can
    contain a space: CoG 2026 plays "(4)Clay Fields1p2(n).scm", which whitespace
    splitting alone would read as two columns and shift every field after it.
    """
    games = []
    for line in text.splitlines():
        f = line.split()
        if not f or not f[0].isdigit():
            continue  # the header line, where present
        head, tail = f[:6], f[6:]
        # The end-type token is the only non-numeric field in either tail.
        if len(tail) >= 14 and not tail[-13].lstrip("-").isdigit():
            mid, t = tail[:-14], tail[-14:]   # 2019 on: Final Frame, Game End Type
            g = dict(frame=int(t[0]), end_type=t[1], score_w=int(t[2]),
                     score_l=int(t[3]), start=t[12])
        elif len(tail) >= 13:                             # 2017, 2018: no end type
            mid, t = tail[:-13], tail[-13:]
            g = dict(score_w=int(t[0]), score_l=int(t[1]), frame=int(t[2]),
                     end_type="", start=t[11])
        else:
            raise AssertionError(f"{label}: {len(f)} fields, too few")
        g.update(round=int(head[1]), winner=head[2], loser=head[3], crash=head[4],
                 timeout=head[5], map=" ".join(mid))
        assert g["winner"] != g["loser"], (label, line)
        assert "/" not in g["map"] and g["map"].endswith((".scx", ".scm")), (label, line)
        games.append(g)
    assert games, label
    return games


def parse_standings(text):
    """The published standings: {bot: {...}} plus a per-pair (wins, games) map."""
    head = "resultsSummary = "
    bots = json.loads(text[text.index(head) + len(head):].rstrip().rstrip(";"))
    pairs = {}
    for b in bots:
        for p in b["resultPairs"]:
            pairs[(b["BotName"], p["Opponent"])] = (p["Wins"], p["Games"])
    return {b["BotName"]: b for b in bots}, pairs


def counted(g, purged):
    """The site's own rule for a game that counts towards the results."""
    if g["end_type"] in ARBITRARY:
        return False
    if g["winner"] in purged or g["loser"] in purged:
        return False
    return g["frame"] > 0 or g["score_w"] > 0


def check(year, kept, bots, pairs):
    """Reproduce the published standings from `kept`; return the surplus game count."""
    wins = collections.Counter()
    losses = collections.Counter()
    crash = collections.Counter()
    tout = collections.Counter()
    pw = collections.Counter()
    pg = collections.Counter()
    for g in kept:
        wins[g["winner"]] += 1
        losses[g["loser"]] += 1
        if g["crash"] != "-":
            crash[g["crash"]] += 1
        if g["timeout"] != "-":
            tout[g["timeout"]] += 1
        pw[(g["winner"], g["loser"])] += 1
        pg[(g["winner"], g["loser"])] += 1
        pg[(g["loser"], g["winner"])] += 1

    assert set(bots) == {b for g in kept for b in (g["winner"], g["loser"])}, year
    surplus = 0
    for (a, b_), (w, n) in pairs.items():
        # Never short of a published count.
        assert pw[(a, b_)] >= w and pg[(a, b_)] >= n, (year, a, b_)
        # A pair the file is over on must be contiguous rounds 0..N: a stale aggregate,
        # not a game the file invented.
        if pg[(a, b_)] > n and a < b_:
            rounds = sorted(g["round"] for g in kept
                            if {g["winner"], g["loser"]} == {a, b_})
            assert rounds == list(range(len(rounds))), (year, a, b_, rounds[:5])
            surplus += pg[(a, b_)] - n
    for name, b in bots.items():
        assert wins[name] >= b["Wins"] and losses[name] >= b["Losses"], (year, name)
        assert crash[name] >= b["Crash"] and tout[name] >= b["Timeout"], (year, name)
        if surplus == 0:
            # Where nothing is surplus the agreement is exact, down to the per-bot
            # crash and frame-timeout counts.
            assert (wins[name], losses[name], crash[name], tout[name]) == \
                   (b["Wins"], b["Losses"], b["Crash"], b["Timeout"]), (year, name)
    if surplus == 0:
        assert all(pw[k] == v[0] and pg[k] == v[1] for k, v in pairs.items()), year
    return surplus


def main(cache, out):
    os.makedirs(cache, exist_ok=True)
    tables = collections.defaultdict(list)
    report = []
    for table, label, path in COMPETITIONS:
        games = parse_games(fetch(cache, path, label, "dr"), label)
        bots, pairs = parse_standings(fetch(cache, path, label, "sum"))
        purged = PURGED.get(label, set())
        kept = [g for g in games if counted(g, purged)]

        surplus = check(label, kept, bots, pairs)
        assert surplus == KNOWN_SURPLUS.get(label, 0), (label, surplus)

        race = {b["BotName"]: b["Race"] for b in bots.values()}
        for g in sorted(kept, key=lambda g: (unix(g["start"]), g["round"])):
            tables[table].append([
                g["winner"], g["loser"], "agent_a", g["score_w"], g["score_l"],
                unix(g["start"]), label, g["round"], g["map"], g["frame"],
                g["end_type"],
                "agent_a" if g["crash"] == g["winner"] else
                "agent_b" if g["crash"] == g["loser"] else "",
                "agent_a" if g["timeout"] == g["winner"] else
                "agent_b" if g["timeout"] == g["loser"] else "",
                race[g["winner"]], race[g["loser"]],
            ])
        report.append(f"  {table:<26} {label:<6} {len(games):6d} rows -> "
                      f"{len(kept):6d} games, {len(bots):2d} bots, surplus {surplus}")

    for table, rows in tables.items():
        # crashed/timeout name one of the row's own two agents or nothing, and a pair
        # plays at most once per round of a competition.
        for r in rows:
            assert r[11] in ("", "agent_a", "agent_b"), r
            assert r[12] in ("", "agent_a", "agent_b"), r
        assert len({(r[6], r[7], frozenset((r[0], r[1]))) for r in rows}) == len(rows), table
        agents = {r[0] for r in rows} | {r[1] for r in rows}
        assert (len(rows), len(agents)) == EXPECTED[table], (table, len(rows), len(agents))
        with open(os.path.join(out, table + ".csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(COLUMNS)
            w.writerows(rows)
        report.append(f"  wrote {table}.csv: {len(rows)} games, {len(agents)} bots")
    print("\n".join(report), file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.cache/irw-comps/aiide"),
         sys.argv[2] if len(sys.argv) > 2 else ".")
