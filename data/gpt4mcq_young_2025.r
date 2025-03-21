# Paper: https://journals.sagepub.com/doi/abs/10.1177/00986283241311220?casa_token=MPHTAzkBPIAAAAAA%3AM8BRVR03F1O_Uz1hxnlUMhq1G-UtQftz6XWZNMoDcLN_qQUTUSxcmfGqdk4Vgd6ypR__0HifaCsp
# Data: https://osf.io/zq4eg/files/osfstorage?view_only=d78eeb2235e940ca9ae4bb6732fad999
library(haven)
library(dplyr)
library(tidyr)

df <- read_sav("ChatGPT IRT DATA_CLEAN.sav")

df <- df |>
  select(starts_with("AIQ"), ResponseId) |>
  rename(id=ResponseId)

df <- pivot_longer(df, cols=-id, names_to="item", values_to="resp")

save(df, file="gpt4mcq_young_2025.Rdata")
write.csv(df, "gpt4mcq_young_2025.csv", row.names=FALSE)