##National-security-defender conjoint (Taiwan) from
##Pan, H.-H., & Kagotani, K. (forthcoming). Diplomatic visits and image-building: A conjoint
##analysis in Taiwan. Asian Survey. (Citation as given in the deposit; no article DOI found.)
##Replication data: Harvard Dataverse doi:10.7910/DVN/HMRB9N, CC0 1.0, no restricted files.
##File read: visit_analysis.dta (Dataverse "original format" of visit_analysis.tab).
##Read as text, not run: PK_Visit_AS_ReadMe.txt, visit_analysis.do. The questionnaire is the
##article's Appendix 1 ("English Translation Follows the Original Text in Traditional
##Chinese"), not in the deposit, so the outcome wording below is a PARAPHRASE.
##Usage: Rscript pan_2025.R <dir holding the .dta> <output dir>
##
##2,245 Taiwanese respondents (survey, mode and date not stated in the deposit), 5 tasks of 2
##hypothetical politicians, 6 attributes. task and profile come from the recorded `contest`
##("t_p", set_card). Outcome:
##  choice: which of the two politicians the respondent prefers as a defender of national
##    security (paraphrase from the do-file's figure titles "Probability of a Politician Being
##    Preferred as a National Security Defender"). OPT-OUT (inferred): never are both profiles
##    of a task chosen (with independent yes/no answers at a 27% rate, ~7% of tasks would
##    be), and in 5,105 of 11,225 tasks neither is (choice = 0 on both; 514
##    respondents chose neither in all 5 tasks), so the question evidently allowed "neither";
##    the answer options are not in the deposit. Mean choice 0.27, matching the do-file's
##    marginal-mean axis (0.20-0.35).
##Attribute text: respondents saw Traditional Chinese (do-file, Figure 1 note); only the .dta
##English value labels survive and are stored as is: gender Female/Male; party Independent/
##DPP/KMT; education BA/MA/PhD; met_china_officials ("Ever met with any senior Chinese
##officials") No/Yes; met_us_officials ("Ever met with any senior US officials") No/Yes;
##cross_strait_policy ("Cross-Strait relations policy") "Oppose 92 Consensus"/"Support 92
##Consensus". Attribute order and randomization rules are not documented; all level pairs
##occur.
##Covariates (.dta value-label text; all are the authors' coarsened versions, no raw answers
##are deposited): cov_gender (r_gender Female -> female, Male -> male), cov_born_before_1978
##(r_age2, "Before 1978"/"After 1978"), cov_college (r_edu, "W/0 college"/"w/ college"),
##cov_residence (r_reside, "6 Capitals"/"Others"), cov_cross_strait_relations (r_chtw3,
##perceived Cross-Strait relations Bad/Average/Good), cov_us_taiwan_relations (r_ustw3,
##perceived US-Taiwan relations Bad/Average/Good). Dropped: r_chtw2, r_ustw2 (two-category
##collapses of the 3-category items). No survey weight in the deposit.
##N: 2,245 respondents; the article was not accessible to compare.
##Spot check (no published numbers available): OLS of choice on the attributes, SEs clustered
##by id: met US officials +0.033 (0.006), met Chinese officials +0.016 (0.006), DPP -0.050 and
##KMT -0.055 vs Independent, within the do-file's AMCE axis (-0.10 to 0.05).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "visit_analysis.dta"))
lt <- function(x) as.character(as_factor(x, levels = "labels"))
tp <- tstrsplit(k$contest, "_")
d <- data.table(id = as.integer(k$id), task = as.integer(tp[[1]]), profile = as.integer(tp[[2]]), choice = as.integer(k$choice),
                attr_gender = lt(k$p_gender), attr_party = lt(k$p_party), attr_education = lt(k$p_edu),
                attr_met_china_officials = lt(k$p_ch), attr_met_us_officials = lt(k$p_us), attr_cross_strait_policy = lt(k$p_consensus),
                cov_gender = c(Female = "female", Male = "male")[lt(k$r_gender)], cov_born_before_1978 = lt(k$r_age2),
                cov_college = lt(k$r_edu), cov_residence = lt(k$r_reside),
                cov_cross_strait_relations = lt(k$r_chtw3), cov_us_taiwan_relations = lt(k$r_ustw3))
stopifnot(all(d$task %in% 1:5), all(d$profile %in% 1:2), d[, .N, .(id, task)][, all(N == 2)], !anyNA(d$choice),
          d[, sum(choice), .(id, task)][, all(V1 <= 1)], uniqueN(d$id) == 2245)
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pan_2025_diplomatic_visits.csv"))
