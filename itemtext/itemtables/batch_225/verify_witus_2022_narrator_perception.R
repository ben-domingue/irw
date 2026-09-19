# verify_witus_2022_narrator_perception.R
#
# CLAIM UNDER TEST (Step 5b, route 9 -- response-frequency matching):
#   The IRW item codes narrator_trustworthy / narrator_comforting /
#   narrator_knowledgeable correspond to columns Q28_1 / Q28_2 / Q28_3 of the
#   PLOS ONE S1 Dataset, and the S1 Appendix numbers the Q28 matrix statements
#   (1) "The narrator was trustworthy", (2) "...comforting",
#   (3) "...knowledgeable". If any two of the three item_texts were swapped,
#   the per-item x per-resp count matrix below would stop matching the raw
#   spreadsheet cell for cell.
#
# The three raw columns have MUTUALLY DISTINCT 1-4 distributions, so this route
# distinguishes every item from every other item -- not just a polarity class
# or a subset of positions. It also confirms the resp coding direction
# (1 = "Not at all" ... 4 = "Very"), since the counts are of the raw 1-4 codes
# the appendix prints beside those anchors.
#
# Uses a server-side GROUP BY (no whole-table export).

suppressMessages(library(redivis))

TABLE_REF <- "datapages.item_response_warehouse_4.witus_2022_narrator_perception"

# Counts of each raw code in the S1 Dataset XLSX
# (10.1371/journal.pone.0267580.s002, sheet "Witus Larson PNAS Data File"),
# hard-coded so this script does not need to refetch the supplement.
RAW <- list(
  Q28_1 = c(`1` =  12, `2` = 56, `3` = 277, `4` = 463),  # -> narrator_trustworthy
  Q28_2 = c(`1` =  16, `2` = 73, `3` = 224, `4` = 496),  # -> narrator_comforting
  Q28_3 = c(`1` =   5, `2` = 36, `3` = 179, `4` = 588)   # -> narrator_knowledgeable
)
MAP <- c(Q28_1 = "narrator_trustworthy",
         Q28_2 = "narrator_comforting",
         Q28_3 = "narrator_knowledgeable")

q <- redivis$query(sprintf("
SELECT item, CAST(resp AS INT64) AS resp, COUNT(*) AS n
FROM `%s`
WHERE resp IS NOT NULL
GROUP BY item, resp", TABLE_REF))
live <- as.data.frame(q$to_data_frame())

cat(sprintf("%-8s %-24s %6s %8s %8s %6s\n",
            "raw col", "item", "resp", "raw n", "live n", "diff"))
ok <- TRUE
for (col in names(RAW)) {
  it <- MAP[[col]]
  for (lv in names(RAW[[col]])) {
    rawn <- unname(RAW[[col]][lv])
    ln <- live$n[live$item == it & live$resp == as.integer(lv)]
    ln <- if (length(ln) == 0) 0 else as.integer(ln)
    if (ln != rawn) ok <- FALSE
    cat(sprintf("%-8s %-24s %6s %8d %8d %6d\n", col, it, lv, rawn, ln, ln - rawn))
  }
}

# A swap test: does any OTHER item also match this column's distribution?
cat("\nCross-match check (a correct mapping matches on the diagonal only):\n")
for (col in names(RAW)) {
  hits <- character(0)
  for (it in unique(live$item)) {
    v <- sapply(names(RAW[[col]]), function(lv) {
      x <- live$n[live$item == it & live$resp == as.integer(lv)]
      if (length(x) == 0) 0L else as.integer(x)
    })
    if (all(v == RAW[[col]])) hits <- c(hits, it)
  }
  cat(sprintf("  %s matches: %s\n", col, paste(hits, collapse = ", ")))
  if (length(hits) != 1 || hits != MAP[[col]]) ok <- FALSE
}

cat("\nNote: this establishes the item<->text and resp<->option_text mappings in full.\n")
cat("It does NOT verify the wording itself, which is transcribed from the S1 Appendix\n")
cat("survey instrument (Q28), nor the 'Please comment on...' instructions text.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
