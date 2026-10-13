##Three German immigration-policy conjoints ("entry gates") from
##Helbling, M., Jäger, F., Maxwell, R., & Traunmüller, R. (2023). Broad and detailed
##agreement: Public preferences for German immigration policy. International Migration
##Review, 59(3), 1219-1232. https://doi.org/10.1177/01979183231216076
##Replication data: Harvard Dataverse doi:10.7910/DVN/JWPDYK, CC0 1.0, no restricted files.
##Files read: df_conj_fac.RData (data frame df_conj_fac: one row per respondent x contest x
##policy package) and data.RData (data frame data: respondent covariates), each loaded into
##its own environment. analysis.Rmd and the custom_functions/*.R (authors' code) read as text.
##The article is not open access and the deposit has no questionnaire, so outcome wording
##is a paraphrase and attribute text is the authors' English factor labels (respondents saw
##German; label_language en).
##Usage: Rscript helbling_2023.R <raw dir> <output dir>
##
##2,786 respondents in Germany (online panel; the deposit's sample_name distinguishes a
##Pretest, MainSampleFirstHalf, MainSampleSecondHalf and a 300Extra batch, all pooled in the
##authors' AMCEs; kept as cov_sample). Each respondent did 3 contests ("contest" 1-3) of two
##policy packages in each of three domains. The authors treat the domains as three separate
##factorial experiments (exp1/exp2/exp3 in analysis.Rmd, each with its own attributes and its own
##choice variable), so there are THREE TABLES:
##  helbling_2023_immigration_policy     choice = Immchoice, 10 attributes (attr_policy_goal,
##      attr_economic_requirement, attr_language_requirement, attr_integration_requirement,
##      attr_labor_market_requirement, attr_duration_work_permit, attr_renewal_work_permit,
##      attr_withdrawal_work_permit, attr_work_conditions_benefits, attr_change_job_sector)
##  helbling_2023_integration_policy     choice = Intchoice, 10 attributes (attr_policy_goal,
##      attr_required_time_residence, attr_economic_requirement, attr_language_requirement,
##      attr_integration_requirement, attr_renewal_residence_permit,
##      attr_withdrawal_residence_permit, attr_access_employment, attr_access_social_security,
##      attr_access_political_rights)
##  helbling_2023_naturalization_policy  choice = Natchoice, 9 attributes (attr_policy_goal,
##      attr_required_time_residence, attr_economic_requirement, attr_language_requirement,
##      attr_integration_requirement, attr_required_criminal_record, attr_withdrawal_citizenship,
##      attr_citizenship_descendents, attr_dual_citizenship)
##Attribute text = the factor labels in df_conj_fac (e.g. "Restrict immigration" / "Encourage
##immigration", "Advanced language skills" / "Basic language skills" / "None").
##Outcome: choice = which of the two packages the respondent prefers (paraphrase); exactly one
##chosen per contest, no opt-out. Contests with no answer (78 immigration, 78 integration,
##73 naturalization) are omitted.
##task = contest. PROFILE ORDER: the deposit does not record screen position; the two rows of a
##contest are numbered 1 and 2 in file order (an outcome-independent key: row 1 is chosen in
##50% of contests in each domain), profile_source = unknown. Whether the three domains were
##shown on the same screen, and in what order, is not documented.
##Randomization restrictions: none documented.
##Covariates (data.RData, answer text as stored, "-99" = NA): cov_gender (sex: Weiblich =
##female, Männlich = male, Divers = other), cov_birth_year (age_formated, a year of birth),
##cov_age_group (age_quota), cov_educ_quota (low / medium / high / Other, the quota
##education band), cov_party_pref (party_pref, vote intention text, incl. "Ich würde nicht
##wählen gehen"), cov_left_right (left_right, 0 "0 - links" ... 10 "10 - rechts" as text),
##cov_populism_1..12 (agreement text), cov_attention_pass (failed_attention_check: passed = 1,
##failed = 0; the authors keep failures in the main AMCEs), cov_control_exp_3 (failed / passed /
##NA as stored; meaning not documented), cov_sample.
##Dropped: derived left_right_clear, left_right_cat. resp_id is the authors' integer id, kept.
##One respondent in df_conj_fac has no covariate row (covariates NA).
##N vs paper: not checked (paywalled); df_conj_fac has 2,786 respondents, data.RData 2,785.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "df_conj_fac.RData"), envir = e); load(file.path(raw, "data.RData"), envir = e)
x <- as.data.table(e$df_conj_fac); y <- as.data.table(e$data)
x[, profile := rowid(resp_id, contest)]
stopifnot(x[, .N, .(resp_id, contest)][, all(N == 2)], x[, .N, resp_id][, all(N == 6)], !anyDuplicated(y$resp_id))
na99 <- function(v) { v <- as.character(v); v[v == "-99"] <- NA; v }
cv <- y[, .(id = resp_id, cov_gender = c(Weiblich = "female", "Männlich" = "male", Divers = "other")[na99(sex)],
            cov_birth_year = as.integer(age_formated), cov_age_group = age_quota, cov_educ_quota = as.character(educ_quota),
            cov_party_pref = na99(party_pref), cov_left_right = na99(left_right),
            cov_attention_pass = as.integer(c(passed = 1L, failed = 0L)[failed_attention_check]),
            cov_control_exp_3 = failed_control_exp_3, cov_sample = sample_name)]
for (k in 1:12) cv[, paste0("cov_populism_", k) := na99(y[[paste0("populism_", k)]])]
stopifnot(!anyNA(cv$cov_attention_pass), all(is.na(y$sex) | y$sex %in% c("-99", "Weiblich", "Männlich", "Divers")))
an <- c(Policygoal = "policy_goal", Economicrequirement = "economic_requirement", Languagerequirement = "language_requirement",
        Integrationrequirement = "integration_requirement", Labormarketrequirement = "labor_market_requirement",
        Durationworkpermit = "duration_work_permit", Renewalworkpermit = "renewal_work_permit",
        Withdrawalworkpermit = "withdrawal_work_permit", Workconditionsandbenefits = "work_conditions_benefits",
        Changejobsector = "change_job_sector", Requiredtimeresidence = "required_time_residence",
        Renewalresidencepermit = "renewal_residence_permit", Withdrawalresidencepermit = "withdrawal_residence_permit",
        Accessemployment = "access_employment", Accesssocialsecurity = "access_social_security",
        Accesspoliticalrights = "access_political_rights", Requiredcriminalrecord = "required_criminal_record",
        Withdrawalcitizenship = "withdrawal_citizenship", Citizenshipdescendents = "citizenship_descendents",
        Dualcitizenship = "dual_citizenship")
exps <- list(immigration = "Imm", integration = "Int", naturalization = "Nat")
for (nm in names(exps)) {
  p <- exps[[nm]]
  ac <- grep(paste0("^", p, "[A-Z]"), names(x), value = TRUE)
  stopifnot(all(sub(p, "", ac) %in% names(an)))
  d <- x[, c("resp_id", "contest", "profile", paste0(p, "choice"), ac), with = FALSE]
  setnames(d, c("id", "task", "profile", "choice", paste0("attr_", an[sub(p, "", ac)])))
  for (v in grep("^attr_", names(d), value = TRUE)) d[, (v) := as.character(get(v))]
  d <- d[!is.na(choice)]
  stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d))
  d <- merge(d, cv, by = "id", all.x = TRUE)
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, sprintf("helbling_2023_%s_policy.csv", nm)))
}
