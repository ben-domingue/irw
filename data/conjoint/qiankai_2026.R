##Older adults in long-term care facilities choosing between two mealtime arrangements (DCE), from the data set
##QIANKAI (2026). Preferences for mealtime among older adults in long-term care facilities: a discrete choice
##experiment [Data set]. OSF. https://doi.org/10.17605/OSF.IO/K4YND (CC BY-NC 4.0, OSF node licence). The OSF
##contributor is listed under one name only; no article, questionnaire or codebook is linked or deposited.
##Files read: DCE-sample.xlsx (Sheet1: 2,760 rows = 230 residents x 6 choice sets x 2 alternatives) and
##"Demographic Characteristics.xlsx" (230 rows, raw demographics; id = personid, checked against the banded *_b
##columns of the DCE file: age_b, sex_b, grade_b, BI_b and time_b all agree with the raw values).
##Usage: Rscript qiankai_2026.R <dir holding both xlsx> <output dir>
##
##Design: 6 choice sets (cno, task as recorded; display order not stated) x 2 alternatives (alt, profile 1/2), forced
##choice (exactly one chosen per set, checked; no opt-out column or none alternative; ASC = 1 on alt 1 is a model
##constant, dropped). Fixed blocked design: version 1-3; within block x set x alternative the levels are identical for
##all respondents except one respondent labelled version 3 whose six sets all differ from the other 74 in version 3
##(kept as deposited; possibly a fourth block or a mislabelled version).
##CODED ATTRIBUTES (#3474). No source gives the attribute names or displayed levels; every attribute keeps the deposit's
##level index (0-based, as in a design matrix), named after the deposit's variable: attr_loc_code (0-2),
##attr_ass_code (0/1), attr_taste_code (0-2), attr_typ_code (0-3), attr_form_code (0-2), attr_cost_code
##(800/1000/1200/1400; cost, currency and period not stated). Nothing is known about what each index means
##(the variable names suggest location, assistance, taste, type, form, cost, which is not confirmed). attr_ass_code is
##treated as a two-level index like the other 0-based codes, not as a presence dummy: no source says 1 = presence.
##Outcome: choice between the two alternatives; wording unknown; opt_out = no.
##Covariates: the raw demographics, codes unlabelled: cov_age (years), cov_sex_code (1/2), cov_grade_code (1-4),
##cov_time (numeric, 0.2-15; the banding time_b suggests years), cov_degree_code, cov_marital_code, cov_child_code,
##cov_income_code, cov_totalfee, cov_foodfee (amounts, units not stated), cov_chronic_code, cov_mna, cov_bi, cov_amt
##(scores as deposited; names suggest MNA nutrition, Barthel index, Abbreviated Mental Test -- not confirmed).
##Dropped: obsid, version (kept as trial_version), ASC, the banded *_b covariates (derived from the raw ones).
##No exclusions applied. PII: none (integer ids).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_excel(file.path(raw, "DCE-sample.xlsx"), sheet = "Sheet1"))
m <- as.data.table(read_excel(file.path(raw, "Demographic Characteristics.xlsx"), sheet = "Sheet1"))
stopifnot(nrow(k) == 2760L, uniqueN(k$personid) == 230L, nrow(m) == 230L, setequal(m$id, k$personid))
stopifnot(k[, .(s = sum(choice), n = .N, a = paste(sort(alt), collapse = "")), .(personid, cno)][, all(s == 1 & n == 2L & a == "12")])
stopifnot(k[, uniqueN(cno), personid][, all(V1 == 6L)], k[, uniqueN(version), personid][, all(V1 == 1L)])
r <- merge(unique(k[, .(personid, age_b, sex_b)]), m, by.x = "personid", by.y = "id")
stopifnot(nrow(r) == 230L, r[, all(findInterval(age, c(70, 80, 90)) == age_b)], r[, all(sex - 1 == sex_b)])
stopifnot(all(k$loc %in% 0:2), all(k$ass %in% 0:1), all(k$taste %in% 0:2), all(k$typ %in% 0:3), all(k$form %in% 0:2),
          all(k$cost %in% c(800, 1000, 1200, 1400)))
d <- k[, .(id = as.integer(personid), task = as.integer(cno), profile = as.integer(alt), choice = as.integer(choice),
  attr_loc_code = as.integer(loc), attr_ass_code = as.integer(ass), attr_taste_code = as.integer(taste),
  attr_typ_code = as.integer(typ), attr_form_code = as.integer(form), attr_cost_code = as.integer(cost),
  trial_version = as.integer(version))]
d <- merge(d, m[, .(id = as.integer(id), cov_age = age, cov_sex_code = sex, cov_grade_code = grade, cov_time = time,
  cov_degree_code = degree, cov_marital_code = marital, cov_child_code = child, cov_income_code = income,
  cov_totalfee = totalfee, cov_foodfee = foodfee, cov_chronic_code = chronic, cov_mna = MNA, cov_bi = BI, cov_amt = AMT)],
  by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "qiankai_2026_mealtime_ltc.csv"))
cat(nrow(d), uniqueN(d$id), "\n")
