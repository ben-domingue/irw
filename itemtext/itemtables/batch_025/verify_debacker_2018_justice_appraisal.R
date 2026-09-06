# verify_debacker_2018_justice_appraisal.R
#
# EXPECTED OUTCOME: VERDICT: FAIL. This table is BLOCKED and ships no
# __items.csv. The script exists so the refutation that produced the block is
# re-runnable rather than only asserted in prose. A FAIL here is the recorded
# finding, not a regression.
#
# Claim under test: that the within-subscale index in the item codes
# (distrpers1-3, distrgroup1-3, procpers1-3, procgroup1-3) follows the order in
# which the 12 justice items are printed in the study's S2 File questionnaire
# (De Backer et al. 2018, PLOS ONE 10.1371/journal.pone.0205559, CC BY 4.0).
# That is the only mapping basis any in-scope source offers. It is falsifiable:
# exactly one of the 12 published items is reverse-worded ("The manner in which
# the coach approached me during the training and/or game was influenced by
# other players"), and it is printed THIRD in the personal-procedural block, so
# the hypothesis predicts the reverse-keyed item in the data is procpers3.
#
# Reads the study's own level-1 SPSS file from PLOS. Does NOT call irw_fetch:
# the IRW table is that file melted long by
# data/debacker_2018_coaching_justice.py with no renaming, so per-item
# correlations are identical and no Redivis export is spent.

suppressMessages(library(haven))

URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0205559.s003")
f <- file.path(tempdir(), "debacker_s003.sav")
if (!file.exists(f)) download.file(URL, f, quiet = TRUE, mode = "wb")
d <- as.data.frame(haven::read_sav(f))

ITEMS <- c("distrpers1", "distrpers2", "distrpers3",
           "distrgroup1", "distrgroup2", "distrgroup3",
           "procpers1", "procpers2", "procpers3",
           "procgroup1", "procgroup2", "procgroup3")
x <- d[, ITEMS]
x[x == 0] <- NA          # resp 0 is an unstripped not-applicable sentinel; see notes

# --- corrected item-total correlations: which item is reverse-keyed? ----------
cat(sprintf("%-12s %8s %8s\n", "item", "mean", "r_rest"))
rrest <- numeric(length(ITEMS)); names(rrest) <- ITEMS
for (i in ITEMS) {
    rest <- rowMeans(x[, setdiff(ITEMS, i)], na.rm = TRUE)
    rrest[i] <- cor(x[[i]], rest, use = "complete.obs")
    cat(sprintf("%-12s %8.2f %8.3f\n", i, mean(x[[i]], na.rm = TRUE), rrest[i]))
}

neg <- names(rrest)[rrest < 0]
cat(sprintf("\nitems with negative corrected item-total: %s\n",
            if (length(neg)) paste(neg, collapse = ", ") else "(none)"))
cat("S2-File-order hypothesis predicts: procpers3\n")

# --- the two blocks whose members ARE separable ------------------------------
cat(sprintf("\nr(distrgroup2,distrgroup3) = %.3f  vs  r(distrgroup1,distrgroup2) = %.3f, r(distrgroup1,distrgroup3) = %.3f\n",
            cor(x$distrgroup2, x$distrgroup3, use = "complete.obs"),
            cor(x$distrgroup1, x$distrgroup2, use = "complete.obs"),
            cor(x$distrgroup1, x$distrgroup3, use = "complete.obs")))
cat("  -> distrgroup2/3 are the two near-synonymous equality items; distrgroup1 is the\n",
    "     talent/competence selection item. Pins distrgroup1 only, not 2 vs 3.\n", sep = "")
cat(sprintf("\ndistrpers within-block r: 1-2 %.3f, 1-3 %.3f, 2-3 %.3f\n",
            cor(x$distrpers1, x$distrpers2, use = "complete.obs"),
            cor(x$distrpers1, x$distrpers3, use = "complete.obs"),
            cor(x$distrpers2, x$distrpers3, use = "complete.obs")))
cat(sprintf("procgroup within-block r: 1-2 %.3f, 1-3 %.3f, 2-3 %.3f\n",
            cor(x$procgroup1, x$procgroup2, use = "complete.obs"),
            cor(x$procgroup1, x$procgroup3, use = "complete.obs"),
            cor(x$procgroup2, x$procgroup3, use = "complete.obs")))
cat("  -> no separating structure in either block.\n")

ok <- identical(neg, "procpers3")
cat("\nWhat this does NOT establish either way: subscale membership, which is not in\n",
    "doubt (the item codes name distr/proc and pers/group themselves, and the S2 File's\n",
    "12 items partition 3+3+3+3 into exactly those four categories).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
