adam2025 <- read_dta(glue("{raw}/97 PsyCapSASTrial.dta")) |> 
  select(id = case_id, 
         treat = arm,
         # covariates
         cov_age = age,
         cov_sex = sex,
         cov_eth = ethnicitysimplified,
         cov_nationality = nationality,
         cov_language = language,
         # psychological capital
         psyo1:psyr3, fu_psyo1:fu_psyr3,
         # gratitude
         gq1:gq6, fu_gq1:fu_gq6,
         # happiness
         happy_scale, fu_happy_scale
         ) |> 
  # simplify treatment by collapsing control
  # (based on stata labels)
  mutate(treat = if_else(treat == 2, 1, 0)) |> 
  # pivot to long
  pivot_longer(psyo1:fu_happy_scale, names_to = "item", values_to = "resp") |> 
  drop_na(resp) |> 
  mutate(
    # extract the wave
    wave = if_else(str_detect(item, "fu_"), 2, 1),
    # make items the same across waves
    item = str_remove(item, "fu_"),
    # get subtest
    test = substr(item, 1, 2)
    ) |> 
  arrange(id, item, wave)

export(adam2025, "ps", 97)
export(adam2025, "gq", 98)
export(adam2025, "ha", 99) ##note: this one is excluded as only a single item
