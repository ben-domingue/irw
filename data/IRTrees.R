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
fsdatT <- fsdatT %>% select(-node, -sub)
fsdatT <- fsdatT %>% rename(resp=value, id=person)
fsdatT$id <- sub("^p", "", fsdatT$id) # Convert ids into integers
fsdatT$id <- as.integer(fsdatT$id)

load("./VerbAgg2.rda")
VerbAgg2_id <- 1:nrow(VerbAgg2)
VerbAgg2 <- cbind(VerbAgg2, id=I(VerbAgg2_id)) # Merge id column into the matrix
VerbAgg2 <- VerbAgg2[, !colnames(VerbAgg2) %in% c("Anger", "Gender")]
VerbAgg2 <- as.data.frame(VerbAgg2)
VerbAgg2_long <-  pivot_longer(VerbAgg2, cols=-id, names_to='item', values_to='resp')  # Reshape VerbAgg2 data to long format

load("./VerbAgg3.rda")
VerbAgg3_id <- 1:nrow(VerbAgg3)
VerbAgg3 <- cbind(VerbAgg3, id=I(VerbAgg3_id))
VerbAgg3 <- VerbAgg3[, !colnames(VerbAgg3) %in% c("Anger", "Gender")]
VerbAgg3 <- as.data.frame(VerbAgg3)
VerbAgg3_long <-  pivot_longer(VerbAgg3, cols=-id, names_to='item', values_to='resp')

save(fsdatT, file="fsdatT.Rdata")
save(stressT, file="stressT.Rdata")
save(VerbAgg2_long, file="VerbAgg2.Rdata")
save(VerbAgg3_long, file="VerbAgg3.Rdata")
write.csv(fsdatT, "fsdatT.csv", row.names=FALSE)
write.csv(stressT, "stressT.csv", row.names=FALSE)
write.csv(VerbAgg2_long, "VerbAgg2.csv", row.names = FALSE)
write.csv(VerbAgg3_long, "VerbAgg3.csv", row.names = FALSE)