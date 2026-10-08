##Candidate conjoint with varying profile length (US partisans) from
##Peterson, E. (2017). The role of the information environment in partisan voting. Journal of
##Politics, 79(4), 1191-1204. https://doi.org/10.1086/692740
##Replication data: Harvard Dataverse doi:10.7910/DVN/VOF11U, CC0 1.0, no restricted files, no
##terms. File read: estimation.data.conjoint.RData (one data.frame, loaded into its own
##environment; one row per candidate profile). conjoint_analysis.R and "Replication
##Materials.txt" read as text only. No questionnaire ships and the article is paywalled (not
##read), so sample provider, date and question wording are not documented here.
##Usage: Rscript peterson_2017.R <dir holding the .RData> <output dir>
##
##1,059 US respondents, all Democrats or Republicans (party.id), 3 tasks (choice.task.number,
##RECORDED) x 2 candidates (candidate.order, RECORDED). Each task showed the candidates' party
##plus 1, 3, 5, 7 or 9 of nine further attributes (trial_information_condition = how many; it
##varies across a respondent's tasks); an attribute not shown is the text "(not shown)" (source
##"NOT.SEEN").
##attr_party is NOT in the file: it is rebuilt from the authors' copartisan flag and the
##respondent's party (copartisan = 1 -> the respondent's party, 0 -> the other one), stored as
##"Democrat"/"Republican"; the exact party wording on screen is not documented (the same
##author's 2016 conjoint, mummolo_2021, displayed "Democrat"/"Republican").
##Other attributes, level text as stored (factor labels): gender, profession, age (28-74),
##family status, race, military service, education, abortion stance, spending stance.
##Levels are NOT uniform (e.g. Male 67% of shown genders, Lawyer 30% of professions, White 49%
##of races, "No military service" 75%), presumably deliberate weights; not documented.
##choice = chosen.candidate (1 = chosen), forced choice; the question wording is not in the
##deposit.
##Dropped: 69 tasks with no choice recorded (chosen.candidate NA), which include all 54 tasks
##with no attribute information and no information condition (all NOT.SEEN, condition NA;
##levels not saved). Left: 3,108 tasks, 1,037 respondents (22 lose all three tasks). The authors' derived variables (copartisan,
##attribute-seen dummies, issue proximity, candidate.profile type) and choice.time are dropped;
##Qualtrics ResponseIds re-keyed.
##Covariates: cov_party_id (the respondent's party, party.id: Democrat/Republican as stored; party
##identification is how the sample was defined), cov_abortion_opinion and cov_spending_opinion (the
##respondent's own positions on the two issue attributes, answer text; blank = no answer).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "estimation.data.conjoint.RData"), envir = e)
s <- as.data.table(e$estimation.data.conjoint)
stopifnot(nrow(s) == 6354, s[, .N, participant.id][, all(N == 6)], !anyDuplicated(s[, .(participant.id, choice.task.number, candidate.order)]))
s[, id := match(as.character(participant.id), sort(unique(as.character(participant.id))))]
s[, drop := any(is.na(information.condition)) | anyNA(chosen.candidate), .(id, choice.task.number)]
stopifnot(s[is.na(information.condition), .N] == 108)
s <- s[drop == FALSE]
other <- c(Democrat = "Republican", Republican = "Democrat")
s[, attr_party := fifelse(copartisan == 1, party.id, other[party.id])]
ns <- function(x) { x <- as.character(x); x[x == "NOT.SEEN"] <- "(not shown)"; x }
d <- s[, .(id, task = as.integer(choice.task.number), profile = as.integer(candidate.order), choice = as.integer(chosen.candidate),
           attr_party, attr_gender = ns(gender.candidate), attr_profession = ns(profession.candidate), attr_age = ns(age.candidate),
           attr_family_status = ns(family.status.candidate), attr_race = ns(race.candidate),
           attr_military_service = ns(military.service.candidate), attr_education = ns(education.candidate),
           attr_abortion = ns(abortion.stance.candidate), attr_spending = ns(spending.stance.candidate),
           trial_information_condition = as.integer(information.condition),
           cov_party_id = party.id, cov_abortion_opinion = abortion.opinion, cov_spending_opinion = spending.opinion)]
a9 <- grep("^attr_", names(d), value = TRUE)[-1]
stopifnot(d[, rowSums(.SD != "(not shown)") == trial_information_condition, .SDcols = a9],
          !d[, any(.SD == "" | is.na(.SD)), .SDcols = c("attr_party", a9)],
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "peterson_2017_information_environment.csv"))
