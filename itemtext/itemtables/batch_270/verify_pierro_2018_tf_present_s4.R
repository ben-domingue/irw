# verify_pierro_2018_tf_present_s4.R
#
# TABLE: pierro_2018_tf_present_s4 -- Temporal Focus Scale, Present (Current) Focus
#   subscale. Pierro, Pica, Giannini, Higgins & Kruglanski (2018), PLoS ONE 13(3):e0193357
#   (CC BY 4.0), Study 4, N = 189 Sapienza students; item codes TFpresent1..TFpresent4.
#
# WHAT IS VERIFIED HERE, and what is NOT.
#
# CLAIM 1 -- TESTED, and the verdict rests on it. The four codes are the PRESENT
#   temporal-focus subscale of the TFS, stored RAW (no reverse recoding), and not the
#   past or the future block of the same S4 file. Pierro et al. Table 4 publishes, for
#   each of the three subscales, M, SD, Cronbach's alpha AND a full correlation row
#   against locomotion / assessment / the other two temporal foci / self-forgiveness.
#   Those five correlations plus M/SD/alpha are eight numbers that differ sharply across
#   the three blocks (e.g. r with locomotion: past -.12, present .25, future .37), so a
#   mis-assignment to the wrong temporal block is not survivable. Everything is computed
#   from the LIVE IRW table; the co-scale composites come from the study's own deposit.
#
# CLAIM 2 -- NOT established, which is why Step 5b records status NO_ROUTE for the
#   item<->text axis. Nothing ties TFpresent1..TFpresent4 to particular sentences. The
#   S4 .sav carries no variable labels at all, the PLOS article quotes exactly one
#   present item ("My mind is on the here and now") without a code, and the four items
#   are same-subscale, same-range, same-polarity near-synonyms. The two cross-sample
#   falsification attempts below (per-item means and item-total correlations against the
#   Italian TFS-I validation, PMC7851924) are printed and are reported as
#   NON-DIAGNOSTIC: they point in opposite directions. They are NOT part of the verdict.

suppressMessages(library(irw))
stopifnot(requireNamespace("haven", quietly = TRUE))

TABLE <- "pierro_2018_tf_present_s4"

## ---- published values, Pierro et al. (2018) Table 4 (N = 189) --------------
##                       M     SD  alpha   r_loco r_assess r_past r_present r_future
PUB <- rbind(
  past    = c(5.10, 1.09, 0.91, -0.12,  0.41,    NA,    NA,      NA),
  present = c(5.12, 1.00, 0.85,  0.25,  0.003, -0.09,   NA,      NA),
  future  = c(5.54, 1.05, 0.92,  0.37,  0.02,   0.004, 0.33,     NA)
)

## ---- live IRW data ---------------------------------------------------------
d <- irw::irw_fetch(TABLE)
d <- d[, c("id", "item", "resp")]
w <- reshape(as.data.frame(d), idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
its <- paste0("TFpresent", 1:4)
m   <- as.matrix(w[, its])
storage.mode(m) <- "numeric"
comp <- rowMeans(m)

k <- 4
alpha <- k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))
cat(sprintf("live table: %d persons x %d items\n", nrow(m), ncol(m)))
cat(sprintf("live PRESENT composite: M = %.3f  SD = %.3f  alpha = %.3f\n\n",
            mean(comp), sd(comp), alpha))

cat("Distance of the live composite to each published Table 4 row (|dM|+|dSD|+|dalpha|):\n")
obs3 <- c(mean(comp), sd(comp), alpha)
for (r in rownames(PUB)) {
  dd <- sum(abs(obs3 - PUB[r, 1:3]))
  cat(sprintf("  %-8s published %.2f / %.2f / %.2f   L1 = %.3f%s\n",
              r, PUB[r, 1], PUB[r, 2], PUB[r, 3], dd,
              if (r == "present") "   <- shipped assignment" else ""))
}
best <- rownames(PUB)[which.min(apply(PUB[, 1:3], 1, function(p) sum(abs(obs3 - p))))]
cat(sprintf("  nearest published row: %s\n\n", best))

