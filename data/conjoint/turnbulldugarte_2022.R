##2x2 factorial vignette on a couple's surrogacy (Britain) from
##Turnbull-Dugarte, S. J. (2022). Fine for Adam & Eve but not Adam & Steve? Homonegativity bias, parasocial contact, and
##public support for surrogacy. Journal of European Public Policy. https://doi.org/10.1080/13501763.2022.2154823
##Replication data: Harvard Dataverse doi:10.7910/DVN/PDOXJD, CC0 1.0 (no restricted files). File read: surrogacyDATA.tab
##(downloaded with format=original, a CSV); mainanalysis.R read as text for the coding of the arms. Figures, QTA files not used.
##Usage: Rscript turnbulldugarte_2022.R <dir holding surrogacyDATA.tab> <output dir>
##
##British online sample, 1,979 respondents in the file; 5 arms (treatgroup 0-4): a control with no couple, and a 2x2 of the
##couple described (gay couple / straight couple) x the couple's status (celebrity / ordinary couple). Arm coding from
##mainanalysis.R (treatment 1 = celebrity gay couple, 2 = celebrity straight, 3 = ordinary gay, 4 = ordinary straight; homo and
##prestige dummies agree with treatgroup in every row). One vignette per respondent, between-subject; each row is a respondent.
##The control arm (392) sees no couple, so it is not a profile of the two attributes and is dropped, as in the authors' AMCE
##(surr_nocontrol). 25 respondents have no outcome and are dropped.
##LABELS: tags only. The deposit holds no questionnaire and the article was not accessible (publisher 403), so the vignette
##text is not recoverable. attr_couple and attr_status are the authors' plain labels from the figure labels in mainanalysis.R
##("Gay couple"/"Straight couple", "Celebrity couple"/"Ordinary couple"), not the displayed wording.
##Outcome: rating = `outcome`, 1-5 attitude to surrogacy; the authors' binary `support` = outcome >= 4 (verified) is derived
##and dropped. Question wording and anchors are not in the deposit: direction is inferred (support = 4-5) and anchors unknown.
##Covariates: cov_gender (Female/Male; "Missing" -> NA), cov_age (years), cov_education (answer text as in file),
##cov_ideology (Left/Centre/Right/Don't know). Dropped: other demographics (region, income, vote, religion, employment, ...),
##all *_nol/_nolab numeric recodes, derived dummies. No identifier in the file; id = row number.
##Count check: article N not read.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "surrogacyDATA.tab"), na.strings = c("NA", ""))
stopifnot(nrow(d) == 1979, all(d$support == as.integer(d$outcome >= 4), na.rm = TRUE))
d[, id0 := .I]
stopifnot(d[treatgroup == 1, all(homo == 1 & prestige == 1 & treatment == 1)], d[treatgroup == 2, all(homo == 0 & prestige == 1 & treatment == 2)],
          d[treatgroup == 3, all(homo == 0 & prestige == 0 & treatment == 4)], d[treatgroup == 4, all(homo == 1 & prestige == 0 & treatment == 3)])
k <- d[treatgroup > 0 & !is.na(outcome)]
r <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L, rating = as.integer(k$outcome),
  attr_couple = ifelse(k$homo == 1, "Gay couple", "Straight couple"),
  attr_status = ifelse(k$prestige == 1, "Celebrity couple", "Ordinary couple"),
  cov_gender = ifelse(k$gender == "Female", "female", ifelse(k$gender == "Male", "male", NA_character_)),
  cov_age = as.integer(k$age), cov_education = k$education, cov_ideology = k$ideology)
setorder(r, id, task, profile)
fwrite(r, file.path(out, "turnbulldugarte_2022_surrogacy.csv")); cat("rows", nrow(r), "\n")
