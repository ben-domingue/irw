library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  select(-introelapse,
         -testelapse,
         -surveyelapse,
         -education,
         -urban,
         -gender,
         -engnat,
         -hand,
         -religion,
         -orientation,
         -race,
         -voted,
         -married,
         -familysize,
         -uniquenetworklocation,
         -country,
         -source,
         -major,
         -`...94`,
         -age) |>
  mutate(r1 = if_else(r1 == 0, NA, r1),
         r2 = if_else(r2 == 0, NA, r2),
         r3 = if_else(r3 == 0, NA, r3),
         r4 = if_else(r4 == 0, NA, r4),
         r5 = if_else(r5 == 0, NA, r5),
         r6 = if_else(r6 == 0, NA, r6),
         r7 = if_else(r7 == 0, NA, r7),
         r8 = if_else(r8 == 0, NA, r8),
         i1 = if_else(i1 == 0, NA, i1),
         i2 = if_else(i2 == 0, NA, i2),
         i3 = if_else(i3 == 0, NA, i3),
         i4 = if_else(i4 == 0, NA, i4),
         i5 = if_else(i5 == 0, NA, i5),
         i6 = if_else(i6 == 0, NA, i6),
         i7 = if_else(i7 == 0, NA, i7),
         i8 = if_else(i8 == 0, NA, i8),
         a1 = if_else(a1 == 0, NA, a1),
         a2 = if_else(a2 == 0, NA, a2),
         a3 = if_else(a3 == 0, NA, a3),
         a4 = if_else(a4 == 0, NA, a4),
         a5 = if_else(a5 == 0, NA, a5),
         a6 = if_else(a6 == 0, NA, a6),
         a7 = if_else(a7 == 0, NA, a7),
         a8 = if_else(a8 == 0, NA, a8),
         s1 = if_else(s1 == 0, NA, s1),
         s2 = if_else(s2 == 0, NA, s2),
         s3 = if_else(s3 == 0, NA, s3),
         s4 = if_else(s4 == 0, NA, s4),
         s5 = if_else(s5 == 0, NA, s5),
         s6 = if_else(s6 == 0, NA, s6),
         s7 = if_else(s7 == 0, NA, s7),
         s8 = if_else(s8 == 0, NA, s8),
         e1 = if_else(e1 == 0, NA, e1),
         e2 = if_else(e2 == 0, NA, e2),
         e3 = if_else(e3 == 0, NA, e3),
         e4 = if_else(e4 == 0, NA, e4),
         e5 = if_else(e5 == 0, NA, e5),
         e6 = if_else(e6 == 0, NA, e6),
         e7 = if_else(e7 == 0, NA, e7),
         e8 = if_else(e8 == 0, NA, e8),
         c1 = if_else(c1 == 0, NA, c1),
         c2 = if_else(c2 == 0, NA, c2),
         c3 = if_else(c3 == 0, NA, c3),
         c4 = if_else(c4 == 0, NA, c4),
         c5 = if_else(c5 == 0, NA, c5),
         c6 = if_else(c6 == 0, NA, c6),
         c7 = if_else(c7 == 0, NA, c7),
         c8 = if_else(c8 == 0, NA, c8),
         tipi1 = if_else(tipi1 == 0, NA, tipi1),
         tipi2 = if_else(tipi2 == 0, NA, tipi2),
         tipi3 = if_else(tipi3 == 0, NA, tipi3),
         tipi4 = if_else(tipi4 == 0, NA, tipi4),
         tipi5 = if_else(tipi5 == 0, NA, tipi5),
         tipi6 = if_else(tipi6 == 0, NA, tipi6),
         tipi7 = if_else(tipi7 == 0, NA, tipi7),
         tipi8 = if_else(tipi8 == 0, NA, tipi8),
         tipi9 = if_else(tipi9 == 0, NA, tipi9),
         tipi10 = if_else(tipi10 == 0, NA, tipi10),
         id = row_number()) |>
  pivot_longer(cols = -id,
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
  select(id, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="riasec.Rdata")