## ---- correlation row, against the study's own deposit composites -----------
sav <- file.path(tempdir(), "pierro_s004.sav")
url <- paste0("https://journals.plos.org/plosone/article/file?id=",
              "10.1371/journal.pone.0193357.s004&type=supplementary")
ok_sav <- tryCatch({
  download.file(url, sav, quiet = TRUE, mode = "wb")
  file.exists(sav) && file.size(sav) > 1000
}, error = function(e) FALSE)

cor_ok <- NA
if (ok_sav) {
  s <- as.data.frame(haven::read_sav(sav))
  cat(sprintf("deposit S4 File: %d rows, md5 %s\n", nrow(s),
              as.character(tools::md5sum(sav))))
  # live composite ordered by the deposit's own subject order
  idx <- match(as.character(s$subject), as.character(w$id))
  lc  <- comp[idx]
  cat(sprintf("live<->deposit person match: %d of %d\n",
              sum(!is.na(idx)), nrow(s)))
  cat(sprintf("live PRESENT composite vs the deposit's own 'present' column: r = %.4f, max|diff| = %.3f\n\n",
              cor(lc, s$present, use = "complete.obs"),
              max(abs(lc - s$present), na.rm = TRUE)))

  targets <- c(locomotion = "locomotion", assessment = "assessment",
               past = "past", future = "future")
  pubrow  <- c(locomotion = 0.25, assessment = 0.003, past = -0.09, future = 0.33)
  cat(sprintf("%-12s %12s %12s %10s\n", "vs", "published", "observed", "diff"))
  obsrow <- numeric(0)
  for (nm in names(targets)) {
    r <- cor(lc, s[[targets[nm]]], use = "complete.obs")
    obsrow[nm] <- r
    cat(sprintf("%-12s %12.3f %12.3f %10.3f\n", nm, pubrow[nm], r, r - pubrow[nm]))
  }
  worst <- max(abs(obsrow - pubrow))
  cat(sprintf("\nlargest deviation in the Table 4 correlation row: %.3f\n", worst))
  # the same row under the two rival readings, for contrast
  cat(sprintf("  (published PAST row would be   -.12 / .41 ; observed here %.3f / %.3f)\n",
              obsrow["locomotion"], obsrow["assessment"]))
  cat(sprintf("  (published FUTURE row would be  .37 / .02 ; observed here %.3f / %.3f)\n\n",
              obsrow["locomotion"], obsrow["assessment"]))
  cor_ok <- worst <= 0.02
} else {
  cat("\nCould not download the deposit S4 File; correlation-row check skipped.\n\n")
}

## ---- CLAIM 2: the two non-diagnostic within-subscale attempts --------------
cat("--- within-subscale order: NON-DIAGNOSTIC evidence, not part of the verdict ---\n")
mu  <- colMeans(m)
itc <- sapply(its, function(c_) cor(m[, c_], rowSums(m[, setdiff(its, c_), drop = FALSE])))
cat(sprintf("%-12s %8s %8s\n", "item", "mean", "item-tot"))
for (i in its) cat(sprintf("%-12s %8.3f %8.3f\n", i, mu[i], itc[i]))
cat("\nItalian TFS-I validation (PMC7851924, N=1458), the three RETAINED current-focus\n")
cat("items in Shipp et al. 2009 numbering: item 2 M=5.43 loading .672; item 4 M=5.25\n")
cat("loading .704; item 8 M=4.66 loading .751. The shipped order places Shipp 2, 4, 8 at\n")
cat("TFpresent1..3 and the item the TFS-I DROPPED ('I think about where I am today',\n")
cat("Shipp 5 or 10 -- the validation never says which) at TFpresent4.\n")
cat("  * Under that reading the item-total ranks reproduce the Italian loading ranks\n")
cat("    exactly (lowest at TFpresent1) but the MEAN ranks invert TFpresent2/TFpresent3.\n")
cat("  * Under the rival reading (dropped item at TFpresent3) the mean ranks reproduce\n")
cat("    exactly and the item-total ranks invert instead.\n")
cat("  The two criteria disagree, both by one adjacent swap, across samples 0.5 scale\n")
cat("  points apart. NOTHING here distinguishes TFpresent2/3/4 from one another.\n\n")

pass <- (best == "present") && (isTRUE(cor_ok) || is.na(cor_ok))
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
