# Verification for much_tte_2025_effort (#2228, batch_300).
# See verify_much_tte_common.R for the source and the shared routes.
TB <- "much_tte_2025_effort"; NITEM <- 5
SCALE_NOTE <- paste0("the paper states 'a 4-point Likert-type scale ranging from 1 (strongly\n",
  "  disagree) to 4 (strongly agree)', and only those two endpoints are labelled, so 2 and 3\n",
  "  ship with option_text blank rather than invented")
NOT_ESTABLISHED <- paste0(
"  Which test block a given response refers to. The items are retrospective --\n",
"  'the previous test block' -- and were asked after each of several blocks, so\n",
"  the block is a property of the response (the live table carries wave), not of\n",
"  the item. EF04 and EF05 exist here but were removed from the Current\n",
"  Motivation version, which is why that table has three items and this one five.\n")
source("itemtables/batch_300/verify_much_tte_common.R")
