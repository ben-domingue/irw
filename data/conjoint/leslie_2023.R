##Primary-care clinic discrete choice experiment for hypertension (Karnataka, India, 2021) from
##Leslie, H. H., Babu, G. R., Dolcy Saldanha, N., Turcotte-Tremblay, A.-M., Ravi, D., Shapeti, S. S.,
##Kapoor, N., Prabhakaran, D., & Kruk, M. E. (2023). Population preferences for primary care models for
##hypertension in Karnataka, India. JAMA Network Open, 6(3), e232937.
##https://doi.org/10.1001/jamanetworkopen.2023.2937 (a correction followed, JAMA Netw Open 2024;7(1):e2354465;
##not seen).
##Replication data: Harvard Dataverse doi:10.7910/DVN/42TAA9, CC0 1.0. Files read (Dataverse "original
##format"): hhDCE01.dta (one row per respondent x choice set x alternative) and hhsurvey02.dta (respondent
##level). Level text, wording and design from the article (Table 1, Methods) and Supplement 1 (eMethods
##Table 3, eFigure 1 introductory script and choice card).
##Usage: Rscript leslie_2023.R <dir holding the two .dta> <output dir>
##
##1,085 adults 30+ with hypertension in Bengaluru Nagara (urban) and Kolar (rural) districts, household
##survey June-July 2021 (= the article). Fixed blocked design: 35 D-efficient choice sets in 5 versions of 7
##plus one set common to all versions (choice_set 36), 8 cards per respondent; data collectors cycled the
##versions (trial_version = dce_block_choice). Two alternatives, "Health facility A" / "Health facility B"
##(profile = alt), no opt-out.
##task = choice_set (the design's choice-set id, 1-36), NOT the order shown: the deposit does not record the
##order (group numbers the sets in id order). 22 respondents skipped one card and 1 skipped two (their
##rows are absent), as in Supplement 1.
##Outcome:
##  choice = outcome. Script: "Please tell us which of the two facilities you would prefer to go to for your
##           care." Exactly one per answered set (checked).
##Attributes, level text from the choice card (eFigure 1) and Table 1; codes are the .dta's binary/numeric
##attribute variables (variable labels "Attribute: courtesy", etc.), 1 = the level named by the label:
##  attr_courtesy  (polite 1/0)   "Clinic staff are courteous" / "Clinic staff are not always courteous"
##                                (1 = 9 of 16 alternatives per version = eMethods Table 3 "Always")
##  attr_wait      (wait, hours)  "Patients wait 15 minutes" / "30 minutes" / "1 hour" / "2 hours" / "3 hours" / "5 hours"
##  attr_provider  (doctor 1/0)   "The provider is a doctor" / "The provider is a nurse"
##  attr_assessment (assesscare)  "Medical staff assess patients carefully" / "Medical staff do not always assess patients carefully"
##  attr_medication (freemed)     "Free medication is available in this facility" / "Free medication is not always available in this facility"
##The wording was also produced in Kannada with illustrations; respondents chose English or Kannada (not
##recorded). Attribute order on the card is fixed (eFigure 1).
##Dropped: derived variables (noeduc, female, nodiag, wait_cat*, wait_sq, dominant_*, dce_respsd, complete,
##record_tag, alt_tag, group). record_id is a sequential study id (kept as id).
##Covariates (hhsurvey02.dta value labels): cov_district (Bengaluru / Kolar), cov_gender (1 Male = male,
##2 Female = female, 3 Other = other), cov_age (age_2vars, years; 2 missing), cov_education (educ4: No formal
##education / Primary / Secondary / College or higher, the deposit's 4-group recode), cov_caste (caste4cat),
##cov_hypertension_diagnosed (hypt_diag No/Yes), cov_occupation (occup_cat; Refused = NA),
##cov_ever_treated (ever_med 0/1), cov_public_primary_care (public_tx 0/1), cov_care_source (hypfac_cat).
##No survey weight in the deposit.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(zap_labels(read_dta(file.path(raw, "hhDCE01.dta"))))
s <- read_dta(file.path(raw, "hhsurvey02.dta"))
lab <- function(v) { r <- as.character(as_factor(v, levels = "labels")); r }
sv <- data.table(record_id = as.numeric(s$record_id), trial_version = as.integer(zap_labels(s$dce_block_choice)),
  cov_district = lab(s$location), cov_gender = c("male", "female", "other")[as.integer(zap_labels(s$gender))],
  cov_age = as.integer(zap_labels(s$age_2vars)), cov_education = lab(s$educ4), cov_caste = lab(s$caste4cat),
  cov_hypertension_diagnosed = lab(s$hypt_diag), cov_occupation = lab(s$occup_cat),
  cov_ever_treated = as.integer(zap_labels(s$ever_med)), cov_public_primary_care = as.integer(zap_labels(s$public_tx)),
  cov_care_source = lab(s$hypfac_cat))
sv[cov_occupation == "Refused", cov_occupation := NA]
stopifnot(!anyDuplicated(sv$record_id), all(zap_labels(s$gender) %in% 1:3))
waits <- c("0.25" = "Patients wait 15 minutes", "0.5" = "Patients wait 30 minutes", "1" = "Patients wait 1 hour",
           "2" = "Patients wait 2 hours", "3" = "Patients wait 3 hours", "5" = "Patients wait 5 hours")
bin <- function(v, yes, no) { stopifnot(all(v %in% 0:1)); ifelse(v == 1, yes, no) }
d <- x[, .(record_id, task = as.integer(choice_set), profile = as.integer(alt), choice = as.integer(outcome),
  attr_courtesy = bin(polite, "Clinic staff are courteous", "Clinic staff are not always courteous"),
  attr_wait = unname(waits[as.character(wait)]),
  attr_provider = bin(doctor, "The provider is a doctor", "The provider is a nurse"),
  attr_assessment = bin(assesscare, "Medical staff assess patients carefully", "Medical staff do not always assess patients carefully"),
  attr_medication = bin(freemed, "Free medication is available in this facility", "Free medication is not always available in this facility"))]
stopifnot(!anyNA(d$attr_wait), d[, .N, .(record_id, task)][, all(N == 2)], d[, sum(choice), .(record_id, task)][, all(V1 == 1)])
d <- merge(d, sv, by = "record_id", all.x = TRUE)
stopifnot(!anyNA(d$trial_version))
## the version's sets: 7 of its own + set 36
stopifnot(d[task != 36, uniqueN(trial_version), task][, all(V1 == 1)])
setnames(d, "record_id", "id"); d[, id := as.integer(id)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "leslie_2023_hypertension_care.csv"))
cat(nrow(d), "rows,", uniqueN(d$id), "respondents\n")
