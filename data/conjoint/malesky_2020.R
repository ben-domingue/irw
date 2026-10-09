##National Assembly candidate conjoint in the PAPI survey (Vietnam, 2016 wave) from
##Malesky, E., & Schuler, P. (2020). Single-party incumbency advantage in Vietnam: A conjoint
##survey analysis of public electoral support. Journal of East Asian Studies, 20(1), 25-52.
##https://doi.org/10.1017/jea.2019.40
##Replication data: Harvard Dataverse doi:10.7910/DVN/Z8ALJA, CC0 1.0, no restricted files.
##File read: PAPI_Conjoint_2016.tab as its original Stata file (read here as
##PAPI_Conjoint_2016.dta; value labels used). Read as text, not run:
##20190718_PAPIConjoint_2016.do (which built this file from the raw PAPI 2016 data). Design and
##wording from the deposited article (Malesky_JEAS.pdf, Table 3) and appendix
##(IncumbencyAdvantage_APPENDIX_final.pdf, Appendix H).
##Usage: Rscript malesky_2020.R <raw dir> <output dir>
##
##ONLY THE 2016 WAVE is built here. The 2017 and 2018 waves (PAPI_Conjoint_2017/2018) are held:
##their attribute columns carry no value labels (codes map to text only through the .do
##dummies), the 2018 file's variable labels are shifted by one variable, the 2018 .do assigns
##candidate 1's province to candidate 2's row, 2018 has randomized career/experience and
##policy/no-policy arms, and both years add a separate village-leader conjoint.
##
##PAPI 2016 (Provincial Governance and Public Administration Performance Index; face-to-face,
##national multi-stage probability sample; interviewers showed the pair on a tablet): one pair
##of hypothetical National Assembly candidates per respondent (task = 1), 7 attributes.
##Profiles: the source has one row per respondent x candidate, built by the .do file: form = 2
##holds candidate 1 (d102_*1 columns), form = 1 candidate 2 (d102_*2); so profile = 3 - form.
##The vote (D102 "Which candidate would you vote for?") was recoded by the .do into 1/0 for
##each row. 1,147 of 14,060 respondents answered don't know or refused (codes 888/999, missing in the
##file): their rows are omitted (no outcome). Tasks with an attribute coded -999999 "Not
##selected" (missing in the source) are dropped (20 more respondents), and 6 rows without a
##respondent_id (a block of 6 rows sharing a missing id) are dropped. The respondent_id is the
##.do file's row number of the raw survey (_n), kept as is.
##Question (appendix H, English master): "Now imagine two candidates for the National Assembly.
##The first candidate is a [age] year old [gender] candidate from [province] ... This candidate
##is a [nomination] [party] with a career background [career]. [policy]. The second candidate
##... Which candidate would you vote for? Please feel free to look at the candidate's profile on
##the screen." Options Candidate 1 / Candidate 2 (DK/RA recorded but not offered). choice = 1
##for the chosen candidate; forced in design, no opt-out.
##Attributes, .dta value labels as stored (Vietnamese for gender and province, English for the
##rest; respondents saw Vietnamese): attr_age 39 / 59; attr_gender Nam (male) / Nữ (female);
##attr_province: the candidate's home province, which by design is either the respondent's own
##province or Hà Nội (article Table 3 "[home province/Hanoi]"; the .do's `home` flag), except
##3 rows of 2 respondents whose candidate province is neither (kept as stored);
##attr_nomination Self-nominated / Nominated; attr_party Party Member / Non-Party Member; attr_job
##Fatherland Front / Business Person; attr_policy one of four sentences "In the meeting with
##voters, this candidate emphasized the need for increased openness to foreign trade." (/
##anti-poverty assistance / economic growth / improved environmental protection). Education
##and experience were added only in 2017/2018. Attribute order fixed (appendix H grid).
##Covariates (.dta value labels; [DK]/[RA] -> NA): cov_gender (a001 Male/Female), cov_age (a002,
##years), cov_ethnicity (a005), cov_education (a006), cov_economic_situation (a011, own family
##today), cov_province (tentinh, respondent's province), cov_area (khuvuc Urban/Rural),
##cov_party_member (a016_opt1, member of the Party 0/1), cov_voted_2016 (d101da, cast own vote
##for National Assembly deputies in May 2016, 0/1), cov_survey_weight (PSW_psweight, the pweight
##in the authors' svyset, which further post-stratifies by province population: kept as
##cov_province_population), cov_psu (PSW_PSU) and cov_strata (PSW_STRATA), the first-stage
##design identifiers of that svyset.
##Dropped: district/commune/village names and codes (fine-grained location), interviewer
##respondent code (idcode0), free-text answers (occupation, other ethnicity, important
##problems d306*), all other PAPI modules, and the .do's derived dummies and match flags.
##N: 12,893 respondents / 25,786 rows here; the article reports 25,684 observations in its first
##2016 model (Table 5 col. 1) and 13,490 respondents exposed to the conjoint (Table 4). Not
##reconciled (the authors' svy models drop rows with missing design or control variables).
##Spot check: unweighted LPM of choice on all attributes gives Party Member +0.143 (article
##Table 5 col. 1, survey-weighted: 0.142).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "PAPI_Conjoint_2016.dta")))
s <- s[!is.na(respondent_id)]
stopifnot(s[, .N, respondent_id][, all(N == 2)], s[, all(sort(form) == 1:2), respondent_id]$V1)
lab <- function(x) { y <- as.character(as_factor(x, levels = "labels")); y[zap_labels(x) %in% c(-999999, 888, 999)] <- NA; y }
num <- function(x) { y <- as.numeric(zap_labels(x)); y[y %in% c(888, 999, -999999)] <- NA; y }
d <- s[, .(id = as.integer(respondent_id), task = 1L, profile = 3L - as.integer(form), choice = as.integer(vote),
           attr_age = lab(age), attr_gender = lab(sex), attr_province = lab(home_province),
           attr_nomination = lab(nomination), attr_party = lab(party_status), attr_job = lab(job),
           attr_policy = lab(policy_priority),
           cov_gender = c(Male = "male", Female = "female")[lab(a001)], cov_age = num(a002),
           cov_ethnicity = lab(a005), cov_education = lab(a006), cov_economic_situation = lab(a011),
           cov_province = tentinh, cov_area = lab(khuvuc), cov_party_member = as.integer(zap_labels(a016_opt1)),
           cov_voted_2016 = num(d101da), cov_survey_weight = as.numeric(PSW_psweight),
           cov_province_population = as.numeric(PSW_province_population),
           cov_psu = as.numeric(PSW_PSU), cov_strata = as.numeric(PSW_STRATA))]
attrs <- grep("^attr_", names(d), value = TRUE)
bad <- d[, .(b = any(is.na(.SD))), id, .SDcols = attrs][b == TRUE, id]
d <- d[!id %in% bad & !is.na(choice)]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)])
stopifnot(d[, uniqueN(attr_policy)] == 4, d[, uniqueN(attr_job)] == 2, all(d$attr_gender %in% c("Nam", "Nữ")))
hp <- zap_labels(s$home_province); stopifnot(sum(!(hp == zap_labels(s$tinh) | hp == 1 | hp == -999999)) == 3)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "malesky_2020_vietnam_na_2016.csv"))
