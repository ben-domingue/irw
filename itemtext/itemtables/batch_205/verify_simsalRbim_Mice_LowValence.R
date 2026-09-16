# Verification for simsalRbim_Mice_LowValence (#1945, batch_205).
# See verify_simsalRbim_common.R for the source and what the routes establish.
TB     <- "simsalRbim_Mice_LowValence"
SRC    <- ".cache/batch_205/simsal_Mice_LowValence.txt"
EXPECT <- c("HCl", "NaCl", "m5MSac", "m10MSac", "water")
NOTE   <- paste0("The paper's low-valence liquid set is 10 mM NaCl, 5 mM sucrose, 10 mM HCl, tap water\n",
                 "  and 10 mM sucrose -- five liquids, which is what the five codes decode to. Note Sac\n",
                 "  is sucrose here, not saccharin: the Methods name sucrose at both concentrations.")
source("itemtables/batch_205/verify_simsalRbim_common.R")
