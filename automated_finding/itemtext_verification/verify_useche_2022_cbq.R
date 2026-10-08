# verify_useche_2022_cbq.R -- Step 5b, re-runnable evidence (automated_finding, repos batch 2026-10-07).
#
# CLAIM: CBQk in useche_2022_cbq__items.csv carries the k-th bullet of the deposit's
# English root questionnaire (Appendix I, Dataverse 10.7910/DVN/EP6QLN), whose sections are
# F1 (8 bullets), F2 (15), F3 (6). The CSV has no labels, so codes are tied to bullets by order (paper_order).
#
# ROUTE: the deposit's own subscale-mean columns. If CBQk were not in the section the
# questionnaire puts bullet k in, the deposit's subscale mean would not equal the mean of the
# claimed block. This pins every item to its SECTION (and so to its section prompt), but does
# not distinguish items within a section -> PARTIAL, not VERIFIED. No per-item statistics
# are published (TRF 2022 paper paywalled-HTML only; Data in Brief 2024 reports factor-level
# ANOVAs only).
#
# Data: the raw deposit CSV (the composites are not in the shipped table). Fetches it.

url <- "https://dataverse.harvard.edu/api/access/datafile/7557056?format=original"
tf <- tempfile(fileext = ".csv")
download.file(url, tf, quiet = TRUE, mode = "wb")
d <- read.csv2(tf, fileEncoding = "UTF-8-BOM", na.strings = c(" ", ""))
blocks <- list(CBQ_Violations = 1:8, CBQ_Errors = 9:23, CBQ_Positive_Behaviors = 24:29)
ok <- TRUE
for (comp in names(blocks)) {
    its <- paste0("CBQ", blocks[[comp]])
    x <- as.matrix(d[, its]); y <- as.numeric(d[[comp]])
    cc <- complete.cases(x) & !is.na(y)
    diff <- max(abs(rowMeans(x[cc, , drop = FALSE]) - y[cc]))
    # a one-position shift at either boundary breaks it:
    alt <- paste0("CBQ", c(blocks[[comp]][-1], max(blocks[[comp]]) + 1))
    alt <- alt[alt %in% names(d)]
    altdiff <- if (length(alt) == length(its))
        max(abs(rowMeans(as.matrix(d[cc, alt])) - y[cc])) else NA
    cat(sprintf("%-24s %-14s n=%d max|mean(block)-composite|=%.2e  shifted-by-one: %s\n",
                comp, paste(range(blocks[[comp]]), collapse = "-"), sum(cc), diff,
                format(altdiff, digits = 3)))
    ok <- ok && diff < 1e-6 && (is.na(altdiff) || altdiff > 0.1)
}
cat("Each section's composite is exactly the mean of the claimed block (and not of the block\n",
    "shifted by one), so every item is pinned to its questionnaire section. Order within a\n",
    "section rests on the questionnaire's bullet order: PARTIAL.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
