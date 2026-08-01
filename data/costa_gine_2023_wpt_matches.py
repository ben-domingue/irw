import csv
from datetime import datetime, timezone

SRC = "../automated_finding/downloads/padel/historico_partidos_wpt.csv"
OUT = "../automated_finding/output_noncore/costa_gine_2023_wpt_matches.csv"

SET_COLS = [("set1_pareja1", "set1_pareja2"), ("set2_pareja1", "set2_pareja2"), ("set3_pareja1", "set3_pareja2")]


def pair_name(p1, p2):
    return f"{p1.strip()} / {p2.strip()}"


def to_unix(datestr):
    # format: DD.MM.YYYY
    try:
        dt = datetime.strptime(datestr, "%d.%m.%Y").replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except ValueError:
        return ""


def sets_won(row):
    a_sets = b_sets = 0
    for a_col, b_col in SET_COLS:
        a, b = row[a_col].strip(), row[b_col].strip()
        if a == "" or b == "":
            continue
        a, b = int(a), int(b)
        if a == 0 and b == 0:
            continue
        if a > b:
            a_sets += 1
        elif b > a:
            b_sets += 1
    return a_sets, b_sets


with open(SRC, encoding="utf-16") as f:
    rows = list(csv.DictReader(f))

out = []
skipped_no_winner = 0
for row in rows:
    agent_a = pair_name(row["pareja1_jugador1"], row["pareja1_jugador2"])
    agent_b = pair_name(row["pareja2_jugador1"], row["pareja2_jugador2"])
    winner_raw = row["pareja_ganadora"].strip()
    if not winner_raw:
        skipped_no_winner += 1
        continue
    winner_pair = winner_raw.replace("_", " / ")
    if winner_pair == agent_a:
        winner = "a"
    elif winner_pair == agent_b:
        winner = "b"
    else:
        skipped_no_winner += 1
        continue
    score_a, score_b = sets_won(row)
    out.append({
        "agent_a": agent_a,
        "agent_b": agent_b,
        "date": to_unix(row["fecha_inicio_torneo"]),
        "homefield": "",
        "score_a": score_a,
        "score_b": score_b,
        "winner": winner,
        "cov_tournament": row["nombre_torneo"],
        "cov_year": row["anio_torneo"],
        "cov_category": row["categoria"],
        "cov_round": row["fase"],
    })

fields = ["agent_a", "agent_b", "date", "homefield", "score_a", "score_b", "winner",
          "cov_tournament", "cov_year", "cov_category", "cov_round"]

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(out)

print(f"matches: {len(out)} (skipped {skipped_no_winner} with no resolvable winner) out of {len(rows)} raw rows")
