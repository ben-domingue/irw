##Resume experiment: institution type x advanced technical coursework (employer evaluations), from the deposit
##"Liberal Arts Plus STEM: Employer Evaluations of Resumes" (replication materials for "Liberal Arts Plus STEM: Experimental Evidence on Employer Evaluations of
##Technical Coursework", Syed & Murdie; no article DOI located 2026-11-10) (Harvard Dataverse doi:10.7910/DVN/6ZUJOR, CC0 1.0; fielded 2026).
##Files read: 01_raw_qualtrics_export.tab (Qualtrics export, 2 header rows: names, question text; 1,269 response rows), 00_run_all.R (read as text: the condition coding,
##outcome recoding and the authors' exclusion rules); 03_analysis_ready.tab (the authors' 1,200-row final sample) was used only to check the exclusion flag below.
##Usage: Rscript syed_2026.R <dir holding 01_raw_qualtrics_export.tab and 03_analysis_ready.tab> <output dir>
##
##Factorial vignette experiment (presentation = text), one resume per respondent (employers / hiring-experienced online respondents), 2 x 2 between-subject (Qualtrics
##randomizer FL_29_DO, conditions CandidateProfile-Condition1-4): educational profile ("State university/BA" vs "Technology-focused university/BS": condition 3 and 4) x advanced technical
##coursework (No vs Yes: conditions 2 and 4). Level text = the authors' own labels in 00_run_all.R (profile_label, course_label); the displayed resume wording is not in the export
##(the education and coursework lines are absent from the question-text rows): "LABELS: authors' labels, paraphrase". The candidate (Jordan Lee, entry-level analyst) and all
##other resume content are constant. One row per respondent: id = row number; task = profile = 1 (inferred).
##Outcomes (all about the one resume): choice = "Would you move this candidate forward to an interview?" (QID65: 1 = Yes -> 1, 2 = No -> 0; code 3, 75 respondents, has no
##documented label and is set NA; the authors count it as not "yes"); this is a single-profile accept/reject, so opt_out = yes. rating_interview_likelihood = "How likely are you to
##recommend interviewing this candidate?" 0 = Extremely unlikely .. 100 = Extremely likely (QID64_6); rating_technical_competence "This candidate has sufficient technical competence for this
##role.", rating_engineering_team_fit "This candidate would fit well on an engineering-heavy team.", rating_long_ramp_up "This candidate would require a long ramp-up period to be effective.",
##rating_communication "This candidate demonstrates strong communication ability." each 0 = Strongly disagree .. 7 = Strongly agree (QID66_1-QID69_1; the stored values run 0-7).
##Ruling (Ben, 2026-11-10): the authors' sample exclusions are NOT applied. The authors' final sample is 1,200 of 1,269 rows after dropping: missing interview-likelihood outcome, missing
##hiring-experience category (QID77), invalid or non-single randomized condition, a documented pilot/test window (2026-02-05 18:23:42 to 2026-04-06 05:52:26), three documented individual test
##responses and the first 48 production-order responses (test runs). Here every respondent with a valid single condition and at least one outcome is kept; the rule is stored as
##cov_authors_exclusion (the authors' reason text, NA = in the authors' sample); reproduce their sample with cov_authors_exclusion missing (checked: 1,200 rows, the same ResponseIds as
##03_analysis_ready.tab). Rows with Status = 1 (Qualtrics survey previews, i.e. the team's own previews, not respondents) and rows without a valid single condition
##(which cannot be assigned factor levels) are dropped: together 6 of the 1,269 rows, leaving 1,263 respondents (all with at least one outcome; 4 lack the interview rating).
##Covariates: cov_duration_sec (Duration, whole survey, seconds), cov_candidates_evaluated_code (QID77 "Approximately how many job candidates have you evaluated?", codes 1-4, labels not in
##the deposit), cov_hiring_capacity_code (QID75 "In what capacity have you participated in hiring decisions? (Select all that apply)", codes joined by comma, labels not in the deposit),
##cov_authors_exclusion. Dropped: ResponseId (platform response id, re-keyed), dates, reCAPTCHA scores, distribution channel, consent text. No weights. PII FOUND: none (the export carries no
##IP, location or contact fields; ResponseId dropped).
##Respondent count vs paper: 1,200 authors' sample reproduced exactly; table holds more (all respondents with an outcome).
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "01_raw_qualtrics_export.tab"), quote = "\"", fill = TRUE)
x <- d[grepl("^\\d{4}-\\d{2}-\\d{2}", StartDate)]
stopifnot(nrow(x) == 1269)
x[, start := as.POSIXct(StartDate, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")]
x[, `:=`(interview = suppressWarnings(as.numeric(QID64_6)), cand = suppressWarnings(as.numeric(QID77)))]
vc <- paste0("CandidateProfile-Condition", 1:4)
x[, why := NA_character_]
x[is.na(interview), why := "Missing primary interview-likelihood outcome"]
x[is.na(why) & is.na(cand), why := "Missing hiring-experience category"]
x[is.na(why) & !(FL_29_DO %in% vc), why := "Invalid or non-single randomized condition"]
x[is.na(why) & start >= as.POSIXct("2026-02-05 18:23:42", tz = "UTC") & start <= as.POSIXct("2026-04-06 05:52:26", tz = "UTC"), why := "Documented pilot/test response window"]
x[is.na(why) & start %in% as.POSIXct(c("2026-04-08 13:35:16", "2026-04-09 07:34:31", "2026-04-09 07:53:43"), tz = "UTC"), why := "Documented individual test response"]
ei <- which(is.na(x$why)); ei <- ei[order(x$start[ei], x$ResponseId[ei])]
x[ei[seq_len(min(48, length(ei)))], why := "First 48 production-order responses were test run"]
ar <- fread(file.path(raw, "03_analysis_ready.tab"), quote = "\"")
stopifnot(sum(is.na(x$why)) == 1200, setequal(x[is.na(why), ResponseId], ar$ResponseId))
x <- x[Status == "0" & FL_29_DO %in% vc]
x[, cond := as.integer(sub(".*Condition([1-4]).*", "\\1", FL_29_DO))]
num <- function(v) suppressWarnings(as.numeric(v))
x[, `:=`(rating_interview_likelihood = num(QID64_6), rating_technical_competence = num(QID66_1), rating_engineering_team_fit = num(QID67_1),
         rating_long_ramp_up = num(QID68_1), rating_communication = num(QID69_1),
         choice = fcase(QID65 == "1", 1L, QID65 == "2", 0L, default = NA_integer_))]
oc <- c("choice", grep("^rating_", names(x), value = TRUE))
x <- x[rowSums(!is.na(x[, ..oc])) > 0]
x[, `:=`(id = .I, task = 1L, profile = 1L,
         attr_educational_profile = c("State university/BA", "State university/BA", "Technology-focused university/BS", "Technology-focused university/BS")[cond],
         attr_advanced_technical_coursework = c("No", "Yes", "No", "Yes")[cond],
         cov_duration_sec = as.integer(round(num(`Duration (in seconds)`))),
         cov_candidates_evaluated_code = as.integer(num(QID77)), cov_hiring_capacity_code = fifelse(QID75 == "", NA_character_, QID75),
         cov_authors_exclusion = why)]
x <- x[, c("id", "task", "profile", "choice", grep("^rating_", names(x), value = TRUE), "attr_educational_profile", "attr_advanced_technical_coursework",
           "cov_duration_sec", "cov_candidates_evaluated_code", "cov_hiring_capacity_code", "cov_authors_exclusion"), with = FALSE]
setorder(x, id, task, profile)
fwrite(x, file.path(out, "syed_2026_resume_coursework.csv"))
cat(nrow(x), "kept; authors' sample", x[, sum(is.na(cov_authors_exclusion))], "; choice NA", x[, sum(is.na(choice))], "\n")
