##Direct-air-capture facility siting conjoint (US national survey) from
##Scott-Buechler, C., Cain, B., Osman, K., Ardoin, N., Fraser, C., Adcox, G., Polk, E., &
##Jackson, R. B. (2024). Communities conditionally support deployment of direct air capture for
##carbon dioxide removal in the United States. Communications Earth & Environment, 5.
##https://doi.org/10.1038/s43247-024-01334-6
##Replication data: Harvard Dataverse doi:10.7910/DVN/SU4MEG, CC0 1.0. Files read:
##conjoint_long.csv (283 MB; only the columns named below are read), README.rtf, "README - File
##Organization.rtf", "1_Full Survey.docx" (Qualtrics export of the questionnaire). Read as text, not
##run: 1_cleaning.R, 4_conjoint_fig2.R.
##Usage: Rscript scottbuechler_2024.R <dir holding conjoint_long.csv> <output dir>
##
##US online national survey ("DAC Conjoint - JAN 23 Adult Universe", fielded January 2023).
##conjoint_long.csv holds the authors' CLEANED sample (1_cleaning.R: finished, passed the attention
##check, fastest 5% removed, age >= 18): 1,195 respondents x 13 tasks x 2 plans = 31,070 rows.
##The 2,198-row raw file (NEWEST_DAC_survey_only.csv) has no conjoint columns, so the excluded
##respondents cannot be added.
##Design: Qualtrics/Sawtooth-style CBC block (embedded data *_CBCONJOINT, vers_CBCONJOINT): a FIXED
##design in 210 versions, one per respondent (trial_version); each version x task x plan has one
##profile. 13 tasks, 2 plans ("Direct Air Capture Plant 1/2"), 7 attributes, rows in the fixed
##order of the questionnaire grid: Funding Source, Project developer & owner, Energy source,
##Community involvement in project planning & implementation, Carbon dioxide storage &
##transportation, Share of project costs reinvested in community (i.e. for schools & roads), Job
##creation. No task repeats another. 476 of 15,535 tasks show two plans with the same funding and
##owner (allowed by the design).
##task = number of C1..C13 ("(k/13)" in the questionnaire, recorded); profile = Option (Opt1/Opt2).
##Outcome: choice, C1..C13 "Imagine that a DAC project is being sited in your community. You will be
##presented with simplified project plans for the new DAC facility. Please choose which plan you
##prefer from each pair." answer (1) / (2) = plan 1 / plan 2; forced, no opt-out.
##IMPORTANT: the deposit's long-format `Choice` column is NOT used. It is 1 on every Opt1 row and 0 on
##every Opt2 row (15,535/15,535), i.e. it marks the first plan, not the answer; the answers are the
##wide C1..C13 columns repeated on every row, and the six attributes that also appear in wide form
##(C<k>_Opt<p>_Owner ... _Jobs) equal the long columns on every row (checked). Funding exists only in
##the long columns.
##Attribute text as stored (= the CBC level text).
##Covariates (answer text as stored): cov_gender (Female/Male -> female/male), cov_age (the authors'
##Age, computed in 1_cleaning.R from the full date of birth; the date of birth itself is NOT kept),
##cov_education, cov_party (Partisanship: "Generally speaking, do you think of yourself as a ...";
##Democrat/Republican/Independent/Something else; not a party ID scale, so not cov_party_id),
##cov_party_lean (PartisanshipPush), cov_ideology, cov_state, cov_race, cov_hispanic, cov_income,
##cov_duration_sec, cov_survey_weight (the authors' `nationalweight`, raked to ACS 2021 PUMS on
##gender, age, race, Hispanic origin, education and region in 1_cleaning.R; used in their AMCEs).
##Dropped (PII or panel ids): ResponseId (re-keyed 1..n in file order), ZipCode, ps_zip, psid,
##SupplierID, BirthDate (full date of birth), OpenEnd (free text); and everything else.
##Spot check (weighted lm, SEs clustered by id): with the recorded answers, community members'
##direct voting power vs "No consultation" +0.081 (SE 0.011), long-term local jobs +0.16-0.17,
##20% of costs reinvested vs none +0.125; the same model on the deposit's `Choice` (= first-plan
##flag) gives estimates near 0 (-0.025 to +0.010). The article's Figure 2 (as corrected: "high
##benefits" -0.006, SE 0.007) looks like the latter; not checked further.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
att <- c("Funding", "Owner", "Energy", "Community", "Storage", "Benefits", "Jobs")
s <- fread(file.path(raw, "conjoint_long.csv"), select = c("ResponseId", "Conjoint", "Option", att, "Choice", "vers_CBCONJOINT",
  paste0("C", 1:13), paste0("C", rep(1:13, each = 12), "_Opt", rep(rep(1:2, each = 6), 13), "_", att[-1]),
  "Gender", "Age", "Education", "Partisanship", "PartisanshipPush", "Ideology", "State", "Race", "Hispanic", "Income",
  "nationalweight", "Duration (in seconds)"))
stopifnot(nrow(s) == 31070, uniqueN(s$ResponseId) == 1195)
s[, task := as.integer(sub("^C", "", Conjoint))][, profile := as.integer(sub("^Opt", "", Option))]
ans <- s[, .(ans = as.integer(.SD[[paste0("C", task[1])]][1])), .(ResponseId, task)]
stopifnot(ans[, all(ans %in% 1:2)], s[, all(Choice == as.integer(profile == 1))])
for (a2 in att[-1]) stopifnot(s[, all(get(a2) == mapply(function(i, t, p) s[[sprintf("C%d_Opt%d_%s", t, p, a2)]][i], .I, task, profile))])
s <- merge(s, ans, by = c("ResponseId", "task"), sort = FALSE)
s[, id := match(ResponseId, unique(ResponseId))]
d <- s[, .(id, task, profile, choice = as.integer(ans == profile),
           attr_funding = Funding, attr_owner = Owner, attr_energy = Energy, attr_community = Community,
           attr_storage = Storage, attr_benefits = Benefits, attr_jobs = Jobs, trial_version = as.integer(vers_CBCONJOINT),
           cov_gender = c(Female = "female", Male = "male")[Gender], cov_age = as.integer(Age), cov_education = Education,
           cov_party = Partisanship, cov_party_lean = fifelse(PartisanshipPush == "", NA_character_, PartisanshipPush),
           cov_ideology = Ideology, cov_state = State, cov_race = Race, cov_hispanic = Hispanic, cov_income = Income,
           cov_duration_sec = as.integer(`Duration (in seconds)`), cov_survey_weight = nationalweight)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          unique(d[, .(trial_version, task, profile, attr_funding, attr_owner, attr_energy, attr_community, attr_storage, attr_benefits, attr_jobs)])[, .N, .(trial_version, task, profile)][, all(N == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "scottbuechler_2024_dac_siting.csv"))
