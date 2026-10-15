##Time-restriction randomized choice experiments (Shenzhen, China): health insurance DCE and hearing-loss
##prevention DCE. Data set: Jiang, Y. (2025). Decision time both influences and reflects willingness to pay for
##health-related risk reduction [Data set]. Mendeley Data. (The journal article behind the data set was not found;
##doi field empty; the title is the deposit title.)
##Data: Mendeley Data doi:10.17632/9hdcpnrbcc.1, CC BY 4.0 (Mendeley public API, data_licence). Files read from the
##zip "data and code files used for analyses.zip": no_time_restrict_original_data_to_reshape.dta and
##time_restrict_original_data_to_reshape.dta (insurance DCE, long); no_time_restrict_indecis_base_indvidual.dta and
##time_restrict_indecis_base_indvidual.dta (respondent covariates, 29 columns, no IP); and for the hearing DCE only the
##columns "RespondentID" and "任务k_j..." (task k, alternative j: probability, degree, cost, chosen) of
##time_nonrestrict_indecis_base_hearing_indvidual.dta and time_restrict_indecis_base_hearing_indvidual.dta.
##Usage: Rscript jiang_2025.R <dir holding the extracted .dta files> <output dir>
##
##Online survey of adults in Shenzhen (the Chinese questionnaire, 2022-2023 per the file contents). Respondents were
##randomized to a time-restricted arm (532; a time limit on the DCE) or an unrestricted arm (531): trial_time_restricted
##1/0. Each respondent answered two DCEs of 10 tasks each, which are two tables:
## (1) jiang_2025_time_insurance: choose between two health-insurance plans or neither (the third row of every task
##     in the file has no attributes and is the opt-out: opt_out = yes, rows dropped; chosen in 594 + 599 of
##     10,630 tasks). Seven attributes: premium, inpatient deductible, outpatient deductible, inpatient reimbursement
##     rate, outpatient reimbursement rate, inpatient cap, outpatient cap.
##     LABELS: UNITS NOT RECOVERABLE. The deposit stores bare numbers (premium 50/100/200; deductibles 0-50,000;
##     reimbursement rates 50/70/90; inpatient cap 50/100/150; outpatient cap 30/50/100); the Stata code divides the cap
##     by 10 for a WTP in the premium unit, so the cap unit differs from the premium unit. The attr_ cells hold the
##     stored number as text with no unit; currency (probably yuan), period and the cap unit are not stated.
## (2) jiang_2025_time_hearing: choose among three drug-prevention scenarios for a disease that may cause deafness,
##     or none. Attributes (the Chinese text respondents saw, translated by me): probability that the disease causes
##     deafness (10%-90%, shown as "70%"), degree of deafness (单耳失聪 = "One-ear deafness", 双耳失聪 = "Both-ear
##     deafness"), total cost of the drug to prevent the disease (1000/5000/10000/15000/30000 元 = "yuan"). No row
##     exists for the none option: a task with attributes shown and no chosen alternative is the opt-out
##     (opt_out = yes). Tasks whose attribute cells are blank ("(空)", about 33 tasks) are dropped as not shown.
##Restrictions: none documented (no article or design file); level weights: not documented -> unknown.
##task = TaskID/number 1-10, profile = alternative order, assumed the order shown.
##Attribute order fixed (assumed).
##Covariates (both tables): cov_age (years, as recorded), cov_gender (male = 1 in the file's `male`), cov_college_and_above
##(0/1 as in the file), cov_married, cov_has_child, cov_has_chronic_disease (0/1; the authors' own dummies are kept
##because the raw answers carry a date of birth and IP, which are not used).
##Dropped / PII: the raw hearing files carry IP addresses ("来自IP"), submission times, date of birth, source and 380
##other survey columns; none was read. The insurance files hold only the model-ready columns.
##N vs paper: article not found; 531 + 532 = 1,063 respondents matches the deposit's own count.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fp <- function(n) list.files(raw, pattern = paste0("^", n, "$"), full.names = TRUE, recursive = TRUE)[1]
rd <- function(n, ...) as.data.table(zap_labels(read_dta(fp(n), ...)))
arms <- list(c("no_time", 0L), c("time", 1L))
cov <- rbindlist(lapply(arms, function(z) { x <- rd(paste0(z[1], "_restrict_indecis_base_indvidual.dta"))
  x[, .(arm = as.integer(z[2]), rid = RespondentID, cov_age = ifelse(age >= 15 & age <= 100, as.integer(age), NA_integer_),
    cov_gender = ifelse(male == 1, "male", ifelse(male == 0, "female", NA_character_)),
    cov_college_and_above = as.integer(college_and_above), cov_married = as.integer(married),
    cov_has_child = as.integer(has_child), cov_has_chronic_disease = as.integer(has_any_chronic))] }))
