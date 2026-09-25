# Paper:
# Data: https://osf.io/wkzan/
library(haven)
library(dplyr)
library(tidyr)

# The file opens with a UTF-8 byte-order mark; without fileEncoding the first
# column is read as "ï..sexo" and select(sexo) fails.
df <- read.csv("IFP maior planilha do mundo IFP.csv", fileEncoding = "UTF-8-BOM")
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
# na = "": the default writes the string "NA", which typed resp and cov_age as
# text on Redivis (irw#2029).
write.csv(df, "mbft_anunciacao_2024.csv", row.names=FALSE, na="")