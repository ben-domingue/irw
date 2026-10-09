##Public-sector job-choice conjoint from
##Pedersen, M. J., Favero, N., & Park, J. (2023). Pay-for-performance, job attraction, and the
##prospects of bureaucratic representation in public organizations: Evidence from a conjoint
##experiment. Public Management Review. https://doi.org/10.1080/14719037.2023.2245841
##Replication data: Harvard Dataverse doi:10.7910/DVN/NSHT68, CC0 1.0, no restricted files.
##Files read: PFP.Anonymized.rda (the authors' anonymized Qualtrics export, loaded into a new
##environment). Design, wording and level text from "PFP v4.0_strong.php" (the profile
##generator, read as text), Survey_Details.pdf (Prolific settings + Qualtrics questionnaire)
##and P4P_anonymize_data.R (read as text).
##Usage: Rscript pedersen_2023.R <raw dir> <output dir>
##
##1,501 US Prolific respondents (May 2021) who finished the survey, recruited as two Prolific
##studies with identical settings except the ethnicity prescreen (White / Nonwhite); the
##authors pool them, so one table with cov_sample ("White" / "Non-White", the authors'
##Study.ID). Respondents read a real-life job posting for a city "Community Activity Worker"
##(Project HOPE) and then made 3 choices between two versions of the job, Job A (profile 1)
##and Job B (profile 2), each described by 8 attributes in a fixed-order grid. The generator
##draws every level uniformly and independently ($weighted = 0, empty $restrictionarray), the
##same attribute order for every respondent. Level text is the generator's text with the
##<strong> bold tags removed (e.g. "Slightly above average").
##Outcomes:
##  choice = ScenarioNChoice, "Which of the two jobs would you personally prefer?" Job A / Job
##           B, forced, no opt-out.
##  rating = ScenarioNJob12_1/_2, "To what extent do jobs A and B reflect your ideal job
##           arrangement?" 1 = Definitely not ideal .. 7 = Definitely ideal (the export holds
##           the end-anchor text for 1 and 7; mapped to 1 and 7 here).
##Covariates (export answer text, checked against the questionnaire in Survey_Details.pdf):
##cov_age (years, typed), cov_gender ("What is your gender?" Male/Female/Non-binary/Prefer
##not to answer -> male/female/other/NA), cov_education ("What is your highest degree or
##level of school you have completed?"), cov_party_id ("What is your preferred political
##party?" Republican/Democratic/Other), cov_employment, cov_income ("Prefer not to answer"
##-> NA), cov_race (select-all answer text, comma-joined as exported), cov_state,
##cov_public_sector (PublicSector, asked only if not employed and not a student),
##cov_attention_pass (PSM_6, "This is an attention check; please click 'Disagree'": 1 if
##Disagree; 7 failed, per the authors' anonymize script), cov_honesty (Honesty, answer text;
##the question wording is not in the PDF extract), cov_duration_sec (whole survey).
##Dropped: Qualtrics ResponseId (IDs re-keyed to the authors' row ID), Prolific STUDY_ID,
##dates, page timers, the free-text fields Sector1_7_TEXT, Sector2_7_TEXT and Party_3_TEXT,
##sector questions, risk / self-efficacy / PSM items (non-conjoint scales), consent.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "PFP.Anonymized.rda"), envir = e)
r <- as.data.table(e$PFP.Anonymized)
stopifnot(!anyDuplicated(r$ID), nrow(r) == 1501)
strip <- function(x) gsub("<[^>]+>", "", x)
rate <- function(x) { x <- gsub("\\s+", " ", x)
  y <- ifelse(x == "Definitely not ideal 1", "1", ifelse(x == "Definitely ideal 7", "7", x))
  y <- ifelse(grepl("^Definitely not ideal", x), "1", ifelse(grepl("^Definitely ideal", x), "7", y))
  y <- as.integer(y); stopifnot(all(is.na(x) == is.na(y)), all(y %in% c(1:7, NA))); y }
an <- c("total_pay", "performance_bonuses", "performance_evaluation", "community_involvement",
        "community_income", "community_demographics", "overtime_work", "key_job_task")
d <- rbindlist(lapply(1:3, function(t) rbindlist(lapply(1:2, function(p) {
  ch <- match(r[[sprintf("Scenario%dChoice", t)]], c("Job A", "Job B"))
  x <- data.table(id = as.integer(as.character(r$ID)), task = t, profile = p, choice = as.integer(ch == p),
                  rating = rate(r[[sprintf("Scenario%dJob12_%d", t, p)]]))
  for (j in 1:8) x[, paste0("attr_", an[j]) := strip(r[[sprintf("F.%d.%d.%d", t, p, j)]])]
  x }))))
stopifnot(!anyNA(d$choice), d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, !anyNA(.SD), .SDcols = patterns("^attr_")])
stopifnot(all(sapply(1:3, function(t) all(r[[sprintf("F.%d.1", t)]] == "Total pay: Expected pay (including bonuses), compared to similar jobs elsewhere"))))
na_if <- function(x, v) { x[x %in% v] <- NA; x }
stopifnot(all(r$Gender %in% c("Male", "Female", "Non-binary", "Prefer not to answer")))
cv <- data.table(id = as.integer(as.character(r$ID)), cov_sample = r$Study.ID, cov_age = as.integer(r$Age),
  cov_gender = c(Male = "male", Female = "female", "Non-binary" = "other")[r$Gender],
  cov_education = r$Education, cov_party_id = r$Party, cov_employment = r$Employment,
  cov_income = na_if(r$Income, "Prefer not to answer"), cov_race = r$Race, cov_state = r$State,
  cov_public_sector = r$PublicSector, cov_attention_pass = as.integer(r$PSM_6 == "Disagree"),
  cov_honesty = r$Honesty, cov_duration_sec = as.integer(r$Duration..in.seconds.))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pedersen_2023_pay_for_performance.csv"))
