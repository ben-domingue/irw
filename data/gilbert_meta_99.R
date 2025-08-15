alfonsi2024 <- read_dta(glue("{raw}/99 Religiosity_Panel.dta")) |> 
  select(id = pupid,
         cluster_id = con_psdpsch98,
         treat = psdp_treat,
         wave = survey_round,
         o1a_importance_KLPS:o2d_donate_money_KLPS,
         # excluding hh_money b/c it looks like they don't include that in the index
         # cov_donate_hours = o2c_donate_hours_KLPS,
         # cov_donate_money = o2d_donate_money_KLPS,
         cov_female = female,
         cov_12_or_younger = younger
         ) |> 
  # dichotomize money and hours so they fit in with the others
  mutate(across(contains("donate"), ~ if_else(. > 0, 1, 0))) |> 
  pivot_longer(o1a_importance_KLPS:o2d_donate_money_KLPS,
               names_to = "item",
               values_to = "resp") |> 
  drop_na(resp) |> 
arrange(id, item, wave)

##gilbert_meta_99
