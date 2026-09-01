##Tests for check_dictionary_dois.R (issue #1764).
##
##Runs offline: fixtures only, nothing touches the network or the sheet. Run it
##from the metadata/ directory:
##
##    Rscript tests/test_dictionary_dois.R
##
##THE TEST THAT MATTERS is goldberg_pattern_is_not_a_violation(). The check's
##whole value is that a curator trusts it; a check that cries wolf on the
##60-table goldberg_2018_* group (one citation, 19 legitimate Dataverse DOIs)
##would be switched off within a week. Suppressing that WITHOUT suppressing the
##drag-fill clusters is the only interesting thing this file asserts.

options(irw.dictcheck.run = FALSE)   ##source the functions, do not run the check
source("check_dictionary_dois.R")

failures <- 0L
check <- function(cond, what) {
    if (isTRUE(cond)) cat("  ok   -", what, "\n")
    else { cat("  FAIL -", what, "\n"); failures <<- failures + 1L }
}

REF_A <- paste("Hyatt, C. S., Lynam, D. R., & Miller, J. D. (2023). Development of a",
               "measure of aggressive behavior expectancies in adults.")
REF_B <- paste("Goldberg, L. R. (2018). Eugene-Springfield Community Sample",
               "[Data set]. Harvard Dataverse.")

frame <- function(tables, dois, refs) data.frame(
    table = tables, Reference = refs, `DOI (for paper)` = dois,
    check.names = FALSE, stringsAsFactors = FALSE)

##-------------------------------------------------------------------- tests ---
cat("check_dictionary_dois\n")

v <- check_dictionary(frame(c("a", "b", "c"),
                            c("10.1002/ab.22088", "10.1002/ab.22089", "10.1002/ab.22090"),
                            rep(REF_A, 3)))
check(length(v) == 1L && v[[1]]$n_tables == 3L, "drag-fill run is flagged")
check(length(v) == 1L && isTRUE(v[[1]]$dragfill), "drag-fill run is labelled as such")

v <- check_dictionary(frame(c("a", "b", "c"), rep("10.1002/ab.22088", 3), rep(REF_A, 3)))
check(length(v) == 0L, "one Reference with one DOI is clean")

##The regression guard: all-data-DOI groups are the one-deposit-per-scale
##pattern, not a contradiction.
v <- check_dictionary(frame(c("a", "b", "c"),
                            c("10.7910/dvn/lhhone", "10.7910/dvn/gcv3zz", "10.7910/dvn/xj6mxh"),
                            rep(REF_B, 3)))
check(length(v) == 0L, "goldberg_pattern_is_not_a_violation")

##A data DOI mixed with an unrelated article DOI is still a contradiction.
v <- check_dictionary(frame(c("a", "b"),
                            c("10.7910/dvn/lhhone", "10.1002/ab.22088"),
                            rep(REF_A, 2)))
check(length(v) == 1L, "data DOI mixed with an article DOI is flagged")

##Allowlisted mixed groups stay quiet, but only at their recorded membership.
v <- check_dictionary(frame(c("a", "b"),
                            c("10.1186/s40359-024-00851-2", "10.34894/fddftj"),
                            rep(REF_A, 2)))
check(length(v) == 0L, "allowlisted mixed group is suppressed")

v <- check_dictionary(frame(c("a", "b", "c"),
                            c("10.1186/s40359-024-00851-2", "10.34894/fddftj", "10.1002/ab.22088"),
                            rep(REF_A, 3)))
check(length(v) == 1L, "allowlist does not cover a group that gained a DOI")

##Normalisation: the same DOI written three ways is one DOI.
v <- check_dictionary(frame(c("a", "b", "c"),
                            c("https://doi.org/10.1002/AB.22088", "doi: 10.1002/ab.22088",
                              "10.1002/ab.22088."),
                            rep(REF_A, 3)))
check(length(v) == 0L, "DOI normalisation collapses url/doi:/case/trailing-dot")

##Two DOIs that merely differ in a trailing number are not a run unless >= 3.
check(!dragfill_run(c("10.1002/ab.22088", "10.1002/ab.22090")), "a 2-DOI gap is not a run")
check(!dragfill_run(c("10.1002/ab.22088", "10.1002/ab.22090", "10.1002/ab.22095")),
      "non-consecutive numbers are not a run")

##Blank DOIs and short references never anchor the invariant.
v <- check_dictionary(frame(c("a", "b"), c("", "10.1002/ab.22088"), rep(REF_A, 2)))
check(length(v) == 0L, "a blank DOI is ignored, not treated as a second value")
v <- check_dictionary(frame(c("a", "b"), c("10.1002/ab.22088", "10.1002/ab.22089"),
                            rep("see paper", 2)))
check(length(v) == 0L, "a too-short Reference cannot anchor the invariant")

cat(if (failures == 0L) "\nall tests passed\n" else sprintf("\n%d FAILURE(S)\n", failures))
quit(status = if (failures == 0L) 0L else 1L)
