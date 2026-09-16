# verify_wang_2016_study1_power.R
#
# CLAIM UNDER TEST (Step 5b), in two parts:
#   (a) SCALE IDENTITY + CODING DIRECTION: power1..power8 are the eight items of
#       the Sense of Power Scale (Anderson, John & Keltner, 2012) AS THE STUDY
#       SCORED THEM -- i.e. stored on an ascending 1..5 coding in which the four
#       canonically reverse-worded items (numbers 2, 4, 6, 7) are ALREADY
#       REVERSE-SCORED.  That is what the shipped option_text asserts: the four
#       forward items carry 1 = "strongly disagree" / 5 = "strongly agree", the
#       four reverse-worded ones carry the anchors flipped (1 = "strongly agree").
#   (b) WITHIN-SCALE ORDER: which canonical item (1..8) each code is.  This script
#       CANNOT test (b) and says so below -- hence status PARTIAL.
#
# Falsifiable predictions for (a), all from Wang YN (2016) PLOS ONE 11(1):e0146050:
#   * per-person sum of the 8 live items = Table 1 Power M 27.71, SD 3.78;
#   * its correlation with the live self-esteem total (wang_2016_study1_se,
#     M 38.34, SD 5.08) = Table 1's .61;
#   * Cronbach's alpha of the 8 stored items = the Measures section's .71.
# Counterfactual that would falsify it: if the reverse-worded items were stored
# RAW rather than reverse-scored, alpha collapses (a scale mixing two keying
# directions cannot be internally consistent) and the total drops by ~5.7 points.

suppressMessages(library(irw))

PUB <- list(m = 27.71, sd = 3.78, se_m = 38.34, se_sd = 5.08, r = 0.61, alpha = 0.71)
TOL_M <- 0.05; TOL_SD <- 0.05; TOL_R <- 0.02; TOL_A <- 0.02

wide <- function(tab) {
    x <- irw::irw_fetch(tab)
    d <- data.frame(id = as.character(x$id), item = as.character(x$item),
                    resp = as.numeric(x$resp))
    d <- d[!is.na(d$resp), ]
    w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
    rownames(w) <- w$id; w$id <- NULL
    colnames(w) <- sub("^resp\\.", "", colnames(w))
    w[complete.cases(w), , drop = FALSE]
}

alpha <- function(m) {
    m <- as.matrix(m); k <- ncol(m)
    k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))
}

pw <- wide("wang_2016_study1_power")
pw <- pw[, paste0("power", 1:8), drop = FALSE]
se <- rowSums(wide("wang_2016_study1_se"))
tot <- rowSums(pw)
common <- intersect(names(tot), names(se))

cat(sprintf("n persons with all 8 power items: %d ; with self-esteem too: %d\n\n",
            nrow(pw), length(common)))

row <- function(lab, pub, obs) cat(sprintf("%-34s %10.3f %10.3f %9.3f\n", lab, pub, obs, obs - pub))
cat(sprintf("%-34s %10s %10s %9s\n", "quantity", "published", "observed", "diff"))
row("Power total M",            PUB$m,     mean(tot))
row("Power total SD",           PUB$sd,    sd(tot))
row("Self-esteem total M",      PUB$se_m,  mean(se))
row("Self-esteem total SD",     PUB$se_sd, sd(se))
row("r(power, self-esteem)",    PUB$r,     cor(tot[common], se[common]))
row("Cronbach's alpha (stored)", PUB$alpha, alpha(pw))

# Counterfactual: the same 8 items with the canonical reverse set 2,4,6,7 put
# back on the raw (un-reversed) coding the shipped anchors rule out.
raw <- pw; rv <- paste0("power", c(2, 4, 6, 7)); raw[, rv] <- 6 - raw[, rv]
cat(sprintf("\nCOUNTERFACTUAL (items 2,4,6,7 stored RAW, i.e. not reverse-scored):\n"))
cat(sprintf("  alpha %.3f (vs published .71), total M %.2f (vs published 27.71)\n",
            alpha(raw), mean(rowSums(raw))))

# What this does NOT establish -- the within-scale order.  If the reverse-worded
# items really sit at positions 2,4,6,7 they should share a wording method factor,
# so print how the canonical split ranks among all 35 4/4 splits of the items by
# within-minus-between mean correlation.  It does not single the canonical one out.
C <- cor(pw)
sp <- combn(8, 4, simplify = FALSE)
gap <- sapply(sp, function(s) {
    o <- setdiff(1:8, s)
    mean(c(C[s, s][upper.tri(diag(4))], C[o, o][upper.tri(diag(4))])) - mean(C[s, o])
})
ord <- order(gap, decreasing = TRUE)
can <- which(sapply(sp, function(s) identical(s, c(2L, 4L, 6L, 7L))))
cat(sprintf("\nReverse-wording method-factor split: canonical {2,4,6,7} ranks %d of %d 4-subsets (gap %.3f; best %.3f for {%s})\n",
            which(ord == can), length(sp), gap[can], gap[ord[1]],
            paste(sp[[ord[1]]], collapse = ",")))
cat("=> the data do NOT distinguish which code is which canonical item; part (b) is untested (PARTIAL).\n\n")

ok <- abs(mean(tot) - PUB$m)  <= TOL_M  && abs(sd(tot) - PUB$sd)  <= TOL_SD &&
      abs(mean(se)  - PUB$se_m) <= TOL_M && abs(sd(se)  - PUB$se_sd) <= TOL_SD &&
      abs(cor(tot[common], se[common]) - PUB$r) <= TOL_R &&
      abs(alpha(pw) - PUB$alpha) <= TOL_A && alpha(raw) < 0.3

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
