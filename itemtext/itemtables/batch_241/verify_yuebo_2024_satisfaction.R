# verify_yuebo_2024_satisfaction.R
#
# Claim being re-run: each US item code in the shipped item table carries the
# wording that the source's own S1 Appendix prints against that very code under
# the "User Satisfaction" heading, and US1..US4 are literal column headers of the
# S1 Data CSV that data/yuebo_2024_online_learning.py melts by name (item IS the
# source column name). So the tie is a label match at the source, not an order
# inference: swapping the text of any two US items breaks the comparison below.
#
# Complication this script exists to settle: the appendix ALSO prints codes
# US1..US5 against its "Continuous Use" block (a labelling slip; the data and the
# paper's measurement table call those USE1..USE5). The US code alone is therefore
# ambiguous in the appendix. It is resolved here by (a) the section heading,
# (b) block size: the satisfaction block has exactly 4 codes, the continuous-use
# block 5, and the S1 Data has 4 US* columns and 5 USE* columns, and (c) US5 --
# present in the continuous-use block -- is not a column in the data.
#
# Source: Yuebo, Halili & Abdul Razak (2024) PLOS ONE 19(2): e0297515,
#   S1 Appendix "The items with their sources" (.s002, DOCX); S1 Data (.s001, CSV).
#
# Does NOT re-check item/resp sets (validate_items.R does that).

APPENDIX <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0297515.s002"
DATA     <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0297515.s001"
ITEMS    <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                      "yuebo_2024_satisfaction__items.csv")
if (!file.exists(ITEMS)) ITEMS <- "itemtables/batch_241/yuebo_2024_satisfaction__items.csv"

norm <- function(x) {
    x <- gsub("’", "'", x)
    x <- gsub("^\\s*[0-9]+\\s*\\.\\s*", "", x)   # strip leading "1." numbering
    x <- gsub("\\s+", " ", x)
    trimws(x)
}

## ---- 1. parse the appendix table, tracking the current section heading ----
tmpd <- file.path(tempdir(), "yuebo_sat_s002")
dir.create(tmpd, showWarnings = FALSE)
docx <- file.path(tmpd, "s002.docx")
utils::download.file(APPENDIX, docx, quiet = TRUE, mode = "wb")
utils::unzip(docx, files = "word/document.xml", exdir = tmpd)
xml <- paste(readLines(file.path(tmpd, "word", "document.xml"), warn = FALSE, encoding = "UTF-8"),
             collapse = "")
rows <- strsplit(xml, "<w:tr[ >]")[[1]][-1]
cellsof <- function(tr) {
    cells <- strsplit(tr, "<w:tc[ >]")[[1]][-1]
    vapply(cells, function(tc) {
        t <- regmatches(tc, gregexpr("<w:t[^>]*>[^<]*</w:t>", tc))[[1]]
        paste(gsub("<[^>]+>", "", t), collapse = "")
    }, character(1))
}
heading <- NA_character_
app <- list()
for (tr in rows) {
    tx <- trimws(gsub("\u3000", " ", cellsof(tr)))   # heading rows pad with U+3000 ideographic spaces
    # heading rows are either a single merged cell or have an empty Code cell
    if (length(tx) < 2 || tx[2] == "") { if (nzchar(tx[1])) heading <- tx[1]; next }
    app[[length(app) + 1]] <- data.frame(section = heading, text = norm(tx[1]),
                                         code = tx[2], stringsAsFactors = FALSE)
}
app <- do.call(rbind, app)
us_rows <- app[grepl("^US[0-9]+$", app$code), ]
cat("Appendix rows carrying a US* code, by section heading:\n")
print(table(us_rows$section))

sat <- us_rows[us_rows$section %in% "User Satisfaction", ]
cu  <- us_rows[us_rows$section %in% "Continuous Use", ]

## ---- 2. S1 Data headers ----
hdr <- names(read.csv(DATA, nrows = 1, check.names = FALSE))
us_hdr  <- grep("^US[0-9]+$", hdr, value = TRUE)
use_hdr <- grep("^USE[0-9]+$", hdr, value = TRUE)
cat(sprintf("\nS1 Data: %d US* columns (%s), %d USE* columns (%s)\n",
            length(us_hdr), paste(us_hdr, collapse = ","), length(use_hdr), paste(use_hdr, collapse = ",")))
cat(sprintf("Appendix 'User Satisfaction' block: %d codes (%s); 'Continuous Use' block: %d codes (%s)\n",
            nrow(sat), paste(sat$code, collapse = ","), nrow(cu), paste(cu$code, collapse = ",")))
block_ok <- nrow(sat) == length(us_hdr) && setequal(sat$code, us_hdr) &&
            nrow(cu) == length(use_hdr) && !all(cu$code %in% us_hdr) &&
            !anyDuplicated(sat$code)
cat(sprintf("Block resolution (satisfaction codes == data US* headers; continuous-use block has a code absent from data): %s\n",
            if (block_ok) "OK" else "FAILED"))

## ---- 3. compare shipped wording against the satisfaction block ----
sh <- read.csv(ITEMS, stringsAsFactors = FALSE)
sh <- unique(sh[, c("item", "item_text")])
sh$item_text <- norm(sh$item_text)
m <- merge(sh, sat, by.x = "item", by.y = "code", all.x = TRUE)
m <- m[order(m$item), ]
m$ok <- !is.na(m$text) & m$text == m$item_text & m$item %in% us_hdr
cat(sprintf("\n%-5s %-5s %s\n", "item", "match", "appendix wording against that code (User Satisfaction block)"))
for (i in seq_len(nrow(m)))
    cat(sprintf("%-5s %-5s %s\n", m$item[i], ifelse(m$ok[i], "OK", "DIFF"),
                ifelse(is.na(m$text[i]), "<absent>", m$text[i])))
# Negative control: the shipped text must NOT match the continuous-use block's same codes.
cu_hits <- sum(sh$item_text %in% cu$text)
cat(sprintf("\n%d/%d shipped items match the satisfaction-block wording printed against their own code;\n",
            sum(m$ok), nrow(m)))
cat(sprintf("%d shipped items match any continuous-use-block wording (must be 0).\n", cu_hits))
cat("Each US code appears exactly once within the User Satisfaction block, so this distinguishes\n",
    "every item from every other item. It does NOT verify option_text (none shipped: the paper\n",
    "states only a 5-point Likert scale and prints no anchors) nor address the English-for-Chinese\n",
    "substitution. No per-item statistic in the paper can test text<->code independently.\n", sep = "")

cat(if (block_ok && all(m$ok) && nrow(m) == 4 && cu_hits == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
