# Checker for the DRAFT conjoint extension standard (conjoint_standard_draft.md).
# Usage: Rscript check_conj.R <file__conj.csv> [<file__design.csv>]
suppressMessages(library(data.table))
a <- commandArgs(TRUE); d <- fread(a[1]); msgs <- character()
err <- function(...) msgs <<- c(msgs, paste("ERROR", ...)); warn <- function(...) msgs <<- c(msgs, paste("NOTE ", ...))
for (c in c("id", "task", "profile")) if (!c %in% names(d)) err(sprintf("[J1] missing required column %s", c))
outs <- intersect(c("choice", "rating"), names(d)); if (!length(outs)) err("[J3] no outcome column (choice or rating)")
at <- grep("^attr_", names(d), value = TRUE); if (length(at) < 2) err("[J4] fewer than two attr_ columns")
ok <- setdiff(names(d), c("id", "task", "profile", "choice", "rating", "rt", "wave", "treat", "date", "weight"))
bad <- ok[!grepl("^(attr_|attrpos_|cov_|trial_)", ok)]; if (length(bad)) err("[J7] undefined columns:", paste(bad, collapse = ", "))
if (all(c("id", "task", "profile") %in% names(d))) {
  dup <- d[, .N, .(id, task, profile)][N > 1]; if (nrow(dup)) err(sprintf("[J2] %d duplicated id-task-profile rows", nrow(dup)))
  pt <- d[, .N, .(id, task)]; warn(sprintf("profiles per task: %s", paste(names(table(pt$N)), table(pt$N), sep = " x", collapse = "; ")))
}
if ("choice" %in% names(d)) {
  if (any(!d$choice %in% c(0, 1, NA))) err("[J3] choice not 0/1")
  s <- d[!is.na(choice), .(s = sum(choice)), .(id, task)]
  if (any(s$s > 1)) err(sprintf("[J3] %d tasks with more than one chosen profile", sum(s$s > 1)))
  if (any(s$s == 0)) warn(sprintf("[J3] %d tasks with no chosen profile: valid only if the design metadata declares an opt-out", sum(s$s == 0)))
}
if ("rating" %in% names(d) && !is.numeric(d$rating)) err("[J3] rating not numeric")
if ("rating" %in% names(d) && anyNA(d$rating)) warn(sprintf("[J3] %d rows with missing rating (allowed only when choice is present)", sum(is.na(d$rating))))
na_all <- sapply(d[, ..at], function(x) all(is.na(x))); if (any(na_all)) err("[J4] attr_ column entirely missing")
nr <- uniqueN(d$id); if (nr < 100) warn(sprintf("[intake] %d respondents < 100", nr))
if (length(a) > 1) { s <- fread(a[2]); miss <- setdiff(sub("^attr_", "", at), s$attribute); if (length(miss)) err("[J5] attributes missing from design sidecar:", paste(miss, collapse = ", ")) }
cat(basename(a[1]), if (any(startsWith(msgs, "ERROR"))) "FAILS draft standard" else "conforms to draft standard", "\n"); if (length(msgs)) cat(paste0("  ", msgs), sep = "\n")
