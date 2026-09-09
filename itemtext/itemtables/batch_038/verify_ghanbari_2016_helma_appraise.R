# verify_ghanbari_2016_helma_appraise.R
#
# CLAIM UNDER TEST: the IRW item codes appraise1..appraise5 correspond, in order, to
# items 25..29 (the appraisal subscale) of the final 44-item HELMA questionnaire
# deposited as S1/S2 File with Ghanbari et al. (2016) PLoS ONE 11(2):e0149202.
#
# WHY A SCRIPT IS NEEDED: the study's S3 File .sav carries NO variable labels, so the
# tie from column name to questionnaire wording is an inference from block order.
#
# HOW IT IS TESTED: the paper's Table 2 publishes the full 8-factor principal-components
# / varimax loading matrix for all 44 final items. That matrix is a falsifiable
# per-item prediction. This script refits it from the raw .sav and checks that each
# appraiseK column's loading profile is nearest to published item 24+K and to no other.
# Swapping any two item_text values would break it.
#
# NOTE ON DATA SOURCE: the live IRW table holds only the 5 appraisal items, from which an
# 8-factor solution cannot be refit, so this fetches the study's raw .sav -- which is
# exactly what data/ghanbari_2016_helma.py builds the live table from. irw_fetch() is
# deliberately NOT called (it would export the whole table against the 200GB quota);
# validate_items.R --table-sets already established the item/resp sets.

suppressMessages(library(psych))
suppressMessages(library(haven))

SAV_URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0149202.s003"
cand <- c(file.path("..", "..", ".cache", "ghanbari_2016_helma_appraise", "s3.sav"),
          file.path(".cache", "ghanbari_2016_helma_appraise", "s3.sav"),
          file.path("itemtext", ".cache", "ghanbari_2016_helma_appraise", "s3.sav"))
cache <- cand[file.exists(cand)][1]
if (is.na(cache)) {
  cache <- tempfile(fileext = ".sav")
  utils::download.file(SAV_URL, cache, quiet = TRUE, mode = "wb")
}
cat("data source:", cache, "\n")
d <- haven::read_sav(cache)

# The 44-item final form, reconstructed from the 47-item pilot pool
# (dropped: access10, access11, use5; reading6 was reassigned to understanding).
final <- c(paste0("access", 1:9), paste0("reading", 1:6), paste0("understand", 1:9),
           paste0("appraise", 1:5), paste0("use", 1:4), paste0("com", 1:8),
           paste0("num", 1:3))
stopifnot(length(final) == 44, all(final %in% names(d)))
x <- as.data.frame(lapply(d[final], as.numeric))

L <- unclass(principal(x, nfactors = 8, rotate = "varimax")$loadings)

ap <- paste0("appraise", 1:5)
# Identify each rotated component by the block that dominates it, and put the
# components in the paper's Factor1..Factor6 order.
blocks <- list(F1_understanding = paste0("understand", 1:9),
               F2_communication = paste0("com", 1:8),
               F3_reading       = paste0("reading", 1:5),
               F4_appraisal     = ap,
               F5_access        = paste0("access", 5:9),
               F6_use           = paste0("use", 1:4))
ord <- sapply(blocks, function(b) names(which.max(colSums(L[b, , drop = FALSE]^2))))
stopifnot(!anyDuplicated(ord))
O <- L[ap, ord]; colnames(O) <- names(blocks)

# Published Table 2, items 25-29, columns Factor1..Factor6 (hard-coded from the paper).
P <- rbind(item25 = c(.272, .103, .064, .596,  .102, .062),
           item26 = c(.175, .215, .139, .671, -.012, .187),
           item27 = c(.260, .203, .058, .724,  .103, .060),
           item28 = c(.182, .221, .060, .674,  .145, .044),
           item29 = c(.392, .193, .148, .559,  .143, .190))
colnames(P) <- names(blocks)

cat("Observed loadings refit from S3 File .sav (n =", nrow(x), "):\n"); print(round(O, 3))
cat("\nPublished loadings, paper Table 2 items 25-29:\n"); print(P)

D <- outer(1:5, 1:5, Vectorize(function(i, j) sqrt(sum((O[i, ] - P[j, ])^2))))
dimnames(D) <- list(ap, rownames(P))
cat("\nEuclidean distance observed x published:\n"); print(round(D, 3))

diagd <- diag(D)
offmin <- sapply(1:5, function(i) min(D[i, -i]))
cat("\n")
for (i in 1:5)
  cat(sprintf("%-10s -> %s  d=%.3f   nearest other = %.3f   margin %.1fx\n",
              ap[i], rownames(P)[i], diagd[i], offmin[i], offmin[i] / diagd[i]))

row_ok <- all(apply(D, 1, which.min) == 1:5)
col_ok <- all(apply(D, 2, which.min) == 1:5)
cat(sprintf("\nrow-wise argmin is the diagonal: %s\ncol-wise argmin is the diagonal: %s\n",
            row_ok, col_ok))

perms <- function(v) if (length(v) == 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
ps <- perms(1:5)
sse <- sapply(ps, function(p) sum((O - P[p, ])^2))
o <- order(sse)
cat(sprintf("SSE identity = %.5f ; runner-up (perm %s) = %.5f ; ratio = %.1fx\n",
            sse[o[1]], paste(ps[[o[2]]], collapse = ""), sse[o[2]], sse[o[2]] / sse[o[1]]))

cat("\nNote: this verifies the item_text<->item axis only. The option_text<->resp axis\n",
    "rests on the .sav's own value labels for appraise1-5 (1=never ... 5=always), a\n",
    "level-1 source that needs no statistical check. It also does not test whether the\n",
    "47-item pilot administration worded these five items exactly as the deposited\n",
    "44-item final form does -- only that the same five items, in the same order, are\n",
    "the appraisal block in both.\n", sep = "")

pass <- row_ok && col_ok &&
        identical(as.integer(ps[[o[1]]]), 1:5) &&
        (sse[o[2]] / sse[o[1]]) > 2 &&
        max(diagd) < 0.10
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
