# verify_yuebo_2024_sysquality.R
#
# Claim being re-run: each SQ item code in the shipped item table carries the
# wording that the source's own S1 Appendix prints against that very code, and
# the same 4 codes are the literal column headers of the S1 Data file the IRW
# processing script melts (data/yuebo_2024_online_learning.py keeps the source
# column name as `item`). So the mapping is a label match at the source, not an
# order inference: swapping the text of any two SQ items would break the
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
                      "yuebo_2024_sysquality__items.csv")
if (!file.exists(ITEMS)) ITEMS <- "itemtables/batch_241/yuebo_2024_sysquality__items.csv"

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
app <- app[grepl("^SQ[0-9]+$", app$code), ]
app$text <- norm(app$text)

cat(sprintf("S1 Appendix: %d rows carry an SQ code; %d distinct codes\n",
            nrow(app), length(unique(app$code))))

## ---- 2. S1 Data column headers ----
hdr <- names(read.csv(DATA, nrows = 1, check.names = FALSE))
sq_hdr <- grep("^SQ[0-9]+$", hdr, value = TRUE)
cat(sprintf("S1 Data headers: %d SQ columns (%s ... %s)\n",
            length(sq_hdr), sq_hdr[1], sq_hdr[length(sq_hdr)]))

## ---- 3. compare against the shipped table ----
sh <- read.csv(ITEMS, stringsAsFactors = FALSE)
sh <- unique(sh[, c("item", "item_text")])
sh$item_text <- norm(sh$item_text)

m <- merge(sh, app, by.x = "item", by.y = "code", all.x = TRUE)
m <- m[order(as.integer(sub("SQ", "", m$item))), ]
m$ok <- !is.na(m$text) & m$text == m$item_text & m$item %in% sq_hdr

cat(sprintf("\n%-6s %-5s %s\n", "item", "match", "S1 Appendix wording against that code"))
for (i in seq_len(nrow(m)))
    cat(sprintf("%-6s %-5s %s\n", m$item[i], ifelse(m$ok[i], "OK", "DIFF"),
                ifelse(is.na(m$text[i]), "<code absent from appendix>", m$text[i])))

nok <- sum(m$ok)
cat(sprintf("\n%d/%d shipped SQ items reproduce the appendix wording printed against their own code,\n",
            nok, nrow(m)))
cat(sprintf("and %d/%d of those codes are literal S1 Data column headers.\n",
            sum(m$item %in% sq_hdr), nrow(m)))
cat("Each of the 4 codes appears exactly once in the appendix, so this distinguishes\n",
    "every item from every other item. It does NOT verify option_text (none is shipped:\n",
    "the source states only '5-point Likert scale' and prints no anchors), nor the\n",
    "English-vs-administered-Chinese question (the administration was Chinese; the\n",
    "appendix English is shipped as a translated substitute).\n", sep = "")

## ---- 4. live IRW table vs S1 Data, per item (ties live code to source column) ----
src <- read.csv(DATA, check.names = FALSE)
live <- tryCatch(as.data.frame(irw::irw_fetch("yuebo_2024_sysquality")), error = function(e) NULL)
live_ok <- FALSE
if (!is.null(live)) {
    cat("\nper-item response counts, levels 1..5: S1 Data column vs live IRW item\n")
    live_ok <- TRUE
    for (it in sq_hdr) {
        a <- tabulate(src[[it]], 5); b <- tabulate(live$resp[live$item == it], 5)
        cat(sprintf("%-4s src %-22s live %-22s mean %.3f / %.3f %s\n", it,
                    paste(a, collapse = "/"), paste(b, collapse = "/"),
                    mean(src[[it]], na.rm = TRUE), mean(live$resp[live$item == it]),
                    if (identical(a, b)) "OK" else "DIFF"))
        if (!identical(a, b)) live_ok <- FALSE
    }
} else cat("\nlive fetch failed -- cannot tie live codes to source columns\n")

cat(if (live_ok && nok == nrow(m) && nrow(m) == 4) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
