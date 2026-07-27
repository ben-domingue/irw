# 09_hero_status.R
#
# Computes both blocks of the irw_site homepage hero's data file
# (data/hero_stats.json) from the local metadata.csv already sitting in
# this directory (the output of 01_metadata.R -- run that first if
# metadata.csv is stale or missing):
#
#   - totals: n_tables, n_responses, n_participants, n_items -- direct
#     sums across all tables.
#   - category_breakdown: tables bucketed by their own aggregate
#     n_categories (2/3/4/5/6/7+, excluding <2 and >=12), with n_items and
#     n_responses summed within each bucket.
#
# category_breakdown is a table-level approximation, not the item-level
# classification in Table 2 / Sec. 2.2 of Domingue et al. (2025): a table
# with a genuine mix of item formats (e.g. some 2-category, some
# 5-category items) is bucketed as a whole by its single aggregate value,
# so it will not exactly reproduce the paper's item-level figures. That
# tradeoff is what keeps this cheap -- no Redivis calls, no response-level
# data downloaded, just the metadata.csv columns 01_metadata.R already
# computes. See the footer copy in irw_site's components/_hero_playful.qmd
# for the user-facing version of this caveat.
#
# Usage (run from this directory, same as 01_metadata.R, so the bare
# "metadata.csv" path resolves):
#   cd metadata
#   Rscript 09_hero_status.R ../../irw_site/data/hero_stats.json

library(dplyr)
library(jsonlite)

args     <- commandArgs(trailingOnly = TRUE)
out_path <- if (length(args) >= 1) args[1] else "../../irw_site/data/hero_stats.json"

meta <- read.csv("metadata.csv", stringsAsFactors = FALSE)

totals <- list(
  n_tables       = nrow(meta),
  n_responses    = sum(meta$n_responses, na.rm = TRUE),
  n_participants = sum(meta$n_participants, na.rm = TRUE),
  # round(): some rows' n_items in metadata.csv are non-integer (data-quality
  # quirk upstream in 01_metadata.R's output, not something to silently
  # truncate via as.integer() -- see category_breakdown below for the same
  # treatment).
  n_items        = round(sum(meta$n_items, na.rm = TRUE))
)

MIN_CATEGORIES <- 2   # single-category (no-variance) tables excluded
MAX_CATEGORIES <- 11  # inclusive; >=12 categories excluded, per paper Sec. 2.2

bucket_for <- function(n) {
  if (is.na(n) || n < MIN_CATEGORIES || n > MAX_CATEGORIES) return(NA_character_)
  if (n >= 7) "7+" else as.character(n)
}

classified <- meta |>
  mutate(bucket = vapply(n_categories, bucket_for, character(1))) |>
  filter(!is.na(bucket)) |>
  group_by(bucket) |>
  summarise(n_items = sum(n_items, na.rm = TRUE), n_responses = sum(n_responses, na.rm = TRUE), .groups = "drop")

# Emit one row per known bucket, in fixed order, matching the site's badge
# set -- a bucket with zero tables in this refresh still appears here as
# zero; the front end (not this script) hides a card's badge when its
# bucket is missing or zero.
all_buckets <- c("2", "3", "4", "5", "6", "7+")
breakdown <- lapply(all_buckets, function(b) {
  row <- classified[classified$bucket == b, ]
  # n_items/n_responses stay plain numeric (not as.integer()): summed
  # response counts routinely exceed R's 32-bit integer limit
  # (2,147,483,647) -- e.g. the 2-category bucket alone -- and as.integer()
  # on an out-of-range value silently overflows to NA rather than erroring.
  list(
    n_categories = if (b == "7+") "7+" else as.integer(b),
    n_items      = if (nrow(row)) round(row$n_items) else 0,
    n_responses  = if (nrow(row)) as.numeric(row$n_responses) else 0
  )
})

hero <- list(
  generated_at       = strftime(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
  totals             = totals,
  category_breakdown = breakdown
)

write_json(hero, out_path, auto_unbox = TRUE, pretty = TRUE, na = "null")
message("Wrote hero stats to ", out_path, ":")
message(paste(capture.output(str(hero)), collapse = "\n"))
