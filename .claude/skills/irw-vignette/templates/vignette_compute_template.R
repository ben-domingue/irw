# <NAME>_compute.R
#
# TODO(agent): One paragraph — what question this answers, what model/test
# is fit per table, and why it needs to run across many IRW tables rather
# than living inline in the .qmd. Get this from the user's answer to the
# "what's the actual question and method" prompt in SKILL.md step 2 —
# do not invent it.
#
# Produces the precomputed results loaded by <NAME>.qmd.
#
# Output: <NAME>_data/<NAME>_results.rds
#         <NAME>_data/references.bib
#
# Usage:
#   Rscript vignettes/<NAME>_compute.R   # from project root

library(irw)
library(dplyr)
library(purrr)
library(furrr)
library(tibble)
# TODO(agent): add whatever modeling package the fit function below needs
# (psych, mirt, lavaan, lme4, ... — see CLAUDE.md's "Key R packages" list
# in the website repo for what's already in renv.lock).

set.seed(<SEED>) # TODO(agent): pick a fixed seed, e.g. today's date as YYYYMMDD

out_dir  <- "vignettes/<NAME>_data"
fits_dir <- file.path(out_dir, "fits")
dir.create(fits_dir, recursive = TRUE, showWarnings = FALSE)
bib_file <- file.path(out_dir, "references.bib")

# TODO(agent): fill these from the user's dataset-selection answer. Every
# threshold here should trace back to something the user said (a compute
# constraint, a construct-type restriction, a minimum sample size) — don't
# pick numbers that merely look plausible.
MIN_ITEMS        <- NA
MAX_ITEMS        <- NA
MIN_PARTICIPANTS <- NA
MAX_N            <- 10000 # downsample respondents before fitting, mirrors dimensionality_compute.R
PILOT            <- TRUE  # TRUE: run on a small hand-picked/sampled subset for a draft page
PILOT_N_TABLES   <- 15

# ==============================================================================
# 1. Select datasets
# ==============================================================================

all_candidates <- irw_filter(
  n_items        = c(MIN_ITEMS, MAX_ITEMS),
  n_participants = c(MIN_PARTICIPANTS, Inf)
  # TODO(agent): add any other irw_filter() criteria the user specified
  # (construct_type, item_format, etc.)
)

message("Candidate tables: ", length(all_candidates))

if (PILOT) {
  # TODO(agent): ask the user for 1-3 "known-good" tables where the expected
  # answer is obvious (a table that should clearly pass, one that should
  # clearly fail) — these make the pilot a real sanity check, not just a
  # smaller random sample. See dimensionality_compute.R's
  # psychtools_bfi / 4thgrade_math_sirt pair for the pattern.
  known_good <- intersect(c(), all_candidates)
  remainder  <- setdiff(all_candidates, known_good)
  tables <- c(known_good, sample(remainder, min(PILOT_N_TABLES - length(known_good), length(remainder))))
  message("PILOT run: ", length(tables), " tables selected.")
} else {
  tables <- all_candidates
}

# Table-level construct_type/item_format for by-construct breakdowns, if used.
tags_meta <- tryCatch(irw_tags(tables = tables), error = function(e) {
  message("irw_tags() failed: ", conditionMessage(e))
  NULL
})

# ==============================================================================
# 2. Per-table computation
#
# TODO(agent): this is the core of the vignette and must come from the
# user's answer to the "actual statistical method" prompt — do not invent
# a model, a fit statistic, or a flagging threshold on your own. Every
# tryCatch below is required: one failed table must never crash the batch.
# ==============================================================================

