library(tidyverse)
library(readr)

df <- read_delim('FBPS-ValidationData.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded columns
  select(-age,
         -engnat,
         -gender,
         -birthpos,
         -birthn,
         -country,
         -source,
         -screensize,
         -introelapse,
         -testelapse,
         -endelapse,
         -dateload) |>
  # convert date variable into unix time
  mutate(submittime = paste0(submittime, ' EST'),
         date = as.numeric(as.POSIXct(submittime, format="%Y-%m-%d %H:%M:%OS")),
         # create participant ID variable
         id = row_number()) |>
  # drop non-unix date variable
  select(-submittime) |>
  # replace invalid responses with NA
  mutate_all(~ replace(., . == 0, NA)) |>
  pivot_longer(cols = -c(id, date),
               names_to = 'item',
               values_to = 'resp')

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  # drop character item variable
  select(id, item_id, resp, date) |>
  # use item_id column as the item column
  rename(item = item_id)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="firstborn_personality.Rdata")
