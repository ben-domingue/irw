# verify_park_2024_ageism.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: item code a<k> in the IRW table is question <k> of the ageism
# block of the study's own questionnaire (S2 File of PLOS ONE 19(11):e0313043),
# an 18-item Korean form of the Fraboni Scale of Ageism. The workbook headers are
# bare codes a1..a18 with no text, so the tie rests on the questionnaire's own
# numbering; this script makes that tie falsifiable against the response data.
#
# ROUTE 6 (keying polarity). Four of the 18 questions are worded PRO-elderly and
# the table stores responses RAW (the burnout block in the same workbook ships
# explicit "역산"/reverse twin columns; the ageism block does not). So those four
# and only those four must correlate NEGATIVELY with the rest of the scale:
#   4  "It's a lot of fun to be with an old person."
#   6  "Most old people are interesting and individualistic."
#   11 "Older people deserve the same freedoms and rights as other members of our society."
#   12 "It's sad to hear about the plight of old people."
# Under a random permutation of the 18 texts the chance of the pro-elderly four
# landing exactly on the four negatively-keyed codes is 1/choose(18,4) = 1/3060.
#
# ROUTE 8 (semantic coherence of the response distribution). Three ordinal
# predictions the item wording makes about item means, on a 1=strongly disagree
# .. 4=strongly agree scale in a sample of clinical nurses:
#   a11 (equal freedoms and rights) is the MOST endorsed of all 18;
#   a12 (sad to hear about their plight) is the SECOND most endorsed;
#   a10 ("Seniors have virtually no need for local sports facilities", the most
#       flatly indefensible statement in the set) is the LEAST endorsed.

suppressMessages(library(irw))

TABLE <- "park_2024_ageism"
ITEMS <- paste0("a", 1:18)
PRO_ELDERLY <- c("a4", "a6", "a11", "a12")

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
m <- sapply(ITEMS, function(i) as.numeric(w[[i]]))

ir <- sapply(ITEMS, function(i)
    cor(m[, i], rowMeans(m[, setdiff(ITEMS, i), drop = FALSE], na.rm = TRUE), use = "pairwise"))
mu <- colMeans(m, na.rm = TRUE)

cat(sprintf("%-5s %6s %8s  %s\n", "item", "mean", "item-rest", "keying predicted from questionnaire text"))
for (i in ITEMS)
    cat(sprintf("%-5s %6.2f %8.3f  %s\n", i, mu[i], ir[i],
                if (i %in% PRO_ELDERLY) "PRO-ELDERLY -> expect NEGATIVE" else "ageist -> expect POSITIVE"))

neg <- ITEMS[ir < 0]
cat("\nnegatively keyed observed: ", paste(neg, collapse = ", "), "\n", sep = "")
cat("pro-elderly text predicts:  ", paste(PRO_ELDERLY, collapse = ", "), "\n", sep = "")
cat(sprintf("separation: max item-rest among the four = %.3f, min among the other 14 = %.3f\n",
            max(ir[PRO_ELDERLY]), min(ir[setdiff(ITEMS, PRO_ELDERLY)])))
ok_polarity <- setequal(neg, PRO_ELDERLY)

ord <- names(sort(mu, decreasing = TRUE))
cat(sprintf("\nmost endorsed  = %s (%.2f); predicted a11 (equal freedoms and rights)\n", ord[1], mu[ord[1]]))
cat(sprintf("second         = %s (%.2f); predicted a12 (sad to hear of their plight)\n", ord[2], mu[ord[2]]))
cat(sprintf("least endorsed = %s (%.2f); predicted a10 (no need for sports facilities)\n",
            ord[18], mu[ord[18]]))
ok_order <- ord[1] == "a11" && ord[2] == "a12" && ord[18] == "a10"

cat("\nWhat this does NOT establish: the two routes pin the four pro-elderly items as a\n",
    "SET and fix three individual positions (a10, a11, a12). They do not order the four\n",
    "pro-elderly items among themselves (a4 vs a6), nor the remaining eleven ageist items\n",
    "among themselves, so a swap inside either block would survive this check. The\n",
    "mapping is PARTIAL, not VERIFIED. The paper's own Table 2 statistics are NOT usable\n",
    "as a third route: they do not reproduce from the deposit for either instrument.\n", sep = "")

cat(if (ok_polarity && ok_order) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
