gilbert2024_a <- glue("{raw}/03 simulated_ssri_binary.csv") |> 
  # read csv2 because of the format
  read_csv2() |> 
  # rename variables
  rename(id = PID, 
         treat = SSRI, 
         item = itemID, 
         std_baseline = HAMD_BASE,
         resp = itemScore)

write_csv(gilbert2024_a, glue("{clean}/gilbert_meta_3.csv"))
