# verify_gao2025_spiritual_wellbeing.R -- Step 5b, route 5 (subscale block structure).
#
# CLAIM UNDER TEST: the questionnaire's Section IV item numbering (1..12) maps onto
# the IRW codes SWB1..SWB12 in order. The instrument is the Spirituality Index of
# Well-Being (Daaleman & Frey 2004), whose PUBLISHED, fixed structure is:
#     items 1-6  = Self-Efficacy subscale
#     items 7-12 = Life Scheme subscale
# That is a falsifiable prediction about the live correlation matrix: an item's
# most-correlated partner should sit in its own block. A mapping that shuffled
# items across the two blocks would break it.
#
# It does NOT establish order WITHIN a block (a swap of, say, SWB3 and SWB5 is
# invisible here), so the recorded status is PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "gao2025_spiritual_wellbeing"
ITEMS <- paste0("SWB", 1:12)
SE <- 1:6; LS <- 7:12   # published SIWB subscale assignment

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
m <- as.matrix(w[, ITEMS]); storage.mode(m) <- "numeric"
C <- cor(m, use = "pairwise.complete.obs")

within <- c(C[SE, SE][upper.tri(C[SE, SE])], C[LS, LS][upper.tri(C[LS, LS])])
cross  <- as.vector(C[SE, LS])
cat(sprintf("within-block mean r = %.3f (n=%d pairs)\n", mean(within), length(within)))
cat(sprintf("cross-block  mean r = %.3f (n=%d pairs)\n", mean(cross),  length(cross)))

cat(sprintf("\n%-7s %-12s %6s %s\n", "item", "best partner", "r", "same block?"))
ok <- 0
for (i in seq_along(ITEMS)) {
    cc <- C[i, -i]
    nb <- names(which.max(cc))
    same <- (i <= 6) == (as.integer(sub("SWB", "", nb)) <= 6)
    ok <- ok + same
    cat(sprintf("%-7s %-12s %6.3f %s\n", ITEMS[i], nb, max(cc), ifelse(same, "yes", "NO")))
}
cat(sprintf("\nitems whose nearest neighbour is in their own SIWB subscale: %d / 12\n", ok))
cat("Does NOT establish: order within a subscale block, or the anchor direction\n",
    "(1=Strongly Disagree .. 5=Strongly Agree, taken verbatim from the deposit's\n",
    "Questionnaire.doc Section IV header).\n", sep = "")

cat(if (ok == 12 && mean(within) > mean(cross)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
