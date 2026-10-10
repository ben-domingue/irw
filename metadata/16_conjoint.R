##conj_metadata.csv: one row per table in the conjoint source (every shard in
##IRW_CONJ_DATASETS: irw_conjoint, irw_conjoint_2, ...).
##
##The conjoint layout has no item/resp (data/conjoint/README.md), so the core
##metadata (01_metadata.R) does not apply. This is the conjoint counterpart of
##05_comps.R / 06_nominal.R, with two differences:
##  * it recomputes every table on every run rather than carrying rows forward
##    from the published irw_meta table. The source is small, every number comes
##    from a server-side query (no table export, so nothing counts against the
##    Redivis export quota that 05_comps.R's comments describe), and a fresh
##    computation cannot carry forward a stale row for a replaced table;
##  * attribute and outcome columns are read from the table schema.
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

info <- lapply(tabs, function(tab) {
  cols <- sapply(tab$list_variables(), function(v) v$name)
  list(name = tab$name, ref = tab$qualified_reference, cols = cols,
       attrs = grep("^attr_", cols, value = TRUE),
       outcomes = grep("^(choice|rating)(_.+)?$", cols, value = TRUE))
})
names(info) <- sapply(info, `[[`, "name")
for (t in info) {
  g <- grep("^attr_(.*_)?(gender|sex)$", t$cols, value = TRUE)
  if (length(g)) gender_attrs[[t$name]] <- g
}
batches <- split(names(info), ceiling(seq_along(info) / BATCH))

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
  message("tables ", match(b[1], names(info)), "-", match(b[length(b)], names(info)), " of ", length(info))
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
out <- do.call(rbind, rows)
out <- out[order(out$table), ]
stopifnot(nrow(out) == length(tabs), !anyNA(out$n_respondents))
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
