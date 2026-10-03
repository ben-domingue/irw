# verify_liem_2024_customer_pressure.R
#
# CLAIM UNDER TEST: live IRW item CuPk holds the responses to column CuPk of the
# study's S1 Data CSV, and the paper's Table 2 prints the wording of CuPk beside
# that very code -- so item_text is tied to item by a label match, not by order.
#
# The falsifiable half is the first link. If two items' texts were swapped, the
# live per-item response-level count vector would no longer match the S1 column
# of the same name. The route distinguishes every item from every other item only
# if all four S1 count vectors are mutually distinct -- checked below, not assumed.
#
# Corroboration (printed, not decisive): Table 2's outer loadings
# (0.680 / 0.852 / 0.809 / 0.758) against each live item's correlation with the
# first principal component of the four items -- the rank order should agree.
#
# Source data: PLOS ONE 19(7):e0306616, S1 Data (CC BY 4.0),
#   https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0306616.s001&type=supplementary
# Processing script: data/liem_2024_env_stewardship.py (melts CuP1..CuP4 by name).

suppressMessages(library(irw))

TABLE <- "liem_2024_customer_pressure"
ITEMS <- paste0("CuP", 1:4)
SRC   <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0306616.s001&type=supplementary"

# Paper Table 2, block "Customer pressure [91]", read from image asset .t002.
WORDING <- c(
 CuP1 = "The organization observes the impact of consumers' environmental concerns.",
 CuP2 = "The organization is under pressure to establish a green reputation.",
 CuP3 = "The company is under Customer pressure regarding environmentally friendly packaging.",
 CuP4 = "Customer contracts will be terminated if the company fails to comply with their environmental requirements")
LOADING <- c(CuP1 = 0.680, CuP2 = 0.852, CuP3 = 0.809, CuP4 = 0.758)

src <- tryCatch(read.csv(SRC, stringsAsFactors = FALSE), error = function(e) NULL)
if (is.null(src) || !all(ITEMS %in% names(src))) {
    cat("Could not retrieve S1 Data from PLOS; cannot re-run the count comparison.\n")
    cat("VERDICT: FAIL\n"); quit(status = 0)
}

d <- as.data.frame(irw::irw_fetch(TABLE))

cnt <- function(x) as.integer(table(factor(x, levels = 1:5)))
src_sig  <- t(sapply(ITEMS, function(i) cnt(src[[i]])))
live_sig <- t(sapply(ITEMS, function(i) cnt(d$resp[d$item == i])))

cat("Per-item response-level counts (resp 1/2/3/4/5): S1 Data column vs live IRW item\n\n")
cat(sprintf("%-6s %-22s %-22s %s\n", "item", "S1 column", "live IRW", "match"))
ok <- logical(length(ITEMS))
for (k in seq_along(ITEMS)) {
    ok[k] <- identical(src_sig[k, ], live_sig[k, ])
    cat(sprintf("%-6s %-22s %-22s %s\n", ITEMS[k],
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

# Corroboration: loading rank order.
w <- reshape(d[d$item %in% ITEMS, c("id", "item", "resp")], idvar = "id",
             timevar = "item", direction = "wide")
X <- as.matrix(w[, paste0("resp.", ITEMS)]); colnames(X) <- ITEMS
pc <- prcomp(X, scale. = TRUE)$x[, 1]
r  <- abs(cor(X, pc, use = "pairwise.complete.obs"))[, 1]
cat("\nTable 2 outer loading vs live |r(item, PC1)|:\n")
for (i in ITEMS) cat(sprintf("  %-5s published %.3f  live %.3f\n", i, LOADING[i], r[i]))
cat(sprintf("Spearman rank agreement: %.2f (corroboration only; PLS loadings are not PC1)\n",
            cor(LOADING, r[ITEMS], method = "spearman")))

cat("\nWhat this does NOT establish: option_text-to-resp is untested beyond the paper's\n",
    "own sentence '1 = strongly disagree and 5 = strongly agree' (points 2-4 ship\n",
    "blank); and nothing here shows the English is what Vietnamese respondents read.\n", sep = "")

pass <- all(ok) && off_hits == 0 && best_off > 0
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
