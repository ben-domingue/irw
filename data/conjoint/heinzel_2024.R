##World Bank development policy loan (DPL) paired conjoint (World Bank task team leaders) from
##Heinzel, M., Weaver, C., & Jorgensen, S. (2025; online 2024). Bureaucratic representation and gender
##mainstreaming in international organizations: Evidence from the World Bank. American Political
##Science Review, 119(1), 332-348. https://doi.org/10.1017/S0003055424000376
##Replication data: Harvard Dataverse doi:10.7910/DVN/U090WG, CC0 1.0, no restricted files.
##Files read: Heinzel_Weaver_Jorgensen_24_APSR_survey_data.tab (original .dta, saved as survey.dta),
##"Survey questionnaire" (Qualtrics PDF), Readme.txt, Heinzel_Weaver_Jorgensen_24_APSR_Appendix.pdf
##(section 3, Table A2: features and levels); the .do file read as text, not run. The project-level
##file is observational and not used. Preregistration: doi:10.17605/OSF.IO/6J3M8.
##Usage: Rscript heinzel_2024.R <raw dir> <output dir>
##
##178 World Bank staff (mostly task team leaders; elite survey, 2022), 7 tasks of two hypothetical
##DPLs ("Project 1", "Project 2") shown side by side as a table, no forced choice. task =
##choice_number, profile = profile_number (both recorded). Eight binary features, "independently
##randomized" (Appendix p.5); source holds 0/1 dummies, mapped to the Table A2 level text:
##  attr_prior_actions      condi_high  1 "16", 0 "4"   ("Number of prior action conditions")
##  attr_amount             amount_high 1 "Above average", 0 "Below average" ("Project amount")
##  attr_env_social_risk    envisoc_yes 1 "High", 0 "Low" ("Environmental and social risk")
##  attr_gender_targets     gender_yes  1 "Yes", 0 "No"  ("Gender-disaggregated targets")
##  attr_macro_risk         macro       1 "High", 0 "Low" ("Macroeconomic risk")
##  attr_cpia               cpia_high   1 "4", 0 "2"     ("Recipient CPIA score")
##  attr_us_opposed         us_board    1 "Yes", 0 "No"  ("US executive director opposed recipient's last loan")
##  attr_income             mic         1 "MIC", 0 "LIC" ("Recipient income status")
##(variable labels "Conditionality: High", "Amount: High", "...: Yes", "Country: MIC" give the
##direction). Attribute rows in the questionnaire order above (fixed grid; nothing says otherwise).
##Outcomes (questionnaire Block 4), 1 = Very unlikely ... 10 = Very likely:
##  rating_approval = "In your personal opinion, how likely is each project to get board approval?"
##  rating_impact   = "In your personal opinion, how likely is each project to have a positive impact
##                     on development outcomes in the recipient country?"
##Covariates: cov_survey_weight = weights_final (the preregistered post-stratification weight by
##region and sector); cov_women (1 = respondent woman, 0 = not; the questionnaire offered Male /
##Female / Non-binary / Prefer not to say, so 0 is not certainly male; kept under its own name);
##cov_gender_expertise (1 No expertise ... 5 A great deal of expertise, questionnaire);
##cov_region_code and cov_sector_code (codes 1-7 and 1-11; no value labels in the deposit; the
##questionnaire lists regions East Asia and Pacific, Europe and Central Asia, Latin America & the
##Caribbean, Middle East and North Africa, North America, South Asia, Sub-Saharan Africa and sectors
##Agriculture ... Water, Sanitation and Waste in that order, which the codes probably follow);
##cov_influence_eds/ttls/pms/cds/vps/oth (0/1, who contributes most to DPL design, multi-select).
##Dropped: education and nationality (unlabelled discipline / country codes, the latter typed
##country names coded without a key), gender_high (derived), progress (always 100), and the
##alternative weights weights_gender / weights_genderedu / weights_gendernat (robustness only).
##No PII in the file (the questionnaire's e-mail field is not deposited).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "survey.dta"))))
stopifnot(nrow(s) == 2492L, uniqueN(s$respondent_id) == 178L)
yn <- function(x, one, zero) { stopifnot(x %in% 0:1); ifelse(x == 1, one, zero) }
d <- s[, .(id = as.integer(respondent_id), task = as.integer(choice_number), profile = as.integer(profile_number),
           rating_approval = as.integer(approval), rating_impact = as.integer(impact),
           attr_prior_actions = yn(condi_high, "16", "4"),
           attr_amount = yn(amount_high, "Above average", "Below average"),
           attr_env_social_risk = yn(envisoc_yes, "High", "Low"),
           attr_gender_targets = yn(gender_yes, "Yes", "No"),
           attr_macro_risk = yn(macro, "High", "Low"),
           attr_cpia = yn(cpia_high, "4", "2"),
           attr_us_opposed = yn(us_board, "Yes", "No"),
           attr_income = yn(mic, "MIC", "LIC"),
           cov_survey_weight = weights_final, cov_women = as.integer(women),
           cov_gender_expertise = as.integer(gender_expertise),
           cov_region_code = as.integer(region), cov_sector_code = as.integer(sector),
           cov_influence_eds = as.integer(eds), cov_influence_ttls = as.integer(ttls), cov_influence_pms = as.integer(pms),
           cov_influence_cds = as.integer(cds), cov_influence_vps = as.integer(vps), cov_influence_oth = as.integer(oth))]
stopifnot(d[, .N, .(id, task, profile)][, all(N == 1)], d[, .N, .(id, task)][, all(N == 2)],
          d$rating_approval %in% 1:10, d$rating_impact %in% 1:10)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "heinzel_2024_world_bank_dpl.csv"))
