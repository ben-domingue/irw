##################################################################################
## Pick the base a per-table metadata stage starts from: the repo CSV, not the
## published irw_meta table.
##
## 01_metadata.R inlines this same logic (PR #2880, 2026-10-07) after the
## 2026-10-05 revert: #2830 corrected 10 metadata.csv rows on main, irw_meta was
## not re-uploaded, and that night's run started from the published table and
## wrote the stale values back. Stages 05 (comps), 07 (simsyn) and 08 (item
## text) had the identical shape -- "start from published, add what is new,
## write the CSV" -- so a row corrected on main but not yet uploaded was lost
## there in exactly the same way. The repo CSV is what each stage writes and
## what upload_meta.py ships, so it is the right base. Published is still read,
## only to report where the two differ: a row that differs is EXPECTED after a
## merged-but-unuploaded pipeline PR; one where published is ahead of main means
## irw_meta was uploaded from a branch that never merged, and this run will
## overwrite it -- check those before merging.
##
## Usage, from a stage running in metadata/:
##   source("base_guard.R")
##   meta <- choose_base("comps_metadata.csv", published, c("table","n_responses","n_actors"))
##
## Returns a data.frame restricted to `cols`, one row per table. Falls back to
## `published` when the CSV is missing or unreadable (a fresh checkout of an old
## commit), which is what every stage did before this file existed.
##################################################################################

choose_base <- function(csv, published, cols, key = "table", label = csv) {
  published <- as.data.frame(published, stringsAsFactors = FALSE)
  repo <- if (file.exists(csv)) {
    tryCatch(read.csv(csv, stringsAsFactors = FALSE, check.names = FALSE,
                      colClasses = setNames("character", key)),
             error = function(e) { message("  ! unreadable ", csv, ": ", conditionMessage(e)); NULL })
  } else NULL
  if (is.null(repo) || nrow(repo) == 0 || !key %in% names(repo)) {
    message("  ! no usable ", csv, " in the working directory; starting from the published table")
    meta <- published
  } else {
    ##a column published carries that the repo copy lacks (added upstream, or a
    ##first run after a schema change) is filled with NA, never a reason to
    ##fall back to published and lose the repo's rows
    for (nm in setdiff(cols, names(repo))) { message("base: repo ", label, " lacks column ", nm, "; filled with NA"); repo[[nm]] <- NA }
    meta <- repo
    message("base: repo ", label, " (", nrow(repo), " rows); published has ", nrow(published))
    only.pub <- setdiff(published[[key]], repo[[key]])
    only.repo <- setdiff(repo[[key]], published[[key]])
    if (length(only.pub) > 0) message("base: ", length(only.pub), " table(s) in published but not repo: ", paste(head(only.pub, 40), collapse = ", "))
    if (length(only.repo) > 0) message("base: ", length(only.repo), " table(s) in repo but not published: ", paste(head(only.repo, 40), collapse = ", "))
    cmp.cols <- setdiff(intersect(cols, names(published)), key)
    both <- intersect(repo[[key]], published[[key]])
    r <- repo[match(both, repo[[key]]), cmp.cols, drop = FALSE]
    p <- published[match(both, published[[key]]), cmp.cols, drop = FALSE]
    same <- function(a, b) {
      an <- suppressWarnings(as.numeric(a)); bn <- suppressWarnings(as.numeric(b))
      if (all(is.na(an) == is.na(a)) && all(is.na(bn) == is.na(b))) return(isTRUE(all.equal(an, bn)))
      a <- trimws(as.character(a)); b <- trimws(as.character(b))
      a[is.na(a)] <- ""; b[is.na(b)] <- ""
      identical(a, b)
    }
    differs <- vapply(seq_along(both), function(k) !same(unlist(r[k, ]), unlist(p[k, ])), logical(1))
    if (any(differs)) {
      message("base: ", sum(differs), " table(s) whose values differ between repo and published (repo kept): ",
              paste(head(both[differs], 40), collapse = ", "))
    } else message("base: repo and published agree on every shared row")
  }
  dup <- duplicated(meta[[key]])
  if (any(dup)) {
    message("dropping ", sum(dup), " duplicate row(s) from the base: ", paste(unique(meta[[key]][dup]), collapse = ", "))
    meta <- meta[!dup, ]
  }
  meta[, cols, drop = FALSE]
}
