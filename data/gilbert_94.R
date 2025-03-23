# list of items to be reversed
pos_items <- c("budget_clean", "hasaccount_clean", "hasIRA_clean",
               "hasstock_clean", "rfulltime")

evans2025 <- read_dta(glue("{raw}/94 WS_Analysis_Final.dta")) |> 
  select(id = paduaid, treat = treatment_b, cov_hhsize = hhsize_b,
         cov_female = female_b, cov_married = married_b,
         # baseline items
         hasstock_clean_b:rollover_clean_b,
         WIC_clean_b, rfulltime_b, tanfdum_b:unemploydum_b,
         homeless_dum_b, hasdebt_b,
         # endline
         hasstock_clean_f1:rollover_clean_f1,
         WIC_clean_f1, rfulltime_f1, tanfdum_f1:unemploydum_f1,
         homeless_dum_f1, hasdebt_f1,
         # followup
         hasstock_clean_f2:rollover_clean_f2,
         WIC_clean_f2, rfulltime_f2, tanfdum_f2:unemploydum_f2,
         homeless_dum_f2, hasdebt_f2
         ) |> 
  pivot_longer(hasstock_clean_b:hasdebt_f2, names_to = "item", values_to = "resp") |> 
  drop_na(resp) |> 
  # get the wave, b = 0, f1 = 1, f2 = 2
  mutate(wave = word(item, -1, sep = "_"),
         wave = case_when(
           wave == "b" ~ 0,
           wave == "f1" ~ 1,
           wave == "f2" ~ 2
         ),
         # remove suffix from item
         item = str_remove(item, "_b|_f1|_f2"),
         # reverse code so that higher value means more poverty
         r = if_else(item %in% pos_items, 1, 0),
         resp = if_else(r == 1, 1 - resp, resp)
         )

# export
write_csv(evans2025, glue("{clean}/gilbert_meta_94.csv"))
