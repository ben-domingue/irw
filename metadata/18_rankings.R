##rank_metadata.csv: one row per table in the rankings source (every shard in
##IRW_RANK_DATASETS: irw_rank, ...).
##
##A rankings table keeps the core column names, but resp is a position and a
##repeated id x item is a duplicate mark kept by the standard
##(data/rankings/README.md), so the core metadata (01_metadata.R) would misread
##it. This is the rankings counterpart of 16_conjoint.R.
##
##Carry-forward (#3039, the conjoint pattern of #2970). ds$list_tables()
##returns updatedAt, numRows and hash per table, and rank_refresh_stamps.csv
##(tracked) records those three for every live table. A table is recomputed
##when it has no row in rank_metadata.csv, no stamp, or a stamp that differs
##from the listing; every other table keeps its row and its stamp, and a table
##no longer listed loses both. Redivis's hash is blind to values swapping
##between rows, so the three stamps are used together: updatedAt moves on any
##re-release. The escape hatch is RANK_RECOMPUTE_ALL=1 (or deleting the stamps
##file), which recomputes everything. The design join below is not stamped:
##design_tables.csv is hand-kept and the join is cheap, so it is redone every run.
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

##---------------------------------------------------------------------------
##What to recompute (header, "Carry-forward").
##---------------------------------------------------------------------------
base_file <- "rank_metadata.csv"
stamps_file <- "rank_refresh_stamps.csv"
computed_cols <- c("table", "n_respondents", "n_rows", "n_tasks", "n_items", "max_resp", "n_duplicate_marks")
stamp_cols <- c("table", "updated_at", "num_rows", "hash", "refreshed_at")
read_tracked <- function(f) {
  if (!file.exists(f)) return(NULL)
  d <- tryCatch(read.csv(f, colClasses = "character", na.strings = character(0), check.names = FALSE),
                error = function(e) { message("  ! unreadable ", f, ", ignoring it: ", conditionMessage(e)); NULL })
  if (is.null(d) || !nrow(d)) NULL else d[!duplicated(d$table, fromLast = TRUE), ]
}
base <- read_tracked(base_file)
if (!is.null(base) && !all(computed_cols %in% names(base))) {
  message("  ! ", base_file, " lacks ", paste(setdiff(computed_cols, names(base)), collapse = ", "), "; recomputing everything")
  base <- NULL
}
stamps <- read_tracked(stamps_file)
if (!is.null(stamps) && !all(stamp_cols %in% names(stamps))) {
  message("  ! ", stamps_file, " lacks ", paste(setdiff(stamp_cols, names(stamps)), collapse = ", "), "; recomputing everything")
  stamps <- NULL
}
if (is.null(base)) base <- data.frame(matrix(character(0), 0, length(computed_cols), dimnames = list(NULL, computed_cols)))
if (is.null(stamps)) stamps <- data.frame(matrix(character(0), 0, length(stamp_cols), dimnames = list(NULL, stamp_cols)))

prop <- function(tab, k) { v <- tab$properties[[k]]; if (is.null(v)) NA else v }
live <- data.frame(table = sapply(tabs, function(t) t$name),
                   updated_at = sapply(tabs, function(t) sprintf("%.0f", as.numeric(prop(t, "updatedAt")))),
                   num_rows = sapply(tabs, function(t) sprintf("%.0f", as.numeric(prop(t, "numRows")))),
                   hash = sapply(tabs, function(t) as.character(prop(t, "hash"))),
                   stringsAsFactors = FALSE)
old <- stamps[match(live$table, stamps$table), ]
is_new <- !live$table %in% base$table
no_stamp <- is.na(old$table)
moved <- !no_stamp & (is.na(old$updated_at) | old$updated_at != live$updated_at |
                      is.na(old$num_rows) | old$num_rows != live$num_rows |
                      is.na(old$hash) | old$hash != live$hash)
dropped <- setdiff(c(base$table, stamps$table), live$table)
all_over <- identical(Sys.getenv("RANK_RECOMPUTE_ALL"), "1")
redo <- is_new | no_stamp | moved | all_over
message("stamps: ", sum(!redo), " of ", nrow(live), " table(s) carried forward from ", base_file,
        "; recompute ", sum(redo), " (", sum(is_new), " new, ", sum(no_stamp & !is_new), " unstamped, ",
        sum(moved & !is_new), " changed on Redivis",
        if (all_over) ", RANK_RECOMPUTE_ALL=1" else "", ")",
        if (length(dropped)) paste0("; dropped ", length(dropped), ": ", paste(dropped, collapse = ", ")) else "")
if (any(moved & !is_new)) message("  changed on Redivis: ", paste(live$table[moved & !is_new], collapse = ", "))

names_all <- sapply(tabs, function(t) t$name)
refs_all <- sapply(tabs, function(t) t$qualified_reference)
todo <- which(redo)
batches <- split(todo, ceiling(seq_along(todo) / BATCH))
rows <- list()
for (b in batches) {
  message("recompute ", length(b), " table(s): ", names_all[b[1]], if (length(b) > 1) paste0(" .. ", names_all[b[length(b)]]) else "")
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
fresh <- if (length(rows)) do.call(rbind, rows) else NULL
##Carried rows: the base's computed columns, typed as the fresh ones are.
carried <- base[match(live$table[!redo], base$table), computed_cols]
for (k in setdiff(computed_cols, "table"))
  carried[[k]] <- suppressWarnings(as.numeric(carried[[k]]))
out <- rbind(fresh, carried)
out <- out[order(out$table), ]
stopifnot(nrow(out) == length(tabs), !anyNA(out$n_respondents))

##The stamps for the next run: a recomputed table gets this listing's, a
##carried table keeps its own.
now <- format(Sys.time(), "%Y-%m-%d %H:%M:%S", tz = "UTC")
new_stamps <- do.call(rbind, lapply(seq_len(nrow(live)), function(i) {
  if (!redo[i]) return(old[i, stamp_cols])
  data.frame(table = live$table[i], updated_at = live$updated_at[i], num_rows = live$num_rows[i],
             hash = live$hash[i], refreshed_at = now, stringsAsFactors = FALSE)
}))
new_stamps <- new_stamps[order(tolower(new_stamps$table), new_stamps$table), ]  ##as canonicalize_csv.py sorts
stopifnot(nrow(new_stamps) == nrow(live), !anyNA(new_stamps$hash))
write.csv(new_stamps, stamps_file, quote = TRUE, row.names = FALSE, na = "")

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
