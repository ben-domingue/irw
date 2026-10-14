##Paired conjoint on which couple should be given a child for adoption (Catalonia) from
##López Ortega, A., Blanco Bosco, A., et al. (2025). Not so sexually modern after all: Homonegativity and prejudice against
##open and age-gap relationships (manuscript 24-0076.R2; journal and article DOI not stated in the deposit).
##Replication data: Harvard Dataverse doi:10.7910/DVN/CBWKQA, CC0 1.0 (no restricted files). File read: conjoint_data.tab
##(the authors' cleaned long file; the CEO .sav microdata "Microdades 1048_conjoint.sav" is not used). Wording and level text
##from "Lopez Ortega 24-0076.R2 supplementary material.docx" (Text S1, S2) and the codebook docx; level definitions from From_raw_to_clean_coint_data.R
##(as text; the age-pair grouping). Usage: Rscript lopezortega_2025_homonegativity.R <dir holding conjoint_data.tab> <output dir>
##
##Catalan online survey (Centre d'Estudis d'Opinió, Enquesta Sociopolítica 2022, web mode), 4,166 respondents in the file, 5 tasks of 2 couples
##(41,660 rows). Question (Text S1): "Below you will see a profile of two couples who have applied to adopt a child. Imagine that you are the person
##responsible for matching the child to one of the two couples. Answer the questions below. Which of these two couples do you think should be given
##a child for adoption first?" (To couple 1 / To couple 2). choice = the couple chosen; forced choice, no opt-out. In 822 of the 20,830 tasks neither
##couple has a choice recorded (1,644 rows with NA): those tasks have no outcome and are omitted.
##Six attributes: the couple's sexuality (conveyed by the partners' names: man-woman, two-men, two-women couples; the data store the category only, the
##names are listed in Text S2), type of relationship (open / closed), ages of the partners (the data store the authors' grouping of ten displayed age pairs
##into more or less age difference), education, family values, reason for adoption. Level text is the Text S2 wording, translated from Catalan; the
##sexuality and age-difference attributes are the authors' category tags with the displayed names / age pairs listed in the level text where the
##appendix gives them ('LABELS: partly tags'). Derived columns agediff_sex_couple and pairwise_so_couple are dropped.
##Randomization restrictions are not documented. Respondent covariates: cov_gender (sex), cov_age_group (age band), cov_ideology (left, centre,
##right; 1,100 rows NA in the file), cov_survey_weight (CEO weight, 'weights'). id = the file's `order` (respondent id) re-keyed to integers.
##Count check: 4,166 respondents, 10 rows each = the file; the article N was not read.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "conjoint_data.tab"), quote = "\"", na.strings = c("NA", ""))
stopifnot(nrow(d) == 41660, d[, .N, .(order, randomization)][, all(N == 2)])
d[, t := paste(order, randomization)]
nchosen <- d[, .(s = sum(choice, na.rm = TRUE), na = sum(is.na(choice))), t]
stopifnot(nchosen[, all((s == 1 & na == 0) | (s == 0 & na == 2))])
k <- d[!t %in% nchosen[s == 0, t]]
cat("tasks dropped (no choice):", uniqueN(d$t) - uniqueN(k$t), "respondents kept:", uniqueN(k$order), "\n")
rel <- c("Closed couple" = "Closed couple (they only have relationships with each other)", "Open couple" = "Open couple (they have relationships with other people)")
age <- c("More age difference" = "More age difference (ages 30 and 50, 55 and 40, 51 and 33, 45 and 53 or 37 and 49)",
         "Less age difference" = "Less age difference (ages 28 and 32, 40 and 35, 29 and 36, 32 and 34 or 43 and 39)")
edu <- c("Primary studies" = "Primary", "Secondary studies" = "Secondary", "University" = "Superior")
reas <- c("Can't have biological children" = "They cannot have biological children", "Already have biological children and want to adopt" = "They have biological children and want to adopt")
sex <- c("Man and woman couple" = "Man and woman couple (partners\x27 names)", "Two-men couple" = "Two-men couple (partners\x27 names)", "Two-women couple" = "Two-women couple (partners\x27 names)")
stopifnot(!anyNA(rel[k$relationship_couple]), !anyNA(age[k$age_couple]), !anyNA(edu[k$education_couple]), !anyNA(reas[k$reason_couple]), !anyNA(sex[k$sexuality_couple]))
r <- data.table(id = as.integer(factor(k$order)), task = as.integer(k$randomization), profile = as.integer(k$couple), choice = as.integer(k$choice),
  attr_sexuality = unname(sex[k$sexuality_couple]), attr_relationship = unname(rel[k$relationship_couple]), attr_age = unname(age[k$age_couple]),
  attr_education = unname(edu[k$education_couple]), attr_family_values = k$values_couple, attr_reason_for_adoption = unname(reas[k$reason_couple]),
  cov_gender = tolower(k$sex), cov_age_group = k$age, cov_ideology = k$ideology, cov_survey_weight = k$weights)

stopifnot(r[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(r, id, task, profile)
fwrite(r, file.path(out, "lopezortega_2025_adoption_couples.csv")); cat("rows", nrow(r), "\n")
