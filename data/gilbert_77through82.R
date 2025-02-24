cabell2025 <- read_csv(glue("{raw}/77 StudentItemLevel deidentified.csv")) |> 
  # limit to relevant vars
  select(id = student_id, cov_grade = grade,
         cov_teacher = teacher_id,
         cluster_id = school_id,
         treat = treatment,
         cov_male = s_male,
         # items
         contains("tnl"),
         contains("ppvt"),
         contains("celf"),
         contains("wj")) |> 
  pivot_longer(contains(c("tnl", "ppvt", "celf", "wj")),
               names_to = "item",
               values_to = "resp") |> 
  # filter out total scores and extraneous stuff
  filter(!str_detect(item, "tot|Admin|rater|pr|lost"),
         !str_detect(item, "tnl_rs|tnl_ss|wj_sst|wj_pvt_rs|wj_scnt")) |> 
  # filter out additional extraneous stuff
  mutate(resp = parse_number(resp)) |> 
  # remove missing responses
  drop_na(resp) |> 
  # all items we want are dichotomous
  filter(resp < 2) |> 
  # extract the test and wave info
  mutate(test = word(item, 1, 1, sep = "_"),
         test2 = word(item, 2, 2, sep = "_"),
         test = if_else(test == "wj", glue("{test}-{test2}"), test),
         test = if_else(str_detect(test, "tnl"), "tnl", test),
         test = if_else(test == "wj-pvt", "wj-pv", test),
         wave = str_sub(item, -1, -1),
         # F is fall/baseline, S is spring endline
         wave = if_else(wave == "F", 0, 1),
         item = str_remove(item, "_F"),
         item = str_remove(item, "_S")) |> 
  # remove a few more items that slipped through
  filter(!item %in% c("celf_ss", "celf_rs"),
         !str_detect(item, "ppvt.*ne")) |> 
  select(-test2) |> 
  # remove 0 var items (by wave)
  group_by(item, wave) |> 
  filter(var(resp) > 0) |> 
  ungroup() |> 
  arrange(id, test, item)

# verify things look ok
table(cabell2025$test)

# separate and save out
cabell2025 |> 
  filter(test == "celf") |> 
  select(-test) |> 
  write_csv(glue("{clean}/gilbert_meta_77.csv"))

cabell2025 |> 
  filter(test == "ppvt") |> 
  select(-test) |> 
  write_csv(glue("{clean}/gilbert_meta_78.csv"))

cabell2025 |> 
  filter(test == "tnl") |> 
  select(-test) |> 
  write_csv(glue("{clean}/gilbert_meta_79.csv"))

cabell2025 |> 
  filter(test == "wj-pv") |> 
  select(-test) |> 
  write_csv(glue("{clean}/gilbert_meta_80.csv"))

cabell2025 |> 
  filter(test == "wj-sc") |> 
  select(-test) |> 
  write_csv(glue("{clean}/gilbert_meta_81.csv"))

cabell2025 |> 
  filter(test == "wj-ss") |> 
  select(-test) |> 
  write_csv(glue("{clean}/gilbert_meta_82.csv"))
