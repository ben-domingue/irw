##Candidate-pair conjoint (UK and France) from
##Coffe, H., Saha, S., & Weeks, A. C. (2024). Quotas or parity? How the framing of positive action measures
##impacts public support and backlash. Journal of European Public Policy, 32(10), 2409-2438.
##https://doi.org/10.1080/13501763.2024.2402864
##Replication data: Harvard Dataverse doi:10.7910/DVN/KH0SQ2, CC0 1.0. Files read: yougov_uk_conjoint.RData
##(object `long`, UK, 3,468 rows = 1,734 respondents x 2 profiles) and FRCONJdataset.RData (object `long`, France,
##2,076 rows = 1,038 x 2), each loaded into its own environment; main.R read as text.
##Usage: Rscript coffe_2024.R <dir holding the .RData files> <output dir>
##Writes two tables (the authors analyse the UK and France samples separately, so no pooled table):
##  coffe_2024_quota_uk  and  coffe_2024_quota_fr
##Design: one task per respondent (task = 1; profiles A = 1 and B = 2 as the file's `profile` column), a pair of
##hypothetical parliamentary candidates described by seven attributes: gender, marital status, policy priority,
##political experience, age, career, personal skill. Levels are the English label text of the files; the UK sample
##(YouGov) saw English, the French sample presumably French (the French display text is not deposited, labels
##are the authors' English ones). Before the conjoint respondents were randomized to a framing of positive-action
##measures (Control / Parity / Quota); that arm is kept as trial_framing (it is a treatment on the respondent, not an
##attribute of a profile).
##Outcomes (question wording is NOT in the deposit; paraphrases):
##  choice: which of the two candidates the respondent chose ("Candidate 1" / "Candidate 2"; source `choice`
##    text, `choice2` is the 0/1 version and agrees). Forced choice, no opt-out.
##  rating_qualified: how qualified the respondent thought this candidate to be an MP, 1-11 (source
##    `Qualified_score` = qualifiedA for profile A, qualifiedB for profile B; verified); anchors not in deposit
##    (main.R names it "Perceived 'Qualified to be an MP' (1-11)"; higher = more qualified assumed).
##Randomization restrictions and level probabilities are not documented (levels are near-equally frequent).
##Covariates: cov_gender (source resp_gender text), cov_age (years), cov_education (resp_education, answer text
##of the source's categories), cov_party_id (UK only, resp_party text, "Don't Know" kept as answer text; France
##has no party item), cov_survey_weight (source Weight; the authors weight in their models). Dropped: other
##survey experiments in the same file (list experiments, framing items, attitude batteries), social class,
##ethnicity, region, vote. IDs re-keyed to integers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ld <- function(f) { e <- new.env(); load(file.path(raw, f), envir = e); stopifnot(identical(ls(e), "long")); as.data.table(e$long) }
mk <- function(s, name, party) {
  s[, profile_n := match(profile, c("A", "B"))]
  stopifnot(all(s$task == 1), !anyNA(s$profile_n), s[, .N, ID][, all(N == 2)],
            all(s$Qualified_score == ifelse(s$profile == "A", s$qualifiedA, s$qualifiedB)),
            all(s$choice2 == (as.integer(sub("Candidate ", "", s$choice)) == s$profile_n)))
  d <- s[, .(id = as.integer(factor(ID)), task = 1L, profile = profile_n, choice = as.integer(choice2),
    rating_qualified = as.integer(Qualified_score),
    attr_gender = as.character(feature1), attr_marital_status = as.character(feature2), attr_policy = as.character(feature3),
    attr_experience = as.character(feature4), attr_age = as.character(feature5), attr_career = as.character(feature6),
    attr_skill = as.character(feature7),
    cov_gender = tolower(as.character(resp_gender)), cov_age = as.integer(resp_age),
    cov_education = as.character(resp_education), cov_survey_weight = Weight, trial_framing = as.character(Treatment))]
  if (party) d[, cov_party_id := as.character(s$resp_party)]
  stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]), d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv"))); cat(name, uniqueN(d$id), nrow(d), "\n")
}
mk(ld("yougov_uk_conjoint.RData"), "coffe_2024_quota_uk", TRUE)
mk(ld("FRCONJdataset.RData"), "coffe_2024_quota_fr", FALSE)
