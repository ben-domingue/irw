##Canadian candidate conjoint (policy positions vs party cue) from
##Treger, C., Galipeau, T., Bergeron, T., Lachance, S., Goel, N., Islam, M. M., Lee-Whiting, B.,
##Magistro, B., & Loewen, P. J. (2026). Party or policy? The role of policy partisanship in voter
##decision-making. Political Behavior. https://doi.org/10.1007/s11109-026-10135-w
##Replication data: Harvard Dataverse doi:10.7910/DVN/AEZ83R, CC0 1.0. File read:
##main_data_party_or_policy.csv (Dataverse "original format" download of the .tab). The README
##and the authors' R script (Party_or_Policy_main_analysis_and_si_190226.R) were read as text.
##The deposit also re-hosts the 2021 Canadian Election Study, CHES 2023 and two StatCan tables
##(used only for the paper's sample-comparison and party-position tables); none is read here.
##Usage: Rscript treger_2026.R <dir holding the csv> <output dir>
##
##1,131 Canadian respondents, 3 pairs of hypothetical candidates each (6 rows per respondent).
##The paper is paywalled and was not read: sample source, dates, the question wordings, the
##rating anchors and the displayed text of the experience attribute are NOT documented in the
##deposit. The file has NO task or profile column: each respondent has exactly 6 consecutive
##rows; consecutive row pairs are taken as tasks (in every pair with a recorded choice exactly
##one profile has Y = 1), so task and profile are INFERRED from row order.
##Attributes (the d_* columns, as text in the file): gender (Man/Woman), experience (stored
##1/4/12; the authors' tables label these "Experience = 4 years", so stored here as "1 year",
##"4 years", "12 years" -- the authors' label, not verified display text), party (d_PID,
##Conservative/Liberal; shown only in the "Partisanship" arm, "(not shown)" in the "No
##partisanship" arm), and six policy positions with two levels each (climate, income
##redistribution, cost of living, deficit, housing, healthcare), stored as the text in the file.
##trial_arm = Treatment (randomized between respondents: party label shown or not).
##Outcomes (wording not in deposit): choice = Y (one candidate of the pair chosen; 339 of 3,393
##tasks have no choice recorded and keep choice NA where a rating exists); rating = scale, a
##1-7 rating of each candidate (direction inferred only from its association with choice: mean
##rating of chosen profiles 4.8 vs 3.3). Rows with neither outcome are dropped.
##Covariates as deposited (author recodes, no codebook): cov_pid (PID: Conservative, Liberal,
##NDP, Non-partisan), cov_male (0/1), cov_post_secondary (0/1), cov_citizen (0/1),
##cov_province_code (1-13, no labels), cov_income (as stored). cov_assoc_* (cc1..he2) are the
##respondent's earlier attribution of each policy option to a party (Conservative, Liberal,
##NDP, Non-partisan); per the authors' code option 1 is the left-leaning policy and option 2
##the right-leaning one, except housing where ho1 is right-leaning. Dropped: Qualtrics
##ResponseId (re-keyed to integers), all derived congruence / partisan-match factors (f_*,
##cong_*), sum_partisan2, PID2, d_PID-based recodes, PID_all.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "main_data_party_or_policy.csv"))
stopifnot(s[, .N, ResponseId][, all(N == 6)])
s[, r := seq_len(.N), by = ResponseId][, task := (r + 1L) %/% 2L][, profile := 2L - r %% 2L]
stopifnot(s[!is.na(Y), sum(Y), by = .(ResponseId, task)][, all(V1 == 1)],
          s[, uniqueN(is.na(Y)), by = .(ResponseId, task)][, all(V1 == 1)],
          s[, uniqueN(Treatment), ResponseId][, all(V1 == 1)])
s[, id := match(ResponseId, unique(ResponseId))]
stopifnot(all(s$d_experience %in% c(1, 4, 12)), s[Treatment == "Partisanship", !anyNA(d_PID)],
          s[Treatment == "No partisanship", all(is.na(d_PID))])
d <- s[, .(id = as.integer(id), task = as.integer(task), profile = as.integer(profile),
           choice = as.integer(Y), rating = as.integer(scale),
           attr_gender = d_gender,
           attr_experience = c(`1` = "1 year", `4` = "4 years", `12` = "12 years")[as.character(d_experience)],
           attr_party = fifelse(is.na(d_PID), "(not shown)", d_PID),
           attr_climate = d_climate, attr_income = d_income, attr_cost_of_living = d_cost,
           attr_deficit = d_deficit, attr_housing = d_housing, attr_healthcare = d_healthcare,
           trial_arm = Treatment,
           cov_pid = PID, cov_male = as.integer(male), cov_post_secondary = as.integer(post_secondary),
           cov_citizen = as.integer(citizen), cov_province_code = as.integer(province), cov_income = income,
           cov_assoc_climate_1 = cc1, cov_assoc_climate_2 = cc2, cov_assoc_income_1 = in1, cov_assoc_income_2 = in2,
           cov_assoc_cost_1 = co1, cov_assoc_cost_2 = co2, cov_assoc_deficit_1 = de1, cov_assoc_deficit_2 = de2,
           cov_assoc_housing_1 = ho1, cov_assoc_housing_2 = ho2, cov_assoc_healthcare_1 = he1, cov_assoc_healthcare_2 = he2)]
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), d[, uniqueN(get(v))] %in% 2:3)
d <- d[!(is.na(choice) & is.na(rating))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "treger_2026_party_or_policy.csv"))
