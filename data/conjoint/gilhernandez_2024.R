##Factorial vignette on teacher bias in assessments (Spanish pre-service teachers) from
##Gil-Hernández, C. J., Pañeda-Fernández, I., Salazar, L., & Castaño Muñoz, J. (2024). Teacher bias in
##assessments by student ascribed status: A factorial experiment on discrimination in education.
##Sociological Science, 11, 743-776. https://doi.org/10.15195/v11.a27
##Replication data: Zenodo record 12666535 (doi 10.5281/zenodo.12666535), "carjgil/teacher-bias:
##Teacher Bias - Replication Package", licence CC BY 4.0 (record); the same data are in the JRC data
##catalogue (f14f5209-f032-4218-a89a-4643143809af), also CC BY 4.0. Files read (from the zip):
##data/STATA/cleandataset.dta (value labels), data/Codebook_cleandataset.xlsx, code/datacleaning.do
##(as text). Design and wording: the article and its online supplement (read as PDF text).
##Usage: Rscript gilhernandez_2024.R <dir holding cleandataset.dta> <output dir>
##
##1,717 pre-service elementary teachers (students of education degrees at 20 sampled Spanish
##universities/faculties, 2023; article n = 1,717, matches). Full factorial of 7 binary factors
##(128 vignettes), ONE vignette per respondent (between-subject): task = 1, profile = 1.
##Respondents saw a student file (table) and the student's essay (text). Attributes:
##  attr_student_name: name shown in the file and essay instructions; carries gender and
##    origin (Daniel García González / Lucía García González = Spanish origin; Youssef Salhi /
##    Salma Salhi = Moroccan origin; .dta value labels).
##  attr_father_email: the fictional father's email shown in the file (stimulus text, not PII), carrying SES (Notarios-<surname>.es =
##    notary, Pintores-Express.es = construction painter) and origin; .dta value labels.
##  attr_subjects_failed: "All subjects passed" / "Three core subjects not passed" (article's
##    English description; the Spanish file text is not deposited).
##  attr_behaviour: "High effort, regularly does homework and behaves well in class" / "Low effort,
##    rarely does homework and misbehaves in class" (article's English description).
##  attr_essay_quality: "Good essay" / "Bad essay" (two real 6th-grade essays; authors' labels).
##  attr_essay_cultural_capital: the Spanish sentence embedded in the essay, from the value labels
##    of the cultural-capital manipulation check q8b_i: highbrow "En todas las estaciones los
##    colores me recuerdan a los cuadros impresionistas de Monet que vi en el museo con mi
##    familia." / lowbrow "..., casi como el que pasan en La isla de las tentaciones, que veo en
##    casa en la televisión." (leading punctuation/brackets stripped).
##  (The essay also embeds the father's occupation; that is the same SES factor as the email.)
##Full factorial; "non-realistic combinations ... are not excluded" (article). Recorded as restrictions yes:
##student name and father's email both carry the ethnicity factor, so the surnames always match.
##Outcomes (sliders with decimals; stored raw, rounded to 4 decimals to remove Stata float noise):
##  rating: essay grade 1-10, "What grade from 1 to 10 (including decimal points) would you give to
##    the essay considering its syntactic structure, orthography, vocabulary, and creativity?"
##  rating_retention: 0-10, "... do you think this student should repeat 6th grade?" 0 = should never
##    repeat, 10 = should definitely repeat (HIGHER = more retention, i.e. less favourable).
##  rating_expectations: 0-10, likely to reach the upper-secondary academic track, 0 = not at all
##    likely, 10 = very likely.
##  rating_parental_support: 0-10, respondent's perception of the student's parental support
##    (supplement: Screen 4; wording and anchors not given; paraphrase).
##(English wording is the article's translation of the Spanish questionnaire.)
##Covariates (Spanish value labels as stored): cov_gender (q9_i Hombre male, Mujer female),
##cov_birth_year (q10_1), cov_degree_year (q11b_1_i), cov_repeated_grade (q12_i), cov_parent_education
##(q13_i), cov_birth_country (q14_i), cov_parent_born_abroad (q15_i), cov_rank_ability/ses/effort/luck
##(q16_1-4, 1 = most important), cov_university (anonymized faculty id), cov_private (public = 0),
##cov_device_phone, cov_duration_sec, manipulation-check answers cov_check_gender/origin/ses/failed/
##behaviour/cultural_capital (q4_i-q8b_i, Spanish answer text; q8b sentences as above).
##Dropped: Qualtrics responseid (re-keyed), dates, screen timings, authors' derived signals/recodes.
##No survey weight in the deposit (the article's Table A.7 weighted models use weights not in
##cleandataset). PII: none found (respondent emails were used for de-duplication in the do-file but
##are not in the deposited files).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "cleandataset.dta"))
L <- function(v) as.character(as_factor(s[[v]], levels = "labels"))
stopifnot(nrow(s) == 1717L, uniqueN(s$responseid) == 1717L)
cc <- L("q8b_i")
hi <- trimws(gsub("^\\[\\.\\s*|\\]$", "", unique(cc[grepl("Monet", cc)])))
lo <- trimws(gsub("^\\[,\\s*|\\]$", "", unique(cc[grepl("tentaciones", cc)])))
lo <- paste0("...", lo)
stopifnot(length(hi) == 1, length(lo) == 1)
d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L,
                rating = round(as.numeric(s$grade_essay), 4), rating_retention = round(as.numeric(s$repit), 4),
                rating_expectations = round(as.numeric(s$expect), 4), rating_parental_support = round(as.numeric(s$psupport), 4),
                attr_student_name = L("student_name"), attr_father_email = L("father_mail"),
                attr_subjects_failed = fifelse(s$allpassed == 1, "All subjects passed", "Three core subjects not passed"),
                attr_behaviour = fifelse(s$behaviour_good == 1, "High effort, regularly does homework and behaves well in class",
                                         "Low effort, rarely does homework and misbehaves in class"),
                attr_essay_quality = fifelse(s$essay_good == 1, "Good essay", "Bad essay"),
                attr_essay_cultural_capital = fifelse(s$essay_cc_high == 1, hi, lo),
                cov_gender = c(Hombre = "male", Mujer = "female")[L("q9_i")], cov_birth_year = as.integer(s$q10_1),
                cov_degree_year = L("q11b_1_i"), cov_repeated_grade = L("q12_i"), cov_parent_education = L("q13_i"),
                cov_birth_country = L("q14_i"), cov_parent_born_abroad = L("q15_i"),
                cov_rank_ability = as.integer(s$q16_1), cov_rank_ses = as.integer(s$q16_2), cov_rank_effort = as.integer(s$q16_3),
                cov_rank_luck = as.integer(s$q16_4), cov_university = as.integer(s$q11a_1_i), cov_private = as.integer(s$public),
                cov_device_phone = as.integer(s$device_phone), cov_duration_sec = as.integer(s$durationinseconds),
                cov_check_gender = L("q4_i"), cov_check_origin = L("q5_i"), cov_check_ses = L("q6_i"), cov_check_failed = L("q7_i"),
                cov_check_behaviour = L("q8_i"), cov_check_cultural_capital = gsub("^\\[[.,]\\s*|\\]$", "", L("q8b_i")))
# factor codes agree with the displayed name / email
stopifnot(all((d$attr_student_name %in% c("Lucía García González", "Salma Salhi")) == (s$sex_female == 1)),
          all(grepl("García", d$attr_student_name) == (s$spanish == 1)), all(grepl("Notarios", d$attr_father_email) == (s$ses_high == 1)),
          all(grepl("David", d$attr_father_email) == (s$spanish == 1)), !anyNA(d$cov_gender),
          all(d$rating >= 1 & d$rating <= 10), all(d$rating_retention >= 0 & d$rating_retention <= 10))
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gilhernandez_2024_teacher_bias.csv"))
