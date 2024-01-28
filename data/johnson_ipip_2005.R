library(tidyverse)
library(haven)

df <- read_sav('ipip20993.sav')

df <- df |>
  # select only relevant variables
  select(age,
         matches('i\\d')) |>
  # add participant ID
  mutate(id = row_number(),
         # replace invalid values (0 is coded for missing data) with NA
         across(starts_with('i'), ~if_else(. == 0, NA, .))) |>
  # reshape data to be long by participant and item
  pivot_longer(cols = -c(id, age),
               names_to = 'item',
               values_to = 'resp') |>
  # remove character from item values to give them unique numerical IDs
  mutate(item = str_remove(item, 'i')) |>
  # rearrange columns
  select(id, age, item, resp)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="johnson_ipip_2005.Rdata")
