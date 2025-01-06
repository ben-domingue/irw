# Paper:
# Data: https://osf.io/wkzan/
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("IFP maior planilha do mundo IFP.csv")
df <- df |>
  select(sexo, idade, profissão, 	instituição, starts_with("r")) |>
  rename(cov_sex=sexo, cov_age=idade, cov_profession=profissão, cov_institution=instituição)
df$id <- seq_len(nrow(df))
df <- pivot_longer(
  df,
  cols = starts_with("r"),
  names_to = "item",
  values_to = "resp"
)
df <- df %>%
  mutate(resp = ifelse(resp %in% 1:7, resp, NA))

save(df, file="mbft_anunciacao_2024.rdata")
write.csv(df, "mbft_anunciacao_2024.csv", row.names=FALSE)