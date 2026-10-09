##Meat-and-fish food-policy-package conjoint (China, Germany, USA) from
##Fesenfeld, L. P., Wicki, M., Sun, Y., & Bernauer, T. (2020). Policy packaging can make food
##system transformation feasible. Nature Food, 1(3), 173-182.
##https://doi.org/10.1038/s43016-020-0047-4
##Replication data: Harvard Dataverse doi:10.7910/DVN/FR73RE, CC0 1.0, no restricted files.
##File read: fesenfeld_etal_df_conj_food.csv. The authors' fesenfeld_etal_food_conjoint_analysis_final.R
##was read as text, not run. Design facts, wording and level text from the deposited
##Supplementary_Information_Fesenfeld_etal.pdf (survey instrument, Q10 "Conjoint Experiment",
##SI pp. 64-66).
##Usage: Rscript fesenfeld_2020.R <raw dir> <output dir>
##
##Same online survey as wicki_2019_passenger_transport (separate experiment): fielded
##15 Feb - 8 Mar 2018 (start_time); 4,874 respondents (DE 1,624, US 1,624, CN 1,626), each
##4 tasks (round) x 2 policy packages (policy A/B = profile 1/2), 7 attributes, all shown.
##SI Table 2a (Germany) reports 12,992 observations and 1,624 respondents, as here.
##THREE TABLES, one per country (fesenfeld_2020_food_policy_cn/_de/_us): every model in the
##authors' analysis script and SI is estimated separately by country (subset(df_conj, country
##== ...)); nothing is pooled. Respondents saw English (US), German or Chinese; only the English
##instrument is published ("German and Chinese translation ... available from the authors upon
##request"), so the stored level text is the English version for all three.
##Outcomes (instrument Q2011-Q2013, asked on the same page after each pair):
##  choice = choice: "Which policy package do you prefer?" Policy Package A / B. Forced: "Even
##           if you don't really support either of the two packages, please choose the one you
##           oppose less." Exactly one chosen per task (checked).
##  rating = rate: "How much do you personally support policy package A/B?" 1 Strongly oppose ..
##           7 Strongly support (stored raw; equals rate_A/rate_B, checked).
##Attribute text = the authors' attrib*_lab labels without their "1) " numbering prefix (and a
##stray tab), which match the instrument's level text. Attribute names follow the instrument:
##meat_tax ("New tax on meat and fish products"), revenue_use ("Use of tax revenues"),
##cafeteria_rules ("Rules for public cafeterias"), vegetarian_discounts ("Discounts for
##vegetarian alternatives"), farming_standards ("Animal farming standards"), campaigns
##("Information campaigns"), producer_subsidies ("Reducing subsidies for meat and fish
##producers").
##Restriction (instrument, checked): "No tax revenues" is shown exactly when the tax is "No new
##tax". Attribute order random but fixed per respondent, with the tax always before the
##revenue use (instrument); not recorded. Levels otherwise drawn at random per task.
##trial_info_treatment: the respondent's earlier randomized information/framing arm (Global
##Climate, Local Environment, Personal Health, Animal Welfare, Control; instrument Q5/Q6), one
##per respondent (identical copy Food_ dropped).
##Covariates: cov_gender, cov_age (years), cov_age_group, cov_edu_group (educ: the authors'
##harmonized Low/Medium/High groups, not answer text), cov_income_group (income quintile group),
##cov_food_habits (Q4.1, the authors' short labels), cov_week_meals (Q4.2.1 main meals per week)
##and cov_week_meat_meals (Q4.2.2 main meals with meat/fish per week), both NA for
##vegetarians/vegans who were not asked (stored as 0 in the source); cov_government_role (Q3.1,
##1 "Government is doing too much" .. 7 "Government should do more") and cov_left_right (Q3.2,
##1 Left .. 10 Right), not asked in China; cov_party_id (Q3.3, US only: Democrat / Republican /
##Independent / Something else / Not close to any party); cov_duration_min (survey duration in
##minutes: equals end_time - start_time). Dropped: start/end time, frame (constant), idround,
##the coded Attrib* and rate_A/rate_B duplicates, meatcons and meat_fish (derived).
##No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "fesenfeld_etal_df_conj_food.csv"), encoding = "UTF-8")
stopifnot(nrow(s) == 38992, uniqueN(s$id) == 4874, s[, .N, .(id, round, policy)][, all(N == 1)], all(s$treatment_food == s$Food_))
cl <- function(x) trimws(sub("^[0-9]+\\)\\s*", "", as.character(x)))
nm <- c(meat_tax = 1, revenue_use = 2, cafeteria_rules = 3, vegetarian_discounts = 4, farming_standards = 5,
        campaigns = 6, producer_subsidies = 7)
d <- s[, .(id = as.integer(id), task = as.integer(round), profile = match(policy, c("A", "B")),
           choice = as.integer(choice), rating = as.integer(rate))]
for (k in names(nm)) d[, paste0("attr_", k) := cl(s[[sprintf("attrib%d_lab", nm[[k]])]])]
stopifnot(all(d$rating == as.integer(sub("_", "", fifelse(s$policy == "A", s$rate_A, s$rate_B)))),
          identical(d$attr_meat_tax == "No new tax", d$attr_revenue_use == "No tax revenues"),
          all(d$attr_farming_standards %in% c("Organic practices (no antibiotics/chemicals) & no cages",
                                              "Stringent limits on antibiotics/chemicals & large cages", "Standards kept at current level")))
veg <- s$meat_fish == "Vegetarian/Vegan"
stopifnot(all(s$weekmeals[veg] == 0), all(s$weekmeals[!veg] > 0))
d[, `:=`(trial_info_treatment = s$treatment_food, cov_country = s$country,
         cov_gender = s$gender, cov_age = as.integer(s$age), cov_age_group = s$age_grp, cov_edu_group = s$educ,
         cov_income_group = s$incgrp, cov_food_habits = s$food_habits,
         cov_week_meals = fifelse(veg, NA_integer_, as.integer(s$weekmeals)),
         cov_week_meat_meals = fifelse(veg, NA_integer_, as.integer(s$weekmeat)),
         cov_government_role = as.integer(s$government_int), cov_left_right = as.integer(s$left_right),
         cov_party_id = fifelse(s$partyID == "", NA_character_, s$partyID), cov_duration_min = as.integer(s$duration))]
stopifnot(!anyNA(d[, .(choice, rating)]), all(d$rating %in% 1:7), all(d$cov_gender %in% c("male", "female")),
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(cov_country), id][, all(V1 == 1)])
for (cc in c("CN", "DE", "US")) {
  x <- d[cov_country == cc][, cov_country := NULL]
  if (cc != "US") x[, cov_party_id := NULL]
  if (cc == "CN") x[, c("cov_government_role", "cov_left_right") := NULL]
  setorder(x, id, task, profile)
  fwrite(x, file.path(out, paste0("fesenfeld_2020_food_policy_", tolower(cc), ".csv")))
}
