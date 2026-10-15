##rank_metadata.csv: one row per table in the rankings source (every shard in
##IRW_RANK_DATASETS: irw_rank, ...).
##
##A rankings table keeps the core column names, but resp is a position and a
##repeated id x item is a duplicate mark kept by the standard
##(data/rankings/README.md), so the core metadata (01_metadata.R) would misread
##it. This is the rankings counterpart of 16_conjoint.R, without the
##carry-forward: the family is small, and a full recompute is one query per
##batch of tables. Add stamps on the conjoint pattern (#2970) when the
##recompute takes longer than the other shard stages together.
##
##Columns computed from the data:
##  table, n_respondents (distinct id), n_rows, n_tasks (largest task index),
##  n_items (distinct item, reserved values included), max_resp (highest
##  position marked), n_duplicate_marks (rows beyond the first per
##  id x task x item: a candidate marked at two positions).
##Design columns, joined from the hand-kept data/rankings/design_tables.csv
##(everything but `evidence`): source_file, collection, jurisdiction, date,
##office, method, seats, n_positions, n_candidates, n_ballots_cast,
##n_ballots_eligible_est, n_ballots_with_marks, n_duplicate_marks (the record's
##own count, kept as design_n_duplicate_marks so the two can be compared),
##n_overvotes, n_writeins, write_in_allowed, candidate_order. Their codes are
##documented in data/rankings/README.md, "Design record".
##
##Runs in run_pipeline.sh with 05/06/07/16, before 02_biblio.R, which uses
##rank_metadata.csv as the liveness oracle for rank_biblio.
options(scipen=999)
library(redivis)
source("redivis_config.R")
##Every rankings shard, newest first: the clients resolve a table name
##newest-first, so a name present in two shards is read from the newest. That
##is an upload mistake (red_up updates a table where it lives), so it is
##reported here and the newest copy kept -- never merged silently.
tabs <- list()
tab_shard <- character(0)
for (rank_dataset in rev(IRW_RANK_DATASETS)) {
  ds <- redivis$organization(IRW_OWNER)$dataset(rank_dataset)
  shard_tabs <- ds$list_tables()
  message("  ", rank_dataset, ": ", length(shard_tabs), " tables")
  for (tab in shard_tabs) {
    if (tab$name %in% names(tabs)) {
      message("  ! ", tab$name, " is in both ", tab_shard[[tab$name]], " and ",
              rank_dataset, "; keeping the copy in ", tab_shard[[tab$name]],
              " -- clients resolve newest-first, so the older one is unreachable")
      next
    }
    tabs[[tab$name]] <- tab
    tab_shard[[tab$name]] <- rank_dataset
  }
}
tabs <- unname(tabs)
if (!length(tabs)) stop("no rankings tables listed in ", paste(IRW_RANK_DATASETS, collapse = ", "))

query1 <- function(sql) {
  for (attempt in 1:4) {
    res <- tryCatch(redivis$query(sql)$to_tibble(), error = function(e) {
      message("  ! query failed (attempt ", attempt, "/4): ", conditionMessage(e)); NULL })
    if (!is.null(res)) return(res)
    Sys.sleep(5)
  }
  stop("query failed four times: ", sql)
}
##One query per batch, a UNION ALL over the batch's tables (one query per table
##is almost all Redivis job overhead, see 16_conjoint.R). A UNION ALL of many
##hundred sub-selects fails on Redivis with no message, so a batch is small.
BATCH <- 25
lit <- function(x) sprintf("'%s'", gsub("'", "\\\\'", x))
counts_sql <- function(name, ref)
  sprintf(paste("SELECT %s AS tbl, COUNT(*) AS n_rows, COUNT(DISTINCT id) AS n_respondents,",
                "CAST(MAX(task) AS FLOAT64) AS n_tasks, COUNT(DISTINCT item) AS n_items,",
                "CAST(MAX(resp) AS FLOAT64) AS max_resp,",
                "COUNT(*) - (SELECT COUNT(*) FROM (SELECT DISTINCT id, task, item FROM `%s`)) AS n_duplicate_marks",
                "FROM `%s`"), lit(name), ref, ref)

names_all <- sapply(tabs, function(t) t$name)
refs_all <- sapply(tabs, function(t) t$qualified_reference)
batches <- split(seq_along(tabs), ceiling(seq_along(tabs) / BATCH))
rows <- list()
for (b in batches) {
  message("tables ", b[1], "-", b[length(b)], " of ", length(tabs))
  cnt <- as.data.frame(query1(paste(mapply(counts_sql, names_all[b], refs_all[b]), collapse = " UNION ALL ")))
  for (i in seq_len(nrow(cnt))) {
    r <- cnt[i, ]
    rows[[r$tbl]] <- data.frame(table = r$tbl,
                                n_respondents = as.numeric(r$n_respondents), n_rows = as.numeric(r$n_rows),
                                n_tasks = as.numeric(r$n_tasks), n_items = as.numeric(r$n_items),
                                max_resp = as.numeric(r$max_resp),
                                n_duplicate_marks = as.numeric(r$n_duplicate_marks),
                                stringsAsFactors = FALSE)
  }
}
out <- do.call(rbind, rows)
out <- out[order(out$table), ]
stopifnot(nrow(out) == length(tabs), !anyNA(out$n_respondents))

##A table without a design record still gets its row, with NA design columns,
##so that one missing record cannot stop the weekly run; it is reported here
##and red_up refuses the upload earlier (checks.check_rank_design).
dtab <- read.csv(file.path("..", "data", "rankings", "design_tables.csv"), colClasses = "character",
                 na.strings = character(0), check.names = FALSE)
design_cols <- setdiff(names(dtab), c("table", "evidence"))
dtab <- dtab[, c("table", design_cols)]
names(dtab)[names(dtab) == "n_duplicate_marks"] <- "design_n_duplicate_marks"
out <- merge(out, dtab, by = "table", all.x = TRUE, sort = TRUE)
no_design <- out$table[is.na(out$method)]
if (length(no_design)) message("  ! no design record (data/rankings/design_tables.csv): ",
                               paste(no_design, collapse = ", "))
##The record against the data (reported, not fatal): the counts the script
##wrote into the record should match what is live.
for (k in c("n_ballots_with_marks", "design_n_duplicate_marks", "n_positions")) {
  live_k <- c(n_ballots_with_marks = "n_respondents", design_n_duplicate_marks = "n_duplicate_marks",
              n_positions = "max_resp")[[k]]
  rec <- suppressWarnings(as.numeric(out[[k]]))
  bad <- !is.na(rec) & if (k == "n_positions") out[[live_k]] > rec else out[[live_k]] != rec
  if (any(bad)) message("  ! ", k, " in the design record disagrees with the live table: ",
                        paste(sprintf("%s (%s vs %s)", out$table[bad], rec[bad], out[[live_k]][bad]), collapse = ", "))
}

##na = "": a literal "NA" makes Redivis type the whole column as text.
write.csv(out, "rank_metadata.csv", quote = TRUE, row.names = FALSE, na = "")
message("rank_metadata.csv: ", nrow(out), " tables")
