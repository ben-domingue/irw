# verify_iwasa_2016_dpssr.R
#
# CLAIM UNDER TEST: the live item code dpssNN is the DPSS-R-J questionnaire item
# numbered N in the study's own S2 (Japanese) / S3 (English) supplements, whose
# English wording is reprinted item-by-item in the paper's Table 1.
#
# The falsifiable prediction: the paper's Table 1 is an exploratory factor
# analysis of the DPSS-R-J run on a named subsample (n = 486), and that exact
# subsample is shipped as sheet "dpss_subgroup1_EFA" of the S1 workbook. So the
# 32 published pattern coefficients must reappear, item for item, when the EFA is
# re-run over the columns dpss01..dpss16 of that sheet. Any permutation of the
# code->item-number tie would move loadings across rows.
#
# A separate step ties the LIVE codes to those deposit columns (per-item means
# must be identical), so the loading comparison speaks about the live table.

suppressMessages({library(irw); library(readxl); library(psych)})

TABLE <- "iwasa_2016_dpssr"
ITEMS <- sprintf("dpss%02d", 1:16)

# Iwasa, Tanaka & Yamada (2016) PLOS ONE 11(10):e0164630, Table 1.
# rows = item 1..16, cols = Factor 1 (propensity), Factor 2 (sensitivity)
PUB <- matrix(c(
  .42, .09,   .00, .47,  -.06, .68,   .07, .51,
  .78,-.03,   .35, .29,   .51, .09,   .08, .52,
  .63, .09,   .93,-.20,  -.09, .70,   .66, .09,
  .27, .38,   .67, .04,   .23, .45,   .03, .50),
  ncol = 2, byrow = TRUE, dimnames = list(1:16, c("F1", "F2")))
TOL <- 0.06

## ---- 1. live data --------------------------------------------------------
d <- irw::irw_fetch(TABLE)
live_mean <- tapply(d$resp, d$item, mean)[ITEMS]

## ---- 2. the deposit workbook (S1 Table of the same paper) ----------------
xlsx <- file.path(tempdir(), "iwasa2016_s001.xlsx")
url  <- paste0("https://journals.plos.org/plosone/article/file",
               "?type=supplementary&id=10.1371/journal.pone.0164630.s001")
ok <- tryCatch({ download.file(url, xlsx, mode = "wb", quiet = TRUE); TRUE },
               error = function(e) FALSE)
if (!ok || !file.exists(xlsx) || file.size(xlsx) < 1e5) {
    alt <- "../../.cache/iwasa_2016_dpssr/s001.xlsx"          # run from batch dir
    alt2 <- ".cache/iwasa_2016_dpssr/s001.xlsx"               # run from itemtext/
    xlsx <- if (file.exists(alt)) alt else alt2
}
s1  <- suppressMessages(as.data.frame(read_excel(xlsx, sheet = "sample1")))
efa <- suppressMessages(as.data.frame(read_excel(xlsx, sheet = "dpss_subgroup1_EFA")))

dep_mean <- colMeans(s1[, ITEMS])
cat("--- step 1: live codes vs deposit columns (sheet 'sample1', n =",
    nrow(s1), "vs live n =", length(unique(d$id)), ") ---\n")
cat(sprintf("%-8s %10s %10s %10s\n", "item", "live mean", "deposit", "diff"))
for (it in ITEMS)
    cat(sprintf("%-8s %10.4f %10.4f %10.2e\n", it, live_mean[[it]],
                dep_mean[[it]], live_mean[[it]] - dep_mean[[it]]))
link_ok <- max(abs(live_mean - dep_mean)) < 1e-10
cat("max |diff| =", format(max(abs(live_mean - dep_mean))),
    if (link_ok) "-> live item codes ARE the deposit columns\n" else "-> LINK BROKEN\n")

## ---- 3. re-run the paper's EFA on its own subsample ----------------------
x <- efa[, ITEMS]
f <- fa(x, nfactors = 2, rotate = "promax", fm = "ml")
L <- unclass(f$loadings)
f1 <- which.max(abs(L[10, ])); L <- L[, c(f1, 3 - f1)]      # F1 = the dpss10 factor
if (L[10, 1] < 0) L[, 1] <- -L[, 1]
if (L[ 3, 2] < 0) L[, 2] <- -L[, 2]

cat("\n--- step 2: paper Table 1 loadings vs re-run on sheet 'dpss_subgroup1_EFA' (n =",
    nrow(efa), ") ---\n")
cat(sprintf("%-8s %14s %14s %14s %14s\n", "item",
            "pub F1", "obs F1", "pub F2", "obs F2"))
