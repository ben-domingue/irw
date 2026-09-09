# verify_ghanbari_2016_helma_understand.R
#
# CLAIM UNDER TEST: the IRW item codes understand1..understand9 correspond, in order,
# to items 16..24 of the final 44-item HELMA questionnaire deposited as S1 File
# (English) / S2 File (Persian) with Ghanbari et al. (2016) PLoS ONE 11(2):e0149202.
# The published understanding subscale has TEN items (15-24); its tenth, item 15, is
# the .sav column `reading6` and lives in the sibling table, not in this one.
#
# WHY A SCRIPT IS NEEDED: the study's S3 File .sav carries NO variable labels on any of
# its 47 item columns, so the tie from column name to questionnaire wording is inferred
# from block position and within-block order.
#
# HOW IT IS TESTED, three ways:
#   (A) The paper's Table 2 publishes the 8-factor PCA/varimax loading matrix for all
#       44 final items. Refit it from the raw .sav and check that the assignment of the
#       10 raw understanding-factor columns (reading6 + understand1..9) to published
#       rows 15..24 that MINIMISES total distance is exactly the claimed identity map.
#   (B) A content-implied prediction that does not use loadings: item 23 is the third
#       media item, so its column must correlate most strongly with the two known media
#       items (21, 22 = understand6, understand7) among the block.
#   (C) A second content prediction: item 20 is about nutrition labels on food packages,
#       so its column must correlate most strongly with the two other nutrition-label
#       items in the instrument -- item 30 (`use1`, choosing food by its nutrition panel)
#       and item 42 (`num1`, computing carbohydrate intake from a nutrition panel).
#
# NOT ESTABLISHED (see the verification row): understand1 vs understand2 (items 16 vs 17)
# are NOT separated from each other by any of these routes.
#
# DATA SOURCE: the study's raw S3 File .sav, which is what data/ghanbari_2016_helma.py
# builds the live table from. irw_fetch() is deliberately NOT called (it would export the
# whole table against the 200GB quota); validate_items.R --table-sets already established
# the item and resp sets.

suppressMessages(library(psych))
suppressMessages(library(haven))
suppressMessages(library(clue))

SAV_URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0149202.s003"
cand <- c(file.path("..", "..", ".cache", "ghanbari_2016_helma_understand", "s3.sav"),
          file.path(".cache", "ghanbari_2016_helma_understand", "s3.sav"),
          file.path("itemtext", ".cache", "ghanbari_2016_helma_understand", "s3.sav"))
cache <- cand[file.exists(cand)][1]
if (is.na(cache)) {
  cache <- tempfile(fileext = ".sav")
  utils::download.file(SAV_URL, cache, quiet = TRUE, mode = "wb")
}
cat("data source:", cache, "\n")
d <- haven::read_sav(cache)

# The 44-item final form reconstructed from the 47-item pilot pool
# (dropped: access10, access11, use5; reading6 reassigned to understanding).
final <- c(paste0("access", 1:9), paste0("reading", 1:6), paste0("understand", 1:9),
           paste0("appraise", 1:5), paste0("use", 1:4), paste0("com", 1:8),
           paste0("num", 1:3))
stopifnot(length(final) == 44, all(final %in% names(d)))
x <- as.data.frame(lapply(d[final], as.numeric))
x <- x[complete.cases(x), ]
cat("complete cases:", nrow(x), "\n\n")

U <- c("reading6", paste0("understand", 1:9))

# ---- (A) published Table 2 loadings, items 15-24, Factor1..Factor7 -------------
P <- rbind(
  item15 = c(.488, .093, .301,  .238, .140,  .091,  .005),
  item16 = c(.646, .156, .129,  .238, .034,  .080,  .183),
  item17 = c(.612, .171, .188,  .209, .083,  .070,  .165),
  item18 = c(.676, .173, .046,  .141, .039,  .008,  .236),
  item19 = c(.650, .181, .146,  .199, .001, -.018,  .242),
  item20 = c(.601, -.010, .163, .277, .140,  .133, -.009),
  item21 = c(.668, .148, .185,  .137, .187,  .132, -.027),
  item22 = c(.683, .167, .199, -.097, .074,  .184, -.145),
  item23 = c(.695, .204, .195,  .085, .104,  .085,  .058),
  item24 = c(.556, .219, .262,  .205, .022, -.024,  .114))
