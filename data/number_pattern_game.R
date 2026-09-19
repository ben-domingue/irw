library(tidyverse)
library(readr)

# Bigelow & Piantadosi (2016), Harvard Dataverse doi:10.7910/DVN/A8ZWLF,
# numbergame_data.tab (original format). Each row is one yes/no judgement:
# does `target` belong with the numbers in `set`? Each subject saw 15 sets and
# rated 30 targets per set, so the item is the set:target pair, not the set --
# keying on set alone made every id+item pair repeat 30 times (#1856).
# Subject 26 was shown one set twice (60 targets, 5 of them rated in both
# blocks); `trial_number` is what tells those repeats apart.
df <- read_csv('numbergame_data.csv')

df <- df |>
  mutate(id = id + 1, # adjust id variable so that the first unique id is 1
         itemcov_set = gsub(' ', '', set),
         item = paste(itemcov_set, target, sep = ':'),
         rt = rt / 1000) |>
  select(id, item, resp = rating, rt, trial_number = trial, itemcov_set) |>
  arrange(id, trial_number)

stopifnot(!anyDuplicated(df[c('id', 'trial_number')]))

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="number_pattern_game.Rdata")
