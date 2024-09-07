# Paper: https://pubmed.ncbi.nlm.nih.gov/36245403/
# Data: https://osf.io/5qxv6/
library(haven)
library(dplyr)
library(tidyr)

df <- read_sav("STARS_Sample1.sav")
colnames(df) <- gsub("\\s*\\(.*\\)", "", colnames(df)) # Remove column labels
df <- lapply(df, function(x) { attr(x, "label") <- NULL; x })
df <- as.data.frame(df)

df <- df |>
  select(ID, starts_with("STAR")) |>
  rename(id=ID)
df[df == -9999] <- NA
df <- pivot_longer(df, cols=-id, names_to="item", values_to = "resp")

save(df, file="STARSinCA_Perlstein_2022.Rdata")
write.csv(df, "STARSinCA_Perlstein_2022.csv", row.names=FALSE)
