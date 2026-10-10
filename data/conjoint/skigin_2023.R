##Victim-solidarity factorial experiment (Mexico; Study 2) from
##Skigin, N. (2023). Prosocial behavior amid violence: The deservingness heuristic and
##solidarity with victims. Political Psychology. https://doi.org/10.1111/pops.12926
##Replication data: Harvard Dataverse doi:10.7910/DVN/OPOZM8, CC0 1.0. File read:
##data_study2.rds (one data.frame). Also read as text: readME.docx (pandoc) and
##"Replication_Study 2_Political Psychology.R" (the author's analysis, not run). The article
##(Wiley, behind a bot check) was not read; no codebook or questionnaire is deposited.
##Usage: Rscript skigin_2023.R <dir holding data_study2.rds> <output dir>
##
##NOT BUILT: Study 1 (data_study1.rds) is a separate single-factor vignette study.
##Study 2: 1,950 Mexican respondents, 4 vignettes each about a victim of violence, one victim
##per vignette (single-profile tasks: profile = 1). task = the number in `grp` (g1-g4); that grp
##is the display order is not documented. 9 respondent ids appear 2 or 3 times under different
##`ticket` values. For 8 of them the copies are identical on every analysed column (panel
##duplicates; one copy kept). One id (b1d064f6...) has two DIFFERENT sets of 4 vignettes and
##answers, so it is dropped: 1,949 respondents, 7,796 rows (article N not checked: paywalled).
##Attributes (7; the author's ENGLISH short labels as stored; the Spanish display text is not
##deposited): nature of violence (Selective / Indiscriminate; source column "Type of Violence",
##renamed by the author), perpetrator (Military / Narcos / Police), crime (Disappeared /
##Displaced / Extortion / Murder / Torture; the stored "Extorsion" is relabelled "Extortion" as
##in the author's script L24), victim occupation (Owner / Street Vendor), victim nationality
##(Central American / Mexican), victim ethnicity (Indigenous / Mixed / White), victim gender
##(Female / Male). Restrictions: none documented; every pair of levels occurs.
##Outcomes, per vignette. NO QUESTION WORDING is in the deposit; names and meanings are from
##the author's variable names and figure labels, so design_outcomes questions are paraphrases
##and scale anchors are unknown:
##  choice                 donatedummy, whether the respondent donated for this victim (0/1);
##                         a single-profile yes/no, so opt_out = yes (choice 0 = did not donate)
##  rating_donation        donateamount, amount donated, 0-150 as stored (unit not stated)
##  rating_thermometer     therm, feeling thermometer toward the victim, 0-100
##  rating_social_distance socialdist, 0-3 ("Social Distance Tolerance with Victims")
##  rating_compassion      empathy, 0-3 ("Compassion for Victims")
##  rating_norms           norms, 0-3 ("Social Norms about Helping Victims")
##Missing single ratings stay NA. Dropped outcome: punish (0-5, varies by vignette, not
##described anywhere in the deposit).
##Covariates (codes as stored; no labels deposited, hence _code suffixes): cov_gender (Gender:
##Female -> female, Male -> male), cov_age (Ages, years), cov_ethnicity (ethnic, text),
##cov_education_code (educ, 1-21; the script notes educ = 7 is "Preparatoria Terminada"),
##cov_party_id_code (party, 1-10), cov_ideology (ideology_1, 1-10), cov_ses_code (SELs),
##cov_geo_code (GEO), cov_state_code (State), cov_interest, cov_talk, cov_trust_military
##(trustffaa), cov_presid_approval, cov_empathy_baseline_2, cov_empathy_baseline_4,
##cov_trust_ffaa_1, cov_identif_victims_4, cov_indirect_victim. Dropped: ticket and resp.id
##(panel hashes; re-keyed to integers in file order), Muni (municipality code: fine-grained
##location), the derived Respondent Ethnicity / Gender / SES (same as / different from victim).
##No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "data_study2.rds")))
stopifnot(nrow(s) == 7844, uniqueN(s$resp.id) == 1950)
s[, task := as.integer(sub("^g", "", grp))]
an <- c("donatedummy", "donateamount", "therm", "socialdist", "empathy", "norms", "Type of Violence", "Perpetrator", "Crime",
        "Victim Occupation", "Victim Nationality", "Victim Ethnicity", "Victim Gender", "Ages", "Gender")
x <- s[, lapply(.SD, uniqueN), .(resp.id, task), .SDcols = an]
bad <- x[apply(x[, -(1:2)] > 1, 1, any), unique(resp.id)]
stopifnot(length(bad) == 1)
s <- unique(s[!resp.id %in% bad], by = c("resp.id", "task"))
lv <- function(v) as.character(s[[v]])
d <- data.table(id = match(s$resp.id, unique(s$resp.id)), task = s$task, profile = 1L,
                choice = as.integer(s$donatedummy), rating_donation = as.numeric(s$donateamount),
                rating_thermometer = as.numeric(s$therm), rating_social_distance = as.integer(s$socialdist),
                rating_compassion = as.integer(s$empathy), rating_norms = as.integer(s$norms),
                attr_violence = lv("Type of Violence"), attr_perpetrator = lv("Perpetrator"),
                attr_crime = sub("^Extorsion$", "Extortion", lv("Crime")), attr_victim_occupation = lv("Victim Occupation"),
                attr_victim_nationality = lv("Victim Nationality"), attr_victim_ethnicity = lv("Victim Ethnicity"),
                attr_victim_gender = lv("Victim Gender"),
                cov_gender = c(Female = "female", Male = "male")[lv("Gender")], cov_age = as.integer(s$Ages),
                cov_ethnicity = s$ethnic, cov_education_code = as.integer(s$educ), cov_party_id_code = as.integer(s$party),
                cov_ideology = as.integer(s$ideology_1), cov_ses_code = as.integer(s$SELs), cov_geo_code = as.integer(s$GEO),
                cov_state_code = as.integer(s$State), cov_interest = as.integer(s$interest), cov_talk = as.integer(s$talk),
                cov_trust_military = as.numeric(s$trustffaa), cov_presid_approval = as.integer(s$presidapproval),
                cov_empathy_baseline_2 = as.numeric(s$empathy_baseline_2), cov_empathy_baseline_4 = as.numeric(s$empathy_baseline_4),
                cov_trust_ffaa_1 = as.numeric(s$trust_ffaa_1), cov_identif_victims_4 = as.numeric(s$identif_victims_4),
                cov_indirect_victim = as.integer(s$`Indirect Victim`))
stopifnot(nrow(d) == 7796, d[, .N, id][, all(N == 4)], !anyDuplicated(d[, .(id, task)]), all(d$task %in% 1:4),
          all(d$choice %in% 0:1), !anyNA(d[, .SD, .SDcols = patterns("^attr_")]), all(d$cov_gender %in% c("female", "male", NA)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "skigin_2023_victim_solidarity.csv"))
