# Verification for simsalRbim_Human_LargeValence_2018 (#1945, batch_205).
# See verify_simsalRbim_common.R for the source and what the routes establish.
TB     <- "simsalRbim_Human_LargeValence_2018"
SRC    <- ".cache/batch_205/simsal_Human_LargeValence_2018.txt"
EXPECT <- c("Cat", "Crow", "Doctor", "Fire", "Frustrated", "Lake", "War")
NOTE   <- paste0("The paper names the high-valence picture set outright: lake, cat, crow, doctor,\n",
                 "  fire, human posture-frustrated, war -- seven OASIS images (Kurdi et al. 2017), which\n",
                 "  is exactly the seven codes. 'LargeValence' in the table name is the paper's\n",
                 "  high-valence range, not a different set.")
source("itemtables/batch_205/verify_simsalRbim_common.R")
