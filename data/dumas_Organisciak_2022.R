## Paper: https://osf.io/qcmex/
## Data: https://osf.io/qcmex/
library(dplyr)
library(tidyr)
library(haven)

df <- read.csv("dumas_organisciak_doherty_2020.csv")
df <- df |>
  select(participant, prompt, response, starts_with("rater")) |>
  rename(id=participant, item=prompt, verbatim=response)
df_long <- df %>%
  gather(key = "rater", value = "resp", rater1:rater4) %>%
  arrange(id, item)

save(df, file="dumas_Organisciak_2022.Rdata")
write.csv(df, "dumas_Organisciak_2022.csv", row.names=FALSE)
