##Police officer conjoint and pictured-officer-team experiment (US) from
##Pickett, J. T., Graham, A., Nix, J., & Cullen, F. T. (2024). Officer diversity may reduce Black
##Americans' fear of the police. Criminology, 62(1), 35-63. https://doi.org/10.1111/1745-9125.12360
##Replication data: Harvard Dataverse doi:10.7910/DVN/ASL3JD, CC0 1.0. File read:
##OfficerDiversity_data(12).dta (Dataverse "original format" download of the .tab, datafile 8141517;
##saved as OfficerDiversity_data.dta; Stata value and variable labels used). Read as text only:
##OfficerDiversity_code.do. Design facts from the SocArXiv preprint (osf.io/7mrgp, sections 5.1-5.4).
##Usage: Rscript pickett_2024.R <dir holding OfficerDiversity_data.dta> <output dir>
##
##YouGov online panel, 21 Apr - 2 May 2022, 1,100 respondents: a general-population sample (650,
##weight_gp) and a Black oversample (450, weight_aa). The authors pool both with combweight
##(= weight_aa, else weight_gp), stored as cov_survey_weight; cov_sample says which sample.
##Two experiments, two tables (different designs, same respondents and ids):
##pickett_2024_officer_conjoint: 5 conjoint tables of 2 officer profiles (Officer A / B), 7 attributes:
##  race/ethnicity, gender, age, physical build, education, body-worn camera, prior civilian complaint.
##  Level text as stored in the deposit (e.g. "Yes, for disrespect and excessive force"; age "25"). The
##  preprint: "They indicated which officer in each pairing would make them the most afraid"; levels
##  "randomized independently for each profile in each conjoint table"; attribute order "randomized
##  between respondents and held constant across tables": recorded in order_conjoint (a list of the 7
##  attribute names) -> attrpos_* (1 = top row). choice = officer_choice<p>, profile p = 2t-1 (A), 2t (B);
##  the script checks it against Q2-Q6 ("Police officer preference - Table t": Officer A / Officer B).
##  Forced choice; tasks with no answer (14 tasks) are dropped: 10,972 profile rows, 1,099 respondents,
##  exactly as the preprint reports.
##pickett_2024_officer_photos: one picture of a two-officer team per respondent (task = profile = 1),
##  2 x 3 x 3 x 2 x 2 factorial: race (White / Latino / Black) and sex (Male / Female) of officer 1 and of
##  officer 2 (six edited Chicago Face Database photos per officer position), and the location of the
##  stop (Empty Street / Busy Street). Level text = the Stata value labels of po_race1/2, po_sex1/2 and
##  MANIPULATION_A (number prefixes such as "0. " stripped); the script checks them against the photo
##  codes MANIPULATION_B / _C ("Black Male 1" etc.). Displayed as an image. Outcomes, raw 1-5 codes as
##  stored (1 = Very Afraid, 2 Afraid, 3 Neither Afraid Nor Unafraid, 4 Unafraid, 5 = Very Unafraid; HIGHER
##  = LESS afraid; the authors reverse them to 0-4 fear): "Afraid these officers will --" (Stata variable
##  labels; the preprint: how afraid they would be of these mistreatments "if the pictured officers
##  stopped them") rating_hurt "Physically hurt you", rating_force "Use excessive force against you",
##  rating_weapon "Point a weapon at you", rating_arrest "Wrongfully arrest you". N = 1,100 as in the paper.
##Covariates (both tables): cov_sample, cov_survey_weight, cov_gender (gender: 1 Male -> male, 2 Female
##-> female; value labels), cov_birth_year (birthyr), cov_race (race value-label text), cov_education
##(educ value-label text), cov_party_id7 (pid7 value-label text, incl. "Not sure"/"Don't know"),
##cov_fear_police_1..10 (Q1_1-Q1_10, personal fear of police: stop, search, yell at, handcuff, kick or
##punch, pin to ground, pepper-spray, tase, shoot, kill you; raw 1 = Very Afraid ... 5 = Very Unafraid).
##Dropped: inputzip (ZIP code, PII), inputstate, other attitude/background items, derived indices.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "OfficerDiversity_data.dta"))
stopifnot(nrow(k) == 1100, uniqueN(k$caseid) == 1100)
lab <- function(x) as.character(as_factor(x, levels = "labels"))
stopifnot(all(k$gender %in% 1:2))
cv <- data.table(id = seq_len(nrow(k)),
  cov_sample = fifelse(!is.na(k$weight_gp), "general population", "Black oversample"),
  cov_survey_weight = fcoalesce(as.numeric(k$weight_aa), as.numeric(k$weight_gp)),
  cov_gender = c("male", "female")[as.integer(k$gender)], cov_birth_year = as.integer(k$birthyr),
  cov_race = lab(k$race), cov_education = lab(k$educ), cov_party_id7 = lab(k$pid7))
