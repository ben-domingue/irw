# verify_che_2026_regulatory_self_efficacy.R
#
# THIS TABLE IS BLOCKED. No che_2026_regulatory_self_efficacy__items.csv was
# written, so there is NO item_text<->item and NO option_text<->resp mapping
# claimed by this round, and therefore none for this script to verify. Step 5b
# status is NO_ROUTE. "VERDICT: PASS" below means ONLY "the three determinate
# facts the block rests on still reproduce" -- it is not, and must not be read
# as, verification of any wording.
#
# The three facts:
#   1. The sole source (Figshare 10.6084/m9.figshare.32090683.v1, CC BY 4.0)
#      declares NO companion publication -- its `references` list is empty --
#      and the paper it names in its title is not indexed in Crossref or
#      Europe PMC. So there is no paper/appendix to transcribe from.
#   2. Its only file, "Raw dade.xlsx", contains no item wording in any
#      language: one sheet, bare coded headers, numeric cells, no value
#      labels, and zero CJK characters anywhere in the workbook. The
#      administration was Chinese, so this is what forces the fallback -- and
#      the fallback has no English list either (see notes_*.csv).
#   3. The 12 IRW item codes ARE those bare spreadsheet headers, verbatim
#      ("RES item1".."RES item12"). A code that is a column position carries
#      no content, so any mapping would be an assumption about column order --
#      unsafe here, since Wen et al. (2009) and Huang et al. (2012) circulate
#      different item structures over the same 12 numbers (Xu et al. 2026,
#      BMC Psychol 14:787, models B vs C, df 42 vs 43).
#
# Live values come from irw::irw_table_sets() -- a server-side aggregate. No
# irw_fetch()/export is performed.

suppressMessages(library(irw))
suppressMessages(library(jsonlite))
suppressMessages(library(readxl))

TABLE <- "che_2026_regulatory_self_efficacy"
CACHE <- file.path(path.expand("~"), "irw-queue-runner", "itemtext", ".cache", TABLE)
dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)
ok <- TRUE

## -- Fact 1: the deposit declares no companion publication -----------------
meta_f <- file.path(CACHE, "meta.json")
if (!file.exists(meta_f))
    try(download.file("https://api.figshare.com/v2/articles/32090683",
                      meta_f, quiet = TRUE), silent = TRUE)
if (file.exists(meta_f)) {
    m <- jsonlite::fromJSON(meta_f)
    nref <- length(m$references)
    cat(sprintf("figshare 32090683: license=%s  files=%d  references=%d\n",
                m$license$name, nrow(m$files), nref))
    cat(sprintf("  expected references=0 (no companion paper)  -> %s\n",
                if (nref == 0) "as expected" else "CHANGED"))
    if (nref != 0) ok <- FALSE   # a paper appeared: the block is retryable
} else {
    cat("figshare metadata unreachable; fact 1 not re-checked this run\n")
}

## -- Fact 2 + 3: the source file's headers, and their tie to the IRW codes --
xlsx <- file.path(CACHE, "raw.xlsx")
if (!file.exists(xlsx))
    try(download.file("https://ndownloader.figshare.com/files/63988402",
                      xlsx, mode = "wb", quiet = TRUE), silent = TRUE)

if (file.exists(xlsx)) {
    sh <- readxl::excel_sheets(xlsx)
    x  <- suppressMessages(readxl::read_excel(xlsx, sheet = sh[1]))
    hdr <- names(x)
    res <- grep("^RES item[0-9]+$", hdr, value = TRUE)
    cat(sprintf("\nRaw dade.xlsx: sheets=%d  columns=%d  RES columns=%d\n",
                length(sh), length(hdr), length(res)))

    # No wording anywhere: no CJK, and no header longer than a code.
    all_txt <- c(hdr, unlist(lapply(x, function(c) as.character(c))))
    cjk <- sum(grepl("[一-鿿]", all_txt), na.rm = TRUE)
    longest <- max(nchar(hdr))
    cat(sprintf("  CJK-bearing cells/headers: %d (expected 0)\n", cjk))
    cat(sprintf("  longest header: %d chars (\"%s\") -- codes, not wording\n",
                longest, hdr[which.max(nchar(hdr))]))
    if (cjk != 0 || longest > 25) ok <- FALSE

    ts <- irw::irw_table_sets(TABLE)
    live <- sort(as.character(unique(ts$item)))
    cat(sprintf("\nIRW item codes (%d) vs source headers (%d): identical sets = %s\n",
                length(live), length(res), identical(live, sort(res))))
    cat(sprintf("  e.g. %s ... %s\n", live[1], live[length(live)]))
    cat(sprintf("  resp set: {%s}\n", paste(sort(unique(ts$resp)), collapse = ",")))
    if (!identical(live, sort(res))) ok <- FALSE
} else {
    cat("\nsource xlsx unreachable; facts 2-3 not re-checked this run\n")
}

cat("\nWhat this does NOT establish: nothing about the wording of any item.\n")
cat("No wording was obtained from any source, so no mapping is claimed and\n")
cat("none is verified here. Step 5b status is NO_ROUTE, not VERIFIED.\n\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
