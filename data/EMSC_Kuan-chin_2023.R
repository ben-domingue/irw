# Paper: https://jeehp.org/journal/view.php?doi=10.3352/jeehp.2023.20.22
# Dataset: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/IFMDCC

library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)

df <- read.xlsx("jeehp-20-22-dataset1.xlsx")
df <- df %>%
  rename(id=OttawaU_ID) %>%
  select(id, starts_with("STN10"), -Stn1010)

df <- pivot_longer(df, cols=-id, values_to="resp", names_to = "item")

save(df, file="EMSC_Kuan-chin_2023.Rdata")
write.csv(df, "EMSC_Kuan-chin_2023.csv", row.names=FALSE)
