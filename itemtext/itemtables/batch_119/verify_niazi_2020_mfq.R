# verify_niazi_2020_mfq.R -- Step 5b evidence, re-runnable.
#
# CLAIM: each IRW item code carries the MFQ30 statement shipped in item_text.
# The IRW code IS the SPSS column name (data/niazi_2020_moral_foundations.py melts
# the .sav's bare MFQ columns), and that .sav labels every one of those columns with
# the statement it holds. The shipped wording is the canonical MFQ30 form
# (moralfoundations.org/wp-content/uploads/files/MFQ30.doc), which is what the study
# says it administered.
#
# So the falsifiable check is: for every code, does the SPSS variable label match the
# statement shipped for that code? If item_text for any two codes were swapped, the
# label-to-text match would break for both.
#
# What this does NOT establish: that the canonical .doc wording is character-identical
# to the form the participants saw (the labels are the .sav author's abridgement --
# Part 1 labels drop the leading "Whether or not "), and it does not check option_text
# order, which rests on the .doc's printed 0..5 anchors.

suppressMessages({library(haven); library(irw)})

TABLE <- "niazi_2020_mfq"
SAV <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0229926.s002"
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                       "niazi_2020_mfq__items.csv")
if (!file.exists(ITEMS_CSV)) ITEMS_CSV <- "itemtables/batch_119/niazi_2020_mfq__items.csv"

tf <- tempfile(fileext = ".sav")
download.file(SAV, tf, quiet = TRUE, mode = "wb")
d <- haven::read_sav(tf)
labs <- vapply(d, function(x) {
  l <- attr(x, "label"); if (is.null(l)) "" else as.character(l)
}, character(1))

items <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE, encoding = "UTF-8")
items <- unique(items[, c("item", "item_text")])

norm <- function(x) {
  x <- gsub("\\[[^]]*\\]", "", x)                 # strip the .sav's "[use this to cut...]" notes
  x <- gsub("’", "'", x)                      # curly -> straight apostrophe
  x <- sub("^Whether or not ", "", x)              # Part 1 labels drop this lead-in
  x <- tolower(gsub("[^A-Za-z0-9 ]", "", x))
  trimws(gsub("[[:space:]]+", " ", x))
}

ok <- 0L; bad <- character(0)
cat(sprintf("%-12s %-55s %s\n", "item", "SPSS variable label (norm.)", "match"))
for (i in seq_len(nrow(items))) {
  code <- items$item[i]
  lab <- if (code %in% names(labs)) labs[[code]] else NA_character_
  a <- norm(lab); b <- norm(items$item_text[i])
  hit <- !is.na(lab) && nzchar(lab) && a == b
  if (hit) ok <- ok + 1L else bad <- c(bad, sprintf("%s: label=<%s> shipped=<%s>", code, a, b))
  cat(sprintf("%-12s %-55s %s\n", code, substr(a, 1, 55), if (hit) "OK" else "MISMATCH"))
}

cat(sprintf("\nlabelled codes matched: %d / %d\n", ok, nrow(items)))
if (length(bad)) cat(paste(bad, collapse = "\n"), "\n")

# Second, cheap structural check: the two response blocks. Part 1 (moral relevance)
# and Part 2 (moral judgement) carry different anchors; confirm the shipped section
# split is 16/16 and that the .sav column order puts the Part 1 codes first.
sec <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE, encoding = "UTF-8")
n1 <- length(unique(sec$item[sec$section_id == "niazi_2020_mfq_part1"]))
n2 <- length(unique(sec$item[sec$section_id == "niazi_2020_mfq_part2"]))
pos <- match(unique(sec$item), names(labs))
p1pos <- pos[unique(sec$section_id[match(unique(sec$item), sec$item)]) == "niazi_2020_mfq_part1"]
cat(sprintf("section sizes: part1=%d part2=%d (MFQ30 is 16+16 incl. 2 catch items)\n", n1, n2))
cat(sprintf(".sav column positions: part1 %d-%d, part2 %d-%d\n",
            min(pos[1:16]), max(pos[1:16]), min(pos[17:32]), max(pos[17:32])))

pass <- ok == nrow(items) && n1 == 16 && n2 == 16 && max(pos[1:16]) < min(pos[17:32])
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
