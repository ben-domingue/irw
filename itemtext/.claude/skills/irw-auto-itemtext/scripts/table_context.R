# Usage: Rscript table_context.R <table>
#
# Prints everything needed before extracting item text for one table:
#   - the ground-truth item/resp sets from the live response data (the
#     target the extraction must hit exactly)
#   - the dictionary row (URL/DOI/Reference/Description) for finding the
#     source paper, same source used for dataset processing
#   - this table's current status in the itemtext index workbook (Sheet1
#     NOTES + whether links are already populated, plus a same-name check
#     against queue/tables_excluded/xz_todo/nj_todo)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) stop("Usage: Rscript table_context.R <table>")
table <- args[1]
table_lower <- tolower(table)

library(gsheet)

cat("=== Ground truth from irw::irw_fetch(\"", table, "\") ===\n", sep = "")
df <- irw::irw_fetch(table)
items <- sort(unique(df$item))
resps <- sort(unique(df$resp))
cat("N items:", length(items), "\n")
cat("Items:", paste(items, collapse = ", "), "\n")
cat("N distinct resp values:", length(resps), "\n")
cat("Resp values:", paste(resps, collapse = ", "), "\n\n")

cat("=== Dictionary row (IRW Data Dictionary) ===\n")
dict <- gsheet2tbl('https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=0#gid=0')
ii <- which(tolower(dict$table) == table_lower | tolower(dict$table.lower) == table_lower)
if (length(ii) == 0) {
    cat("No dictionary row found for", table, "-- source paper/DOI unknown from this route.\n")
} else {
    row <- dict[ii[1], ]
    cat("Description:", row$Description, "\n")
    cat("URL (for data):", row[["URL (for data)"]], "\n")
    cat("Reference:", row$Reference, "\n")
    cat("DOI (for paper):", row[["DOI (for paper)"]], "\n")
}
cat("\n")

cat("=== Itemtext index workbook status ===\n")
idx <- gsheet2tbl('https://docs.google.com/spreadsheets/d/1jvwxYJ3gjSpEDtx4km-8czvDXu7iEIHhF5V5Y9VWNG0/edit?gid=0#gid=0')
jj <- match(table_lower, tolower(idx$table))
if (!is.na(jj)) {
    has_links <- !is.na(idx$instrument[jj]) && nchar(trimws(idx$instrument[jj])) > 0
    cat("Row exists in Sheet1. NOTES:", ifelse(is.na(idx$NOTES[jj]) || idx$NOTES[jj] == "", "(none)", idx$NOTES[jj]), "\n")
    cat("Links already populated:", has_links, "\n")
    if (has_links) cat("STOP: this table already has a per-table sheet -- do not reprocess without being told to redo it.\n")
} else {
    cat("Not yet in Sheet1.\n")
}

check_tab <- function(name) {
    url <- sprintf(
        "https://docs.google.com/spreadsheets/d/1jvwxYJ3gjSpEDtx4km-8czvDXu7iEIHhF5V5Y9VWNG0/gviz/tq?tqx=out:csv&sheet=%s",
        name
    )
    lines <- tryCatch(readLines(url), error = function(e) NULL)
    if (is.null(lines)) {
        cat(name, ": could not fetch\n", sep = "")
        return(invisible())
    }
    hit <- any(grepl(table_lower, tolower(lines), fixed = TRUE))
    cat(name, ": ", if (hit) "PRESENT -- inspect before proceeding" else "not present", "\n", sep = "")
}
for (nm in c("queue", "tables_excluded", "xz_todo", "nj_todo")) check_tab(nm)

cat("\n=== Local state ===\n")
out_csv <- paste0(table, "__items.csv")
if (file.exists(out_csv)) {
    cat(out_csv, "already exists locally -- check before overwriting.\n")
} else {
    cat("No local", out_csv, "yet.\n")
}
