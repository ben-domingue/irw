##conj_metadata.csv: one row per table in the conjoint source (every shard in
##IRW_CONJ_DATASETS: irw_conjoint, irw_conjoint_2, ...).
##
##The conjoint layout has no item/resp (data/conjoint/README.md), so the core
##metadata (01_metadata.R) does not apply. This is the conjoint counterpart of
##05_comps.R / 06_nominal.R: rows are carried forward from the repo's
##conj_metadata.csv (the same base 01_metadata.R uses since #2880) and only the
##tables that changed are recomputed. Attribute and outcome columns are read
##from the table schema.
##
##Carry-forward (#2970). Until 2026-10-12 every table was recomputed on every
##run; at 973 tables that was 33 minutes, longer than every other shard stage
##together. ds$list_tables() returns updatedAt, numRows and hash per table in a
##few seconds, and conj_refresh_stamps.csv (tracked) records those three for
##every live table, with what else the recompute learns and a carried row would
##otherwise lack: the attr_ and outcome columns (so list_variables() is skipped)
##and the design-check observations (empty_pairs, max_level_ratio, so the check
##below still runs over the whole corpus). A table is recomputed when it has no
##row in conj_metadata.csv, no stamp, a stamp that differs from the listing, or
##falls in the rolling slice of refresh.per.run oldest-refreshed tables (a safety
##net, as in 01_metadata.R); every other table keeps its row and its stamp, and
##a table no longer listed loses both. Redivis's hash is blind to values
##swapping between rows, so the three stamps are used together: updatedAt moves
##on any re-release. The escape hatch is CONJ_RECOMPUTE_ALL=1 (or deleting the
##stamps file), which recomputes everything, as every run did before.
##
##Columns:
##  table, n_respondents (distinct id), n_rows, n_tasks (largest task index),
##  n_profiles (largest profile index; 1 = single-profile design),
##  n_attributes (attr_ columns), outcomes (choice/rating columns, ";"-joined),
##  n_optout_tasks (tasks where `choice` exists and no profile was chosen; 0
##  for a forced choice, NA when the table has no `choice`).
##Design columns, joined from the hand-kept data/conjoint/design_tables.csv (the
##numbers above come from the data; these come from the scripts' headers and the
##deposits, and say what the numbers mean): country, display_language,
##label_language, restrictions, level_weights, restrictions_note, attr_order,
##survey_weight, presentation, task_source, profile_source.
##Their codes are documented in data/conjoint/README.md.
##
##Design check (reported, not fatal): for each table, the level shares of every
##attribute and the level pairs that never occur together, from one server-side
##query, compared with the record's restrictions and level_weights.
##
##Also writes conj_outcomes.csv: data/conjoint/design_outcomes.csv (one row per
##table x outcome column: type, question wording, opt-out, stored scale and its
##anchors) restricted to the live tables. Pooling across tables needs it: `choice`
##means "vote for" in one table and "admit" in another, and ratings run 1-7, 0-10
##or 0-100.
##
##Runs in run_pipeline.sh with 05/06/07, before 02_biblio.R, which uses
##conj_metadata.csv as the liveness oracle for conj_biblio.
options(scipen=999)
library(redivis)
source("redivis_config.R")
##Every conjoint shard, newest first: the clients resolve a table name
##newest-first, so a name present in two shards is read from the newest. That
##is an upload mistake (red_up updates a table where it lives), so it is
##reported here and the newest copy kept -- never merged silently.
tabs <- list()
tab_shard <- character(0)
for (conj_dataset in rev(IRW_CONJ_DATASETS)) {
  ds <- redivis$organization(IRW_OWNER)$dataset(conj_dataset)
  shard_tabs <- ds$list_tables()
  message("  ", conj_dataset, ": ", length(shard_tabs), " tables")
  for (tab in shard_tabs) {
    if (tab$name %in% names(tabs)) {
      message("  ! ", tab$name, " is in both ", tab_shard[[tab$name]], " and ",
              conj_dataset, "; keeping the copy in ", tab_shard[[tab$name]],
              " -- clients resolve newest-first, so the older one is unreachable")
      next
    }
    tabs[[tab$name]] <- tab
    tab_shard[[tab$name]] <- conj_dataset
  }
}
tabs <- unname(tabs)
if (!length(tabs)) stop("no conjoint tables listed in ", paste(IRW_CONJ_DATASETS, collapse = ", "))

