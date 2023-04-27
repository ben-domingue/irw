library(tidyverse)
library(haven)
library(labelled)

df <- read_sav('DeceptionBan_ProfSurvey_OSF.sav')

names(df) <- tolower(names(df))

df <- df |>
  # rename subject ID variable to id
  rename(id = subid) |>
  # drop unneeded variables
  select(-psych_reviewer,
         -numb_psychrevier,
         -numb_psycheditor,
         -eco_reviewer,
         -numb_ecoreview,
         -numb_ecoedit,
         -gensci_reviewer,
         -numb_genscireview,
         -numb_gensciedit,
         -you_use_decept,
         -you_rejected_bc_decept,
         -sex,
         -age,
         -hispanic,
         -race,
         -position,
         -instituteion_type,
         -region,
         -department,
         -you_behave_eco) |>
  mutate(
    # recode item to be 0/1 binary (0 == no, 1 == yes)
    decept_rigorous = if_else(decept_rigorous == 2, 0, decept_rigorous),
    # create new variable to store various answers to one open response item
    reason_less_rigorous = case_when(necessary_or_more_rigorous == 1 ~ 1,
                                     immoral == 1 ~ 2,
                                     misinterprets_deception == 1 ~ 3,
                                     depends_on_method == 1 ~ 4,
                                     hurts_future_studies == 1 ~ 5,
                                     subjects_notdeceived == 1 ~ 6,
                                     its_lazy_unnecessary == 1 ~ 7,
                                     other == 1 ~ 8),
    # recode item to be 0/1 binary (0 == no, 1 == yes)
    you_worry_rigor = if_else(you_worry_rigor == 2, 0, you_worry_rigor),
    # create new variable to store various answers to one open response item
    reason_no_deception = case_when(not_relevant == 1 ~ 1,
                                    not_necessary == 1 ~ 2,
                                    iam_economist == 1 ~ 3,
                                    lose_trust_pool == 1 ~ 4,
                                    need_trust_study == 1 ~ 5,
                                    difficult_publish == 1 ~ 6,
                                    unethical == 1 ~ 7,
                                    other2 == 1 ~ 8)) |>
  # drop variables that stored different response options to two different open response items
  select(-necessary_or_more_rigorous,
         -immoral,
         -misinterprets_deception,
         -depends_on_method,
         -hurts_future_studies,
         -subjects_notdeceived,
         -its_lazy_unnecessary,
         -blank,
         -other,
         -not_relevant,
         -not_necessary,
         -iam_economist,
         -lose_trust_pool,
         -need_trust_study,
         -difficult_publish,
         -unethical,
         -blank2,
         -other2) |>
  pivot_longer(!id,
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

# remove obsolete label for resp column
df$resp <- remove_labels(df$resp)

# get values for response variable
table(df$resp)

# detibble df
df <- as.data.frame(df)

# save df to Rdata file
save(df, file="deception_professors.Rdata")
