##Four two-factor vignette experiments from the MigCrimeMexSurvey 2021 (Mexico), by
##López García, A. I., Berens, S., & Maydom, B. (2023). MigCrimeMexSurvey 2021 (Harvard Dataverse). The tax experiment (E1) is
##in López García, A. I., Berens, S., & Maydom, B. (2023/24). Emigration, social remittances and fiscal policy preferences:
##Experimental evidence from Mexico. Comparative Political Studies. https://doi.org/10.1177/00104140231204235
##Replication data: Harvard Dataverse doi:10.7910/DVN/BYAVMC, CC0 1.0 (no restricted files). Files read:
##"Surveys 1-12 Pollfish.tab" (2,401 respondents x 209 columns), the questionnaire "MigCrimeMexSurvey 2021 - questionnaire.pdf"
##(English column; Experiments 1, 4, 5, 6) and "Data preparation.do" (as text; E1 vignette coding).
##Usage: Rscript lopezgarcia_2023.R <dir holding Surveys 1-12 Pollfish.tab (renamed surveys.tab)> <output dir>   (reads surveys.tab)
##
##Pollfish online survey of Mexican adults, 31 Dec 2021-2 Jan 2022, 2,401 respondents (the authors' sample; the file is one row per
##respondent, no respondent id other than the sequential id column). Every respondent saw ALL experiments in the one survey; each
##experiment is one table (own attribute set and outcome). Each has two independently randomized clauses (columns Q*_vign1, Q*_vign2) inserted into
##one sentence; the control level of a clause is left out ("Empty" in the questionnaire) and is stored as '(not shown)'. The design is a balanced
##full factorial (every cell has 200 or 201 respondents). Code order = the questionnaire's listed order of the treatments (E1 order is confirmed by
##Data preparation.do). Level text is the English translation of the questionnaire's (Spanish displayed) wording.
##  lopezgarcia_2023_mx_tax_earmark      E1 (Q36): "To what extent do you agree or disagree with you paying more taxes <tax> than you do now to
##      increase public spending <use>?" tax: such as the VAT / such as the income tax; use: in public health and hospitals / building and maintaining
##      public roads / public security and justice delivery. rating_agree 1-5 (1 strongly disagree, 5 strongly agree).
##  lopezgarcia_2023_mx_military_proposal E4 (Q46): "A recent proposal <source> calls for the national government to take the military off the
##      streets and find other ways to reduce crime <partner>": source: made by the PAN / by the PRI; partner: in collaboration with municipal
##      authorities / the private sector / citizens and community organisations. rating_agree 1-5.
##  lopezgarcia_2023_mx_security_officers E5 (Q26): "To what extent do you agree or disagree with the following statement? To reduce and control
##      crime <place>, it is necessary to have more security officers on the streets <programme>": place: in the most violent municipalities of the
##      country; programme: five add-ons (vocational and training programmes for the youth; more employment opportunities for at-risk young people; more
##      correction and detention centres with more severe laws and longer prison terms; the same with better living conditions and rehabilitation;
##      night curfews, crackdowns and zero tolerance). rating_agree 1-5.
##  lopezgarcia_2023_mx_police_recruits  E6 (Q15, Q16): "If authorities hire more <female> municipal police officers <background>": female / (not shown);
##      background: who previously worked as soldiers / in private security companies / were members of the self-defence forces / have been human
##      rights activists / previously worked as migrants in the US. rating_faith (Q15: "how much faith would you have that these policemen catch the
##      criminals, if you were a victim of a robbery or assault?" 1 not at all ... 4 a lot) and rating_abuse_likelihood (Q16: how likely they would
##      incur in bribery, torture, discrimination, aggression, abuse or false arrest, 1 not likely ... 4 very likely).
##The questionnaire's exact English sentence is quoted above in part; answer scales are as listed in the questionnaire. The *_eval columns are stored as
##in the file. Experiments 2, 3 and 7 are single-factor (one treatment clause) and are not conjoint-type; Experiments 8-12 are not in the questionnaire.
##Covariates: cov_gender (gender: Data preparation.do `recode gender 2=0, gen(female)` so 1 = female, 2 = male), cov_age (age), cov_age_group (age_range,
##the .do labels 1 18-24, 2 25-34, 3 35-44, 4 45-54, 5 55+), cov_education (the authors' 4-level recode of education: 1-2 elementary/middle school,
##3-4 high school / technical college, 5 university, 6 postgraduate), cov_state (Area, Pollfish location, the state). Weight column is 1 for everyone (no weight).
##Dropped (PII or location): City, PostalCode, birth year, device/provider fields, timestamps, the rest of the survey.
##Count check: 2,401 respondents = the authors' sample; each experiment has 2,401 rows.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "surveys.tab"), quote = "\"", encoding = "UTF-8")
stopifnot(nrow(d) == 2401, !anyDuplicated(d$id), all(d$gender %in% 1:2))
cov <- data.table(id = as.integer(d$id), task = 1L, profile = 1L)
cov[, `:=`(cov_gender = c("female", "male")[d$gender], cov_age = as.integer(d$age),
           cov_age_group = c("18-24", "25-34", "35-44", "45-54", "55+")[d$age_range],
           cov_education = c("elementary/middle school", "elementary/middle school", "high school / technical college", "high school / technical college",
                             "university", "postgraduate")[d$education],
           cov_state = d$Area)]
