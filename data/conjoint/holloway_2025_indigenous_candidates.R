##Photographed prospective-candidate experiment (Australia), 4 ethnicity/skin-tone groups x 2 genders, from
##Holloway, J., McDonnell, D., & Evans, M. (2025). The Inverted Hierarchy: How Public Bias Can Favor
##Potential Indigenous Candidates. Perspectives on Politics. https://doi.org/10.1017/S1537592725102107
##Replication data: Harvard Dataverse doi:10.7910/DVN/ATSAKJ, CC0 1.0. File read: Survey 2.sav
##(Dataverse "original format" download); readme.rtf read for the file description.
##Usage: Rscript holloway_2025_indigenous_candidates.R <dir holding Survey 2.sav saved as s2.sav> <output dir>
##
##3,914 Australian citizens (nationally representative online sample; the readme says ~4,000). Each respondent saw ONE
##photographed prospective candidate (with an identical biography, per the Dataverse description) drawn from 8 cells:
##{Chinese-Australian, Indigenous (dark skinned), Indigenous (light skinned), White} x {man, woman} (variable
##Category, "Candidate Shown", value labels). One task, one profile per respondent (task = profile = 1; id = the
##deposit's internal respondent number). Each cell is a single photograph, so ethnicity/gender are confounded with
##the individual photo; presentation = image. Roughly 490 respondents per cell. Attributes: attr_ethnicity
##(Chinese-Australian / Indigenous (dark skinned) / Indigenous (light skinned) / White), attr_gender (Man / Woman),
##from the Category value labels.
##Outcomes (ratings, stored raw, higher = more of the trait): rating_<trait> = Q13 "Candidate trait perceptions",
##8 traits (intelligent, competent, hardworking, experienced, likeable, trustworthy, compassionate, approachable),
##5-point agree scale 1 Strongly disagree ... 5 Strongly agree (value labels); rating_attractive = Q25 attractiveness
##of the candidate, 1-9 (1 Extremely unattractive, 5 Neither, 9 Extremely attractive). The deposit has a "Scale order
##shown" variable (Normal/Reversed); the file stores the trait ratings with the labelled coding above, so it is kept
##as trial_scale_order for reference (whether the values were un-reversed by the authors is not stated).
##Question wording of Q13/Q25 is in the online appendix (Appendix C), not deposited: design records give a paraphrase.
##Survey 1.sav (1,201 respondents rating 24 photographs to SELECT the stimuli) is a stimulus pre-test, not a
##randomized-profile experiment, and is not built.
##Covariates: cov_gender (Q26: Woman = female, Man = male, Non-binary/Other = other), cov_age (Q1Exact, years),
##cov_education (Q34 value-label text), cov_party_id (Q6 value-label text; "Another party (specify)" kept as such,
##free text dropped), No survey weight. Dropped: derived indices (Comp_ind, Char_ind), dummies,
##interactions, free-text party fields, state, income, religion, geography.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_sav(file.path(raw, "s2.sav")))
stopifnot(nrow(s) == 3914, !anyDuplicated(s$sys_RespNum))
cat8 <- as.character(as_factor(s$Category, levels = "labels"))
eth <- c("Chinese-Australian man" = "Chinese-Australian", "Chinese-Australian woman" = "Chinese-Australian",
         "Indigenous (dark skinned) man" = "Indigenous (dark skinned)", "Indigenous (dark skinned) woman" = "Indigenous (dark skinned)",
         "Indigenous (light skinned) man" = "Indigenous (light skinned)", "Indigenous (light skinned) woman" = "Indigenous (light skinned)",
         "White man" = "White", "White woman" = "White")
stopifnot(all(cat8 %in% names(eth)))
d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L,
  rating_intelligent = as.integer(s$Q13.1), rating_competent = as.integer(s$Q13.2), rating_hardworking = as.integer(s$Q13.3),
  rating_experienced = as.integer(s$Q13.4), rating_likeable = as.integer(s$Q13.5), rating_trustworthy = as.integer(s$Q13.6),
  rating_compassionate = as.integer(s$Q13.7), rating_approachable = as.integer(s$Q13.8), rating_attractive = as.integer(s$Q25_r1),
  attr_ethnicity = unname(eth[cat8]), attr_gender = ifelse(grepl("woman$", cat8), "Woman", "Man"),
  trial_scale_order = as.character(as_factor(s$Scale, levels = "labels")),
  cov_gender = c("female", "male", "other", "other")[as.integer(s$Q26)], cov_age = as.integer(s$Q1Exact),
  cov_education = as.character(as_factor(s$Q34, levels = "labels")), cov_party_id = as.character(as_factor(s$Q6, levels = "labels")))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "holloway_2025_indigenous_candidates.csv"))
