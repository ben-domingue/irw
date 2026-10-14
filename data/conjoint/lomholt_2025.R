##Teacher expectations factorial survey (Denmark) from
##Hejli Lomholt, R. (2025). RESEARCH DATA: Formation of teacher expectations: Evidence from a factorial
##survey experiment manipulating student information [Data set]. Mendeley Data, V2.
##https://doi.org/10.17632/mg9cw32z2c.2  (no article DOI in the deposit; "currently in review").
##Licence: CC BY 4.0 (Mendeley record licence, versions 1 and 2 hold the same files; V2 used).
##Files read: Formation_of_teacher_expectations_dataset.RData (one data.frame
##teacher_expectation_data_long, loaded into its own environment) and codebook.xlsx (value labels).
##The analysis scripts (V1/V2_Data_analysis.R) were read as text only.
##Usage: Rscript lomholt_2025.R <dir holding the .RData> <output dir>
##
##403 teachers (Danish schools; 301 completed the survey, 102 did not; 325 rated all 12 vignettes,
##78 fewer) each rated up to 12 text vignettes of a described student, 4,400 ratings in all, drawn
##from a fractional factorial of 384 vignettes in 32 blocks (a respondent sees one block of 12).
##Seven randomized attributes (levels as in the codebook value labels):
##  ethnicity (Majority/Minority), gender (Male/Female), parental involvement (two sentences),
##  engagement (Disengaged/Engaged), subject (L1/Mathematics), instructional context
##  (Classroom discussion/Individual work/Group Work/Teacher presentation), mode of learning
##  engagement (Affective/Behavioural/Cognitive).
##Attribute level text is the codebook's value-label text; the deposit does not hold the vignette
##wording shown to respondents and no article is available, so the levels are the codebook labels,
##not the displayed text (LABELS: codebook labels only). "L1" is the codebook's label for the subject
##(taken to be the first language, Danish; not stated).
##Outcomes on every vignette:
##  rating: "How likely do you think it is that [name] will be in the top 25% academically at the end
##    of the school year?" 1 = Very unlikely ... 6 = Very likely (stored 1-6).
##  rating_others_agree: "To what extent do you think other teachers would agree or disagree to your
##    response?" Codebook: 1 = Completely disagree ... 4 = Completely agree, but the data hold codes
##    1-5 (5 = 133 rows); stored raw, the meaning of 5 is not documented.
##No opt-out; one rating per vignette. No task or profile column: task = row order within respondent
##(the file lists each respondent's vignettes together; whether row order is presentation order is not
##documented, so task_source is INFERRED); profile = 1 (single-profile ratings).
##Randomization: fractional factorial of 384 vignettes (2^5 x 4 x 3); restrictions between attributes
##are not documented. 383 distinct vignettes occur in the data. Attribute order and survey weight not
##documented (the authors' imputation weights are not in the data).
##Covariates: cov_gender (female: 0 Male, 1 Female, codebook), cov_age (years), cov_completed_survey
##(status: 1 = completed the entire survey, 0 = incomplete, codebook), cov_duration_min (minutes,
##codebook says minutes), cov_teaching_years (overall teaching experience, years), cov_years_at_school,
##cov_country_of_birth (Denmark/Other), cov_home_language (Danish/Other), cov_school_size,
##school aggregates cov_school_wellbeing / cov_school_absenteeism / cov_school_skill_coverage / cov_school_gpa (school mean GPA, codebook). Dropped: municipality and school identifiers (anonymised codes), respondentID
##(re-keyed to integers), the authors' derived/imputed columns (none present).
##Incomplete respondents' ratings are kept (they rated what they saw); rows with no rating: none.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "Formation_of_teacher_expectations_dataset.RData"), envir = e)
s <- as.data.table(e$teacher_expectation_data_long)
stopifnot(nrow(s) == 4400, uniqueN(s$respondentID) == 403, !anyNA(s$response1), !anyNA(s$response2))
s[, id := as.integer(factor(respondentID, levels = unique(respondentID)))]
s[, task := seq_len(.N), by = id]
L <- function(x, lab) unname(lab[as.character(x)])
par_lab <- c("1" = "Parents show little interest in school performance and behaviour; do not help with schoolwork.",
             "2" = "Parents show great interest in school performance and behaviour; help with schoolwork.")
d <- s[, .(id, task, profile = 1L,
           rating = as.integer(as.character(response1)), rating_others_agree = as.integer(as.character(response2)),
           attr_ethnicity = L(Vethnicity, c("1" = "Majority", "2" = "Minority")),
           attr_gender = L(Vgender, c("1" = "Male", "2" = "Female")),
           attr_parental_involvement = L(Vparents, par_lab),
           attr_engagement = L(Vengagement, c("1" = "Disengaged", "2" = "Engaged")),
           attr_subject = L(Vsubject, c("1" = "L1", "2" = "Mathematics")),
           attr_instructional_context = L(Vactivity, c("1" = "Classroom discussion", "2" = "Individual work", "3" = "Group Work", "4" = "Teacher presentation")),
           attr_engagement_mode = L(Vtype, c("1" = "Affective", "2" = "Behavioural", "3" = "Cognitive")),
           trial_block = as.integer(as.character(block)), trial_vignette = as.integer(as.character(vignette)),
           cov_gender = L(female, c("0" = "male", "1" = "female")), cov_age = as.integer(age),
           cov_completed_survey = as.integer(as.character(status)), cov_duration_min = responsetime,
           cov_teaching_years = teacherexp, cov_years_at_school = schoolexp,
           cov_country_of_birth = L(bcntry, c("0" = "Denmark", "1" = "Other")),
           cov_home_language = L(homelang, c("0" = "Danish", "1" = "Other")),
           cov_school_size = schoolsize, cov_school_gpa = school_GPA, cov_school_wellbeing = school_wellbeing,
           cov_school_absenteeism = school_absenteeism, cov_school_skill_coverage = school_teacher_skill_coverage)]
stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lomholt_2025_teacher_expectations.csv"))
