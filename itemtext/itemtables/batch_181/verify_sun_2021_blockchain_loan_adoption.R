# verify_sun_2021_blockchain_loan_adoption.R -- Step 5b mapping check (batch_181)
#
# Claim: the code prefixes pr/rs/pf/com/ui denote the constructs the item text
# assigns them to (Perceived risk, Reward sensitivity, Perceived fairness,
# Complexity, Usage intention; Sun et al. 2021 PLOS ONE 10.1371/journal.pone.0245964),
# and within each construct code suffix 1/2/3 = the paper's / S1 Appendix's item 1/2/3.
#
# Falsifiable predictions, hard-coded from the paper:
#   * Table 2 Cronbach's alpha per NAMED construct (all five values distinct).
#   * Table 3 HTMT for all 10 pairs of first-order constructs (named).
# A relabelling of any two construct blocks permutes these numbers and fails.
#
# NOT established: order WITHIN a construct. All three items of a construct
# share polarity and have near-identical means (e.g. pr 5.01/5.06/5.08), and
# the published Table 2 outer loadings (0.87-0.96) do not reproduce from the
# data (item-composite r 0.95-0.99), so nothing distinguishes pr1 from pr2 from
# pr3 except the paper's numbering. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "sun_2021_blockchain_loan_adoption"
TOL <- 0.0015  # published to 3 dp

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

groups <- list(PR = c("pr1","pr2","pr3"), RS = c("rs1","rs2","rs3"),
               PF = c("pf1","pf2","pf3"), COM = c("com1","com2","com3"),
               UI = c("ui1","ui2","ui3"))

alpha <- function(x) { x <- na.omit(x); k <- ncol(x)
  k / (k - 1) * (1 - sum(apply(x, 2, var)) / var(rowSums(x))) }

PUB_ALPHA <- c(PR = 0.968, RS = 0.954, PF = 0.956, COM = 0.986, UI = 0.980)
cat("Cronbach's alpha, paper Table 2 vs live data\n")
cat(sprintf("%-4s %9s %9s %8s\n", "cons", "published", "observed", "diff"))
dev <- c()
for (g in names(groups)) {
  a <- alpha(w[, groups[[g]]])
  dev <- c(dev, abs(a - PUB_ALPHA[g]))
  cat(sprintf("%-4s %9.3f %9.4f %8.4f\n", g, PUB_ALPHA[g], a, a - PUB_ALPHA[g]))
}

R <- abs(cor(w[, unlist(groups)], use = "pairwise.complete.obs"))
mono <- function(G) { m <- R[G, G]; mean(m[upper.tri(m)]) }
htmt <- function(a, b) mean(R[groups[[a]], groups[[b]]]) /
  sqrt(mono(groups[[a]]) * mono(groups[[b]]))

PUB_HTMT <- list(c("PF","COM",0.096), c("PR","COM",0.025), c("RS","COM",0.161),
                 c("UI","COM",0.321), c("PR","PF",0.297), c("RS","PF",0.415),
                 c("UI","PF",0.236), c("RS","PR",0.079), c("UI","PR",0.119),
                 c("UI","RS",0.350))
cat("\nHTMT, paper Table 3 vs live data\n")
cat(sprintf("%-8s %9s %9s %8s\n", "pair", "published", "observed", "diff"))
for (p in PUB_HTMT) {
  h <- htmt(p[1], p[2]); pub <- as.numeric(p[3])
  dev <- c(dev, abs(h - pub))
  cat(sprintf("%-8s %9.3f %9.4f %8.4f\n", paste(p[1], p[2], sep = "-"), pub, h, h - pub))
}

# Discrimination check: would the nearest-alpha swap (RS<->PF) be caught?
cat("\nSwap test: relabel RS<->PF blocks -> alpha diffs",
    sprintf("%.4f / %.4f", alpha(w[, groups$PF]) - PUB_ALPHA["RS"],
            alpha(w[, groups$RS]) - PUB_ALPHA["PF"]),
    "; HTMT RS-COM would read", sprintf("%.3f", htmt("PF","COM")), "vs published 0.161\n")

cat("\nNot used for verdict -- Table 2 outer loadings vs item-composite r (within-construct order):\n")
PUB_LOAD <- c(pr1=.901, pr2=.887, pr3=.865, rs1=.958, rs2=.956, rs3=.951,
              pf1=.935, pf2=.950, pf3=.946, com1=.960, com2=.964, com3=.962,
              ui1=.946, ui2=.935, ui3=.952)
for (g in names(groups)) for (it in groups[[g]])
  cat(sprintf("  %-5s published %.3f  item-composite r %.3f\n", it, PUB_LOAD[it],
              cor(w[, it], rowMeans(w[, groups[[g]]]), use = "complete.obs")))

worst <- max(dev)
cat(sprintf("\nlargest deviation over 5 alphas + 10 HTMTs: %.4f (tolerance %.4f)\n", worst, TOL))
cat("Establishes construct membership of every code prefix; does NOT establish order within a construct.\n")
cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
