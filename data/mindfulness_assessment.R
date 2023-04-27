library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded variables
  select(-observing,
         -describing,
         -accepting,
         -acting,
         -gender) |>
  # replace invalid values with NA
  mutate_all(~ replace(., . == 0, NA)) |>
  # create ID variable
  mutate(id = row_number()) |>
  # pivot dataframe to be long by item
  pivot_longer(cols = -c(id, age),
               names_to = 'item',
               values_to = 'resp') |>
  mutate(item = as.numeric(str_replace(item, 'q', '')))

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="mindfulness_assessment.Rdata")
