## Tests for data/enem_checks.R (#1942, finding 3).
##
## Offline and deterministic: the checks touch no INEP microdata, so the
## thresholds are exercised on synthetic forms built to look like the two
## defects the issue reports and like a healthy table. Run from `data/`:
##
##     Rscript tests/test_enem_checks.R

source("enem_checks.R")

failures <- 0L
ok    <- function(what) cat("  ok   -", what, "\n")
check <- function(cond, what) {
  if (isTRUE(cond)) ok(what)
  else { cat("  FAIL -", what, "\n"); failures <<- failures + 1L }
}
expect_stop <- function(expr, pattern, what) {
  e <- tryCatch({ suppressWarnings(force(expr)); NULL }, error = conditionMessage)
  if (is.null(e)) { cat("  FAIL -", what, "(no error)\n"); failures <<- failures + 1L }
  else check(grepl(pattern, e, fixed = TRUE), what)
}
expect_warn <- function(expr, pattern, what) {
  w <- character(0)
  withCallingHandlers(suppressMessages(capture.output(force(expr))),
                      warning = function(x) { w <<- c(w, conditionMessage(x));
                                              invokeRestart("muffleWarning") })
  check(any(grepl(pattern, w, fixed = TRUE)), what)
}
quiet <- function(expr) suppressWarnings(capture.output(force(expr)))

## ------------------------------------------------------------- fixtures ---
## A healthy five-option form: one latent ability, items of varying difficulty,
## and a chance floor -- what every ENEM table should look like.
make_form <- function(n_ids = 400, n_items = 45, seed = 1) {
  set.seed(seed)
  theta <- stats::rnorm(n_ids)
  b     <- seq(-1.5, 1.5, length.out = n_items)
  g     <- 1 / 5
  out <- expand.grid(id = seq_len(n_ids), item = seq_len(n_items))
  pr   <- g + (1 - g) * stats::plogis(theta[out$id] - b[out$item])
  out$resp <- stats::rbinom(nrow(out), 1, pr)
  out
}

healthy <- make_form()

cat("a healthy form passes\n")
local({
  st <- enem_scored_stats(healthy)
  check(st$median_p > ENEM_CHANCE, "median p is above the chance floor")
  check(st$median_item_rest > ENEM_MIN_MEDIAN_ITEM_REST,
        "median item-rest clears the floor")
  check(st$share_all_wrong <= ENEM_MAX_SHARE_ALL_WRONG,
        "almost nobody scores exactly zero")
  quiet(enem_check_scored(healthy, "healthy"))
  ok("enem_check_scored() does not stop on it")
})

cat("finding 1 -- non-responses scored as wrong answers\n")
local({
  ## 40% of candidates sat the form but left it blank; scoring blanks as 0
  ## puts them at exactly zero with every item present.
  d <- healthy
  absent <- 1:160
  d$resp[d$id %in% absent] <- 0
  st <- enem_scored_stats(d)
  check(st$share_all_wrong > 0.3,
        "the all-wrong share detects the block (this is the 45% in the issue)")
  expect_warn(enem_check_scored(d, "blank-scored"),
              "scored exactly zero",
              "and enem_check_scored() warns, naming #1942")
})

local({
  ## Once the blanks are NA rather than 0, the same candidates are simply
  ## absent from the form and the statistic returns to normal.
  d <- healthy
  d$resp[d$id %in% 1:160] <- NA
  st <- enem_scored_stats(d)
  check(st$share_all_wrong <= ENEM_MAX_SHARE_ALL_WRONG,
        "dropping them clears it -- the check tracks the fix, not the sample")
})

cat("finding 2 -- a mis-keyed form\n")
local({
  ## enem_2019_1mil_lc: five items scored 0 for everyone who answered them.
  d <- healthy
  d$resp[d$item %in% 1:5] <- 0
  expect_stop(enem_check_scored(d, "dead-items"),
              "scored identically for every candidate",
              "an item nobody gets right stops the build")
})

local({
  ## The wider defect: responses joined to the wrong keys, so scoring is
  ## near-random and item-rest correlations collapse toward zero.
  set.seed(9)
  d <- healthy
  d$resp <- stats::rbinom(nrow(d), 1, 0.16)   # median p .16, as observed
  expect_stop(enem_check_scored(d, "mis-keyed"),
              "median item-rest correlation",
              "a form with no item-total structure stops the build")
})

local({
  ## The check must not fire on a merely HARD form. Same latent structure,
  ## every item shifted well above the sample's ability.
  d <- make_form(seed = 3)
  set.seed(4)
  theta <- stats::rnorm(400); b <- seq(1.5, 4.0, length.out = 45)
  pr <- 1/5 + (1 - 1/5) * stats::plogis(theta[d$id] - b[d$item])
  d$resp <- stats::rbinom(nrow(d), 1, pr)
  st <- enem_scored_stats(d)
  check(st$median_p < 0.35, "the fixture really is a hard form")
  check(st$median_item_rest > ENEM_MIN_MEDIAN_ITEM_REST,
        "a hard form still has item-total structure")
  quiet(enem_check_scored(d, "hard"))
  ok("and is not stopped -- difficulty alone never fails the build")
})

cat("shape\n")
local({
  d <- healthy
  set.seed(11)
  d$resp[sample(nrow(d), 500)] <- NA   # scattered, so no item empties out
  st <- enem_scored_stats(d)
  check(st$n_items == 45, "NA responses are excluded, not counted as items")
  check(st$min_n_per_item > 0, "every item keeps respondents")
})

cat("\n")
if (failures > 0L) { cat(failures, "FAILURE(S)\n"); quit(status = 1L) }
cat("all tests passed\n")
