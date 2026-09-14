# verify_qin_2025_tourist_satisfaction.R
#
# CLAIM: SA1/SA2/SA3 in the live IRW table carry the three satisfaction item
# texts that S1 Table of PLOS ONE 10.1371/journal.pone.0336220 prints against
# exactly those codes.
#
# Two independent links, neither of which is a count check:
#
#  (A) live code -> deposited column. The live table is joined to the study's own
#      S1 Data CSV (10.1371/journal.pone.0336220.s002) on id == "No." and each
#      live item is compared to each source column respondent by respondent. A
#      permutation of the three codes in the processing script breaks here. The
#      cross-code comparisons are printed so the wrong pairings can be seen to
#      disagree.
#
#  (B) deposited column -> the paper's own code. The paper's Table 7
#      (cross-loading analysis, an image) gives, for each of SA1/SA2/SA3, its
#      loading on BI, CI, PCD and RCTE. Those 12 cells are recomputed from the
#      source CSV as correlations of the raw item with each construct's mean.
#      This ties the codes the paper (hence its S1 Table wording) uses to the
#      columns of the deposited data. The SA2/SA3 swap is scored explicitly.

suppressMessages(library(irw))

TABLE <- "qin_2025_tourist_satisfaction"
SRC   <- "https://doi.org/10.1371/journal.pone.0336220.s002"

# Paper Table 7 (Discriminant Validity, Cross-Loading Analysis), SA rows.
#                      BI     CI     PCD    RCTE
PUB <- rbind(SA1 = c(0.769, 0.704, 0.321, 0.742),
             SA2 = c(0.819, 0.760, 0.335, 0.792),
             SA3 = c(0.812, 0.724, 0.289, 0.747))
colnames(PUB) <- c("BI", "CI", "PCD", "RCTE")

d <- irw::irw_fetch(TABLE)
s <- read.csv(SRC, check.names = FALSE)

## ---- (A) live item code vs source column, per respondent ------------------
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("resp.", "", names(w), fixed = TRUE)
m <- merge(w, s, by.x = "id", by.y = "No.")
cat(sprintf("joined respondents: %d (live ids x S1 Data 'No.')\n\n", nrow(m)))

cat("(A) per-respondent agreement, live item x source column (% of joined):\n")
cat(sprintf("%-6s %8s %8s %8s\n", "live", "SA1", "SA2", "SA3"))
agree <- matrix(NA_real_, 3, 3, dimnames = list(paste0("SA", 1:3), paste0("SA", 1:3)))
for (i in paste0("SA", 1:3)) {
    for (j in paste0("SA", 1:3))
        agree[i, j] <- 100 * mean(m[[paste0(i, ".x")]] == m[[paste0(j, ".y")]])
    cat(sprintf("%-6s %7.1f%% %7.1f%% %7.1f%%\n", i, agree[i, 1], agree[i, 2], agree[i, 3]))
}
diag_ok <- all(abs(diag(agree) - 100) < 1e-9)
offdiag_max <- max(agree[row(agree) != col(agree)])
cat(sprintf("\ndiagonal all 100%%: %s ; largest off-diagonal: %.1f%%\n\n",
            diag_ok, offdiag_max))

## ---- (B) recomputed cross-loadings vs paper Table 7 ------------------------
cons <- list(BI = paste0("BI", 1:3), CI = paste0("CI", 1:3),
             PCD = paste0("PCD", 1:3), RCTE = paste0("RCTE", 1:5))
comp <- sapply(cons, function(cc) rowMeans(s[, cc]))
obs <- t(sapply(paste0("SA", 1:3), function(i)
    sapply(colnames(PUB), function(k) cor(s[[i]], comp[, k]))))

cat("(B) paper Table 7 cross-loadings vs correlations recomputed from S1 Data:\n")
cat(sprintf("%-5s %-6s %10s %10s %8s\n", "item", "constr", "published", "observed", "diff"))
for (i in rownames(PUB)) for (k in colnames(PUB))
    cat(sprintf("%-5s %-6s %10.3f %10.3f %8.3f\n", i, k, PUB[i, k], obs[i, k],
                obs[i, k] - PUB[i, k]))
resid <- max(abs(obs - PUB))
cat(sprintf("\nlargest residual as mapped: %.4f\n", resid))

# Every one of the 5 permutations of SA1/SA2/SA3 other than the identity, scored
# the same way. If any fits comparably the mapping is not pinned by (B).
perms <- list(c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
cat("residual under each wrong permutation of the three codes:\n")
worst_wrong <- Inf
for (p in perms) {
    alt <- obs[p, , drop = FALSE]; rownames(alt) <- rownames(obs)
    r <- max(abs(alt - PUB))
    worst_wrong <- min(worst_wrong, r)
    cat(sprintf("  SA1<-SA%d SA2<-SA%d SA3<-SA%d : %.4f (%.1fx the mapped residual)\n",
                p[1], p[2], p[3], r, r / resid))
}
cat(sprintf("\nbest-fitting wrong permutation: %.4f vs %.4f as mapped (%.1fx)\n",
            worst_wrong, resid, worst_wrong / resid))

cat("\nWhat this does NOT establish: nothing here reads the item WORDING -- it ties\n",
    "each live code to a deposited column and to the paper's own code. The words come\n",
    "from S1 Table, which prints 'SA1'..'SA3' beside the three sentences (Step 5b's\n",
    "explicit-code-label exemption). The scale anchors are not checked at all: the\n",
    "source never states them and option_text ships blank.\n", sep = "")

ok <- diag_ok && offdiag_max < 100 && resid <= 0.01 && worst_wrong > 3 * resid
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
