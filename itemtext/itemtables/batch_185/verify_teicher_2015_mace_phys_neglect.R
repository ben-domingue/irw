# verify_teicher_2015_mace_phys_neglect.R -- Step 5b check for batch_185.
#
# Claim: the five IRW item codes (S9 File column names, used verbatim by
# data/teicher_2015_mace_items.py) are MACE-X items 59, 60, 62, 63, 73 = MACE
# (52-item, S2 File) items 44, 45, 46, 47, 51, whose MACE-X wording ships as item_text.
#
# Route 1 (per-item descriptive statistics): Teicher & Parigger (2015) PLOS ONE
# Table 8 (doi:10.1371/journal.pone.0117423.t008, image) prints, per MACE item
# number + description, "% Yes" on n=1050, with items 44/45/51 marked "(reverse)"
# and shown AFTER reversal (so their % is % answering No). The five published
# values are all distinct (3.0, 2.3, 5.7, 3.7, 9.5). Each live item must match its
# own published value, under its own polarity, better than any other. resp stays
# RAW (1 = Yes) in the IRW table, which is why reversed items compare on resp == 0.
# A swap of any two items, or a reversed direction, breaks this.
# Hard-coded published values; fetches only the live IRW table (5 items, ~5.3k rows).

suppressMessages(library(irw))
TABLE <- "teicher_2015_mace_phys_neglect"

pub <- data.frame(
  item     = c("P_protect", "P_ER", "No_food", "Dirty_clothes", "Looked_out_each_other"),
  mace_no  = c(44, 45, 46, 47, 51),
  macex_no = c(59, 60, 62, 63, 73),
  label    = c("One or more family members there to take care of you and protect you (reverse)",
               "One or more would be there to take you to doctor or ER if needed (reverse)",
               "You did not have enough to eat",
               "You had to wear dirty clothes",
               "People in family looked out for each other (reverse)"),
  reversed = c(TRUE, TRUE, FALSE, FALSE, TRUE),
  pct_yes  = c(3.0, 2.3, 5.7, 3.7, 9.5),
  stringsAsFactors = FALSE)
TOL <- 0.3   # percentage points; published n=1050 vs live n 1050-1051; smallest rival gap ~0.7

d <- as.data.frame(irw::irw_fetch(TABLE))

live_pct <- function(it, rev) {
  x <- d$resp[d$item == it]
  100 * mean(if (rev) x == 0 else x == 1)
}

cat(sprintf("%-22s %-4s %-5s %-80s %6s %9s %9s %7s\n", "item", "MACE", "MACEX",
            "Table 8 label", "n", "published", "live", "diff"))
ok <- TRUE
for (i in seq_len(nrow(pub))) {
  n <- sum(d$item == pub$item[i])
  o <- live_pct(pub$item[i], pub$reversed[i])
  cat(sprintf("%-22s %-4d %-5d %-80s %6d %9.1f %9.2f %7.2f\n", pub$item[i], pub$mace_no[i],
              pub$macex_no[i], pub$label[i], n, pub$pct_yes[i], o, o - pub$pct_yes[i]))
  if (abs(o - pub$pct_yes[i]) > TOL) ok <- FALSE
}

# Discrimination: distance of each live item (row) to each published value (column),
# computed under the COLUMN's polarity. Argmin must be the diagonal.
M <- outer(seq_len(nrow(pub)), seq_len(nrow(pub)),
           Vectorize(function(i, j) abs(live_pct(pub$item[i], pub$reversed[j]) - pub$pct_yes[j])))
dimnames(M) <- list(pub$item, paste0("MACE", pub$mace_no))
cat("\nDistance matrix (pp), live item x published column:\n"); print(round(M, 2))
own <- apply(M, 1, which.min) == seq_len(nrow(pub))
gap <- sapply(seq_len(nrow(pub)), function(i) min(M[i, -i]) - M[i, i])
cat("argmin is own item:", paste(own, collapse = " "), "\n")
cat("margin to nearest rival column per item (pp):", paste(round(gap, 2), collapse = " "), "\n")
if (!all(own)) ok <- FALSE
# column-wise too: each published value must be nearest to its own live item
own_col <- apply(M, 2, which.min) == seq_len(nrow(pub))
cat("column argmin is own item:", paste(own_col, collapse = " "), "\n")
if (!all(own_col)) ok <- FALSE

# Polarity: under the opposite direction every item should miss by a wide margin.
flip <- sapply(seq_len(nrow(pub)), function(i) abs(live_pct(pub$item[i], !pub$reversed[i]) - pub$pct_yes[i]))
cat("\ndistance to published % under the OPPOSITE polarity (pp):", paste(round(flip, 1), collapse = " "), "\n")
if (any(flip <= TOL)) ok <- FALSE

# Informational only (not in verdict): raw storage predicts protective items correlate
# positively with each other and negatively with No_food / Dirty_clothes.
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
R <- cor(w[, pub$item], use = "pairwise.complete.obs")
cat("\nInter-item correlations (live, informational):\n"); print(round(R, 2))

cat("\nNot established by this script: the Yes/No option labels beyond direction (read from the\n",
    "MACE-X form's Yes/No boxes with subscript codes 1/0); Table 8 labels MACE items, so the\n",
    "MACE<->MACE-X item-number correspondence rests on identical S2/S3 wording (item 45/60 differs\n",
    "only by S2's trailing ', or would have if needed.') and the MACEscore index comments; and\n",
    "which of the two published P_ER wordings the online administration used.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
