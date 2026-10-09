##CDU candidate / far-right cooperation conjoint (Germany) from
##Gross, M., Juen, C.-M., & Stecker, C. (2026). The cordon dilemma: How voters evaluate
##cooperation with the far-right in parliament. Comparative Political Studies.
##https://doi.org/10.1177/00104140261448429
##Replication data: Harvard Dataverse doi:10.7910/DVN/NPYXMK, CC0 1.0. File read:
##data/survey_cj.rds (long, one row per respondent x conjoint round x profile, plus one row for
##each respondent without conjoint data). codebooks/analysis_codebook.csv,
##tables/Table_1_conjoint_attributes_and_levels.csv (English translation of the levels),
##Table_2_example_choice_situation.csv and cordon_dilemma_replication.Rmd were read as text.
##Usage: Rscript gross_2026.R <dir holding survey_cj.rds> <output dir>
##
##German online survey (Qualtrics, 9 Aug - 20 Sep 2024, German; samples from Saxony, Thuringia
##and Western Germany, pooled by the authors with region as a moderator: one table, region in
##cov_survey_region). 2,773 respondents did the conjoint: 3 rounds (cjround) of 2 hypothetical
##CDU candidates (cjprofile), 7 attributes: age (28/34/47/54/67), gender (männlich/weiblich),
##political experience, refugee immigration cap, income and wealth differences should...,
##Ukraine should..., (non-)cooperation with the AfD. Levels are the German text stored in the
##deposit (e.g. "keine Zusammenarbeit", "Koalition mit AfD denkbar"); the authors' Table 1 gives
##longer English renderings ("would not be open for cooperation with the AfD", "would form
##coalition with the AfD"), so the screen probably showed fuller sentences than the stored
##labels; the stored German is used as is. Attribute order and randomization rules are not
##documented.
##Outcomes (wording not deposited; paraphrase from the codebook labels):
##  choice = cj_elect "Candidate choice" (0/1; no opt-out). In 45 rounds neither profile is
##    chosen and both ratings are NA: the source codes an unanswered round 0/0 (the wide
##    survey.rds has fewer non-missing cjr<k>_elect in later rounds: 2,773 / 2,756 / ...).
##    These 45 rounds are dropped as having no outcome.
##  rating = cj_skalo "Candidate thermometer", -5..+5 as stored (the survey's party/politician
##    thermometers use the same -5..+5 scale; higher = more positive); 90 profile ratings are
##    missing (NA, row kept for its choice).
##The authors analyse respondents who passed the attention check (Rmd L55) with complete
##cases: all 2,773 conjoint respondents in the deposit passed it (cov_attention_pass is 1
##throughout; the failed checks belong to respondents without conjoint rows).
##Covariates: cov_age (years; values outside 18-99 would be set NA: none among conjoint respondents), cov_gender
##(Weiblich/Männlich/Divers -> female/male/other), cov_education (edu, German answer text),
##cov_survey_region (survey_bland: Sachsen/Thüringen/Westdeutschland), cov_state (bland),
##cov_vote_state (vote_ltw, state-election vote intention, answer text), cov_vote_federal
##(vote_btw), cov_lr_self (lire_self, 1 ganz links .. 11 ganz rechts, as text),
##cov_thermometer_afd (skalo_parties_afd, -5..5), cov_attention_pass (attention_check:
##"passed (= stimme eher zu)" = 1, failed = 0), cov_duration_sec (whole survey).
##Dropped: m (a panel member id; some values repeat across ResponseIds), ResponseId (Qualtrics
##id, re-keyed 1..N in order of first appearance), browser fields (all empty), the separate
##vignette items (vig_*), all other attitude batteries.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "survey_cj.rds")))
s <- s[!is.na(cjround)]
s[, id := match(ResponseId, unique(ResponseId))]
stopifnot(uniqueN(s$id) == 2773, s[, .N, id][, all(N == 6)])
ch <- function(x) as.character(x)
d <- s[, .(id, task = as.integer(cjround), profile = as.integer(cjprofile), choice = as.integer(cj_elect),
           rating = as.integer(cj_skalo),
           attr_age = ch(cj_age), attr_gender = ch(cj_geschlecht), attr_experience = ch(cj_experience),
           attr_refugee_immigration = ch(cj_immi), attr_income_differences = ch(cj_redis),
           attr_ukraine = ch(cj_ukraine), attr_afd_cooperation = ch(cj_afdtreatment),
           cov_age = fifelse(age >= 18 & age <= 99 & age == round(age), as.integer(age), NA_integer_),
           cov_gender = c(Weiblich = "female", "Männlich" = "male", Divers = "other")[ch(gender)],
           cov_education = ch(edu), cov_survey_region = survey_bland, cov_state = ch(bland),
           cov_vote_state = ch(vote_ltw), cov_vote_federal = ch(vote_btw), cov_lr_self = ch(lire_self),
           cov_thermometer_afd = as.integer(skalo_parties_afd),
           cov_attention_pass = as.integer(attention_check == "passed (= stimme eher zu)"),
           cov_duration_sec = as.integer(duration_sec))]
d[, nch := sum(choice), .(id, task)]
stopifnot(d[nch == 0, all(is.na(rating))], d[, all(nch <= 1)])
d <- d[nch == 1][, nch := NULL]
stopifnot(!anyNA(d[, .(choice)]), !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% c(-5:5, NA)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gross_2026_cordon_dilemma.csv"))
