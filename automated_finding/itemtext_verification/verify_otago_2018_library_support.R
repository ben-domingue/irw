# Step 5b verification for otago_2018_library_support.
#
# The claim: each Q22_n item code carries the stem the deposit's own
# questionnaire transcript prints against row (n) of the Q22 matrix -- not the
# stem of a neighbouring row.
#
# The route is the transcript's own row numbering, re-derived here from the
# .docx rather than from the builder (make_itemtext_otago_2018.py), so a bug
# in the builder cannot pass this. Qualtrics exports each matrix row with its
# row id in parentheses, "Printed guides  (1)" .. "Annual multiday ...  (8)",
# and those ids are the suffixes of the Q22_1..Q22_8 columns in the data file.
# The check is that the eight ids are complete and unique, that the join is
# bijective with the shipped item set, and that every shipped item_text equals
# the transcript stem for its OWN id.
#
# Usage: Rscript verify_otago_2018_library_support.R <Transcript of questions asked.docx> [items csv]
# Falls back to the live IRW copy of the items table when no path is given.

suppressMessages({library(irw)})

TABLE <- "otago_2018_library_support"

args <- commandArgs(trailingOnly = TRUE)

# Read the document text out of the .docx with no helper package: a .docx is
# a zip whose word/document.xml holds the paragraphs.
tmp <- tempfile(); dir.create(tmp)
utils::unzip(args[1], files = "word/document.xml", exdir = tmp)
xml <- paste(readLines(file.path(tmp, "word", "document.xml"),
                       warn = FALSE, encoding = "UTF-8"), collapse = "")
xml <- gsub("</w:p>", "\n", xml, fixed = TRUE)
txt <- gsub("<[^>]+>", "", xml)
txt <- gsub("&amp;", "&", gsub("&#8217;", "'", txt))
lines <- trimws(strsplit(txt, "\n")[[1]])

start <- grep("^Q22 What is the best way the Library can support you", lines)[1]
stop  <- grep("^Q35", lines)
stop  <- stop[stop > start][1]
blk   <- lines[start:(stop - 1L)]

m <- regmatches(blk, regexec("^(.+?)\\s*\\((\\d)\\)$", blk))
stems <- list()
for (x in m) {
  if (length(x) != 3L) next
  label <- trimws(x[2]); num <- as.integer(x[3])
  if (grepl("^\\d(\\s*\\(.*\\))?$", label)) next   # a scale-point header
  stems[[as.character(num)]] <- label
}
cat(sprintf("transcript row ids found: %s\n",
            paste(sort(as.integer(names(stems))), collapse = ",")))
ok <- identical(sort(as.integer(names(stems))), 1:8)

items <- if (length(args) >= 2) utils::read.csv(args[2], stringsAsFactors = FALSE) else
  irw::irw_fetch_itemtext(TABLE)
items <- items[!duplicated(items$item), c("item", "item_text")]

norm <- function(x) tolower(gsub("[[:space:]]+", " ", trimws(x)))

cat(sprintf("%-8s %-62s %s\n", "item", "transcript stem for that row id", "match"))
for (i in seq_len(nrow(items))) {
  code <- items$item[i]
  num <- sub("^Q22_", "", code)
  want <- stems[[num]]
  if (is.null(want)) {
    cat(sprintf("%-8s %-62s %s\n", code, "<no transcript row with that id>", "FAIL"))
    ok <- FALSE; next
  }
  hit <- norm(want) == norm(items$item_text[i])
  ok <- ok && hit
  cat(sprintf("%-8s %-62s %s\n", code, substr(want, 1, 62),
              if (hit) "ok" else paste0("FAIL <- shipped: ", items$item_text[i])))
}

bij <- identical(sort(paste0("Q22_", names(stems))), sort(items$item))
cat(sprintf("\ntranscript rows: %d ; shipped items: %d ; bijective: %s\n",
            length(stems), nrow(items), bij))
ok <- ok && bij

cat("Note: this pins every item individually -- the tie is the row id the\n",
    "questionnaire itself prints, which is the data file's own column suffix,\n",
    "not an ordering and not a statistical signal. What this does not establish\n",
    "is that the transcript matches what Qualtrics actually displayed; the\n",
    "deposit ships no second record of the form.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
