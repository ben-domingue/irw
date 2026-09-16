# verify_yuebo_2024_netbenefit.R
#
# Claim being re-run: each NB item code in the shipped item table carries the
# wording that the source's own S1 Appendix prints against that very code, and
# the same 16 codes are the literal column headers of the S1 Data file the IRW
# processing script melts (data/yuebo_2024_online_learning.py keeps the source
# column name as `item`). So the mapping is a label match at the source, not an
# order inference: swapping the text of any two NB items would break the
# comparison below.
#
# Source: Yuebo, Halili & Abdul Razak (2024) PLOS ONE 19(2): e0297515,
#   S1 Appendix "The items with their sources" (.s002, DOCX)
#   S1 Data (.s001, CSV)
#
# This script deliberately does NOT re-check item/resp sets -- validate_items.R
# does that, and a count is not mapping evidence.

APPENDIX <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0297515.s002"
DATA     <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0297515.s001"
ITEMS    <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                      "yuebo_2024_netbenefit__items.csv")
if (!file.exists(ITEMS)) ITEMS <- "itemtables/batch_240/yuebo_2024_netbenefit__items.csv"

norm <- function(x) {
    x <- gsub("’", "'", x)
    x <- gsub("^\\s*[0-9]+\\s*\\.\\s*", "", x)   # strip leading "12." numbering
    x <- gsub("\\s+", " ", x)
    trimws(x)
}

## ---- 1. parse the S1 Appendix DOCX table (measure text | code | source) ----
tmpd <- file.path(tempdir(), "yuebo_s002")
dir.create(tmpd, showWarnings = FALSE)
docx <- file.path(tmpd, "s002.docx")
utils::download.file(APPENDIX, docx, quiet = TRUE, mode = "wb")
utils::unzip(docx, files = "word/document.xml", exdir = tmpd)
xml <- paste(readLines(file.path(tmpd, "word", "document.xml"), warn = FALSE), collapse = "")

rows <- strsplit(xml, "<w:tr[ >]")[[1]][-1]
app <- do.call(rbind, lapply(rows, function(tr) {
    cells <- strsplit(tr, "<w:tc[ >]")[[1]][-1]
    txt <- vapply(cells, function(tc) {
        t <- regmatches(tc, gregexpr("<w:t[^>]*>[^<]*</w:t>", tc))[[1]]
        paste(gsub("<[^>]+>", "", t), collapse = "")
    }, character(1))
    if (length(txt) < 2) return(NULL)
    data.frame(text = txt[1], code = trimws(txt[2]), stringsAsFactors = FALSE)
}))
app <- app[grepl("^NB[0-9]+$", app$code), ]
app$text <- norm(app$text)
# item NB1's cell also carries the block's shared stem; the stem is shipped as
# section_prompt, so strip it before comparing the item's own wording.
STEM <- "After using online learning system, I am able to perform these tasks:"
app$text <- norm(sub(STEM, "", app$text, fixed = TRUE))

cat(sprintf("S1 Appendix: %d rows carry an NB code; %d distinct codes\n",
            nrow(app), length(unique(app$code))))

## ---- 2. S1 Data column headers ----
hdr <- names(read.csv(DATA, nrows = 1, check.names = FALSE))
nb_hdr <- grep("^NB[0-9]+$", hdr, value = TRUE)
cat(sprintf("S1 Data headers: %d NB columns (%s ... %s)\n",
            length(nb_hdr), nb_hdr[1], nb_hdr[length(nb_hdr)]))

## ---- 3. compare against the shipped table ----
sh <- read.csv(ITEMS, stringsAsFactors = FALSE)
sh <- unique(sh[, c("item", "item_text")])
sh$item_text <- norm(sh$item_text)

m <- merge(sh, app, by.x = "item", by.y = "code", all.x = TRUE)
m <- m[order(as.integer(sub("NB", "", m$item))), ]
m$ok <- !is.na(m$text) & m$text == m$item_text & m$item %in% nb_hdr

cat(sprintf("\n%-6s %-5s %s\n", "item", "match", "S1 Appendix wording against that code"))
for (i in seq_len(nrow(m)))
    cat(sprintf("%-6s %-5s %s\n", m$item[i], ifelse(m$ok[i], "OK", "DIFF"),
                ifelse(is.na(m$text[i]), "<code absent from appendix>", m$text[i])))

nok <- sum(m$ok)
cat(sprintf("\n%d/%d shipped NB items reproduce the appendix wording printed against their own code,\n",
            nok, nrow(m)))
cat(sprintf("and %d/%d of those codes are literal S1 Data column headers.\n",
            sum(m$item %in% nb_hdr), nrow(m)))
cat("Each of the 16 codes appears exactly once in the appendix, so this distinguishes\n",
    "every item from every other item. It does NOT verify option_text (none is shipped:\n",
    "the source states only '5-point Likert scale' and prints no anchors), nor the\n",
    "English-vs-administered-Chinese question (the administration was Chinese; the\n",
    "appendix English is shipped as a translated substitute).\n", sep = "")

cat(if (nok == nrow(m) && nrow(m) == 16) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
