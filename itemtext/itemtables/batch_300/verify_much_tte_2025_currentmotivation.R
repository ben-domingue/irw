# Verification for much_tte_2025_currentmotivation (#2228, batch_300).
# See verify_much_tte_common.R for the source and the shared routes.
TB <- "much_tte_2025_currentmotivation"; NITEM <- 3
SCALE_NOTE <- paste0("the paper states 'a visual analogue scale from strongly disagree to strongly\n",
  "  agree with an internal range of 101 points' whose numeric value was not shown to the\n",
  "  participant, so the table ships one row per observed value with only 0 and 100 labelled")
NOT_ESTABLISHED <- paste0(
"  Nothing about the wording, which the deposit prints. Note the items are the\n",
"  PROSPECTIVE rephrasings ('the next test block'); the item-overview PDF marks\n",
"  the other two TTMI items '[removed]' for this version because, in the paper's\n",
"  words, rephrasing them forward 'would be semantically unsuitable'.\n")
source("itemtables/batch_300/verify_much_tte_common.R")
