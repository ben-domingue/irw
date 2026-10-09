##Factorial survey of apprenticeship applicants rated by German recruiters, from
##Forster, A. G., & Neugebauer, M. (2024). Factorial survey experiments to predict real-world
##behavior: A cautionary tale from hiring studies. Sociological Science, 11, 886-906.
##https://doi.org/10.15195/v11.a32 (CC BY 4.0 article; online supplement read for the design)
##Replication data: OSF https://osf.io/x2tcp/ (doi:10.17605/OSF.IO/X2TCP), CC BY 4.0. File read:
##replication_package_incl_data.zip -> 00_data/validation_fs.dta (the factorial survey). The
##zip's validation_fe.dta is the field experiment (one real application per employer, callback
##outcome; not a survey) and is not used. The authors' .do files were read as text, not run.
##Usage: Rscript forster_2024.R <dir holding validation_fs.dta> <output dir>
##
##480 recruiters at German firms that had earlier received one fictitious application in the
##authors' field experiment (spring and fall 2022 waves), surveyed online eight weeks later,
##each rating 8 fictitious apprenticeship applicants (3,840 vignettes; article p. 892).
##Each vignette was a one-screen mock-up of application materials in German: a short cover
##letter, a tabular CV with photo and parents' occupations, and an excerpt of a school-leaving
##certificate (supplement 1.2). One vignette = one task with one profile (profile = 1).
##task = vignette_nr, the position in the respondent's sequence (the authors' 04_robustness.do
##keeps vignette_nr == 1 as "the first vignette", supplement 4.1).
##Design: full factorial of 144 vignettes in 18 sets of 8 chosen by D-efficiency; each
##recruiter got one set at random (article p. 894): a FIXED BLOCKED DESIGN.
##Attributes (level text = the authors' categories in English, from the .dta value labels and
##article Table 1 / supplement Table S4; the displayed German materials are not deposited, so
##these are NOT the text respondents saw):
##  attr_gender       Female / Male: signalled by the applicant's first name (and photo).
##  attr_ethnicity    German / Turkish: signalled by the name ("e.g., Anna Wagner" / "Ayse Sahin").
##  attr_education    Intermediate high school degree / Upper secondary high school degree
##                    (Abitur) / Abitur + some college without degree (on CV and cover letter).
##  attr_study_field  Mathematics / German studies: only for the "some college" applicants (value
##                    labels mathematics / language; supplement 1.1 names the subjects as
##                    mathematics and German studies); "(not shown)" for the other two levels.
##  attr_ses          parents' occupations on the CV: Low (unskilled worker parents) /
##                    Intermediate (skilled worker parents) / High (graduate worker parents).
##  attr_achievement  grades on the certificate: Low (sufficient) / Intermediate
##                    (satisfactory) / High (good).
##Restriction: field of study exists only for the some-college level (checked below). Level
##weights follow from the full factorial: education is 1/4, 1/4, 1/2 (some college = two
##study fields); every other attribute is uniform. Names, photos, hobbies and internships
##varied at a constant level and are not in the deposit.
##Outcomes:
##  rating: after each vignette, how likely they were to invite the candidate to the next step
##     of the hiring process, 0 to 100 percent in steps of 10 (invperc; supplement 1.3).
##  choice: after all eight, the eight applicants were shown again on one page with their
##     ratings and the recruiter marked which to invite ("I would like to invite [name]
##     (yes/no)", article Fig. 1); invitation_dich, 1 = invite. Several or none of the eight
##     could be invited: a single-profile accept/reject, opt-out = yes. This is the paper's
##     dependent variable.
##Covariates: cov_wave (field-experiment wave, 1 spring / 2 fall 2022), cov_occupational_field
##(codes 1-4 = Electronics, Laboratory, Administration, Media: article Table 2 order, and its
##counts 512/560/1,944/824 match the codes), cov_recruiter_responsible (value-label text),
##cov_applicants_typical (value-label text; -998/-949 missing codes -> NA),
##cov_vignette_time_sec (time_use: average seconds per vignette, article Table 2).
##Dropped: the authors' standardized social-desirability and survey-attitude scales
##(socdesire_std, survatt_std; derived scores, item responses not deposited). ID is the
##authors' case number (not a platform ID), kept.
##N: 480 respondents x 8 vignettes = 3,840, as in the article. Spot check: the article reports
##an average invitation of 0.59 (Table 2); this table gives 2,278/3,840 = 0.593.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "validation_fs.dta"))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
d <- data.table(id = as.integer(s$ID), task = as.integer(s$vignette_nr), profile = 1L,
                choice = as.integer(zap_labels(s$invitation_dich)), rating = as.integer(s$invperc))
stopifnot(all(d$choice %in% 0:1), all(d$rating %in% seq(0, 100, 10)))
stopifnot(identical(lab(s$fs_applicant_female)[1:2] %in% c("Man", "Woman"), c(TRUE, TRUE)))
d[, attr_gender := c(Man = "Male", Woman = "Female")[lab(s$fs_applicant_female)]]
d[, attr_ethnicity := c(German = "German", Turkish = "Turkish")[lab(s$fs_applicant_migration)]]
d[, attr_education := c(`Intermediate HS` = "Intermediate high school degree",
                         Abitur = "Upper secondary high school degree (Abitur)",
                         Dropout = "Abitur + some college without degree")[lab(s$fs_applicant_education)]]
sf <- lab(s$fs_applicant_studyfield)
d[, attr_study_field := fifelse(is.na(sf), "(not shown)", c(mathematics = "Mathematics", language = "German studies")[sf])]
d[, attr_ses := c(`Low SES` = "Low (unskilled worker parents)", `Intermediate SES` = "Intermediate (skilled worker parents)",
                   `High SES` = "High (graduate worker parents)")[lab(s$fs_ses)]]
d[, attr_achievement := c(sufficient = "Low (sufficient)", satisfactory = "Intermediate (satisfactory)",
                           good = "High (good)")[lab(s$fs_achievement)]]
stopifnot(!anyNA(d))
stopifnot(d[, all((attr_study_field != "(not shown)") == (attr_education == "Abitur + some college without degree"))])
d[, cov_wave := as.integer(s$wave)]
d[, cov_occupational_field := c("Electronics", "Laboratory", "Administration", "Media")[as.integer(s$occupational_field)]]
d[, cov_recruiter_responsible := lab(s$recruiter_responsible)]
ta <- as.integer(zap_labels(s$type_applicants))
d[, cov_applicants_typical := fifelse(ta %in% 1:4, lab(s$type_applicants), NA_character_)]
stopifnot(all(d[!is.na(cov_applicants_typical), unique(cov_applicants_typical)] %in% c("not at all", "rather not", "rather", "very much")))
d[, cov_vignette_time_sec := as.numeric(s$time_use)]
stopifnot(d[, .N, id][, all(N == 8)], d[, uniqueN(task), id][, all(V1 == 8)], uniqueN(d$id) == 480)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "forster_2024_hiring_vignettes.csv"))
