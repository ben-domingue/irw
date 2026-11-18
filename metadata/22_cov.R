##cov_metadata.csv: one row per matrix in the covariance family (irw_cov,
##source = "cov"), i.e. per table x group. Standard: data/covariance/README.md.
##
##A cov table holds a published matrix, not responses -- stat, var1, var2,
##value, n, and optionally group -- so 01_metadata.R's response statistics mean
##nothing for it. This is the covariance counterpart of 18_rankings.R.
##
##Columns computed from the live table:
##  table, group ("" when the table has no group column), n_vars, n_obs (the
##  largest cell n: the matrix N, or the largest pairwise n), stat ("cor" or
##  "cov"), has_sd, has_mean, min_eigenvalue, is_pd (min_eigenvalue > 0; a
##  non-PD matrix is kept as published and flagged here, rule V8), and
##  n_missing_cells (lower-triangle cells the source did not report, held as
##  rows with an empty value; Ben, 2026-11-18). For a matrix with blank cells,
##  min_eigenvalue and is_pd describe its complete part: the matrix after
##  dropping the fewest variables that leaves no blank, the same rule as
##  irw_validate.cov.complete_drop and the packages' complete = TRUE.
##Record columns, joined from the hand-kept data/covariance/matrices.csv on
##table + group: matrix_type, missing, population, source_citation,
##source_location, via, capture, verified, licence, licence_source, variables
##(published variable order and labels, " | "-separated; the packages re-sort a
##fetched table by it), notes. Every record column is copied, so a new one
##needs no change here.
##
##Every table is downloaded and recomputed each run. The tables are tiny (a
##24-variable matrix is 300 rows) and the family is small; when it is not, add
##the carry-forward stamps 18_rankings.R uses.
##
##Runs in run_pipeline.sh with 05/06/07/16/18, before 02_biblio.R, which uses
##cov_metadata.csv as the liveness oracle for cov_biblio.
options(scipen=999)
library(redivis)
source("redivis_config.R")

if (!"cov" %in% names(IRW_AUX_DATASETS)) stop("irw_cov is not registered in IRW_AUX_DATASETS")
ds <- redivis$organization(IRW_OWNER)$dataset(IRW_AUX_DATASETS[["cov"]])
tabs <- ds$list_tables()
message("  ", IRW_AUX_DATASETS[["cov"]], ": ", length(tabs), " tables")
if (!length(tabs)) stop("no tables listed in ", IRW_AUX_DATASETS[["cov"]])

##The fewest variables to drop so no cell is blank; ties keep the variables
##listed first (candidates tried latest-first). Mirrors complete_drop() in
##irw_validate/cov.py -- keep the two in step.
complete_drop <- function(v, m, exact_max = 20) {
  idx <- which(is.na(m) & lower.tri(m), arr.ind = TRUE)
  if (!nrow(idx)) return(character(0))
  pairs <- lapply(seq_len(nrow(idx)), function(i) v[idx[i, ]])
  involved <- unique(unlist(pairs))
  involved <- involved[order(-match(involved, v))]
  covers <- function(drop) all(vapply(pairs, function(p) any(p %in% drop), logical(1)))
  if (length(involved) <= exact_max) {
    for (size in seq_along(involved)) {
      cand <- utils::combn(involved, size, simplify = FALSE)
      for (drop in cand) if (covers(drop)) return(v[v %in% drop])
    }
  }
  drop <- character(0); left <- pairs
  while (length(left)) {
    cnt <- vapply(involved, function(x) sum(vapply(left, function(p) x %in% p, logical(1))), numeric(1))
    best <- involved[order(-cnt, -match(involved, v))][1]
    drop <- c(drop, best)
    left <- Filter(function(p) !best %in% p, left)
  }
  v[v %in% drop]
}

one_matrix <- function(name, d, g) {
  cells <- d[d$stat %in% c("cor", "cov"), , drop = FALSE]
  v <- unique(c(cells$var1, cells$var2))
  m <- matrix(NA_real_, length(v), length(v), dimnames = list(v, v))
  m[cbind(cells$var1, cells$var2)] <- cells$value
  m[cbind(cells$var2, cells$var1)] <- cells$value
  ##A blank cell has no eigenvalues; judge the complete part (header).
  keep <- setdiff(v, complete_drop(v, m))
  ev <- if (!length(keep) || anyNA(m[keep, keep])) NA_real_ else
    min(eigen(m[keep, keep, drop = FALSE], symmetric = TRUE, only.values = TRUE)$values)
  data.frame(table = name, group = g, n_vars = length(v), n_obs = max(as.numeric(cells$n)),
             stat = paste(unique(cells$stat), collapse = "+"),
             has_sd = any(d$stat == "sd"), has_mean = any(d$stat == "mean"),
             min_eigenvalue = signif(ev, 6), is_pd = if (is.na(ev)) NA else ev > 0,
             n_missing_cells = sum(is.na(m[lower.tri(m, diag = TRUE)])),
             stringsAsFactors = FALSE)
}

