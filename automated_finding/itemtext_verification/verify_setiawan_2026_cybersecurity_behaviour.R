# Step 5b verification for setiawan_2026_cybersecurity_behaviour.
#
# The claim: each item code in the __items.csv carries the wording the
# deposit's own instrument file attaches to THAT data column -- not the
# wording of a neighbouring column.
#
# The route is an exact NAME join, re-derived here from the raw deposit file
# rather than from the builder (make_itemtext_setiawan_2026.py), so a bug in
# the builder cannot pass this. CSLE_instrument_ID-EN.csv has one row per
# item; its `variable` cell IS the column name in CSLE_teacher_dataset_233.csv
# and therefore the `item` value in the response table. The check is that the
# join is bijective over this subscale and that every shipped item_text and
# item_text_translated equals the instrument file's Indonesian and English
# wording for its own code.
#
# Usage: Rscript verify_setiawan_2026_cybersecurity_behaviour.R <CSLE_instrument_ID-EN.csv> [items csv]
# Falls back to the live IRW copy of the items table when no path is given.

suppressMessages({library(irw)})

TABLE <- "setiawan_2026_cybersecurity_behaviour"
PREFIX <- "BH"
SUBSCALE_N <- 20L

args <- commandArgs(trailingOnly = TRUE)
instr <- utils::read.csv(args[1], stringsAsFactors = FALSE, encoding = "UTF-8")
instr$variable <- trimws(instr$variable)

items <- if (length(args) >= 2) utils::read.csv(args[2], stringsAsFactors = FALSE) else
  irw::irw_fetch_itemtext(TABLE)
items <- items[!duplicated(items$item), c("item", "item_text", "item_text_translated")]

norm <- function(x) tolower(gsub("[[:space:]]+", " ", trimws(x)))

blk <- instr[startsWith(instr$variable, PREFIX), ]
cat(sprintf("instrument rows for %s: %d ; shipped items: %d\n",
            PREFIX, nrow(blk), nrow(items)))
cat(sprintf("%-6s %-56s %s\n", "item", "instrument stem (administered Indonesian)", "match"))
ok <- nrow(blk) == SUBSCALE_N
for (i in seq_len(nrow(items))) {
  code <- items$item[i]
  row <- blk[blk$variable == code, , drop = FALSE]
  if (nrow(row) != 1L) {
    cat(sprintf("%-6s %-56s %s\n", code, "<no unique instrument row>", "FAIL")); ok <- FALSE; next
  }
  hit_id <- norm(row$item_indonesian[1]) == norm(items$item_text[i])
  hit_en <- norm(row$item_english[1]) == norm(items$item_text_translated[i])
  ok <- ok && hit_id && hit_en
  cat(sprintf("%-6s %-56s %s\n", code, substr(row$item_indonesian[1], 1, 56),
              if (hit_id && hit_en) "ok" else
                paste0("FAIL <- id:", hit_id, " en:", hit_en)))
}

bij <- identical(sort(blk$variable), sort(items$item))
cat(sprintf("\ninstrument codes in this subscale: %d ; shipped items: %d ; bijective: %s\n",
            nrow(blk), nrow(items), bij))
ok <- ok && bij

cat("Note: this pins every item individually -- the tie is an exact name match\n",
    "supplied by the depositors, not an ordering or a statistical signal. What it\n",
    "does NOT establish is that the depositors' own instrument file is right about\n",
    "their own survey; no independent per-item published statistic exists, the\n",
    "data article being under review at the time of deposit.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
