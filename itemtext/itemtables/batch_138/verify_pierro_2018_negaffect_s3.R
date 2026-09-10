# verify_pierro_2018_negaffect_s3.R
#
# TABLE:  pierro_2018_negaffect_s3  -- BLOCKED in batch_138, no __items.csv written.
# CLAIM being made re-runnable: the item codes negaffect1..negaffect10 CANNOT be tied
# to particular PANAS negative-affect adjectives from anything the source publishes,
# and the one testable ordering hypothesis -- that negaffect_i is the i-th NA adjective
# of the canonical Watson/Clark/Tellegen (1988) 20-item sequence -- is DISCONFIRMED by
# the deposit's own covariance structure. That is why mapping_basis=unknown /
# status=NO_ROUTE and why no item text was shipped.
#
# This verifies the MAPPING claim, not the plumbing: it never counts items.
#
# Source of data: the study's own deposit, S3 File of
# Pierro, Pica, Giannini, Higgins & Kruglanski (2018) PLoS ONE 13(3):e0193357,
# https://doi.org/10.1371/journal.pone.0193357.s003  (SPSS .sav, CC BY 4.0).
# The IRW code IS that file's column name (data/pierro_2018_selfforgiveness.py melts
# the negaffect* columns unrenamed), so the .sav columns and the live item codes are
# the same objects and the structure below is the live table's structure.
#
# THE TEST
#   The PANAS NA half is five near-synonym couplets:
#     distressed/upset, guilty/ashamed, scared/afraid, hostile/irritable, nervous/jittery
#   In canonical order (1 distressed, 2 upset, 3 guilty, 4 scared, 5 hostile,
#   6 irritable, 7 ashamed, 8 nervous, 9 jittery, 10 afraid) those couplets sit at
#   index pairs (1,2) (3,7) (4,10) (5,6) (8,9), and Watson & Clark's NA facets are
#   fear{4,8,9,10} guilt{3,7} hostility{5,6} sadness{1,2}.
#   If the numbering were canonical, those pairs should be the strongest correlations
#   in the matrix and within-facet r should exceed between-facet r.
#   PASS = the prediction fails (canonical ordering ruled out, block justified).
#   FAIL = the prediction holds (canonical ordering supported -- reopen the table).

suppressMessages({
    ok <- requireNamespace("haven", quietly = TRUE)
})
if (!ok) stop("needs the 'haven' package to read the deposit .sav")

URL <- "https://doi.org/10.1371/journal.pone.0193357.s003"
f <- tempfile(fileext = ".sav")
utils::download.file(URL, f, quiet = TRUE, mode = "wb")
d <- haven::read_sav(f)

items <- paste0("negaffect", 1:10)
m <- as.data.frame(d[, items])
# the IRW script keeps only 1-5; the raw file holds one stray 6 on negaffect6.
m[m > 5 | m < 1] <- NA
cc <- cor(m, use = "pairwise.complete.obs")
dimnames(cc) <- list(1:10, 1:10)

cat("Inter-item correlations, negaffect1..10 (S3 File, N=85):\n")
print(round(cc, 2))

# --- 1. observed mutual-top-partner couplets ---------------------------------
top <- sapply(1:10, function(i) { r <- cc[i, ]; r[i] <- -2; which.max(r) })
mutual <- unique(t(apply(cbind(1:10, top), 1, sort)))
mutual <- unique(mutual[apply(mutual, 1, function(p) top[p[1]] == p[2] && top[p[2]] == p[1]), , drop = FALSE])
cat("\nObserved mutual top-partner couplets (each item's single strongest partner,\nreciprocated):\n")
for (k in seq_len(nrow(mutual)))
    cat(sprintf("  {%d,%d}  r = %.2f\n", mutual[k,1], mutual[k,2], cc[mutual[k,1], mutual[k,2]]))

CANON <- list(c(1,2), c(3,7), c(4,10), c(5,6), c(8,9))
cat("\nCouplets the canonical PANAS ordering predicts, and their observed r:\n")
nm <- c("distressed/upset","guilty/ashamed","scared/afraid","hostile/irritable","nervous/jittery")
hits <- 0
for (k in seq_along(CANON)) {
    p <- CANON[[k]]
    is_mut <- any(apply(mutual, 1, function(q) all(sort(q) == sort(p))))
    hits <- hits + is_mut
    cat(sprintf("  %-18s {%d,%d}  r = %.2f   mutual-top: %s\n",
                nm[k], p[1], p[2], cc[p[1], p[2]], if (is_mut) "YES" else "no"))
}
cat(sprintf("\n  canonical couplets recovered as mutual top partners: %d of 5\n", hits))

# --- 2. within- vs between-facet correlation under canonical ordering --------
fac <- c(1,1,2,3,4,4,2,3,3,3)   # 1 sadness, 2 guilt, 3 fear, 4 hostility
w <- c(); b <- c()
for (i in 1:9) for (j in (i+1):10)
    if (fac[i] == fac[j]) w <- c(w, cc[i,j]) else b <- c(b, cc[i,j])
cat(sprintf("\nUnder canonical ordering: mean WITHIN-facet r = %.3f (n=%d)\n", mean(w), length(w)))
cat(sprintf("                          mean BETWEEN-facet r = %.3f (n=%d)\n", mean(b), length(b)))
cat(sprintf("                          within - between      = %+.3f  (should be clearly positive\n", mean(w) - mean(b)))
cat("                                                   if the numbering were canonical)\n")

cat("\nWhat this does NOT establish: it does not identify the true ordering, and it\n")
cat("cannot -- five clean synonym couplets are visible in the data but nothing in the\n")
cat("deposit or the paper says which adjective any of them is. Ruling out one ordering\n")
cat("is the whole of the evidence; NO_ROUTE is the honest status.\n\n")

pass <- (hits == 0) && (mean(w) <= mean(b))
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