stopifnot(!anyNA(cv$cov_survey_weight), cv[, sum(cov_sample == "Black oversample")] == 450)
for (j in 1:10) cv[, paste0("cov_fear_police_", j) := as.integer(k[[paste0("Q1_", j)]])]
## Experiment 1: conjoint
an <- c(race = "Race/Ethnicity", gender = "Gender", age = "Age", build = "Physical Build", education = "Education",
        camera = "Body-Worn Camera", complaint = "Prior Civilian Complaint")
src <- c(race = "officer_race", gender = "officer_gender", age = "officer_age", build = "officer_build",
         education = "officer_educ", camera = "officer_cam", complaint = "officer_complain")
ord <- lapply(regmatches(k$order_conjoint, gregexpr("'[^']+'", k$order_conjoint)), function(x) gsub("'", "", x))
stopifnot(all(lengths(ord) == 7), all(vapply(ord, function(x) setequal(x, an), TRUE)))
L <- rbindlist(lapply(1:10, function(p) {
  d <- data.table(id = seq_len(nrow(k)), task = (p + 1L) %/% 2L, profile = 2L - p %% 2L,
                  choice = as.integer(k[[paste0("officer_choice", p)]]))
  for (nm in names(src)) d[, paste0("attr_", nm) := as.character(k[[paste0(src[[nm]], p)]])]
  for (nm in names(an)) d[, paste0("attrpos_", nm) := vapply(ord, function(x) match(an[[nm]], x), 1L)]
  d }))
qa <- sapply(2:6, function(q) as.integer(k[[paste0("Q", q)]]))
L[, ans := qa[cbind(id, task)]]
stopifnot(L[is.na(ans), all(is.na(choice))], L[!is.na(ans), all(choice == as.integer(profile == ans))])
L <- L[!is.na(choice)][, ans := NULL]
stopifnot(nrow(L) == 10972, uniqueN(L$id) == 1099, L[, sum(choice), .(id, task)][, all(V1 == 1)],
          !anyNA(L[, .SD, .SDcols = patterns("^attr_")]), all(L[, .SD, .SDcols = patterns("^attr_")] != ""))
L <- merge(L, cv, by = "id"); setorder(L, id, task, profile)
fwrite(L, file.path(out, "pickett_2024_officer_conjoint.csv"))
## Experiment 2: pictured officer team
strip <- function(x) sub("^[0-9]+\\.\\s*", "", lab(x))
P <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L,
  rating_hurt = as.integer(k$Q7_1), rating_force = as.integer(k$Q7_2), rating_weapon = as.integer(k$Q7_3), rating_arrest = as.integer(k$Q7_4),
  attr_officer1_race = strip(k$po_race1), attr_officer1_sex = strip(k$po_sex1),
  attr_officer2_race = strip(k$po_race2), attr_officer2_sex = strip(k$po_sex2), attr_location = strip(k$MANIPULATION_A))
chkp <- function(m, r, s) { t <- sub("Man", "Male", sub(" [12]$", "", lab(m))); all(t == paste(r, s)) }
stopifnot(chkp(k$MANIPULATION_B, P$attr_officer1_race, P$attr_officer1_sex), chkp(k$MANIPULATION_C, P$attr_officer2_race, P$attr_officer2_sex))
stopifnot(all(P$attr_location %in% c("Empty Street", "Busy Street")), !anyNA(P), all(as.matrix(P[, .(rating_hurt, rating_force, rating_weapon, rating_arrest)]) %in% 1:5))
P <- merge(P, cv, by = "id"); setorder(P, id, task, profile)
fwrite(P, file.path(out, "pickett_2024_officer_photos.csv"))
