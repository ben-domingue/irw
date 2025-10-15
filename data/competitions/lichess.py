#from: https://github.com/ayaan-gupta/IRW-data-scripts/blob/main/harvest/lichess.py

# harvest/lichess_local.py
import argparse, csv, os, sys
from datetime import timezone, datetime
import chess.pgn

# ---- schema helpers ----
COLUMNS = [
    "match_id", # deterministic hash id
    "date",         # event date (from event_dt)
    "homefield",    # not available, set to empty or NA
    "agent_a",
    "agent_b",
    "score_a",
    "score_b",
    "duration",     # not available, set to empty
    "winner",
    "source",       # lichess
    "source_ref",   # lichess URL
    "domain",         # chess
]

def make_match_id(domain, source_ref, event_dt, a, b):
    # short, stable, deterministic (good enough for v0)
    import hashlib
    key = f"{domain}|{source_ref}|{event_dt}|{a}|{b}"
    return hashlib.sha1(key.encode()).hexdigest()[:16]

def parse_event_epoch(tags):
    """Return UNIX epoch seconds from PGN headers (UTCDate/UTCTime or Date)."""
    date = (tags.get("UTCDate") or tags.get("Date") or "").strip()
    time_ = (tags.get("UTCTime") or "").strip()
    if not date or date == "????.??.??":
        return None
    # PGN uses YYYY.MM.DD
    parts = date.split(".")
    try:
        year = int(parts[0]); month = int(parts[1]); day = int(parts[2])
    except Exception:
        return None
    if not time_ or time_ in {"??:??:??", "?", "*"}:
        hh, mm, ss = 0, 0, 0
    else:
        try:
            hh, mm, ss = map(int, time_.split(":"))
        except Exception:
            hh, mm, ss = 0, 0, 0
    try:
        dt = datetime(year, month, day, hh, mm, ss, tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return None

def result_to_fields(res):
    # Map PGN Result -> (winner_label, score_a, score_b)
    res = (res or "").strip()
    if res == "1-0":
        return "agent_a", 1.0, 0.0
    if res == "0-1":
        return "agent_b", 0.0, 1.0
    if res in {"1/2-1/2", "1/2-1/2 "}:
        return "draw", 0.5, 0.5
    return None  # unfinished/abandoned/etc.

def normalize_game(game):
    tags = game.headers
    event_dt = parse_event_epoch(tags)
    if event_dt is None:
        return None

    white = (tags.get("White") or "").strip()
    black = (tags.get("Black") or "").strip()
    if not white or not black or white == black:
        return None

    mapped = result_to_fields(tags.get("Result"))
    if mapped is None:
        return None
    winner, sa, sb = mapped

    source_ref = (tags.get("Site") or "").strip()  # usually a lichess URL
    if not source_ref:
        # last-ditch fallback: compose a reference
        source_ref = f"{tags.get('Event','lichess')}|{event_dt}|{white}|{black}"

    # Map to new data standard
    row = {
        "date": event_dt,
        "homefield": "N/A",  # chess has no homefield
        "agent_a": white,
        "agent_b": black,
        "score_a": sa,
        "score_b": sb,
        "duration": "",  # not available from PGN
        "winner": winner,
        "source": "lichess",
        "source_ref": source_ref,
        "domain": "chess",
        "match_id": make_match_id("chess", source_ref, event_dt, white, black),
    }
    return row

def stream_pgn_to_csv(pgn_path, out_csv, max_games=None, chunk_size=5000):
    processed = 0
    written = 0
    skipped = 0

    # ensure out dir
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)

    # open writer
    f_out = open(out_csv, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(f_out, fieldnames=COLUMNS)
    writer.writeheader()

    rows = []
    with open(pgn_path, "r", encoding="utf-8", errors="ignore") as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            processed += 1

            row = normalize_game(game)
            if row is None:
                skipped += 1
            else:
                rows.append(row)

            # flush periodically
            if len(rows) >= chunk_size:
                writer.writerows(rows)
                written += len(rows)
                rows.clear()

            if max_games and processed >= max_games:
                break

    # flush tail
    if rows:
        writer.writerows(rows)
        written += len(rows)
    f_out.close()

    print(f"[lichess] processed={processed} written={written} skipped={skipped} → {out_csv}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pgn_path", help="Path to local .pgn file (unzipped)")
    ap.add_argument("--out", default="data/samples/chess.csv", help="Output CSV path")
    ap.add_argument("--max-games", type=int, default=None, help="Optional cap for quick tests")
    ap.add_argument("--chunk-size", type=int, default=5000)
    args = ap.parse_args()
    stream_pgn_to_csv(args.pgn_path, args.out, args.max_games, args.chunk_size)

if __name__ == "__main__":
    main()
