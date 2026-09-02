## verify_COACH_Chen_2022_WHOQOL_BREF.R  --  batch_016, issue #1831
##
## Re-derives the shipped text from the cached deposit codebook via
## rederive_coach.py and diffs it, so this checks the mapping rather than the
## plumbing: an evidence string cannot be re-run, a rebuild can.
##
## Run from itemtext/:
##   Rscript itemtables/batch_016/verify_COACH_Chen_2022_WHOQOL_BREF.R
##   Rscript itemtables/batch_016/verify_COACH_Chen_2022_WHOQOL_BREF.R --resp-csv <path>
source("itemtables/batch_016/verify_coach_common.R")
verify_coach("COACH_Chen_2022_WHOQOL_BREF", verify_args())