query1 <- function(sql) {
  for (attempt in 1:4) {
    res <- tryCatch(redivis$query(sql)$to_tibble(), error = function(e) {
      message("  ! query failed (attempt ", attempt, "/4): ", conditionMessage(e)); NULL })
    if (!is.null(res)) return(res)
    Sys.sleep(5)
  }
  stop("query failed four times: ", sql)
}

design_obs <- list()     ##table -> observed level shares / empty pairs
gender_attrs <- list()   ##table -> its gender attribute(s), for the crosswalk check

##Tables are queried in batches: one query per batch for each of three things
##(counts, level shares, level pairs), each a UNION ALL over the batch. One
##query per table and kind took about 2.5 minutes a table, almost all of it
##Redivis job overhead -- over nine hours for 216 tables, against the weekly
##job's 120-minute limit.
BATCH <- 20
##A UNION ALL of many hundred sub-selects fails on Redivis with no message (the
##level-pair checks of one batch did), so each query carries at most this many.
MAX_PARTS <- 50
union_query <- function(parts)
  do.call(rbind, lapply(split(parts, ceiling(seq_along(parts) / MAX_PARTS)),
                        function(p) as.data.frame(query1(paste(p, collapse = " UNION ALL ")))))
q <- function(a) sprintf("`%s`", a)
lit <- function(x) sprintf("'%s'", gsub("'", "\\\\'", x))

##---------------------------------------------------------------------------
##What to recompute (header, "Carry-forward").
##---------------------------------------------------------------------------
base_file <- "conj_metadata.csv"
stamps_file <- "conj_refresh_stamps.csv"
refresh.per.run <- 40   ##two batches, about 80 s; sweeps the corpus in ~6 months
computed_cols <- c("table", "n_respondents", "n_rows", "n_tasks", "n_profiles",
                   "n_attributes", "outcomes", "n_optout_tasks")
stamp_cols <- c("table", "updated_at", "num_rows", "hash", "attrs", "outcomes",
                "empty_pairs", "max_level_ratio", "refreshed_at")
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
names(tabs) <- live$table
old <- stamps[match(live$table, stamps$table), ]
is_new <- !live$table %in% base$table
no_stamp <- is.na(old$table)
moved <- !no_stamp & (is.na(old$updated_at) | old$updated_at != live$updated_at |
                      is.na(old$num_rows) | old$num_rows != live$num_rows |
                      is.na(old$hash) | old$hash != live$hash)
dropped <- setdiff(c(base$table, stamps$table), live$table)
all_over <- identical(Sys.getenv("CONJ_RECOMPUTE_ALL"), "1")
redo <- is_new | no_stamp | moved | all_over
##Rolling slice: oldest-refreshed first (never-refreshed sorts first), name as tiebreak.
slice <- character(0)
if (refresh.per.run > 0 && !all_over) {
  cand <- live$table[!redo]
  last <- suppressWarnings(as.POSIXct(old$refreshed_at[match(cand, live$table)], tz = "UTC"))
  slice <- head(cand[order(!is.na(last), last, cand)], refresh.per.run)
  redo[live$table %in% slice] <- TRUE
}
message("stamps: ", sum(!redo), " of ", nrow(live), " table(s) carried forward from ", base_file,
        "; recompute ", sum(redo), " (", sum(is_new), " new, ", sum(no_stamp & !is_new), " unstamped, ",
        sum(moved & !is_new), " changed on Redivis, ", length(slice), " rolling slice",
        if (all_over) ", CONJ_RECOMPUTE_ALL=1" else "", ")",
        if (length(dropped)) paste0("; dropped ", length(dropped), ": ", paste(dropped, collapse = ", ")) else "")
if (any(moved & !is_new)) message("  changed on Redivis: ", paste(live$table[moved & !is_new], collapse = ", "))

