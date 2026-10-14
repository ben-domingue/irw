##Paired candidate conjoint on surname recognition (Germany, Bundestag-style candidates) from
##Leininger, A., & Swalve, T. (2026). What's in a name? Name recognition, place-based identities, and candidate success.
##The Journal of Politics (per the deposit README; volume, pages and article DOI not stated in the deposit; year 2026 from the
##deposit's version date 08/05/2026).
##Replication data: Harvard Dataverse doi:10.7910/DVN/R22WYY, CC0 1.0, no restricted files. Files read (from
##WhatsInAName_replication_package.zip): conjoint/data/conjoint_analysis.RData (object df_analysis, loaded into its own environment),
##codebook.pdf (variable descriptions), README.md, conjoint/code/*.R (as text). The observational data and name-recognition
##battery (df_namerecog) are not used.
##Usage: Rscript leininger_2026.R <dir holding WhatsInAName_replication_package/> <output dir>
##
##947 respondents of a Bilendi online panel in six German regions, 5 tasks x 2 candidate profiles (9,470 rows). Attributes
##randomized per profile (codebook): surname (40 surnames, local to some regions and not others; the nametype/dispersion
##variables are the authors' analysis codings and are dropped), party (CDU, SPD, Greens, FDP, AfD, The Left), gender (female/male),
##occupation (white collar / blue collar), place of residence (city / town/village).
##LABELS: tags only for occupation and residence: the deposit has no questionnaire, the article was not located, and neither the
##displayed occupation titles nor the residence wording are recoverable; the stored tags are used. One surname is stored as
##"Janssen (not local)": the " (not local)" suffix is the authors' tag for the same surname used as a non-local name in another
##region and is stripped (inferred, displayed text is the surname).
##Outcomes (wording NOT in the deposit; codebook descriptions): choice = chosencand, the candidate chosen over the alternative in the
##pair (the exact question is not deposited); rating_trustworthy, rating_local_knowledge, rating_district_representative and
##rating_election_chance = perceived trustworthiness / local knowledge / representativeness of the district / election chances of the
##candidate, each 1-5 (anchors not deposited; higher read as more). No opt-out is recorded: every task with a recorded choice has
##exactly one chosen profile (checked). 628 tasks have no choice (both profiles NA); those are kept only where a rating exists
##(choice NA on both profiles; 1 task with neither is dropped); 4 further rows with no outcome at all are omitted.
##Covariates: cov_gender (male 0/1 -> female/male), cov_age, cov_education_level (authors' high/medium/low/other grouping, not the source
##categories), cov_region, cov_urban (urban/rural), cov_local_born, cov_local_identity_index (mean of three items, 1-5),
##cov_attach_birth and cov_attach_localknow (agreement that representatives should be born locally / have local knowledge, 1-5).
##Dropped: bilendi_id (panel id), plz (postal code), respondent distance to candidate residence, ptv_candparty, derived
##nametype/cand_surname_disp/foreign. id = df_analysis `id` re-keyed to integers.
##Count check: the article was not read; 947 respondents = deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "WhatsInAName_replication_package", "conjoint", "data", "conjoint_analysis.RData"), envir = e)
d <- as.data.table(e$df_analysis)
stopifnot(nrow(d) == 9470, d[, .N, .(id, task, profile)][, all(N == 1)], d[, .N, .(id, task)][, all(N == 2)], !anyNA(d[, .(lastname, party, cand_gender, cand_occupationtype, cand_residencetype)]))
d[, tk := paste(id, task)]
ch <- d[, .(s = sum(chosencand, na.rm = TRUE), na = sum(is.na(chosencand)), rt = sum(!is.na(trustworthy) | !is.na(localknow) | !is.na(districtrep) | !is.na(electionchance))), tk]
stopifnot(ch[, all((s == 1 & na == 0) | (s == 0 & na == 2))])
keep <- ch[(s == 1) | (rt > 0), tk]
cat("tasks total", uniqueN(d$tk), "kept", length(keep), "no choice but rated", ch[s == 0 & rt > 0, .N], "\n")
d <- d[tk %in% keep]
d[, rid := as.integer(factor(id, levels = unique(sort(id))))]
cap <- function(x) as.character(x)
r <- data.table(id = d$rid, task = as.integer(d$task), profile = match(as.character(d$profile), c("A", "B")), choice = as.integer(d$chosencand),
  rating_trustworthy = as.integer(d$trustworthy), rating_local_knowledge = as.integer(d$localknow),
  rating_district_representative = as.integer(d$districtrep), rating_election_chance = as.integer(d$electionchance),
  attr_surname = sub(" \\(not local\\)$", "", d$lastname), attr_party = cap(d$party), attr_gender = cap(d$cand_gender),
  attr_occupation = cap(d$cand_occupationtype), attr_residence = cap(d$cand_residencetype),
  cov_gender = ifelse(d$male == 1, "male", ifelse(d$male == 0, "female", NA_character_)), cov_age = as.integer(d$age),
  cov_education_level = cap(d$education_dum), cov_region = d$region, cov_urban = cap(d$urban_highdensity), cov_local_born = cap(d$local_born),
  cov_local_identity_index = d$localid_index, cov_attach_birth = as.integer(d$localattachment_politicianbirth),
  cov_attach_localknow = as.integer(d$localattachment_politicianlocalknow))
r[, attr_gender := tools::toTitleCase(attr_gender)]
r <- r[!(is.na(choice) & is.na(rating_trustworthy) & is.na(rating_local_knowledge) & is.na(rating_district_representative) & is.na(rating_election_chance))]  # rows with no outcome at all
setorder(r, id, task, profile)
fwrite(r, file.path(out, "leininger_2026_name_recognition.csv")); cat("rows", nrow(r), "resp", uniqueN(r$id), "\n")