fit_one_table <- function(table_name) {
  message("  Processing: ", table_name)

  df <- tryCatch(irw_fetch(table_name), error = function(e) {
    message("    fetch failed: ", conditionMessage(e))
    NULL
  })
  if (is.null(df)) return(NULL)

  unique_ids <- unique(df$id)
  if (length(unique_ids) > MAX_N) {
    df <- df[df$id %in% sample(unique_ids, MAX_N), ]
  }

  resp <- irw_long2resp(df)
  resp$id <- NULL

  # Drop zero-variance items — near-universal cleanup step across existing
  # compute scripts (dimensionality, local_dependence, 2pl_across_datasets).
  resp <- resp[, sapply(resp, function(x) length(unique(na.omit(x))) > 1), drop = FALSE]

  # TODO(agent): the actual model/test fit, wrapped in tryCatch, returning
  # NULL (and a message()) on any failure rather than raising.
  #
  # result <- tryCatch({ ... }, error = function(e) {
  #   message("    fit failed: ", conditionMessage(e))
  #   NULL
  # })
  # if (is.null(result)) return(NULL)

  meta_row <- if (!is.null(tags_meta)) tags_meta[tags_meta$table == table_name, ] else NULL
  construct_type <- if (!is.null(meta_row) && nrow(meta_row) > 0) meta_row$construct_type[1] else NA_character_
  item_format    <- if (!is.null(meta_row) && nrow(meta_row) > 0) meta_row$item_format[1] else NA_character_

  list(
    summary = tibble(
      table          = table_name,
      n_items        = ncol(resp),
      n_participants = nrow(resp),
      construct_type = construct_type,
      item_format    = item_format
      # TODO(agent): add the actual per-table result columns the .qmd plots/tables need
    )
    # TODO(agent): add any other keyed per-table objects the .qmd needs for
    # a sanity-check figure (e.g. dimensionality's `eigenvalues`, local
    # dependence's `q3_matrices`) — keep these small, they all get held in
    # memory during the combine step.
  )
}

# ==============================================================================
# 3. Run, writing each result to disk as it completes
#    If the script crashes or is interrupted, re-running skips finished tables.
# ==============================================================================

fit_to_disk <- function(table_name) {
  out_file <- file.path(fits_dir, paste0(table_name, ".rds"))
  if (file.exists(out_file)) {
    message("  Skipping (already done): ", table_name)
    return(invisible(NULL))
  }
  result <- tryCatch(fit_one_table(table_name), error = function(e) {
    message("    unexpected error for ", table_name, ": ", conditionMessage(e))
    NULL
  })
  if (!is.null(result)) saveRDS(result, out_file)
}

plan(multisession, workers = min(4, parallel::detectCores() %/% 2))
message("\nAnalyzing ", length(tables), " candidate tables...")
future_map(tables, fit_to_disk, .options = furrr_options(seed = TRUE))
plan(sequential)

# ==============================================================================
# 4. Combine results
# ==============================================================================

all_raw <- map(tables, function(tbl) {
  f <- file.path(fits_dir, paste0(tbl, ".rds"))
  if (file.exists(f)) readRDS(f) else NULL
}) |> compact()

all_summary <- map(all_raw, "summary") |> compact() |> bind_rows()

message("\nDone. ", nrow(all_summary), " tables with usable results out of ",
        length(tables), " candidates.")

# ==============================================================================
# 5. Save combined output
# ==============================================================================

saveRDS(
  list(
    summary          = all_summary,
    # TODO(agent): include any other keyed lists collected above
    candidate_tables = tables,
    n_all_candidates = length(all_candidates),
    pilot            = PILOT,
    date_run         = Sys.Date(),
    session          = sessionInfo()
  ),
  file = file.path(out_dir, "<NAME>_results.rds")
)

message("Saved to ", out_dir, "/<NAME>_results.rds")

# ==============================================================================
# 6. Generate citations
# ==============================================================================

tryCatch(
  irw_save_bibtex(unique(all_summary$table), output_file = bib_file),
  error = function(e) message("  bibtex generation failed: ", conditionMessage(e))
)

# TODO(agent): if the Motivation/Limitations text cites methods papers (not
# IRW datasets), append hand-written @article/@book entries the same way
# dimensionality_compute.R does at the bottom of its file — ask the user
# for the citation(s) rather than fabricating one.
