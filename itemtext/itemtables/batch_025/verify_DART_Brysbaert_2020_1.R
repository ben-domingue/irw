# verify_DART_Brysbaert_2020_1.R
#
# This table is BLOCKED on rights (CC BY-NC-SA on the only published sources of
# the DART item list), so NO item text was shipped and there is no shipped
# mapping to verify. What this script does instead is make the provenance claim
# re-runnable: that the mapping would have been inference-free, because each
# live IRW `item` code CONTAINS the author name, and that the study's own OSF
# key file (DART.docx) covers that same 132-name list with an AUT/NON scoring
# code for every one of them.
#
# It compares NAMES, not counts -- a permutation of the DART key against the
# live codes would break the match, which is the thing validate_items.R cannot
# see. Ground truth is read with irw_table_sets() (server-side aggregate), so
# this costs no Redivis export quota.
#
# Run: Rscript verify_DART_Brysbaert_2020_1.R

suppressMessages(library(irw))

TABLE <- "DART_Brysbaert_2020_1"

## --- live item codes (no export) ---------------------------------------
s <- irw::irw_table_sets(TABLE, source = "core")
live <- s$items
names_live <- sub("^Is de volgende persoon een auteur- \\[", "", live)
names_live <- sub("\\]$", "", names_live)

## --- the study's own key: OSF DART.docx, table Rank / Naam / Code -------
docx_path <- file.path(tempdir(), "DART.docx")
ok <- tryCatch({
    download.file("https://osf.io/download/3up89/", docx_path,
                  quiet = TRUE, mode = "wb"); TRUE
}, error = function(e) FALSE)
if (!ok || !file.exists(docx_path)) {
    cat("could not download OSF DART.docx (osf.io/download/3up89/)\n")
    cat("VERDICT: FAIL\n"); quit(status = 0)
}

## minimal docx table reader: pull <w:t> runs per row/cell from document.xml
xml <- readLines(unz(docx_path, "word/document.xml"), warn = FALSE)
xml <- paste(xml, collapse = "")
trs <- regmatches(xml, gregexpr("<w:tr[ >].*?</w:tr>", xml))[[1]]
cellsof <- function(tr) {
    tcs <- regmatches(tr, gregexpr("<w:tc>.*?</w:tc>", tr))[[1]]
    vapply(tcs, function(tc) {
        ts <- regmatches(tc, gregexpr("<w:t[^>]*>[^<]*</w:t>", tc))[[1]]
        paste(gsub("<[^>]*>", "", ts), collapse = "")
    }, character(1), USE.NAMES = FALSE)
}
rows <- lapply(trs, cellsof)
rows <- Filter(function(r) length(r) >= 3, rows)
hdr  <- rows[[1]]
rows <- rows[-1]
dart_name <- trimws(vapply(rows, `[`, character(1), 2))
dart_code <- trimws(vapply(rows, `[`, character(1), 3))

## --- normalise: strip accents/punctuation, and undo the raw file's ------
## 'ja' -> '1' find/replace corruption (James -> 1mes, Jane -> 1ne)
norm <- function(x) {
    x <- iconv(x, "UTF-8", "ASCII//TRANSLIT")
    x <- tolower(x)
    x <- gsub("1", "ja", x, fixed = TRUE)
    gsub("[^a-z]", "", x)
}
nl <- norm(names_live); nd <- norm(dart_name)

matched   <- sum(nl %in% nd)
unmatched <- names_live[!(nl %in% nd)]
dupes     <- sum(duplicated(nd))

cat(sprintf("live item codes            : %d\n", length(live)))
cat(sprintf("DART.docx key rows (%s/%s/%s): %d\n",
            hdr[1], hdr[2], hdr[3], length(dart_name)))
cat(sprintf("AUT (real authors)         : %d\n", sum(dart_code == "AUT")))
cat(sprintf("NON (foils)                : %d\n", sum(dart_code == "NON")))
cat(sprintf("duplicate normalised names in key: %d\n", dupes))
cat(sprintf("live names found in the key: %d of %d\n", matched, length(live)))
cat(sprintf("unmatched live names (%d)  : %s\n",
            length(unmatched), paste(unmatched, collapse = " | ")))
cat("\nExpected (recorded 2026-09-04): 132 live, 132 key rows, 90 AUT / 42 NON,\n",
    "0 duplicate names, 130 of 132 matched, the 2 unmatched being spelling\n",
    "differences on two names the key scores AUT (real authors) -- live\n",
    "'Georges Simeon' vs key row 92 'Georges_Simenon', and live 'Susan Smith'\n",
    "vs key row 45 'Susan_Smit'.\n", sep = "")
cat("\nWhat this does NOT establish: nothing about shipped item text (none was\n",
    "shipped), nothing about the ja/nee -> 1/0 response coding (the raw workbook\n",
    "was not opened), and nothing about whether the two unmatched names are\n",
    "misspellings in the Study 1 form or deliberate variants.\n",
    sep = "")

pass <- length(live) == 132 && length(dart_name) == 132 &&
        sum(dart_code == "AUT") == 90 && sum(dart_code == "NON") == 42 &&
        dupes == 0 && matched == 130
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
