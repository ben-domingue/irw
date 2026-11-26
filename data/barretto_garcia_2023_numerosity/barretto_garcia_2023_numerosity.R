## Barretto-Garcia, M., de Hollander, G., Grueschow, M., Polania, R.,
## Woodford, M., & Ruff, C. C. (2023). Individual risk attitudes arise from
## noise in neurocognitive magnitude representations. Nature Human Behaviour,
## 7, 1551-1567. doi:10.1038/s41562-023-01643-4
## Data: OpenNeuro ds004259 v1.0.0, doi:10.18112/openneuro.ds004259.v1.0.0.
## Licence: CC0 (dataset_description.json). Psychophysics collection, irw#3686.
##
## Task (fMRI, task-numrisk): two clouds of coins are shown one after the
## other (stim1-<n>, stim2-<n> events) and the participant reports which held
## more coins. First-cloud numerosity is one of 5, 7, 10, 14, 20, 28; the
## second is set relative to it. 6 runs x 36 trials = 216 trials per person,
## 64 participants. The events files carry no column dictionary and the
## dataset has no participants.tsv (so no covariates).
##
## Coding, inferred from the events and checked on every answered trial:
##   - an `error` event marks an incorrect answer;
##   - `left` is the answer "the second cloud had more", `right` "the first
##     had more" (on every answered trial without an `error` event, left
##     occurs exactly when n2 > n1, right exactly when n2 < n1).
##
## Layout:
##   item  = first x second numerosity, e.g. n10_vs_14 (47 pairs; 41 seen by
##           all 64 people, the rest by 52-63)
##   resp  = 1 if correct (no `error` event)
##   rt    = response time in seconds (`response_time`)
##   trial_chose_second = 1 if the answer was "second had more"
##   trial_run (1-6), trial_number (order within person)
##   itemcov_n1, itemcov_n2, itemcov_log_ratio = log(n2 / n1)
## Dropped: 68 trials with no response. BIDS subject labels remapped to
## integers.
##
## Usage: Rscript barretto_garcia_2023_numerosity.R <dir with ev/*.tsv> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw_dir <- if (length(args) >= 1) args[1] else "raw"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

fs <- sort(Sys.glob(file.path(raw_dir, "ev", "sub-*_task-numrisk_run-*_events.tsv")))
stopifnot(length(fs) == 64 * 6)
rows <- list()
for (f in fs) {
  d <- read.delim(f, na.strings = "n/a", stringsAsFactors = FALSE)
  s1 <- which(grepl("^stim1-", d$trial_type))
  for (k in seq_along(s1)) {
    b <- d[s1[k]:(if (k < length(s1)) s1[k + 1] - 1 else nrow(d)), ]
    s2 <- b$trial_type[grepl("^stim2-", b$trial_type)]
    stopifnot(length(s2) == 1)
    ch <- intersect(b$trial_type, c("left", "right"))
    rt <- b$response_time[b$trial_type %in% c("left", "right")]
    rows[[length(rows) + 1]] <- data.frame(
      sub = sub("_task.*", "", basename(f)),
      run = as.integer(sub(".*_run-([0-9]+)_.*", "\\1", basename(f))),
      k = k,
      n1 = as.integer(sub("stim1-", "", b$trial_type[1])),
      n2 = as.integer(sub("stim2-", "", s2)),
      choice = if (length(ch) == 1) ch else NA,
      err = any(b$trial_type == "error"),
      rt = if (length(rt) == 1) rt else NA)
  }
}
x <- do.call(rbind, rows)
x <- x[!is.na(x$choice), ]
stopifnot(all(x$n1 != x$n2),
          all((x$choice == "left") == ((x$n2 > x$n1) != x$err)))

subs <- unique(x$sub)
subs <- subs[order(as.integer(sub("sub-", "", subs)))]
x <- x[order(match(x$sub, subs), x$run, x$k), ]
d <- data.frame(
  id = match(x$sub, subs),
  item = sprintf("n%d_vs_%d", x$n1, x$n2),
  resp = as.integer(!x$err),
  rt = as.numeric(x$rt),
  trial_chose_second = as.integer(x$choice == "left"),
  trial_number = ave(seq_len(nrow(x)), x$sub, FUN = seq_along),
  trial_run = x$run,
  itemcov_log_ratio = round(log(x$n2 / x$n1), 4),
  itemcov_n1 = x$n1,
  itemcov_n2 = x$n2,
  stringsAsFactors = FALSE)
table <- "barretto_garcia_2023_numerosity"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
cat(sprintf("%s rows=%d ids=%d items=%d accuracy=%.3f\n", table, nrow(d),
            length(unique(d$id)), length(unique(d$item)), mean(d$resp)))
print(round(tapply(d$resp, cut(abs(d$itemcov_log_ratio), c(0, .1, .25, .5, 1.5)), mean), 3))
