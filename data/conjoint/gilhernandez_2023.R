##Teacher assessment-bias factorial survey (DIGCLASS-BIAS) from
##Gil Hernandez, C. J., Paneda-Fernandez, I., Salazar, L., & Castano Munoz, J. (2023). A factorial survey
##experiment on teacher's bias in assessments (JRC135784). European Commission, Joint Research Centre.
##Data: JRC Data Catalogue doi:10.2905/JRC.RJDFN28 (record research-data.ec.europa.eu/records/n35rf-h7t17,
##DIGCLASS-BIAS.zip), CC BY 4.0, anonymous access. File read: data/CSV/cleandataset.csv (the authors' cleaned
##working file; Codebook_cleandataset.xlsx and code/datacleaning.txt read as text, not run).
##Usage: Rscript gilhernandez_2023.R <dir holding the unzipped DIGCLASS-BIAS folder> <output dir>
##  (the script reads <dir>/data/CSV/cleandataset.csv)
##
##1,717 Spanish pre-service teachers (Qualtrics, 2023). Each rated ONE vignette of a student (a student file
##plus an essay), drawn from the full 2^7 = 128 factorial; one task of one profile per respondent, id = row order
##(the file's only respondent ID is the Qualtrics ResponseId, dropped). Factors, as labelled in the codebook:
##  student_gender      sex_female          Boy / Girl (carried by the student's name)
##  ethnic_origin       spanish             Spanish-origin / Moroccan-origin (name and father's e-mail domain)
##  father_ses          ses_high            High-SES / Low-SES (father a notary or lawyer vs a construction painter or mechanic)
##  essay_quality       essay_good          Good / Bad essay
##  essay_cultural_cap  essay_cc_high       Highbrow / Lowbrow cultural-capital sentence in the essay
##  subjects_failed     allpassed           0 subjects failed / 3 core subjects failed
##  behaviour_effort    behaviour_good      Good / Bad behaviour and effort
##The codebook gives these level labels; the Spanish vignette wording is not in the deposit, so level text is the
##codebook's English labels, lightly expanded (paraphrased from the codebook, not verbatim display text).
##Outcomes (codebook labels; the exact questions are not in the deposit): rating = grade_essay, "Essay Grade", 1-10;
##rating_grade_retention = repit, "Grade Retention Recommendation", 0-10; rating_edu_expectations = expect,
##"Educational Expectations for Upper-Secondary Academic Track", 0-10; rating_parental_support = psupport,
##"Parental Support of Student's Education" (the authors' mechanism item), 0-10. All raw, no opt-out. The
##essay-grade-by-quality splits (grade_essay_good/bad) are derived and dropped.
##Dropped: Qualtrics ResponseId, timestamps/timing, the six manipulation checks and their right/wrong flags, the
##respondents' ranking of success factors, derived vignette id and name/e-mail/essay-type codes.
##Covariates: cov_gender from q9_i (1 Men = male, 2 Women = female, codebook), cov_birth_year q10_1,
##cov_age_group (codebook "Age Groups": 18-25, >=26), cov_ba_year_code (q11b_1_i, codes 1-5 = year of the degree,
##7 = graduated), cov_grade_retention (q12_i No/Yes), cov_parent_education (q13_i, ">=College"/"<College"),
##cov_born (q14_i Spain/Abroad), cov_parents_born (q15_i), cov_university_id_code (anonymised faculty id), cov_public (public=0/private=1 institution),
##cov_duration_sec. No survey weight. Randomization: balanced full factorial (cell sizes 4-24 per vignette, uneven
##because respondents were allocated at random to 128 cells); the authors' balance of factors is near 50/50.
##The authors' filters (finished, consent, teaching degree, adult, duplicate e-mails) are already applied in
##cleandataset.csv.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "data", "CSV", "cleandataset.csv"))
stopifnot(nrow(d) == 1717, uniqueN(d$responseid) == 1717)
d[, id := .I]
lab <- function(x, l0, l1) ifelse(x == 1, l1, l0)
r <- d[, .(id, task = 1L, profile = 1L, rating = as.integer(grade_essay),
  rating_grade_retention = as.integer(repit), rating_edu_expectations = as.integer(expect),
  rating_parental_support = as.integer(psupport),
  attr_student_gender = lab(sex_female, "Boy", "Girl"),
  attr_ethnic_origin = lab(spanish, "Moroccan-origin", "Spanish-origin"),
  attr_father_ses = lab(ses_high, "Low-SES", "High-SES"),
  attr_essay_quality = lab(essay_good, "Bad essay", "Good essay"),
  attr_essay_cultural_capital = lab(essay_cc_high, "Lowbrow", "Highbrow"),
  attr_subjects_failed = lab(allpassed, "3 core subjects failed", "0 subjects failed"),
  attr_behaviour_effort = lab(behaviour_good, "Bad behaviour and effort", "Good behaviour and effort"),
  cov_gender = c("male", "female")[q9_i], cov_birth_year = as.integer(q10_1),
  cov_age_group = c("18-25", ">=26")[age], cov_ba_year_code = as.integer(q11b_1_i),
  cov_grade_retention = c("No", "Yes")[q12_i], cov_parent_education = c(">=College", "<College")[q13_i],
  cov_born = c("Spain", "Abroad")[q14_i], cov_parents_born = c("Spain", "At least one parent abroad")[q15_i],
  cov_university_id_code = as.integer(q11a_1_i), cov_public = c("Public", "Private")[public + 1L],
  cov_duration_sec = as.integer(durationinseconds))]
stopifnot(!anyNA(r$rating), !anyNA(r[, grep("^attr_", names(r)), with = FALSE]))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "gilhernandez_2023_teacher_bias.csv"))
