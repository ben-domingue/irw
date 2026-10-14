##2 x 4 factorial candidate vignette (Italy), one per respondent, from
##Portmann, L. (2021). Do stereotypes explain discrimination against minority candidates or discrimination in
##favor of majority candidates? British Journal of Political Science. https://doi.org/10.1017/S0007123420000800
##Replication data: Harvard Dataverse doi:10.7910/DVN/BNSXB2, CC0 1.0 (no restricted files). Files read:
##Data_SurveyExperiment.tab (1,597 rows, the main experiment; Pilot.tab is not used) and 0_DataPreparation.R (as text;
##coding of treat, candname, Treat_c4, evaluation categories, age/gender labels).
##Usage: Rscript portmann_2021.R <dir holding Data_SurveyExperiment.tab> <output dir>
##
##Online experiment with Italian citizens (Dynata; fielded 25 May-3 June 2019), restricted by the authors to partisans (who "feel
##close to" a party): 1,597 respondents = the article's N after 346 dropouts. Respondents read that their preferred party
##was considering nominating a person for the next national parliamentary elections (single-member seat). Two randomized
##attributes (treat = Candidatechoiceexperiment{IT,AL}{1-4}): the candidate's name (IT: Giuseppe Martinelli, an Italian
##name; AL: Ahmed Haddou, an Algerian name) and the positive information given (1 = none, 2 = positive character traits,
##3 = positive civic citizenship, 4 = both; 'mediator' in the article). Roughly 200 per cell (189-205).
##Level text is NOT in the deposit: it is taken from the article's research-design text (names; information paraphrased: traits
##'sincere, honest, respected, high level of expertise'; civic citizenship 'promotes Italian interests, values Italian culture,
##understands the political system'), paraphrased from the article; the vignette wording is in the closed appendix B.1. In the control
##vignette the information is left off (only name, age and party affiliation were shown): attr_positive_information = '(not shown)'.
##Outcomes, one vignette per respondent, no opt-out:
##  rating_vote = DV_vote, 11-point scale (0-10) of how likely the respondent is to vote for the candidate if the preferred party nominates him
##  rating_nomination = DV_nom, 11-point scale (0-10): whether the preferred party should nominate the candidate
##  rating_evaluation = DV_eval_4: overall evaluation to be forwarded to the party: 1 negative, 2 neutral, 3 positive (coded from the
##    answer text 'Evaluation negativ/neutral/positiv'; 'No answer' is NA).
##Scale anchors and exact wording are in the closed appendix C and are not stated.
##Rows with no outcome at all (3) are omitted. No respondent id kept (Qualtrics ResponseId dropped; id = row number).
##Covariates: cov_age_group (AGE bands, Italian text), cov_gender (GENDER: Donna female, Uomo male, Altro other), cov_region, cov_education
##(EDUC answer text, Italian), cov_ideology_lr (IDEOL 0 Sinistra to 10 Destra; 'cannot place myself'/refused NA),
##cov_migration_background (IO_RESP, Italian answer text). Dropped: the two 9-item stereotype batteries (EXSTYP_*), derived D_Traits, D_CivCit,
##and NAT_RESP (all Italian citizens).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "Data_SurveyExperiment.tab"), quote = "\"")
stopifnot(nrow(d) == 1597, !anyDuplicated(d$ResponseId))
d[, cand := substr(treat, 26, 27)][, info := as.integer(substr(treat, 28, 28))]
stopifnot(all(d$cand %in% c("IT", "AL")), all(d$info %in% 1:4))
evalc <- c("Evaluation negativ" = 1L, "Evaluation neutral" = 2L, "Evaluation positiv" = 3L)
d[, ev := evalc[DV_eval_4]]
info <- c("(not shown)", "positive character traits (sincere, honest, respected, high level of expertise)",
          "positive civic citizenship (promotes Italian interests, values Italian culture, understands the political system)",
          "both positive character traits and positive civic citizenship")
r <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L,
  rating_vote = as.integer(d$DV_vote), rating_nomination = as.integer(d$DV_nom), rating_evaluation = as.integer(d$ev),
  attr_candidate_name = c(IT = "Giuseppe Martinelli (Italian name)", AL = "Ahmed Haddou (Algerian name)")[d$cand],
  attr_positive_information = info[d$info])
r[, cov_age_group := sub(" anni", " years", sub("Più di", "More than", d$AGE))]
r[, cov_gender := c(Donna = "female", Uomo = "male", Altro = "other")[d$GENDER]]
r[, cov_region := d$REGION]
r[, cov_education := trimws(gsub("\\\\t|\\t", "", d$EDUC))]
r[cov_education == "", cov_education := NA]
r[, cov_ideology_lr := suppressWarnings(as.integer(sub(" .*", "", d$IDEOL)))]
r[, cov_migration_background := c("No, non ho un background migratorio." = "No (non ho un background migratorio)", "Preferisco non rispondere." = NA)[d$IO_RESP]]
r[grepl("^S", d$IO_RESP), cov_migration_background := "Sì, ho un background migratorio"]
r <- r[!(is.na(rating_vote) & is.na(rating_nomination) & is.na(rating_evaluation))]
print(r[, .N, .(attr_candidate_name, attr_positive_information)]); print(summary(r$rating_vote)); print(table(r$cov_education, useNA = "a"))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "portmann_2021_candidate_stereotypes.csv")); cat("rows", nrow(r), "\n")