split_cols <- function(x) if (is.na(x) || !nzchar(x)) character(0) else strsplit(x, ";", fixed = TRUE)[[1]]
##The recomputed tables read their schema; a carried table's attr_ and outcome
##columns come from its stamp (that is what the stamp is for).
info <- lapply(seq_len(nrow(live)), function(i) {
  tab <- tabs[[i]]
  if (redo[i]) {
    cols <- sapply(tab$list_variables(), function(v) v$name)
    list(name = tab$name, ref = tab$qualified_reference, cols = cols,
         attrs = grep("^attr_", cols, value = TRUE),
         outcomes = grep("^(choice|rating)(_.+)?$", cols, value = TRUE))
  } else {
    attrs <- split_cols(old$attrs[i]); outcomes <- split_cols(old$outcomes[i])
    list(name = tab$name, ref = tab$qualified_reference, cols = c(attrs, outcomes),
         attrs = attrs, outcomes = outcomes)
  }
})
names(info) <- sapply(info, `[[`, "name")
for (t in info) {
  g <- grep("^attr_(.*_)?(gender|sex)$", t$attrs, value = TRUE)
  if (length(g)) gender_attrs[[t$name]] <- g
}
todo <- live$table[redo]
batches <- if (length(todo)) split(todo, ceiling(seq_along(todo) / BATCH)) else list()

##Counts, and opt-out tasks: choice tasks where no profile was chosen (0 for a
##forced choice, NA without a `choice` column).
counts_sql <- function(t) {
  optout <- if ("choice" %in% t$cols)
    sprintf("(SELECT COUNTIF(s = 0) FROM (SELECT SUM(choice) AS s FROM `%s` WHERE choice IS NOT NULL GROUP BY id, task))", t$ref)
  else "CAST(NULL AS INT64)"
  sprintf(paste("SELECT %s AS tbl, COUNT(*) AS n_rows, COUNT(DISTINCT id) AS n_respondents,",
                "CAST(MAX(task) AS FLOAT64) AS n_tasks, CAST(MAX(profile) AS FLOAT64) AS n_profiles,",
                "%s AS n_optout_tasks FROM `%s`"), lit(t$name), optout, t$ref)
}

##Level shares, leaving out '(not shown)', which is the design hiding an
##attribute, not a level.
shares_sql <- function(t)
  sprintf("SELECT %s AS tbl, %s AS a, CAST(%s AS STRING) AS la, COUNT(*) AS n FROM `%s` WHERE CAST(%s AS STRING) != '(not shown)' GROUP BY 3",
          lit(t$name), lit(t$attrs), q(t$attrs), t$ref, q(t$attrs))

##Never-seen level pairs. A pair is tested only when both attributes have at
##most 20 levels and every combination would be expected at least 20 times
##under independent uniform draws, so that a missing pair is unlikely to be
##chance.
test_pairs <- function(t, nlev, n_rows) {
  pairs <- t(combn(t$attrs, 2))
  keep <- apply(pairs, 1, function(p) isTRUE(nlev[p[1]] <= 20 && nlev[p[2]] <= 20 &&
                                               n_rows / (nlev[p[1]] * nlev[p[2]]) >= 20))
  pairs[keep, , drop = FALSE]
}
pairs_sql <- function(t, pp)
  sprintf("SELECT %s AS tbl, '%s|%s' AS p, COUNT(*) AS k FROM (SELECT DISTINCT %s, %s FROM `%s` WHERE CAST(%s AS STRING) != '(not shown)' AND CAST(%s AS STRING) != '(not shown)')",
          lit(t$name), pp[, 1], pp[, 2], q(pp[, 1]), q(pp[, 2]), t$ref, q(pp[, 1]), q(pp[, 2]))