cov[, id := .I]
## ---- insurance
ins <- rbindlist(lapply(arms, function(z) { x <- rd(paste0(z[1], "_restrict_original_data_to_reshape.dta")); x[, arm := as.integer(z[2])]; x }))
stopifnot(ins[, .N, .(arm, RespondentID)][, all(N == 30)], ins[, sum(choice_indicator), .(arm, GroupID)][, all(V1 == 1)],
  ins[TaskAlternativeN == 3, all(is.na(DCEtask_premium))], ins[TaskAlternativeN < 3, !anyNA(DCEtask_premium)])
ins <- merge(ins, cov, by.x = c("arm", "RespondentID"), by.y = c("arm", "rid"))
n <- function(v) as.character(as.integer(v))
d <- ins[TaskAlternativeN < 3, .(id, task = as.integer(TaskID), profile = as.integer(TaskAlternativeN), choice = as.integer(choice_indicator),
  attr_premium = n(DCEtask_premium), attr_inpatient_deductible = n(DCEtask_inpatient_deductible),
  attr_outpatient_deductible = n(DCEtask_outpatient_deductible), attr_inpatient_reimbursement_rate = n(DCEtask_inpatient_reimb_rate),
  attr_outpatient_reimbursement_rate = n(DCEtask_outpatient_reimb_rate), attr_inpatient_cap = n(DCEtask_inpatient_cap),
  attr_outpatient_cap = n(DCEtask_outpatient_cap),
  cov_age, cov_gender, cov_college_and_above, cov_married, cov_has_child, cov_has_chronic_disease, trial_time_restricted = arm)]
stopifnot(uniqueN(d$id) == 1063, d[, .N, .(id, task)][, all(N == 2)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile); fwrite(d, file.path(out, "jiang_2025_time_insurance.csv"))
## ---- hearing
hr <- rbindlist(lapply(arms, function(z) {
  f <- fp(paste0("time_", if (z[1] == "no_time") "nonrestrict" else "restrict", "_indecis_base_hearing_indvidual.dta"))
  nm <- names(read_dta(f, n_max = 0)); k <- nm[c(1, grep("^任务[0-9]+_[0-9]", nm))]
  x <- as.data.table(zap_labels(read_dta(f, col_select = all_of(k))))
  l <- rbindlist(lapply(1:10, function(t) rbindlist(lapply(1:3, function(j) {
    p <- paste0("任务", t, "_", j)
    data.table(rid = x$RespondentID, task = t, profile = j, prob = x[[paste0(p, "该病导致失聪概率")]], deg = x[[paste0(p, "该病导致失聪程度")]],
      cost = x[[paste0(p, "预防该病药品总费用")]], sel = x[[paste0(p, "是否选中")]]) }))))
  l[, arm := as.integer(z[2])]; l }))
hr <- hr[!(prob %in% c("(空)", "") | deg %in% c("(空)", "") | cost %in% c("(空)", ""))]
stopifnot(hr[, all(sel %in% c("是", "否"))], hr[, .N, .(arm, rid, task)][, all(N == 3)], hr[, sum(sel == "是"), .(arm, rid, task)][, all(V1 <= 1)])
hr <- merge(hr, cov, by = c("arm", "rid"))
dg <- c("单耳失聪" = "One-ear deafness", "双耳失聪" = "Both-ear deafness")
h <- hr[, .(id, task, profile, choice = as.integer(sel == "是"), attr_deafness_probability = prob, attr_deafness_degree = unname(dg[deg]),
  attr_prevention_drug_cost = paste(sub("元$", "", cost), "yuan"),
  cov_age, cov_gender, cov_college_and_above, cov_married, cov_has_child, cov_has_chronic_disease, trial_time_restricted = arm)]
stopifnot(!anyNA(h[, .SD, .SDcols = patterns("^attr_")]))
setorder(h, id, task, profile); fwrite(h, file.path(out, "jiang_2025_time_hearing.csv"))
