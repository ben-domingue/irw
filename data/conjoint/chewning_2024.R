##Campaign-volunteer conjoint (elite survey of 2020 US congressional and statewide campaigns) from
##Chewning, T. K., Green, J., Hassell, H. J. G., & Miles, M. R. (2024). Campaign principal-agent
##problems: Volunteers as faithful and representative agents. Political Behavior, 46(1), 405-426.
##https://doi.org/10.1007/s11109-022-09836-9
##Replication data: Harvard Dataverse doi:10.7910/DVN/VNUJM8, CC0 1.0, no restricted files.
##File read: clean_conjoint_values.csv (the authors' cleaned long conjoint file, one row per
##response x profile, level text in *_conjoint columns). Codebook: codebook.xlsx (level text,
##question wording, covariate codes). Read as text only: _README, conjoint_analysis.R, conjoint.do.
##Usage: Rscript chewning_2024.R <raw dir> <output dir>
##
##Survey of candidates and campaign staff/volunteers of 2020 campaigns (House, Senate, Governor,
##Lieutenant Governor), fielded Feb-Jun 2020 in four email waves (FSU/BYUI x Republican/Democratic
##campaigns). 233 survey responses (230 distinct hashed emails; 3 emails answered twice -- README:
##"more [rows] if the respondent took the survey twice"); 39 responses answered no conjoint task.
##id = survey response (ResponseId, re-keyed to integers in file order); cov_person links the 3
##repeat responses (hashed RecipientEmail re-keyed to integers; the hash itself is dropped).
##Each response made 3 choices between two volunteer profiles: conjoint_number 1-6 = profile
##number (codebook "Conjoint Volunteer profile number (k)"), task = (k + 1) %/% 2, profile = 2 - k %% 2.
##That pair numbering is the survey's; the README does not say the pairs were shown in that order.
##Attributes (level text = *_conjoint columns, as in codebook rows 89-106):
##  attr_gender Female / Male; attr_age 22 / 47 / 72; attr_race African-American / White /
##  Hispanic/Latino; attr_ideology Moderate / Strong Conservative / Strong Progressive;
##  attr_dedication Inconsistent in their effort level / No Information / Very dedicated and
##  consistent / Very dedicated and consistent in their effort level; attr_reliability
##  (source compliance_conjoint, codebook label "Reliability") Consistent and always follows
##  campaign instructions / Inconsistent in following campaign instructions / No Information.
##RESTRICTION (codebook): "Strong Conservative" was offered only to Republican campaigns and
##"Strong Progressive" only to Democratic campaigns (the authors pool them as "strong ideology");
##one table with cov_candidate_party because the authors pool both parties. The two
##"Very dedicated" strings both occur in every wave (159 vs 296 profiles); the codebook lists
##both under one level (ded_cons_vol); kept as stored.
##Outcome: choice = "Which of the following two individuals would you prefer to have work on
##your campaign as a volunteer?" (codebook), exactly one of the pair chosen in every answered
##task; 124 unanswered tasks (choice NA on both profiles) are dropped. No opt-out.
##Covariates, codes mapped to text from codebook.xlsx: cov_role ("Who is answering this
##survey?" I am the candidate / I am a paid member of the campaign staff / I am a volunteer
##member of the campaign staff), cov_gender ("What is your gender?" 1 Male, 2 Female, 3 Other),
##cov_ideology and cov_candidate_ideology (Very Liberal .. Very Conservative), cov_race (White /
##Not White), cov_experience (election cycles worked, 0-50), cov_volunteers ("about how many
##volunteers": None / 1-5 / 5-20 / More than 20), cov_office (from the email list),
##cov_incumbent (1 Incumbent, 0 Non-incumbent), cov_candidate_party (republican_candidate:
##Republican / Democratic). Dropped: ResponseId, RecipientEmail (hashed email), handle and FEC
##(hashed campaign identifiers), dates, status/progress/duration, primary_winner and the FEC /
##Twitter derived flags, scaled ideology and all *_vol dummies.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "clean_conjoint_values.csv"), na.strings = c("", "NA"))
stopifnot(r[, .N, ResponseId][, all(N == 6)], all(r$conjoint_number %in% 1:6))
r[, id := match(ResponseId, unique(ResponseId))]
r[, cov_person := match(RecipientEmail, unique(RecipientEmail))]
lab <- function(x, lv) { stopifnot(all(is.na(x) | x %in% seq_along(lv))); lv[x] }
d <- r[, .(id, task = (conjoint_number + 1L) %/% 2L, profile = 2L - conjoint_number %% 2L, choice,
  attr_gender = gender_conjoint, attr_age = as.character(age_conjoint), attr_race = race_conjoint,
  attr_ideology = ideology_conjoint, attr_dedication = dedication_conjoint, attr_reliability = compliance_conjoint,
  cov_person,
  cov_role = lab(Respondent, c("I am the candidate", "I am a paid member of the campaign staff", "I am a volunteer member of the campaign staff")),
  cov_gender = lab(Gender, c("male", "female", "other")),
  cov_ideology = lab(PersonalIdeology, c("Very Liberal", "Liberal", "Moderate", "Conservative", "Very Conservative")),
  cov_candidate_ideology = lab(CandidateIdeology, c("Very Liberal", "Liberal", "Moderate", "Conservative", "Very Conservative")),
  cov_race = lab(RespondentRace, c("White", "Not White")),
  cov_experience = as.integer(Experience),
  cov_volunteers = lab(VolNumbers, c("None", "1-5", "5-20", "More than 20")),
  cov_office = Office, cov_incumbent = as.integer(Incumbent),
  cov_candidate_party = c("Democratic", "Republican")[republican_candidate + 1L])]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
d <- d[!is.na(choice)]
stopifnot(d[, .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)],
          d[cov_candidate_party == "Republican", !any(attr_ideology == "Strong Progressive")],
          d[cov_candidate_party == "Democratic", !any(attr_ideology == "Strong Conservative")])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "chewning_2024_campaign_volunteers.csv"))
