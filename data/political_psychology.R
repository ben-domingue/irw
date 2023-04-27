library(tidyverse)
library(readr)

df <- read_csv('yllanon.csv')

names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded columns
  select(-enddate,
         -wave,
         -check,
         -gender,
         -ethnic,
         -edu,
         -inc,
         -state,
         -relig,
         -age,
         -responseid,
         -`duration (in seconds)`) |>
  # recode voting item to have numeric values
  mutate(voting = case_when(voting == 'trump' ~ 1,
                            voting == 'clinton' ~ 2,
                            voting == 'other' ~ 3),
         # add time zone for data (data collected from a university in the Netherlands --> Central European Time (CET))
         startdate = paste0(startdate, " CET"),
         # make date in unix time
         date = as.numeric(as.POSIXct(startdate, format="%Y-%m-%d %H:%M:%OS")),
         # recode values that correspond with "don't know" or "i haven't thought about it much" to NA
         def = if_else((def == 8 | def == 9), NA, def),
         crime = if_else((crime == 8 | crime == 9), NA, crime),
         terror = if_else((terror == 8 | terror == 9), NA, terror),
         poor = if_else((poor == 8 | poor == 9), NA, poor),
         health = if_else((health == 8 | health == 9), NA, health),
         econ = if_else((econ == 8 | econ == 9), NA, econ),
         abort = if_else((abort == 5 | abort == 6), NA, abort),
         unemploy = if_else((unemploy == 8 | unemploy == 9), NA, unemploy),
         blkaid = if_else((blkaid == 8 | blkaid == 9), NA, blkaid),
         adopt = if_else((adopt == 8 | adopt == 9), NA, adopt),
         imm = if_else((imm == 8 | imm == 9), NA, imm),
         vaccines = if_else((vaccines == 8 | vaccines == 9), NA, vaccines),
         guns = if_else((guns == 8 | guns == 9), NA, guns),
         djt = if_else((djt == 5 | djt == 6), NA, djt),
         friends_1 = if_else((friends_1 == 8 | friends_1 == 9), NA, friends_1),
         friends_2 = if_else((friends_2 == 8 | friends_2 == 9), NA, friends_2),
         friends_3 = if_else((friends_3 == 8 | friends_3 == 9), NA, friends_3),
         friends_4 = if_else((friends_4 == 8 | friends_4 == 9), NA, friends_4),
         friends_5 = if_else((friends_5 == 8 | friends_5 == 9), NA, friends_5),
         climate = if_else((climate == 8 | climate == 9), NA, climate),
         ideo = if_else((ideo == 8 | ideo == 9), NA, ideo),
         partyid = if_else((partyid == 8 | partyid == 9), NA, partyid),
         beh_att_1 = if_else(beh_att_1 == 8, NA, beh_att_1),
         beh_att_2 = if_else(beh_att_2 == 8, NA, beh_att_2),
         beh_att_3 = if_else(beh_att_3 == 8, NA, beh_att_3),
         beh_identity = if_else(beh_identity == 9, NA, beh_identity),
         quarantine = if_else((quarantine == 8 | quarantine == 9), NA, quarantine),
         sickleave = if_else((sickleave == 8 | sickleave == 9), NA, sickleave),
         votereport = if_else((votereport == 6 | votereport == 3), NA, votereport),
         votereport = if_else((votereport == 5 | votereport == 4), 3, votereport)) 

|>
  # drop old date variable
  select(-startdate) |>
  group_by(id) |>
  # reshape data long by item
  pivot_longer(cols = !c(id, date),
               names_to = 'item',
               values_to = 'resp') |>
  # sort dataframe by id and then date
  arrange(id, date)
  

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

# response counts
table(df$resp)

# save df to Rdata file
save(df, file="political_psychology.Rdata")


