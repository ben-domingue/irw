# Paper: https://pubmed.ncbi.nlm.nih.gov/35723836/
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/UA5GTO
library(haven)
library(dplyr)
library(tidyr)
library(readxl)

df <- read_xlsx("Faces Spanish Adolescents.xlsx")
df <- as.data.frame(t(df))
colnames(df) <- df[1, ]
df <- df[-1, ]
df$id <- seq_len(nrow(df))

# ------ Process FACES Dataset ------
faces_df <- df |>
  select(id, starts_with("FACE"))
faces_df <- pivot_longer(faces_df, cols=-id, names_to="item", values_to="resp")
faces_df$resp <- as.numeric(faces_df$resp)
faces_df$resp <- ifelse(faces_df$resp %% 1 != 0, NA, faces_df$resp)
faces_df$resp[43139] <- NA # Remove the unexpected values of 0 and 6
faces_df$resp[43978] <- NA

save(faces_df, file="FACES_Spanish_Vegas_2022_FACES.Rdata")
write.csv(faces_df, "FACES_Spanish_Vegas_2022_FACES.csv", row.names=FALSE)

# ------ Process FSS Dataset ------
fss_df <- df |>
  select(id, starts_with("FSS"), -FSS)
fss_df <- pivot_longer(fss_df, cols=-id, names_to="item", values_to="resp")
fss_df$resp <- as.numeric(fss_df$resp)
fss_df$resp <- ifelse(fss_df$resp %% 1 != 0, NA, fss_df$resp)

save(fss_df, file="FACES_Spanish_Vegas_2022_FSS.Rdata")
write.csv(fss_df, "FACES_Spanish_Vegas_2022_FSS.csv", row.names=FALSE)
