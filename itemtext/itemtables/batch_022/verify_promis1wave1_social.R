## verify_promis1wave1_social.R  --  batch_022, issue #1831
##
## Re-derives the shipped text from the cached study codebook via
## rederive_promis.py and diffs it, so this checks the mapping rather than the
## plumbing: an evidence string cannot be re-run, a rebuild can.
##
## Run from itemtext/:
##   Rscript itemtables/batch_022/verify_promis1wave1_social.R
##   Rscript itemtables/batch_022/verify_promis1wave1_social.R --resp-csv <path>
source("itemtables/batch_022/verify_common.R")
verify_table("promis1wave1_social", verify_args())
