##North Carolina households' referendum votes on stream water quality action plans (ecosystem condition, health risk,
##murky water days, monthly stormwater fee), from the data set
##von Haefen, R. H., et al. (2023). Replication Data for: Estimating the Benefits of Stream Water Quality Improvements in
##Urbanizing Watersheds: An Ecological Production Function Approach [Data set]. Harvard Dataverse.
##https://doi.org/10.7910/DVN/Q2RXT0 (CC0 1.0; no restricted files, no terms). Article: von Haefen, R. H., et al.
##(2023). PNAS, 120(18), e2120252120. https://doi.org/10.1073/pnas.2120252120 (OA, PMC10160966; read).
##Files read: streams_sp_data_final.tab (raw survey data, 2,511 respondents, wide: one column per plan a-d), ce_data.tab
##(only for wgt_final), 4-ce_data_analysis.do and Readme-1.pdf (as text).
##Usage: Rscript vonhaefen_2023.R <dir holding the two .tab files> <output dir>
##
##Design (PNAS): online survey, Wake, Mecklenburg and Guilford counties (cov_county W/M/G), 2020-21. "Each SP choice
##task confronted respondents with a hypothetical action plan that would improve stream water quality but raise their
##monthly water bills through a new stormwater fee ... described by increases (decreases) in the percentage of stream
##miles in the best (worst) quality level categories for each ecological endpoint ... respondents could either vote for
##or against the proposed action plan through a county-level referendum format"; 10 blocks of four tasks. One profile
##per task (the plan); choice = ce (do-file label "Action Plan Vote (1 = Yes, 0 = No)"); voting against is the outside
##option (opt_out = yes). ce = -1 (no answer, 206 plan-responses) omitted. task = order_* ("Ordering of CEs (1 = First,
##4 = Last)", recorded); trial_plan = the plan letter a-d (the deposit's sequence id) and trial_block = block_id 1-10.
##The plan is fixed by block x plan letter (checked) and the same in all three counties. block_f (do-file: attributes
##presented in forward or reverse direction; which value is forward is not stated) is kept as trial_block_f.
##The county versions name different local streams (maps); the authors pool the counties in one model, so one table.
##CODED ATTRIBUTES (#3474). The article and the do-file labels give each column's meaning, but the displayed wording and
##number format are in the SI Appendix only (not read), so the deposit's values are kept as codes:
##  attr_cost_code: 4 / 9 / 18 / 32 (do-file "Action Plan Cost"; a monthly stormwater fee in US dollars per PNAS).
##  attr_ec_g_code / attr_ec_p_code: change in the percentage of stream miles with GOOD / POOR ecosystem condition.
##  attr_hr_g_code / attr_hr_p_code: change in the percentage of stream miles with LOW ("good") / HIGH ("poor") human
##    health risk.
##  attr_md_g_code / attr_md_p_code: same for murky water days (low / high).
##  (do-file labels "Ecosystem Conditions = % Good w/ Action Plan" etc.; values are changes, g + fair + poor = 0.) The
##  fair/medium columns (*_m) are dropped: they equal -(g + p) (checked) and PNAS says only the best and worst
##  categories were described.
##Covariates as deposited (codes unlabelled in the deposit): cov_county (W/M/G = Wake/Mecklenburg/Guilford per PNAS),
##cov_gender_code (0/1, -1 = missing), cov_age (years), cov_income (income midpoint in $, -1 = missing), cov_educ_code
##(-1-6), cov_access_mode_code (do-file: 1 = computer/tablet), cov_duration_sec (survey_duration in minutes x 60),
##cov_attention_pass (trap question debrief_3: 1 = "D", the answer the authors keep; 0 = other answer; NA = blank),
##cov_debrief_1, cov_debrief_2 (consequentiality statements, SA/A/N/D/SD as deposited; blank = NA),
##cov_survey_weight (wgt_final from ce_data.tab, the authors' post-stratification weight).
##The authors' analysis sample excludes 615 respondents: survey_duration < 8 minutes or > 1 week, failing the trap
##question, or answering D/SD to either consequentiality statement; reproduce it with cov_duration_sec >= 480 &
##cov_duration_sec <= 604800 & cov_attention_pass == 1 & !(cov_debrief_1 %in% c("D","SD")) &
##!(cov_debrief_2 %in% c("D","SD")) (PNAS: 1,896 respondents, 7,584 tasks). Not applied here.
##Dropped: resp_id (re-keyed), code (6-digit invitation code), survey_date, incentive, demographic detail (employment,
##housing, household, race items), debrief_4-11, attribute_1-3, stream/activity/causes/info items, comments (free text),
##near_dist (distance to nearest stream). PII: none read; the deposit also holds lat/long files (not downloaded).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fs <- list.files(raw, full.names = TRUE)
k <- fread(grep("streams_sp_data_final", fs, value = TRUE))
w <- fread(grep("ce_data", fs, value = TRUE), select = c("resp_id", "wgt_final"))
stopifnot(nrow(k) == 2511L, uniqueN(k$resp_id) == 2511L, w[, uniqueN(wgt_final), resp_id][, all(V1 == 1L)])
w <- unique(w)
L <- c("a", "b", "c", "d")
s <- rbindlist(lapply(L, function(x) {
  g <- function(v) k[[paste0(v, "_", x)]]
  data.table(resp_id = k$resp_id, plan = x, block = k$block_id, ce = g("ce"), order = g("order"), cost = g("cost"),
             ec_g = g("ec_g"), ec_m = g("ec_m"), ec_p = g("ec_p"), hr_g = g("hr_g"), hr_m = g("hr_m"), hr_p = g("hr_p"),
             md_g = g("md_g"), md_m = g("md_m"), md_p = g("md_p"))
}))
stopifnot(s[, all(ec_g + ec_m + ec_p == 0 & hr_g + hr_m + hr_p == 0 & md_g + md_m + md_p == 0)])
stopifnot(s[, uniqueN(paste(cost, ec_g, ec_p, hr_g, hr_p, md_g, md_p)), .(block, plan)][, all(V1 == 1L)])
stopifnot(s[, all(sort(order) == 1:4), resp_id]$V1, all(s$ce %in% c(-1L, 0L, 1L)))
s <- s[ce != -1L]
s <- merge(s, k[, .(resp_id, block_f, county, gender, age, income, educ, access_mode, survey_duration, debrief_1,
                    debrief_2, debrief_3)], by = "resp_id")
