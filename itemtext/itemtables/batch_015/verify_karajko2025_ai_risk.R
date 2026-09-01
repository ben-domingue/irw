## verify_karajko2025_ai_risk.R  --  batch_015, issue #1774
##
## Re-derives the shipped text from the cached Dataverse source via
## rederive.py and diffs it, so this checks the mapping rather than the plumbing:
## an evidence string cannot be re-run, a rebuild can.
##
## Run from itemtext/:  Rscript itemtables/batch_015/verify_karajko2025_ai_risk.R
suppressMessages({library(jsonlite); library(irw)})
TBL <- "karajko2025_ai_risk"
CSV <- "itemtables/batch_015/karajko2025_ai_risk__items.csv"
JSN <- "itemtables/batch_015/rederived.json"
fail <- character(0)

if (!file.exists(JSN)) system2("python3", "itemtables/batch_015/rederive.py")
src <- fromJSON(JSN, simplifyVector = FALSE)[[TBL]]
it  <- read.csv(CSV, stringsAsFactors = FALSE)

cat("=== 1. item_text re-derived from source, per item ===\n")
bad <- 0
for (code in names(src)) {
  want <- src[[code]]$text
  got  <- unique(it$item_text[it$item == code])
  if (length(got) != 1 || !identical(got, want)) {
    bad <- bad + 1
    if (bad <= 3) cat(sprintf("  MISMATCH %s\n    source : %s\n    shipped: %s\n",
                              code, substr(want,1,90), substr(paste(got,collapse="|"),1,90)))
  }
}
cat(sprintf("  items compared: %d | mismatches: %d\n", length(src), bad))
if (bad) fail <- c(fail, "item_text mismatch")

cat("\n=== 2. the _translated columns are deliberately empty ===\n")
tt <- unique(c(it$item_text_translated, it$option_text_translated))
cat("  distinct values in the _translated columns:", paste(unique(tt), collapse=", "), "\n")
cat("  (empty by design: no English exists in this record for this block -- see provenance)\n")

cat("\n=== 3. option_text per resp level ===\n")
obad <- 0
for (code in names(src)) {
  o <- src[[code]]$opts
  for (r in names(o)) {
    got <- it$option_text[it$item == code & as.character(it$resp) == r]
    if (length(got) != 1 || !identical(got, o[[r]])) obad <- obad + 1
  }
}
cat(sprintf("  option cells checked: %d | mismatches: %d\n",
            sum(vapply(src, function(x) length(x$opts), 1L)), obad))
if (obad) fail <- c(fail, "option_text mismatch")

cat("\n=== 4. item and resp sets vs live ===\n")
live <- tryCatch(irw_fetch(TBL), error = function(e) NULL)
if (is.null(live) || !nrow(live)) {
  cat("  live data unavailable -- sets unchecked\n"); fail <- c(fail, "live data unavailable")
} else {
  si <- identical(sort(unique(as.character(it$item))), sort(unique(as.character(live$item))))
  sr <- identical(sort(unique(as.numeric(it$resp))), sort(unique(as.numeric(live$resp))))
  cat("  item set identical:", si, "| resp set identical:", sr, "| live rows:", nrow(live), "\n")
  if (!si || !sr) fail <- c(fail, "live set mismatch")
}

cat("\n", strrep("-", 60), "\n", sep = "")
if (length(fail)) { cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
} else            { cat("VERDICT: PASS\n") }