## Area has its accented letters corrupted in the source file (two replacement characters): repaired by name; "Unknown" is NA
fix <- function(x, pat, to) sub(pat, to, x)
cov[, cov_state := fix(cov_state, "^Michoac.*n$", "Michoac\u00e1n")][, cov_state := fix(cov_state, "^M.{1,3}xico$", "M\u00e9xico")]
cov[, cov_state := fix(cov_state, "^Nuevo Le.*n$", "Nuevo Le\u00f3n")][, cov_state := fix(cov_state, "^Quer.*taro$", "Quer\u00e9taro")]
cov[, cov_state := fix(cov_state, "^San Luis Potos.*$", "San Luis Potos\u00ed")][, cov_state := fix(cov_state, "^Yucat.*n$", "Yucat\u00e1n")]
cov[cov_state == "Unknown", cov_state := NA]
mk <- function(nm, rating, v1, v2, a1, a2, l1, l2) {
  r <- copy(cov)
  for (k in names(rating)) r[[k]] <- as.integer(d[[rating[[k]]]])
  x1 <- d[[v1]]; x2 <- d[[v2]]
  stopifnot(all(x1 %in% 0:(length(l1))), all(x2 %in% 0:(length(l2))))
  r[[a1]] <- c("(not shown)", l1)[x1 + 1L]; r[[a2]] <- c("(not shown)", l2)[x2 + 1L]
  front <- c("id", "task", "profile", names(rating), a1, a2); setcolorder(r, c(front, setdiff(names(r), front)))
  stopifnot(all(unlist(r[, names(rating), with = FALSE]) %in% 1:5))
  cat(nm, nrow(r), "cells", nrow(r[, .N, c(a1, a2)]), "\n")
  setorder(r, id, task, profile); fwrite(r, file.path(out, paste0(nm, ".csv")))
}
mk("lopezgarcia_2023_mx_tax_earmark", c(rating_agree = "Q36_eval"), "Q36_vign1", "Q36_vign2", "attr_tax_type", "attr_spending_use",
   c("such as the Value Added Tax (VAT)", "such as the income tax (ISR)"),
   c("in public health and hospitals", "in building and maintaining public roads", "in public security and justice delivery"))
mk("lopezgarcia_2023_mx_military_proposal", c(rating_agree = "Q46_eval"), "Q46_vign1", "Q46_vign2", "attr_proposing_party", "attr_collaboration",
   c("made by the PAN", "made by the PRI"),
   c("in collaboration with municipal authorities", "in collaboration with the private sector", "in collaboration with citizens and community organisations"))
mk("lopezgarcia_2023_mx_security_officers", c(rating_agree = "Q26_eval"), "Q26_vign1", "Q26_vign2", "attr_place", "attr_programme",
   "in the most violent municipalities of the country",
   c("and implement vocational and training programs for the youth", "and create more employment opportunities for at-risk young people",
     "and invest more in correction and detention centres, with more severe laws and longer prison terms",
     "and invest more in correction and detention centres, with better living conditions and in-prison rehabilitation programmes",
     "such as implementing night curfews, crackdowns and zero tolerance strategies"))
mk("lopezgarcia_2023_mx_police_recruits", c(rating_faith = "Q15_eval", rating_abuse_likelihood = "Q16_eval"), "Q15_vign1", "Q15_vign2",
   "attr_officer_sex", "attr_officer_background", "female",
   c("who previously worked as soldiers", "who previously worked in private security companies", "who previously were members of the self-defence forces",
     "who have been human rights activists", "who previously worked as migrants in the US"))
