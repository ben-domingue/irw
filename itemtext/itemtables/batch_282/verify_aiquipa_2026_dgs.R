# verify_aiquipa_2026_dgs.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: item code COD<i> in the IRW table carries the text printed
# as item <i> in the deposit's Appendix (Supplementary Material 3), i.e. the
# "Adapted version (final)" Spanish column.
#
# ROUTE 3 (a total published by the source). Sheet 2 of the deposit workbook
# carries a scored column `Codicia` alongside COD1..COD7. It is NOT the 7-item
# sum; it is the sum of the FIVE items the Appendix prints in bold as "the items
# that make up the Peruvian version of the DGS" -- appendix items 1, 2, 3, 4 and
# 7. If COD numbering were permuted relative to the Appendix numbering, the
# subset of COD columns reproducing `Codicia` would not be {1,2,3,4,7}.
# All 21 five-item subsets are tested; exactly one reproduces the column.
#
# Supporting check: per-item means in the live IRW table are compared against the
# same COD columns in the raw workbook, which ties the shipped codes to the
# deposit columns the subset test was run on.
#
# WHAT THIS DOES NOT ESTABLISH: it separates {COD1,COD2,COD3,COD4,COD7} from
# {COD5,COD6} and nothing finer. A permutation inside either group would survive
# it. Hence the recorded status is PARTIAL, not VERIFIED.

suppressMessages({library(readxl); library(irw)})

TABLE <- "aiquipa_2026_dgs"
URL <- paste0("https://data.mendeley.com/public-files/datasets/w5f55333p4/",
              "files/278fbad0-9bbc-419f-a047-a5b4ee6c34da/file_downloaded")
CACHE <- file.path(".cache", TABLE, "Supplementary Material 1. Data base.xlsx")
BOLD <- c(1, 2, 3, 4, 7)   # bold rows of the Appendix "Adapted version (final)" column

path <- if (file.exists(CACHE)) CACHE else {
    tmp <- tempfile(fileext = ".xlsx")
    download.file(URL, tmp, mode = "wb", quiet = TRUE)
    tmp
}
d <- as.data.frame(read_excel(path, sheet = 2))
its <- paste0("COD", 1:7)
stopifnot(all(c(its, "Codicia") %in% names(d)))
cat("raw sheet 2 rows:", nrow(d), "\n\n")

cat("=== Which 5-item COD subset reproduces the deposit's `Codicia` total? ===\n")
combos <- combn(1:7, 5, simplify = FALSE)
hits <- integer(0)
for (k in seq_along(combos)) {
    s <- rowSums(d[, paste0("COD", combos[[k]]), drop = FALSE])
    n <- sum(s == d$Codicia)
    if (n > 0) cat(sprintf("  {%s}: %d / %d rows match\n",
                           paste(combos[[k]], collapse = ","), n, nrow(d)))
    if (n == nrow(d)) hits <- c(hits, k)
}
exact <- length(hits) == 1 && setequal(combos[[hits]], BOLD)
cat(sprintf("\nsubsets matching every row: %d; appendix bold set {%s}: %s\n\n",
            length(hits), paste(BOLD, collapse = ","),
            if (exact) "MATCH" else "MISMATCH"))

cat("=== Live IRW per-item means vs the same raw COD columns ===\n")
live <- irw::irw_fetch(TABLE)
lm_ <- tapply(live$resp, live$item, mean)[its]
s1 <- as.data.frame(read_excel(path, sheet = 1))
pooled <- rbind(s1[, its], d[, its])
rm_ <- colMeans(pooled, na.rm = TRUE)[its]
cat(sprintf("%-6s %8s %8s %8s\n", "item", "raw", "live", "diff"))
for (i in its) cat(sprintf("%-6s %8.4f %8.4f %8.4f\n", i, rm_[i], lm_[i], lm_[i] - rm_[i]))
worst <- max(abs(lm_ - rm_))
cat(sprintf("largest deviation: %.2e\n\n", worst))

cat("Note: this pins the five-item Peruvian final set against the two dropped\n",
    "items only. It does not order items within either group.\n", sep = "")
cat(if (exact && worst < 1e-8) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
