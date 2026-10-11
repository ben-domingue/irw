##Human-rights x democracy vignette experiments (support for a preventive strike) from
##Tomz, M. R., & Weeks, J. L. P. (2020). Human rights and public support for war.
##The Journal of Politics, 82(1), 182-194. https://doi.org/10.1086/705741
##Replication data: Harvard Dataverse doi:10.7910/DVN/CCKENU, CC0 1.0, no restricted files.
##Files read: the deposit's single archive "TomzWeeks-HumanRights-JOP-Files" (a zip; save it as
##TomzWeeks-HumanRights-JOP-Files.zip next to nothing else and unzip it into <raw dir>/x, so that
##<raw dir>/x/2012-10-01-Main-YouGov/... exists). Inside, only the "rawdata/*-extracted.dta"
##files of four experiments and the authors' *-prepdata.do (read as text, never run) and the
##extracted questionnaires (docx, read as text). Not read: HR-versus-Democ (country-level
##data), 2017-04-19-Beliefs-SSI (a belief survey about real countries, no randomized profile).
##Usage: Rscript tomz_2020.R <raw dir> <output dir>
##
##Each respondent read ONE vignette about a country developing weapons and was asked whether the
##home country should attack its development sites. Four tables, one per experiment (different
##population, fielding and attribute set, so they are not pooled; the paper reports the US main
##study and treats the others as appendix replications):
##  tomz_2020_hr_war_us      Main study, US YouGov sample, n = 1,500 (nuclear program).
##  tomz_2020_hr_war_uk      UK sample (SSI), n = 1,452, British Armed Forces (nuclear program).
##  tomz_2020_hr_war_africa  US MTurk sample, n = 763, nuclear program in a country "in Africa".
##  tomz_2020_ballistic      US Lucid sample, n = 1,211, ballistic missile program, the region
##                           ("in Africa" / "in Asia" / "in Eastern Europe" / "in South America")
##                           is a third randomized factor.
##Attributes: attr_regime (democracy vs not) x attr_rights (does not violate vs violates human
##rights); the Africa table has a constant region ("in Africa", not randomized, dropped). Fixed
##text in every vignette: no alliance or high trade with the home country, the country's military
##is weaker, unclear motives, refused all requests to stop. Cells are near-equal (about 25 percent
##each); no source states the assignment probabilities or restrictions.
##LEVEL TEXT. Africa and Ballistic: the Qualtrics randomization blocks in the extracted
##questionnaire / the data give the exact sentence ("is a democracy. The president, the
##legislature, and local councils are elected by the people" / "is not a democracy. The people do
##not have the power to choose the leader"; "does not violate human rights; it does not imprison
##or torture its citizens because of their beliefs" / "violates human rights; it imprisons or
##tortures some of its citizens because of their beliefs"). Main and UK: the data hold only the
##authors' condition codes (Main value labels "is a democracy", "not a democracy", "does not
##violate rights", "violates rights"; UK 4 codes decoded by the prepdata.do), the sentences are
##not in the deposit, so the short forms "is a democracy" / "is not a democracy" / "does not
##violate human rights" / "violates human rights" are stored (the longer sentences of the other
##two experiments probably also applied, not verified).
##Outcome (all tables): rating = "Do you favor or oppose using the U.S. military (British Armed
##Forces in the UK) to attack the country's nuclear [missile] development sites?" 1 Favor
##strongly, 2 Favor somewhat, 3 Neither, 4 Oppose somewhat, 5 Oppose strongly, stored as in the
##source (LOWER = more support for the strike; the authors recode it to 0-100 with higher =
##more support). No opt-out ("Neither" is a scale point). Not kept: the mediator questions
##(chances of the country building weapons, costs, morality), which are beliefs about the
##situation, and the authors' index scales.
##Covariates (labels from the .dta value labels or the extracted questionnaires): Main
##cov_gender, cov_birth_year, cov_education (CCES categories), cov_party_id7 (pid7 labels;
##"not sure" kept as text, skipped = NA). UK cov_gender (1 Male, 2 Female per questionnaire),
##cov_age (code + 16 as in the authors' prepdata.do; code 1 "Under 18" is NA). Africa cov_gender,
##cov_birth_year (implausible years dropped), cov_education, cov_party_id (pid5 text from the
##questionnaire; "Other" and "Not sure" kept). Ballistic cov_gender (male 1 / female 0), cov_age
##(17 + the index of the age dummy, as the authors' prepdata.do), cov_education (docx categories).
##Dropped: Qualtrics response IDs, start dates, race, religiosity, attitudes. Ids are row numbers.
##PII: none found (Qualtrics ResponseIDs/rid in three files dropped; they are panel ids).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
X <- file.path(raw, "x")
rd <- function(f) as.data.table(read_dta(file.path(X, f)))
lab <- function(x) { l <- attr(x, "labels"); n <- names(l)[match(as.numeric(x), l)]; n }
nz <- function(x, bad) { x <- as.numeric(x); x[x %in% bad] <- NA; x }
rg <- c("is a democracy", "is not a democracy"); hr <- c("does not violate human rights", "violates human rights")
mk <- function(d, name) {
  stopifnot(all(d$rating %in% 1:5), !anyNA(d$attr_regime), !anyNA(d$attr_rights))
  d <- cbind(data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L), d)
  setorder(d, id, task, profile); fwrite(d, file.path(out, paste0(name, ".csv")))
}
## ---- Main (US YouGov) ----
m <- rd("2012-10-01-Main-YouGov/rawdata/2012-10-01-Main-extracted.dta")
stopifnot(nrow(m) == 1500, all(m$sta306_rand %in% 1:4))
edu <- lab(m$educ); edu[m$educ %in% c(8, 9)] <- NA
pid <- lab(m$pid7); pid[m$pid7 %in% c(98, 99)] <- NA
gen <- lab(m$gender); gen[!gen %in% c("male", "female")] <- NA
by <- nz(m$birthyr, c(9998, 9999)); by[!is.na(by) & (by < 1900 | by > 1994)] <- NA
mk(data.table(rating = as.integer(nz(m$sta307, c(8, 9))),
  attr_regime = rg[ifelse(m$sta306_rand <= 2, 1, 2)], attr_rights = hr[ifelse(m$sta306_rand %in% c(1, 3), 1, 2)],
  cov_gender = gen, cov_birth_year = as.integer(by), cov_education = edu, cov_party_id7 = pid), "tomz_2020_hr_war_us")
