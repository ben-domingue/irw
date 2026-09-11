# verify_teicher_2015_mace_emot_neglect.R -- Step 5b check for batch_184.
#
# Claim: the five IRW item codes (S9 File column names, used verbatim by
# data/teicher_2015_mace_items.py) are MACE-X items 51, 52, 57, 58, 75 = MACE
# (52-item) items 38, 39, 42, 43, 52, whose wording ships as item_text.
#
# Route 1 (per-item descriptive statistics): Teicher & Parigger (2015) PLOS ONE
# Table 2 (doi:10.1371/journal.pone.0117423.t002, image) prints, per MACE item
# number + description, "% Yes" on n=1045, with items 42/43/52 shown AFTER
# reversal (so their % is % answering No). The five published values are all
# distinct (22.0, 30.7, 2.2, 4.4, 10.8), so each live item must match its own
# published value and no other. It also checks polarity: resp stays RAW
# (1 = Yes) in the IRW table, which is why the reversed items are compared on
# resp == 0. A swap of any two items, or a reversed direction, breaks this.
# Hard-coded published values; fetches only the live IRW table.

suppressMessages(library(irw))
TABLE <- "teicher_2015_mace_emot_neglect"

pub <- data.frame(
  item      = c("M_unavail_poor", "F_unavail_poor", "P_loved_you", "P_special", "Fam_strength"),
  mace_no   = c(38, 39, 42, 43, 52),
  label     = c("Mother unavailable poor reasons", "Father unavailable poor reasons",
                "Family member made you feel loved (reversed)",
                "Family member helped you feel special/important (reversed)",
                "Family was source of strength and support (reversed)"),
  reversed  = c(FALSE, FALSE, TRUE, TRUE, TRUE),
  pct_yes   = c(22.0, 30.7, 2.2, 4.4, 10.8),
  stringsAsFactors = FALSE)
TOL <- 0.6   # percentage points; published n=1045 vs live n up to 1051

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)

# live "% Yes" in the published sense, for every live item under both polarities
live_pct <- function(it, rev) {
  x <- d$resp[d$item == it]
  100 * mean(if (rev) x == 0 else x == 1)
}
cat(sprintf("%-16s %-4s %-58s %6s %9s %9s %7s\n", "item", "MACE", "Table 2 label",
            "n", "published", "live", "diff"))
ok <- TRUE
obs <- numeric(nrow(pub))
for (i in seq_len(nrow(pub))) {
  n <- sum(d$item == pub$item[i])
  obs[i] <- live_pct(pub$item[i], pub$reversed[i])
  cat(sprintf("%-16s %-4d %-58s %6d %9.1f %9.2f %7.2f\n", pub$item[i], pub$mace_no[i],
              pub$label[i], n, pub$pct_yes[i], obs[i], obs[i] - pub$pct_yes[i]))
  if (abs(obs[i] - pub$pct_yes[i]) > TOL) ok <- FALSE
}

# Discrimination: for every live item, the nearest published value (under that
# row's polarity) must be its own, with every other published value further away.
cat("\nNearest published value per live item (distance matrix, pp):\n")
M <- outer(seq_len(nrow(pub)), seq_len(nrow(pub)),
           Vectorize(function(i, j) abs(live_pct(pub$item[i], pub$reversed[j]) - pub$pct_yes[j])))
dimnames(M) <- list(pub$item, paste0("MACE", pub$mace_no))
print(round(M, 2))
own <- apply(M, 1, which.min) == seq_len(nrow(pub))
gap <- sapply(seq_len(nrow(pub)), function(i) min(M[i, -i]) - M[i, i])
cat("argmin is own item:", paste(own, collapse = " "), "\n")
cat("smallest margin to a rival column (pp):", round(min(gap), 2), "\n")
if (!all(own)) ok <- FALSE

# Correlations: raw storage predicts the positively-worded items correlate negatively
# with the 'unavailable' items and positively with each other.
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
R <- cor(w[, pub$item], use = "pairwise.complete.obs")
cat("\nInter-item correlations (live):\n"); print(round(R, 2))
neg_block <- R[c("M_unavail_poor", "F_unavail_poor"), c("P_loved_you", "P_special", "Fam_strength")]
pos_block <- R[c("P_loved_you", "P_special", "Fam_strength"), c("P_loved_you", "P_special", "Fam_strength")]
cat("unavailable x positive-worded (expect < 0):", paste(round(neg_block, 2), collapse = " "), "\n")
cat("positive-worded among themselves (expect > 0):",
    paste(round(pos_block[upper.tri(pos_block)], 2), collapse = " "), "\n")
# Informational only, NOT part of the verdict: P_loved_you is endorsed by 97.8%, so its
# correlations are range-restricted (observed ~0.00/+0.01 with the unavailable items).
# Direction is decided instead by the flipped-polarity comparison below.
flip <- sapply(seq_len(nrow(pub)), function(i) abs(live_pct(pub$item[i], !pub$reversed[i]) - pub$pct_yes[i]))
cat("distance to published % under the OPPOSITE polarity (pp):", paste(round(flip, 1), collapse = " "), "\n")
if (any(flip <= TOL)) ok <- FALSE

cat("\nNot established by this script: the Yes/No wording of options is read from the\n",
    "MACE-X form (subscript scoring codes Yes=1, No=0), not tested beyond polarity; and\n",
    "Table 2 describes MACE items, so the MACE-X<->MACE item-number correspondence rests on\n",
    "identical wording in S2 vs S3 File and the authors' MACEscore index comments.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
