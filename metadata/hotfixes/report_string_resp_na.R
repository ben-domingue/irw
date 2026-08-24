##############################################################################
## Measurement for the open question in metadata/pipeline_logs/NEXT_RUN_NOTES.md:
## what does the literal "NA" token do to n_responses on string-typed `resp`?
##
## Background. 01_metadata.R defines n_responses as the count of rows where
## `resp IS NOT NULL` -- that is what Redivis' own `count` statistic reports,
## and what the old to_tibble() fallback counted too. On a string-typed `resp`
## the four-character token "NA" is NOT null: R reads it back as the string
## "NA", the server counts it, and it is therefore published as a response.
## A 2026-08-18 scan found 310 of 3,024 core tables with a string `resp`, some
## with a very large "NA" share (dscore_denver_weber_2019: 118,589 of 142,899
## rows; FACIT_YOUNT_2021_limitations: 10,276 of 42,200).
##
## Whether those rows *should* count is a real question, but changing it is a
## change to what n_responses MEANS across the whole corpus, and it belongs on
## the main path rather than hidden in a fallback. So this script does not
## change anything -- it measures, so the decision can be made on numbers.
##
## Cost: one list_variables() call per table (~0.15s, metadata API) to find the
## string-typed ones, then one COUNT query per string table. Queries are not
## subject to the 200 GB/30-day export cap; nothing here exports a table.
##
## Usage (from metadata/):
##   Rscript hotfixes/report_string_resp_na.R              # full sweep, resumable
##   Rscript hotfixes/report_string_resp_na.R --limit 25   # first 25 string tables
##   Rscript hotfixes/report_string_resp_na.R --summary    # re-print summary only
##
## Resumable: every finished table is appended to the output CSV immediately,
## and a re-run skips whatever is already in there. Delete the file to restart.
##############################################################################
options(scipen = 999)
suppressMessages(library(redivis))

out.file <- "hotfixes/string_resp_na_report.csv"
out.cols <- c("table", "shard", "resp_type", "n_rows", "n_resp_not_null",
              "n_resp_na_token", "n_resp_blank", "n_resp_excl_na", "pct_na_of_responses")

args <- commandArgs(trailingOnly = TRUE)
limit <- if ("--limit" %in% args) as.integer(args[which(args == "--limit") + 1]) else Inf
summary.only <- "--summary" %in% args

read_out <- function() {
  if (!file.exists(out.file)) {
    return(setNames(data.frame(matrix(character(0), nrow = 0, ncol = length(out.cols)),
                               stringsAsFactors = FALSE), out.cols))
  }
  d <- tryCatch(read.csv(out.file, stringsAsFactors = FALSE), error = function(e) NULL)
  if (is.null(d) || !all(out.cols %in% names(d))) {
    return(setNames(data.frame(matrix(character(0), nrow = 0, ncol = length(out.cols)),
                               stringsAsFactors = FALSE), out.cols))
  }
  d[, out.cols]
}

print_summary <- function(d) {
  if (nrow(d) == 0) { message("no rows in ", out.file, " yet"); return(invisible(NULL)) }
  d$n_resp_not_null <- as.numeric(d$n_resp_not_null)
  d$n_resp_na_token <- as.numeric(d$n_resp_na_token)
  d$n_resp_blank    <- as.numeric(d$n_resp_blank)
  hit <- d[d$n_resp_na_token > 0, ]
  cat("\n================ summary ================\n")
  cat("string-typed resp tables measured :", nrow(d), "\n")
  cat("  ...with at least one \"NA\" token :", nrow(hit), "\n")
  cat("responses currently counted       :", sum(d$n_resp_not_null, na.rm = TRUE), "\n")
  cat("  of which the literal \"NA\"       :", sum(d$n_resp_na_token, na.rm = TRUE), "\n")
  cat("  of which blank/whitespace       :", sum(d$n_resp_blank, na.rm = TRUE), "\n")
  cat("n_responses if \"NA\" were excluded :",
      sum(d$n_resp_not_null, na.rm = TRUE) - sum(d$n_resp_na_token, na.rm = TRUE), "\n")
  if (nrow(hit) > 0) {
    hit <- hit[order(-hit$n_resp_na_token), ]
    cat("\nworst affected tables:\n")
    show <- utils::head(hit[, c("table", "n_resp_not_null", "n_resp_na_token", "pct_na_of_responses")], 20)
    print(show, row.names = FALSE)
    cat("\ntables that would lose ALL responses:",
        sum(hit$n_resp_na_token >= hit$n_resp_not_null), "\n")
    gone <- hit$table[hit$n_resp_na_token >= hit$n_resp_not_null]
    if (length(gone) > 0) cat("  ", paste(utils::head(gone, 20), collapse = ", "), "\n")
  }
  cat("=========================================\n")
}

