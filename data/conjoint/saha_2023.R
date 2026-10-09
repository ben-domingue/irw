##Candidate conjoint (Study 2) from
##Saha, S. (2023). Why don't politicians talk about meat? The political psychology of
##human-animal relations in elections. Frontiers in Psychology, 14, 1021013.
##https://doi.org/10.3389/fpsyg.2023.1021013
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZDT7TW, CC0 1.0. File read: clean_dat.csv
##(the authors' cleaned long file; modeldata.RData is the separate one-factor Study 1 vignette,
##not a conjoint, and is not built). The authors' Saha_FrontiersRR_2023.R was read as text only.
##Usage: Rscript saha_2023.R <dir holding clean_dat.csv> <output dir>
##
##857 US adults (Dynata panel, quota-balanced on age, gender, ethnicity, region and party; article
##Methods), 5 tasks x 2 candidate profiles = 8,570 rows, as in the article. Respondents were told
##they would choose between candidates in their own party's presidential primary; they picked the
##candidate they "would be most likely to vote for in the presidential primary" (article wording;
##the deposit has no questionnaire). Forced choice, no opt-out: exactly one chosen per task (checked).
##Source `chosen` -> choice; source `choice` (the label "Candidate k" picked) agrees with it and is
##dropped. task = source `task`, profile = source `profile` (A = 1, B = 2).
##8 attributes (gender, diet, animal-rights support, race, pets, marital status, age, experience),
##stored as the text in the file. The article says each attribute was drawn independently and at
##random; attribute order is not described. No survey weight in the deposit.
##Covariates: cov_gender (Gender_ssi, panel profile Female/Male), cov_age (Age_ssi, panel profile, years),
##cov_region (census_region), cov_party_id (party_affiliation, panel profile text; blank = NA),
##cov_race (Race_ssi, text), cov_ideology (Q24 answer text; blank = NA), cov_party (Q25 answer text),
##cov_party_lean (Q27 answer text; the authors' code builds party from Q25 and Q27), cov_income (Q26
##answer text), cov_diet (Q30.1, "Yes, I'm vegan" / "Yes, I'm vegetarian" / "No, I'm neither").
##Question wordings of Q24-Q30 are not deposited; the answer texts make their topics plain.
##Dropped: Qualtrics ResponseId and the panel id `idp` (platform IDs), the free-text answer Q35,
##Q27_1, Q29_1, `empathy` and Q28_1 (wording and meaning not documented in the deposit), the row
##counters X, X.1 and `pair`. Respondent ids are the source `respondent` integers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "clean_dat.csv"), na.strings = c("", "NA"))
stopifnot(nrow(s) == 8570, uniqueN(s$respondent) == 857)
d <- data.table(id = as.integer(s$respondent), task = as.integer(s$task),
                profile = match(s$profile, c("A", "B")), choice = as.integer(s$chosen))
for (v in c("Gender", "Diet", "Animals", "Race", "Pets", "Marital", "Age", "Experience"))
  d[, paste0("attr_", tolower(v)) := as.character(s[[v]])]
stopifnot(!anyNA(d))
d[, `:=`(cov_gender = c(Female = "female", Male = "male")[s$Gender_ssi], cov_age = as.integer(s$Age_ssi),
         cov_region = s$census_region, cov_party_id = s$party_affiliation, cov_race = s$Race_ssi,
         cov_ideology = s$Q24, cov_party = s$Q25, cov_party_lean = s$Q27, cov_income = s$Q26, cov_diet = s$Q30.1)]
stopifnot(!anyNA(d$cov_gender), d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "saha_2023_meat_candidates.csv"))
