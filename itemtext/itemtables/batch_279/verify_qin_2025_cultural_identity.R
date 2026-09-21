# verify_qin_2025_cultural_identity.R
#
# CLAIM: CI1/CI2/CI3 in the live IRW table carry the three cultural-identity item
# texts that S1 Table of PLOS ONE 10.1371/journal.pone.0336220 prints against
# exactly those codes.
#
# Two independent links are checked; neither is a count check.
#
#  (A) code -> column. The live table is joined to the study's own S1 Data CSV
#      (10.1371/journal.pone.0336220.s002) on id == "No.", and each live item's
#      responses are compared to the source column of the same name, respondent by
#      respondent. If data/qin_2025_cultural_tourism.py had permuted the three
#      codes, this is where it breaks. The cross-code comparisons are printed too,
#      so a reader can see the wrong pairings do NOT match.
#
#  (B) column -> paper code. The paper's Table 7 cross-loading matrix gives, for
#      each of CI1/CI2/CI3, its loading on the BI, PCD, RCTE and SA constructs.
#      Those 12 cells are recomputed from the source CSV as correlations of the raw
#      item with each construct's mean, and compared to the published values. This
#      is what ties the paper's OWN codes (hence its S1 Table item texts) to the
#      columns of the deposited data. Every pairwise swap is scored explicitly.
#      Note CI2 and CI3 share the SAME published own-construct loading (0.922), so
#      the own-construct column is useless for separating them; the four
#      cross-construct columns are what do it.

suppressMessages(library(irw))

TABLE <- "qin_2025_cultural_identity"
SRC   <- "https://doi.org/10.1371/journal.pone.0336220.s002"

# Paper Table 7 (Discriminant Validity, Cross-Loading Analysis), CI rows.
#                     BI     PCD    RCTE     SA
PUB <- rbind(CI1 = c(0.678, 0.208, 0.732, 0.673),
             CI2 = c(0.686, 0.294, 0.775, 0.734),
             CI3 = c(0.716, 0.295, 0.834, 0.733))
colnames(PUB) <- c("BI", "PCD", "RCTE", "SA")

d <- irw::irw_fetch(TABLE)
s <- read.csv(SRC, check.names = FALSE)

## ---- (A) live item code vs source column, per respondent ------------------
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("resp.", "", names(w), fixed = TRUE)
m <- merge(w, s, by.x = "id", by.y = "No.")
cat(sprintf("joined respondents: %d (live ids x S1 Data 'No.')\n\n", nrow(m)))

cat("(A) per-respondent agreement, live item x source column (% of joined):\n")
cat(sprintf("%-6s %8s %8s %8s\n", "live", "CI1", "CI2", "CI3"))
agree <- matrix(NA_real_, 3, 3,
                dimnames = list(paste0("CI", 1:3), paste0("CI", 1:3)))
for (i in paste0("CI", 1:3)) {
    for (j in paste0("CI", 1:3))
        agree[i, j] <- 100 * mean(m[[paste0(i, ".x")]] == m[[paste0(j, ".y")]])
    cat(sprintf("%-6s %7.1f%% %7.1f%% %7.1f%%\n", i, agree[i, 1], agree[i, 2], agree[i, 3]))
}
diag_ok <- all(abs(diag(agree) - 100) < 1e-9)
offdiag_max <- max(agree[row(agree) != col(agree)])
cat(sprintf("\ndiagonal all 100%%: %s ; largest off-diagonal: %.1f%%\n\n",
            diag_ok, offdiag_max))

## ---- (B) recomputed cross-loadings vs paper Table 7 ------------------------
cons <- list(BI = paste0("BI", 1:3), PCD = paste0("PCD", 1:3),
             RCTE = paste0("RCTE", 1:5), SA = paste0("SA", 1:3))
comp <- sapply(cons, function(cc) rowMeans(s[, cc]))
obs <- t(sapply(paste0("CI", 1:3), function(i)
    sapply(colnames(PUB), function(k) cor(s[[i]], comp[, k]))))

cat("(B) paper Table 7 cross-loadings vs correlations recomputed from S1 Data:\n")
cat(sprintf("%-5s %-6s %10s %10s %8s\n", "item", "constr", "published", "observed", "diff"))
for (i in rownames(PUB)) for (k in colnames(PUB))
    cat(sprintf("%-5s %-6s %10.3f %10.3f %8.3f\n", i, k, PUB[i, k], obs[i, k],
                obs[i, k] - PUB[i, k]))
resid <- max(abs(obs - PUB))
cat(sprintf("\nlargest residual as mapped: %.4f\n", resid))

# Score every non-identity permutation of the three codes against Table 7.
perms <- list(c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
worst_alt <- Inf
for (p in perms) {
    alt <- obs[p, , drop = FALSE]; rownames(alt) <- rownames(obs)
    r <- max(abs(alt - PUB))
    worst_alt <- min(worst_alt, r)
    cat(sprintf("largest residual under permutation (%s): %.4f (%.1fx the mapped fit)\n",
                paste0("CI", p, collapse = ","), r, r / resid))
}
cat(sprintf("\nbest-fitting WRONG permutation: %.4f vs %.4f as mapped (%.1fx worse)\n",
            worst_alt, resid, worst_alt / resid))

cat("\nWhat this does NOT establish: nothing here reads the item WORDING -- it ties\n",
    "each live code to a source column and each source column to the paper's own\n",
    "code. The words come from S1 Table, which prints 'CI1'..'CI3' beside the three\n",
    "sentences (Step 5b's explicit-code-label exemption); the checks above are what\n",
    "rule out the codes having been permuted between paper, deposit and IRW. It also\n",
    "says nothing about option_text, which is blank for all six levels because the\n",
    "source never publishes the scale's anchors.\n",
    sep = "")

ok <- diag_ok && offdiag_max < 100 && resid <= 0.01 && worst_alt > 2 * resid
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