done <- read_out()
if (summary.only) { print_summary(done); quit(status = 0) }

## ---- find string-typed resp tables across all four core shards -------------
shards <- c("item_response_warehouse", "item_response_warehouse_2",
            "item_response_warehouse_3", "item_response_warehouse_4")
targets <- list()
## --limit has to short-circuit the SCAN, not just the measure loop: the scan is
## one list_variables() call per table over ~3,650 tables, so scanning
## everything before trimming made `--limit 3` take as long as a full run.
for (ds in shards) {
  if (length(targets) >= limit) break
  v1 <- redivis$organization("datapages")$dataset(ds)
  tabs <- v1$list_tables()
  message("scanning ", ds, " (", length(tabs), " tables) for string-typed resp ...")
  for (tb in tabs) {
    if (length(targets) >= limit) break
    if (tb$name %in% done$table) next
    vars <- tryCatch(tb$list_variables(), error = function(e) NULL)
    if (is.null(vars)) { message("  ! could not list variables for ", tb$name); next }
    nms <- sapply(vars, function(x) x$properties$name)
    j <- which(nms == "resp")
    if (length(j) != 1) next
    ty <- vars[[j]]$properties$type
    if (!identical(tolower(ty), "string")) next
    targets[[length(targets) + 1]] <- list(tab = tb, shard = ds, type = ty)
  }
}
message("string-typed resp tables to measure this run: ", length(targets))

## ---- one COUNT query per table ---------------------------------------------
## Single pass over the table; the conditional sums avoid three separate scans.
count_sql <- function(ref) {
  sprintf(paste(
    "SELECT COUNT(*) AS n_rows,",
    "COUNTIF(resp IS NOT NULL) AS n_not_null,",
    "COUNTIF(resp = 'NA') AS n_na_token,",
    "COUNTIF(resp IS NOT NULL AND TRIM(resp) = '') AS n_blank",
    "FROM `%s`"), ref)
}

for (k in seq_along(targets)) {
  tg <- targets[[k]]
  tb <- tg$tab
  message("  ", k, "/", length(targets), " ", tb$name)
  res <- tryCatch(redivis$query(count_sql(tb$qualified_reference))$to_tibble(),
                  error = function(e) { message("    ! query failed: ", conditionMessage(e)); NULL })
  if (is.null(res)) next
  n_rows <- as.numeric(res$n_rows[1]); n_nn <- as.numeric(res$n_not_null[1])
  n_na <- as.numeric(res$n_na_token[1]); n_bl <- as.numeric(res$n_blank[1])
  row <- data.frame(table = tb$name, shard = tg$shard, resp_type = tg$type,
                    n_rows = n_rows, n_resp_not_null = n_nn,
                    n_resp_na_token = n_na, n_resp_blank = n_bl,
                    n_resp_excl_na = n_nn - n_na,
                    pct_na_of_responses = if (n_nn > 0) round(100 * n_na / n_nn, 2) else NA_real_,
                    stringsAsFactors = FALSE)
  had <- file.exists(out.file)
  write.table(row[, out.cols], out.file, sep = ",", row.names = FALSE,
              col.names = !had, append = had, qmethod = "double")
}

print_summary(read_out())
