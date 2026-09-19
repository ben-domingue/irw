# verify_yang2026_efl_learner_perspective.R
#
# CLAIM UNDER TEST
#   The processing script (data/yang2026_efl_learner_perspective.py) assigns item
#   codes POSITIONALLY: item_NN := spreadsheet column (NN + 6) of the study's own
#   deposit, pone.0340479.s002.xlsx. Every item_text shipped is the label in row 2
#   (the header row) of that column. If any two items' texts were swapped, the
#   shipped text would no longer describe the column whose responses the live
#   table stores under that code.
#
# EVIDENCE 1 (decisive, per item, per respondent)
#   Re-run the mapping from the raw file and compare CELL BY CELL against the live
#   table, joined on id (= the file's "Serial No.") and item. 154 ids x 36 items =
#   5544 cells. A shifted, permuted or swapped assignment breaks this immediately,
#   including for items whose marginals happen to tie (item_03/item_04 are both
#   114/40; item_15/item_16 are both 53/101) -- the per-respondent join separates
#   those, marginals alone do not.
#
# EVIDENCE 2 (independent, from the paper, and fixes the SCALE DIRECTION)
#   Yang & Nie (2026), PLOS ONE 10.1371/journal.pone.0340479, report per-item means
#   for questionnaire items 9-12 on their 4-point scale (1 = lowest, 4 = highest)
#   over the 135 valid responses (completion time >= 35 s): 2.98, 2.96, 3.08, 3.21.
#   The live table stores these REVERSED (1 = strongest agreement), so the
#   prediction is 5 - mean over that subset. The four published means are distinct,
#   so this identifies item_29..item_32 individually as Q9..Q12 respectively.

suppressMessages(library(irw))
TABLE <- "yang2026_efl_learner_perspective"

XLSX_URL <- "https://ndownloader.figshare.com/files/61706521"   # pone.0340479.s002.xlsx
tmp <- tempfile(fileext = ".xlsx")
utils::download.file(XLSX_URL, tmp, quiet = TRUE, mode = "wb",
                     headers = c("User-Agent" = "Mozilla/5.0"))
raw <- as.data.frame(readxl::read_excel(tmp, col_names = FALSE,
                                        .name_repair = "minimal"))
stopifnot(ncol(raw) == 44)
dat <- raw[-c(1, 2), ]                       # rows 1-2 are the two header rows
ids <- suppressWarnings(as.integer(dat[[1]]))

d <- irw::irw_fetch(TABLE)
d$id <- as.integer(d$id)

cat(sprintf("source rows: %d   live rows: %d   live items: %d\n",
            nrow(dat), nrow(d), length(unique(d$item))))
cat(sprintf("id sets identical: %s\n\n",
            identical(sort(unique(ids)), sort(unique(d$id)))))

cat("=== Evidence 1: per-cell reproduction of the positional mapping ===\n")
cat(sprintf("%-8s %-6s %-62s %8s %10s\n",
            "item", "col", "header label (source row 2)", "cells", "mismatch"))
tot <- 0; bad <- 0
for (pos in 7:42) {
    item <- sprintf("item_%02d", pos - 6)
    src <- suppressWarnings(as.integer(dat[[pos + 1]]))   # R is 1-based
    names(src) <- ids
    liv <- d[d$item == item, ]
    liv <- liv[order(liv$id), ]
    got <- as.integer(liv$resp)
    exp <- as.integer(src[as.character(liv$id)])
    nm <- sum(got != exp)
    tot <- tot + length(got); bad <- bad + nm
    lab <- gsub("\\s+", " ", trimws(as.character(raw[2, pos + 1])))
    cat(sprintf("%-8s %-6d %-62s %8d %10d\n", item, pos, substr(lab, 1, 62),
                length(got), nm))
}
cat(sprintf("\ncells compared: %d   mismatches: %d\n\n", tot, bad))

cat("=== Evidence 2: published means for Q9-Q12, reverse-coded ===\n")
secs <- suppressWarnings(as.numeric(gsub("[^0-9]", "", as.character(dat[[3]]))))
keep <- !is.na(secs) & secs >= 35
PUB <- c(item_29 = 2.98, item_30 = 2.96, item_31 = 3.08, item_32 = 3.21)
cols <- c(item_29 = 36, item_30 = 37, item_31 = 38, item_32 = 39)   # 1-based
cat(sprintf("valid subset n = %d (completion time >= 35 s)\n", sum(keep)))
cat(sprintf("%-8s %10s %10s %8s\n", "item", "published", "5 - mean", "diff"))
dev <- numeric(0)
for (nm in names(PUB)) {
    v <- suppressWarnings(as.numeric(dat[[cols[[nm]]]]))[keep]
    obs <- 5 - mean(v, na.rm = TRUE)
    dev <- c(dev, obs - PUB[[nm]])
    cat(sprintf("%-8s %10.2f %10.3f %8.3f\n", nm, PUB[[nm]], obs, obs - PUB[[nm]]))
}
worst <- max(abs(dev))
cat(sprintf("largest deviation: %.3f (tolerance 0.02)\n\n", worst))

cat("Note: Evidence 2 pins item_29..item_32 and the direction of their scale; it\n",
    "says nothing about the other 32 items. Evidence 1 is what distinguishes every\n",
    "item from every other. Neither establishes the wording of any response option:\n",
    "the deposit carries no value labels and the paper prints no anchors, so\n",
    "option_text is shipped blank by design.\n", sep = "")

cat(if (bad == 0 && worst <= 0.02) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
