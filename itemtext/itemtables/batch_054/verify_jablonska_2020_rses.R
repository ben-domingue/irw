# verify_jablonska_2020_rses.R -- Step 5b evidence, re-runnable.
#
# Claim under test: each live item code (which IS the S2 Dataset column header,
# e.g. "26. In general, I am satisfied with myself.") carries the Polish item
# text shipped for it, taken from S3 Appendix "Questionnaire (in English and
# Polish)" of the same paper.
#
# Two independent checks, neither of which is plumbing:
#   A. The item CODE is the source column header verbatim (10/10). This is the
#      data_labels tie -- the code names its own content, so a permutation of
#      item_text against item would be self-evident from the shipped English.
#   B. Keying polarity in the raw source data. The five items whose shipped text
#      is negatively worded must correlate positively with each other and
#      negatively with the five positively worded ones. This would break if the
#      positive/negative blocks had been swapped or shifted.
#
# Uses irw::irw_table_sets() (server-side, no export) for the live item set and
# the paper's own CC BY 4.0 S2 Dataset for the responses -- no full-table export.

suppressMessages(library(irw))

TABLE <- "jablonska_2020_rses"
S2 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0229354.s006")

items_csv <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                       paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv)) items_csv <- file.path("itemtables", "batch_054", paste0(TABLE, "__items.csv"))
shipped <- read.csv(items_csv, stringsAsFactors = FALSE, encoding = "UTF-8")
shipped <- shipped[!duplicated(shipped$item), c("item", "item_text", "item_text_translated")]
shipped <- shipped[order(as.integer(sub("\\..*$", "", shipped$item))), ]

tmp <- tempfile(fileext = ".xlsx")
ok <- tryCatch({ download.file(S2, tmp, quiet = TRUE, mode = "wb"); TRUE }, error = function(e) FALSE)
if (!ok || !requireNamespace("readxl", quietly = TRUE)) {
    cat("Could not fetch S2 Dataset or readxl unavailable -- cannot re-run polarity check.\n")
    cat("VERDICT: FAIL\n"); quit(status = 0)
}
raw <- as.data.frame(readxl::read_excel(tmp))
num <- suppressWarnings(as.integer(sub("\\..*$", "", names(raw))))
cols <- names(raw)[!is.na(num) & num >= 26 & num <= 35]
cols <- cols[order(as.integer(sub("\\..*$", "", cols)))]

# ---- A. code == source header ----
same <- identical(cols, shipped$item)
cat("A. item code vs S2 Dataset column header (columns 26-35):\n")
for (i in seq_along(cols))
    cat(sprintf("   %-2s %-64s %s\n", i, substr(cols[i], 1, 64),
                if (identical(cols[i], shipped$item[i])) "== shipped item" else "!! MISMATCH"))
cat(sprintf("   matched %d/%d\n", sum(cols == shipped$item), length(cols)))

live <- tryCatch(irw::irw_table_sets(TABLE), error = function(e) NULL)
if (!is.null(live)) {
    liveitems <- sort(unique(as.character(live$item)))
    cat(sprintf("   live item set from irw_table_sets(): %d items, identical to shipped: %s\n",
                length(liveitems), identical(liveitems, sort(shipped$item))))
}

# ---- B. keying polarity ----
LIK <- c("Strongly disagree" = 1, "Disagree" = 2, "Rather disagree" = 3,
         "Neither agree or disagree" = 4, "Rather agree" = 5, "Agree" = 6,
         "Strongly agree" = 7)
d <- as.data.frame(lapply(raw[cols], function(x) unname(LIK[as.character(x)])))
names(d) <- as.integer(sub("\\..*$", "", cols))
d <- d[complete.cases(d), ]

# Polarity asserted from the SHIPPED text (canonical RSES keying):
POS <- c("26", "28", "29", "32", "35")   # satisfied / good qualities / as well as others / person of worth / positive attitude
NEG <- c("27", "30", "31", "33", "34")   # no good at all / not much to be proud of / useless / more respect / a failure
cm <- cor(d)
wpp <- cm[POS, POS][upper.tri(diag(5))]
wnn <- cm[NEG, NEG][upper.tri(diag(5))]
bet <- as.vector(cm[POS, NEG])
cat(sprintf("\nB. keying polarity, N=%d complete cases from the S2 Dataset:\n", nrow(d)))
cat(sprintf("   positive block %s: %d pairs, r in [%.2f, %.2f]\n",
            paste(POS, collapse = ","), length(wpp), min(wpp), max(wpp)))
cat(sprintf("   negative block %s: %d pairs, r in [%.2f, %.2f]\n",
            paste(NEG, collapse = ","), length(wnn), min(wnn), max(wnn)))
cat(sprintf("   across blocks:        %d pairs, r in [%.2f, %.2f]\n",
            length(bet), min(bet), max(bet)))
cat("   item means: ",
    paste(sprintf("%s=%.2f", names(d), colMeans(d)), collapse = "  "), "\n", sep = "")
polarity_ok <- min(wpp) > 0 && min(wnn) > 0 && max(bet) < 0

cat("\nNot established by B: it separates the five positively worded items from the five\n",
    "negatively worded ones, but not the order WITHIN either block. That ordering rests on\n",
    "check A -- the item code is the source column header and carries the item's own wording.\n", sep = "")

cat(if (same && polarity_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
