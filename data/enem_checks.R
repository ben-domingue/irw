## Post-scoring sanity checks for the ENEM ingest (#1942, finding 3).
##
## Everything the year scripts guarded before this file was a guard on the
## INPUTS and the JOINS: off-length response strings, raw codes outside the
## expected alphabet, `9` padding surviving the language mapping, duplicate
## id+item rows after the booklet/position join. Both defects #1942 reports get
## past all of them, because both produce structurally valid output that is
## psychometrically impossible:
##
##   * blanks and double marks scored as wrong answers -- 45% of candidates in
##     the 2013/2014 tables score exactly zero on 45 answered five-option
##     items, which has probability ~4e-5 each;
##   * enem_2019_1mil_lc, where five items are scored 0 for all 1,504
##     candidates who answered them and 73% of items correlate below .05 with
##     the rest of the form.
##
## Both are one-line summaries of the SCORED output. This file computes them.
##
## Sourced by each enem_<year>.R. Self-tested offline against synthetic data:
##
##     Rscript tests/test_enem_checks.R

## ENEM is five-option multiple choice throughout, so a candidate who knows
## nothing still scores 1/5 by guessing. Everything below is calibrated to that.
ENEM_N_OPTIONS <- 5
ENEM_CHANCE    <- 1 / ENEM_N_OPTIONS

## Thresholds. Deliberately far from the healthy tables rather than tight: the
## point is to catch a form that is mis-keyed, not to police difficulty. Across
## the ten healthy tables measured in #1942 the median item-rest correlation
## runs .09-.49 and no table has more than 27% of items below .05.
ENEM_MAX_SHARE_BELOW_CHANCE <- 0.50   # items with p < 1/5
ENEM_MIN_MEDIAN_ITEM_REST   <- 0.05
ENEM_MAX_SHARE_LOW_ITEM_REST<- 0.60
ENEM_MAX_SHARE_ALL_WRONG    <- 0.05   # candidates at exactly zero, all answered

## Item-rest correlations on 45,000,000 rows are not free. A sample of
## candidates is enough for a statistic used as a floor, and the seed makes the
## build reproducible.
ENEM_CHECK_SAMPLE_IDS <- 5000
ENEM_CHECK_SEED       <- 1942

## Returns a named list of statistics; `enem_check_scored()` decides what to do
## about them. Split so the thresholds can be tested without a build.
enem_scored_stats <- function(df, sample_ids = ENEM_CHECK_SAMPLE_IDS,
                              seed = ENEM_CHECK_SEED) {
  stopifnot(all(c("id", "item", "resp") %in% names(df)))
  scored <- df[!is.na(df$resp), c("id", "item", "resp")]
  if (nrow(scored) == 0) stop("no scored responses")

  p <- tapply(scored$resp, scored$item, mean)
  n <- tapply(scored$resp, scored$item, length)

  ids <- unique(scored$id)
  if (length(ids) > sample_ids) {
    set.seed(seed)
    ids <- sample(ids, sample_ids)
  }
  s <- scored[scored$id %in% ids, ]
  w <- tapply(s$resp, list(as.character(s$id), as.character(s$item)), sum)

  ## Item-rest: correlate each item with the total of the OTHER items, so a
  ## mis-keyed item cannot prop up its own correlation.
  tot <- rowSums(w, na.rm = TRUE)
  rest <- vapply(colnames(w), function(j) {
    x <- w[, j]
    ok <- !is.na(x)
    r <- tot[ok] - x[ok]
    if (length(unique(x[ok])) < 2 || length(unique(r)) < 2) return(NA_real_)
    stats::cor(x[ok], r)
  }, numeric(1))

  ## "All wrong" counts only candidates with NO missing item on the form --
  ## a candidate who answered three items and got them wrong is not evidence.
  answered <- rowSums(!is.na(w))
  complete <- answered == ncol(w)
  all_wrong <- if (any(complete)) mean(tot[complete] == 0) else 0

  list(n_items          = length(p),
       median_p         = stats::median(p),
       share_below_chance = mean(p < ENEM_CHANCE),
       zero_variance    = names(p)[p == 0 | p == 1],
       median_item_rest = stats::median(rest, na.rm = TRUE),
       share_low_item_rest = mean(rest < ENEM_MIN_MEDIAN_ITEM_REST, na.rm = TRUE),
       share_all_wrong  = all_wrong,
       n_complete       = sum(complete),
       min_n_per_item   = min(n))
}

## `label` is used in every message so a failing build says which table.
## Stops on the two conditions that cannot be produced by difficulty; warns on
## the rest, because a warning that fires on a legitimately hard form is worse
## than useless.
enem_check_scored <- function(df, label, stats = NULL) {
  st <- if (is.null(stats)) enem_scored_stats(df) else stats
  cat(sprintf("  %s scored: %d items, median p=%.3f, %.0f%% below chance, ",
              label, st$n_items, st$median_p, 100 * st$share_below_chance))
  cat(sprintf("median item-rest=%.3f, %.1f%% of candidates all-wrong\n",
              st$median_item_rest, 100 * st$share_all_wrong))

  if (length(st$zero_variance) > 0) {
    stop(sprintf("%s: %d item(s) scored identically for every candidate (%s). ",
                 label, length(st$zero_variance),
                 paste(utils::head(st$zero_variance, 8), collapse = ", ")),
         "An item nobody gets right is a keying failure, not a hard item.")
  }
  if (!is.na(st$median_item_rest) &&
      st$median_item_rest < ENEM_MIN_MEDIAN_ITEM_REST &&
      st$share_low_item_rest > ENEM_MAX_SHARE_LOW_ITEM_REST) {
    stop(sprintf(paste0("%s: median item-rest correlation %.3f with %.0f%% of ",
                        "items below %.2f. A correctly keyed item correlates ",
                        "positively with the rest of the form regardless of ",
                        "difficulty."),
                 label, st$median_item_rest, 100 * st$share_low_item_rest,
                 ENEM_MIN_MEDIAN_ITEM_REST))
  }
  if (st$share_below_chance > ENEM_MAX_SHARE_BELOW_CHANCE) {
    warning(sprintf("%s: %.0f%% of items sit below the 1/%d chance floor.",
                    label, 100 * st$share_below_chance, ENEM_N_OPTIONS),
            call. = FALSE)
  }
  if (st$share_all_wrong > ENEM_MAX_SHARE_ALL_WRONG) {
    warning(sprintf(paste0("%s: %.1f%% of candidates who answered every item ",
                           "scored exactly zero. On %d five-option items that ",
                           "has probability ~%.0e each -- suspect non-responses ",
                           "being scored as wrong (#1942)."),
                    label, 100 * st$share_all_wrong, st$n_items,
                    (1 - ENEM_CHANCE)^st$n_items),
            call. = FALSE)
  }
  invisible(st)
}
