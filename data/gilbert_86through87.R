## Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/NWKSHA
## Paper: https://osf.io/preprints/osf/8x46u_v1
## License: CC BY 4.0


                                        # create an answer key for the knowledge items
# (based on codebook)
know_answers <- tibble(
  item = c("know_speaker",
           "know_term",
           "know_roberts",
           "know_macron",
           "know_vp",
           "know_gov",
           "know_nchouse",
           "know_ncsenate",
           "know_moore",
           "know_chatham",
           "know_alford"),
  correct = c(4,7,7,5,5,4,5,5,5,5,8)
)

# make a function b/c both pre and post CSVs have the same structure
trex_read <- function(name, w){
  
  # load in the pretest
  dat <- read_csv(glue("{raw}/{name}.csv")) |> 
    select(id = code, media_accurate:media_inform,
           trust_gov:trust_respond, efficacy_care:efficacy_voice,
           efficacy_grasp:efficacy_complex,
           norm_vote:norm_election,
           elections_fair,
           know_speaker, know_term,
           know_roberts, know_macron, know_vp, know_gov,
           know_nchouse, know_ncsenate, know_moore,
           know_chatham, know_alford,
           gender, cov_asian = race_1,
           cov_black = race_2, cov_hispanic = race_3,
           cov_middle_eastern = race_4,
           cov_native = race_5, cov_white = race_6,
           cov_multiracial = race_7,
           # use contains b/c some covariates are only present in pre
           cov_educ = contains("education"),
           cov_age = age_screen) |> 
    mutate(cov_male = if_else(gender == 1, 1, 0)) |> 
    select(-c(gender)) |> 
    # reverse code (see codebook)
    mutate(
      # don't reverse code violence, it looks like
      across(c(media_accurate:efficacy_grasp, norm_vote, norm_law:elections_fair), ~ 7 - .)
    ) |> 
    # pivot to long
    pivot_longer(media_accurate:know_alford, names_to = "item", values_to = "resp") |> 
    mutate(test = if_else(word(item, 1, 1, sep = "_") == "know", "knowledge", "trust"))
  
  dat <- dat |> 
    left_join(know_answers, by = "item") |> 
    mutate(resp = case_when(
            resp == correct & test == "knowledge" ~ 1,
            resp != correct & test == "knowledge" ~ 0,
            .default = resp
           )) |> 
    select(-correct) |> 
    mutate(wave = w)
  
}

# get the pre and post data
trexler_pre <- trex_read("86 data_pre", 0)
trexler_post <- trex_read("86 data_post", 1) |> 
  select(-starts_with("cov_"))

# for merging and stacking, separate into demo and item response
trexler_pre_items <- trexler_pre |> 
  select(id, item, resp, test, wave)

trexler_cov <- trexler_pre |> 
  distinct(id, .keep_all = TRUE) |> 
  select(id, starts_with("cov_"))

# bring in the treatment ID
tid <- read_csv(glue("{raw}/86 treatment_codes.csv")) |> 
  rename(id = 1, treat = 2)

# combine
trexler2025 <- trexler_post |> 
  bind_rows(trexler_pre_items) |> 
  arrange(id, test, item, wave) |> 
  left_join(tid, by = "id") |> 
  mutate(treat = replace_na(treat, 0)) |> 
  left_join(trexler_cov, by = "id")

# export by outcome
trexler2025 |> 
  filter(test == "trust") |> 
  select(-test) |> 
  write_csv(glue("{clean}/gilbert_meta_86.csv"))

trexler2025 |> 
  filter(test == "knowledge") |> 
  select(-test) |> 
  write_csv(glue("{clean}/gilbert_meta_87.csv"))
