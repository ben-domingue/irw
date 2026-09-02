## verify_promis1wave1_fatigue.R  --  batch_016, issue #1831
##
## Re-derives the shipped text from the cached study codebook via
## rederive_promis.py and diffs it, so this checks the mapping rather than the
## plumbing: an evidence string cannot be re-run, a rebuild can.
##
## Run from itemtext/:
##   Rscript itemtables/batch_016/verify_promis1wave1_fatigue.R
##   Rscript itemtables/batch_016/verify_promis1wave1_fatigue.R --resp-csv <path>
source("itemtables/batch_016/verify_common.R")
verify_table("promis1wave1_fatigue", verify_args())
