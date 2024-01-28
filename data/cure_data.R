library(tidyverse)
library(readxl)

df <- read_excel('CURE Pretest and Posttest Public File.xlsx')

names(df) <- tolower(names(df))

df <- df |>
  # remove duplicates
  filter(studentidnew != 12902868) |>
  select(-condition,
         -curelength,
         -curetype,
         -schooltype,
         -studentidnew,
         -starts_with('academicstanding'),
         -starts_with('academicgoal'),
         -sex,
         -urm,
         -starts_with('courseelements'),
         -starts_with('overallevaluation'),
         -starts_with('scienceattitudes'),
         -starts_with('coursebenefits'),
         -year) |>
  mutate_all(~ replace(., . == 99 | . == 88, NA)) |>
  mutate(id = row_number()) |>
  pivot_longer(cols = -c(id),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(period = case_when(str_detect(item, 'pre') ~ 'pre',
                            str_detect(item, 'post') ~ 'post'),
         item = str_replace(item, '_pre', ''),
         item = str_replace(item, '_post', '')) 


# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())


df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  # drop character item variable
  select(id, item_id, period, resp) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(id, item, period)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="cure_data.Rdata")
