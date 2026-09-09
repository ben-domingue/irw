# verify_jo_2023_pbc.R -- Step 5b evidence, re-runnable.
#
# CLAIM: item codes PBC1/PBC2/PBC3 in the live IRW table are the literal column
# names of the study's S1 File CSV, and the study's S1 Appendix (Table A1) prints
# each item's wording against those same literal codes. So the item<->item_text
# tie is a label match, not an order inference.
#
# This script re-derives that tie from the two source files and diffs the shipped
# item_text against the appendix cell for the SAME code. It would FAIL if the
# text for any two items were swapped.

suppressMessages(library(irw))

TABLE  <- "jo_2023_pbc"
DOCX   <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0283997.s001"
DATCSV <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0283997.s003"
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                       "jo_2023_pbc__items.csv")
if (!file.exists(ITEMS_CSV)) ITEMS_CSV <- "itemtables/batch_058/jo_2023_pbc__items.csv"

tmp <- tempfile(fileext = ".docx")
download.file(DOCX, tmp, quiet = TRUE, mode = "wb")
xml <- readLines(unzip(tmp, "word/document.xml", exdir = tempdir()), warn = FALSE)
xml <- paste(xml, collapse = "")

# Word splits text across runs ("P" + "BC1"), so read whole TABLE CELLS, not runs.
cells <- strsplit(xml, "</w:tc>", fixed = TRUE)[[1]]
cells <- gsub("<[^>]*>", "", cells)
cells <- gsub("&amp;", "&", cells)
cells <- trimws(gsub("[[:space:]]+", " ", cells))

# appendix: the cell after a code cell holds that code's wording
app <- list()
for (i in seq_along(cells))
  if (grepl("^PBC[0-9]$", cells[i])) app[[cells[i]]] <- cells[i + 1]

raw_hdr <- strsplit(readLines(DATCSV, n = 1, warn = FALSE), ",")[[1]]
raw_pbc <- grep("^PBC", raw_hdr, value = TRUE)

live <- sort(irw::irw_table_sets(TABLE)$item)
ship <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE)
ship <- unique(ship[, c("item", "item_text")])
ship <- ship[order(ship$item), ]

cat("S1 File CSV column names (PBC block): ", paste(raw_pbc, collapse = ", "), "\n", sep = "")
cat("live IRW item codes:                  ", paste(live, collapse = ", "), "\n\n", sep = "")

ok_codes <- identical(sort(raw_pbc), sort(live)) &&
            identical(sort(names(app)), sort(live)) &&
            identical(sort(ship$item), sort(live))

cat(sprintf("%-6s %-8s %s\n", "code", "match", "appendix wording vs shipped item_text"))
ok_text <- TRUE
for (k in sort(names(app))) {
  s <- ship$item_text[ship$item == k]
  same <- length(s) == 1 && identical(trimws(app[[k]]), trimws(s))
  ok_text <- ok_text && same
  cat(sprintf("%-6s %-8s appendix: %s\n", k, if (same) "OK" else "DIFF", app[[k]]))
  if (!same) cat(sprintf("%-6s %-8s shipped : %s\n", "", "", paste(s, collapse = " / ")))
}

cat("\nCodes reconciled 3/3 across S1 File header, S1 Appendix Table A1, live IRW and shipped CSV: ",
    ok_codes, "\n", sep = "")
cat("Note: this establishes the item<->item_text tie only. The 7 response levels carry\n",
    "no option_text (the paper states a '7-point Likert scale' but never prints its\n",
    "anchors), so nothing here verifies the resp<->option_text axis -- there is none.\n", sep = "")

cat(if (ok_codes && ok_text) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
