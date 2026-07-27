# Usage: Rscript list_candidates.R
#
# Diffs irw::irw_list_itemtext_tables() (already has item text) against
# irw::irw_list_tables() (all tables) -- same pattern as tags/src.R -- then
# cross-checks the itemtext index workbook's queue/tables_excluded/xz_todo/
# nj_todo tabs so already-claimed or intentionally-excluded tables aren't
# re-suggested. Prints the remaining candidate list to stdout.

library(gsheet)

done <- tolower(irw::irw_list_itemtext_tables())
all_tabs <- tolower(irw::irw_list_tables()$name)

candidates <- setdiff(all_tabs, done)

fetch_tab_names <- function(sheet_name) {
    url <- sprintf(
        "https://docs.google.com/spreadsheets/d/1jvwxYJ3gjSpEDtx4km-8czvDXu7iEIHhF5V5Y9VWNG0/gviz/tq?tqx=out:csv&sheet=%s",
        sheet_name
    )
    lines <- tryCatch(readLines(url), error = function(e) NULL)
    if (is.null(lines)) return(character(0))
    tolower(lines)
}

## Sheet1 itself: any row with a populated `instrument` link is already done
## (or in progress) via the manual/Sheets-fill workflow.
idx <- gsheet2tbl('https://docs.google.com/spreadsheets/d/1jvwxYJ3gjSpEDtx4km-8czvDXu7iEIHhF5V5Y9VWNG0/edit?gid=0#gid=0')
idx_claimed <- tolower(idx$table[!is.na(idx$instrument) & nchar(trimws(idx$instrument)) > 0])

queue_lines <- fetch_tab_names("queue")
excluded_lines <- fetch_tab_names("tables_excluded")
xz_lines <- fetch_tab_names("xz_todo")
nj_lines <- fetch_tab_names("nj_todo")

is_claimed_or_excluded <- function(tab) {
    any(vapply(
        list(idx_claimed, queue_lines, excluded_lines, xz_lines, nj_lines),
        function(v) any(grepl(tab, v, fixed = TRUE)),
        logical(1)
    ))
}

flags <- vapply(candidates, is_claimed_or_excluded, logical(1))
open_candidates <- candidates[!flags]

cat("Total tables:", length(all_tabs), "\n")
cat("Already have item text:", length(done), "\n")
cat("Candidates before cross-check:", length(candidates), "\n")
cat("Claimed/excluded (queue, tables_excluded, xz_todo, nj_todo, or Sheet1 already populated):",
    sum(flags), "\n")
cat("Open candidates:", length(open_candidates), "\n\n")

cat(paste(open_candidates, collapse = "\n"), "\n")
