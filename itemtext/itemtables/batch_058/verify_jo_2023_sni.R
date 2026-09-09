# verify_jo_2023_sni.R -- mapping verification for jo_2023_sni
#
# Mapping claim: item_text for SNI1/SNI2/SNI3 comes from S1 Appendix (Table A1)
# of Jo & Baek (2023), PLOS ONE 10.1371/journal.pone.0283997, which prints each
# item beside the very code the data uses. data/jo_2023_social_networking.py
# melts the S1 File CSV's own named columns SNI1/SNI2/SNI3 (no positional
# assignment), so the live item code IS the source column name.
#
# What this script checks: that each live item code carries the SAME per-level
# response distribution as the identically named column of the source CSV, and
# that the three distributions are mutually distinct -- i.e. the code->column
# tie is not merely asserted, and no permutation of the three would reproduce
# the live data. The appendix then ties that column name to the wording.
#
# Run: Rscript verify_jo_2023_sni.R

suppressMessages(library(irw))

SRC <- "https://doi.org/10.1371/journal.pone.0283997.s003"
tmp <- tempfile(fileext = ".csv")
download.file(SRC, tmp, quiet = TRUE)
src <- read.csv(tmp, fileEncoding = "latin1")

d <- irw_fetch("jo_2023_sni")   # ~1035 rows; trivial export
its <- c("SNI1", "SNI2", "SNI3")

dist <- function(x) as.vector(table(factor(x, levels = 1:7)))
live <- sapply(its, function(i) dist(d$resp[d$item == i]))
raw  <- sapply(its, function(i) dist(src[[i]]))

cat("Per-item response-level counts (resp 1..7)\n")
for (i in its) {
  cat(sprintf("  %s  live: %-28s src[%s]: %-28s match: %s\n", i,
              paste(live[, i], collapse = ","), i,
              paste(raw[, i], collapse = ","),
              identical(live[, i], raw[, i])))
}

ok_match <- all(sapply(its, function(i) identical(live[, i], raw[, i])))

cat("\nCross-pairings (a permutation would have to match here too):\n")
distinct <- TRUE
for (i in its) for (j in its) if (i != j) {
  eq <- identical(live[, i], raw[, j])
  if (eq) distinct <- FALSE
  cat(sprintf("  live %s vs src %s: %s\n", i, j, if (eq) "IDENTICAL (ambiguous!)" else "differs"))
}

cat("\nitem-code tie matched:", ok_match, "| all three distributions mutually distinct:", distinct, "\n")
if (ok_match && distinct) cat("VERDICT: PASS\n") else cat("VERDICT: FAIL\n")