s <- merge(s, w, by = "resp_id", all.x = TRUE)
na_blank <- function(x) ifelse(x == "", NA_character_, x)
d <- s[, .(id = match(resp_id, sort(k$resp_id)), task = as.integer(order), profile = 1L, choice = as.integer(ce),
  attr_cost_code = as.integer(cost), attr_ec_g_code = ec_g, attr_ec_p_code = ec_p, attr_hr_g_code = hr_g,
  attr_hr_p_code = hr_p, attr_md_g_code = md_g, attr_md_p_code = md_p,
  trial_plan = plan, trial_block = as.integer(block), trial_block_f = as.integer(block_f),
  cov_county = county, cov_gender_code = as.integer(gender), cov_age = as.integer(age), cov_income = income,
  cov_educ_code = as.integer(educ), cov_access_mode_code = as.integer(access_mode),
  cov_duration_sec = round(survey_duration * 60), cov_attention_pass = fifelse(debrief_3 == "", NA_integer_, as.integer(debrief_3 == "D")),
  cov_debrief_1 = na_blank(debrief_1), cov_debrief_2 = na_blank(debrief_2), cov_survey_weight = wgt_final)]
stopifnot(!anyNA(d$cov_survey_weight), d[, .N, .(id, task)][, all(N == 1L)], all(d$cov_county %in% c("W", "M", "G")))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "vonhaefen_2023_stream_quality.csv"))
cat(nrow(d), uniqueN(d$id), mean(d$choice), "\n")
