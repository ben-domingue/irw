##Police-recruitment conjoint (Yonkers, NY residents and police officers) from
##Peyton, K., Weiss, C. M., & Vaughn, P. E. (2022). Beliefs about minority representation in
##policing and support for diversification. Proceedings of the National Academy of Sciences,
##119(52), e2213986119. https://doi.org/10.1073/pnas.2213986119
##Replication data: Harvard Dataverse doi:10.7910/DVN/VU1JI1, CC0 1.0, no restricted files.
##Files read: conjoints_stacked.rds (16,620 rows, one per respondent x pair x applicant, both
##samples) and municipal_survey.rds (resident covariates and weight, joined on person_id).
##Read as text: ReadMe, manuscript.R. Design and wording: SI Appendix S1.2 and S1.4
##(Figs. S9-S10, pp. 16-18; PMC9907127 supplementary file pnas.2213986119.sapp.pdf).
##Usage: Rscript peyton_2022.R <raw dir> <output dir>
##
##TWO TABLES, one per population (the authors fit and report the two samples separately,
##manuscript.R est_community / est_police, Fig. 4):
##  peyton_2022_police_recruit_residents: municipal (baseline) survey of Yonkers residents,
##    May 2021, Qualtrics, recruited by the Yale Community Vitality panel; 1,412 respondents
##    in the deposit (the paper says 1,413).
##  peyton_2022_police_recruit_officers: survey of sworn Yonkers PD officers, June 2021,
##    invitations to 600 officers' government e-mail, 250 completed (deposit 250).
##Each respondent saw 5 pairs ("Comparison k of 5", source `pair` -> task) of hypothetical
##police applicants ("Applicant 1/2", source `applicant` -> profile), 8 attributes.
##Outcomes (screen in SI Fig. S10):
##  choice: "If you had to choose between them, which of these two applicants would your
##    prefer to see recruited into the Yonkers PD?" (sic) Applicant 1 / Applicant 2; forced,
##    no opt-out (conjoint_chosen).
##  rating: "Please rate each applicant on a scale from 1 to 7, where 1 indicates they should
##    definitely not be recruited and 7 indicates they should definitely be recruited."
##    1 = Definitely Not Recruit .. 7 = Definitely Recruit (conjoint_rating), stored raw.
##Rows with neither outcome are omitted; tasks with a missing choice keep choice = NA on both
##profiles (the respondent skipped the choice but rated).
##Attribute levels are the authors' factor labels in conjoints_stacked.rds, which are shortened
##versions of the displayed text (Fig. S10 shows e.g. "Scored in top 10% of applicants" for
##exam "Top 10%", "Job benefits (i.e. medical/pension)" for "Job benefits", "Does not live in
##Yonkers" for "Does not live in city"); the full displayed wording of every level is not
##deposited, so the authors' labels are kept unchanged.
##Restriction (SI S1.4, manuscript.R constraint_list): applicants whose previous occupation is
##School teacher or Social worker always have a Bachelors or Graduate degree; otherwise levels
##uniform and independent. Attribute row order on the example screen differs from the listing
##order, but no source says how it was randomized and the order is not in the data.
##Resident covariates (municipal_survey.rds, authors' text labels): cov_gender (x_sex Female/
##Male), cov_age_group (x_age_cat), cov_education (x_edu, the authors' collapsed categories),
##cov_party_id (x_pid_3_t0 Democrat/Republican/Independent), cov_race (x_race), cov_birthplace,
##cov_income (x_income_cat), cov_employment (x_emp_long_t0), cov_survey_weight (`weights`,
##raking weights to ACS margins; the authors do not use them, SI S1.2). The police table has
##no covariates (none deposited). Qualtrics ResponseIds (person_id) are re-keyed to integers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "conjoints_stacked.rds")))
m <- as.data.table(readRDS(file.path(raw, "municipal_survey.rds")))
stopifnot(nrow(s) == 16620L, all(s$pair %in% sprintf("%d of 5", 1:5)))
s[, task := as.integer(sub(" of 5", "", pair))]
s[, profile := as.integer(sub("Applicant ", "", applicant))]
stopifnot(all(s$task %in% 1:5), all(s$profile %in% 1:2), s[, .N, .(person_id, task, profile)][, all(N == 1)])
s[, `:=`(choice = as.integer(conjoint_chosen), rating = as.integer(conjoint_rating))]
## choice is all-or-nothing within a task and exactly one chosen where answered
stopifnot(s[, .(n = sum(!is.na(choice)), k = sum(choice, na.rm = TRUE)), .(person_id, task)][, all(n %in% c(0, 2) & (n == 0 | k == 1))])
at <- c(sex = "sex_", age = "age_", race = "race_", education = "education_", residency = "residency_",
        exam = "exam_", motivation = "motivation_", occupation = "occupation_")
for (v in names(at)) s[, paste0("attr_", v) := as.character(get(at[[v]]))]
stopifnot(!anyNA(s[, paste0("attr_", names(at)), with = FALSE]))
stopifnot(s[attr_occupation %in% c("School teacher", "Social worker"), all(attr_education %in% c("Bachelors degree", "Graduate degree"))])
s <- s[!(is.na(choice) & is.na(rating))]
keep <- c("person_id", "task", "profile", "choice", "rating", paste0("attr_", names(at)))
build <- function(d, file) {
  d <- copy(d)
  ids <- sort(unique(d$person_id)); d[, id := match(person_id, ids)]
  d[, person_id := NULL]
  setcolorder(d, c("id", setdiff(names(d), "id")))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, file))
}
## residents
r <- s[sample == "Civilian sample", ..keep]
stopifnot(all(r$person_id %in% m$person_id), !anyDuplicated(m$person_id))
cv <- m[, .(person_id, cov_gender = tolower(x_sex), cov_age_group = x_age_cat, cov_education = as.character(x_edu),
            cov_party_id = x_pid_3_t0, cov_race = x_race, cov_birthplace = x_birthplace,
            cov_income = as.character(x_income_cat), cov_employment = x_emp_long_t0, cov_survey_weight = weights)]
stopifnot(all(cv$cov_gender %in% c("female", "male")))
r <- merge(r, cv, by = "person_id", all.x = TRUE)
build(r, "peyton_2022_police_recruit_residents.csv")
## officers
p <- s[sample == "Police sample", ..keep]
build(p, "peyton_2022_police_recruit_officers.csv")
