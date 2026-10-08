##conj_metadata.csv: one row per table in the conjoint source (irw_conjoint).
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
conj_dataset <- IRW_AUX_DATASETS[["conj"]]

ds <- redivis$organization(IRW_OWNER)$dataset(conj_dataset)
tabs <- ds$list_tables()

query1 <- function(sql) {
  for (attempt in 1:4) {
    res <- tryCatch(redivis$query(sql)$to_tibble(), error = function(e) {
      message("  ! query failed (attempt ", attempt, "/4): ", conditionMessage(e)); NULL })
    if (!is.null(res)) return(res)
    Sys.sleep(5)
  }
  stop("query failed four times: ", sql)
}

one <- function(tab) {
  ref <- tab$qualified_reference
  cols <- sapply(tab$list_variables(), function(v) v$name)
  g <- grep("^attr_(.*_)?(gender|sex)$", cols, value = TRUE)
  if (length(g)) gender_attrs[[tab$name]] <<- g
  outcomes <- grep("^(choice|rating)(_.+)?$", cols, value = TRUE)
  s <- query1(sprintf(paste("SELECT COUNT(*) AS n_rows, COUNT(DISTINCT id) AS n_respondents,",
                            "MAX(task) AS n_tasks, MAX(profile) AS n_profiles FROM `%s`"), ref))
  optout <- NA
  if ("choice" %in% cols) {
    o <- query1(sprintf(paste("SELECT COUNTIF(s = 0) AS n FROM (SELECT SUM(choice) AS s FROM `%s`",
                              "WHERE choice IS NOT NULL GROUP BY id, task)"), ref))
    optout <- as.numeric(o$n[1])
  }
  attrs <- grep("^attr_", cols, value = TRUE)
  if (length(attrs) >= 2) design_obs[[tab$name]] <<- observe_design(ref, attrs, as.numeric(s$n_rows[1]))
  data.frame(table = tab$name,
             n_respondents = as.numeric(s$n_respondents[1]), n_rows = as.numeric(s$n_rows[1]),
             n_tasks = as.numeric(s$n_tasks[1]), n_profiles = as.numeric(s$n_profiles[1]),
             n_attributes = sum(startsWith(cols, "attr_")),
             outcomes = paste(outcomes, collapse = ";"),
             n_optout_tasks = optout)
}

##Level shares and never-seen level pairs, in one query per table, leaving out
##'(not shown)', which is the design hiding an attribute, not a level. A pair is
##tested only when both attributes have at most 20 levels and every combination
##would be expected at least 20 times under independent uniform draws, so that a
##missing pair is unlikely to be chance.
observe_design <- function(ref, attrs, n_rows) {
  q <- function(a) sprintf("`%s`", a)
  shares <- paste(sprintf("SELECT '%s' AS a, CAST(%s AS STRING) AS la, COUNT(*) AS n FROM `%s` WHERE CAST(%s AS STRING) != '(not shown)' GROUP BY 2",
                          attrs, q(attrs), ref, q(attrs)), collapse = " UNION ALL ")
  lv <- query1(paste0("SELECT a, la, n FROM (", shares, ")"))
  nlev <- tapply(lv$la, lv$a, length)
  ratio <- max(tapply(as.numeric(lv$n), lv$a, function(x) max(x) / min(x)))
  pairs <- t(combn(attrs, 2))
  keep <- apply(pairs, 1, function(p) nlev[p[1]] <= 20 && nlev[p[2]] <= 20 &&
                  n_rows / (nlev[p[1]] * nlev[p[2]]) >= 20)
  empty <- 0
  if (any(keep)) {
    pp <- pairs[keep, , drop = FALSE]
    sql <- paste(sprintf("SELECT '%s|%s' AS p, COUNT(*) AS k FROM (SELECT DISTINCT %s, %s FROM `%s` WHERE CAST(%s AS STRING) != '(not shown)' AND CAST(%s AS STRING) != '(not shown)')",
                         pp[, 1], pp[, 2], q(pp[, 1]), q(pp[, 2]), ref, q(pp[, 1]), q(pp[, 2])), collapse = " UNION ALL ")
    seen <- query1(sql)
    want <- setNames(nlev[pp[, 1]] * nlev[pp[, 2]], paste(pp[, 1], pp[, 2], sep = "|"))
    empty <- sum(as.numeric(seen$k) < want[seen$p])
  }
  list(empty_pairs = empty, max_level_ratio = ratio, n_rows = n_rows)
}

design_obs <- list()     ##filled by one(): table -> observed level shares / empty pairs
gender_attrs <- list()   ##filled by one(): table -> its gender attribute(s), for the crosswalk check
out <- do.call(rbind, lapply(tabs, function(t) { message(t$name); one(t) }))
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
