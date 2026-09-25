# KNOWN DEFECT, ACCEPTED AS-IS (irw#1856, ruled 2026-09-25): stress_deboeck2012
# has an `occasion` column, but 792 excess rows remain after it (4,862 repeated
# (id, item) rows in all): 36 of its 185 people hold two or more complete response
# sets in the source, fsdatT/stressT from the JSS v048c01 supplement. The source
# does not say which set is which. If your analysis needs unique
# (id, item, occasion), drop the repeated sets.

##bd note: verbagg data duplicative, commented out

# https://www.jstatsoft.org/article/view/v048c01
library(dplyr)
library(tidyverse)
library(tidyr)

load("./stressT.rda")
write.csv(stressT, "stressT.csv", row.names=FALSE)
stressT <- stressT |> 
  select(-exo1, -exo2, -exo3, -exo4, -exo5) |> # Remove columns for decision-tree model
  rename(id=person,
         resp=value,
         item=crossitem)

load("./fsdatT.rda")
# `sub` is `item:node` -- the pseudo-item an IRTrees model actually treats as an
# item, and the source hands it over ready-made. Dropping it collapsed each
# person's node1 response and their node2-or-node3 response onto one item, which
# is every one of this table's 5,811 doubled id+item pairs (irw#1842 block F).
# They are not duplicates: node1 is the first branching decision and the second
# row is whichever branch it led to, so the two disagree on 51% of pairs.
fsdatT <- fsdatT %>% select(-node, -item) %>% rename(item = sub)
fsdatT <- fsdatT %>% rename(resp=value, id=person)
fsdatT$id <- sub("^p", "", fsdatT$id) # Convert ids into integers
fsdatT$id <- as.integer(fsdatT$id)

#load("./VerbAgg2.rda")
#VerbAgg2_id <- 1:nrow(VerbAgg2)
#VerbAgg2 <- cbind(VerbAgg2, id=I(VerbAgg2_id)) # Merge id column into the matrix
#VerbAgg2 <- VerbAgg2[, !colnames(VerbAgg2) %in% c("Anger", "Gender")]
#VerbAgg2 <- as.data.frame(VerbAgg2)
#VerbAgg2_long <-  pivot_longer(VerbAgg2, cols=-id, names_to='item', values_to='resp')  # Reshape VerbAgg2 data to long format

#load("./VerbAgg3.rda")
#VerbAgg3_id <- 1:nrow(VerbAgg3)
#VerbAgg3 <- cbind(VerbAgg3, id=I(VerbAgg3_id))
#VerbAgg3 <- VerbAgg3[, !colnames(VerbAgg3) %in% c("Anger", "Gender")]
#VerbAgg3 <- as.data.frame(VerbAgg3)
#VerbAgg3_long <-  pivot_longer(VerbAgg3, cols=-id, names_to='item', values_to='resp')

save(fsdatT, file="fsdatT.Rdata")
save(stressT, file="stressT.Rdata")
#save(VerbAgg2_long, file="VerbAgg2.Rdata")
#save(VerbAgg3_long, file="VerbAgg3.Rdata")
write.csv(fsdatT, "ravens_deboeck2012.csv", row.names=FALSE)
write.csv(stressT, "stress_deboeck2012.csv", row.names=FALSE)
#write.csv(VerbAgg2_long, "VerbAgg2.csv", row.names = FALSE)
#write.csv(VerbAgg3_long, "VerbAgg3.csv", row.names = FALSE)
