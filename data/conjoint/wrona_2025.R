##Teachers' job preferences: a discrete choice experiment in Kutno, Poland, from
##Wrona, S., Gajderowicz, T., & Jakubowski, M. (2025). How to keep teachers in a profession in times of budget
##shortages? European Journal of Teacher Education, 48(1), 178-199. https://doi.org/10.1080/02619768.2025.2454635
##(article behind a publisher wall: not read; N not compared).
##Data: Gajderowicz, T. (2025). How to keep teachers in a profession in times of budget shortages? RepOD,
##doi:10.58132/43ILCE, CC BY 4.0 (dataset page and file-level licence: "CC BY - Creative Commons Attribution 4.0").
##Files read: Data_Teachers.tab and Codebook_Teachers.tab (variable labels only, no value labels).
##Usage: Rscript wrona_2025.R <dir holding Data_Teachers.tab> <output dir>
##
##Teachers of the city of Kutno (Poland); long file, one row per respondent x choice set x alternative (3 per set):
##two job profiles (altnr 1, 2) and altnr 3, a row with every attribute blank = the opt-out (the third alternative,
##chosen in 36% of sets; its wording is not documented). `choice` in the file is the number of the selected
##alternative and `selected` the 0/1 flag; choice = 1 on the selected job profile, 0 on both when alt 3 was chosen.
##Exactly one selected row per set (verified). 8 choice sets per respondent.
##Respondent id: userid is a code ("N001001"); userid N009052 holds two people (useridno 141 and 3, with different
##demographics, 24 rows each), so the respondent key is (userid, useridno): 225 respondents (the deposit counts 224
##userids). N002004 has 7 sets (21 rows). Ids re-keyed to integers in order of first appearance.
##Task order is INFERRED from row order within respondent (each 3 consecutive rows are one set, altnr 1,2,3; the file
##also carries choicesetid, the design set id, which repeats across respondents): task_source = inferred.
##Attributes and LABELS (codes only for two): classes = weekly number of compulsory teaching hours (18-23), admintask =
##weekly hours devoted to administrative tasks (0-5), extraclass = weekly hours devoted to extracurricular
##activities (0-5), salary = monthly net salary in PLN, supervisor = being a class supervisor (0/1, written
##No/Yes from the variable label), BENEFITS ("Fringe benefits") and CONDITIONS ("Working conditions") are 0-5 codes
##with no value labels in the codebook and no article access: stored as the codes with the attribute name
##("LABELS: codes only" for these two). Hours are written "N hours per week" and salary "N PLN per month" from the
##variable labels.
##Restrictions: none documented. Level weights: unknown (shares near equal for most attributes).
##Covariates (codebook gives no value labels): cov_gender_code (gender, 0/1), cov_age_code (age, 1-7),
##cov_education_code (educ, 5-7). Dropped: tenure, subjects, career status, number of jobs, osobochoice.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "Data_Teachers.tab"))
stopifnot(nrow(x) == 5397)
x[, key := paste(userid, useridno)]
x[, rid := match(key, unique(key))]
x[, k := seq_len(.N), rid]
x[, task := (k - 1L) %/% 3L + 1L]
stopifnot(x[, all(altnr == (k - 1L) %% 3L + 1L)], x[, .N, rid][, all(N %in% c(21L, 24L))], x[, sum(selected), .(rid, task)][, all(V1 == 1)])
stopifnot(x[altnr == 3, all(is.na(salary))], x[altnr < 3, !anyNA(salary)])
p <- x[altnr < 3]
d <- p[, .(id = rid, task, profile = altnr, choice = as.integer(selected),
  attr_class_hours = paste(classes, "hours per week"), attr_admin_hours = paste(admintask, "hours per week"),
  attr_extracurricular_hours = paste(extraclass, "hours per week"), attr_class_supervisor = c("No", "Yes")[supervisor + 1L],
  attr_fringe_benefits = as.character(benefits), attr_working_conditions = as.character(conditions),
  attr_salary = paste(salary, "PLN per month"),
  cov_gender_code = gender, cov_age_code = age, cov_education_code = educ)]
stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wrona_2025_teacher_jobs.csv"))
