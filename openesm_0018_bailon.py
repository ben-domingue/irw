"""
Standard-library only ingestion script for openESM: 0018_bailon (CoVidAffect)
"""

import sys
import csv
import argparse
from datetime import datetime

def parse_iso_to_unix(date_str):
    if not date_str or date_str.strip() in ("", "NA", "NaN", "null"):
        return None
    clean_str = date_str.strip().replace("Z", "")
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S.%f",
    ):
        try:
            dt = datetime.strptime(clean_str, fmt)
            return dt
        except ValueError:
            continue
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Path to 0018_bailon_ts.tsv")
    parser.add_argument("--output", type=str, default="openesm_0018_bailon.csv", help="Output path")
    args = parser.parse_args()

    delim = "\t" if args.input.endswith(".tsv") else ","

    with open(args.input, "r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin, delimiter=delim)
        fieldnames = [c.strip() for c in reader.fieldnames]

        id_col = "id" if "id" in fieldnames else fieldnames[0]
        issued_col = "timestamp_issued" if "timestamp_issued" in fieldnames else None
        answer_col = "timestamp_answer" if "timestamp_answer" in fieldnames else None

        target_items = [c for c in ["valence", "arousal"] if c in fieldnames]

        user_obs_counts = {}
        out_rows = []

        for row in reader:
            uid = row.get(id_col, "").strip()
            if not uid:
                continue

            user_obs_counts[uid] = user_obs_counts.get(uid, 0) + 1
            wave_val = str(user_obs_counts[uid])

            dt_answer = parse_iso_to_unix(row.get(answer_col, "")) if answer_col else None
            dt_issued = parse_iso_to_unix(row.get(issued_col, "")) if issued_col else None

            date_str = str(int(dt_answer.timestamp())) if dt_answer else ""

            # Calculate rt
            if dt_answer and dt_issued:
                elapsed = (dt_answer - dt_issued).total_seconds()
                rt_str = str(round(elapsed, 2)) if 0 <= elapsed <= 3600 else ""
            else:
                rt_str = ""

            for item_name in target_items:
                raw_resp = row.get(item_name, "").strip()
                if raw_resp not in ("", "NA", "NaN", "null"):
                    try:
                        resp_num = float(raw_resp)
                        resp_str = str(int(resp_num)) if resp_num.is_integer() else str(resp_num)
                        out_rows.append({
                            "id": uid,
                            "item": item_name,
                            "resp": resp_str,
                            "wave": wave_val,
                            "date": date_str,
                            "rt": rt_str
                        })
                    except ValueError:
                        continue

    # Deterministic sorting
    out_rows.sort(
        key=lambda r: (
            int(r["id"]) if r["id"].isdigit() else r["id"],
            int(r["wave"]),
            r["item"]
        )
    )

    with open(args.output, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=["id", "item", "resp", "wave", "date", "rt"])
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Ingestion complete: {len(out_rows):,} rows written to {args.output}")

if __name__ == "__main__":
    main()