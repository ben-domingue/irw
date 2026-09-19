# verify_kim_2023_pss10.R -- Step 5b, mapping evidence BANKED for a blocked table.
#
# STATUS: kim_2023_pss10 is BLOCKED on instrument rights (PSS family; irw#1945
# 2026-09-05, irw#1955 2026-09-06, extended 2026-09-07 to the whole PSS family).
# No __items.csv was written and NO ITEM WORDING is reproduced here. What this
# script banks is (a) the code -> source-column identity, so a reversal of the
# ruling is a re-run rather than a restart, and (b) a mapping ANOMALY that any
# future extraction must resolve before assigning canonical PSS-10 wording.
#
# Claim under test (the MAPPING, not the plumbing):
#   1. The live item codes PSS_1..PSS_10 ARE the column names of the study's own
#      S1 File .sav. data/kim_2023_pss_phq_gad.py melts [f"PSS_{i}" for i in
#      1..10] BY NAME -- no positional step -- so per-item n and mean must
#      reproduce cell for cell from the source file. A permuted item would break
#      this immediately.
#   2. The stored values are RAW (unreversed): the .sav's own PSS_T column equals
#      the plain unreversed sum of PSS_1..PSS_10 for every respondent.
#   3. ANOMALY, reported not asserted: the correlation matrix splits the ten
#      items into {PSS_1,2,3,9,10} and {PSS_4,5,6,7,8}, NOT the canonical PSS-10
#      keying split {4,5,7,8} positive vs {1,2,3,6,9,10} negative. PSS_6 sits
#      with the positively-worded block. So the trailing digit CANNOT be assumed
#      to be the canonical PSS-10 item number for this table.
#
# VERDICT is PASS when 1 and 2 reproduce; 3 is printed as a caveat either way.

suppressMessages(library(irw))

TABLE  <- "kim_2023_pss10"
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0278921.s001")
COLS <- paste0("PSS_", 1:10)

cache <- file.path("..", "..", ".cache", TABLE, "s001.sav")
if (!file.exists(cache)) {
  dir.create(dirname(cache), recursive = TRUE, showWarnings = FALSE)
  utils::download.file(SI_URL, cache, mode = "wb", quiet = TRUE)
}
raw <- as.data.frame(haven::read_sav(cache))

live <- irw::irw_fetch(TABLE)
live$resp <- as.numeric(live$resp)

ok <- TRUE

cat("== 1. code -> source-column identity (n and mean per item) ==\n")
cat(sprintf("%-8s %6s %6s %10s %10s %12s\n",
            "item", "n_src", "n_live", "mean_src", "mean_live", "abs_diff"))
for (cl in COLS) {
  s <- raw[[cl]]; s <- s[!is.na(s)]
  l <- live$resp[live$item == cl]
  d <- abs(mean(s) - mean(l))
  cat(sprintf("%-8s %6d %6d %10.6f %10.6f %12.3e\n",
              cl, length(s), length(l), mean(s), mean(l), d))
  if (length(s) != length(l) || d > 1e-10) ok <- FALSE
}

cat("\n== 2. stored raw vs already-reversed (source PSS_T vs sums) ==\n")
d  <- raw[stats::complete.cases(raw[, COLS]), COLS]
tt <- raw[stats::complete.cases(raw[, COLS]), "PSS_T"]
raw_sum <- rowSums(d)
rev_d <- d; for (i in c(4, 5, 7, 8)) rev_d[[paste0("PSS_", i)]] <- 4 - rev_d[[paste0("PSS_", i)]]
rev_sum <- rowSums(rev_d)
cat(sprintf("PSS_T == unreversed sum for %d/%d respondents (mean %.4f vs %.4f)\n",
            sum(tt == raw_sum), length(tt), mean(tt), mean(raw_sum)))
cat(sprintf("PSS_T == canonically-reversed sum for %d/%d respondents (mean %.4f)\n",
            sum(tt == rev_sum), length(tt), mean(rev_sum)))
if (!all(tt == raw_sum)) ok <- FALSE

cat("\n== 3. ANOMALY: polarity blocks vs canonical PSS-10 keying ==\n")
cm <- stats::cor(d)
A <- paste0("PSS_", c(1, 2, 3, 9, 10)); B <- paste0("PSS_", c(4, 5, 6, 7, 8))
wi <- function(g) { v <- cm[g, g][upper.tri(cm[g, g])]; sprintf("%.2f..%.2f", min(v), max(v)) }
cr <- as.vector(cm[A, B])
cat(sprintf("within {1,2,3,9,10}: %s | within {4,5,6,7,8}: %s | cross: %.2f..%.2f\n",
            wi(A), wi(B), min(cr), max(cr)))
cat(sprintf("canonical positive set {4,5,7,8} vs rest, cross range: %.2f..%.2f\n",
            min(as.vector(cm[paste0("PSS_", c(4, 5, 7, 8)),
                             paste0("PSS_", c(1, 2, 3, 6, 9, 10))])),
            max(as.vector(cm[paste0("PSS_", c(4, 5, 7, 8)),
                             paste0("PSS_", c(1, 2, 3, 6, 9, 10))]))))
cat("PSS_6 loads with the {4,5,7,8} block, so the digit is NOT safely the\n",
    "canonical PSS-10 item number. Unresolved; no wording was assigned.\n", sep = "")

cat("\n", if (ok) "VERDICT: PASS" else "VERDICT: FAIL", "\n", sep = "")
