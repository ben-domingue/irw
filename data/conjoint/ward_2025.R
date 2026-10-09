##South Korean candidate-choice conjoint from
##Ward, P., & Denney, S. (2025). Partisan voters in party systems with ephemeral parties:
##Evidence from South Korea. Party Politics. https://doi.org/10.1177/13540688251339976
##Replication data: Harvard Dataverse doi:10.7910/DVN/3N4UFF (v2), CC0 1.0, no restricted files.
##Files read: final_df_conjoint.csv (long, 20 rows per respondent), data_dictionary_conjoint.csv
##and README.md (deposit). Design facts and wording from the authors' working paper
##(29 Aug 2024, sinonk.com; text, Table 1, Appendix A-B); the published article was not
##reachable. No questionnaire is deposited.
##Usage: Rscript ward_2025.R <raw dir> <output dir>
##
##Qualtrics online panel, South Korea, January-February 2024 (paper: n = 2,006; deposit: 2,005).
##Each respondent saw 10 paired tasks of hypothetical candidates with 10 attributes (age,
##origin, gender, career, scandal + labor, housing, social, foreign and nuclear policy) and
##"asked to choose which among them they support the most" (paraphrase; forced choice, no
##opt-out; exactly one chosen per task, checked). task/profile = the deposit's question_profile
##("t.p", recorded). Half the sample was told the candidates ran in a general election and half
##in a presidential election (randomized); that arm is NOT in the deposit, so it is not here.
##Respondents saw Korean text; attr_ keep the authors' English labels from the deposit (which
##word some levels differently from the paper's Table 1, e.g. "Female"/"Male" vs "Woman"/"Man").
##Paper: personal attributes are shown together and "the order within the personal
##characteristics and all other attributes and values are randomly assigned without
##constraints" -> restrictions none; whether row order was randomized is ambiguous and is not
##recorded. Age levels 40/55/70 are years (text).
##Dropped: 22 respondents (440 rows) whose `chosen` is empty (README: their Qualtrics responses
##could not be matched), leaving 1,983 respondents; open_text_reason (free text, task-6 "why"
##answer); the Qualtrics ResponseId (R_...; re-keyed to integers in file order).
##Covariates (text as deposited): cov_gender (resp_gender Female/Male, "What was your assigned sex
##at birth?"), cov_age (resp_age, years; 4 respondents NA), cov_education (education, deposit's
##English category text), cov_region (region of residence, grouped by the authors),
##cov_polid_numeric (political identification on a numeric 1-10 scale; the deposit does not say
##which end is left, so codes kept), cov_party_preference (preferred political party; kept under its
##own name: the dictionary says "preferred party", not party identification), cov_prez_vote (vote in
##the 2022 presidential election, text as deposited, two answers in Korean: 다른 후보 = another
##candidate, 심상정 = Sim Sang-jung), cov_alt_dv_* (direct policy-preference questions, Appendix B
##"For each policy, please select the one option with which you most agree"), and
##cov_party_of_task1_choice (manipulation_check1: after task 1, which party the respondent thought
##the chosen candidate belonged to: Conservative / Progressive / Other).
##No survey weight is documented or deposited.
##Spot check: marginal mean of age 70 = 0.45 (paper: "Only 45 percent of profiles with an older
##candidate were preferred").
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "final_df_conjoint.csv"), colClasses = list(character = c("question_profile", "chosen")), encoding = "UTF-8")
stopifnot(nrow(s) == 40100L, s[, .N, respondent_id][, all(N == 20)])
s <- s[chosen != ""]
s[, id := match(respondent_id, unique(respondent_id))]
tp <- tstrsplit(s$question_profile, ".", fixed = TRUE)
d <- data.table(id = s$id, task = as.integer(tp[[1]]), profile = as.integer(tp[[2]]), choice = as.integer(s$chosen))
stopifnot(all(d$task %in% 1:10), all(d$profile %in% 1:2), d[, .N, .(id, task)][, all(N == 2)])
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
at <- c(age = "age_attribute", origin = "origin", gender = "gender_attribute", career = "career", scandal = "scandal",
        labor_policy = "labor_policy", housing_policy = "housing_policy", social_policy = "social_policy",
        foreign_policy = "foreign_policy", nuclear_policy = "nuclear_policy")
for (v in names(at)) { x <- as.character(s[[at[[v]]]]); stopifnot(!anyNA(x), all(x != "")); d[, paste0("attr_", v) := x] }
stopifnot(all(s$resp_gender %in% c("Female", "Male")))
d[, cov_gender := tolower(s$resp_gender)]
d[, cov_age := as.integer(s$resp_age)]
d[, cov_education := s$education]
d[, cov_region := s$region]
d[, cov_polid_numeric := as.integer(s$polid_numeric)]
d[, cov_party_preference := s$party_preference]
d[, cov_prez_vote := s$prez_vote]
for (v in c("realestate", "foreign_policy", "nuclear_policy", "labor_policy", "social_policy")) d[, paste0("cov_alt_dv_", v) := s[[paste0("alt_dv_", v)]]]
d[, cov_party_of_task1_choice := s$manipulation_check1]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ward_2025_korean_candidates.csv"))
