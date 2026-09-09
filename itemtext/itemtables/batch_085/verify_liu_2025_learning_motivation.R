# verify_liu_2025_learning_motivation.R -- Step 5b, re-runnable mapping evidence.
#
# CLAIM UNDER TEST: each item_N in the IRW table carries the Chinese sentence
# shipped as item_text, i.e. that the positional assignment in
# data/liu_2025_meaning_learning.py (item_labels = enumerate(src_cols)) put
# question 15+N of the S1 Appendix workbook under item_N.
#
# Two independent checks, neither of which is a count-of-items check:
#   (A) STRING IDENTITY. The live IRW table carries its own `item_text` column
#       (the processing script preserved the original Chinese column header).
#       Compare it, code by code, against the shipped item_text. A swap of any
#       two items breaks this immediately. Decisive.
#   (B) ROUTE 9 / cell-for-cell count matching against the source deposit.
#       For each item, the 5-level response-count vector computed from the
#       PLOS S1 Appendix workbook column at the mapped position must equal the
#       live table's, and no two source columns may share a vector (otherwise
#       the route would not separate every item from every other).

suppressMessages(library(irw))
TABLE <- "liu_2025_learning_motivation"
ITEMS <- paste0("item_", 1:16)

ship <- read.csv(file.path(dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1])),
                           paste0(TABLE, "__items.csv")),
                 stringsAsFactors = FALSE, fileEncoding = "UTF-8")
ship <- unique(as.data.frame(ship[, c("item", "item_text")]))

d <- irw::irw_fetch(TABLE)
live <- unique(as.data.frame(d[, c("item", "item_text")]))
live$stripped <- trimws(sub("^[0-9]+、", "", live$item_text))

cat("=== (A) shipped item_text vs the live table's own item_text column ===\n")
okA <- TRUE
for (it in ITEMS) {
    a <- ship$item_text[match(it, ship$item)]; b <- live$stripped[match(it, live$item)]
    same <- identical(a, b)
    okA <- okA && same
    cat(sprintf("%-8s %-5s %s\n", it, if (same) "SAME" else "DIFF", substr(b, 1, 28)))
}
cat(sprintf("string identity: %d/16\n", sum(sapply(ITEMS, function(it) identical(ship$item_text[match(it, ship$item)], live$stripped[match(it, live$item)])))))
cat(sprintf("distinct shipped strings: %d/16 (a permutation would still be caught by the per-code compare above)\n",
            length(unique(ship$item_text))))

cat("\n=== (B) route 9: per-item response-level counts, source deposit vs live ===\n")
src_ok <- NA
raw_path <- file.path("..", "..", ".cache", TABLE, "s001.xlsx")
alt <- file.path("itemtext", ".cache", TABLE, "s001.xlsx")
if (!file.exists(raw_path) && file.exists(alt)) raw_path <- alt
if (!file.exists(raw_path) && requireNamespace("curl", quietly = TRUE)) {
    raw_path <- tempfile(fileext = ".xlsx")
    try(curl::curl_download(
        "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0330447.s001",
        raw_path, quiet = TRUE), silent = TRUE)
}
if (file.exists(raw_path) && requireNamespace("readxl", quietly = TRUE)) {
    x <- as.data.frame(readxl::read_excel(raw_path))
    qn <- suppressWarnings(as.integer(sub("、.*$", "", names(x))))
    srccols <- sapply(16:31, function(q) which(qn == q)[1])
    livemat <- table(factor(d$item, ITEMS), factor(d$resp, 1:5))
    srcmat <- t(sapply(srccols, function(j) {
        v <- suppressWarnings(as.numeric(x[[j]])); v <- v[!is.na(v) & v >= 1 & v <= 5]
        as.integer(table(factor(v, 1:5)))
    }))
    rownames(srcmat) <- ITEMS
    hits <- 0; offdiag <- 0
    for (i in 1:16) {
        cat(sprintf("%-8s live %-22s src %-22s %s\n", ITEMS[i],
                    paste(livemat[i, ], collapse = "/"), paste(srcmat[i, ], collapse = "/"),
                    if (all(livemat[i, ] == srcmat[i, ])) "match" else "MISMATCH"))
        if (all(livemat[i, ] == srcmat[i, ])) hits <- hits + 1
        for (k in 1:16) if (k != i && all(livemat[i, ] == srcmat[k, ])) offdiag <- offdiag + 1
    }
    l1 <- min(sapply(1:15, function(i) min(sapply((i + 1):16, function(k) sum(abs(srcmat[i, ] - srcmat[k, ]))))))
    cat(sprintf("diagonal matches %d/16, off-diagonal matches %d, smallest L1 distance between any two source vectors %d\n",
                hits, offdiag, l1))
    src_ok <- (hits == 16 && offdiag == 0 && l1 > 0)
} else {
    cat("source workbook unavailable offline -- check (B) skipped; (A) alone is decisive.\n")
    src_ok <- TRUE
}

cat("\nWhat this does NOT establish: nothing about the ENGLISH in item_text_translated,\n")
cat("which was matched to the Chinese by content from the paper's S2 Appendix (whose\n")
cat("printed order is a permutation of the administered order), nor the response anchors,\n")
cat("which are published in English only.\n")

cat(if (okA && isTRUE(src_ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
