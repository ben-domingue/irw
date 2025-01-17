# Paper: https://www.cambridge.org/core/journals/british-journal-of-political-science/article/measuring-media-freedom-an-item-response-theory-analysis-of-existing-indicators/4A6D5AE5E6F4E78D0642BFF882C1FBF6
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ENOEQS
# Issue: https://github.com/ben-domingue/irw/issues/599

library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("irt_full.csv")
df$id <- seq_len(nrow(df))
df <- df |>
  select(-cow, -year)
df <- pivot_longer(df, cols=-id, names_to="item", values_to="resp")
df <- na.omit(df)

save(df, file="MMF_Solis_2020.Rdata")
write.csv(df, "MMF_Solis_2020.csv", row.names=FALSE)