rows <- list()
for (b in batches) {
  message("tables ", match(b[1], todo), "-", match(b[length(b)], todo), " of ", length(todo))
  cnt <- union_query(sapply(info[b], counts_sql))
  with_attrs <- Filter(function(t) length(t$attrs) >= 2, info[b])
  lv <- if (length(with_attrs))
    union_query(unlist(lapply(with_attrs, shares_sql)))
  pair_sql <- character(0); want <- c()
  for (t in with_attrs) {
    l <- lv[lv$tbl == t$name, ]
    nlev <- tapply(l$la, l$a, length)
    n_rows <- as.numeric(cnt$n_rows[cnt$tbl == t$name])
    design_obs[[t$name]] <- list(empty_pairs = 0, n_rows = n_rows,
                                 max_level_ratio = max(tapply(as.numeric(l$n), l$a, function(x) max(x) / min(x))))
    pp <- test_pairs(t, nlev, n_rows)
    if (nrow(pp)) {
      pair_sql <- c(pair_sql, pairs_sql(t, pp))
      want <- c(want, setNames(nlev[pp[, 1]] * nlev[pp[, 2]], paste(t$name, pp[, 1], pp[, 2], sep = "|")))
    }
  }
  if (length(pair_sql)) {
    seen <- union_query(pair_sql)
    short <- as.numeric(seen$k) < want[paste(seen$tbl, seen$p, sep = "|")]
    for (t in unique(seen$tbl[short])) design_obs[[t]]$empty_pairs <- sum(short & seen$tbl == t)
  }
  for (n in b) {
    t <- info[[n]]; r <- cnt[cnt$tbl == n, ]
    rows[[n]] <- data.frame(table = n,
                            n_respondents = as.numeric(r$n_respondents), n_rows = as.numeric(r$n_rows),
                            n_tasks = as.numeric(r$n_tasks), n_profiles = as.numeric(r$n_profiles),
                            n_attributes = length(t$attrs),
                            outcomes = paste(t$outcomes, collapse = ";"),
                            n_optout_tasks = as.numeric(r$n_optout_tasks))
  }
}
fresh <- if (length(rows)) do.call(rbind, rows) else NULL
##Carried rows: the base's computed columns, typed as the fresh ones are.
carried <- base[match(live$table[!redo], base$table), computed_cols]
for (k in setdiff(computed_cols, c("table", "outcomes")))
  carried[[k]] <- suppressWarnings(as.numeric(carried[[k]]))
carried$outcomes[is.na(carried$outcomes)] <- ""
##A rolling-slice table whose numbers moved under an unchanged stamp is worth a
##line: it is the case the stamps are not supposed to let through.
if (length(slice) && !is.null(fresh)) for (n in intersect(slice, base$table)) {
  ov <- base[base$table == n, computed_cols][-1]; nv <- fresh[fresh$table == n, computed_cols][-1]
  cell <- function(x) { x <- as.character(x); if (is.na(x)) "" else x }  ##NA is written as "" (below)
  diff <- names(ov)[sapply(names(ov), function(k) !identical(cell(ov[[k]]), cell(nv[[k]])))]
  if (length(diff)) message("  ! ", n, ": rolling slice found changed ", paste(diff, collapse = ", "),
                            " under an unchanged stamp (", paste(ov[diff], collapse = ", "), " -> ",
                            paste(nv[diff], collapse = ", "), ")")
}
out <- rbind(fresh, carried)
out <- out[order(out$table), ]
stopifnot(nrow(out) == length(tabs), !anyNA(out$n_respondents))
for (n in live$table[!redo]) {
  o <- old[match(n, live$table), ]
  if (nzchar(o$max_level_ratio))
    design_obs[[n]] <- list(empty_pairs = as.numeric(o$empty_pairs), n_rows = out$n_rows[out$table == n],
                            max_level_ratio = as.numeric(o$max_level_ratio))
}

##The stamps for the next run: a recomputed table gets this listing's, a
##carried table keeps its own.
now <- format(Sys.time(), "%Y-%m-%d %H:%M:%S", tz = "UTC")
new_stamps <- do.call(rbind, lapply(seq_len(nrow(live)), function(i) {
  n <- live$table[i]
  if (!redo[i]) return(old[i, stamp_cols])
  o <- design_obs[[n]]
  data.frame(table = n, updated_at = live$updated_at[i], num_rows = live$num_rows[i], hash = live$hash[i],
             attrs = paste(info[[n]]$attrs, collapse = ";"), outcomes = paste(info[[n]]$outcomes, collapse = ";"),
             empty_pairs = if (is.null(o)) "" else as.character(o$empty_pairs),
             max_level_ratio = if (is.null(o)) "" else as.character(o$max_level_ratio),
             refreshed_at = now, stringsAsFactors = FALSE)
}))
new_stamps <- new_stamps[order(tolower(new_stamps$table), new_stamps$table), ]  ##as canonicalize_csv.py sorts
stopifnot(nrow(new_stamps) == nrow(live), !anyNA(new_stamps$hash))
write.csv(new_stamps, stamps_file, quote = TRUE, row.names = FALSE, na = "")
##Fewer than two attributes breaks the conjoint rule (irw_validate.conjoint J4)
##but must not stop the weekly run; report it.
few <- out$table[out$n_attributes < 2]
if (length(few)) message("  ! fewer than 2 attr_ columns: ", paste(few, collapse = ", "))

