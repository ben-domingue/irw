##Factorial-survey vignettes of just earnings from
##Wysieńska-Di Carlo, K., & Karpiński, Z. (2024). Status and just gender pay gaps: results of a
##vignette study. Socius. https://doi.org/10.1177/23780231241227158
##Replication data: Harvard Dataverse doi:10.7910/DVN/CKJI71, CC0 1.0. File read:
##vignette-study-1-just-earnings.sav (SPSS original; value labels), data structure PDF
##(vignette-study-1-data-structure.pdf) used as the codebook. The .tab and .RData copies are not read.
##Usage: Rscript wysienska_2024.R <dir holding the .sav> <output dir>
##
##Polish nationwide non-probability sample (2017, quota-matched on gender, age, education, region), 2,001
##recruited; the file has 1,964 respondents with 38,183 vignette ratings (most have 21). Each vignette describes a
##hypothetical worker: occupation (21 occupations, English titles from the data), gender (male/female), age
##(30-65 in 5-year steps), number of children (0-4) and years of job experience (1-40); the respondent states the
##amount of earnings in PLN that is just for that worker. The vignette wording (period, net/gross) is not in the
##deposit. Table = one rating per vignette, profile = 1, one vignette per task.
##  rating = `just`, "the amount of earnings (in PLN) that the respondent thinks is just" for the vignette
##           (codebook wording; continuous, observed range 213-144,812; higher = more earnings).
##Task order: the file has no order variable; vignid (996 ids) is the vignette's id, not its position. Rows are not
##sorted by vignid within respondent, so task = row order within respondent (inferred; task_source inferred);
##vignid is kept as trial_vignette_id. Job experience is tied to age (never above age-ish), so combinations are restricted
##(observed, not documented). No opt-out. Survey weight: none in the deposit.
##Covariates: cov_gender from r_gender (SPSS value labels male/female). Dropped: derived columns (lnjust, v_isco*,
##v_psco, prestige and segregation scales, prop_fem, dummies v_high/v_agebin/v_childcat). The paper's N (2,001) is the
##recruited sample; 1,964 respondents appear in the vignette file.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_sav(file.path(raw, "vignette-study-1-just-earnings.sav")))
d <- data.table(id = as.integer(factor(k$respid)), rating = k$just,
                attr_occupation = k$v_occ, attr_gender = as.character(as_factor(k$v_gender)),
                attr_age = as.character(as.integer(k$v_age)), attr_children = as.character(as.integer(k$v_child)),
                attr_job_experience = as.character(as.integer(k$v_jobexp)),
                cov_gender = as.character(as_factor(k$r_gender)), trial_vignette_id = as.integer(k$vignid))
d[, task := seq_len(.N), id][, profile := 1L]
stopifnot(!anyNA(d[, .(rating, attr_occupation, attr_gender, attr_age, attr_children, attr_job_experience)]),
          d[, all(cov_gender %in% c("male", "female"))], d[, all(attr_gender %in% c("male", "female"))])
d[, attr_gender := tools::toTitleCase(attr_gender)]
setcolorder(d, c("id", "task", "profile")); setorder(d, id, task, profile)
fwrite(d, file.path(out, "wysienska_2024_just_pay.csv"))
