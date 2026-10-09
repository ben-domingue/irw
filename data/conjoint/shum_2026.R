##Hong Kong diaspora foreign-policy conjoint (four host countries) from
##Shum, M., Yeung, E., Chan, K. M., Chung, S., Tong, A., & Yip, K. S. (2026). Voice after exit:
##The prioritization of homeland-facing foreign policy among the Hong Kong diaspora. Political
##Behavior (forthcoming; no article DOI found 2026-10-08).
##Replication data: Harvard Dataverse doi:10.7910/DVN/4SEPIM, CC0 1.0, no restricted files.
##Files read: cleaned_data/df_AU.RData, df_CA.RData, df_UK.RData, df_US.RData (inside
##Voice_After_Exit_replication.zip; each holds data frame df_cj). README.txt, analysis_main.R
##and sample_demographics_*.R were read as text. The deposit has no questionnaire or codebook
##and the article could not be found, so the outcome wording is a paraphrase from the authors'
##code (axis label "Probability of Choosing the Party/Candidate").
##Usage: Rscript shum_2026.R <dir holding the four .RData files> <output dir>
##
##Hong Kong emigrants surveyed online (Qualtrics, July-November 2024) in Australia (472),
##Canada (489), the UK (703) and the US (459). Each chose between 2 parties/candidates in 5
##tasks (source task 1-5, profile 1-2), described by 6 policy proposals: policy toward Hong Kong
##(Status quo / Facilitate asylum provision / Facilitate asylum provision and naturalization),
##cross-Strait policy, policy toward China (identical text in all four countries), and three
##domestic proposals (economic, immigration, healthcare) whose text is country-specific (e.g.
##healthcare: AU "Expand universal healthcare", UK "Recruit more doctors and nurses to the NHS",
##US "Protect and expand the Affordable Care Act"). The authors pool the four samples after
##recoding the domestic levels to "Conservative/Liberal ... proposal"; because the displayed
##domestic text differs by country, the IRW keeps FOUR TABLES, one per country
##(shum_2026_hk_diaspora_policy_au/_ca/_uk/_us), with the text as stored. Attribute names
##follow the authors' labels: attr_hk_policy, attr_cross_strait_policy, attr_china_policy,
##attr_economic_policy (domestic_1), attr_immigration_policy (domestic_2),
##attr_healthcare_policy (domestic_3).
##Respondents took the survey in English or Traditional Chinese (cov_survey_language, the
##source UserLanguage EN / ZH-T); the level text is stored in English only.
##choice = selected: exactly one profile per task (checked), so forced choice, no opt-out.
##Randomization restrictions, level probabilities and attribute order are not documented.
##Covariates (source codings; wording not deposited unless stated): cov_age (years),
##cov_gender (Male/Female/Other -> male/female/other), cov_education_level (Below / Bachelor's
##Degree / Above, as stored), cov_party_id (pid, host-country party text; plotted by the
##authors as "Partisanship"), cov_ideology (Q95.1_1, 0 = most left .. 10 = most right, the
##authors' axis label), cov_years_in_host (Q80.3, "Years Lived in <country>"; all missing in
##the UK file), cov_citizen and cov_voted (Yes/No; voted = "Voted in the Latest National
##Election" per the authors' plot label), cov_talk_politics (0-7), cov_soc_tie_1 (0-4),
##cov_soc_tie_2 (0-5), cov_civic_engage_1..9 (0/1, the nine items the authors sum to a civic
##engagement score), cov_duration_sec (EndDate - StartDate, whole survey).
##Dropped: Qualtrics ResponseId (re-keyed to integers within each table), Start/End/Recorded
##dates, the authors' derived variables (age_bin, years_bin_*, female_bin, edu_bin,
##left_right, talk_bin, civic_engage, soc_tie, soc_tie_bin), the constant country column.
##No survey weight in the deposit. No repeated task.
##N: 472 + 489 + 703 + 459 = 2,123 respondents (the article could not be checked).
##Spot check: the pooled data reproduce the authors' setup (rbind of the four files, 21,230 rows).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
for (cc in c("AU", "CA", "UK", "US")) {
  e <- new.env(); load(file.path(raw, paste0("df_", cc, ".RData")), envir = e); s <- as.data.table(e$df_cj)
  stopifnot(all(s$country == cc), s[, .N, id][, all(N == 10)], s[, .N, .(id, task, profile)][, all(N == 1)])
  ids <- unique(s$id)
  d <- data.table(id = match(s$id, ids), task = as.integer(s$task), profile = as.integer(s$profile), choice = as.integer(s$selected))
  am <- c(hk_policy = "hk_policy", cross_strait_policy = "tw_policy", china_policy = "china_policy",
          economic_policy = "domestic_1", immigration_policy = "domestic_2", healthcare_policy = "domestic_3")
  for (v in names(am)) d[, paste0("attr_", v) := as.character(s[[am[[v]]]])]
  stopifnot(!anyNA(d), all(s$gender %in% c("Male", "Female", "Other")), all(s$UserLanguage %in% c("EN", "ZH-T")))
  d[, `:=`(cov_survey_language = s$UserLanguage, cov_age = as.integer(s$age), cov_gender = tolower(s$gender),
           cov_education_level = as.character(s$education), cov_party_id = as.character(s$pid),
           cov_ideology = as.integer(s$Q95.1_1), cov_years_in_host = as.numeric(s$Q80.3),
           cov_citizen = as.character(s$citizen), cov_voted = as.character(s$voted),
           cov_talk_politics = as.integer(s$talk_politics), cov_soc_tie_1 = as.integer(s$soc_tie_1),
           cov_soc_tie_2 = as.integer(s$soc_tie_2))]
  for (k in 1:9) d[, paste0("cov_civic_engage_", k) := as.integer(s[[paste0("ce_", k)]])]
  stopifnot(d[, all(cov_civic_engage_1 + cov_civic_engage_2 + cov_civic_engage_3 + cov_civic_engage_4 + cov_civic_engage_5 +
                    cov_civic_engage_6 + cov_civic_engage_7 + cov_civic_engage_8 + cov_civic_engage_9 == s$civic_engage)])
  d[, cov_duration_sec := as.integer(round(as.numeric(difftime(s$EndDate, s$StartDate, units = "secs"))))]
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("shum_2026_hk_diaspora_policy_", tolower(cc), ".csv")))
}
