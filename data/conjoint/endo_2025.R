##Candidate-ambition x candidate-gender vignette experiment (Japan, Lucid) from
##Endo, Y., & Ono, Y. (2025). Emphasizing or downplaying political ambitions: Exploring the role of
##candidate gender in shaping voter perceptions. Electoral Studies, 98, 103004.
##https://doi.org/10.1016/j.electstud.2025.103004
##Replication data: Harvard Dataverse doi:10.7910/DVN/C8ECQA, CC0 1.0. File read (from replication.zip):
##replication/data/data_endo_ono.csv. Also read as text, not run: coodbook.pdf, readme.txt,
##main_analysis.R. Vignette text and outcome descriptions from the working paper (Endo & Ono, "Unveiling or
##concealing aspirations", RIETI DP 23-E-074, 2023, Research Design section; English translation of the
##articles, Japanese originals shown there only as images).
##Usage: Rscript endo_2025.R <dir holding data_endo_ono.csv> <output dir>
##
##Factorial vignette (2 x 2, between respondents): one short newspaper-style article about a hypothetical
##municipal council candidate per respondent (task = 1, profile = 1, both constant). Factors:
##  attr_candidate_gender: "Yasuko Takahashi, female" / "Yasuhiko Takahashi, male" (name and the sentence
##     "... is a female (male), currently 35 years old"); source cand_gender.
##  attr_motivation: the sentence that differs between the two article versions (WP English translation,
##     pronouns set to the candidate's gender). Source treat: choice = ambition-revealing ("has aspired to
##     be a politician since ... a college student ..." + quote "I volunteered to run"), circumstance =
##     ambition-hiding ("was encouraged by ... friends and acquaintances in the local assembly to run ..."
##     + quote "people around me encouraged me"). Codebook: treat = motivation for the candidacy (reveals
##     or hides ambition); main_analysis.R treats `choice` as the treatment.
##Everything else in the article (Waseda graduate, civil servant, age 35, two policy priorities) is fixed.
##Outcomes (wording is a paraphrase: the codebook gives only scales, the WP describes the questions):
##  rating_favorability   = favorability, how favorable an impression of the candidate; 1-4,
##                          4 very favorable .. 1 not favorable at all (codebook).
##  rating_popular        = popular, how popular the candidate would be among the respondent's peers;
##                          1-5, 5 very likely .. 1 highly unlikely (codebook). The WP says both main
##                          questions were 4-point; the deposit and codebook say 5 for this one.
##  rating_trust, rating_decisive, rating_compassion, rating_competent, rating_consensus_building,
##  rating_ambition       = perceived traits of the candidate (manipulation checks), 5-point; the codebook
##                          gives no anchors or direction (WP regressions imply higher = more of the trait;
##                          not stated).
##Respondents: 3,151 rows, one per respondent. The WP (earlier fielding description) reports 3,168
##attention-check passers and 3,867 in its tables; the published article's N was not checked.
##Dropped: ResponseId (Qualtrics ID; ids re-keyed to integers in file order), male and cand_female (dummies),
##Age (coarsened age), PID (undocumented; PID_merge is the codebook's party support).
##Covariates: cov_age (years), cov_gender (resp_gender: "Female Respondent" = female, "Male Respondent" =
##male), cov_region (text), cov_prefecture_code (ken, unlabelled code), cov_education_code (1-7, no labels
##in the deposit), cov_party_id (PID_merge, "Respondent's party support", party abbreviations as stored;
##DK = don't know), cov_ideology_code (1-5, no labels). No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "data_endo_ono.csv"))
stopifnot(!anyDuplicated(x$ResponseId), x$treat %in% c("choice", "circumstance"), x$cand_gender %in% c("female", "male"))
he <- ifelse(x$cand_gender == "female", "she", "he"); his <- ifelse(x$cand_gender == "female", "her", "his")
title <- ifelse(x$cand_gender == "female", "Ms.", "Mr.")
mot <- ifelse(x$treat == "choice",
  paste0(title, " Takahashi has aspired to be a politician since ", he, " was a college student and made various efforts to become a politician, and decided to run for this election. \"I have wanted to become a politician since I was a college student. This time, I volunteered to run for office.\""),
  paste0(title, " Takahashi was encouraged by ", his, " friends and acquaintances in the local assembly to run for office and decided to run for this election. \"I had never thought of becoming a politician before. This time, people around me encouraged me to run for office, so I did.\""))
d <- data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L,
  rating_favorability = x$favorability, rating_popular = x$popular, rating_trust = x$Trust,
  rating_decisive = x$Decisive, rating_compassion = x$Compassion, rating_competent = x$Competent,
  rating_consensus_building = x$Consensus_Building, rating_ambition = x$Ambition,
  attr_candidate_gender = ifelse(x$cand_gender == "female", "Yasuko Takahashi, female", "Yasuhiko Takahashi, male"),
  attr_motivation = mot,
  cov_age = as.integer(x$age),
  cov_gender = c("Female Respondent" = "female", "Male Respondent" = "male")[x$resp_gender],
  cov_region = x$region, cov_prefecture_code = as.integer(x$ken), cov_education_code = as.integer(x$education),
  cov_party_id = x$PID_merge, cov_ideology_code = as.integer(x$ideology))
stopifnot(!anyNA(d$cov_gender), d$rating_favorability %in% 1:4, d$rating_popular %in% 1:5)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "endo_2025_candidate_ambition.csv"))
