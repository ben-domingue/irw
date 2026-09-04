# verify_conner_2017_bfi.R
#
# CLAIM UNDER TEST (the option_text <-> resp axis, not the plumbing):
#   The 16 canonically reverse-keyed BFI-44 items are stored ALREADY REVERSED in
#   this table, so the anchors shipped for those items run 1 = "Strongly Agree"
#   ... 5 = "Strongly disagree", the OPPOSITE of the direction the source .sav's
#   own value labels state (labels18: 1 = Strongly disagree ... 5 = Strongly Agree).
#   The .sav variable labels assert the same thing in prose -- each of those 16
#   carries the suffix "(already reverse scored)" -- but a label is an assertion,
#   so it is checked here against the data.
#
# FALSIFIABLE PREDICTION (route 6, keying polarity):
#   If the data were stored RAW, each reverse-keyed item would correlate
#   NEGATIVELY with the other items of its own Big Five domain. If stored already
#   reversed, all 44 items correlate POSITIVELY within domain. The sign of the
#   mean within-domain correlation for the 16 R items is therefore the test.
#
# WHAT THIS DOES NOT ESTABLISH:
#   It does not distinguish one item from another within a polarity class -- it
#   pins a DIRECTION, not an identity. Item identity (bfi1..bfi44 -> wording)
#   rests on the source .sav's own variable labels (mapping_basis = data_labels,
#   and data/conner_2017_fruit.py melts those columns under their own names), not
#   on this script. Hence status PARTIAL.

suppressMessages(library(irw))

TABLE <- "conner_2017_bfi"

DOMAIN <- list(
  Extraversion      = c(1, 6, 11, 16, 21, 26, 31, 36),
  Agreeableness     = c(2, 7, 12, 17, 22, 27, 32, 37, 42),
  Conscientiousness = c(3, 8, 13, 18, 23, 28, 33, 38, 43),
  Neuroticism       = c(4, 9, 14, 19, 24, 29, 34, 39),
  Openness          = c(5, 10, 15, 20, 25, 30, 35, 40, 41, 44)
)
REV <- c(2, 6, 8, 9, 12, 18, 21, 23, 24, 27, 31, 34, 35, 37, 41, 43)

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- as.data.frame(tapply(d$resp, list(d$id, d$item), function(x) x[1]))

cat(sprintf("%-18s %-7s %-3s %8s %7s\n",
            "domain", "item", "key", "mean_r", "mean"))
res <- data.frame()
for (s in names(DOMAIN)) {
  it <- DOMAIN[[s]]
  for (i in it) {
    oth <- paste0("bfi", setdiff(it, i))
    r <- mean(cor(w[[paste0("bfi", i)]], w[, oth], use = "pairwise.complete.obs"))
    m <- mean(w[[paste0("bfi", i)]], na.rm = TRUE)
    cat(sprintf("%-18s %-7s %-3s %+8.3f %7.2f\n",
                s, paste0("bfi", i), if (i %in% REV) "R" else "-", r, m))
    res <- rbind(res, data.frame(i = i, rev = i %in% REV, r = r))
  }
}

rev_r <- res$r[res$rev]
fwd_r <- res$r[!res$rev]
cat(sprintf("\n16 reverse-keyed items : mean within-domain r range %+.3f .. %+.3f (all positive: %s)\n",
            min(rev_r), max(rev_r), all(rev_r > 0)))
cat(sprintf("28 forward-keyed items : mean within-domain r range %+.3f .. %+.3f (all positive: %s)\n",
            min(fwd_r), max(fwd_r), all(fwd_r > 0)))
cat(sprintf("negative correlations among the 16: %d of 16 (raw storage would predict 16)\n",
            sum(rev_r < 0)))

# Semantic cross-check: under the already-reversed reading, the raw endorsement of
# "Starts quarrels with others" (bfi12) is 6 - stored mean, which must be low in a
# healthy young-adult sample; under the raw reading it would be the stored mean.
m12 <- mean(w$bfi12, na.rm = TRUE)
cat(sprintf("bfi12 'Starts quarrels with others': stored mean %.2f -> raw endorsement %.2f\n",
            m12, 6 - m12))

ok <- all(rev_r > 0) && all(fwd_r > 0)
cat("\nNote: this route pins the STORAGE DIRECTION of all 44 items; it does not\n")
cat("separate items within a polarity class. Item identity comes from the .sav\n")
cat("variable labels, not from this script.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