rows <- list()
var_sets <- list()   # table \r group -> the matrix's variable names, for the `variables` check
for (tab in tabs) {
  d <- NULL
  for (attempt in 1:4) {
    d <- tryCatch(as.data.frame(tab$to_tibble()), error = function(e) {
      message("  ! ", tab$name, " (attempt ", attempt, "/4): ", conditionMessage(e)); NULL })
    if (!is.null(d)) break
    Sys.sleep(5)
  }
  if (is.null(d)) stop("could not read ", tab$name)
  d$value <- as.numeric(d$value)
  d$var2 <- ifelse(is.na(d$var2) | d$var2 == "", NA, d$var2)
  if ("group" %in% names(d)) {
    d$group[is.na(d$group)] <- ""
    for (g in unique(d$group)) rows[[length(rows) + 1]] <- one_matrix(tab$name, d[d$group == g, ], g)
  } else {
    d$group <- ""
    rows[[length(rows) + 1]] <- one_matrix(tab$name, d, "")
  }
  cl <- d[d$stat %in% c("cor", "cov"), , drop = FALSE]
  for (g in unique(d$group))
    var_sets[[paste(tab$name, g, sep = "\r")]] <- unique(c(cl$var1[cl$group == g], cl$var2[cl$group == g]))
}
out <- do.call(rbind, rows)

##A table without a record row still gets its row, with NA record columns, so
##one missing record cannot stop the run; it is reported here and red_up
##refuses the upload earlier (checks.check_cov_record).
rec <- read.csv(file.path("..", "data", "covariance", "matrices.csv"), colClasses = "character",
                na.strings = character(0), check.names = FALSE)
rec_cols <- setdiff(names(rec), c("table", "group", "n_obs"))
out <- merge(out, rec[, c("table", "group", "n_obs", rec_cols)], by = c("table", "group"),
             all.x = TRUE, sort = FALSE, suffixes = c("", "_record"))
no_rec <- unique(out$table[is.na(out$matrix_type)])
if (length(no_rec)) message("  ! no record (data/covariance/matrices.csv): ", paste(no_rec, collapse = ", "))
##The record against the data (reported, not fatal).
bad <- !is.na(out$n_obs_record) & as.numeric(out$n_obs_record) != out$n_obs
if (any(bad)) message("  ! n_obs in matrices.csv disagrees with the live table: ",
                      paste(sprintf("%s/%s (%s vs %s)", out$table[bad], out$group[bad],
                                    out$n_obs_record[bad], out$n_obs[bad]), collapse = ", "))
out$n_obs_record <- NULL
##`variables` against the live matrix (reported, not fatal; red_up refuses the
##upload of a mismatched record).
live_vars <- list()
if ("variables" %in% names(out)) {
  for (i in seq_len(nrow(out))) {
    f <- out$variables[i]
    if (is.na(f) || !nzchar(trimws(f))) next
    listed <- trimws(sub(" = .*$", "", strsplit(f, " | ", fixed = TRUE)[[1]]))
    k <- paste(out$table[i], out$group[i], sep = "\r")
    if (!is.null(var_sets[[k]]) && (anyDuplicated(listed) || !setequal(listed, var_sets[[k]])))
      message("  ! `variables` in matrices.csv does not match the live matrix: ", out$table[i],
              if (nzchar(out$group[i])) paste0(" / ", out$group[i]) else "")
  }
}
nonpd <- out$table[out$is_pd %in% FALSE]
if (length(nonpd)) message("  non-positive-definite as published (V8, kept): ", paste(unique(nonpd), collapse = ", "))

out <- out[order(tolower(out$table), out$table, out$group), ]
write.csv(out, "cov_metadata.csv", quote = TRUE, row.names = FALSE, na = "")
message("wrote cov_metadata.csv: ", nrow(out), " matrices in ", length(unique(out$table)), " tables")