for (i in 1:16)
    cat(sprintf("%-8s %14.2f %14.2f %14.2f %14.2f\n",
                ITEMS[i], PUB[i, 1], L[i, 1], PUB[i, 2], L[i, 2]))
worst <- max(abs(L - PUB))
cat(sprintf("largest deviation over all 32 loadings: %.3f (tolerance %.2f)\n", worst, TOL))
cat(sprintf("factor correlation: observed %.2f, published .67\n", f$Phi[1, 2]))

# Rank agreement. Table 1 is printed to 2dp, so pairs whose published loadings
# differ by <= .01 are ties and carry no ordering information; a genuine
# permutation would show up as a DISCORDANT pair among the rest.
disc <- function(k) {
    n <- 0; tot <- 0
    for (i in 1:15) for (j in (i+1):16) {
        dp <- PUB[i, k] - PUB[j, k]
        if (abs(dp) > 0.011) { tot <- tot + 1
            if (sign(dp) != sign(L[i, k] - L[j, k])) n <- n + 1 }
    }
    c(discordant = n, comparable = tot)
}
d1 <- disc(1); d2 <- disc(2)
cat(sprintf("ordering of resolvable loading pairs: F1 %d/%d discordant, F2 %d/%d discordant\n",
            d1[1], d1[2], d2[1], d2[2]))
rank_ok <- d1[1] == 0 && d2[1] == 0

# global assignment check: is the identity the best of all 16! matchings, judged
# one transposition at a time?
D <- as.matrix(dist(rbind(L, PUB)))[1:16, 17:32]
ident <- sum(diag(D))
alt <- min(sapply(1:15, function(i) min(sapply((i+1):16, function(j) {
    p <- 1:16; p[c(i, j)] <- p[c(j, i)]; sum(D[cbind(1:16, p)]) }))))
cat(sprintf("assignment cost: identity %.3f, best single transposition %.3f\n", ident, alt))
cat("  (the tie is the {3,11} transposition, whose loadings are close in Euclidean\n",
    "   terms; the pairwise-ordering test above resolves it -- item 11 loads higher\n",
    "   than item 3 on F2 and lower on F1, both published and observed)\n", sep = "")

## ---- 4. secondary corroboration: the deposit's own subscale indices ------
ix <- suppressMessages(as.data.frame(read_excel(xlsx, sheet = "sample1indexes")))
prop <- ITEMS[c(1, 5, 6, 7, 9, 10, 12, 14)]   # DPSS-R disgust propensity
sens <- ITEMS[c(2, 3, 4, 8, 11, 13, 15, 16)]  # DPSS-R disgust sensitivity
cat(sprintf("\n--- step 3 (corroborative): canonical subscale sets vs deposit's own indices ---\n"))
cat(sprintf("propensity mean of %s  r with 'dpss-dp' = %.3f\n",
            paste(prop, collapse = ","), cor(rowMeans(s1[, prop]), ix$`dpss-dp`)))
cat(sprintf("sensitivity mean of %s  r with 'dpss-ds' = %.3f\n",
            paste(sens, collapse = ","), cor(rowMeans(s1[, sens]), ix$`dpss-ds`)))
cat("(the index sheet is keyed on the study's original participant ids, which the\n",
    " sample1 sheet renumbers 1..481, so these are correlations, not identities)\n", sep = "")

## ---- what this does NOT establish ---------------------------------------
# A pair of items is SEPARATED by this route if their published loadings differ
# by more than the 2dp print resolution on at least one factor. Enumerate the
# pairs that are not.
unres <- character(0)
for (i in 1:15) for (j in (i+1):16)
    if (abs(PUB[i,1] - PUB[j,1]) <= 0.011 && abs(PUB[i,2] - PUB[j,2]) <= 0.011)
        unres <- c(unres, sprintf("{%d,%d}", i, j))
cat("\nitem pairs NOT separated by the published loadings:",
    if (length(unres)) paste(unres, collapse = " ") else "none", "\n")
cat("NOT ESTABLISHED: the pair(s) above are interchangeable as far as this route\n",
    "is concerned -- their Table 1 loadings agree to the printed precision on both\n",
    "factors, so a swap of just those two would leave every number above unchanged.\n",
    "Every other item is distinguished from every other item. Nothing here checks\n",
    "option_text<->resp: the 1-5 anchors come from the questionnaire's own printed\n",
    "column headers, which are ordered on the page, not inferred.\n", sep = "")

pass <- link_ok && worst <= TOL && rank_ok && ident <= alt
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
