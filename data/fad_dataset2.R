library(tidyverse)
library(readr)

df1 <- read_csv('FADGS_dataset2_clean.csv')

df2 <- read_csv('FADGS_dataset3_clean.csv')

df <- rbind(df1, df2)

names(df) <- tolower(names(df))

df <- df |>
  # filter out participants who failed the attention check test
  filter(check == 3 & is.na(recheck)) |>
  # drop unneeded variables
  select(-dataset,
         -session,
         -check,
         -gender,
         -edu,
         -faedu,
         -moedu,
         -faoccu, 
         -mooccu,
         -native,
         -resession,
         -regender,
         -reedu,
         -reage,
         -recheck) |>
  mutate(id = row_number()) |>
  # pivot df longer by item
  pivot_longer(cols = -c(id, age),
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
  select(id, item_id, resp, age) |>
  # use item_id column as the item column
  rename(item = item_id)

# response counts
table(df$resp)

# save df to Rdata file
save(df, file="fad_dataset2.Rdata")

