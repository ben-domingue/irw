library(tidyverse)
library(haven)
library(janitor)

# import raw data files
smile_white_prototypicality_trans <- read_sav("Smile_White_prototypicality_trans.sav")
smile_smile_final_trans <- read_sav("Smile_smile_final_trans.sav")
neutral_asian_prototypicality_trans <- read_sav('Neutral_Asian_prototypicality_trans.sav')
neutral_black_prototypicality_trans <- read_sav('Neutral_Black_prototypicality_trans.sav')
neutral_expression_trans <- read_sav('Neutral_Expression_trans.sav')
neutral_expression_trans <- neutral_expression_trans |> select(-`filter_$`)
neutral_ambiguity_trans <- read_sav('Neutral_ambiguity_trans.sav')
neutral_latinx_prototypicality_trans.sav <- read_sav('Neutral_Latinx_prototypicality_trans.sav')
neutral_masculinity_trans.sav <- read_sav('Neutral_Masculinity_trans.sav')
neutral_midEast_prototypicality_trans.sav <- read_sav('Neutral_MidEast_prototypicality_trans.sav')
neutral_multi_prototypicality_trans.sav <- read_sav('Neutral_Multi_prototypicality_trans.sav')
neutral_white_prototypicality_trans.sav <- read_sav('Neutral_White_prototypicality_trans.sav')
smile_asian_prototypicality_trans.sav <- read_sav('Smile_Asian_prototypicality_trans.sav')
smile_expression_trans.sav <- read_sav('Smile_Expression_trans.sav')
smile_latinx_prototypicality_trans.sav <- read_sav('Smile_Latinx_prototypicality_trans.sav')
smile_masculinity_trans.sav <- read_sav('Smile_Masculinity_trans.sav')
smile_midEast_prototypicality_trans.sav <- read_sav('Smile_MidEast_prototypicality_trans.sav')
smile_multi_prototypicality_trans.sav <- read_sav('Smile_Multi_prototypicality_trans.sav')
smile_ambiguity_trans.sav <- read_sav('Smile_ambiguity_trans.sav')
smile_attractive_trans.sav <- read_sav('Smile_attractive_trans.sav')

# append different files together
all_objects <- ls()
df_names <- all_objects[sapply(all_objects, function(obj) is.data.frame(get(obj)))]
dataframes <- mget(df_names)
df <- do.call(rbind, dataframes)

df <- df |>
  # remove index from df
  rownames_to_column(var = "row_index") |>
  # convert variable names to lowercase
  clean_names(case = 'snake') |>
  # drop unneeded variables
  select(-row_index,
         -id,
         -face) |>
  # rename variables to be consistent with IRW standards
  rename(id = rater,
         resp = rating) |>
  # recode invalid response values to NA
  mutate(resp = if_else(resp == 0, NA, resp)) |>
  # drop observations without response values
  drop_na()

# create item IDs for each survey item
items <- as.data.frame(unique(df$case_lbl))
items <- items |>
  mutate(item = row_number())


df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("case_lbl" = "unique(df$case_lbl)")) |>
  # select only relevant columns
  select(id, item, resp) |>
  # sort df by id and item
  arrange(id, item)
  

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="american_multiracial_face.Rdata")
