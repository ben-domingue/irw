## verify_ecps_sahm_2024_moral.R  --  batch_016, issue #1831
##
## Re-derives the shipped text from the cached COVIDiSTRESS Round II
## questionnaire via rederive_ecps.py and diffs it, so this checks the mapping
## rather than the plumbing: an evidence string cannot be re-run, a rebuild can.
##
## Run from itemtext/:
##   Rscript itemtables/batch_016/verify_ecps_sahm_2024_moral.R
##   Rscript itemtables/batch_016/verify_ecps_sahm_2024_moral.R --resp-csv <path>
source("itemtables/batch_016/verify_ecps_common.R")
verify_ecps("ecps_sahm_2024_moral", verify_args())
