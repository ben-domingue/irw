# verify_yang_2023_emotional_eating_cesd.R -- Step 5b mapping evidence.
#
# CLAIM UNDER TEST. data/yang_2023_emotional_eating.py assigns the item codes
# POSITIONALLY: cesd_cols = ["I don't want to eat. I have a bad appetite"] +
# [c for c in cols if c.startswith("@11")], then CESD_{i+1} = cesd_cols[i].
# The code therefore keeps no trace of the source column header, and the shipped
# item_text is that header. This script rebuilds the assignment from the source
# workbook and asks whether the live IRW table could have come from any OTHER
# assignment of those 20 columns to those 20 codes.
#
# It also re-derives the reverse-scored set from the deposit's own precomputed
# CESD total column, which is what identifies CESD_2 (whose source header is the
# block instruction, not item wording) as canonical CES-D item 1.
#
# Fetches the live table (small: 20 items x 494 respondents) and the PLOS S1
# workbook (sha256 8a2cc778ce20aafd8d9dd1a463c54f7e211b83e48b59a9c5cec3d997b62f1f21).

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "yang_2023_emotional_eating_cesd"
SI <- paste0("https://journals.plos.org/plosone/article/file?",
             "type=supplementary&id=10.1371/journal.pone.0280701.s001")

cache <- file.path(".cache", TABLE, "s001.xlsx")
if (!file.exists(cache)) {
    dir.create(dirname(cache), recursive = TRUE, showWarnings = FALSE)
    download.file(SI, cache, mode = "wb", quiet = TRUE)
}
cat("source workbook sha256: ",
    as.character(tools::md5sum(cache)), " (md5)\n", sep = "")

raw <- suppressMessages(as.data.frame(read_excel(cache)))
cols <- names(raw)
# Reproduce the processing script's column selection, in its order.
cesd_cols <- c(cols[29], cols[grepl("^@11", cols)])   # R is 1-based; py cols[28]
stopifnot(length(cesd_cols) == 20)
codes <- paste0("CESD_", 1:20)

cat("\n=== A. Source column -> item code, as the script assigns it ===\n")
for (i in 1:20)
    cat(sprintf("%-9s <- col %2d  %s\n", codes[i], match(cesd_cols[i], cols),
                substr(cesd_cols[i], 1, 58)))

## ---- B. Does the claimed assignment reproduce the live table exactly? ----
d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = codes), factor(d$resp, levels = 1:4))

src <- sapply(cesd_cols, function(cc) {
    v <- suppressWarnings(as.numeric(raw[[cc]]))
    v <- v[!is.na(v) & v >= 1 & v <= 4]
    tabulate(v, nbins = 4)
})                      # 4 x 20, columns in script order
dimnames(src) <- list(1:4, codes)

cat("\n=== B. Per-item response-frequency match (live vs rebuilt from source) ===\n")
cat(sprintf("%-9s %-22s %-22s %s\n", "item", "live n(1,2,3,4)", "source n(1,2,3,4)", "ok"))
ok_all <- TRUE
for (i in 1:20) {
    l <- as.integer(live[i, ]); s <- as.integer(src[, i])
    ok <- identical(l, s); ok_all <- ok_all && ok
    cat(sprintf("%-9s %-22s %-22s %s\n", codes[i],
                paste(l, collapse = ","), paste(s, collapse = ","),
                if (ok) "yes" else "NO"))
}
cat("all 20 reproduced exactly: ", ok_all, "\n", sep = "")

## ---- C. Is the claimed assignment UNIQUE? ----
# For each code, how many of the 20 source columns reproduce its live counts?
cat("\n=== C. Uniqueness: rival source columns matching each code's live counts ===\n")
rivals <- integer(20)
for (i in 1:20) {
    l <- as.integer(live[i, ])
    rivals[i] <- sum(apply(src, 2, function(s) identical(as.integer(s), l)))
}
for (i in 1:20) cat(sprintf("%-9s candidate columns: %d\n", codes[i], rivals[i]))
uniq <- all(rivals == 1)
cat("every code matched by exactly one source column: ", uniq, "\n", sep = "")

## ---- D. Which columns are reverse-scored, from the deposit's own total ----
# The workbook carries a precomputed 'CESD' total. Recoding 1-4 to 0-3 and
# reversing the four canonical positive-affect items must reproduce it.
X <- sapply(cesd_cols, function(cc) suppressWarnings(as.numeric(raw[[cc]])))
colnames(X) <- codes
tot <- suppressWarnings(as.numeric(raw[["CESD"]]))
score <- function(rev_idx) {
    Y <- X
    Y[, rev_idx] <- 5 - Y[, rev_idx]
    rowSums(Y) - 20
}
claim <- c(4, 8, 12, 16)      # CESD_4, _8, _12, _16 = canonical CES-D 4,8,12,16
n_ok <- sum(score(claim) == tot, na.rm = TRUE)
cat("\n=== D. Deposit's own precomputed CESD total ===\n")
cat(sprintf("reversing {%s} and recoding 1-4 -> 0-3 reproduces the total for %d / %d respondents\n",
            paste(codes[claim], collapse = ", "), n_ok, nrow(X)))
cat(sprintf("no reversal at all reproduces it for %d / %d\n",
            sum(rowSums(X) - 20 == tot, na.rm = TRUE), nrow(X)))
# Every single-item swap of the reverse set, for contrast.
alt_best <- 0
for (drop in claim) for (add in setdiff(1:20, claim)) {
    a <- sum(score(c(setdiff(claim, drop), add)) == tot, na.rm = TRUE)
    if (a > alt_best) alt_best <- a
}
cat(sprintf("best rival reverse-set (one item swapped) reproduces it for %d / %d\n",
            alt_best, nrow(X)))
d_ok <- n_ok == nrow(X) && alt_best < nrow(X)

cat("\nWHAT THIS DOES NOT ESTABLISH.\n",
    "B and C tie each item CODE to a source COLUMN uniquely, and 19 of the 20\n",
    "shipped item_text strings are that column's own header, verbatim. CESD_2 is\n",
    "the exception: its source header is the block instruction ('@11, there are 20\n",
    "statements...'), so its wording is NOT transcribed from the source. It is\n",
    "canonical CES-D item 1, assigned by elimination -- the other 19 headers\n",
    "reproduce canonical CES-D items 2-20 in exact order, and D confirms the block\n",
    "is a complete, canonically ordered 20-item CES-D by recovering the\n",
    "{4,8,12,16} reverse set from the deposit's own total. Strong, but an\n",
    "inference rather than a transcription.\n", sep = "")

cat(if (ok_all && uniq && d_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
