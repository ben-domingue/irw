# verify_duboz_2021_swls.R
#
# This table is BLOCKED on rights, so NO item text was shipped and there is no
# item_text<->item mapping in the corpus to verify. The instrument is the 5-item
# Satisfaction With Life Scale (Diener, Emmons, Larsen & Griffin, 1985). The source
# study's CC BY deposit publishes no wording, so the wording could only come from the
# rights holder's own distribution, which states:
#   "The use of these scales is permitted for non-commercial purposes only."
#   -- eddiener.com/scales, "Permissions to use scales" (retrieved 2026-09-04)
# That fires the itemtext_standard.md 2026-09-04 non-commercial ruling (irw#1891).
#
# What this script re-runs is the evidence recorded in
# verification_duboz_2021_swls.csv, so that an unblock (a ruling that the clause does
# not fire) needs no further investigation. It is ROUTE 3 -- published totals -- run
# against Duboz et al. 2021 PLOS ONE 16(5):e0252134:
#
#   published: Dakar     mean 21.427, SD 5.918 (N = 1000)
#              Tessekere mean 23.220, SD 5.743 (N =  500)
#              t = -5.585 ; Cronbach alpha (whole sample) = 0.725
#
# The live table is the same data with the 7 exact duplicate rows removed by
# data/duboz_2021_swls_pss.py (993 + 500 = 1493 respondents), so Dakar's figures are
# expected to move in the third decimal and Tessekere's not at all.
#
# WHAT THIS VERIFIES: that the five live items ARE the SWLS, scored raw with no
# reverse-coding, and that resp runs 1 = strongly disagree .. 7 = strongly agree
# (a flipped assignment gives 40 - 21.43 = 18.57 for Dakar, off by 2.86 points).
# WHAT IT DOES NOT VERIFY: a sum is invariant to permuting the five items, so it says
# nothing about which canonical SWLS item is Q1..Q5. No route in the paper does -- it
# publishes no per-item statistics. Hence the item-order mapping would have been
# PARTIAL, never VERIFIED. The item-total profile printed at the end is a contrary
# signal on that point, recorded deliberately rather than suppressed.
#
# irw_fetch() is used deliberately: per-respondent sums are needed and
# irw_table_sets() does not supply them. The table is 7,465 rows.

suppressMessages({library(irw)})

TABLE <- "duboz_2021_swls"
PUB <- list(dakar = c(mean = 21.427, sd = 5.918),
            tesse = c(mean = 23.220, sd = 5.743),
            t     = -5.585,
            alpha = 0.725)

d <- as.data.frame(irw::irw_fetch(TABLE))
items <- sort(unique(d$item))
cat("live items (", length(items), "):\n  ", paste(items, collapse = "\n  "), "\n\n", sep = "")

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
loc <- d[!duplicated(d$id), c("id", "cov_location")]
w <- merge(w, loc, by = "id")
M <- as.matrix(w[, items])
w$tot <- rowSums(M)

cat(sprintf("%-10s %5s %10s %10s %10s %10s\n",
            "group", "n", "live mean", "pub mean", "live SD", "pub SD"))
res <- list()
for (g in c("Dakar", "Tessekere")) {
    k  <- if (g == "Dakar") "dakar" else "tesse"
    tt <- w$tot[w$cov_location == g]
    res[[k]] <- c(mean = mean(tt), sd = sd(tt))
    cat(sprintf("%-10s %5d %10.3f %10.3f %10.3f %10.3f\n",
                g, length(tt), mean(tt), PUB[[k]]["mean"], sd(tt), PUB[[k]]["sd"]))
}
tstat <- unname(t.test(tot ~ cov_location, data = w)$statistic)
k     <- length(items)
alpha <- (k / (k - 1)) * (1 - sum(apply(M, 2, var)) / var(w$tot))
cat(sprintf("\nt statistic : live %8.3f   published %8.3f\n", tstat, PUB$t))
cat(sprintf("Cronbach a  : live %8.4f   published %8.3f\n", alpha, PUB$alpha))

# Direction control: the reversed 1-7 coding must miss the published means badly.
rev_dakar <- mean(rowSums(8 - M[w$cov_location == "Dakar", , drop = FALSE]))
cat(sprintf("\ndirection control: reversed coding gives Dakar mean %.3f vs published %.3f (gap %.3f)\n",
            rev_dakar, PUB$dakar["mean"], abs(rev_dakar - PUB$dakar["mean"])))

cat("\ncorrected item-total correlations (NOT part of the verdict -- recorded because\n",
    "they do NOT corroborate the canonical Qn = SWLS item n order; the SWLS literature's\n",
    "weakest item is item 5, whereas the weakest here is Q1):\n", sep = "")
for (i in items)
    cat(sprintf("  %-35s %.3f\n", i, cor(w[[i]], w$tot - w[[i]])))

ok <- abs(res$dakar["mean"] - PUB$dakar["mean"]) < 0.05 &&
      abs(res$dakar["sd"]   - PUB$dakar["sd"])   < 0.05 &&
      abs(res$tesse["mean"] - PUB$tesse["mean"]) < 0.05 &&
      abs(res$tesse["sd"]   - PUB$tesse["sd"])   < 0.05 &&
      abs(tstat - PUB$t) < 0.05 &&
      abs(alpha - PUB$alpha) < 0.005 &&
      abs(rev_dakar - PUB$dakar["mean"]) > 1

cat("\nNote: PASS here means the five live items reproduce the paper's published SWLS\n",
    "totals, so they are the SWLS, stored raw, on a 1 = strongly disagree .. 7 = strongly\n",
    "agree coding. It says NOTHING about any shipped wording -- none was shipped -- and\n",
    "nothing about which SWLS item is Q1..Q5. The block is on the rights clause, not the\n",
    "mapping.\n", sep = "")
cat(if (isTRUE(unname(ok))) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
