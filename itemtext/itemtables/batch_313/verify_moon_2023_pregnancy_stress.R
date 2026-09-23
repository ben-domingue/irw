# verify_moon_2023_pregnancy_stress.R -- Step 5b re-runnable check (batch_313).
#
# Mapping claim: item code pregnancystressN <-> item_text is tied at the SOURCE.
# The study's own questionnaire (PeerJ 10.7717/peerj.16295, Supplemental File
# peerj-11-16295-s002.pdf, page "- 4 -", section 5) prints each SPSS column
# name (pregnancystress1..pregnancystress11, in red) in the row beside its item,
# and data/moon_2023_pregnancy_stress.py melts those .sav columns BY NAME
# (derivation pattern 1: IRW item == source column name). So the tie is a
# label match, not an order inference.
#
# Checks:
#  (1) the shipped CSV's code->text pairs equal the pairs printed in s002
#      (hard-coded below from the questionnaire page); 11/11 required.
#  (2) corroboration from live data (these pin only SOME items):
#      - overall item-mean vs paper Table 2 (1.59 +/- 0.81, N=206, 1-4 scale);
#      - "Finantial worries" (item 1) is the most-endorsed stressor;
#      - "Being exposed to violence (physical)" (item 8) is the least endorsed;
#      - the two violence items + recent loss + substance items (7,8,9,10) all
#        have floor >= 70%, i.e. rare stressors sit at the floor.
#  What (2) does NOT establish: order among the mid-range items 2-6, 11
#  (2 and 3 have near-identical means 1.74/1.74). Only check (1) separates those.

suppressMessages(library(irw))
TABLE <- "moon_2023_pregnancy_stress"

SOURCE_PAIRS <- c(
 pregnancystress1  = "Finantial worries",
 pregnancystress2  = "Family problems (e.g.children, etc)",
 pregnancystress3  = "Parents-in-law or relatives problems",
 pregnancystress4  = "Sexual life problems",
 pregnancystress5  = "marital relationship problems",
 pregnancystress6  = "Housing or Surrounding environment(including moving) problems",
 pregnancystress7  = "Being exposed to violence (emotional)",
 pregnancystress8  = "Being exposed to violence (physical)",
 pregnancystress9  = "Having lost someone you love recently (e.g., death, divorce, being away from each other)",
 pregnancystress10 = "Problems about consuming alcohol or cigaretts and coffee",
 pregnancystress11 = "Problems about work life(housework or job)")

ok <- TRUE
here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) NULL)
if (is.null(here)) {
  a <- commandArgs(FALSE); f <- sub("^--file=", "", a[grep("^--file=", a)])
  here <- if (length(f)) dirname(normalizePath(f)) else "."
}
csv <- file.path(here, paste0(TABLE, "__items.csv"))
it <- read.csv(csv, stringsAsFactors = FALSE)
shipped <- unique(it[, c("item", "item_text")])
shipped_txt <- setNames(shipped$item_text, shipped$item)[names(SOURCE_PAIRS)]
match <- shipped_txt == SOURCE_PAIRS
cat("(1) code->text pairs vs questionnaire s002 p.4:\n")
for (k in names(SOURCE_PAIRS)) cat(sprintf("  %-18s %s  %s\n", k, if (isTRUE(match[k])) "OK  " else "DIFF", shipped_txt[k]))
cat(sprintf("  %d/11 match\n\n", sum(match, na.rm = TRUE)))
ok <- ok && sum(match, na.rm = TRUE) == 11

d <- irw::irw_fetch(TABLE)
mu <- tapply(d$resp, d$item, mean)[names(SOURCE_PAIRS)]
fl <- tapply(d$resp == 1, d$item, mean)[names(SOURCE_PAIRS)]
cat("(2) live per-item mean / floor%:\n")
for (k in names(mu)) cat(sprintf("  %-18s %.2f  %5.1f%%  %s\n", k, mu[k], 100 * fl[k], SOURCE_PAIRS[k]))
pm <- rowMeans(sapply(split(d, d$item), function(x) x$resp[match(sort(unique(d$id)), x$id)]), na.rm = TRUE)
cat(sprintf("\n  person-mean scale score: %.2f (SD %.2f), paper Table 2: 1.59 (SD 0.81)\n", mean(pm), sd(pm)))
cat(sprintf("  pooled over all person-item responses: %.2f (SD %.2f) -- the paper's SD 0.81 matches this pooled form\n", mean(d$resp), sd(d$resp)))
c_a <- abs(mean(pm) - 1.59) <= 0.05 && abs(sd(d$resp) - 0.81) <= 0.02
c_b <- names(which.max(mu)) == "pregnancystress1"
c_c <- names(which.min(mu)) == "pregnancystress8"
c_d <- all(fl[paste0("pregnancystress", 7:10)] >= 0.70)
cat(sprintf("  mean within 0.05 of 1.59: %s\n  max-mean item is pregnancystress1 (financial): %s (%s)\n  min-mean item is pregnancystress8 (physical violence): %s (%s)\n  items 7-10 floor >= 70%%: %s\n",
            c_a, c_b, names(which.max(mu)), c_c, names(which.min(mu)), c_d))
cat("Note: (2) is corroborative only; it does not order items 2-6 and 11. Check (1), the\n",
    "questionnaire's printed column names, is what distinguishes every item.\n", sep = "")
ok <- ok && c_a && c_b && c_c && c_d
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
