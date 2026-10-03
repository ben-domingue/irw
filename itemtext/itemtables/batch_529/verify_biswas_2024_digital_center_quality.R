# verify_biswas_2024_digital_center_quality.R
#
# Claim: the paper's Table 2 prints each item against the very code the data uses
# (INFQ1..4, SYSQ1..3, SERQ1..3, SPES1..3, ACCS1..3, CONI1..3) and CITP1..3 for the
# data's PAR1..3. That label match ties code to text for 19 items; this script checks
# the falsifiable part underneath it -- that the data's code BLOCKS are the paper's
# constructs -- by reproducing Table 4's per-construct Cronbach's alpha from the live
# items, including that the paper's CONI is exactly CONI1-3 (not CONI1-7).
#
# What this does NOT establish: order WITHIN a block (alpha is permutation-invariant),
# so it cannot tell PAR1 from PAR2 (the one place where the code differs from the
# paper's label), nor anything about CONI4-7, which the paper never prints.

suppressMessages(library(irw))
TABLE <- "biswas_2024_digital_center_quality"

# Table 4 (PLOS ONE 10.1371/journal.pone.0304178), Cronbach's alpha column.
PUBLISHED <- c(ACCS = .919, SPES = .919, CONI = .794, SERQ = .875, SYSQ = .876, INFQ = .884)
BLOCKS <- list(ACCS = paste0("ACCS", 1:3), SPES = paste0("SPES", 1:3),
               CONI = paste0("CONI", 1:3), SERQ = paste0("SERQ", 1:3),
               SYSQ = paste0("SYSQ", 1:3), INFQ = paste0("INFQ", 1:4))
TOL <- 0.01

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
alpha <- function(X) { X <- na.omit(X); k <- ncol(X)
  k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }

obs <- sapply(BLOCKS, function(b) alpha(w[, b]))
cat(sprintf("%-6s %10s %10s %8s\n", "block", "published", "observed", "diff"))
for (b in names(PUBLISHED))
  cat(sprintf("%-6s %10.3f %10.3f %8.3f\n", b, PUBLISHED[b], obs[b], obs[b] - PUBLISHED[b]))

# Alternative CONI definitions, to show the published .794 singles out CONI1-3.
cat(sprintf("\nCONI1-7 alpha: %.3f   CONI4-7 alpha: %.3f   (published CONI: .794)\n",
            alpha(w[, paste0("CONI", 1:7)]), alpha(w[, paste0("CONI", 4:7)])))
cat(sprintf("PAR1-3 alpha: %.3f (Table 4 omits CITP; Table 5 gives CITP CR .835)\n",
            alpha(w[, paste0("PAR", 1:3)])))

# Informational: CONI3 is printed negatively worded but is stored positively keyed.
others <- setdiff(names(w), c("id", "CONI3", paste0("CONI", 4:7)))
r <- sapply(others, function(o) cor(w$CONI3, w[[o]]))
cat(sprintf("CONI3 correlation with the other 21 non-CONI4-7 items: min %.2f, max %.2f\n",
            min(r), max(r)))

worst <- max(abs(obs - PUBLISHED))
cat(sprintf("\nlargest deviation: %.3f (tolerance %.2f)\n", worst, TOL))
cat("Note: alpha pins block membership only, not order within a block.\n")
cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
