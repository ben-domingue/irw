# verify_carver_2017_puggs_pilot1_attitudes.R
#
# CLAIM UNDER TEST (the mapping, not the plumbing):
#   IRW item code "Qk" (k = 32..51) carries the attitude statement numbered k in
#   Carver et al. 2017 (PLoS ONE 10.1371/journal.pone.0169808) S3 Table (the
#   initial PUGGS questionnaire, used in the FIRST pilot) and S4 Table (the first
#   pilot's Code Book), and resp 1..4 = Strongly disagree / Disagree / Agree /
#   Strongly agree.
#
# Two falsifiable predictions, both computed from the study's own raw file
# (S5 Table, first pilot) -- no whole-table export:
#   (A) Applying the IRW processing script's filter (keep resp in 1..4; drop the
#       "don't know" code 5 and the missing code 99) to raw column Qk must
#       reproduce the LIVE per-item n for item Qk, for all 20 items.
#   (B) The Code Book assigns each attitude item a direction (its "att" secondary
#       code): 8 items are reverse-keyed (32,35,38,40,43,45,49,50) and 12 are
#       positively keyed. The sign of each item's correlation with the
#       direction-scored mean of the OTHER 19 items must match that assignment
#       for all 20 columns. A permutation that moved a statement across the
#       polarity boundary would break this.
#
# Live per-item n are hard-coded from irw::irw_table_sets(TABLE, per_item=TRUE)
# (server-side aggregate, no export) so this script needs no Redivis access.

TABLE <- "carver_2017_puggs_pilot1_attitudes"
S5 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0169808.s005")

LIVE_N <- c(Q32=193, Q33=194, Q34=193, Q35=193, Q36=187, Q37=202, Q38=196,
            Q39=200, Q40=193, Q41=195, Q42=192, Q43=185, Q44=193, Q45=193,
            Q46=189, Q47=200, Q48=200, Q49=196, Q50=189, Q51=192)
REVERSE <- c(32, 35, 38, 40, 43, 45, 49, 50)   # S4 Table Code Book, Section 4

cache <- file.path("..", "..", ".cache", TABLE, "s005.xlsx")
if (!file.exists(cache)) {
    cache <- tempfile(fileext = ".xlsx")
    utils::download.file(S5, cache, quiet = TRUE, mode = "wb")
}
suppressMessages(library(readxl))
d <- as.data.frame(readxl::read_excel(cache, sheet = "Sheet1"))

items <- paste0("Q", 32:51)
m <- sapply(items, function(i) suppressWarnings(as.numeric(d[[i]])))
m[!(m %in% 1:4)] <- NA   # drop "don't know" (5) and missing (99)

cat("(A) per-item n: raw S5 column vs live IRW table\n")
cat(sprintf("%-6s %8s %8s %6s\n", "item", "raw", "live", "ok"))
okA <- TRUE
for (i in items) {
    n <- sum(!is.na(m[, i]))
    hit <- n == LIVE_N[[i]]
    okA <- okA && hit
    cat(sprintf("%-6s %8d %8d %6s\n", i, n, LIVE_N[[i]], if (hit) "OK" else "MISMATCH"))
}
cat(sprintf("all 20 per-item n reproduce: %s\n\n", okA))

key <- ifelse(as.integer(sub("Q", "", items)) %in% REVERSE, -1, 1)
scored <- sweep(m, 2, key, "*")
cat("(B) polarity: item vs direction-scored mean of the other 19 items\n")
cat(sprintf("%-6s %10s %8s %6s\n", "item", "codebook", "r", "ok"))
okB <- TRUE
for (j in seq_along(items)) {
    rest <- rowMeans(scored[, -j], na.rm = TRUE)
    r <- cor(m[, j], rest, use = "pairwise.complete.obs")
    hit <- sign(r) == key[j]
    okB <- okB && hit
    cat(sprintf("%-6s %10s %8.3f %6s\n", items[j],
                if (key[j] < 0) "reverse" else "positive", r,
                if (hit) "OK" else "WRONG SIGN"))
}
cat(sprintf("all 20 signs match the Code Book: %s\n\n", okB))

cat("Establishes: the IRW item code is the raw file's own column name (A, exact\n",
    "counts for all 20), and each column's content sits on the side of the\n",
    "attitude scale the Code Book assigns to that number (B). Item identity is\n",
    "pinned outright by the Code Book labelling each statement with the very\n",
    "number the data column carries; (A)+(B) corroborate it.\n",
    "Does NOT establish: (B) alone cannot separate two items of the same polarity\n",
    "within the same topic block, and nothing here tests the four section_prompt\n",
    "assignments beyond the questionnaire's own printed block boundaries.\n", sep = "")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