FL <- c("understanding", "communication", "reading", "appraisal", "access", "use", "self_efficacy")
colnames(P) <- FL

L <- unclass(principal(x, nfactors = 8, rotate = "varimax")$loadings)
blocks <- list(paste0("understand", 1:9), paste0("com", 1:8), paste0("reading", 1:5),
               paste0("appraise", 1:5), paste0("access", 5:9), paste0("use", 1:4),
               paste0("access", 1:4))
ord <- sapply(blocks, function(b) names(which.max(colSums(L[b, , drop = FALSE]^2))))
stopifnot(!anyDuplicated(ord))
O <- L[U, ord]; colnames(O) <- FL

cat("Observed loadings refit from S3 File .sav:\n"); print(round(O, 3))
cat("\nPublished loadings, paper Table 2 items 15-24:\n"); print(P)

D <- outer(1:10, 1:10, Vectorize(function(i, j) sqrt(sum((O[i, ] - P[j, ])^2))))
dimnames(D) <- list(U, rownames(P))
cat("\nEuclidean distance observed x published:\n"); print(round(D, 3))

a <- as.integer(solve_LSAP(D))
cat("\nminimum-cost assignment:\n")
for (i in 1:10) cat(sprintf("  %-12s -> %s   d=%.3f\n", U[i], rownames(P)[a[i]], D[i, a[i]]))
id_cost <- sum(diag(D))
cat(sprintf("identity cost = %.4f ; optimal cost = %.4f\n", id_cost, sum(D[cbind(1:10, a)])))
lsap_identity <- identical(a, 1:10)

# how much worse is the best assignment that DENIES each claimed pair?
cat("\ncost of the best assignment that forbids each claimed pair (excess over identity):\n")
excess <- numeric(10)
for (i in 1:10) {
  D2 <- D; D2[i, i] <- 1e6
  b <- as.integer(solve_LSAP(D2))
  excess[i] <- sum(D2[cbind(1:10, b)]) - id_cost
  cat(sprintf("  %-12s !-> %-7s : %.4f  (excess %.4f)\n", U[i], rownames(P)[i],
              excess[i] + id_cost, excess[i]))
}

# ---- (B) media-content route: item 23 must be the third media item ------------
R <- cor(x)
ub <- paste0("understand", 1:9)
media <- c("understand6", "understand7")           # claimed items 21 and 22
rmedia <- rowMeans(R[ub, media])
cat("\n(B) mean correlation with the two claimed media items (understand6, understand7):\n")
print(round(rmedia[setdiff(ub, media)], 3))
b_ok <- names(which.max(rmedia[setdiff(ub, media)])) == "understand8"
cat(sprintf("highest is %s (claim: understand8 = item 23, 'health and illness in the media') -> %s\n",
            names(which.max(rmedia[setdiff(ub, media)])), if (b_ok) "as predicted" else "CONTRADICTED"))

# ---- (C) nutrition-label route: item 20 -------------------------------------
rnut <- rowMeans(cbind(R[ub, "num1"], R[ub, "use1"]))
cat("\n(C) mean correlation with the two nutrition-panel items num1 (item 42) and use1 (item 30):\n")
print(round(rnut, 3))
c_ok <- names(which.max(rnut)) == "understand5"
cat(sprintf("highest is %s (claim: understand5 = item 20, 'nutrition facts on food packages') -> %s\n",
            names(which.max(rnut)), if (c_ok) "as predicted" else "CONTRADICTED"))

cat("\nWhat this does NOT establish: understand1 and understand2 (claimed items 16 and 17)\n",
    "are mutually interchangeable under route A -- forbidding either claimed pair costs\n",
    "only ~0.026 extra, and a 300-replicate bootstrap of the same EFA makes item16's\n",
    "modal partner ambiguous. Their order rests on the block-order argument, not on data.\n",
    "It also says nothing about the option_text<->resp axis, which comes from the .sav's\n",
    "own value labels (1=never ... 5=always) and needs no inference.\n", sep = "")

pass <- lsap_identity && b_ok && c_ok && excess[1] > 0.10
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
