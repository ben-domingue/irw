##Quota-politician factorial vignette (Morocco) from
##Barnett, C., Blackman, A., & Shalaby, M. (2025). Competent legislators or mere pawns? Experimental
##evidence of attitudes toward gender quota politicians. Political Science Research and Methods,
##13(4). https://doi.org/10.1017/psrm.2024.69
##Replication data: Harvard Dataverse doi:10.7910/DVN/HXLRBY, CC0 1.0, no restricted files, no terms.
##File read: quota_experiment.rds (927 respondents, one row each). Read as text only: Gender Quotas
##Codebook.xlsx (tab quota_experiment), README.pdf, 01_setup.R, 02_main_manuscript.R. Vignette text
##from the article (CC BY 4.0, "Experimental design"); outcome wording from the pre-registration
##(supplementary file S2049847024000694sup001.pdf, AsPredicted #144381); manipulation-check codes
##from the online appendix (sup002, Table A.5).
##Usage: Rscript barnett_2025_quota.R <raw dir> <output dir>
##
##Face-to-face, nationally representative survey of Moroccan adults by One to One Polling and
##Research, August-October 2023; 927 of the 1,800 respondents were randomly assigned the survey
##version with this experiment (the other version is not this table; barnett_2025_politicians_morocco
##is a different deposit and article). One vignette per respondent (task = 1, profile = 1):
##  "A [man elected as an MP in the district elections]/[woman elected as an MP in the district
##  elections]/[woman elected as an MP through the gender quota] during the 2021 elections, has been
##  successful in getting a new proposal approved to create new jobs in Morocco. [He/She worked on
##  this proposal with other members of his/her party.]/[He/She worked on this proposal with members
##  of other parties.] In a recent television interview, [he/she] stressed the importance of the
##  development of work prospects in the field of the economy of care, ..."
##Two randomized factors, stored as the article's English text (the interview language is not
##documented; the pawn item used a Moroccan-dialect term):
##  attr_politician (source vignette_election; codebook maps Man/general, Woman/general, Woman/quota
##    to the three texts; the article's wording "district elections" is used, the codebook says
##    "general election"): probabilities 25% / 25% / 50% (article: the quota woman arm is double);
##    there is no quota-man arm by design.
##  attr_collaboration (vignette_work: "With his/her party" / "With another party"), equal
##    probability, randomized independently of attr_politician (article).
##  The derived vignette_gender / vignette_mode columns are dropped (they recode attr_politician).
##Outcomes, 1-10, stored raw; endpoint labels not documented (pre-registration wording):
##  rating_competence: "If you had to rate this politician on a scale from 1-10, how would you rate
##    him/her in terms of competence?"
##  rating_pawnlike: "... how would you rate whether this politician is a pawn of party elites?"
##  rating_cooperation: "... how would you rate whether this politician is cooperative?"
##"Don't know"/refused are NA (21, 34, 25 respondents; appendix 7.1). Respondents with all three
##missing are dropped (rows with no outcome).
##Covariates: cov_age (years), cov_gender (RespGender Female/Male -> female/male), cov_education
##(the codebook's four categories, from the one-hot edu_* columns: "No formal education",
##"Primary or preparatory", "Secondary", "BA or higher"; 9 respondents with none set are NA),
##cov_vote_2021 (from voted_parl21 and the one-hot voted_* party columns, codebook party
##abbreviations PJD, RNI, Istiqlal, USFP, PAM, MP, UC, PPS, MDS, "Other party", "Did not vote";
##don't know/refused (one merged code in the source) and missing are NA; a vote, not party ID),
##cov_urban, cov_employed, cov_unemployed, cov_in_laborforce, cov_married_widowed (0/1 per
##codebook), cov_ses_subj (1-4), cov_religiosity (1 not religious .. 3 very religious),
##cov_govt_satis (1-10), the 13 sexism/gender-attitude items bs_*, hs_*, ms_* (non-reversed), women_*
##(1 strongly disagree .. 4 strongly agree), cov_trust_in_elections ("High" = agrees elections are
##free and fair, "Low" = disagrees; source factor), cov_manip_correct (post-vignette check "was this
##politician elected via a quota?": 1 correct, 0 incorrect, 9 don't know or refused; appendix Table
##A.5 counts 662/206/59 match). Dropped as derived: female, *_rev items, the indices
##hostile_sexism/modern_sexism/patriarchal and their High/Low factors, value_clientelism and
##Clientelism, govt_satisfaction, Voted, straightliner. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "quota_experiment.rds")))
stopifnot(nrow(s) == 927L, !anyDuplicated(s$QID))
pol <- c(`Man/general` = "man elected as an MP in the district elections",
         `Woman/general` = "woman elected as an MP in the district elections",
         `Woman/quota` = "woman elected as an MP through the gender quota")
