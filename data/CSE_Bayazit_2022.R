# Paper:
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/M0NJIQ
library(haven)
library(dplyr)
library(tidyr)

# ------ Data Pre-process ------
data <- read.delim("clinical_self_efficacy_dataset.tab", header = TRUE, sep = ";",
                   stringsAsFactors = FALSE, quote = "")
data$ID <- sub('^"', '', data$ID)
data$Item15 <- sub('"$', '', data$Item15)
data[] <- lapply(data, function(x) as.numeric(as.character(x)))
data <- data |>
  rename(id=ID) |>
  select(-Term)
data <- pivot_longer(data, cols=-id, names_to="item", values_to="resp")

save(data, file="CSE_Bayazit_2022.Rdata")
write.csv(data, "CSE_Bayazit_2022.csv", row.names=FALSE)
