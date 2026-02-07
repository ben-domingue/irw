mosher2025 <- read_dta(glue("{raw}/109 structured_supplements_public.dta")) |> 
  select(id = s_id,
         cluster_id = t_id,
         block_id = school_id,
         treat = treatment,
         cov_black = s_black_num,
         cov_other = s_other_race_num,
         cov_ses_high = s_highses_num,
         cov_ses_med = s_medses_num,
         cov_ses_low = s_lowses_num,
         cov_male = s_male_num,
         std_baseline = s_mapread_w_std,
         std_baseline_math = s_mapmath_w_std,
         # items
         s_recall1:s_mid13) |> 
  pivot_longer(s_recall1:s_mid13,
               names_to = "item",
               values_to = "resp") |> 
  drop_na(resp)

# separate by test
mosher2025_a <- mosher2025 |> 
  filter(str_detect(item, "recall"))

mosher2025_b <- mosher2025 |> 
  filter(str_detect(item, "near"))

mosher2025_c <- mosher2025 |> 
  filter(str_detect(item, "mid"))

write_csv(mosher2025_a, glue("{clean}/gilbert_meta_109.csv"))
write_csv(mosher2025_b, glue("{clean}/gilbert_meta_110.csv"))
write_csv(mosher2025_c, glue("{clean}/gilbert_meta_111.csv"))
