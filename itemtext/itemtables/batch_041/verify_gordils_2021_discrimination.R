# verify_gordils_2021_discrimination.R
#
# CLAIM UNDER TEST: DISCRIM1..DISCRIM9 correspond, in order, to the nine
# Perceived Discrimination items printed in the paper's S1 Appendix
# (10.1371/journal.pone.0245671.s001):
#   1 less courtesy   2 less respect   3 poorer service   4 not smart
#   5 afraid of him/her   6 better than him/her   7 dishonest
#   8 called names or insulted   9 threatened or harassed
# The appendix lists the items but ties them to no code (mapping_basis=paper_order),
# so the mapping is an order inference and needs a falsifiable prediction.
#
# TWO PREDICTIONS, both about content, both broken by a permutation:
#  (A) Endorsement hierarchy (route 8). Overt-harassment events -- being called
#      names (8) and being threatened or harassed (9) -- are the least frequently
#      reported items of the Everyday Discrimination Scale in every published
#      administration; the interpersonal-disrespect items sit above them. So
#      items 8 and 9 must be the two lowest means, and item 9 (the most extreme
#      event) at or below item 8.
#  (B) Near-synonym adjacency (structural). The appendix order contains exactly
#      two pairs of near-synonymous items: (1 courtesy, 2 respect) and
#      (8 called names, 9 threatened/harassed). If the order is right, those two
#      pairs must be the two most strongly correlated pairs in the 36-pair
#      correlation matrix. A permutation that moved either member breaks this.
#
# WHAT THIS DOES NOT ESTABLISH: it cannot separate DISCRIM3/4/5 (poorer service /
# not smart / afraid) from one another -- their means sit within 0.10 and none of
# them is a near-synonym of another item -- and it cannot tell DISCRIM1 from
# DISCRIM2 (means 3.71 vs 3.70), only that the pair occupies positions 1-2.
# Hence the recorded status is PARTIAL, not VERIFIED.
#
# NOTE ON DISCRIM2: its Study-2 column was dropped by data/gordils_2021_interracial.py
# as a spreadsheet artifact, so it carries Study-1 rows only (n=847 vs ~2540).
# Prediction (B) is therefore also re-run on the Study-1-only subset, where every
# item has the same respondents.

suppressMessages(library(irw))
TABLE <- "gordils_2021_discrimination"
IT <- paste0("DISCRIM", 1:9)

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)

wide <- function(df) {
    w <- reshape(df[, c("id", "item", "resp")], idvar = "id",
                 timevar = "item", direction = "wide")
    names(w) <- sub("^resp\\.", "", names(w))
    w[, IT]
}

top_pairs <- function(cm, k = 4) {
    idx <- which(upper.tri(cm), arr.ind = TRUE)
    v <- data.frame(a = rownames(cm)[idx[, 1]], b = colnames(cm)[idx[, 2]],
                    r = cm[idx])
    head(v[order(-v$r), ], k)
}

## ---- (A) endorsement hierarchy -------------------------------------------
m <- tapply(d$resp, d$item, mean)[IT]
cat("--- (A) per-item means (1 = never ... 7 = frequently) ---\n")
for (i in IT) cat(sprintf("%-9s %.2f\n", i, m[i]))
lowest2 <- names(sort(m))[1:2]
cat("\ntwo lowest items:", paste(sort(lowest2), collapse = ", "),
    "| expected: DISCRIM8, DISCRIM9\n")
cat(sprintf("DISCRIM9 (%.2f) <= DISCRIM8 (%.2f): %s\n",
            m["DISCRIM9"], m["DISCRIM8"], m["DISCRIM9"] <= m["DISCRIM8"]))
okA <- setequal(lowest2, c("DISCRIM8", "DISCRIM9")) && m["DISCRIM9"] <= m["DISCRIM8"]

## ---- (B) near-synonym adjacency ------------------------------------------
run_B <- function(df, label) {
    cm <- cor(wide(df), use = "pairwise.complete.obs")
    tp <- top_pairs(cm)
    cat(sprintf("\n--- (B) strongest correlated pairs, %s ---\n", label))
    for (i in seq_len(nrow(tp)))
        cat(sprintf("%-9s %-9s r = %.3f\n", tp$a[i], tp$b[i], tp$r[i]))
    got <- paste(tp$a[1:2], tp$b[1:2])
    ok <- setequal(got, c("DISCRIM1 DISCRIM2", "DISCRIM8 DISCRIM9"))
    cat("top two pairs are the two expected near-synonym pairs:", ok, "\n")
    ok
}
okB1 <- run_B(d, "all rows")
okB2 <- run_B(d[d$id < 1e5, ], "Study 1 only (complete on all 9 items)")

cat("\nNot established by either route: the order of DISCRIM3/4/5 among",
    "themselves,\nand DISCRIM1 vs DISCRIM2 within their pair. Status recorded",
    "as PARTIAL.\n")
cat(if (okA && okB1 && okB2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
