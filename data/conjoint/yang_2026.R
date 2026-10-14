##Facebook-post survey experiment on candidate gender and personalization in Taiwan from
##Yang, W.-Y. (2026). Uneven echoes: Gender's divergent influence on candidate personalization and voter response
##in Taiwan. Political Communication, 43(5), 807-827. https://doi.org/10.1080/10584609.2026.2633335
##(article not read: citation from the publisher listing; the figshare item is titled "Uneven Echo").
##Replication data: figshare doi:10.6084/m9.figshare.30928337 (v2), CC BY 4.0. Files read: surveyexperiment.csv
##(saved locally as survey.csv), "surveyexperiment(table3-5).R" (survey.R; read as text, not run),
##table3_groupn.csv (g.csv), Readme.txt. The content-analysis file socialmediapost.csv is observational and not used.
##Usage: Rscript yang_2026.R <dir with survey.csv> <output dir>
##
##1,322 Taiwanese adults aged 20+ (NTU WebSurvey, 10-12 Jan 2024; the Readme says 1,332 valid responses, the
##file and the authors' Table 3 hold 1,322: 258/264/262/263/275 per group). Each respondent saw ONE pair of
##hypothetical candidates on one page, as simulated Facebook posts with AI-generated photos: a woman (Huang
##Hsiu-ying) and a man (Chang Chien-hung), every pair holding one of each gender. The randomized factor is the
##post type, assigned to a candidate by group (Table 3): control = both "Campaign"; group 1 = Campaign woman,
##Personal Viewpoints man; 2 = Campaign man, Personal Viewpoints woman; 3 = Campaign woman, Personal Lives man;
##4 = Campaign man, Personal Lives woman. Attributes: candidate gender, post type. Each task is the pair.
##Profile order: option 1 / option 2 of the vote question as the script documents them (e.g. group 1: 1 =
##Campaign Female, 2 = Personal Viewpoints Male), so profile_source is recorded from that coding.
##  choice  = Vote_*: "If the legislative election were held tomorrow, which candidate would you vote for?"
##            (forced choice between the two, 1/2, no opt-out; no missing).
##  rating  = FeelT_*: "After viewing the above Facebook post excerpt, please rate your impression of the legislative
##            candidate on a scale from 0 to 10. 0 means 'Dislike very much,' 10 means 'Like very much.' On a scale
##            from 0 to 10, how favorably do you view <name>?" (script comments). Higher = more favourable.
##Level text: gender and post type as named in the authors' Table 3 (Female/Male; Campaign, Personal Viewpoints,
##Personal Lives); the actual Chinese post text is not in the deposit.
##Covariates: cov_age (years), cov_survey_weight (weight, the authors' post-stratification weight, mean 1);
##cov_gender_code (sex, 1/2, no codebook) and cov_education_code (edu, 1-6, no codebook) keep their codes;
##age5 (an age-band code) dropped. trial_group = ExpGroup (1 control, 2-5 = the authors' experimental groups 1-4).
##Randomization: five groups of near-equal size; no combination rules beyond the five fixed pair types.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "survey.csv"), na.strings = ".")
stopifnot(nrow(d) == 1322, uniqueN(d$ID) == 1322)
d[, id := .I]
## per group: profile 1 and 2 = (gender, post type, FeelT column suffix) and the vote variable
G <- list(
  `1` = list(g = c("Female", "Male"),   p = c("Campaign", "Campaign"),                  f = c("Cont_F", "Cont_M"), v = "Vote_Cont"),
  `2` = list(g = c("Female", "Male"),   p = c("Campaign", "Personal Viewpoints"),       f = c("Exp1_F", "Exp1_M"), v = "Vote_Exp1"),
  `3` = list(g = c("Male", "Female"),   p = c("Campaign", "Personal Viewpoints"),       f = c("Exp2_M", "Exp2_F"), v = "Vote_Exp2"),
  `4` = list(g = c("Female", "Male"),   p = c("Campaign", "Personal Lives"),            f = c("Exp3_F", "Exp3_M"), v = "Vote_Exp3"),
  `5` = list(g = c("Male", "Female"),   p = c("Campaign", "Personal Lives"),            f = c("Exp4_M", "Exp4_F"), v = "Vote_Exp4"))
L <- list()
for (k in names(G)) {
  s <- d[ExpGroup == as.integer(k)]; gg <- G[[k]]
  for (j in 1:2) {
    L[[length(L) + 1]] <- s[, .(id, task = 1L, profile = j, choice = as.integer(get(gg$v) == j),
      rating = as.integer(get(paste0("FeelT_", gg$f[j]))),
      attr_candidate_gender = gg$g[j], attr_post_type = gg$p[j], trial_group = ExpGroup,
      cov_age = as.integer(age), cov_survey_weight = weight, cov_gender_code = as.integer(sex),
      cov_education_code = as.integer(edu))]
  }
}
r <- rbindlist(L)
stopifnot(!anyNA(r$choice), !anyNA(r$rating), r[, sum(choice), by = id][, all(V1 == 1)], r[, .N, by = id][, all(N == 2)])
setorder(r, id, task, profile)
fwrite(r, file.path(out, "yang_2026_candidate_posts.csv"))
