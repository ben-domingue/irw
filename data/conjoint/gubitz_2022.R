##Incivility vignette conjoint (US, white non-Hispanic respondents) from
##Gubitz, S. R. (2022). Race, gender, and the politics of incivility: How identity moderates
##perceptions of uncivil discourse. The Journal of Race, Ethnicity, and Politics, 7(3),
##526-543. https://doi.org/10.1017/rep.2022.7 (corrigendum doi:10.1017/rep.2022.15, not read)
##Replication data: Harvard Dataverse doi:10.7910/DVN/ODPNI8, CC0 1.0, no restricted files,
##no terms. File read: "Gubitz reshaped.tab" (Dataverse "original format" download: the
##author's long file, one row per respondent x scenario, with displayed level text). Read as
##text: "srg cleaning.R" (how the file was made, sample filter), "OLS analysis.R", "Survey
##text.docx" (Qualtrics instrument, converted to text). The article (paywalled) was not read.
##Usage: Rscript gubitz_2022.R <raw dir> <output dir>
##
##450 respondents (Bovitz/Forthright online panel; the consent form says "about 450 people";
##the author kept consenting, White, non-Latino respondents: srg cleaning.R filter consent ==
##1 & race == 1 & Latino == 2). Each read 6 one-sentence "excerpts from recent newspaper
##articles" (task = iteration 1-6, profile = 1), built from embedded-data fields (instrument):
##  "<Headline>" / "<SParty> <SJob> <SF> <SL> told a <TParty> <TJob>, <TF> <TL>, that <TL>
##  was <Incivility> during last night's town hall meeting."
##and, when speaker and target share a party (trial_fellow_partisan = 1, the author's `sym`),
##"...told a <TJob>, <TF> <TL>, a fellow <TSym>, that ..." (TSym = Democrat/Republican).
##attr_ columns hold the displayed field text: attr_headline (Police: "Recent Townhall Meeting
##Turns Uncivil" / "Details From Recent Townhall Meeting"), attr_speaker_party / attr_target_party
##("Democratic"/"Republican"; in the fellow-partisan wording the target party was shown as
##"a fellow Democrat|Republican"), attr_speaker_job / attr_target_job (Representative or one
##of 10 occupations), attr_speaker_first_name, attr_speaker_last_name, attr_target_first_name,
##attr_target_last_name, attr_incivility (14 insults/threats/slurs as shown, e.g. "a 'moron'",
##"going to 'get punched'"). Race and gender of speaker and target were signalled only by the
##names; the author's coding of the drawn names is kept as trial_speaker_race,
##trial_speaker_gender, trial_target_race, trial_target_gender (White/Black, Male/Female).
##6 tasks have sym = 0 although both parties are equal (kept as recorded).
##Outcomes (instrument wording; stored raw, higher = more):
##  rating_uncivil "How uncivil do you think the above scenario was?" 1 Not at all uncivil ..
##    5 Very uncivil (the article's outcome);
##  rating_newsworthy "How newsworthy do you think the above scenario was?" 1 Not at all
##    newsworthy .. 5 Very newsworthy.
##The fellow-partisan block asked the same items (uncivilsym/newssym), merged by the author.
##Dropped: the six PANAS emotion items (PANAS1-6): the instrument lists the emotions with
##codes 2,3,4,5,6,8 while the file has indexes 1-6, so which column is which emotion is not
##documented. One scenario row with neither outcome is omitted; 13 more lack rating_newsworthy
##(kept, NA). 2,699 rows.
##Covariates (instrument codes -> text): cov_age (age), cov_gender ("What is your gender?" 1
##Male = male, 2 Female = female, 3 "Other/prefer not to say" = NA since it mixes other and
##refusal: 24 respondents), cov_education (education text), cov_income (income text),
##cov_party_id (pid1: Democrat/Republican/Independent), cov_party_id7 (the author's pid built
##from pid1/piddem/pidrep/pidlean in srg cleaning.R, as text: Strong Democrat .. Strong
##Republican), cov_ideology (7-point text), cov_therm_dem / cov_therm_rep (negparty 0-100
##feeling thermometers), cov_duration_sec (whole survey, "Duration (in seconds)").
##Dropped: identity, racial-resentment, sexism, SDO and system-justification items (GID, White,
##PSI*, RR, sex, SDO, SJ) and Qualtrics metadata.
##PII: the deposited files (raw, reshaped and cleaned) contain IPAddress, LocationLatitude/
##LocationLongitude and ResponseId; all dropped. Respondents re-keyed to integers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "reshaped.csv"), encoding = "UTF-8")
stopifnot(nrow(k) == 2700L, uniqueN(k$RESPONDENT_ID) == 450L, k[, .N, RESPONDENT_ID][, all(N == 6)])
ids <- unique(k$RESPONDENT_ID)
d <- data.table(id = match(k$RESPONDENT_ID, ids), task = as.integer(k$iteration), profile = 1L,
                rating_uncivil = as.integer(k$uncivil), rating_newsworthy = as.integer(k$news),
                attr_headline = k$Police, attr_speaker_party = k$SParty, attr_speaker_job = k$SJob,
                attr_speaker_first_name = k$SF, attr_speaker_last_name = k$SL,
                attr_target_party = k$TParty, attr_target_job = k$TJob,
                attr_target_first_name = k$TF, attr_target_last_name = k$TL, attr_incivility = k$Incivility,
                trial_fellow_partisan = as.integer(k$sym),
                trial_speaker_race = k$SRace, trial_speaker_gender = k$SGender,
                trial_target_race = k$TRace, trial_target_gender = k$TGender)
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), all(d[, .SD, .SDcols = patterns("^attr_")] != ""),
          all(d$rating_uncivil %in% c(NA, 1:5)), all(d$rating_newsworthy %in% c(NA, 1:5)),
          k[sym == 1, all(TSym == sub("ic$", "", TParty))], !anyDuplicated(d[, .(id, task)]))
pid7 <- with(k, fcase(piddem == 1, "Strong Democrat", piddem == 2, "Not so strong Democrat",
                      pidlean == 1, "Independent, closer to the Democratic Party", pidlean == 3, "Independent, neither",
                      pidlean == 2, "Independent, closer to the Republican Party",
                      pidrep == 2, "Not so strong Republican", pidrep == 1, "Strong Republican"))
stopifnot(all(k$gender %in% 1:3), all(k$education %in% 1:6), all(k$income %in% c(NA, 1:5)),
          all(k$pid1 %in% 1:3), all(k$ideology %in% c(NA, 1:7)))
d[, `:=`(cov_age = as.integer(k$age), cov_gender = c("male", "female", NA)[k$gender],
         cov_education = c("Less than high school", "High school graduate", "Some college", "2 year degree",
                           "4 year degree", "Advanced degree")[k$education],
         cov_income = c("< $30,000", "$30,000 - $69,999", "$70,000 - $99,999", "$100,000 - $200,000", "> $200,000")[k$income],
         cov_party_id = c("Democrat", "Republican", "Independent")[k$pid1], cov_party_id7 = pid7,
         cov_ideology = c("Very liberal", "Liberal", "Slightly liberal", "Moderate, or middle of the road",
                          "Slightly conservative", "Conservative", "Very conservative")[k$ideology],
         cov_therm_dem = as.integer(k$negparty_dem), cov_therm_rep = as.integer(k$negparty_rep),
         cov_duration_sec = as.integer(k$`Duration (in seconds)`))]
d <- d[!(is.na(rating_uncivil) & is.na(rating_newsworthy))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gubitz_2022_incivility.csv"))
