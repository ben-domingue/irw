# verify_karpudewan_2022_stp_cca.R
#
# CLAIM UNDER TEST. The CCA supplementary workbook (S1 Dataset, PLOS ONE
# 10.1371/journal.pone.0268509.s004) labels its columns STP1-8, KN1-7, PD1-10,
# PE1-4, but the paper's item wording (S3 Appendix) is keyed to the ORIGINAL
# 33-item numbering, from which EFA removed KN1, KN9, STP6 and STP9. So the
# shipped mapping asserts a contiguous, ORDER-PRESERVING renumbering:
#
#   KN1..KN7  <- original KN2..KN8
#   STP1..STP8 <- original STP1,2,3,4,5,7,8,10
#   PD1..PD10, PE1..PE4  <- unchanged (all retained)
#
# Two falsifiable predictions follow, both against paper Table 1, which reports
# PLS-SEM outer loadings computed on THIS sample (n = 397):
#
#  (A) The first principal component loadings of the live KN block, in column
#      order KN1..KN7, must reproduce the published loadings for KN2..KN8 in
#      that order. A permutation of the block breaks this. Same for PE1..PE4.
#  (B) The paper removed exactly two STP items at CCA for outer loading < 0.708.
#      Under the mapping those are original STP1 and STP3 = live STP1 and STP3,
#      so those two and only those two must fall below 0.708 in the live block.

suppressMessages(library(irw))

TABLE <- "karpudewan_2022_stp_cca"

# Paper Table 1 (Outer loading, AVE, CR), original item codes.
PUB_KN <- c(KN2 = 0.873, KN3 = 0.867, KN4 = 0.892, KN5 = 0.940,
            KN6 = 0.889, KN7 = 0.901, KN8 = 0.834)
PUB_PE <- c(PE1 = 0.841, PE2 = 0.905, PE3 = 0.914, PE4 = 0.896)
TOL_KN <- 0.02
TOL_PE <- 0.05
CUTOFF <- 0.708

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

pc1 <- function(cols) {
    X <- as.matrix(w[, cols]); X <- X[complete.cases(X), , drop = FALSE]
    C <- cor(X); e <- eigen(C)
    ld <- e$vectors[, 1] * sqrt(e$values[1])
    if (sum(ld) < 0) ld <- -ld
    setNames(ld, cols)
}

ok <- TRUE

cat("=== (A) KN block: live PC1 loadings vs paper Table 1, KN2..KN8 ===\n")
obs <- pc1(paste0("KN", 1:7))
cat(sprintf("%-6s %-6s %10s %10s %8s\n", "live", "paper", "published", "observed", "diff"))
for (i in 1:7)
    cat(sprintf("%-6s %-6s %10.3f %10.3f %8.3f\n",
                paste0("KN", i), names(PUB_KN)[i], PUB_KN[i], obs[i], obs[i] - PUB_KN[i]))
wKN <- max(abs(obs - PUB_KN))
cat(sprintf("largest deviation: %.3f (tolerance %.2f)\n", wKN, TOL_KN))
if (wKN > TOL_KN) ok <- FALSE

cat("\n  rival hypothesis (renumbered in S3-Appendix listing order, i.e.\n")
cat("  KN1..KN7 <- KN5,KN6,KN7,KN2,KN4,KN8,KN3) predicts, in live order:\n")
riv <- PUB_KN[c("KN5", "KN6", "KN7", "KN2", "KN4", "KN8", "KN3")]
cat("   predicted:", sprintf("%.3f", riv), "\n")
cat("   observed :", sprintf("%.3f", obs), "\n")
cat(sprintf("   largest deviation under rival: %.3f\n", max(abs(obs - riv))))
if (max(abs(obs - riv)) <= wKN) ok <- FALSE   # rival must fit strictly worse

cat("\n=== (A') PE block: live PC1 loadings vs paper Table 1, PE1..PE4 ===\n")
obsPE <- pc1(paste0("PE", 1:4))
for (i in 1:4)
    cat(sprintf("%-6s %10.3f %10.3f %8.3f\n",
                paste0("PE", i), PUB_PE[i], obsPE[i], obsPE[i] - PUB_PE[i]))
wPE <- max(abs(obsPE - PUB_PE))
cat(sprintf("largest deviation: %.3f (tolerance %.2f)\n", wPE, TOL_PE))
if (wPE > TOL_PE) ok <- FALSE

cat("\n=== (B) STP block: which two items fall below the paper's 0.708 cutoff ===\n")
obsS <- pc1(paste0("STP", 1:8))
for (i in 1:8) cat(sprintf("%-6s %6.3f%s\n", paste0("STP", i), obsS[i],
                           if (obsS[i] < CUTOFF) "   <- below 0.708" else ""))
below <- names(obsS)[obsS < CUTOFF]
cat("below cutoff:", paste(below, collapse = ", "),
    "| expected under the mapping: STP1, STP3\n")
if (!setequal(below, c("STP1", "STP3"))) ok <- FALSE

cat("\n=== (C) corroboration: belief statements vs self-report practice items ===\n")
# Original STP5, STP7, STP10 are general statements about STEM teaching
# ("STEM teaching engages students to work in groups", "...involves students
# solving daily problems", "Questioning is an important component..."); the
# other five are first-person practice reports ("I use...", "I regularly
# observe..."). Under the mapping the belief items are live STP5, STP6, STP8.
mn <- sort(tapply(d$resp, d$item, mean)[paste0("STP", 1:8)], decreasing = TRUE)
cat("live STP item means, descending:\n")
for (i in seq_along(mn)) cat(sprintf("  %-6s %5.3f\n", names(mn)[i], mn[i]))
top3 <- names(mn)[1:3]
cat("top three:", paste(top3, collapse = ", "),
    "| expected belief items: STP5, STP6, STP8\n")
if (!setequal(top3, c("STP5", "STP6", "STP8"))) ok <- FALSE

cat("\nNote: what this does NOT establish. The published STP outer loadings\n",
    "(0.823-0.971) are not reproduced in magnitude by any subset of this block\n",
    "(max PC1 loading 0.86), so check (B) pins only WHICH two STP positions were\n",
    "dropped, and (C) only the 3-vs-5 belief/practice split. The order of the six\n",
    "retained STP items among themselves rests on the order-preserving renumbering\n",
    "convention, which is proven for KN by (A) but not re-proven within STP.\n",
    "PD1-10 and PE1-4 are unrenumbered and carry no inference at all.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
