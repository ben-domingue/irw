## verify_lee2024_relative_clause.R  --  batch_015, issue #1774
##
## This table's codes are assigned POSITIONALLY by the processing script
## ("Unnamed: 1".."Unnamed: 18" -> rc_01..rc_18), which alone is the highest-risk
## pattern. The mapping was recovered rather than trusted, so this script re-runs
## the recovery: row 2 of the source xlsx is the real header and numbers all 25
## source columns, which is what places columns 1-18 on test items 1-18.
##
## Run from itemtext/:  Rscript itemtables/batch_015/verify_lee2024_relative_clause.R
suppressMessages({library(jsonlite); library(irw)})
TBL <- "lee2024_relative_clause"
CSV <- "itemtables/batch_015/lee2024_relative_clause__items.csv"
JSN <- "itemtables/batch_015/rederived.json"
fail <- character(0)
if (!file.exists(JSN)) system2("python3", "itemtables/batch_015/rederive.py")
hdr <- unlist(fromJSON(JSN, simplifyVector = FALSE)[[TBL]][["__header_row2__"]])
it  <- read.csv(CSV, stringsAsFactors = FALSE)

cat("=== 1. the recovered header row numbers all 25 source columns ===\n")
lab <- hdr[-1]                                  # drop the ID column
lab <- lab[nzchar(lab)]
n   <- suppressWarnings(as.integer(sub("^\\s*(\\d+)\\..*$", "\\1", lab)))
cat("  labelled columns:", length(lab), "| numbered 1..25 in order:",
    identical(n, 1:25), "\n")
if (!identical(n, 1:25)) fail <- c(fail, "row-2 header does not number 1..25 in order")

cat("\n=== 2. columns 1-18 are the 18 IRW items; 19-25 excluded ===\n")
codes <- sprintf("rc_%02d", 1:18)
cat("  shipped items identical to rc_01..rc_18:",
    identical(sort(unique(it$item)), sort(codes)), "\n")
cat("  source labels 19-25 (excluded, the O/X block):\n")
for (k in 19:25) cat("    ", lab[k], "\n")
if (!identical(sort(unique(it$item)), sort(codes))) fail <- c(fail, "item set is not rc_01..rc_18")

cat("\n=== 3. type codes corroborate the alignment ===\n")
chk <- list(c("rc_13","SG","whose"), c("rc_14","OG","whose"),
            c("rc_16","S IO","taught math to"), c("rc_08","SP","yelled to"))
for (c3 in chk) {
  code <- c3[1]; typ <- c3[2]; cue <- c3[3]
  k <- as.integer(sub("rc_", "", code))
  txt <- unique(it$item_text[it$item == code])
  ok <- grepl(typ, lab[k], fixed = TRUE) && grepl(cue, txt, fixed = TRUE)
  cat(sprintf("  %-6s label '%s' vs item text containing '%s': %s\n", code, lab[k], cue,
              ifelse(ok, "consistent", "*** INCONSISTENT ***")))
  if (!ok) fail <- c(fail, paste("type code mismatch:", code))
}

cat("\n=== 4. item and resp sets vs live ===\n")
live <- tryCatch(irw_fetch(TBL), error = function(e) NULL)
if (is.null(live) || !nrow(live)) { cat("  live data unavailable\n"); fail <- c(fail, "live data unavailable")
} else {
  cat("  item set identical:", identical(sort(unique(it$item)), sort(unique(as.character(live$item)))),
      "| resp set identical:", identical(sort(unique(as.numeric(it$resp))), sort(unique(as.numeric(live$resp)))), "\n")
}
cat("\n", strrep("-", 60), "\n", sep = "")
if (length(fail)) { cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
} else            { cat("VERDICT: PASS\n") }
