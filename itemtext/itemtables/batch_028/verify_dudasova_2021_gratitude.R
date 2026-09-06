# verify_dudasova_2021_gratitude.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM UNDER TEST: the six live item codes Grat1..Grat6 are the six items of the
# Gratitude Questionnaire-Six Item Form (GQ-6; McCullough, Emmons & Tsang 2002)
# IN CANONICAL NUMBER ORDER, i.e. Grat1 = GQ-6 item 1 ... Grat6 = GQ-6 item 6.
# The paper (PLOS ONE 10.1371/journal.pone.0247114) never mentions gratitude and
# the S1 .sav carries NO variable or value labels, so the mapping is reconstructed.
#
# FALSIFIABLE PREDICTION: the GQ-6 has exactly two reverse-worded items, 3 and 6.
# The S1 .sav's own naming convention marks recoded reverse items with a trailing
# "i" (JS3i, Hope3i/5i/7i/11i, Perf14i-18i -- all of which show POSITIVE item-rest
# correlations, confirming "i" == already recoded). In the gratitude block only
# Grat3i carries the marker; Grat6 does not and is therefore stored RAW. So if the
# canonical numbering holds, Grat6 -- and Grat6 alone -- must correlate NEGATIVELY
# with every other item, and Grat3i must correlate positively with them.
# Under a random permutation of the six texts, the chance that the two canonical
# reverse items land on exactly {position 3 (marked), position 6 (unmarked)} is 1/30.
#
# The script fetches the live table (1,692 rows -- negligible export) and prints
# the full correlation matrix.

suppressMessages(library(irw))
TABLE <- "dudasova_2021_gratitude"
ITEMS <- c("Grat1","Grat2","Grat3i","Grat4","Grat5","Grat6")

d <- as.data.frame(irw::irw_fetch(TABLE))
d <- d[, c("id","item","resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[, ITEMS, drop = FALSE]
cat("N respondents:", nrow(w), "\n\n")

m <- round(cor(w, use = "pairwise.complete.obs"), 2)
cat("Correlation matrix (live data):\n"); print(m); cat("\n")

means <- round(colMeans(w, na.rm = TRUE), 2)
cat("Item means:\n"); print(means); cat("\n")

offdiag_mean <- sapply(ITEMS, function(i) mean(m[i, setdiff(ITEMS, i)]))
cat("Mean off-diagonal r per item:\n"); print(round(offdiag_mean, 3)); cat("\n")

neg <- ITEMS[offdiag_mean < 0]
cat("Items with mean NEGATIVE correlation to the rest:",
    paste(neg, collapse = ", "), "\n")
cat("Expected under canonical GQ-6 numbering + the file's 'i' recode convention: Grat6\n\n")

# Secondary, weaker check: GQ-6 items 5 and 6 are the two weakest indicators in
# every published validation (item 6 is the one dropped to form the GQ-5).
absr <- sapply(ITEMS, function(i) mean(abs(m[i, setdiff(ITEMS, i)])))
weakest2 <- names(sort(absr))[1:2]
cat("Two weakest items by mean |r|:", paste(weakest2, collapse = ", "),
    "-- expected Grat5, Grat6\n")
cat("mean |r| per item:\n"); print(round(absr, 3)); cat("\n")

ok1 <- identical(sort(neg), "Grat6")
ok2 <- setequal(weakest2, c("Grat5","Grat6"))
cat("check 1 (Grat6 is the unique negatively-keyed item):", ok1, "\n")
cat("check 2 (Grat5 and Grat6 are the two weakest):", ok2, "\n\n")

cat("WHAT THIS DOES NOT ESTABLISH: it pins the reverse-worded pair to positions\n",
    "3 and 6 and separates them from the four positively-worded items, but it does\n",
    "NOT distinguish Grat1 from Grat2 (r = 0.81, near-duplicate GQ-6 content), nor\n",
    "Grat4 from Grat5 beyond the weak-indicator argument, nor prove Grat3i is GQ-6\n",
    "item 3 rather than item 6 except by the 'i' marker plus its stronger item-rest\n",
    "correlation. Status is therefore PARTIAL, not VERIFIED.\n", sep = "")

cat(if (ok1 && ok2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
