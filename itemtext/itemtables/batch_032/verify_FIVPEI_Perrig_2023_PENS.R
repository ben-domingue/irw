# verify_FIVPEI_Perrig_2023_PENS.R
#
# This table is BLOCKED on rights + on the source withholding the wording; no
# __items.csv was written, so there is no shipped item->text mapping to verify.
# What this script re-runs is the two FACTUAL claims the block rests on:
#
#   (1) REDACTION: the study's own deposit (OSF 8xuhr) publishes the full printout
#       of every instrument it administered EXCEPT the PENS, whose 21 items appear
#       only as bracketed placeholders ("[PENS autonomy item 1]" ...). So the
#       administered wording is not published in the openly licensed deposit.
#   (2) IDENTITY: the 21 live IRW item codes are byte-identical to the PENS_*
#       column names of the deposit's PXI_validation_main_data.xlsx, i.e. the
#       items IRW holds are exactly the redacted PENS items and nothing else.
#
# Neither claim is about item_text accuracy -- none was shipped. PASS here means
# "the block's premises still hold", not "a mapping reproduced".

suppressMessages(library(irw))

TABLE  <- "FIVPEI_Perrig_2023_PENS"
CACHE  <- file.path("..", "..", ".cache", TABLE)   # itemtext/.cache/<table>
if (!dir.exists(CACHE)) dir.create(CACHE, recursive = TRUE)

PDF  <- file.path(CACHE, "survey.pdf")     # Printout_online_survey.pdf
XLSX <- file.path(CACHE, "main.xlsx")      # PXI_validation_main_data.xlsx
PDF_URL  <- "https://files.osf.io/v1/resources/8xuhr/providers/osfstorage/64e6268250640d068669da62?direct"
XLSX_URL <- "https://files.osf.io/v1/resources/8xuhr/providers/osfstorage/64e625d74c0ee2054743336a?direct"
if (!file.exists(PDF))  download.file(PDF_URL,  PDF,  mode = "wb", quiet = TRUE)
if (!file.exists(XLSX)) download.file(XLSX_URL, XLSX, mode = "wb", quiet = TRUE)

## ---- (1) redaction -------------------------------------------------------
txt <- system2("pdftotext", c("-layout", shQuote(PDF), "-"), stdout = TRUE)
pens_start <- grep("^\\s*4\\.1\\.2\\s+PENS", txt)
pens_end   <- grep("^\\s*4\\.1\\.3", txt)
pens_end   <- pens_end[pens_end > pens_start][1]
block      <- txt[pens_start:pens_end]

placeholders <- grep("^\\s*\\[PENS .*\\]\\s*$", block, value = TRUE)
cat("PENS section of Printout_online_survey.pdf: lines", pens_start, "-", pens_end, "\n")
cat("bracketed placeholder lines in that section:", length(placeholders), "(expected 21)\n")
cat("  e.g. ", trimws(placeholders[1]), " / ", trimws(placeholders[length(placeholders)]), "\n", sep = "")

# Any non-placeholder content line in the block is framing/anchors, not item wording.
content <- trimws(block)
content <- content[nzchar(content)]
content <- content[!grepl("^\\[PENS ", content)]
cat("non-placeholder content lines in the PENS section:", length(content), "\n")
for (l in content) cat("   |", l, "\n")

# Control: the neighbouring IMI section IS printed verbatim in the same document.
imi_start <- grep("^\\s*4\\.1\\.3\\s+IMI", txt)
cat("control - first printed IMI item line:", trimws(txt[imi_start + 5]), "\n")

ok_redaction <- length(placeholders) == 21

## ---- (2) identity --------------------------------------------------------
live <- sort(irw::irw_table_sets(TABLE, per_item = TRUE)$item)
hdr  <- names(readxl::read_xlsx(XLSX, n_max = 0))
src  <- sort(grep("^PENS", hdr, value = TRUE))
cat("\nlive item codes (irw_table_sets):", length(live), "\n")
cat("deposit PENS_* column names      :", length(src), "\n")
cat("identical sets:", identical(live, src), "\n")
if (!identical(live, src)) {
  cat("  live only  :", setdiff(live, src), "\n")
  cat("  deposit only:", setdiff(src, live), "\n")
}
ok_identity <- identical(live, src)

## ---- what this does NOT establish ---------------------------------------
cat("\nNOT established: anything about item_text fidelity or item<->text mapping,\n",
    "because no item text was shipped. Also not re-tested here (fetched by hand,\n",
    "Cloudflare blocks scripted access): the rights holder's clause on\n",
    "selfdeterminationtheory.org/player-experience-of-needs-satisfaction-pens/ --\n",
    "\"All academic use is permitted, but you must obtain permission from the\n",
    "Center for Self-Determination Theory for commercial use.\"\n", sep = "")

cat(if (ok_redaction && ok_identity) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
