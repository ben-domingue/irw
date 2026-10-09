##E-government chatbot design conjoint (Germany, 2023), citizens and municipal front desk officers, from
##Hemesath, S., & Tepe, M. (2024). Public value positions and design preferences toward AI-based chatbots
##in e-government. Evidence from a conjoint experiment with citizens and municipal front desk officers.
##Government Information Quarterly, 41(4), 101985. https://doi.org/10.1016/j.giq.2024.101985
##Replication data: Harvard Dataverse doi:10.7910/DVN/JJYIUD, CC0 1.0. Files read: Citizen_Sample.RDS,
##Municipalities_Sample.RDS. Script.R read as text, not run (attribute names/English level names, the
##authors' gender and education labels, sample sizes). Contacts.RDS (municipal contact list) not
##downloaded. The article (Elsevier, CC BY) could not be fetched here, so no question wording was seen.
##Usage: Rscript hemesath_2024.R <dir holding the two .RDS> <output dir>
##
##Two tables, one per population (the authors analyse them side by side and compare them):
##  hemesath_2024_chatbot_citizens  citizens, February 2023 (StartDate), 1,690 respondents (Script.R map
##                                  legend "Citizens (n=1690)").
##  hemesath_2024_chatbot_officers  municipal front desk officers (Bürgeramt staff), March 2023, 267
##                                  respondents (Script.R "Municipalities (n=267)").
##6 tasks x 2 chatbot profiles, 8 attributes, levels stored in the German shown in the data (the
##authors' factor levels; respondents saw German, UserLanguage DE). task/profile are recorded columns.
##Outcome:
##  choice = selected (CJ_task<t> = 1/2): which of the two chatbots the respondent prefers. Forced choice,
##           exactly one per task (checked). Wording not seen: paraphrase.
##Not kept: CJ_task<t>a_1, a task-level -5..+5 scale; in the data -5 goes with choosing chatbot 1 and +5
##with chatbot 2 (selected_num = its rescaling to the profile). Its wording and anchors are undocumented
##and it is a relative scale, not a rating of one profile, so it is dropped.
##Attributes (Script.R English names in brackets): attr_developer [Development], attr_chat_history
##[Privacy], attr_chat_termination [Takeover], attr_chatbot_decides [ADM], attr_workload_reduction
##[Workload, "Reduction workload (municipality)"], attr_time_saving [Time, "Time saving (citizens)"],
##attr_communication_type [Interface], attr_communication_tone [Style]. Workload levels are stored as in
##the data ("14 %", "27%", "4%"). Randomization restrictions and attribute order are not documented.
##Citizens: trial_prime = Prime (Control / Duty / Service), a between-respondent priming module shown
##before the conjoint (the prime_* questions themselves are dropped). Covariates: cov_age (years as
##recorded; 48 respondents report 99, kept), cov_gender (1 Female, 2 Male, 3 Non-Binary = other; the
##authors' labels in Script.R balancing plot), cov_education (1-6 = Without Degree, Student, Hauptschule
##(Lower Secondary Degree), Realschule (Intermediate Degree), (Fach-)Abitur (High School Degree),
##(Applied) University Degree; the authors' English labels in Script.R), cov_area_code, cov_state_code,
##cov_leftright_code, cov_vote_code, cov_tech_regulation_<k>_code, cov_psm_<k>_code (unlabelled codes),
##cov_gaais<k> (General Attitudes towards AI items as stored), cov_duration_sec (whole survey).
##Officers: cov_age, cov_gender_code and cov_education_code (the authors' Script.R relabels the officers'
##education levels in a different order from the citizens', and labels no officer gender, so the codes are
##kept), cov_state (Bundesland of the municipality, text), cov_duration_sec. The municipality's type, mayor
##gender and party, area, population and density are dropped (with Bundesland they identify the
##municipality, and so the officer); Q161-Q175 (unlabelled) dropped.
##Dropped from both: ResponseId/respondent (Qualtrics IDs; ids re-keyed to integers), LocationLatitude/
##LocationLongitude, dates, browser metadata, free text (prime_*_open, prime_manipulation_*, lastvisit,
##employer/oed_org _TEXT, feedback), straightlining flags, selected_num, consent.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ats <- c(Development = "developer", Privacy = "chat_history", Takeover = "chat_termination", ADM = "chatbot_decides",
         Workload = "workload_reduction", Time = "time_saving", Interface = "communication_type", Style = "communication_tone")
core <- function(x) {
  x <- as.data.table(x)
  stopifnot(!anyNA(x$selected), x[, .N, .(ResponseId, task)][, all(N == 2)], x[, sum(selected), .(ResponseId, task)][, all(V1 == 1)])
  x[, cj := as.integer(get(paste0("CJ_task", task[1]))), by = task]
  stopifnot(x[, all((cj == profile) == (selected == 1))])
  ids <- unique(x$ResponseId)
  d <- x[, .(id = match(ResponseId, ids), task, profile, choice = as.integer(selected))]
  for (v in names(ats)) { stopifnot(!anyNA(x[[v]])); d[, paste0("attr_", ats[[v]]) := as.character(x[[v]])] }
  list(x = x, d = d)
}
num <- function(v) { v <- trimws(as.character(v)); v[v == ""] <- NA; as.integer(v) }
## citizens
r <- core(readRDS(file.path(raw, "Citizen_Sample.RDS"))); x <- r$x; d <- r$d
stopifnot(x$Prime %in% c("Control", "Duty", "Service"), num(x$gender) %in% 1:3, num(x$education) %in% 1:6)
d[, trial_prime := x$Prime]
d[, cov_age := num(x$age)]
d[, cov_gender := c("female", "male", "other")[num(x$gender)]]
d[, cov_education := c("Without Degree", "Student", "Hauptschule (Lower Secondary Degree)", "Realschule (Intermediate Degree)",
                       "(Fach-)Abitur (High School Degree)", "(Applied) University Degree")[num(x$education)]]
d[, `:=`(cov_area_code = num(x$area), cov_state_code = num(x$state), cov_leftright_code = num(x$leftright_1), cov_vote_code = num(x$vote))]
for (k in 1:5) d[, paste0("cov_tech_regulation_", k, "_code") := num(x[[paste0("tech_regulation_", k)]])]
for (k in 1:5) d[, paste0("cov_psm_", k, "_code") := num(x[[paste0("PSM_", k)]])]
for (k in 1:20) d[, paste0("cov_gaais", k) := as.numeric(x[[paste0("gaais", k)]])]
d[, cov_duration_sec := num(x$Duration..in.seconds.)]
setorder(d, id, task, profile)
stopifnot(uniqueN(d$id) == 1690)
fwrite(d, file.path(out, "hemesath_2024_chatbot_citizens.csv"))
## front desk officers
r <- core(readRDS(file.path(raw, "Municipalities_Sample.RDS"))); x <- r$x; d <- r$d
d[, `:=`(cov_age = num(x$age), cov_gender_code = num(x$gender), cov_education_code = num(x$education),
         cov_state = x$Bundesland, cov_duration_sec = num(x$Duration..in.seconds.))]
setorder(d, id, task, profile)
stopifnot(uniqueN(d$id) == 267)
fwrite(d, file.path(out, "hemesath_2024_chatbot_officers.csv"))
