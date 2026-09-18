# Verification for much_tte_2025_concentrationtask (#2228, batch_300).
# See verify_much_tte_common.R for the source and the shared routes.
#
# A SOURCE DEFECT WAS RESOLVED HERE, and it is worth knowing about. In
# ct_ItemOverview.pdf the three Block 3 grids are ALL labelled "CT07_03" -- the
# labels for the eighth and ninth items were not incremented. The supplementary
# codebook disambiguates them by position: it documents the page-time variables
# as "the first", "the fourth", "the sixth ... concentration task item" in the
# same order, so the three Block 3 grids are CT07, CT08 and CT09 as printed.
TB <- "much_tte_2025_concentrationtask"; NITEM <- 9
SCALE_NOTE <- "resp is 0/1 for whether the count the participant gave matched the true count"
NOT_ESTABLISHED <- paste0(
"  The grids themselves. item_text names the target letter and how many times it\n",
"  occurs, from the deposit's item overview, but the 4 x 15 array of confusable\n",
"  letters is a visual stimulus and is not reproduced. correct_response carries\n",
"  the true occurrence count, which IS the printed answer for each grid.\n")
source("itemtables/batch_300/verify_much_tte_common.R")
