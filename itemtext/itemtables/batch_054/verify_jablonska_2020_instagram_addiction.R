# verify_jablonska_2020_instagram_addiction.R
#
# Step 5b route 9 (response-frequency matching) plus the item-code identity check.
#
# The claim under test: the shipped Polish item_text / option_text rows are pinned
# to the live `item` codes and `resp` integers by the study's own S2 Dataset
# (10.1371/journal.pone.0229354.s006), whose column HEADERS are the live item codes
# verbatim and whose CELLS are English anchor label strings that
# data/jablonska_2020_instagram.py recodes 1..7 via LIKERT_MAP.
#
# What would break if the mapping were wrong: swap any two items' text, or flip /
# permute the 1..7 anchor order, and the item x resp count matrix below stops
# matching cell for cell.
#
# irw_fetch() is used deliberately here: this table is 9,740 rows (974 x 10), so
# the export is negligible against the account-wide 200GB/30-day cap, and no
# server-side route supplies an item x resp cross-tabulation.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "jablonska_2020_instagram_addiction"
S2 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0229354.s006"

# LIKERT_MAP, copied verbatim from data/jablonska_2020_instagram.py.
LIKERT <- c("Strongly disagree" = 1, "Disagree" = 2, "Rather disagree" = 3,
            "Neither agree or disagree" = 4, "Rather agree" = 5,
            "Agree" = 6, "Strongly agree" = 7)

tmp <- tempfile(fileext = ".xlsx")
download.file(S2, tmp, mode = "wb", quiet = TRUE)
raw <- readxl::read_excel(tmp)

items_csv <- read.csv(file.path(dirname(sub("^--file=", "",
    commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])),
    paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
shipped <- unique(items_csv$item)

# --- Check A: the live item codes ARE source column headers, verbatim ---
hdr <- names(raw)
inhdr <- shipped %in% hdr
cat("=== A. item code == S2 Dataset column header (verbatim) ===\n")
for (s in shipped) cat(sprintf("  %-5s %s\n", if (s %in% hdr) "OK" else "MISS", s))
cat(sprintf("matched %d/%d\n\n", sum(inhdr), length(shipped)))

# --- Check B: item x resp counts, source labels vs live integers ---
d <- irw::irw_fetch(TABLE)
cat("=== B. item x resp counts: S2 label counts vs live resp counts ===\n")
cat(sprintf("%-62s %s\n", "item (truncated)", "1 2 3 4 5 6 7  src / live"))
ok <- TRUE
for (s in shipped) {
    src <- sapply(names(LIKERT), function(lb) sum(raw[[s]] == lb, na.rm = TRUE))
    src <- as.integer(src[order(LIKERT)])                       # index = resp 1..7
    liv <- as.integer(table(factor(d$resp[d$item == s], levels = 1:7)))
    cat(sprintf("%-62s src %s\n", substr(s, 1, 60), paste(src, collapse = " ")))
    cat(sprintf("%-62s liv %s  %s\n", "", paste(liv, collapse = " "),
                if (identical(src, liv)) "MATCH" else "*** MISMATCH ***"))
    if (!identical(src, liv)) ok <- FALSE
}

# Falsification control: does the count vector actually distinguish the items?
mat <- t(sapply(shipped, function(s)
    as.integer(table(factor(d$resp[d$item == s], levels = 1:7)))))
cat(sprintf("\ndistinct count vectors across the 10 items: %d/10 (a permutation of\n",
            nrow(unique(mat))))
cat("item_text would therefore be detected by check B)\n")

cat("\nWhat this does NOT establish: the Polish option wording in `option_text`.\n")
cat("Check B pins resp 1..7 to the S2 Dataset's ENGLISH anchor labels only. The\n")
cat("Polish anchors shipped come from S3 Appendix (s004), which lists the same 7\n")
cat("anchors in descending order beside its English version; their alignment to\n")
cat("resp is an ordinal inference from that document, not a measured quantity.\n")

cat(if (ok && all(inhdr)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