## ---- UK ----
u <- rd("2014-03-01-UK-SSI/rawdata/2014-03-01-UK-extracted.dta")
stopifnot(nrow(u) == 1452, all(u$randforce %in% 1:4))
ag <- ifelse(u$age >= 2, u$age + 16, NA)
mk(data.table(rating = as.integer(u$sta307),
  attr_regime = rg[ifelse(u$randforce <= 2, 1, 2)], attr_rights = hr[ifelse(u$randforce %in% c(1, 3), 1, 2)],
  cov_gender = c("male", "female")[u$gender], cov_age = as.integer(ag)), "tomz_2020_hr_war_uk")
## ---- Africa MTurk ----
f <- rd("2012-10-07-Africa-MTurk/rawdata/2010-10-07-Africa-extracted.dta")
stopifnot(nrow(f) == 763, all(as.character(f$region) == "in Africa"))
rgl <- c("is a democracy. The president, the legislature, and local councils are elected by the people",
         "is not a democracy. The people do not have the power to choose the leader")
hrl <- c("does not violate human rights; it does not imprison or torture its citizens because of their beliefs",
         "violates human rights; it imprisons or tortures some of its citizens because of their beliefs")
fr <- as.character(as_factor(f$regime)); fh <- as.character(as_factor(f$hrts))
if (!all(fr %in% rgl)) { fr <- as.character(f$regime); fh <- as.character(f$hrts) }
stopifnot(all(fr %in% rgl), all(fh %in% hrl))
yb <- as.numeric(f$year_born); yb[!is.na(yb) & (yb < 1900 | yb > 1995)] <- NA
mk(data.table(rating = as.integer(f$p_pref), attr_regime = fr, attr_rights = fh,
  cov_gender = c("male", "female")[f$gender], cov_birth_year = as.integer(yb),
  cov_education = c("Did not graduate form high school", "High school graduate", "Some college, but no degree (yet)",
    "2-year college degree", "4-year college degree", "Postgraduate degree (MA, MBA, MD, JD, PhD, etc.)")[f$education],
  cov_party_id = c("Democrat", "Republican", "Independent", "Other", "Not sure")[f$pid5]), "tomz_2020_hr_war_africa")
## ---- Ballistic (Lucid) ----
b <- rd("2018-04-13-Ballistic-Lucid/rawdata/2018-04-13-Ballistic-extracted.dta")
stopifnot(nrow(b) == 1211)
br <- as.character(b$regime); bh <- as.character(b$rights); bg <- as.character(b$region)
stopifnot(all(br %in% rgl), all(bh %in% hrl), all(bg %in% c("in Africa", "in Asia", "in Eastern Europe", "in South America")))
am <- as.matrix(b[, paste0("age_", 1:82), with = FALSE]); agb <- ifelse(rowSums(am == 1, na.rm = TRUE) == 1, 17 + max.col(replace(am, is.na(am), 0), "first"), NA)
edb <- c("No formal education", "1st, 2nd, 3rd, or 4th grade", "5th or 6th grade", "7th or 8th grade", "9th grade", "10th grade",
  "11th grade", "12th grade NO DIPLOMA", "HIGH SCHOOL GRADUATE - high school DIPLOMA or the equivalent (GED)",
  "Some college, no degree", "Associate degree", "Bachelor's degree", "Master's degree", "Professional or Doctorate degree")
stopifnot(b$male %in% c(0, 1, NA), b$educ %in% c(1:14, NA))
mk(data.table(rating = as.integer(b$sta307), attr_region = bg, attr_regime = br, attr_rights = bh,
  cov_gender = c("female", "male")[b$male + 1L], cov_age = as.integer(agb), cov_education = edb[b$educ]), "tomz_2020_ballistic")
