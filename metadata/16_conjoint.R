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
##
##Not yet wired into run_pipeline.sh: that happens when `conj` is registered in
##redivis_config.R together with the package configs (the parity check compares
##all three). Until then the dataset name falls back to "irw_conjoint".
options(scipen=999)
library(redivis)
source("redivis_config.R")
conj_dataset <- if ("conj" %in% names(IRW_AUX_DATASETS)) IRW_AUX_DATASETS[["conj"]] else "irw_conjoint"

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
  outcomes <- grep("^(choice|rating)(_.+)?$", cols, value = TRUE)
  s <- query1(sprintf(paste("SELECT COUNT(*) AS n_rows, COUNT(DISTINCT id) AS n_respondents,",
                            "MAX(task) AS n_tasks, MAX(profile) AS n_profiles FROM `%s`"), ref))
  optout <- NA
  if ("choice" %in% cols) {
    o <- query1(sprintf(paste("SELECT COUNTIF(s = 0) AS n FROM (SELECT SUM(choice) AS s FROM `%s`",
                              "WHERE choice IS NOT NULL GROUP BY id, task)"), ref))
    optout <- as.numeric(o$n[1])
  }
  data.frame(table = tab$name,
             n_respondents = as.numeric(s$n_respondents[1]), n_rows = as.numeric(s$n_rows[1]),
             n_tasks = as.numeric(s$n_tasks[1]), n_profiles = as.numeric(s$n_profiles[1]),
             n_attributes = sum(startsWith(cols, "attr_")),
             outcomes = paste(outcomes, collapse = ";"),
             n_optout_tasks = optout)
}

out <- do.call(rbind, lapply(tabs, function(t) { message(t$name); one(t) }))
out <- out[order(out$table), ]
stopifnot(nrow(out) == length(tabs), !anyNA(out$n_respondents), all(out$n_attributes >= 2))
write.csv(out, "conj_metadata.csv", quote = TRUE, row.names = FALSE)
message("conj_metadata.csv: ", nrow(out), " tables")
