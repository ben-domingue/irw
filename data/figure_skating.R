library(tidyverse)
library(readr)

# import raw data
performances <- read_csv('performances.csv')
judged_aspects <- read_csv('judged-aspects.csv')

# merge raw datasets together
df <- left_join(judged_aspects, performances, by="performance_id")

# identify performances that have duplicated aspects listed (aspects = item)
dups <- df |>
  mutate(count = 1) |>
  group_by(performance_id, aspect_desc) |>
  summarize(count = sum(count)) |>
  ungroup() |>
  filter(count > 1)

dup_list <- unique(dups$performance_id)

# remove performances with duplicates aspects from df
df <- subset(df, !(performance_id %in% dup_list))

# clean df
df <- df |>
  # select relevant columns
  # [participant] id = name
  # performance = performance_id
  # item = aspect_desc
  # resp = scores_of_panel
  select(name,
         nation,
         performance_id,
         aspect_desc,
         scores_of_panel) |>
  arrange(name, performance_id, aspect_desc) |>
  mutate(performance_type = if_else(str_detect(name, ' / '), 'double', 'single'))

# create IDs for each participant
ids <- as.data.frame(unique(df$name))
ids <- ids |>
  mutate(person_id = row_number())

# create IDs for each performance
performances <- as.data.frame(unique(df$performance_id))
performances <- performances |>
  mutate(performance = row_number()) 

# create item IDs for each survey item
items <- as.data.frame(unique(df$aspect_desc))
items <- items |>
  mutate(item_id = row_number())

df <- df |>
  left_join(ids,
            by=c("name" = "unique(df$name)")) |>
  left_join(performances,
            by=c("performance_id" = "unique(df$performance_id)")) |>
  left_join(items,
            by=c("aspect_desc" = "unique(df$aspect_desc)")) |>
  mutate(id = paste(person_id, performance, sep = '_')) |>
  select(id, 
         person_id, 
         nation, 
         performance, 
         performance_type, 
         item_id, 
         scores_of_panel) |>
  rename(performance_id = performance,
         item = item_id,
         resp = scores_of_panel)

summary(df$resp)

# save df to Rdata file
save(df, file="figure_skating.Rdata")