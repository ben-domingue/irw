# IL-HTE Econ, 21: Davenport (2023) JREE - Math
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# they have the pre and post over multiple years in separate files
# combine into one
read_davenport <- function(year){
  
  pre <- read_xlsx(glue("{raw}/21 Y{year} ICUE Student Pretest.xlsx")) |> 
    select(s_id = id.stu, cluster_id = id.tea, treat = id.condition, contains("pre.scored"))
  
  post_a <- read_xlsx(glue("{raw}/21 Y{year} ICUE Student PostA.xlsx")) |> 
    select(s_id = id.stu, contains("post.scored"))
  
  post_b <- read_xlsx(glue("{raw}/21 Y{year} ICUE Student PostB.xlsx")) |> 
    select(s_id = id.stu, contains("postB.scored")) |> 
    # some of these have 99999 to signify NA
    mutate(across(contains("postB.scored"), ~ as.numeric(.)),
           across(contains("postB.scored"), ~ if_else(. == 999999, NA_real_, .)))
  
  out <- pre |> 
    left_join(post_a, by = "s_id") |> 
    left_join(post_b, by = "s_id")
  
}

# bring in the wide data
davenport2023 <- map(1:3, read_davenport) |> 
  bind_rows() |> 
  # some items only have one response category, must be dropped
  select(where(~ var(., na.rm = TRUE) != 0)) |> 
  # make treat numeric
  mutate(treat = as.numeric(treat)) |> 
  # get rid of the arithmetic questions - data exploration showed
  # extreme ceilings and very few students answering the items
  select(-matches("arithmetic.*post")) |> 
  # pivot to long
  select(s_id, cluster_id, treat, contains("pre"), contains("post")) |> 
  pivot_longer(c(contains("pre"), contains("post")), 
               names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = if_else(str_detect(item, "pre"), 0, 1),
         item = str_remove_all(item, "pre"),
         item = str_remove_all(item, "post"),
         item = str_remove_all(item, "..scored")) |> 
  arrange(s_id, item, time)

# previous code to explore ceillings - seems to be corrected now
# there is an issue with ceiling effects on these items
# get the % correct
dav_p_vals <- davenport2023 |> 
  group_by(item) |> 
  summarise(p_correct = mean(score), n = n())

rm(dav_p_vals)
