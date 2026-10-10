##Democratic-system conjoint (Chile) from
##Singh, S. P., & Williams, N. S. (2021). What type of democracy do Chileans want?
##Research & Politics, 8(3), 20531680211031045. https://doi.org/10.1177/20531680211031045
##Replication data: Harvard Dataverse doi:10.7910/DVN/PC0TLQ, CC0 1.0, no restricted files, no terms.
##File read: Chile_Conjoint_June.tab (Dataverse tab version of the authors' Chile_Conjoint_June.csv,
##one row per respondent x contest x profile); readme.rtf and the authors' Chileans_Want_Supplementary.R
##and _June.txt log read as text. The article (Sage, open access) could not be fetched (bot wall), so
##the question wording, panel provider and fielding dates are not documented here.
##Usage: Rscript singh_2021.R <dir holding Chile_Conjoint_June.tab> <output dir>
##
##2,650 respondents x 5 contests x 2 profiles = 26,500 rows in the file. Each profile is a
##hypothetical democratic system (the outcome column is called Chosen_country) described by 7
##attributes, stored as the Spanish text in the file (column names = the attribute headings):
##who can vote (3 levels), law creation, same-sex marriage, presidency, voting rules (3), party
##system, electoral system (2 each). Surrounding spaces are trimmed. One voting-rule level is stored
##truncated in the source ("El voto es obligatorio por ley, pero quienes no votan no reciben
##ninguna"); the authors' code uses the same string (English "Compulsory voting with no punishment"),
##kept as stored. task = contest_no, profile = Profile (1/2), both recorded.
##choice = Chosen_country (1 = profile chosen). Forced choice: every answered contest has exactly one
##chosen profile (checked). 2,242 contests (all profiles NA) were not answered and are dropped;
##respondents with no answered contest disappear.
##Randomization restrictions, level probabilities and attribute order are not documented in the deposit.
##The authors' analysis keeps respondents who passed an instructed-response attention check (IMC ==
##"Otra"); all respondents are kept here with cov_attention_pass (1 = "Otra", 0 = any other answer,
##NA = "NA"). The authors rake their own weights in code (sex, age, education); no weight is in the
##deposit, so none is stored.
##Covariates: cov_gender (Female: Femenino = female, Masculino = male, Otra = other, "NA" = NA),
##cov_age (Age, free-typed; whole numbers 18-100 kept, others NA: the file has values 15-144),
##cov_education (Education answer text; "Prefiero no decirlo" and "NA" = NA), cov_income (Income
##answer text; "NA" = NA). Dropped: caseID (Qualtrics ResponseId; re-keyed to integers in file order).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "Chile_Conjoint_June.tab"), encoding = "UTF-8", na.strings = "")
stopifnot(nrow(s) == 26500, uniqueN(s$caseID) == 2650)
d <- data.table(id = match(s$caseID, unique(s$caseID)), task = as.integer(s$contest_no),
                profile = as.integer(s$Profile), choice = as.integer(s$Chosen_country))
att <- c(who_can_vote = "¿Quién puede votar?", law_creation = "Creación de leyes",
         same_sex_marriage = "Matrimonio igualitario", presidency = "Presidencia",
         voting_rules = "Reglas para votar", party_system = "Sistema de partidos",
         electoral_system = "Sistema electoral")
for (k in names(att)) d[, paste0("attr_", k) := trimws(s[[att[k]]])]
na <- function(x) { x[x %in% c("NA", "")] <- NA; x }
age <- suppressWarnings(as.numeric(na(as.character(s$Age))))
d[, `:=`(cov_gender = c(Femenino = "female", Masculino = "male", Otra = "other")[na(s$Female)],
         cov_age = fifelse(!is.na(age) & age == round(age) & age >= 18 & age <= 100, as.integer(age), NA_integer_),
         cov_education = { e <- na(s$Education); e[e == "Prefiero no decirlo"] <- NA; e },
         cov_income = na(s$Income),
         cov_attention_pass = fifelse(na(s$IMC) == "Otra", 1L, 0L))]
d[, cov_gender := unname(cov_gender)]
stopifnot(d[, all(is.na(choice)) | all(!is.na(choice)), .(id, task)]$V1)
d <- d[!is.na(choice)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "singh_2021_chile_democracy.csv"))
