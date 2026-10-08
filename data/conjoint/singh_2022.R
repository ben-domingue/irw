##Candidate-choice conjoint (Argentina, 2019 general election) from
##Singh, S. P. (2022). Does compulsory voting affect how voters choose? A test using a
##combined conjoint and regression discontinuity analysis. Comparative Political Studies,
##55(12), 2119-2143. https://doi.org/10.1177/00104140211066219
##Replication data: Harvard Dataverse doi:10.7910/DVN/65OW82, CC0 1.0, no restricted files,
##no terms. Files read: Argentina_2019_Gen_Elec_Survey_Conjoint_CPS.dta (one row per
##respondent x candidate), Argentina_2019_Gen_Elec_Survey_CPS.dta (respondent covariates),
##Codebook.pdf; the authors' do-files read as text. The article (paywalled) and its Supporting
##Information were NOT read, so question wording, Spanish display text, sample provider and
##fielding dates are not documented here.
##Usage: Rscript singh_2022.R <raw dir> <output dir>
##
##2,042 Argentine respondents surveyed after the 27 October 2019 general election, sampled
##around the age-18 and age-70 thresholds of compulsory voting (the RD design: ages about
##16-20 and 68-72, so the sample includes 16- and 17-year-olds, who may vote in Argentina).
##Each made 5 choices between two candidate profiles (codebook: "ten randomly drawn candidate
##profiles shown to each respondent (two per each of five tasks)").
##task = task (recorded); profile = 1 for the odd candidate number, 2 for the even one in each
##  task (candidate 2t-1 / 2t; the authors' SI do-file codes the even one as "the second
##  profile in each task").
##attr_ text = the Stata value labels / codebook labels, which are ENGLISH (the survey was
##  fielded in Argentina, presumably in Spanish; the displayed Spanish text is not deposited):
##  deficit, IMF, abortion opinions ("No Opinion" + positions), experience ("No Experience",
##  "5 Years".."15 Years"), family ("No Information", married/single), gender (Male/Female),
##  favorite music ("No Favorite Type of Music", Jazz/Pop/Rock/Tango), favorite food ("No Favorite
##  Type of Food", Asado/Empanadas/Provoleta). Whether the "No Opinion"/"No Information"/"No
##  Favorite..." levels were displayed as text or the row was left blank is NOT documented; they
##  are stored as the labelled text (not "(not shown)").
##choice: vote_choice_conjoint. The codebook says 0 = voted for the candidate, 1 = did not, but
##  the variable label is "Respondent's vote within task", the authors regress it on attributes
##  as the vote, and the data agree with 1 = chosen (No Experience 0.44 vs 0.50-0.53 for 5-15
##  years); 1 = chosen is used. Exactly one chosen per task (checked): no opt-out observed.
##  Question wording unknown (paraphrase in the design record).
##Covariates (codebook mappings): cov_age = completed years on 27 Oct 2019, computed here from
##  days_over_18_election (the deposited days-past-18 count, which pins the exact date of birth;
##  the day counts themselves are NOT kept, see PII note), cov_gender (female 1 -> female, 0 ->
##  male), cov_education (educ 1-10 -> codebook text), cov_political_interest (pol_int 1-4 ->
##  none/little/some/a lot), cov_ideology (0 far left - 10 far right, numeric),
##  cov_income (income 1-18 -> codebook peso brackets; the codebook's "$4,001 - $,8000" typo
##  written as "$4,001 - $8,000"), cov_voted (valid_blank_or_null_vote: 1 = reported voting
##  valid, blank or null, 0 = reported not voting).
##Dropped: respondent ids (long hashed panel tokens; re-keyed to integers), days_over_18 /
##  days_over_70 (exact date of birth, Ben's 10-05 no-DOB ruling), the derived age-threshold
##  dummies.
##Randomization: "randomly drawn" (codebook); no restriction or probability rule documented.
##N = 2,042 respondents, 20,420 profile rows (no comparison with the article, not read).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(file.path(raw, "Argentina_2019_Gen_Elec_Survey_Conjoint_CPS.dta")))
s <- as.data.table(read_dta(file.path(raw, "Argentina_2019_Gen_Elec_Survey_CPS.dta")))
stopifnot(uniqueN(s$respondent) == nrow(s), all(x$candidate %in% c(2 * x$task - 1, 2 * x$task)))
x[, `:=`(task = as.integer(task), profile = as.integer(2 - candidate %% 2))]
stopifnot(x[, .N, .(respondent, task)][, all(N == 2)], x[, sum(vote_choice_conjoint), .(respondent, task)][, all(V1 == 1)])
lab <- function(v) as.character(as_factor(v, levels = "labels"))
d <- x[, .(respondent, task, profile, choice = as.integer(vote_choice_conjoint),
           attr_deficit = lab(at_encoded_opinion_deficit), attr_imf = lab(at_encoded_opinion_IMF),
           attr_abortion = lab(at_encoded_opinion_abortion), attr_experience = lab(at_encoded_experience),
           attr_family = lab(at_encoded_family), attr_gender = lab(at_encoded_gender),
           attr_music = lab(at_encoded_favorite_music), attr_food = lab(at_encoded_favorite_food))]
stopifnot(!anyNA(d))
## covariates
el <- as.Date("2019-10-27")
dob18 <- el - s$days_over_18_election                       # 18th birthday
bd <- as.POSIXlt(dob18); y18 <- bd$year + 1900
age <- (as.POSIXlt(el)$year + 1900) - (y18 - 18) - as.integer(format(el, "%m%d") < format(dob18, "%m%d"))
edu <- c("No education", "Incomplete primary", "Complete primary", "Incomplete secondary", "Complete secondary",
         "Incomplete tertiary", "Complete tertiary", "Incomplete university", "Complete university",
         "Incomplete or complete postgraduate")
inc <- c("No income", "Less than $4,000", "$4,001 - $8,000", "$8,001 - $12,000", "$12,001 - $16,000",
         "$16,001 - $20,000", "$20,001 - $24,000", "$24,001 - $28,000", "$28,001 - $32,000", "$32,001 - $36,000",
         "$36,001 - $40,000", "$40,001 - $44,000", "$44,001 - $48,000", "$48,001 - $52,000", "$52,001 - $56,000",
         "$56,001 - $60,000", "$60,001 - $64,000", "More than $64,000")
cv <- s[, .(respondent, cov_age = as.integer(age),
            cov_gender = c("male", "female")[as.integer(female) + 1L],
            cov_education = edu[as.integer(educ)],
            cov_political_interest = c("none", "little", "some", "a lot")[as.integer(pol_int)],
            cov_ideology = as.integer(ideo), cov_income = inc[as.integer(income)],
            cov_voted = as.integer(valid_blank_or_null_vote))]
stopifnot(all(cv$cov_age %between% c(14, 80)))
d <- merge(d, cv, by = "respondent", all.x = TRUE)
stopifnot(nrow(d) == nrow(x))
ids <- sort(unique(d$respondent)); d[, id := match(respondent, ids)][, respondent := NULL]
setcolorder(d, "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "singh_2022_compulsory_voting.csv"))
