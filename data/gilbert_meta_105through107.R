#https://github.com/ben-domingue/irw/issues/1254
#Paper: https://escholarship.org/uc/item/33j1k1k4
#Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/899DIN
#License: PD

cohen2023 <- read_dta(glue("{raw}/105 survey_data.dta")) |> 
  select(id = code, 
         cluster_id = community_id,
         block_id = pair_id,
         treat = treated,
         cov_age = age_base,
         cov_attend_school = attend_school_base,
         cov_ever_attend_school = ever_school_base,
         # baseline items
         social_famhelp_str_base:norm_fatherchoose_base,
         # endline items
         social_famhelp_str:norm_fatherchoose
         ) |> 
  # drop missing treatment var
  drop_na(treat) |> 
  pivot_longer(social_famhelp_str_base:norm_fatherchoose,
               names_to = "item",
               values_to = "resp") |> 
  drop_na(resp) |> 
  mutate(wave = if_else(str_detect(item, "_base"), 0, 1),
         test = word(item, 1, 1, sep = "_"),
         item = word(item, 2, 2, sep = "_"))

# export
export(cohen2023, "social", 105)
export(cohen2023, "self", 106)
export(cohen2023, "norm", 107)
