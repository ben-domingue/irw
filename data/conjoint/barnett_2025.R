##Politician (MP) profile conjoint (Morocco) from
##Barnett, C., Blackman, A., & Shalaby, M. (2025). Gender stereotypes in autocracies: Experimental
##evidence from Morocco. The Journal of Politics, 87(3), 995-1011. https://doi.org/10.1086/733000
##Replication data: Harvard Dataverse doi:10.7910/DVN/POQR6F, licence CC BY-NC 4.0 (Ben ruled 10-07
##that NC is acceptable for irw_conjoint; the derived table carries CC BY-NC 4.0). File read:
##politicians_conjoint_long.rds (datafile 10152226). Read as text only: README.pdf,
##"Gender Stereotypes Codebook.xlsx" (tab politicians_conjoint_long), 01_setup.R,
##02_main_manuscript.R, 03_summary_stats.R. The article itself was not accessible (paywalled).
##Usage: Rscript barnett_2025.R <dir holding politicians_conjoint_long.rds> <output dir>
##
##927 Moroccan respondents (README: the conjoint dataset has 5,562 rows, 6 per respondent; the full
##survey had 1,800 respondents, summary_stats_1800.rds; the deposit does not say how the 927 were
##selected) each evaluated 6 politician profiles one at a time: single-profile design, task = the
##codebook's `profile` (1-6, "the conjoint profile (1-6) for a given respondent"), profile = 1.
##7 attributes, text = the authors' factor levels (English short labels; the display language and
##wording are not in the deposit): gender (Male/Female), party (No party mentioned/PJD/USFP/RNI),
##education (Secondary/University/Masters), character (Consensus/Compassionate/Ambitious/Assertive),
##productivity (Less/More Productive), priorities (Natl Health/Natl Jobs/Local Health/Local Jobs),
##family (Unmarried/Married Young/Married Grown; the codebook writes "Married Old").
##No randomization restriction or level probability is documented; shares are near-uniform.
##Outcomes (wording not deposited; codebook descriptions):
##  choice = reelect: "would the respondent reelect the politician in the conjoint profile?"
##    1 = Yes, 0 = No. A single-profile accept/reject question, so opt_out = yes (README standard).
##    55 rows missing.
##  rating_competence = competence: "how the respondent rated the competence of the politician",
##    1 (least competent) - 10 (most competent). 31 rows missing.
##Rows with neither outcome are omitted. Where only one outcome is missing it stays NA.
##Dropped: QID (re-keyed to integers in source order); the authors' derived variables (female dummy
##duplicate, labour-force dummies, education dummies other than as recombined below, hostile/modern/
##patriarchal indices and their splits, reverse-coded items, clientelism and Voted factors,
##vote-choice dummies). No free text or platform ids in the file.
##Covariates (codes and labels from the codebook): cov_age (years), cov_gender (RespGender:
##Female -> female, Male -> male), cov_education_group (from the authors' mutually exclusive
##education dummies: "No formal education", "Primary or preparatory", "Secondary", "BA or higher";
##the original answer categories are not deposited, so not the reserved cov_education; 9 respondents
##with all four dummies 0 are NA),
##cov_urban (1 urban/0 rural), cov_voted_2021 (1/0), cov_married_widowed (1/0), cov_employed (1/0),
##cov_ses_subjective (ses_subj answer text from the codebook), cov_religiosity (Not religious/Religious/
##Very religious), cov_govt_satisfaction (1-10), the attitude items as codes 1 = Strongly disagree ...
##4 = Strongly agree: cov_bs_cherish, cov_bs_moral, cov_hs_offended, cov_hs_work, cov_hs_control,
##cov_ms_denial_1, cov_ms_denial_2, cov_ms_denial_3, cov_ms_antagonism, cov_ms_resentment,
##cov_women_leaders, cov_women_jobs, cov_women_decision (item wording in the codebook);
##cov_value_clientelism (1/0, codebook definition), cov_manip_check_1_wrong, cov_manip_check_2_wrong
##(1 = answered the manipulation check incorrectly), cov_straightliner (1/0).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "politicians_conjoint_long.rds")))
stopifnot(nrow(s) == 5562, uniqueN(s$QID) == 927, s[, .N, QID][, all(N == 6)], s[, uniqueN(profile), QID][, all(V1 == 6)])
s[, id := match(QID, unique(QID))]
edu <- s[, fcase(edu_no_formal == 1, "No formal education", edu_elem_prep == 1, "Primary or preparatory",
                 edu_second == 1, "Secondary", edu_above_second == 1, "BA or higher", default = NA_character_)]
stopifnot(s[, all(is.na(edu_no_formal) | (edu_no_formal + edu_elem_prep + edu_second + edu_above_second) <= 1)])
ses <- c("Our net household income does not cover our expenses; we face significant difficulties.",
         "Our net household income does not cover our expenses; we face some difficulties.",
         "Our net household income covers our expenses without notable difficulties.",
         "Our net household income covers our expenses and we are able to save.")
rel <- c("Not religious", "Religious", "Very religious")
d <- s[, .(id, task = as.integer(profile), profile = 1L, choice = as.integer(reelect), rating_competence = as.integer(competence),
  attr_gender = as.character(Gender), attr_party = as.character(Party), attr_education = as.character(Education),
  attr_character = as.character(Character), attr_productivity = as.character(Productivity),
  attr_priorities = as.character(Priorities), attr_family = as.character(Family),
  cov_age = as.integer(age), cov_gender = c(Female = "female", Male = "male")[as.character(RespGender)],
  cov_education_group = edu, cov_urban = as.integer(urban), cov_voted_2021 = as.integer(voted_parl21),
  cov_married_widowed = as.integer(married_widowed), cov_employed = as.integer(employed),
  cov_ses_subjective = ses[ses_subj], cov_religiosity = rel[religiosity], cov_govt_satisfaction = as.integer(govt_satis),
  cov_bs_cherish = bs_cherish, cov_bs_moral = bs_moral, cov_hs_offended = hs_offended, cov_hs_work = hs_work,
  cov_hs_control = hs_control, cov_ms_denial_1 = ms_denial_1, cov_ms_denial_2 = ms_denial_2, cov_ms_denial_3 = ms_denial_3,
  cov_ms_antagonism = ms_antagonism, cov_ms_resentment = ms_resentment, cov_women_leaders = women_leaders,
  cov_women_jobs = women_jobs, cov_women_decision = women_decision, cov_value_clientelism = as.integer(value_clientelism),
  cov_manip_check_1_wrong = as.integer(manip_check_1_wrong), cov_manip_check_2_wrong = as.integer(manip_check_2_wrong),
  cov_straightliner = as.integer(straightliner))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), all(d$rating_competence %in% c(1:10, NA)),
          all(s$ses_subj %in% c(1:4, NA)), all(s$religiosity %in% c(1:3, NA)))
d <- d[!(is.na(choice) & is.na(rating_competence))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "barnett_2025_politicians_morocco.csv"))
