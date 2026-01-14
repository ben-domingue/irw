## https://link.springer.com/article/10.3758/s13428-025-02650-1

yu_long <- readRDS("data/raw/yu_data.Rds") |> 
  # rename with IRW conventions
  rename(id = participant,
         item = stim,
         resp = esti,
         item_cov_truth = size,
         cov_gender = gender,
         cov_age = age,
         item_cov_phase = phase) |> 
  select(-c(file_name)) |> 
  # get trial number
  group_by(id, item) |> 
  mutate(item_cov_rep = frank(trial, ties.method = "dense")) |> 
  ungroup() |> 
  mutate(item_unique = glue("{item}-{item_cov_phase}-{item_cov_rep}")) |> 
  drop_na(resp) |> 
  # transform resp to 0/1
  mutate(resp_prop = 100*resp/max(resp),
         resp01 = (resp_prop - .5) / max(resp_prop + 1)) |> 
  arrange(id, item, item_cov_phase, item_cov_rep)
  
# clean up gender
gender <- yu_long |> 
  distinct(cov_gender) |> 
  mutate(cov_female = c(0, 1, 1, rep(0, 6)))

# export IRW
yu_long <- yu_long |> 
  left_join(gender, by = "cov_gender") |> 
  select(-cov_gender)

write_csv(yu_long, "data/clean/yu2025.csv")
