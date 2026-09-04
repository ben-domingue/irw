## verify_ecps_sahm_2024_vaccine.R  --  batch_022, issue #1831
##
## Re-derives the shipped text from the administered COVIDiSTRESS Round II
## instrument via rederive_ecps.py and diffs it, so this checks the mapping
## rather than the plumbing: an evidence string cannot be re-run, a rebuild can.
##
## Run from itemtext/:
##   Rscript itemtables/batch_022/verify_ecps_sahm_2024_vaccine.R
##   Rscript itemtables/batch_022/verify_ecps_sahm_2024_vaccine.R --resp-csv <path>
source("itemtables/batch_022/verify_ecps_common.R")
verify_ecps("ecps_sahm_2024_vaccine", verify_args())
