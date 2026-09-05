# verify_evpromisi_stone_2021_ddedanx.R
#
# This table is BLOCKED ON RIGHTS: no item text was shipped, so there is no
# item->wording mapping to verify. What IS verifiable, and what the block rests
# on, are two factual claims. This script re-runs both from their sources.
#
#   A. IDENTITY. Every live item code of this table is a PROMIS Emotional
#      Distress-Anxiety item-bank item. The study's own codebooks (Harvard
#      Dataverse doi:10.7910/DVN/G4E2SR, CC0 1.0) label each DDEDANX<nn> row
#      "Modified daily diary version of EDANX<nn>" -- so the wording is PROMIS
#      instrument content with the recall window changed from "In the past 7
#      days" to "In the last day", not study-authored text.
#
#   B. CLAUSE. The wording's rights holder (PROMIS Health Organization /
#      Northwestern University, via HealthMeasures) states an explicit,
#      quotable bar on redistributing the instruments, on its own live site.
#
# Together they make the block determinate under the 2026-09-04 DSES ruling in
# references/itemtext_standard.md ("a quotable clause barring redistribution of
# the instrument governs, even when IRW's wording came from an openly licensed
# deposit"), notwithstanding the deposit's CC0 1.0 licence.
#
# What this does NOT establish: anything about item-text accuracy, since none
# was shipped; and it does not settle the POLICY question -- only that the
# clause exists and that these items are PROMIS content. Seven PROMIS tables
# (promis1wave1_*) already shipped in batch_022 under the opposite reading;
# see notes_evpromisi_stone_2021_ddedanx.csv.
#
# VERDICT: PASS means "the block reproduces" (items are PROMIS AND the clause
# is still published), not "the item text is correct".

suppressMessages(library(irw))

TABLE   <- "evpromisi_stone_2021_ddedanx"
CB_IDS  <- c("hernia surgery" = 4807815, "chemotherapy" = 4807816)
TOU_URL <- paste0("https://healthmeasures.net/wp-content/uploads/2026/06/",
                  "Terms-of-Use_HM_approved_1-12-17-Updated-Copyright-Notices.pdf")
DV      <- "https://dataverse.harvard.edu/api/access/datafile/"

CLAUSES <- c(
  "shall not distribute, publish, sell, license, or provide HealthMeasures products",
  "Commercial Users must seek permission to use, reproduce, or distribute")

## ---- live item codes -----------------------------------------------------
live <- sort(unique(irw::irw_fetch(TABLE)$item))
cat(sprintf("live items (%d): %s\n\n", length(live), paste(live, collapse = ", ")))

## ---- A. codebook identity -------------------------------------------------
# The .docx is a zip; document.xml holds the table text. Strip tags and search
# for "<code> ... Modified daily diary version of EDANX<nn>" pairings.
read_docx_text <- function(url) {
    tmp <- tempfile(fileext = ".docx"); dir <- tempfile(); dir.create(dir)
    utils::download.file(url, tmp, quiet = TRUE, mode = "wb")
    utils::unzip(tmp, files = "word/document.xml", exdir = dir)
    x <- paste(readLines(file.path(dir, "word", "document.xml"),
                         warn = FALSE, encoding = "UTF-8"), collapse = "")
    x <- gsub("</w:p>", " | ", x)          # paragraph -> separator
    x <- gsub("<[^>]+>", "", x)            # drop tags
    gsub("[[:space:]]+", " ", x)
}

cat("A. IDENTITY -- study codebooks label each live code a modified PROMIS EDANX item\n")
matched_any <- rep(FALSE, length(live)); names(matched_any) <- live
for (nm in names(CB_IDS)) {
    txt <- read_docx_text(paste0(DV, CB_IDS[[nm]]))
    hits <- vapply(live, function(it) {
        nn  <- sub("^DDEDANX", "", it)
        pat <- paste0(it, " \\| Modified daily diary version of EDANX", nn, " \\|")
        grepl(pat, txt)
    }, logical(1))
    matched_any <- matched_any | hits
    cat(sprintf("  codebook [%s]: %d/%d live codes carry \"Modified daily diary version of EDANX<nn>\"\n",
                nm, sum(hits), length(live)))
}
cat(sprintf("  union over codebooks: %d/%d matched, %d unmatched (%s)\n\n",
            sum(matched_any), length(live), sum(!matched_any),
            if (all(matched_any)) "none" else paste(live[!matched_any], collapse = ",")))

## ---- B. rights clause ------------------------------------------------------
cat("B. CLAUSE -- HealthMeasures Terms of Use, fetched from the rights holder's site\n")
pdf <- tempfile(fileext = ".pdf")
ok  <- tryCatch({ utils::download.file(TOU_URL, pdf, quiet = TRUE, mode = "wb"); TRUE },
                error = function(e) FALSE)
counts <- rep(NA_integer_, length(CLAUSES))
if (ok && file.exists(pdf) && file.size(pdf) > 1000) {
    txt <- tryCatch(paste(system2("pdftotext", c(pdf, "-"), stdout = TRUE), collapse = " "),
                    error = function(e) "")
    txt <- gsub("[[:space:]]+", " ", txt)
    cat(sprintf("  fetched %s (%d bytes), extracted %d characters of text\n",
                basename(TOU_URL), file.size(pdf), nchar(txt)))
    for (i in seq_along(CLAUSES)) {
        counts[i] <- length(gregexpr(CLAUSES[i], txt, fixed = TRUE)[[1]][
                            gregexpr(CLAUSES[i], txt, fixed = TRUE)[[1]] > 0])
        cat(sprintf("  occurrences of \"%s...\": %d\n", substr(CLAUSES[i], 1, 52), counts[i]))
    }
} else {
    cat("  FETCH FAILED -- cannot re-verify the clause from here\n")
}

## ---- verdict ---------------------------------------------------------------
pass <- all(matched_any) && !any(is.na(counts)) && all(counts >= 1)
cat("\nNote: this reproduces the BLOCK, not an item-text mapping. No __items.csv\n",
    "exists for this table, and none should until the PROMIS rights question is ruled on.\n", sep = "")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
