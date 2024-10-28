# Paper: https://pubmed.ncbi.nlm.nih.gov/37385687/
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/UE55JT
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)

df <- read.xlsx("jeehp-20-20-dataset1.xlsx")
df <- df |>
  rename(id=Person) |>
  select(id, starts_with("itm"))
df[] <- lapply(df, function(x) as.numeric(as.character(x)))
df <- pivot_longer(df, cols=-id, names_to="item", values_to="resp")

save(df, file="CQTMS_Hur_2023.Rdata")
write.csv(df, "CQTMS_Hur_2023.csv", row.names=FALSE)