##A table without a design record still gets its row, with NA design columns, so
##that one missing record cannot stop the weekly run; it is reported here and
##metadata/tests/test_conj_design.py catches it earlier for every table the
##ledger (data/conjoint/candidates.csv) marks built or uploaded.
read_design <- function(f) read.csv(file.path("..", "data", "conjoint", f), colClasses = "character",
                                    na.strings = character(0), check.names = FALSE)
dtab <- read_design("design_tables.csv")
dout <- read_design("design_outcomes.csv")
design_cols <- c("country", "display_language", "label_language", "restrictions",
                 "level_weights", "restrictions_note", "attr_order", "survey_weight",
                 "presentation", "task_source", "profile_source")
out <- merge(out, dtab[, c("table", design_cols)], by = "table", all.x = TRUE, sort = TRUE)
no_design <- out$table[is.na(out$restrictions)]
if (length(no_design)) message("  ! no design record (data/conjoint/design_tables.csv): ",
                               paste(no_design, collapse = ", "))
##Topic tags (data/conjoint/tags.csv; README "Topic tags"): what the study is
##about (domain, multi-select joined with ";") and what a profile represents
##(choice_object). Joined as two more columns, so the packages filter on them
##like any other conj_metadata field. A table with no row gets NA and is
##reported; metadata/tests/test_conj_design.py catches it earlier.
dtags <- read_design("tags.csv")
out <- merge(out, dtags[, c("table", "domain", "choice_object")], by = "table", all.x = TRUE, sort = TRUE)
no_tags <- out$table[is.na(out$domain)]
if (length(no_tags)) message("  ! no topic tags (data/conjoint/tags.csv): ",
                             paste(no_tags, collapse = ", "))
expected <- do.call(rbind, lapply(seq_len(nrow(out)), function(i)
  data.frame(table = out$table[i], outcome = strsplit(out$outcomes[i], ";", fixed = TRUE)[[1]])))
key <- function(d) paste(d$table, d$outcome, sep = ":")
no_outcome <- expected[!key(expected) %in% key(dout), ]
if (nrow(no_outcome)) message("  ! no outcome record (data/conjoint/design_outcomes.csv): ",
                              paste(key(no_outcome), collapse = ", "))
stale <- dout[dout$table %in% out$table & !key(dout) %in% key(expected), ]
if (nrow(stale)) message("  ! outcome record for a column the live table lacks: ",
                         paste(key(stale), collapse = ", "))
outcomes <- dout[key(dout) %in% key(expected), setdiff(names(dout), "evidence")]
outcomes <- outcomes[order(outcomes$table, outcomes$outcome), ]

##The record against the data: a table recorded as having no combination rules
##but with never-seen level pairs, or as uniform but with clearly unequal level
##shares (largest over smallest above 1.5 with at least 2,000 rows).
for (t in intersect(names(design_obs), out$table)) {
  o <- design_obs[[t]]; r <- out[out$table == t, ]
  if (identical(r$restrictions, "none") && o$empty_pairs > 0)
    message("  ! ", t, ": restrictions = none but ", o$empty_pairs, " attribute pair(s) with never-seen combinations")
  if (identical(r$level_weights, "uniform") && o$n_rows >= 2000 && o$max_level_ratio > 1.5)
    message("  ! ", t, ": level_weights = uniform but level shares differ up to ", round(o$max_level_ratio, 1), "x")
}

##A table with a gender attribute but no crosswalk rows does not pool with the
##others (data/conjoint/README.md, "Attribute crosswalk"). Reported, not fatal.
xw <- read_design("crosswalk.csv")
no_xw <- unlist(lapply(names(gender_attrs), function(t) {
  a <- gender_attrs[[t]]
  a <- a[!paste(t, a) %in% paste(xw$table, xw$attribute)]
  if (length(a)) paste0(t, ":", a)
}))
if (length(no_xw)) message("  ! gender attribute with no crosswalk rows (data/conjoint/crosswalk.csv): ",
                           paste(no_xw, collapse = ", "))

##na = "": a literal "NA" makes Redivis type the whole column as text
##(n_optout_tasks, NA for rating-only tables, arrived as a string in v37.1).
write.csv(out, "conj_metadata.csv", quote = TRUE, row.names = FALSE, na = "")
write.csv(outcomes, "conj_outcomes.csv", quote = TRUE, row.names = FALSE, na = "")
message("conj_metadata.csv: ", nrow(out), " tables; conj_outcomes.csv: ", nrow(outcomes), " outcomes")
