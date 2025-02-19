thai2022 <- read_xlsx(glue("{raw}/76 Student Assessment Data.xlsx")) |> 
  clean_names() |> 
  # only keep those with both pre and post
  filter(exclude == "Include") |> 
  # limit and rename variables
  select(id = study_student_id, cluster_id = study_teacher_id, block_id = study_school_id,
         cov_grade = grade, treat = condition,
         cov_gender = gender, cov_age_wave1 = w1_age,
         cov_age_wave2 = w2_age,
         w1_3, w1_21:w1_32,
         w2_3, w2_21:w2_32) |> 
  # clean up
  mutate(treat = if_else(treat == "Treatment", 1, 0),
         cov_male = if_else(cov_gender == "male", 1, 0)) |> 
  select(-cov_gender) |> 
  pivot_longer(starts_with("w"), names_to = "item", values_to = "resp") |> 
  mutate(wave = if_else(str_detect(item, "w1"), 0, 1),
         item = str_remove(item, "w1_"),
         item = str_remove(item, "w2_"))

##see https://github.com/ben-domingue/irw/issues/848#event-16357311085
