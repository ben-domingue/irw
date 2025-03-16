arteaga2025 <- read_dta(glue("{raw}/88 temp1.dta")) |> 
  select(id = resp_id, block_id = center_code,
         treat = T, wave = baseline,
         cov_mother_age = mother_demo_2,
         cov_mother_educ = mother_demo_3,
         cov_mother_n_children = child_demo_num,
         cov_child_age = focal_child_demo_age,
         cov_child_female = female,
         cov_child_disability = disabilities_focalchild,
         # family care index
         fci_1, fci_1a_1:fci_6,
         # vocabulary (scored)
         vocab_a:vocab_bx, vocab_by:vocab_do,
         # credi (scored)
         CREDI_B1:CREDI_F18,
         # GAD
         gad_1_a:gad_1_g,
         # TOPSE
         topse_1:topse_16,
         # KIDI (scored)
         graded_kidi_1_a:graded_kidi_2_k
         ) |> 
  # flip wave so 0 is baseline
  mutate(wave = 1 - wave) |> 
  # demographics are only at baseline, get them at both time points
  group_by(id) |> 
  mutate(across(c(block_id, cov_mother_age:cov_mother_n_children, 
                  cov_child_female:cov_child_disability), ~ mean(., na.rm = TRUE))) |> 
  ungroup() |> 
  arrange(id, wave) |> 
  pivot_longer(fci_1:graded_kidi_2_k, names_to = "item", values_to = "resp") |> 
  drop_na(resp) |> 
  # remove graded from KIDI labels
  mutate(item = str_remove_all(item, "graded_"),
         test = word(item, 1, 1, sep = "_"))

export(arteaga2025, "fci", 88)
export(arteaga2025, "CREDI", 89)
export(arteaga2025, "kidi", 90)
export(arteaga2025, "topse", 91)
export(arteaga2025, "gad", 92)
export(arteaga2025, "vocab", 93)
