# Step 5b verification for han_2015_peer_assisted_learning.
#
# Claim under test: item codes B_1..B_12 carry the 12 upper-limb learning-objective
# statements in the order printed in the S1 Text questionnaire (Section B, items 1-12)
# and in Table 2 of Han, Chung & Nam (2015), PLOS ONE 10.1371/journal.pone.0142988.
#
# Falsifiable prediction: Table 2 publishes, per item, mean+-SD separately for the
# experimental (peer-assisted) and control (faculty-led) groups plus a Mann-Whitney
# p-value. The live table keeps cov_group, so all 24 means, 24 SDs and 12 p-values are
# recomputable. Any permutation of item_text across items breaks the match.

suppressMessages(library(irw))

TABLE <- "han_2015_peer_assisted_learning"
ITEMS <- paste0("B_", 1:12)

# Published values, paper Table 2, rows 1-12 in printed order.
PUB_EXP_M  <- c(3.63, 3.64, 3.75, 3.99, 3.51, 4.10, 3.16, 3.99, 3.96, 3.75, 3.69, 3.61)
PUB_EXP_SD <- c(0.70, 0.64, 0.74, 0.74, 0.73, 0.83, 0.86, 0.75, 0.73, 0.80, 0.91, 0.81)
PUB_CTL_M  <- c(3.21, 3.29, 3.33, 3.08, 3.10, 3.17, 2.77, 3.23, 3.57, 3.44, 3.25, 3.48)
PUB_CTL_SD <- c(0.74, 0.75, 0.70, 0.92, 0.84, 0.93, 0.97, 0.90, 0.82, 0.86, 0.72, 0.82)
PUB_P      <- c(0.000, 0.002, 0.000, 0.000, 0.001, 0.000, 0.018, 0.000, 0.001, 0.022, 0.001, 0.274)
TOL_M <- 0.011   # published to 2dp
TOL_SD <- 0.011

d <- irw::irw_fetch(TABLE)

cat(sprintf("%-5s %18s %18s %16s\n", "item", "exp M+-SD (pub/obs)", "ctl M+-SD (pub/obs)", "p (pub/obs)"))
worst_m <- 0; worst_sd <- 0; p_ok <- TRUE
for (k in seq_along(ITEMS)) {
    s  <- d[d$item == ITEMS[k], ]
    e  <- s$resp[s$cov_group == "Experimental group"]
    cg <- s$resp[s$cov_group == "Control group"]
    om <- mean(e); osd <- sd(e); cm <- mean(cg); csd <- sd(cg)
    op <- suppressWarnings(wilcox.test(e, cg)$p.value)
    cat(sprintf("%-5s  %.2f/%.2f %.2f/%.2f   %.2f/%.2f %.2f/%.2f   %.3f/%.3f\n",
                ITEMS[k], PUB_EXP_M[k], om, PUB_EXP_SD[k], osd,
                PUB_CTL_M[k], cm, PUB_CTL_SD[k], csd, PUB_P[k], op))
    worst_m  <- max(worst_m,  abs(om - PUB_EXP_M[k]),  abs(cm - PUB_CTL_M[k]))
    worst_sd <- max(worst_sd, abs(osd - PUB_EXP_SD[k]), abs(csd - PUB_CTL_SD[k]))
    # p agreement: published rounds to 3dp, and the sole non-significant row must be item 12
    if (PUB_P[k] >= 0.05 && op < 0.05) p_ok <- FALSE
    if (PUB_P[k] < 0.05 && op >= 0.05) p_ok <- FALSE
}

cat(sprintf("\nlargest mean deviation: %.3f (tol %.3f)\n", worst_m, TOL_M))
cat(sprintf("largest SD deviation:   %.3f (tol %.3f)\n", worst_sd, TOL_SD))
cat(sprintf("significance pattern reproduces: %s\n", p_ok))

# Uniqueness: the (exp mean, ctl mean) pair must be distinct for every item, otherwise
# the route could not separate the tied items from each other.
pairs <- paste(PUB_EXP_M, PUB_CTL_M)
cat(sprintf("distinct published (exp,ctl) mean pairs: %d of 12\n", length(unique(pairs))))

cat("Note: this route pins every item individually -- B_3/B_10 tie on the experimental\n",
    "mean (3.75) and B_4/B_8 on 3.99, but each pair separates on the control mean\n",
    "(3.33 vs 3.44; 3.08 vs 3.23). It does NOT independently verify the option_text\n",
    "anchors (Not at all..Very much), which come from the questionnaire's own column\n",
    "headers over the printed codes 1-5.\n", sep = "")

ok <- worst_m <= TOL_M && worst_sd <= TOL_SD && p_ok && length(unique(pairs)) == 12
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
