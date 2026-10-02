library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

# Item order was randomised per person. Q<n>I is the position (1-42) at which
# that person saw DASS item Q<n> (codebook: "that question's position in the
# survey"); every row is a permutation of 1-42. Kept as `position`, as in the
# ENEM tables (irw#2513). TIPI and VCL items (43-68 in the output) have no
# recorded position, so theirs is NA.
positions <- df |>
  mutate(id = row_number()) |>
  select(id, matches('^q[0-9]+i$')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'position') |>
  mutate(item = str_replace(item, 'i$', 'a'))

df <- df |>
  select(-education,
         -urban,
         -gender,
         -engnat,
         -age,
         -screensize,
         -uniquenetworklocation,
         -hand,
         -religion,
         -orientation,
         -race,
         -voted,
         -married,
         -familysize,
         -major,
         -country,
         -source,
         -introelapse,
         -testelapse,
         -surveyelapse,
         -ends_with('i')) |>
  # add ID variable
  mutate(id = row_number(),
         # replace invalid values with NA
         across(starts_with('tipi') | ends_with('a'), ~if_else(. == 0, NA, .)))

times <- df |>
  select(id,
         ends_with('e')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'rt') |>
  # convert response time from milliseconds to seconds
  mutate(rt = rt / 1000,
         item = str_replace(item, 'e', 'a'))

df <- df |>
  select(-ends_with('e')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  left_join(times, 
            by = c('id', 'item')) |>
  left_join(positions,
            by = c('id', 'item'))


# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  # drop character item variable
  select(id, item_id, resp, rt, position) |>
  # use item_id column as the item column
  rename(item = item_id)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="depression_anxiety_stress.Rdata")


##removing negative rt values
df$rt<-ifelse(df$rt<0,NA,df$rt)
