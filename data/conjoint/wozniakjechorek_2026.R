##Remote-work job conjoint (US full-time employees, March 2022) from
##Wozniak-Jechorek, B., D'Urso, A. S., Thurston, C. N., & Patnaik, M. (2026). Understanding
##employee trade-offs in remote work: Toward more sustainable workplace design. Journal of
##Strategic Information Systems, 35(2), 101970. https://doi.org/10.1016/j.jsis.2026.101970
##Replication data: Harvard Dataverse doi:10.7910/DVN/OHIKOR, CC0 1.0, no restricted files.
##File read: rw_dat.rds (the authors' cleaned long file, 12,560 rows = respondent x task x
##profile, attribute levels as text). README.docx and the analysis .Rmd files read as text (not
##run). The article was not accessible (paywalled); facts below come from the deposit and the
##article's abstract (choice-based conjoint, 627 full-time US workers).
##Usage: Rscript wozniakjechorek_2026.R <raw dir> <output dir>
##
##Qualtrics survey, 25-27 March 2022 (start_date), full-time employees (demo_employment). 10
##tasks (iteration = task, recorded), each a pair of jobs (source profile a = 1, b = 2), 6
##attributes: Work location (Fully remote / Mostly remote / Remote-leaning / Office-leaning /
##Mostly office), Salary (15% salary reduction / Salary unchanged / 15% salary increase),
##Supervision (No monitoring control / Time-tracking control / Performance control), Work
##schedule flexibility (Employer-set standard hours / Flexible schedules / Self-set fixed hours),
##Expense reimbursement (Employer-funded / Employee-funded / Government tax-credit), Support
##resources (Structured upskilling / Mentoring / Workplace social events / Annual retreats /
##Performance reward trip). Level text as stored by the authors (displayed wording not
##deposited). Attribute order, restrictions and level probabilities are not documented. No
##identical pairs occur.
##Outcome: choice = job_picked, which of the two jobs the respondent picked (forced choice; one
##pick in every answered task). Question wording not in the deposit -> unknown.
##Dropped tasks/respondents: 2 tasks with no pick (job_7/job_8 NA; unanswered). One panel
##respondent (respondent_id) took the survey twice, 4 minutes apart (two Qualtrics response_ids,
##same birth year, gender and state): the second response is dropped, giving the article's 627
##respondents (the authors' code clusters by response_id, 628). 627 x 10 x 2 - 4 = 12,536 rows.
##PII in the deposit, dropped: ip_address, location_latitude/longitude, response_id (Qualtrics),
##respondent_id and pid (panel IDs), free-text fields (*_text). Also dropped: dates, status,
##progress, page timers (q*_click), consent, the wide job_1..job_10 answers (= job_picked), the
##authors' derived dummies (white, female, married, pid3) and the items q327, q330, q331_41,
##q331_44 (wording not deposited). IDs re-keyed to integers in file order.
##Covariates (answer text as stored; deposit labels): cov_gender (gender: Male / Female /
##Non-binary -> male / female / other), cov_birth_year (demo_age: the source stores the year of
##birth), cov_age (age: the authors' 2022 - birth year), cov_education (demo_educ),
##cov_party_id (demo_pid3: Democrat / Republican / Independent / Other / Not sure),
##cov_party_strength_dem, cov_party_strength_rep, cov_party_lean, cov_ideology (7 labels),
##cov_race, cov_citizen, cov_marital (demo_married), cov_income, cov_employment, cov_state,
##cov_religion, cov_vote2020, cov_biden_approval, cov_econ, cov_finance_worry,
##cov_duration_sec (whole-survey duration_in_seconds). No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- as.data.table(readRDS(file.path(raw, "rw_dat.rds")))
r[] <- lapply(r, function(x) if (is.factor(x)) as.character(x) else x)
stopifnot(nrow(r) == 12560, r[, .N, .(response_id, iteration)][, all(N == 2)])
# one panel respondent answered twice: keep the earlier response
two <- r[, .(n = uniqueN(response_id)), respondent_id][n > 1, respondent_id]
stopifnot(length(two) == 1)
dropresp <- r[respondent_id == two][order(as.POSIXct(start_date, format = "%m/%d/%y %H:%M")), unique(response_id)][2]
r <- r[response_id != dropresp]
# unanswered tasks
r[, npick := sum(job_picked), .(response_id, iteration)]
stopifnot(r[, all(npick %in% 0:1)], r[npick == 0, uniqueN(paste(response_id, iteration))] == 2)
r <- r[npick == 1]
ids <- unique(r$response_id)
d <- r[, .(id = match(response_id, ids), task = as.integer(iteration), profile = match(profile, c("a", "b")),
           choice = as.integer(job_picked),
           attr_work_location = `Work location`, attr_salary = Salary, attr_supervision = Supervision,
           attr_schedule_flexibility = `Work schedule flexibility`, attr_expense_reimbursement = `Expense reimbursement`,
           attr_support_resources = `Support resources`,
           cov_gender = c(Male = "male", Female = "female", "Non-binary" = "other")[gender],
           cov_birth_year = as.integer(demo_age), cov_age = as.integer(age), cov_education = demo_educ,
           cov_party_id = demo_pid3, cov_party_strength_dem = demo_strongdem, cov_party_strength_rep = demo_strongrep,
           cov_party_lean = demo_lean, cov_ideology = demo_ideology, cov_race = demo_race, cov_citizen = demo_citizen,
           cov_marital = demo_married, cov_income = income, cov_employment = demo_employment, cov_state = demo_state,
           cov_religion = relig_resp, cov_vote2020 = gap_vote2020, cov_biden_approval = gap_bidenapproval,
           cov_econ = gap_econ, cov_finance_worry = gap_financeworry, cov_duration_sec = duration_in_seconds)]
stopifnot(!anyNA(d$profile), all(is.na(d$cov_gender) == is.na(r$gender)),
          d[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(d$id) == 627, nrow(d) == 12536,
          d[, all(complete.cases(.SD)), .SDcols = patterns("^attr_")])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wozniakjechorek_2026_remote_work.csv"))
