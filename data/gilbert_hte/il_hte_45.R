# IL-HTE Econ, 45: Bateman (2020) Trials - Burnout/Depression
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Because of the small sample, combining the two metrics (they are very similar anyway).

bateman2020 <- read_xlsx(glue("{raw}/45 STOPTHEBURN Data.xlsx")) |> 
  clean_names() |> 
  select(s_id = record_id, event_name,
         cov_age = what_is_your_age,
         cov_female = what_is_your_self_identified_gender,
         cov_race = what_is_your_race,
         cov_role = what_is_your_role_on_the_healthcare_team,
         cov_years_exp = how_many_years_of_experience_do_you_have,
         # surveys
         little_interest_or_pleasure_in_doing_things:i_feel_patients_blame_me_for_some_of_their_problems
         ) |> 
  mutate(treat = word(event_name, 2, 2, sep = ":"),
         treat = if_else(treat == " Control)", 0, 1),
         cov_female = if_else(cov_female == "Female", 1, 0),
         time = word(event_name, 1, 1),
         time = case_when(
           time == "Baseline" ~ 0,
           time == "1" ~ 1,
           time == "3" ~ 2,
           time == "6" ~ 3
         )) |> 
  # make the survey items numeric
  # and reverse code some of the burnout items
  mutate(across(little_interest_or_pleasure_in_doing_things:feeling_afraid_as_if_something_awful_might_happen, ~ parse_number(.)),
         across(little_interest_or_pleasure_in_doing_things:feeling_afraid_as_if_something_awful_might_happen, ~ case_when(
           . == 0 ~ 0,
           . == 2 ~ 1,
           . == 7 ~ 2,
           . == 12 ~ 3
         )),
         across(i_feel_emotionally_drained_from_my_work:i_feel_patients_blame_me_for_some_of_their_problems, ~ case_when(
           . == "Never" ~ 0,
           . == "A few times a year or less" ~ 1,
           . == "Once a month or less" ~ 2,
           . == "A few times a month" ~ 3,
           . == "Once a week" ~ 4,
           . == "A few times a week" ~ 5,
           . == "Every day" ~ 6
         )),
         across(c(i_can_easily_understand_how_my_patients_feel_about_things,
                  i_deal_very_effectively_with_the_problems_of_my_patients,
                  i_feel_im_positively_influencing_other_peoples_lives_through_my_work,
                  i_feel_very_energetic,
                  i_can_easily_create_a_relaxed_atmosphere_with_my_patients,
                  i_feel_exhilarated_after_working_closely_with_my_patients,
                  i_have_accomplished_many_worthwhile_things_in_this_job,
                  in_my_work_i_deal_with_emotional_problems_very_calmly), ~ 6 - .)
         ) |> 
  relocate(treat, time) |> 
  select(-event_name) |> 
  # pivot to long
  pivot_longer(little_interest_or_pleasure_in_doing_things:i_feel_patients_blame_me_for_some_of_their_problems, 
               names_to = "item", values_to = "polyscore") |> 
  drop_na(polyscore) |> 
  arrange(s_id, item, time) |> 
  # get max score for each item
  group_by(item) |> 
  mutate(max_score = max(polyscore)) |> 
  ungroup() |> 
  # dichtomize
  mutate(score = case_when(
    max_score == 3 ~ if_else(polyscore > 1, 1, 0),
    max_score > 3 ~ if_else(polyscore > 3, 1, 0)
  )) |> 
  select(-max_score)
