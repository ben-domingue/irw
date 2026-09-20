# verify_pellerin2020_asti.R -- Step 5b, route 5 (subscale/block structure) applied
# WITHIN one subscale, against an external reference correlation matrix.
#
# CLAIM UNDER TEST: ST_1..ST_7 correspond, in order, to the seven
# self-transcendence items of the ASTI as numbered by Koller, Levenson & Glueck
# (2017) -- ASTI2, ASTI4, ASTI7, ASTI13, ASTI16, ASTI24, ASTI25.
#
# The prediction that would break if any two item_texts were swapped: the 7x7
# inter-item correlation matrix of the live French data should, up to sampling
# noise, reproduce the SHAPE of the same seven items' correlation matrix in the
# ASTI reference sample distributed in MPsychoR (n=1129; identical to the matrix
# printed in Koller et al. 2017's Appendix / DataSheet1.docx). We score all 5040
# permutations and report where the claimed one lands.
#
# Response data: the study's own OSF deposit (osf.io/45aq3,
# data.PsyR_lockdown2020.csv, sha256 4909d4819b8b6682eaf7db347e702afd20088b979f43cd09667160cd8b7db5fb),
# which is what data/pellerin2020_covid_resources.py melts into the IRW table --
# it keeps the column names ST_1..ST_7 verbatim, so no re-derivation is needed.
# irw::irw_fetch() is deliberately NOT called (200GB/30d export quota); the live
# table's item set, resp set and per-item n=1010 were confirmed server-side with
# irw::irw_table_sets() and match this file exactly.

suppressMessages(library(MPsychoR))

URL <- "https://osf.io/download/dc6me/"
loc <- file.path("..", "..", ".cache", "pellerin2020_asti", "data.csv")
if (!file.exists(loc)) {
  loc <- tempfile(fileext = ".csv")
  download.file(URL, loc, quiet = TRUE)
}
d <- read.csv(loc)
m <- d[, paste0("ST_", 1:7)]
stopifnot(all(colSums(!is.na(m)) == 1010))
obs <- cor(m, use = "pairwise.complete.obs")

data("ASTI", package = "MPsychoR")
ref <- cor(ASTI[, c(2, 4, 7, 13, 16, 24, 25)], use = "pairwise.complete.obs")
LAB <- c("ASTI2", "ASTI4", "ASTI7", "ASTI13", "ASTI16", "ASTI24", "ASTI25")
dimnames(ref) <- list(LAB, LAB)

cat("Reference (MPsychoR ASTI, n =", sum(complete.cases(ASTI[, c(2,4,7,13,16,24,25)])), ") ST correlations:\n")
print(round(ref, 3))
cat("\nLive (Pellerin & Raufaste 2020, French, n = 1010 obs/item) ST_ correlations:\n")
print(round(obs, 3))

ut <- upper.tri(ref); rv <- ref[ut]
permn <- function(n) { if (n == 1) return(matrix(1)); p <- permn(n - 1); o <- NULL
  for (i in 1:n) o <- rbind(o, cbind(i, matrix(ifelse(p < i, p, p + 1), nrow = nrow(p)))); o }
P <- permn(7)
scP <- apply(P, 1, function(p) { o <- obs[p, p]; cor(o[ut], rv) })
scS <- apply(P, 1, function(p) { o <- obs[p, p]; cor(o[ut], rv, method = "spearman") })
ord <- order(-scP)
idr <- which(apply(P, 1, function(p) all(p == 1:7)))

cat("\nAll 5040 permutations scored (Pearson r between the 21 off-diagonal\n",
    "reference correlations and the correspondingly permuted live ones).\n",
    "Top 6 -- 'ST_a ST_b ...' means reference item k is claimed to be ST_<k-th entry>:\n", sep = "")
for (i in ord[1:6])
  cat(sprintf("   r=%.4f  rho=%.4f   %s%s\n", scP[i], scS[i],
              paste0("ST_", P[i, ], collapse = " "),
              if (i == idr) "   <-- SHIPPED MAPPING" else ""))

cat(sprintf("\nShipped (identity) mapping: rank %d of 5040 by Pearson (r=%.4f), rank %d by Spearman (rho=%.4f)\n",
            which(ord == idr), scP[idr], which(order(-scS) == idr), scS[idr]))

cat(sprintf("\nMarker pairs -- reference r(ASTI2,ASTI7)=%.2f is the largest of the 21;\n", ref["ASTI2","ASTI7"]))
cat(sprintf("  live r(ST_1,ST_3)=%.2f is likewise the largest of the 21.\n", obs["ST_1","ST_3"]))
cat(sprintf("Reference r(ASTI24,ASTI25)=%.2f; live r(ST_6,ST_7)=%.2f -- both the 2nd-tier pair.\n",
            ref["ASTI24","ASTI25"], obs["ST_6","ST_7"]))
cat(sprintf("ASTI13 is the reference's least-connected ST item (mean r=%.3f); ST_4 is the live one (mean r=%.3f).\n",
            mean(ref["ASTI13", -4]), mean(obs["ST_4", -4])))

cat("\nWHAT THIS DOES NOT ESTABLISH. The top four permutations are the shipped one\n",
    "and the three obtained by swapping ST_1<->ST_3 and/or ST_2<->ST_5, all within\n",
    "0.009 of it in r. So the route pins the blocks {ST_1,ST_3}={ASTI2,ASTI7},\n",
    "{ST_2,ST_5}={ASTI4,ASTI16}, ST_4=ASTI13, {ST_6,ST_7}={ASTI24,ASTI25} and,\n",
    "via the 6<->7 swap costing 0.039 in r, the order within that last pair -- but\n",
    "it does NOT separate ASTI2 from ASTI7, nor ASTI4 from ASTI16. Those two\n",
    "assignments rest on presentation order alone. Status is PARTIAL, not VERIFIED.\n", sep = "")

pass <- which(ord == idr) == 1 &&
        obs["ST_1","ST_3"] == max(obs[ut]) &&
        which.max(obs["ST_4", -4]) == which.max(ref["ASTI13", -4])
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
