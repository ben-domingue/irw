##AI decision-support-system discrete choice experiment (Certified Crop Advisors) from
##Zia, A., Gardezi, M., Yu, X., Ryan, B., Merrill, S. C., Clark, E. M., Dadkhah, A., Rizzo, D. M.,
##McMaine, J., & Clay, D. (2026). Harnessing discrete choice experiments to elicit preferred
##configurations of trustworthy AI augmented decision support systems for certified crop
##advisors. Frontiers in Artificial Intelligence, 9, 1747663. https://doi.org/10.3389/frai.2026.1747663
##Replication data: Harvard Dataverse doi:10.7910/DVN/CODYMJ, CC0 1.0, no restricted files.
##Files read: Final_LongForm_AI-DSS_CE_02162026.tab (Dataverse "original format" download, the
##Stata file with value labels; the deposit's "-1" .tab is the same data without labels) and
##CCA2024.pdf (the questionnaire, read with pdftotext and as page images). STATA Code
##02162026.docx was read as text.
##Usage: Rscript zia_2026.R <dir holding Final_LongForm_AI-DSS_CE_02162026.dta> <output dir>
##
##771 Certified Crop Advisors (survey sent by the Crop Science Society of America to ~2,600 CCAs
##in North America, 29 Feb - 20 Mar 2024; article). Each answered up to 5 choice questions
##("Here, you face a choice between three slightly different configurations of these AI-DSS
##with respect to different levels of cost, accuracy, precision, and data ownership attributes.
##Which system would you prefer (Please choose only one option)?"; one question says "decision
##support systems" instead of "AI-DSS") among AI-DSS 1, AI-DSS 2, AI-DSS 3 (profile 1-3) and
##"None of these". The opt-out has no attributes and is not a profile: choice = 0 on all three
##profiles when it was picked (995 of 3,823 tasks), opt_out = yes. The source's long file has a
##row for the opt-out (ChoiceSet = 1, filled with the AI-DSS 1 base values); those rows are
##dropped after their choice is used.
##FIXED DESIGN: there are only 5 choice sets (source EXPERIMENT 1-5, "Experiment No
##(Randomized)") and every respondent saw the same 5 sets; the article says the order of the
##sets was randomized, which the deposit does not record. task = EXPERIMENT, i.e. the identity
##of the choice set, NOT the position in which it was shown. 751 respondents answered all 5,
##20 answered 2-4. The 15 alternatives' levels are fixed and strongly collinear (AI-DSS 1 is
##always the cheapest, least accurate; data ownership is tied to the column: AI-DSS 2 always
##"AI-DSS Company only", AI-DSS 3 always "AI-DSS Company and you").
##Attribute text as displayed in CCA2024.pdf (the PDF shows all 5 sets; each matches one
##EXPERIMENT exactly): cost "Free" / "$N/acre/year"; accuracy "70%".."99%"; precision "Medium
##(10 X 10 meters)", "High (5 X 5 meters)", "High (3 X 3 meters)", "Very High (5 X 5
##centimeters)", "Very High (10 X 10 centimeters)" (source precision in m^2: 100, 25, 9, 0.25,
##and 1.00 for 10 x 10 cm, as coded by the authors); data ownership "Open to all", "AI-DSS
##Company only", "AI-DSS Company and you".
##Covariates (.dta value labels): cov_country (CountryCode), cov_region (Region, state/province
##code; blank -> NA), cov_specialization_<area> (1 = checked, NA otherwise, as stored),
##cov_ai_perception_1..6 (1 Strongly disagree .. 5 Strongly agree, 6 N/A), cov_pa_concern_1..14
##(0 Do not know, 1 Strongly Disagree .. 4 Strongly Agree; item 10 also has 5 = Do not know),
##cov_dss_experience_1..9 (1 Strongly Disagree .. 4 Strongly Agree), cov_farm_size_acres,
##cov_experience_years, cov_education (label text), cov_gender (Male/Female ->
##male/female, Non-binary/third gender -> other, Prefer not to say -> NA), cov_race (label text,
##Prefer not to Answer -> NA), cov_income (label text, Wish not to say -> NA),
##cov_employment (label text), cov_age_group (label text).
##Dropped: ResponseID (survey-platform id; re-keyed to integers in file order), the free-text
##"Specialization in Other", the ChoiceExperiment1-5 / ChoiceExperiment answer copies (checked
##against AIDSS), the authors' dummies (AIDSS0-3, Female, AdvancedDegree, White, Data_*,
##SelfEmployed, Employed*) and the numeric attribute codings. No survey weight.
##N: 771 respondents, 3,823 tasks = the article's 15,292 long-form observations / 4.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "Final_LongForm_AI-DSS_CE_02162026.dta")))
stopifnot(k[, .N, .(ResponseID, EXPERIMENT)][, all(N == 4)], k[, sum(AIDSS), .(ResponseID, EXPERIMENT)][, all(V1 == 1)])
ids <- unique(k$ResponseID)
d <- k[ChoiceSet != 1, .(id = match(ResponseID, ids), task = as.integer(EXPERIMENT), profile = as.integer(ChoiceSet) - 1L,
                         choice = as.integer(AIDSS), cost = as.numeric(cost), accuracy = as.numeric(accuracy),
                         precision = as.numeric(precision), data = as.integer(zap_labels(data)))]
