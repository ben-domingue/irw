##Candidate-gender conjoint (Morocco, face-to-face) from
##Barnett, C., Blackman, A., & Shalaby, M. (2026). Misperceptions of male bias against female
##candidates: An obstacle to women's political representation? Political Behavior (forthcoming;
##article DOI not found in Crossref on 2026-10-08).
##Replication data: Harvard Dataverse doi:10.7910/DVN/ALYII5, CC BY-NC 4.0 (Ben ruled 10-07 that
##NC is acceptable for conj). No restricted files, no terms. Files read: candidates_conjoint_long.rds
##(authors' profile-level file) and Misperceptions Codebook.xlsx (sheet candidates_conjoint_long);
##000_README.pdf, 01_setup.R and 02_main_manuscript.R read as text (not run).
##Usage: Rscript barnett_2026.R <dir holding the rds and codebook> <output dir>
##
##873 Moroccan respondents of a 2023 face-to-face survey (n = 1,800; the subset that completed this
##conjoint, per 01_setup.R), 4 rounds x 2 candidate profiles, 7 attributes: Gender, Party
##(Istiqlal, PJD, USFP, RNI), Education (Secondary, University, Masters), Character (Consensus,
##Compassionate, Ambitious, Assertive), Connected (Less/More Connected), Previous (No/Has
##Experience), Family (Unmarried, Married Young, Married Old). Level text is the authors' English
##labels (the interview language is not stated in the deposit). task = round; the file's profile
##runs 1-8 within respondent, so profile = 1 for odd and 2 for even profile numbers (recorded).
##Outcomes (codebook wording, paraphrased into questions):
##  rating: how the respondent rated the candidate, 1 (least competent) to 10 (most competent).
##  choice: prefer_self, does the respondent prefer this candidate vs the paired one.
##  choice_men: would men in the respondent's community prefer this candidate.
##  choice_women: would women in the community prefer this candidate.
##  Each pick is one per task where answered; NA on both profiles where not answered (302, 110 and
##  92 of 3,492 tasks); 18 profiles lack a rating. No explicit opt-out is documented.
##trial_outcome_order_1 / _2: the authors' randomized question order (self vs others first; men
##vs women first). The authors' analyses keep all respondents; cov_manip_check_wrong and
##cov_straightliner are their flags (used in robustness checks).
##Covariates (codebook): cov_age, cov_gender (RespGender Female/Male), cov_education_level (from
##the authors' four exclusive education dummies: "No formal education", "Primary or preparatory",
##"Secondary", "BA or higher"; NA for 6 respondents with none), cov_employed, cov_in_laborforce, cov_urban, cov_voted_parl21,
##cov_married_widowed (0/1), cov_ses_subj (1-4), cov_religiosity (1 Not religious, 2 Religious,
##3 Very religious), cov_govt_satis (1-10), cov_enumerator_gender (Male/Female), the attitude items
##cov_bs_cherish, cov_bs_moral, cov_hs_offended, cov_hs_work, cov_hs_control, cov_ms_denial_1/2/3,
##cov_ms_antagonism, cov_ms_resentment, cov_women_leaders, cov_women_jobs, cov_women_decision
##(1 Strongly disagree - 4 Strongly agree), and the perceived-norm estimates cov_hs_perceived,
##cov_ms_perceived, cov_bs_perceived, cov_pat_perceived (out of 100). Dropped: derived indices
##and median splits (hostile_sexism, Hostile, ... Sensitive, Clientelism), reversed items,
##trust_in_elections (median split only), the voted_* dummies, unemployed, enum_fem, Round.
##No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "candidates_conjoint_long.rds")))
stopifnot(uniqueN(x$QID) == 873, x[, .N, QID][, all(N == 8)], all(x$profile == 2 * x$round - (x$profile %% 2)))
x[, id := as.integer(QID)][, task := as.integer(round)][, p := 2L - as.integer(profile) %% 2L]
for (v in c("prefer_self", "prefer_men", "prefer_women"))
  stopifnot(x[, .(s = sum(get(v)), n = sum(is.na(get(v)))), .(id, task)][, all((n == 0 & s == 1) | n == 2)])
edu <- x[, edu_no_formal + edu_elem_prep + edu_second + edu_above_second]
stopifnot(all(edu <= 1, na.rm = TRUE))  # 6 respondents have none of the four (NA)
ch <- function(f) as.character(f)
d <- x[, .(id, task, profile = p, choice = as.integer(prefer_self), choice_men = as.integer(prefer_men),
           choice_women = as.integer(prefer_women), rating = as.integer(rating),
           attr_gender = ch(Gender), attr_party = ch(Party), attr_education = ch(Education), attr_character = ch(Character),
           attr_connected = ch(Connected), attr_previous = ch(Previous), attr_family = ch(Family),
           trial_outcome_order_1 = outcomes_order_1, trial_outcome_order_2 = outcomes_order_2,
           cov_age = age, cov_gender = c(Female = "female", Male = "male")[ch(RespGender)],
           cov_education_level = fcase(edu_no_formal == 1, "No formal education", edu_elem_prep == 1, "Primary or preparatory",
                                       edu_second == 1, "Secondary", edu_above_second == 1, "BA or higher"),
           cov_employed = employed, cov_in_laborforce = in_laborforce, cov_urban = urban, cov_voted_parl21 = voted_parl21,
           cov_married_widowed = married_widowed, cov_ses_subj = ses_subj, cov_religiosity = religiosity,
           cov_govt_satis = govt_satis, cov_enumerator_gender = ch(enum_gender),
           cov_bs_cherish = bs_cherish, cov_bs_moral = bs_moral, cov_hs_offended = hs_offended, cov_hs_work = hs_work,
           cov_hs_control = hs_control, cov_ms_denial_1 = ms_denial_1, cov_ms_denial_2 = ms_denial_2, cov_ms_denial_3 = ms_denial_3,
           cov_ms_antagonism = ms_antagonism, cov_ms_resentment = ms_resentment, cov_women_leaders = women_leaders,
           cov_women_jobs = women_jobs, cov_women_decision = women_decision, cov_hs_perceived = hs_perceived,
           cov_ms_perceived = ms_perceived, cov_bs_perceived = bs_perceived, cov_pat_perceived = pat_perceived,
           cov_manip_check_wrong = manip_check_candidates_wrong, cov_straightliner = straightliner)]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
d <- d[!(is.na(choice) & is.na(choice_men) & is.na(choice_women) & is.na(rating))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "barnett_2026_morocco_candidates.csv"))
