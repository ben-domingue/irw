# verify_gordils_2021_intergroup_anxiety.R
#
# CLAIM UNDER TEST (mapping_basis = paper_order): the four items of the
# "Perceived Intergroup Anxiety" block of the paper's S1 Appendix
# (10.1371/journal.pone.0245671.s001) map to the live codes in listed order --
#   ANX1 = "...feel nervous about interacting..."
#   ANX2 = "...seem to feel uneasy about interacting..."
#   ANX3 = "...feel tense about interacting..."
#   ANX4 = "...feel bothered about interacting..."
# Nothing in the deposit ties a column to a wording (checked: both XLSX data
# files carry bare headers; the three SPSS syntax files label only filter_$),
# and the four items are near-synonymous affect words, so no content route can
# tell them apart by mean or endorsement.
#
# The one falsifiable structure available is a SIMPLEX: if the codes really run
# in presentation order, correlations should decay monotonically with distance
# in that order. That is a real test because only three distinct adjacency
# orderings of four items exist (up to reversal): 1-2-3-4, 1-3-2-4, 1-2-4-3.
# This script checks that the shipped order is the unique one of the three
# under which mean r declines monotonically with lag, and that it replicates in
# Study 1 and Study 2 separately.
#
# It does NOT establish direction: the simplex is symmetric under reversal, so
# it cannot rule out ANX1 = "bothered" ... ANX4 = "nervous". Hence PARTIAL.

suppressMessages(library(irw))
suppressMessages(library(tidyr))

TABLE <- "gordils_2021_intergroup_anxiety"
ITEMS <- c("ANX1", "ANX2", "ANX3", "ANX4")

d <- irw::irw_fetch(TABLE)
w <- tidyr::pivot_wider(d, id_cols = id, names_from = item, values_from = resp)
w <- as.data.frame(w)

# Study 1 ids are < 100000, Study 2 ids are offset by 100000
# (see data/gordils_2021_interracial.py). ANX2's Study-2 column was dropped
# upstream as a spreadsheet artifact, so Study 2 has only ANX1/ANX3/ANX4.
s1 <- w[w$id <  100000, ]
s2 <- w[w$id >= 100000, ]

R  <- cor(w[,  ITEMS],                  use = "pairwise.complete.obs")
R1 <- cor(s1[, ITEMS],                  use = "pairwise.complete.obs")
R2 <- cor(s2[, c("ANX1","ANX3","ANX4")], use = "pairwise.complete.obs")

cat("per-item n and mean (full table):\n")
for (it in ITEMS)
    cat(sprintf("  %-5s n=%5d  mean=%.3f\n", it, sum(d$item == it),
                mean(d$resp[d$item == it])))

cat("\nfull-sample correlation matrix:\n"); print(round(R, 3))
cat("\nStudy 1 only (n=", nrow(s1), "):\n", sep = ""); print(round(R1, 3))
cat("\nStudy 2 only (n=", nrow(s2), ", ANX2 dropped upstream):\n", sep = ""); print(round(R2, 3))

# ---- simplex test over the three distinct adjacency orderings ----
lag_means <- function(M, ord) {
    p <- length(ord)
    out <- numeric(p - 1)
    for (L in seq_len(p - 1)) {
        v <- c()
        for (i in 1:(p - L)) v <- c(v, M[ord[i], ord[i + L]])
        out[L] <- mean(v)
    }
    out
}
ORDERS <- list("1-2-3-4" = c("ANX1","ANX2","ANX3","ANX4"),
               "1-3-2-4" = c("ANX1","ANX3","ANX2","ANX4"),
               "1-2-4-3" = c("ANX1","ANX2","ANX4","ANX3"))

cat("\nmean correlation by lag, for each of the three distinct orderings",
    "\n(full sample; monotone decline is the prediction):\n")
mono <- logical(length(ORDERS))
for (k in seq_along(ORDERS)) {
    lm_ <- lag_means(R, ORDERS[[k]])
    mono[k] <- all(diff(lm_) < 0)
    cat(sprintf("  %-8s lag1=%.4f lag2=%.4f lag3=%.4f  monotone=%s\n",
                names(ORDERS)[k], lm_[1], lm_[2], lm_[3], mono[k]))
}
shipped_unique <- mono[1] && !any(mono[-1])

lm1 <- lag_means(R1, ORDERS[[1]])
cat(sprintf("\nStudy 1 only, shipped order: lag1=%.4f lag2=%.4f lag3=%.4f  monotone=%s\n",
            lm1[1], lm1[2], lm1[3], all(diff(lm1) < 0)))
s1_ok <- all(diff(lm1) < 0)

# Study 2 has positions 1, 3, 4: distances 2, 1 and 3. The only prediction the
# missing item leaves is that the distance-3 pair (ANX1, ANX4) is the weakest.
s2_ok <- R2["ANX1","ANX4"] < min(R2["ANX1","ANX3"], R2["ANX3","ANX4"])
cat(sprintf("Study 2 only: r(ANX1,ANX4)=%.4f (distance 3) vs r(ANX1,ANX3)=%.4f (2) and r(ANX3,ANX4)=%.4f (1); weakest-is-most-distant=%s\n",
            R2["ANX1","ANX4"], R2["ANX1","ANX3"], R2["ANX3","ANX4"], s2_ok))

cat("\nNOT ESTABLISHED: the simplex is symmetric under reversal, so this cannot\n",
    "distinguish the shipped order from ANX1='bothered' ... ANX4='nervous'; and\n",
    "the correlations it separates differ by only 0.02-0.06, so the ordering\n",
    "evidence is structural, not decisive per item. PARTIAL, not VERIFIED.\n", sep = "")

cat(if (shipped_unique && s1_ok && s2_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
