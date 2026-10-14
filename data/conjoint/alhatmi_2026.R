##Factorial survey of graduate hiring among Omani employers from
##Al Hatmi, K. (2026). Social networks, gender, and graduate hiring in a rentier state: Disentangling
##referral types and ascriptive signals in Omani labour markets. Research in Social Stratification and
##Mobility (journal article not yet identified by DOI; the README calls it "submitted").
##Replication data: Harvard Dataverse doi:10.7910/DVN/R2W8AW, CC0 1.0, no restricted files, no terms
##(sibling deposit 10.7910/DVN/O5XKXR holds only the README and R scripts, CC0, read as text).
##File read: "Factorial Survey Data.zip" -> "Anaylsis Data Prepartion/newdata.dta" (2,280 rows = 190 employers x
##12 vignettes, with Stata value labels). Also read as text/labels: "Final Vignettes Design and SAS/Final
##Factors and Levels.docx" (factors, levels, the two questions), vignettetexts_1.dta (the 144 vignettes).
##The README in O5XKXR describes outcomes as 0-10 and a different file (vignette_data.csv) that is not in
##the deposit; the data hold 0-100 values (see below), so the values stored in newdata.dta are used.
##Usage: Rscript alhatmi_2026.R <raw dir> <output dir>   (raw dir holds newdata.dta)
##
##190 employers/recruiters in Oman (Qualtrics survey, 2019). Each rated 12 text resumes of job applicants
##for ONE occupation (trial_job_type: Accountant / Software Developer / Mechanical Engineer, constant within
##respondent). The 144 vignettes come from a fixed fractional design (SAS, 144 vignettes in 12 decks of 12);
##each respondent got one deck (trial_deck 1-12, constant within respondent) and the 12 vignettes of that
##deck, in position qnum 1-12 (task = qnum; that it equals the order shown is assumed, not stated).
##Fixed blocked design: everyone in a deck saw the same 12 vignettes.
##Nine attributes (levels exactly as in the design document / value labels):
##  attr_gender, attr_nationality (Omani / Expatriate), attr_experience (4 levels, internship at/outside the
##  organisation, relevant experience, none), attr_extracurricular, attr_place_of_study (leading/non-leading
##  university in Oman/abroad), attr_education (Diploma/Bachelor's/Master's), attr_field, attr_grade (4 levels),
##  attr_referral (4 levels incl. "No").
##Outcomes (0-100 as stored, no anchors in the deposit; README says 0-10):
##  rating_hire   V1_  "How likely is it that you would hire this applicant?"
##  rating_train  V2_  "If this applicant [is] hired, how likely [is it that] the applicant would be easy to train
##                to meet the job demands?" (wording from the design document, light editing in the doc itself)
##Rows with both outcomes missing are omitted (42 and 39 missing values, partly the same rows). No opt-out.
##Covariates: cov_gender (RESP_gender; Prefer not to say -> NA), cov_age_group (RESP_age text; prefer not -> NA),
##cov_education (RESP_hig_qualification, the label text; prefer not -> NA), cov_nationality (RESP_nationality).
##Dropped: the respondent-level "importance" rankings s_*, free text (s_others_text, *_text), job description
##similarity, estimation flags _est_*, firm descriptors. PII FOUND in another file of the deposit:
##"Cleaned_Recruitment Practices in Oman ...dta" (IP address, lat/long, recipient names/email columns): NOT used.
##Respondent id = re-keyed integer of id_resp.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_dta(file.path(raw, "newdata.dta")))
stopifnot(nrow(d) == 2280, uniqueN(d$id_resp) == 190, !anyDuplicated(d[, .(id_resp, qnum)]))
lab <- function(x) { l <- attr(x, "labels"); as.character(names(l)[match(as.numeric(x), l)]) }
chk <- function(x) { stopifnot(!anyNA(x)); x }
rl <- function(x) { v <- lab(x); v[v %in% c("Prefer not to say", "prefer_not_to_say", "missing")] <- NA; v }
x <- data.table(id = match(d$id_resp, sort(unique(d$id_resp))), task = as.integer(d$qnum), profile = 1L,
  rating_hire = as.integer(d$V1_), rating_train = as.integer(d$V2_),
  attr_gender = chk(lab(d$gender)), attr_nationality = chk(lab(d$nationality)),
  attr_experience = chk(lab(d$experience_and_internship)), attr_extracurricular = chk(lab(d$extra_curricular_activities)),
  attr_place_of_study = chk(lab(d$place_of_study)), attr_education = chk(lab(d$level_of_education)),
  attr_field = chk(lab(d$field_of_study)), attr_grade = chk(lab(d$grade)), attr_referral = chk(lab(d$referral)),
  trial_deck = as.integer(d$id_deck), trial_job_type = chk(lab(d$job_type)),
  cov_gender = tolower(rl(d$RESP_gender)), cov_age_group = rl(d$RESP_age), cov_education = rl(d$RESP_hig_qualification),
  cov_nationality = rl(d$RESP_nationality))
x <- x[!(is.na(rating_hire) & is.na(rating_train))]
stopifnot(all(x$rating_hire >= 0 & x$rating_hire <= 100, na.rm = TRUE))
setorder(x, id, task, profile)
fwrite(x, file.path(out, "alhatmi_2026_oman_graduate_hiring.csv"))
cat(nrow(x), uniqueN(x$id), "\n")
