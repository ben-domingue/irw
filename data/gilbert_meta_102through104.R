##Paper: https://doi.org/10.1002/rrq.70048


relyea_wide <- read_dta(glue("{raw}/102 more_y4_public.dta")) |> 
  select(id = s_id, cluster_id = teacher_name, block_id = school_name,
         treat = g3_treatment, cov_black = s_black, 
         cov_male = s_male, cov_lep = s_lep,
         cov_homelang_english = s_homelang_english,
         cov_iep = s_iep,
         cov_ses_high = s_ses_high,
         cov_ses_med = s_ses_med,
         cov_ses_low = s_ses_low,
         std_baseline = s_mapritread2021f_std)

relyea_long <- read_dta(glue("{raw}/102 more_y4_public_item.dta")) |> 
  rename(item_cov_transfer = transfer,
         id = s_id) |> 
  left_join(relyea_wide, by = "id")

relyea2025_a <- relyea_long |> 
  filter(test == "vocab") |> 
  select(-test, -item_cov_transfer)

relyea2025_b <- relyea_long |> 
  filter(test == "cc") |> 
  select(-test)

relyea2025_c <- relyea_long |> 
  filter(test == "bg") |> 
  select(-test, -item_cov_transfer)

write_csv(relyea2025_a, glue("{clean}/gilbert_meta_102.csv"))
write_csv(relyea2025_b, glue("{clean}/gilbert_meta_103.csv"))
write_csv(relyea2025_c, glue("{clean}/gilbert_meta_104.csv"))
