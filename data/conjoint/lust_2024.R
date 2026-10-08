##Single-profile candidate conjoint (2x2x2x2 factorial vignette) from
##Lust, E., & Benstead, L. J. (2024). Is the future female? Lessons from a conjoint experiment
##on voter preferences in six Arab countries. Comparative Political Studies.
##https://doi.org/10.1177/00104140241237462
##Replication data: Harvard Dataverse doi:10.7910/DVN/2G7A0M, CC0 1.0. Files read:
##IsFemaleFuture_Raw.dta (original format; value labels used for all level text). Read as text
##only: README.pdf, Cleaning_Preparation.do, Analysis.do. Educ_translated.dta not used.
##Usage: Rscript lust_2024.R <raw dir> <output dir>
##
##Fielded 2022-08-19 to 2022-09-25 (SurveyDate) in Egypt, Algeria, Morocco, Jordan, Tunisia and
##Libya; one table with cov_country because the authors pool the countries (country fixed
##effects) and the attribute set is shared. Pilot respondents in Saudi Arabia (231) and Yemen
##(129) are dropped, as the authors did (Cleaning_Preparation.do: vignette judged unrealistic).
##Each respondent read ONE candidate description (task 1, profile 1) with four randomized binary
##attributes; all 16 cells have 1,900-2,070 respondents. Level text = Stata value labels:
##  attr_gender       Female / Male
##  attr_background   CSO / Business         (the do-file's "Competency"; CSO = civil society)
##  attr_party_goals  Local Development / National Economy
##  attr_success      No Information / Successful
##The vignette prose, survey language(s), vendor and the outcome question wording are NOT in the
##deposit, and the article could not be reached (publisher and repository copies behind a
##bot check), so outcome wording below is a paraphrase of the authors' variable names. All ten
##outcomes are 0-10 ratings of the same candidate (EQ1-EQ10; anchors unknown; 98/99 = don't
##know/refused, set to NA as in the authors' do-file):
##  rating                 EQ1  Vote_For
##  rating_endorse         EQ2  Would_Infl_Endorse
##  rating_raise_funds     EQ3  Good_Raise_Funds
##  rating_security        EQ4  Good_Improve_Security
##  rating_development     EQ5  Good_Promote_Development
##  rating_social_problems EQ6  Good_Social_Probs
##  rating_national_econ   EQ7  Improve_Ntnl_Econ
##  rating_services        EQ8  Help_Obtain_Services
##  rating_others_vote     EQ9  Others_Would_Vote
##  rating_similar         EQ10 Likely_See_Similar_Candidate
##Direction assumed higher = more (likely/good), from the variable names; not confirmed.
##Respondents with all ten outcomes missing are omitted. No survey weights in the deposit.
##Dropped: SbjNum (vendor respondent number; re-keyed), SurveyDate, Consent (all yes),
##Governorate (labels are only "Governorate N"), Education_other (Arabic free text), and the
##authors' derived variables (Congruent*, *Bi). Covariates: cov_age, cov_gender (Stata value labels
##on Gender: 1 "Male" -> "male", 2 "Female" -> "female", 3 "Refuse to Answer" -> NA), cov_education
##(the Stata value-label text of Education: "Less than high school", "High school", "Bachelor
##degree", "Masters, professional degree, or PhD", "Other (specify)"; the Arabic free text of
##"Other" is dropped). The rest keep the source codes (labels in the .dta): cov_citizen,
##cov_religiosity (0-10, 98/99 -> NA), the six stereotype/sexism items, and the two manipulation
##checks (cov_check_gender, cov_check_background).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- read_dta(file.path(raw, "IsFemaleFuture_Raw.dta"))
x <- x[!(zap_labels(x$Country) %in% c(2, 7)), ]
lab <- function(v) as.character(as_factor(v, levels = "labels"))
num <- function(v, na = c(98, 99)) { v <- as.integer(zap_labels(v)); v[v %in% na] <- NA_integer_; v }
d <- data.table(rid = as.numeric(x$SbjNum), task = 1L, profile = 1L)
oc <- c(rating = "EQ1", rating_endorse = "EQ2", rating_raise_funds = "EQ3", rating_security = "EQ4",
        rating_development = "EQ5", rating_social_problems = "EQ6", rating_national_econ = "EQ7",
        rating_services = "EQ8", rating_others_vote = "EQ9", rating_similar = "EQ10")
for (o in names(oc)) d[, (o) := num(x[[oc[[o]]]])]
d[, attr_gender := lab(x$CandidateGender)][, attr_background := lab(x$Competency)]
d[, attr_party_goals := lab(x$PartyGoals)][, attr_success := lab(x$Successful)]
d[, cov_country := lab(x$Country)]
d[, cov_age := as.integer(x$Age)]
stopifnot(identical(names(attr(x$Gender, "labels")), c("Male", "Female", "Refuse to Answer")))
d[, cov_gender := c("male", "female", NA)[as.integer(zap_labels(x$Gender))]]
d[, cov_citizen := as.integer(zap_labels(x$Citizen))]
d[, cov_education := lab(x$Education)]
d[, cov_religiosity := num(x$Religiosity)]
for (v in c("ComSexism", "BizAppropriate", "CSOAppropriate", "BizAbility", "CSOAbility", "BenSexism", "HosSexism"))
  d[, paste0("cov_", tolower(v)) := as.integer(zap_labels(x[[v]]))]
d[, cov_check_gender := as.integer(zap_labels(x$CheckGender))][, cov_check_background := as.integer(zap_labels(x$CheckCompetency))]
stopifnot(!anyDuplicated(d$rid), d[, all(attr_gender != "" & attr_background != "" & attr_party_goals != "" & attr_success != "")])
d <- d[rowSums(!is.na(d[, names(oc), with = FALSE])) > 0]
setorder(d, rid)
d[, id := seq_len(.N)][, rid := NULL]
setcolorder(d, c("id", "task", "profile"))
fwrite(d, file.path(out, "lust_2024_female_candidates.csv"))
