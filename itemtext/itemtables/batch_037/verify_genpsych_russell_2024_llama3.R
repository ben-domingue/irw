# verify_genpsych_russell_2024_llama3.R
#
# mapping_basis is data_labels, so this table is formally exempt from Step 5b:
# the source is a Qualtrics export whose row 1 holds the column names
# (items_1..items_30 -- the very codes the IRW table uses) and row 2 holds the
# administered question text for that same column. Code and text are tied at the
# source with no inference. This script re-runs that tie anyway, plus an
# independent structural fingerprint, so the claim is reproducible.
#
# Two checks, neither of which is plumbing:
#   A. For every column, the shipped item_text equals row 2 of the source file at
#      that column, minus the shared Qualtrics matrix stem. A swap of any two
#      items' text breaks this.
#   B. Per-item non-missing n in the live IRW table equals the per-item count of
#      non-blank cells in that source column. This is a structural fingerprint of
#      column identity that does not depend on the header at all -- it would break
#      if the processing script had shifted the column range.
#
# Both use irw::irw_table_sets() (server-side aggregate), never irw_fetch(): no
# export is spent.

suppressMessages({library(irw); library(readxl)})

TABLE   <- "genpsych_russell_2024_llama3"
VO      <- "79d2c8bf12c24393863d60c4143f8a0e"
# /Empirical Validation/llama-3/data/llama-3_deID.xlsx on https://osf.io/zcytb/
OSF_URL <- paste0("https://files.osf.io/v1/resources/zcytb/providers/osfstorage/",
                  "68b130268fdb03009a780c04?view_only=", VO)
CACHE   <- if (dir.exists(".cache")) file.path(".cache", TABLE, "llama-3_deID.xlsx") else file.path(tempdir(), "llama-3_deID.xlsx")
# Resolve the items CSV whether run from itemtext/ or from the batch directory.
CAND <- c(paste0(TABLE, "__items.csv"),
          file.path("itemtables", "batch_037", paste0(TABLE, "__items.csv")),
          file.path("..", "..", "itemtables", "batch_037", paste0(TABLE, "__items.csv")))
ITEMS <- CAND[file.exists(CAND)][1]
if (is.na(ITEMS)) stop("cannot locate ", TABLE, "__items.csv")

if (!file.exists(CACHE)) {
    dir.create(dirname(CACHE), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(OSF_URL, CACHE, mode = "wb", quiet = TRUE)
}

raw <- suppressMessages(readxl::read_xlsx(CACHE, col_names = FALSE))
hdr <- as.character(unlist(raw[1, ]))
qtx <- as.character(unlist(raw[2, ]))
cols <- which(grepl("^items_", hdr))
stopifnot(length(cols) == 30)

STEM <- paste0("The following questions ask about your personality. You should respond ",
               "with the extent to which you agree with each statement based on how you ",
               "act, think, and feel on average. There is no right or wrong answers, so ",
               "answer honestly. - ")
src_text <- substring(qtx[cols], nchar(STEM) + 1)
names(src_text) <- hdr[cols]

it <- utils::read.csv(ITEMS, stringsAsFactors = FALSE)
ship <- tapply(it$item_text, it$item, function(x) unique(x)[1])

## ---- Check A: shipped text vs source question row, per column ----
cat("== Check A: shipped item_text vs source Qualtrics question row ==\n")
badA <- 0
for (i in names(src_text)) {
    ok <- identical(trimws(ship[[i]]), trimws(src_text[[i]]))
    if (!ok) badA <- badA + 1
    cat(sprintf("%-9s %-5s src: %s\n", i, if (ok) "OK" else "DIFF",
                substr(src_text[[i]], 1, 62)))
    if (!ok) cat(sprintf("%-9s %-5s shp: %s\n", i, "", substr(ship[[i]], 1, 62)))
}
cat(sprintf("mismatched item_text cells: %d of 30\n\n", badA))

## ---- Check B: per-item n fingerprint ----
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live_n <- setNames(s$per_item$n, s$per_item$item)
src_n <- sapply(cols, function(j) sum(!is.na(raw[[j]][-(1:2)])))
names(src_n) <- hdr[cols]

cat("== Check B: per-item non-missing n, source column vs live IRW table ==\n")
cat(sprintf("%-9s %8s %8s %6s\n", "item", "source", "live", "diff"))
badB <- 0
for (i in names(src_n)) {
    d <- as.integer(live_n[[i]]) - as.integer(src_n[[i]])
    if (d != 0) badB <- badB + 1
    cat(sprintf("%-9s %8d %8d %6d\n", i, src_n[[i]], live_n[[i]], d))
}
cat(sprintf("per-item n mismatches: %d of 30\n", badB))
cat(sprintf("total live rows %s vs 30 items x %d source respondents = %d\n\n",
            format(s$n_rows, big.mark = ","), nrow(raw) - 2, 30 * (nrow(raw) - 2)))

cat("Note: Check B's counts are not all distinct (e.g. 990 occurs three times), so\n",
    "the fingerprint alone would not separate every pair of items. Check A is what\n",
    "pins each item individually, and it is a source-level tie, not an inference.\n",
    "Neither check speaks to option_text<->resp: that mapping comes from\n",
    "data/genpsych_russell_2024.r's explicit likert_mapping.\n", sep = "")

cat(if (badA == 0 && badB == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
