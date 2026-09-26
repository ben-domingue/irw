# verify_liem_2024_perceived_benefit_ema.R
#
# CLAIM UNDER TEST: live IRW item PB_EMAk holds the responses to column PB_EMAk of the
# study's S1 Data CSV, and the paper's Table 2 prints the wording of PB_EMAk beside
# that very code -- so item_text is tied to item by a label match, not by order.
#
# The falsifiable half is the first link. If two items' texts were swapped, the
# live per-item response-level count vector would no longer match the S1 column
# of the same name. The route distinguishes every item from every other item only
# if all four S1 count vectors are mutually distinct -- checked below, not assumed.
#
# Corroboration (printed, not decisive): Table 2's outer loadings
# (0.876 / 0.859 / 0.797 / 0.890) against each live item's correlation with the
# first principal component of the four items -- the rank order should agree.
#
# Source data: PLOS ONE 19(7):e0306616, S1 Data (CC BY 4.0),
#   https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0306616.s001&type=supplementary
# Processing script: data/liem_2024_env_stewardship.py (melts PB_EMA1..PB_EMA4 by name).

suppressMessages(library(irw))

TABLE <- "liem_2024_perceived_benefit_ema"
ITEMS <- paste0("PB_EMA", 1:4)
SRC   <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0306616.s001&type=supplementary"

# Paper Table 2, block "Perceived benefit of EMA implementation [94]", read from image asset .t002.
WORDING <- c(
 PB_EMA1 = "The implementation of environmental management accounting will enhance the legitimacy and competitiveness of your organization.",
 PB_EMA2 = "The implementation of environmental management accounting is advantageous for mitigating the environmental expenses and consequences of your organization, thereby bolstering its reputation.",
 PB_EMA3 = "Environmental management accounting facilitates the reduction of operational expenses and the identification of new opportunities for your organization.",
 PB_EMA4 = "The integration of environmental management accounting can furnish our organization with diverse data to facilitate informed decision-making and enhance overall performance.")
LOADING <- c(PB_EMA1 = 0.876, PB_EMA2 = 0.859, PB_EMA3 = 0.797, PB_EMA4 = 0.890)

src <- tryCatch(read.csv(SRC, stringsAsFactors = FALSE), error = function(e) NULL)
if (is.null(src) || !all(ITEMS %in% names(src))) {
    cat("Could not retrieve S1 Data from PLOS; cannot re-run the count comparison.\n")
    cat("VERDICT: FAIL\n"); quit(status = 0)
}

d <- as.data.frame(irw::irw_fetch(TABLE))

cnt <-function(x) as.integer(table(factor(x, levels = 1:5)))
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

csvp <- file.path(dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1])),
                  paste0(TABLE, "__items.csv"))
txt_ok <- TRUE
if (file.exists(csvp)) {
    it <- unique(read.csv(csvp, stringsAsFactors = FALSE)[, c("item", "item_text")])
    txt_ok <- all(sapply(ITEMS, function(i) identical(it$item_text[it$item == i], WORDING[[i]])))
    cat(sprintf("\nShipped item_text equals Table 2 wording printed beside each code: %s\n", txt_ok))
}
pass <- all(ok) && off_hits == 0 && best_off > 0 && txt_ok
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
