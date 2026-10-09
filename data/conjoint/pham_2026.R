##Rural-practice job DCE among family physicians (Vietnam) from
##Pham, C. A. T., Le, N. Q. T., & Kim, D. (2026). What drives family physicians to rural practice?
##A discrete choice experiment in Vietnam. Health Policy OPEN, 11, 100175.
##https://doi.org/10.1016/j.hpopen.2026.100175
##Data: Le, N. Q. T. (2026). Discrete choice experiment dataset on job preferences among family
##physicians in Vietnam [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22070298, CC BY 4.0
##(Zenodo record licence). Files read (from DCE_JobPreferences_FamilyPhysicians_Dataset.zip):
##01.DCE analysis.csv, 02.Respondents minimized.csv, 03.Choice design.csv, 04.Codebook.csv,
##README.md, DCE_Choice_cards.pdf (the 20 bilingual cards; attribute text taken from them).
##Usage: Rscript pham_2026.R <dir holding the unzipped files> <output dir>
##
##315 family physicians and physician assistants (README; the questionnaire PDF has no extractable
##text, so sampling details are not repeated here). Fixed blocked design: 20 cards in 2 blocks of
##10 (03.Choice design.csv); each respondent answered the 10 cards of one block. Card 8 (block 1)
##repeats card 1 and card 18 (block 2) repeats card 11; the deposit EXCLUDES these repeat answers
##(README), so 9 tasks per respondent remain. task = task_order_original (the position among the
##10 cards as administered, 1-10), so one position per respondent is missing (the repeat card).
##Profiles: Job A (1) and Job B (2). The third alternative, "Current job (status quo)", showed no
##attributes on the card (its attributes in 01.DCE analysis.csv are the authors' characterisation
##of each respondent's current job from the questionnaire, README "Status-quo alternative") and is
##not a profile: it is the opt-out of choice_final.
##Outcomes (card wording, Vietnamese with English on the card):
##  choice       = choice_forced, "Between jobs A and B, which job do you prefer?" (Giữa A và B,
##                 công việc nào anh/chị mong muốn hơn?) Job A / Job B, no opt-out.
##  choice_final = choice_final, "Which job would you choose in practice?" (Trong thực tế, nếu chỉ
##                 lựa chọn một, anh/chị sẽ chọn?) Job A / Job B / Current job. OPT-OUT: when the
##                 current job is chosen both profiles are 0.
##Attributes: codes (04.Codebook.csv) mapped to the English line printed on each card, checked
##against all 20 cards: income_change_pct -30/0/50/100 = "30% decrease in income" / "No change in
##income" / "50% increase in income" / "100% increase in income"; promotion_within_1y 1/0 = "Be
##promoted immediately" / "Be promoted later"; urban_location 1/0 = "Urban work location" / "Rural
##work location"; easy_private_practice 1/0 = "High chance of opening a private clinic" / "Low
##chance of opening a private clinic". The Vietnamese line printed above each (e.g. "Thu nhập giảm
##30%") is not stored. Attribute order on the cards is fixed (income, promotion, location,
##private clinic).
##Covariates (02.Respondents minimized.csv, codebook): cov_gender (female 1 = female, 0 = male),
##cov_age_over_50 (1 = older than 50), cov_university_doctor (1 = university doctor, 0 = assistant
##doctor), cov_married, cov_rural_born, cov_rural_internship, cov_current_job_level (1-5 as codebook
##text: commune, district, provincial, national, private), cov_current_urban. trial_block = block,
##trial_card = card_id.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "01.DCE analysis.csv"), encoding = "UTF-8")
r <- fread(file.path(raw, "02.Respondents minimized.csv"), encoding = "UTF-8")
g <- fread(file.path(raw, "03.Choice design.csv"), encoding = "UTF-8")
setnames(s, sub("^﻿", "", names(s))); setnames(r, sub("^﻿", "", names(r))); setnames(g, sub("^﻿", "", names(g)))
stopifnot(nrow(s) == 8505, uniqueN(s$respondent_id) == 315, s[, .N, respondent_id][, all(N == 27)])
stopifnot(!any(s$card_id %in% c(8, 18)), s[, uniqueN(task_order_original), respondent_id][, all(V1 == 9)])
# the analysis file's attributes for A/B equal the published design
chk <- merge(s[alternative_id %in% 1:2], g, by = c("block_id", "card_id", "alternative_id"), suffixes = c("", ".g"))
stopifnot(nrow(chk) == 315 * 9 * 2, chk[, all(income_change_pct == income_change_pct.g & promotion_within_1y == promotion_within_1y.g &
                                             urban_location == urban_location.g & easy_private_practice == easy_private_practice.g)])
stopifnot(s[, sum(choice_final), choice_set_id][, all(V1 == 1)], s[alternative_id %in% 1:2, sum(choice_forced), choice_set_id][, all(V1 == 1)])
d <- s[alternative_id %in% 1:2, .(id = respondent_id, task = task_order_original, profile = alternative_id,
                                  choice = as.integer(choice_forced), choice_final = as.integer(choice_final),
                                  attr_income = c("-30" = "30% decrease in income", "0" = "No change in income", "50" = "50% increase in income",
                                                  "100" = "100% increase in income")[as.character(income_change_pct)],
                                  attr_promotion = c("1" = "Be promoted immediately", "0" = "Be promoted later")[as.character(promotion_within_1y)],
                                  attr_location = c("1" = "Urban work location", "0" = "Rural work location")[as.character(urban_location)],
                                  attr_private_clinic = c("1" = "High chance of opening a private clinic",
                                                          "0" = "Low chance of opening a private clinic")[as.character(easy_private_practice)],
                                  trial_block = block_id, trial_card = card_id)]
stopifnot(!anyNA(d))
cv <- r[, .(id = respondent_id, cov_gender = c("male", "female")[female + 1L], cov_age_over_50 = age_over_50,
            cov_university_doctor = university_doctor, cov_married = married, cov_rural_born = rural_born,
            cov_rural_internship = rural_internship,
            cov_current_job_level = c("commune", "district", "provincial", "national", "private")[current_job_level],
            cov_current_urban = current_urban)]
stopifnot(nrow(cv) == 315, all(r$female %in% 0:1), all(r$current_job_level %in% 1:5))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pham_2026_rural_jobs.csv"))
