##Natural-hazard adaptation cost-sharing conjoint (Switzerland) from
##Schick, V., Metz, F., Joon, K., Hanger-Kopp, S., & Lieberherr, E. (2026). Distributive
##preferences in natural hazard adaptation [Data set]. Zenodo. https://doi.org/10.5281/zenodo.21458444
##(no article DOI in the record; pre-registration https://osf.io/rgq9y).
##Licence: CC BY-NC 4.0 (Zenodo record licence field; README.pdf "Copyright" states the same).
##Files read: df_clean.csv and README.pdf (codebook: question wording, response options, recodes).
##The authors' analysis code (github.com/NikaSchi/survey_climate_adaptation_justice,
##01_scripts/04_conjoint_general.R) was read as text, not run.
##Usage: Rscript schick_2026.R <dir holding df_clean.csv> <output dir>
##
##Swiss residents, online panel (Bilendi), 2-14 May 2025, quotas on age and gender; the survey was
##offered in German, French, Italian and English (column `language`). 6 tasks x 2 policy options,
##3 attributes; the README names them by their question: costs ("Who should bear the costs?", 5
##levels), exemptions ("Should there be people exempted from the costs?", 3 levels), municipality
##("Which municipalities should be particularly protected?", 5 levels).
##Attribute text is stored AS DISPLAYED in the respondent's survey language (README: "Displayed
##attribute level"), so each level appears in up to four languages; cov_language says which. The
##authors' own DE/FR/IT -> EN mapping is 04_conjoint_general.R section 1.2 (not applied here).
##One table: one experiment, one fielding, pooled across languages by the authors.
##Outcomes (README):
##  choice = x_conjoint_prefer, "Which option do you prefer?" Option 1 / Option 2, forced (no opt-out).
##  rating_acceptance = x_conjoint_acceptance_y, "Irrespective of your choice, how acceptable do you
##    find the two options?" 1 "Totally unacceptable" ... 6 "Totally acceptable" (README: verbal
##    endpoints recoded to 1 and 6 by the authors, "I don't know"/"Prefer not to say" -> NA; none NA).
##Repeated task: task 6 repeats task 1 with the two options swapped (04_conjoint_general.R L199-207
##"Task 6 mirrors Task 1"; verified below on every respondent), so trial_repeat_of = 1 on task 6.
##Randomization restrictions, level probabilities and attribute order are not documented in the
##deposit. Restriction OBSERVED: when costs = "Companies pay proportionally to their CO2 emissions"
##(any language), exemptions is always "No groups exempted from costs" (2,216 of 2,216 profiles);
##all other cost x exemption pairs occur. Level shares look roughly even (not documented).
##Covariates keep the README's recoded text (already collapsed by the authors): cov_age_group (18 - 34,
##35 - 49, 50+), cov_gender (Female/Male -> female/male; the authors set Non-binary/Other and
##Prefer not to say to NA), cov_education (3 collapsed groups, README), cov_language_region,
##cov_party_bloc (party_choice collapsed into Left/Liberal/Conservative/No party association; a bloc,
##not party identification, so not cov_party_id), cov_income (Low/Mid/High). Other attitude batteries
##are not kept. Dropped: free-text fields experience_nh_10_text and party_choice_13_text.
##respondent_id is a 1..923 serial and is kept as id.
##COUNT: the file has 923 respondents; README section 5 says "The final dataset includes n = 891
##responses" (Zenodo record and triage also saw 923). Not resolved; flagged.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "df_clean.csv"), encoding = "UTF-8")
stopifnot(nrow(s) == 923, uniqueN(s$respondent_id) == 923)
d <- rbindlist(lapply(1:6, function(t) rbindlist(lapply(1:2, function(p) s[, .(
  id = as.integer(respondent_id), task = t, profile = p,
  choice = as.integer(get(paste0(t, "_conjoint_prefer")) == paste("Option", p)),
  rating_acceptance = as.integer(get(paste0(t, "_conjoint_acceptance_", p))),
  attr_costs = get(paste0("choice", t, "_costs", p)), attr_exemptions = get(paste0("choice", t, "_exemptions", p)),
  attr_municipality = get(paste0("choice", t, "_municipality", p)),
  cov_language = language, cov_age_group = age, cov_gender = c(Female = "female", Male = "male")[gender],
  cov_education = education, cov_language_region = language_region, cov_party_bloc = party_choice, cov_income = income)]))))
stopifnot(all(s[, `1_conjoint_prefer`] %in% c("Option 1", "Option 2")))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating_acceptance %in% 1:6))
stopifnot(!anyNA(d[, .(attr_costs, attr_exemptions, attr_municipality)]), all(d$attr_costs != ""))
stopifnot(d[, uniqueN(attr_costs)] == 20, d[, uniqueN(attr_exemptions)] == 12, d[, uniqueN(attr_municipality)] == 20)  # 5/3/5 levels x 4 languages
# task 6 = task 1 with options swapped
t1 <- d[task == 1, .(id, profile = 3L - profile, attr_costs, attr_exemptions, attr_municipality)]
t6 <- d[task == 6, .(id, profile, attr_costs, attr_exemptions, attr_municipality)]
stopifnot(fsetequal(t1, t6))
d[, trial_repeat_of := fifelse(task == 6L, 1L, NA_integer_)]
setcolorder(d, c("id", "task", "profile", "choice", "rating_acceptance"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "schick_2026_hazard_adaptation.csv"))
