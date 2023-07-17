library(tidyverse)
library(readr)
library(janitor)

arhq <- read_csv('Study2_ARHQ_187_raw.csv')
art <- read_csv('Study2_ART_3Versions_raw.csv')
gmg_comp_s <- read_csv('Study2_GatesMacGinitieComp_FormS_raw.csv')
gmg_comp_t <- read_csv('Study2_GatesMacGinitieComp_FormT_raw.csv')
gmg_vocab_t <- read_csv('Study2_GatesMacGinitieVocab_FormT_raw.csv')
nd_comp <- read_csv('Study2_NeslonDenny_Comp_FormG_raw.csv')
nd_vocab <- read_csv('Study2_NeslonDenny_Vocab_FormG_raw.csv')


# batch process datasets in enviroment
all_objects <- ls()
dataframe_names <- all_objects[sapply(all_objects, function(x) is.data.frame(get(x)))]

# iterate over each dataframe
for (name in dataframe_names) {
  # get the dataframe object
  dataset <- get(name)
  
  # convert the variable names to snake case and remove special characters
  new_names <- tolower(names(dataset))
  new_names <- str_replace_all(new_names, ' ', '_')
  new_names <- str_remove_all(new_names, '[^A-Za-z0-9_]')
  new_names <- str_replace(new_names, 'subj_id', 'id')
  
  # reassign new names to dataframe
  names(dataset) <- new_names
  
  # assign the modified dataframe back to the environment
  assign(name, dataset)
}

# individually process the adult reading history questionnaire
arhq <- arhq |>
  # rescale item values so that all are > 0
  mutate(across(starts_with('rh_'), ~. + 1)) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp')

# individually process the author recognition questionnaire
art <- art |>
  select(-session,
         -finished) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp')

# individually process Gates-MacGinitie Comprehension test for adults, form S
gmg_comp_s <- gmg_comp_s |>
  select(id,
         matches('^c[0-9]')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp')

# individually process Gates-MacGinitie Comprehension test for adults, form T
gmg_comp_t <- gmg_comp_t |>
  select(id,
         matches('^q[0-9]')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  # change item names that conflict with other DFs' names
  mutate(item = str_replace_all(item, 'q', 'gmgcompt'))

# individually process Gates-MacGinitie Vocabulary test for adults, form T
gmg_vocab_t <- gmg_vocab_t |>
  select(-finished,
         -session,
         -v1,
         -v2) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  mutate(item = paste('gmgvocab', item))

# individually process Nelson-Denny Vocabulary test
nd_vocab <- nd_vocab |>
  select(-session,
         -p1,
         -p2,
         -p3,
         -finished) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  # change item names that conflict with other DFs' names
  mutate(item = str_replace_all(item, 'q', 'ndvocab'))

# individually process Nelson-Denny Comprehension test
nd_comp <- nd_comp |>
  select(id,
         matches('^q[0-9]')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  # change item names that conflict with other DFs' names
  mutate(item = str_replace_all(item, 'q', 'ndcomp'))

# make one big dataframe made up of all individual questionnaires
df <- rbind(arhq, art, gmg_comp_s, gmg_comp_t, gmg_vocab_t, nd_comp, nd_vocab)

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
  rename(item = item_id) |>
  # update IDs so that first unique value starts with 1
  mutate(id = id + 1) |>
  # sort df by id and item
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="approaches_to_text_study2.Rdata")