# the five fixed choice sets as printed in CCA2024.pdf (PDF order 1-5 = EXPERIMENT 4, 2, 1, 5, 3)
d[, attr_cost := fifelse(cost == 0, "Free", paste0("$", cost, "/acre/year"))]
d[, attr_accuracy := paste0(accuracy, "%")]
prec <- c("100" = "Medium (10 X 10 meters)", "25" = "High (5 X 5 meters)", "9" = "High (3 X 3 meters)",
          "0.25" = "Very High (5 X 5 centimeters)", "1" = "Very High (10 X 10 centimeters)")
d[, attr_precision := prec[as.character(precision)]]
d[, attr_data_ownership := c("Open to all", "AI-DSS Company only", "AI-DSS Company and you")[data]]
pdf <- data.table(task = rep(c(4L, 2L, 1L, 5L, 3L), each = 3), profile = rep(1:3, 5),
  cost = c("Free", "$30/acre/year", "$80/acre/year", "Free", "$10/acre/year", "$80/acre/year", "$2/acre/year", "$30/acre/year",
           "$60/acre/year", "Free", "$30/acre/year", "$60/acre/year", "$4/acre/year", "$10/acre/year", "$80/acre/year"),
  acc = c("70%", "85%", "95%", "70%", "85%", "99%", "70%", "85%", "90%", "70%", "85%", "90%", "80%", "85%", "99%"),
  prec = c("Medium (10 X 10 meters)", "High (3 X 3 meters)", "Very High (5 X 5 centimeters)",
           "Medium (10 X 10 meters)", "High (5 X 5 meters)", "Very High (10 X 10 centimeters)",
           "High (5 X 5 meters)", "High (5 X 5 meters)", "Very High (10 X 10 centimeters)",
           "Medium (10 X 10 meters)", "High (5 X 5 meters)", "Very High (10 X 10 centimeters)",
           "High (5 X 5 meters)", "High (5 X 5 meters)", "Very High (10 X 10 centimeters)"),
  own = c("Open to all", "AI-DSS Company only", "AI-DSS Company and you", "Open to all", "AI-DSS Company only",
          "AI-DSS Company and you", "AI-DSS Company and you", "AI-DSS Company only", "AI-DSS Company and you",
          "Open to all", "AI-DSS Company only", "AI-DSS Company and you", "AI-DSS Company and you", "AI-DSS Company only",
          "AI-DSS Company and you"))
chk <- merge(unique(d[, .(task, profile, attr_cost, attr_accuracy, attr_precision, attr_data_ownership)]), pdf, by = c("task", "profile"))
stopifnot(nrow(chk) == 15, chk[, all(attr_cost == cost & attr_accuracy == acc & attr_precision == prec & attr_data_ownership == own)])
d[, c("cost", "accuracy", "precision", "data") := NULL]
# the per-question answer copies agree with AIDSS
sel <- k[AIDSS == 1]; for (e in 1:5) stopifnot(all(sel[EXPERIMENT == e][[paste0("ChoiceExperiment", e)]] ==
                                                   c(4, 1, 2, 3)[sel[EXPERIMENT == e]$ChoiceSet]))
r <- k[!duplicated(ResponseID)]
lab <- function(x) as.character(as_factor(x, levels = "labels"))
stopifnot(all(r$Gender %in% c(1:4, NA)))
cv <- r[, .(id = match(ResponseID, ids), cov_country = CountryCode, cov_region = fifelse(Region == "", NA_character_, Region))]
spec <- c(Specialization_NutrientReco = "nutrient_recommendation", `_v1` = "pest_disease_management",
          Specialization_Seed_Selection = "seed_selection", Specialization_Tillage_Practices = "tillage_practices",
          Specialization_Crop_Rotations = "crop_rotation", Specialization_Cover_Crop = "cover_crop")
for (v in names(spec)) cv[, paste0("cov_specialization_", spec[[v]]) := as.integer(zap_labels(r[[v]]))]
for (i in 1:6) cv[, paste0("cov_ai_perception_", i) := as.integer(zap_labels(r[[paste0("AI_Perception", i)]]))]
for (i in 1:14) cv[, paste0("cov_pa_concern_", i) := as.integer(zap_labels(r[[paste0("PA_Concern", i)]]))]
for (i in 1:9) cv[, paste0("cov_dss_experience_", i) := as.integer(zap_labels(r[[paste0("DSS_Experience", i)]]))]
cv[, `:=`(cov_farm_size_acres = as.numeric(r$FarmSize_Acres), cov_experience_years = as.numeric(r$Experience_Years),
          cov_education = lab(r$Education), cov_gender = c("male", "female", "other", NA)[as.integer(zap_labels(r$Gender))],
          cov_race = lab(r$Race), cov_income = lab(r$Income), cov_employment = lab(r$EmploymentStatus), cov_age_group = lab(r$AgeGroup))]
cv[cov_race == "Prefer not to Answer", cov_race := NA][cov_income == "Wish not to say", cov_income := NA]
d <- merge(d, cv, by = "id")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)], d[, .N, .(id, task)][, all(N == 3)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "zia_2026_ai_decision_support.csv"))
