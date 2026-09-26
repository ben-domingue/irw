# verify_liem_2024_perceived_benefit_cp.R
#
# CLAIM UNDER TEST: live IRW item PB_CPk holds the responses to column PB_CPk of
# the study's S1 Data CSV, and the paper's Table 2 prints the wording of PB_CPk
# beside that very code -- so item_text is tied to item by a label match, not by
# order.
#
# The falsifiable half is the first link. If two items' texts/codes were swapped,
# the live per-item response-level count vector would no longer match the S1
# column of the same name. The script also checks that all 9 S1 count vectors are
# mutually distinct, i.e. that the route distinguishes EVERY item from EVERY other.
#
# Second, independent route (corroboration only, not part of the verdict): the
# PLS-SEM outer loadings printed beside each item in Table 2, approximated by each
# item's |correlation| with the first principal component of the 9 live items.
#
# Source data: PLOS ONE 19(7):e0306616, S1 Data (CC BY 4.0),
#   https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0306616.s001&type=supplementary
# Processing script: data/liem_2024_env_stewardship.py (melts PB_CP1..PB_CP9 by name).

suppressMessages(library(irw))

TABLE <- "liem_2024_perceived_benefit_cp"
ITEMS <- paste0("PB_CP", 1:9)
SRC   <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0306616.s001&type=supplementary"

# Table 2 block "Perceived benefit of Cleaner production [75]", image asset .t002.
LOADING <- c(PB_CP1 = 0.867, PB_CP2 = 0.822, PB_CP3 = 0.712, PB_CP4 = 0.825,
             PB_CP5 = 0.852, PB_CP6 = 0.713, PB_CP7 = 0.770, PB_CP8 = 0.745,
             PB_CP9 = 0.896)

src <- tryCatch(read.csv(SRC, stringsAsFactors = FALSE), error = function(e) NULL)
if (is.null(src) || !all(ITEMS %in% names(src))) {
    cat("Could not retrieve S1 Data from PLOS; cannot re-run the count comparison.\n")
    cat("VERDICT: FAIL\n"); quit(status = 0)
}

d <- as.data.frame(irw::irw_fetch(TABLE))

cnt <- function(x) as.integer(table(factor(x, levels = 1:5)))
src_sig  <- t(sapply(ITEMS, function(i) cnt(src[[i]])))
live_sig <- t(sapply(ITEMS, function(i) cnt(d$resp[d$item == i])))

cat("Route 9 -- per-item response-level counts (resp 1/2/3/4/5): S1 column vs live IRW item\n\n")
cat(sprintf("%-7s %-22s %-22s %s\n", "item", "S1 column", "live IRW", "match"))
ok <- logical(length(ITEMS))
for (k in seq_along(ITEMS)) {
    ok[k] <- identical(src_sig[k, ], live_sig[k, ])
    cat(sprintf("%-7s %-22s %-22s %s\n", ITEMS[k],
                paste(src_sig[k, ], collapse = "/"),
                paste(live_sig[k, ], collapse = "/"),
                if (ok[k]) "OK" else "MISMATCH"))
}

n <- length(ITEMS)
D <- matrix(0L, n, n, dimnames = list(paste0("S1:", ITEMS), paste0("live:", ITEMS)))
for (a in 1:n) for (b in 1:n) D[a, b] <- sum(abs(src_sig[a, ] - live_sig[b, ]))
cat("\nL1 distance, S1 column (rows) vs live item (cols):\n"); print(D)
diag_hits <- sum(diag(D) == 0)
off_hits  <- sum(D == 0) - diag_hits
best_off  <- min(D[row(D) != col(D)])
cat(sprintf("\nExact-count hits on the diagonal: %d/%d; off-diagonal exact hits: %d\n",
            diag_hits, n, off_hits))
cat(sprintf("Smallest off-diagonal L1 distance: %d (0 would mean two items are indistinguishable)\n",
            best_off))

# Corroboration: loadings.
w <- reshape(d[d$item %in% ITEMS, c("id", "item", "resp")], idvar = "id",
             timevar = "item", direction = "wide")
X <- as.matrix(w[, paste0("resp.", ITEMS)]); colnames(X) <- ITEMS
X <- X[complete.cases(X), ]
pc <- prcomp(X, scale. = TRUE)$x[, 1]
r  <- abs(cor(X, pc))[, 1]
cat("\nCorroboration -- published PLS outer loading vs |r(item, PC1)| on live data:\n")
for (k in ITEMS) cat(sprintf("%-7s published %.3f   live %.3f\n", k, LOADING[k], r[k]))
cat(sprintf("Spearman(published, live) = %.2f\n", cor(LOADING, r, method = "spearman")))
cat("PLS outer loadings depend on the structural model, which PC1 does not reproduce,\n",
    "so this is corroboration of the pattern only; it cannot separate near-tied items\n",
    "(published PB_CP3 0.712 vs PB_CP6 0.713). The label match + route 9 pin every item.\n", sep = "")

cat("\nWhat this does NOT establish: option_text is not tested against resp -- only the\n",
    "two extreme anchors are published ('1 = strongly disagree and 5 = strongly agree')\n",
    "and points 2-4 ship blank. Nor does it show the English shipped is what the\n",
    "(presumably Vietnamese-speaking) respondents read.\n", sep = "")

pass <- all(ok) && off_hits == 0 && best_off > 0
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
