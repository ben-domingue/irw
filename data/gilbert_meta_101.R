schumaker2023 <- read_delim(glue("{raw}/101 data.csv"), delim = ";") |> 
  clean_names() |> 
  select(id = pat_id_x,
         treat = group_x,
         wave = session_n,
         mood:appetite) |> 
  pivot_longer(mood:appetite,
               names_to = "item",
               values_to = "resp") |> 
  # based on N, group 2 is control
  mutate(treat = if_else(treat == 2, 0, treat)) |> 
  drop_na(resp)

write_csv(schumaker2023, glue("{clean}/gilbert_meta_101.csv"))
