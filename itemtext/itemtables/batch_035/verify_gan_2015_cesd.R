# verify_gan_2015_cesd.R -- Step 5b re-runnable evidence.
#
# CLAIM: the item codes CES1..CES20 in gan_2015_cesd are the canonical CES-D
# (Radloff 1977) item numbers 1..20, so CES4 = "I felt that I was just as good
# as other people", CES8 = "I felt hopeful about the future", CES12 = "I was
# happy", CES16 = "I enjoyed life" -- the four positively worded, reverse-keyed
# items -- and the other 16 are the negatively worded ones.
#
# FALSIFIABLE PREDICTION (route 6, keying polarity): the source paper states
# outright "Four items (4, 8, 12, 16) are reverse-scored"
# (Gan et al. 2015, PLoS ONE 10(9):e0137176, Measures / CES-D).  If the shipped
# text were permuted onto different codes, the polarity signature in the live
# data would not sit on exactly {CES4, CES8, CES12, CES16}: those four must
# correlate NEGATIVELY with the sum of the other sixteen (the data are stored
# raw, not reverse-scored), and POSITIVELY with each other.
#
# This would break if, say, CES4's and CES5's item_text were swapped.
#
# WHAT IT DOES NOT ESTABLISH: it separates the reverse-worded quadruple from the
# other sixteen as SETS. It does not distinguish CES4 from CES8/CES12/CES16, nor
# order the sixteen negatively worded items among themselves. Hence PARTIAL.
# A weak secondary signal is printed for semantic coherence (route 8).

suppressMessages(library(irw))
suppressMessages(library(stats))

TABLE <- "gan_2015_cesd"
REV   <- paste0("CES", c(4, 8, 12, 16))
ALL   <- paste0("CES", 1:20)
NEG   <- setdiff(ALL, REV)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", ALL)]
w <- w[complete.cases(w), ]
cat(sprintf("complete cases used: %d of %d respondents\n", nrow(w), length(unique(d$id))))

negsum <- rowSums(w[, NEG])

cat("\nper-item correlation with the sum of the 16 negatively worded items\n")
cat(sprintf("%-7s %6s %6s %8s\n", "item", "mean", "r", "keying"))
r <- setNames(numeric(length(ALL)), ALL)
for (it in ALL) {
    rest <- if (it %in% NEG) rowSums(w[, setdiff(NEG, it)]) else negsum
    r[it] <- cor(w[[it]], rest)
    cat(sprintf("%-7s %6.2f %6.2f %8s\n", it, mean(w[[it]]), r[it],
                if (it %in% REV) "reverse" else "-"))
}

cat("\nintercorrelations among the four claimed reverse-worded items:\n")
print(round(cor(w[, REV]), 2))

max_rev <- max(r[REV]); min_neg <- min(r[NEG])
cat(sprintf("\nlargest r among the four reverse items : %.3f\n", max_rev))
cat(sprintf("smallest r among the sixteen others    : %.3f\n", min_neg))
cat(sprintf("minimum intercorrelation within the reverse quadruple: %.3f\n",
            min(cor(w[, REV])[upper.tri(cor(w[, REV]))])))

# Semantic coherence (route 8, supporting only): in a nursing-home sample,
# "My sleep was restless" (CES11) should be the most endorsed negatively worded
# symptom and "I thought my life had been a failure" (CES9) among the least.
m <- sapply(w[, NEG], mean)
cat(sprintf("\nhighest-mean negative item: %s (%.2f); lowest: %s (%.2f)\n",
            names(which.max(m)), max(m), names(which.min(m)), min(m)))

ok <- max_rev < 0 && min_neg > 0.2 &&
      all(cor(w[, REV])[upper.tri(cor(w[, REV]))] > 0)

cat("\nNote: this pins the reverse-worded QUADRUPLE {CES4,CES8,CES12,CES16} against\n",
    "the other sixteen, matching the paper's own statement of which item numbers are\n",
    "reverse-scored. It does NOT distinguish CES4 from CES8/CES12/CES16, nor order the\n",
    "sixteen negatively worded items among themselves. Status is PARTIAL, not VERIFIED.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
