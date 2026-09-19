# verify_yuebo_2024_use.R
#
# Claim being re-run: each shipped USE<n> item carries the wording the S1 Appendix
# prints as item n of its "Continuous Use" block.
#
# Why this is not a plain label match: the appendix codes that block US1..US5 --
# the same stem it uses for the "User Satisfaction" block (US1..US4). The S1 Data
# headers and the paper's measurement table (Table 3: "USE USE1 0.894 3.200 ...
# USE5 0.906 3.575") call these items USE1..USE5, and the paper defines
# "continuous use (USE), user-perceived satisfaction (US)". So the text->code tie
# rests on (a) the section heading "Continuous Use", (b) block size 5 = the 5
# USE* data columns (vs 4 US* columns), and (c) the ORDINAL SUFFIX: each row's
# printed code suffix equals its printed leading number (US<n> / "n."), and that
# n is taken as USE<n>. The stem typo is the one inferential step.
#
# Then, separately, live IRW USE<n> is tied to S1 Data column USE<n> by per-item
# response counts (data/yuebo_2024_online_learning.py melts USE1..USE5 by name).
#
# What this does NOT establish: no statistic in the source can tell the five
# continuous-use items apart by CONTENT -- item means are 4.08-4.21, and the
# paper prints only loadings/VIFs, which tie the paper's USE<n> to the data's
# USE<n> but say nothing about wording. A swap of two appendix rows by the
# authors would be undetectable. Hence PARTIAL, not VERIFIED.

APPENDIX <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0297515.s002"
DATA     <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0297515.s001"
ITEMS    <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                      "yuebo_2024_use__items.csv")
if (!file.exists(ITEMS)) ITEMS <- "itemtables/batch_243/yuebo_2024_use__items.csv"

norm <- function(x) trimws(gsub("\\s+", " ", gsub("^\\s*[0-9]+\\s*\\.\\s*", "", gsub("’", "'", x))))

## ---- 1. parse the appendix, tracking section headings ----
tmpd <- file.path(tempdir(), "yuebo_use_s002"); dir.create(tmpd, showWarnings = FALSE)
docx <- file.path(tmpd, "s002.docx")
utils::download.file(APPENDIX, docx, quiet = TRUE, mode = "wb")
utils::unzip(docx, files = "word/document.xml", exdir = tmpd)
xml <- paste(readLines(file.path(tmpd, "word", "document.xml"), warn = FALSE, encoding = "UTF-8"), collapse = "")
cellsof <- function(tr) vapply(strsplit(tr, "<w:tc[ >]")[[1]][-1], function(tc) {
    t <- regmatches(tc, gregexpr("<w:t[^>]*>[^<]*</w:t>", tc))[[1]]
    paste(gsub("<[^>]+>", "", t), collapse = "")
}, character(1))
heading <- NA_character_; app <- list()
for (tr in strsplit(xml, "<w:tr[ >]")[[1]][-1]) {
    tx <- trimws(gsub("　", " ", cellsof(tr)))
    if (length(tx) < 2 || tx[2] == "") { if (length(tx) && nzchar(tx[1])) heading <- tx[1]; next }
    app[[length(app) + 1]] <- data.frame(section = heading, raw = tx[1], code = tx[2], stringsAsFactors = FALSE)
}
app <- do.call(rbind, app)
cu <- app[app$section %in% "Continuous Use", ]
cu$lead <- as.integer(sub("^\\s*([0-9]+).*", "\\1", cu$raw))
cu$suffix <- as.integer(sub("^US", "", cu$code))
cat(sprintf("Appendix 'Continuous Use' block: %d rows, codes %s\n", nrow(cu), paste(cu$code, collapse = ",")))
cat(sprintf("Appendix 'User Satisfaction' block codes: %s\n",
            paste(app$code[app$section %in% "User Satisfaction"], collapse = ",")))
suffix_ok <- all(cu$code == paste0("US", seq_len(nrow(cu)))) && all(cu$lead == cu$suffix)
cat(sprintf("code suffix == printed leading number == row order for every row: %s\n", suffix_ok))

## ---- 2. S1 Data headers ----
src <- read.csv(DATA, check.names = FALSE)
hdr <- names(src)
cat(sprintf("S1 Data: USE* columns %s; US* columns %s\n",
            paste(grep("^USE[0-9]+$", hdr, value = TRUE), collapse = ","),
            paste(grep("^US[0-9]+$", hdr, value = TRUE), collapse = ",")))

## ---- 3. shipped text vs appendix row n ----
sh <- unique(read.csv(ITEMS, stringsAsFactors = FALSE)[, c("item", "item_text")])
sh$n <- as.integer(sub("^USE", "", sh$item))
m <- merge(sh, data.frame(n = cu$suffix, app_text = norm(cu$raw)), by = "n", all.x = TRUE)
m$ok <- !is.na(m$app_text) & norm(m$item_text) == m$app_text & m$item %in% hdr
cat("\nitem  match  appendix 'Continuous Use' row n\n")
for (i in seq_len(nrow(m))) cat(sprintf("%-5s %-6s %s\n", m$item[i], ifelse(m$ok[i], "OK", "DIFF"), m$app_text[i]))
nok <- sum(m$ok)
cat(sprintf("%d/%d shipped items reproduce appendix row n verbatim (leading numbering stripped)\n", nok, nrow(m)))

## ---- 4. live IRW vs S1 Data, per item ----
live <- tryCatch(as.data.frame(irw::irw_fetch("yuebo_2024_use")), error = function(e) NULL)
live_ok <- FALSE
if (!is.null(live)) {
    live_ok <- TRUE
    cat("\nper-item counts of resp 1..5, S1 Data column vs live IRW item\n")
    for (it in paste0("USE", 1:5)) {
        a <- tabulate(src[[it]], 5); b <- tabulate(live$resp[live$item == it], 5)
        cat(sprintf("%-5s src %-18s live %-18s mean %.3f / %.3f %s\n", it,
                    paste(a, collapse = "/"), paste(b, collapse = "/"),
                    mean(src[[it]]), mean(live$resp[live$item == it]),
                    if (identical(a, b)) "OK" else "DIFF"))
        if (!identical(a, b)) live_ok <- FALSE
    }
} else cat("\nlive fetch failed -- cannot tie live codes to source columns\n")

cat("\nNOT established: content-level distinction between the five items (means 4.08-4.21;\n",
    "no per-item content-diagnostic statistic published). The appendix's own US-for-USE stem\n",
    "slip is resolved by heading + block size + ordinal suffix, not by a code match.\n", sep = "")
cat(if (suffix_ok && live_ok && nok == 5 && nrow(cu) == 5) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
