# verify_pang_2023_perceived_risk.R -- Step 5b, re-runnable mapping evidence.
#
# CLAIM UNDER TEST: data/pang_2023_nev_adoption.py assigns item_01..item_05
# POSITIONALLY (item_cols[10:15]) over the S1 workbook's columns Q15..Q19, whose
# headers ARE the shipped item text. A positional slice leaves no trace in the
# code, so this re-runs the derivation: it counts each of the FORTY item columns
# in the source workbook by response level and asks which one reproduces each
# live item's count vector. A swap of any two shipped item_texts breaks it.
#
# It also prints the demographic reconciliation that underpins the option-axis
# direction (1 = "Definitely agree"), which is an inference and is NOT part of
# the PASS/FAIL verdict.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "pang_2023_perceived_risk"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0285815.s001")
CACHE <- file.path(".cache", TABLE, "s001.xlsx")

if (!file.exists(CACHE)) {
    dir.create(dirname(CACHE), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(URL, CACHE, quiet = TRUE, mode = "wb")
}
src <- as.data.frame(readxl::read_excel(CACHE))
stopifnot(ncol(src) == 45L)
item_cols <- names(src)[6:45]                 # 40 item columns, Q5..Q44
PREDICTED <- item_cols[11:15]                 # R 1-based == python item_cols[10:15]

cv <- function(v) { v <- as.numeric(v); sapply(1:5, function(k) sum(v == k, na.rm = TRUE)) }
src_vecs <- sapply(item_cols, function(c) cv(src[[c]]))   # 5 x 40

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
codes <- sprintf("item_%02d", 1:5)
live_vecs <- sapply(codes, function(it) cv(d$resp[d$item == it]))

cat("Distinct count-vectors among the 40 source item columns: ",
    ncol(unique(t(src_vecs))), " of 40\n\n", sep = "")

ok <- TRUE
cat(sprintf("%-8s %-20s %-30s %s\n", "item", "live counts 1..5", "unique source column match", "predicted?"))
for (i in seq_along(codes)) {
    lv <- live_vecs[, i]
    hits <- item_cols[apply(src_vecs, 2, function(v) all(v == lv))]
    hit <- if (length(hits) == 1L) hits else paste0("<", length(hits), " matches>")
    good <- length(hits) == 1L && identical(hits, PREDICTED[i])
    ok <- ok && good
    cat(sprintf("%-8s %-20s %-30s %s\n", codes[i],
                paste(lv, collapse = ","), substr(hit, 1, 30), if (good) "YES" else "NO"))
}

cat("\nShipped item_text vs the matched source header (first 60 chars):\n")
shipped <- read.csv(file.path("itemtables", "batch_126",
                              paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
for (i in seq_along(codes)) {
    txt <- unique(shipped$item_text[shipped$item == codes[i]])
    cat(sprintf("  %s\n    shipped: %s\n    header : %s\n", codes[i],
                substr(txt, 1, 60), substr(sub("^[0-9]+\\.\\s*", "", PREDICTED[i]), 1, 60)))
}

cat("\n-- OPTION AXIS (context only, not in the verdict) --\n")
n <- nrow(src)
cat(sprintf("gender code 1 = %.1f%% (paper: 55.7%% men, 'Male' listed first)\n",
            100 * sum(src[[2]] == 1) / n))
cat(sprintf("age codes 1+2 = %.1f%% (paper: 88.5%% aged 20-40)\n",
            100 * sum(src[[3]] %in% 1:2) / n))
cat(sprintf("education codes 3+4 = %.1f%% (paper: 90.3%% bachelor's or above)\n",
            100 * sum(src[[4]] %in% 3:4) / n))

cat("\nWhat this does NOT establish: the option_text<->resp direction. The paper's\n",
    "Methods says 1 = strongly disagree while S2 File lists 'Definitely agree' first;\n",
    "the shipped direction follows S2 and the display-order coding evidenced above,\n",
    "which is an inference, not a value label. Nor does it tie the shipped English to\n",
    "any Chinese original, which no supplement supplies.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
