# verify_zhang_2024_expertise.R -- Step 5b check for zhang_2024_expertise (batch_411).
#
# Claim: live codes EXP1..EXP3 are the S1 Dataset columns the paper's Table 2 labels
# EXP1..EXP3, and those are S1 Appendix Expertise items 1..3 in order.
#
# Route: the paper publishes per-item CFA factor loadings (Table 2: EXP1 0.806,
# EXP2 0.730, EXP3 0.733) and alpha 0.800. For a single 3-indicator factor the
# standardized loadings are identified from the correlations alone:
#   l1 = sqrt(r12*r13/r23), l2 = sqrt(r12*r23/r13), l3 = sqrt(r13*r23/r12).
# The paper's loadings come from a 6-factor CFA, so expect small residuals.
#
# What this does NOT establish: which Appendix sentence goes with which code.
# The loadings tie live codes to the paper's own code labels (EXP1 distinctly
# highest), but the paper never prints text beside a code; the text->code link rests
# on the Appendix listing Expertise items numbered 1-3, read as EXP1-EXP3. The three
# items are near-synonymous, so no statistic in this source can separate them.

suppressMessages(library(irw))
TABLE <- "zhang_2024_expertise"
PUB_LOAD <- c(EXP1 = 0.806, EXP2 = 0.730, EXP3 = 0.733)
PUB_ALPHA <- 0.800
TOL <- 0.05

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
x <- w[, c("EXP1", "EXP2", "EXP3")]
r <- cor(x, use = "pairwise.complete.obs")
r12 <- r[1, 2]; r13 <- r[1, 3]; r23 <- r[2, 3]
obs <- c(EXP1 = sqrt(r12 * r13 / r23), EXP2 = sqrt(r12 * r23 / r13),
         EXP3 = sqrt(r13 * r23 / r12))
k <- 3; alpha <- k / (k - 1) * (1 - sum(apply(x, 2, var)) / var(rowSums(x)))

cat(sprintf("n respondents: %d\n", nrow(x)))
cat(sprintf("r12=%.3f r13=%.3f r23=%.3f\n", r12, r13, r23))
cat(sprintf("%-6s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (i in names(obs))
  cat(sprintf("%-6s %10.3f %10.3f %8.3f\n", i, PUB_LOAD[i], obs[i], obs[i] - PUB_LOAD[i]))
cat(sprintf("alpha  %10.3f %10.3f %8.3f\n", PUB_ALPHA, alpha, alpha - PUB_ALPHA))

worst <- max(abs(obs - PUB_LOAD))
# Ordering check: paper has EXP1 as the clearly highest loading.
top_ok <- names(which.max(obs)) == "EXP1"
cat(sprintf("largest loading deviation: %.3f (tol %.2f); EXP1 highest: %s\n", worst, TOL, top_ok))
cat("Note: pins live codes to the paper's code labels only; text->code rests on Appendix order (PARTIAL).\n")
cat(if (worst <= TOL && top_ok && abs(alpha - PUB_ALPHA) <= 0.01) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