col <- c(`With his/her party` = "He/She worked on this proposal with other members of his/her party.",
         `With another party` = "He/She worked on this proposal with members of other parties.")
stopifnot(all(as.character(s$vignette_election) %in% names(pol)), all(as.character(s$vignette_work) %in% names(col)))
edu <- s[, .(edu_no_formal, edu_elem_prep, edu_second, edu_above_second)]
stopifnot(all(rowSums(edu) <= 1))
edu_txt <- c("No formal education", "Primary or preparatory", "Secondary", "BA or higher")[apply(edu, 1, function(r) if (any(r == 1)) which(r == 1) else NA)]
pv <- c(voted_pjd = "PJD", voted_rni = "RNI", voted_istiqlal = "Istiqlal", voted_usfp = "USFP", voted_pam = "PAM",
        voted_mp = "MP", voted_uc = "UC", voted_pps = "PPS", voted_mds = "MDS", voted_other = "Other party", voted_dk_refuse = NA)
vm <- as.matrix(s[, names(pv), with = FALSE])
stopifnot(all(rowSums(vm[s$voted_parl21 %in% 1, , drop = FALSE]) == 1), all(is.na(rowSums(vm[!s$voted_parl21 %in% 1, , drop = FALSE])) | rowSums(vm[!s$voted_parl21 %in% 1, , drop = FALSE]) == 0))
vote <- rep(NA_character_, nrow(s))
vote[s$voted_parl21 %in% 0] <- "Did not vote"
i <- which(s$voted_parl21 %in% 1); vote[i] <- unname(pv[apply(vm[i, , drop = FALSE], 1, function(r) which(r == 1))])
d <- s[, .(id = as.integer(QID), task = 1L, profile = 1L,
           rating_competence = as.integer(vignette_competence), rating_pawnlike = as.integer(vignette_pawnlike),
           rating_cooperation = as.integer(vignette_cooperation),
           attr_politician = unname(pol[as.character(vignette_election)]), attr_collaboration = unname(col[as.character(vignette_work)]),
           cov_age = as.integer(age), cov_gender = c(Female = "female", Male = "male")[as.character(RespGender)],
           cov_education = edu_txt, cov_vote_2021 = vote,
           cov_urban = as.integer(urban), cov_employed = as.integer(employed), cov_unemployed = as.integer(unemployed),
           cov_in_laborforce = as.integer(in_laborforce), cov_married_widowed = as.integer(married_widowed),
           cov_ses_subj = as.integer(ses_subj), cov_religiosity = as.integer(religiosity), cov_govt_satis = as.integer(govt_satis))]
items <- c("bs_cherish", "bs_moral", "hs_offended", "hs_work", "hs_control", "ms_denial_1", "ms_denial_2", "ms_denial_3",
           "ms_antagonism", "ms_resentment", "women_leaders", "women_jobs", "women_decision")
for (v in items) d[, paste0("cov_", v) := as.integer(s[[v]])]
d[, cov_trust_in_elections := as.character(s$trust_in_elections)]
d[, cov_manip_correct := as.integer(s$manip_correct)]
stopifnot(all(d$cov_manip_correct %in% c(0L, 1L, 9L)), d[, table(cov_manip_correct)][["1"]] == 662L)
d <- d[!(is.na(rating_competence) & is.na(rating_pawnlike) & is.na(rating_cooperation))]
for (v in c("rating_competence", "rating_pawnlike", "rating_cooperation")) stopifnot(all(d[[v]] %in% c(1:10, NA)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "barnett_2025_quota_politicians.csv"))
