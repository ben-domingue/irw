##Clinical vignette factorial survey (self-management support) from
##Bos-Touwen, I. D., Trappenburg, J. C. A., van der Wulp, I., Schuurmans, M. J., & de Wit, N. J.
##(2017). Patient factors that influence clinicians' decision making in self-management support:
##A clinical vignette study. PLoS ONE, 12(2), e0171251. https://doi.org/10.1371/journal.pone.0171251
##Data: Dryad doi:10.5061/dryad.9g5m2 (mirrored as Zenodo record 4987374), CC0 1.0. Files read:
##"Data I.D. Bos- Touwen clinical vignette study.sav" (+ README docx for variable meanings).
##Wording and vignette template: the article's S1 Questionnaire (English and Dutch versions).
##Usage: Rscript bostouwen_2017.R <dir holding bos.sav (the .sav renamed)> <output dir>
##
##140 Dutch primary-care providers (60 GPs, 80 practice nurses; 21 incomplete respondents were
##excluded by the authors and are not in the deposit), July-October 2014. Each read 12 text
##vignettes (Dutch) describing "Patient X" with 11 factors: age (40/60/80), education level,
##disease (COPD / diabetes type 2), symptom severity, patient-provider relationship, knowledge,
##illness perception, social support, motivation, self-efficacy, anxiety/depressive disorder.
##Fixed blocked design: from the 6,912-cell full factorial, unrealistic combinations were removed
##and 96 vignettes chosen with a Fedorov (main-effects) algorithm, split into 8 blocks of 12; each
##provider was randomly given one block (stratified by GP/PN). One vignette per task (profile = 1),
##task = Case_nr (position in the questionnaire; the questionnaire order was fixed per block).
##Levels are the deposit's SPSS value labels (English short forms of the Dutch sentences).
##Outcomes (asked after every vignette, 1-5):
##  rating           = Prov_SM, "How likely is it that you will support this patient in
##                     self-management?" 1 very unlikely ... 5 very likely (the .sav labels 3 as
##                     "somewhat unlikely", the questionnaire as "somewhat likely").
##  rating_success   = Success, "How successful do you think self-management support will be in this
##                     patient?" 1 not at all successful ... 5 very successful.
##  rating_certainty = Certainty, "I am confident about my answers:" 1 strongly disagree ... 5
##                     strongly agree (.sav labels: not certain at all ... very certain).
##trial_vignette = Casenrs (design vignette 1-96); trial_block = questionnaire (block_nr); two rows
##of respondent 100 carry block_nr 95/96 (a data-entry slip: Casenrs 95/96 belong to block 8, as
##do that respondent's other rows), so trial_block is set to 8 there.
##Covariates: cov_gender (1 male, 2 female, .sav labels), cov_age (Age_CP, years), cov_profession
##(Profession3 label text: GP / final year GP trainee / primary care nurse). Respondent_nr re-keyed.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- list.files(raw, pattern = "\\.sav$", full.names = TRUE); stopifnot(length(f) == 1)
x <- as.data.table(read_sav(f))
lab <- function(v) as.character(as_factor(v, levels = "labels"))
x[, id := match(Respondent_nr, sort(unique(Respondent_nr)))]
blk <- as.integer(zap_labels(x$block_nr))
stopifnot(sum(blk > 8) == 2, all(x$Respondent_nr[blk > 8] == 100))
blk[blk > 8] <- 8L
d <- data.table(id = x$id, task = as.integer(x$Case_nr), profile = 1L,
  rating = as.integer(zap_labels(x$Prov_SM)), rating_success = as.integer(zap_labels(x$Success)),
  rating_certainty = as.integer(zap_labels(x$Certainty)),
  attr_age = lab(x$Age), attr_education = lab(x$Education), attr_disease = lab(x$Disease),
  attr_disease_severity = lab(x$Disease_severity), attr_provider_relationship = lab(x$HCP_relation),
  attr_knowledge = lab(x$Knowledge), attr_illness_perception = lab(x$Perception),
  attr_social_support = lab(x$Social_support), attr_motivation = lab(x$Motivation),
  attr_self_efficacy = lab(x$Self_efficacy), attr_depression = lab(x$Depression),
  trial_vignette = as.integer(x$Casenrs), trial_block = blk,
  cov_gender = c("male", "female")[as.integer(zap_labels(x$Gender))], cov_age = as.integer(x$Age_CP),
  cov_profession = lab(x$Profession3))
d[cov_profession == "Pramary care nurse", cov_profession := "Primary care nurse"]
stopifnot(d[, .N, .(id, task)][, all(N == 1)], d[, uniqueN(trial_block), id][, all(V1 == 1)],
          d[, uniqueN(trial_vignette), trial_block][, all(V1 == 12)], d[, uniqueN(trial_block), trial_vignette][, all(V1 == 1)],
          !anyNA(d))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bostouwen_2017_selfmanagement.csv"))
cat(nrow(d), uniqueN(d$id), "\n"); print(d[, uniqueN(trial_vignette), trial_block])
