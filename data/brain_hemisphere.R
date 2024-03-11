library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  select(-country,
         -introelapse,
         -testelapse,
         -wrapupelapse,
         -screenw,
         -screenh) |>
  # replace invalid values with NA
  mutate_all(~ replace(., . == 0, NA)) |>
  # create ID variable
  mutate(id = row_number())

# store item response times in separate df to merge onto their respective items later
times <- df |>
  select(id,
         starts_with('e')) |>
  # pivot longer by id
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'rt') |>
  # remove string from item ID
  mutate(item = as.numeric(str_remove(item, 'e')),
         # convert response times to seconds from milliseconds
         rt = rt / 1000)

df <- df |>
  # drop time variables
  select(-starts_with('e')) |>
  # pivot to be long by item
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  # remove string from item ID
  mutate(item = as.numeric(str_remove(item, 'q'))) |>
  # merge response times to items
  left_join(times,
            by = c('id', 'item'))

# print response values
table(df$resp)

df$resp<-as.numeric(df$resp)

# save df to Rdata file
save(df, file="brain_hemisphere.Rdata")


##removing negative rt values
df$rt<-ifelse(df$rt<0,NA,df$rt)
