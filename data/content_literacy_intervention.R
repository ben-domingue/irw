library(tidyverse)
library(haven)

df <- read_stata('item_response_public.dta')

df <- df |>
  select(s_id,
         s_q_num,
         s_correct,
         s_itt_consented) |>
  rename(item = s_q_num,
         resp = s_correct,
         treatment = s_itt_consented)

ids <- as.data.frame(unique(df$s_id))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  left_join(ids, by=c('s_id' = "unique(df$s_id)"))  |>
  # drop character item variable
  select(id, treatment, item, resp) |>
  # use item_id column as the item column
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="content_literacy_intervention.Rdata") ##this was updated to 'gilbert_meta_2'
