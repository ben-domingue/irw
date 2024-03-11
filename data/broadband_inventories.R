library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded variables
  select(-ends_with('i')) |>
  # add ID variable
  mutate(id = row_number(),
         # replace invalid values with NA
         across(ends_with('a'), ~if_else(. == 0, NA, .)))

# create separate df for response times to merge onto their respective items later
times <- df |>
  select(id, 
         ends_with('e')) |>
  # pivot long by ID
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'rt') |>
  mutate(item = str_replace(item, 'e', 'a'))

df <- df |>
  # drop the response time variables
  select(-ends_with('e')) |>
  # pivot to be long by item
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  # pivot data to be long by item
  left_join(times, by=c('id', 'item')) |>
  # convert response time from milliseconds to seconds
  mutate(rt = rt / 1000) |>
  mutate(item = str_remove(item, 'q'),
         item = str_remove(item, 'a'))

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="broadband_inventories.Rdata")


df$rt<-ifelse(df$rt<0,NA,df$rt)
