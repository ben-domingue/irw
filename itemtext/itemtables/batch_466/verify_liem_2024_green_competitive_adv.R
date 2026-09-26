# verify_liem_2024_green_competitive_adv.R
#
# CLAIM UNDER TEST: live IRW item GCAk holds the responses to column GCAk of the
# study's S1 Data CSV, and the paper's Table 2 prints the wording of GCAk beside
# that very code ("GCA1: In comparison to its market leaders, ...") -- so item_text
# is tied to item by a label match, not by order.
#
# The falsifiable half is the data link: if two items' texts were swapped the live
# per-item response-level count vector would no longer match the S1 column of the
# same name. The 4 S1 count vectors are mutually distinct, so the route
# distinguishes EVERY item from EVERY other item. A second check confirms the
# shipped __items.csv carries, for each code, the Table 2 wording printed next to
# that code (so the text-to-code half is also re-checked, not just asserted).
#
# Source: PLOS ONE 19(7):e0306616 (CC BY 4.0), S1 Data,
#   https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0306616.s001&type=supplementary
# Processing script: data/liem_2024_env_stewardship.py (melts GCA1..GCA4 by name).
# Route reused from itemtables/batch_078/verify_liem_2024_attitude_env.R.

suppressMessages(library(irw))

TABLE <- "liem_2024_green_competitive_adv"
ITEMS <- paste0("GCA", 1:4)
SRC   <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0306616.s001&type=supplementary"

# Paper Table 2 ("Construct reliability and validity"), block "Green competitive
# advantage [93]", read from image asset .t002 -- leading fragments, code-labelled.
TABLE2 <- c(
 GCA1 = "In comparison to its market leaders, the organization possesses a competitive advantage",
 GCA2 = "The company provides green products or services of a higher quality",
 GCA3 = "Green innovation and environmental R&D capabilities surpass",
 GCA4 = "Environmental management capabilities are superior")

here <- tryCatch(dirname(sys.frame(1)$ofile), error = function(e) NULL)
if (is.null(here)) {
    a <- commandArgs(FALSE); f <- sub("^--file=", "", a[grepl("^--file=", a)])
    here <- if (length(f)) dirname(f) else "."
}
csv <- file.path(here, paste0(TABLE, "__items.csv"))

src <- tryCatch(read.csv(SRC, stringsAsFactors = FALSE), error = function(e) NULL)
if (is.null(src) || !all(ITEMS %in% names(src))) {
    cat("Could not retrieve S1 Data from PLOS; cannot re-run the count comparison.\n")
    cat("VERDICT: FAIL\n"); quit(status = 0)
}
d <- irw::irw_fetch(TABLE)

cnt <- function(x) as.integer(table(factor(x, levels = 1:5)))
src_sig  <- t(sapply(ITEMS, function(i) cnt(src[[i]])))
live_sig <- t(sapply(ITEMS, function(i) cnt(d$resp[d$item == i])))

cat("Per-item response-level counts (resp 1/2/3/4/5): S1 Data column vs live IRW item\n\n")
cat(sprintf("%-6s %-22s %-22s %s\n", "item", "S1 column", "live IRW", "match"))
ok <- logical(length(ITEMS))
for (k in seq_along(ITEMS)) {
    ok[k] <- identical(src_sig[k, ], live_sig[k, ])
    cat(sprintf("%-6s %-22s %-22s %s\n", ITEMS[k], paste(src_sig[k, ], collapse = "/"),
                paste(live_sig[k, ], collapse = "/"), if (ok[k]) "OK" else "MISMATCH"))
}

n <- length(ITEMS)
D <- matrix(0L, n, n, dimnames = list(paste0("S1:", ITEMS), paste0("live:", ITEMS)))
for (a in 1:n) for (b in 1:n) D[a, b] <- sum(abs(src_sig[a, ] - live_sig[b, ]))
cat("\nL1 distance, S1 column (rows) vs live item (cols):\n"); print(D)
diag_hits <- sum(diag(D) == 0); off_hits <- sum(D == 0) - diag_hits
best_off <- min(D[row(D) != col(D)])
cat(sprintf("\nExact hits on diagonal: %d/%d; off-diagonal exact hits: %d; smallest off-diagonal L1: %d\n",
            diag_hits, n, off_hits, best_off))

# Text-to-code half: shipped item_text for each code begins with the Table 2 wording
# printed beside that code.
txt_ok <- NA
if (file.exists(csv)) {
    it <- read.csv(csv, stringsAsFactors = FALSE, encoding = "UTF-8")
    it <- unique(it[, c("item", "item_text")])
    txt_ok <- all(sapply(ITEMS, function(i) {
        s <- it$item_text[it$item == i]
        h <- length(s) == 1 && startsWith(s, TABLE2[[i]])
        cat(sprintf("%-6s shipped text starts with Table 2 wording for that code: %s\n", i, h)); h }))
} else cat("Shipped CSV not found beside this script; text-to-code check skipped.\n")

cat("\nWhat this does NOT establish: option_text vs resp is not tested (only the two\n",
    "anchors '1 = strongly disagree' and '5 = strongly agree' are published; 2-4 ship\n",
    "blank), and nothing here shows the English is what Vietnamese respondents read.\n", sep = "")

pass <- all(ok) && off_hits == 0 && best_off > 0 && !isFALSE(txt_ok)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
