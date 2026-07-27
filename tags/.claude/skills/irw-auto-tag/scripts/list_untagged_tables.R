#!/usr/bin/env Rscript
# Lists IRW Redivis tables that do not yet have a row in the "IRW Tags" sheet.
# Case-insensitive diff, matching the logic already in tags/src.R.
#
# Usage:
#   Rscript list_untagged_tables.R                # print every untagged table, one per line
#   Rscript list_untagged_tables.R --sample 50     # random sample of 50
#   Rscript list_untagged_tables.R --out queue.csv # write to CSV instead of stdout

suppressMessages(library(gsheet))

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  i <- match(flag, args)
  if (is.na(i) || i == length(args)) return(default)
  args[i + 1]
}
sample_n <- get_arg("--sample")
out_path <- get_arg("--out")

tabs <- irw::irw_list_tables()
tabs <- tolower(tabs$name)

tags <- gsheet2tbl("https://docs.google.com/spreadsheets/d/1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/edit?gid=126134123#gid=126134123")
names(tags) <- tolower(names(tags))
# first data row is the sheet's own instruction/template row, not a real table
tabs.done <- tolower(tags$table)[-1]
tabs.done <- tabs.done[!is.na(tabs.done)]

tabs.todo <- sort(tabs[!(tabs %in% tabs.done)])

if (!is.null(sample_n)) {
  tabs.todo <- sample(tabs.todo, min(as.integer(sample_n), length(tabs.todo)))
}

if (!is.null(out_path)) {
  writeLines(tabs.todo, out_path)
  cat(sprintf("Wrote %d untagged table names to %s\n", length(tabs.todo), out_path))
} else {
  cat(tabs.todo, sep = "\n")
}
