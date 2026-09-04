## verify_ecps_sahm_2024_distrust.R  --  batch_022, issue #1831
##
## Re-derives the shipped text from the cached COVIDiSTRESS Round II
## questionnaire via rederive_ecps.py and diffs it, so this checks the mapping
## rather than the plumbing: an evidence string cannot be re-run, a rebuild can.
##
## Run from itemtext/:
##   Rscript itemtables/batch_022/verify_ecps_sahm_2024_distrust.R
##   Rscript itemtables/batch_022/verify_ecps_sahm_2024_distrust.R --resp-csv <path>
source("itemtables/batch_022/verify_ecps_common.R")
verify_ecps("ecps_sahm_2024_distrust", verify_args())
