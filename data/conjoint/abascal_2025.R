##Racial-classification profile conjoint (US) from
##Abascal, M., Armenta, A., Halm, W. M., & Hopkins, D. J. (2025). Who polices which
##boundaries? How racial self-identification affects external classification. American
##Journal of Sociology, 131(3), 630-683. https://doi.org/10.1086/737164
##Replication data: Harvard Dataverse doi:10.7910/DVN/PWDZPQ, CC0 1.0. File read:
##CleanedPooledREPS_04252023_WH.csv; replication_file_who_polices_abascal_et_al.R read as
##text. Design and wording from the SocArXiv version (doi:10.31235/osf.io/bhrdj, pp. 22-27).
##Usage: Rscript abascal_2025.R <dir holding the .csv> <output dir>
##
##Two samples, pooled by the authors in every analysis ("we therefore pool the samples"),
##same attributes and questions -> ONE table with cov_sample: Dynata online panel (1,719,
##May-July 2022, oversamples of Black, Asian and Latino respondents) and 1,016
##undergraduates (UC Irvine, UC Riverside, Howard; April-June 2022). Single-profile design:
##each respondent saw one profile at a time (10 profiles; 9 in the Dynata data, where a
##programming error forced the authors to drop one) and answered six agree/disagree
##statements about it. task = the source `Profile` number (1-10), profile = 1. The file's
##row order within a respondent differs from `Profile`, and neither is documented as the
##display order, so task-order analyses should not lean on it.
##Attributes (seven, "independently randomized", article p. 22): self-identification, the
##setting of that self-report (respondent-level arm, below), birth parents' race/ethnicity,
##a face photo (10 Chicago Face Database faces, each in light/medium/dark skin versions,
##blurred), parents' occupations, religion, English spoken at home, age. Level text: the
##source's short labels are mapped to the article's quoted display text for
##self-identification and parents ("White", "Black/African American",
##"Latino/Latino(a/x)", "Asian/Asian American", "Middle Eastern or North African") and for
##English at home ("Yes"/"No"); occupations ("Doctor, Lawyer", ...; the source's "Lawer" is
##kept as is), religion and age are stored as in the source. The photo is stored as the
##authors' image code (attr_photo, e.g. LF201) plus attr_skin_tone (Light/Medium/Dark, the
##skin-colour version of that face). attr_photo_gender (F/M) and attr_photo_ethnicity
##(Latino/White, the CFD model's self-identification) are the authors' coding of each face,
##nested in attr_photo; respondents saw the face, not these words. Face LF206 appears about
##a third as often as each other face (947 vs about 2,600 rows; not documented).
##trial_condition: respondents were assigned with equal probability to learn that profiles
##reported their race on an "Anonymous Survey" or a "Scholarship Application" (4 student
##respondents have no value).
##Outcomes, five-point, 1 = strongly disagree to 5 = strongly agree ("indicate whether you
##agree or disagree with each statement"): rating_white "This person is White",
##rating_black "... is Black/African American", rating_latino "... is Latino/Latino(a/x)",
##rating_asian "... is Asian/Asian American", rating_mena "... is Middle Eastern or North
##African", rating_poc "... is a person of color". The source's *_disagree columns are
##6 - *_agree and are dropped.
##DROPPED: 58 student respondents whose 580 rows have no attributes and no answers, then
##rows with no answer to any statement: 2,653 respondents, 24,233 rows remain (article: 1,719 + 1,016 =
##2,735 recruited). Respondent_ID (Qualtrics response IDs for the Dynata sample) re-keyed to
##integers. Free text (race, Hispanic and Asian origin write-ins, university major) and the
##raw Q* survey codes are dropped; the authors' labelled respondent variables are kept:
##cov_race (Wht/Blk/Hisp/Asn), cov_gender, cov_income, cov_nativity, cov_party,
##cov_education, cov_birth_year.
##Check: share agreeing (4-5) that a profile is White/Latino/MENA = 28%/30%/30% (article
##p. 27: White 28%, Latino 31%, MENA 30%).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "CleanedPooledREPS_04252023_WH.csv"), na.strings = c("", "NA"))
stopifnot(s[, uniqueN(Respondent_ID), Sample][order(Sample), V1] == c(1719, 1016),
          s[, .N, .(Respondent_ID, Profile)][, all(N == 1)], all(s$White_agree + s$White_disagree == 6, na.rm = TRUE))
s <- s[!is.na(image_ID)]
self_map <- c("White (self)" = "White", Black = "Black/African American", Hispanic = "Latino/Latino(a/x)",
              Asian = "Asian/Asian American", MENA = "Middle Eastern or North African")
par_map <- c("White (parents)" = "White", "Black/African-American" = "Black/African American",
             "Hispanic/Latino(a/x)" = "Latino/Latino(a/x)", "Asian/Asian-American" = "Asian/Asian American",
             "Middle Eastern or North African" = "Middle Eastern or North African")
stopifnot(all(s$selfID_ethnic %in% names(self_map)), all(s$birthparents_ethnicID %in% names(par_map)),
          all(s$english %in% c("Speak English at home", "Don't speak English at home")))
key <- unique(s$Respondent_ID)
d <- s[, .(id = match(Respondent_ID, key), task = as.integer(Profile), profile = 1L,
           rating_white = White_agree, rating_black = Black_agree, rating_latino = Hispanic_agree,
           rating_asian = Asian_agree, rating_mena = MENA_agree, rating_poc = POC_agree,
           attr_self_identification = unname(self_map[selfID_ethnic]), attr_parents = unname(par_map[birthparents_ethnicID]),
           attr_photo = image_ID, attr_skin_tone = trimws(skin_tone), attr_photo_gender = gender, attr_photo_ethnicity = ethnicity,
           attr_parents_occupation = parents_occupation, attr_religion = religion,
           attr_english_at_home = ifelse(english == "Speak English at home", "Yes", "No"), attr_age = as.character(age),
           trial_condition = Condition, cov_sample = Sample, cov_race = resrace, cov_gender = Gender, cov_income = Income,
           cov_nativity = Nativity, cov_party = party, cov_education = educ, cov_birth_year = as.integer(rYOB))]
oc <- grep("^rating_", names(d), value = TRUE)
d <- d[rowSums(!is.na(d[, ..oc])) > 0]
d[, id := match(id, sort(unique(id)))]
stopifnot(uniqueN(d$id) == 2653, nrow(d) == 24233)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "abascal_2025_racial_classification.csv"))
