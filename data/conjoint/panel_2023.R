##Technocratic-minister conjoint (France, Germany, Italy, Poland, Spain, UK) from
##Panel, S., Paulis, E., Pilet, J.-B., Rojon, S., & Vittori, D. (2023). The lure of technocrats:
##a conjoint experiment on preferences for technocratic ministers in six European countries.
##Political Behavior, 46, 1961-1984. https://doi.org/10.1007/s11109-023-09904-8
##Replication data: Harvard Dataverse doi:10.7910/DVN/RZTIOY, CC0 1.0, no restricted files, no
##terms. Files read: TechnocratsData.tab (117 MB; only the columns used are read), Codebook.pdf.
##ReplicationCode.do read as text. No questionnaire is deposited.
##Usage: Rscript panel_2023.R <dir holding TechnocratsData.tab> <output dir>
##
##9,692 respondents (online survey, Qualtrics-style export; StartDate 21 June - 28 August 2021;
##1,558-1,670 per country; the article's Ns were not checked, it is paywalled), each doing 5
##paired forced-choice tasks, one per post: Prime Minister and the Ministers of Finance, Foreign
##Affairs, Agriculture and Education. Task numbers follow the codebook's vignette pairs (= the
##order of questions Q12-Q16); whether the posts were shown in that order is not documented. Codebook: `vignette` 1-10, odd =
##profile shown on the LEFT, even = RIGHT; pairs 1-2 PM, 3-4 Finance, 5-6 Foreign, 7-8
##Agriculture, 9-10 Education. So task = (vignette + 1) / 2 and profile = 1 (left) / 2 (right),
##both RECORDED. Outcome `selected` = the profile chosen as preferred (wording not deposited;
##codebook: "chosen as the respondent's preferred profile"); forced choice, exactly one per task
##(checked; Q12-Q16 = 1/2 agree with it). trial_post = the post of the task.
##One table per country, as the authors estimate every model separately by country
##(ReplicationCode.do, `if ... Country==`). The deposit stores one English text for all
##countries (label_language en); the language shown outside the UK is not documented (no
##questionnaire), though presumably the national language. Tables
##panel_2023_technocrats_{fr,de,it,pl,es,uk}.
##Attributes (English strings as stored, whitespace trimmed): age (40/65), gender, education
##(constant "Phd" on every profile; kept since it is displayed), parents' occupations
##(class background), occupation (levels depend on the post: e.g. "Minister of Agriculture (Rural
##Affairs)" only for Agriculture; RESTRICTIONS yes), party member (Yes/No), accountability ("would
##take decisions ... that are widely supported by citizens / by Members of Parliament / based on
##his/her knowledge and expertise"; the stem is not deposited), policy position (two per post,
##each post-specific). Some levels have two spellings
##in the source (e.g. "Mother = home help, ..." on 33 UK rows; "Head of an accounting firm" vs
##"CEO of an accounting firm"; "ministry of justice" lower case); kept as stored.
##Dropped: the 3 tasks (6 rows, 2 Italian respondents) whose attribute text is blank in the
##source (not saved). Derived codes (occupation, expertise, class, match, gendernum, party,
##account2) and the per-variable weight components are dropped.
##Covariates: cov_gender (Q1_Gender Male/Female/Other -> male/female/other), cov_age_group
##(Q2_Age text), cov_education (Q4_Education text), cov_survey_weight (ALL_weights: codebook
##"sampling weights ... based on sex, age, region, and educational attainment"; equals the
##country's own <CC>_weights; NA for 33 respondents), cov_attention_pass (Q17: 0 if "Minister of
##Sport", the codebook's failure answer; 1 for any other minister; NA for the 74 respondents
##coded "Failed for softlaunch respondents", whose check was not a regular answer),
##cov_duration_sec (whole survey), cov_issue_priority_1..4 (Q33, Foreign Affairs, Education,
##Agriculture, Finance; text), cov_policy_pref_1..10 (Q34/Q35, text; the 10 policies of the
##codebook). PII: Qualtrics ResponseId re-keyed to integers; Q3_Region not kept.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
pp <- c(paste0("Q34_PolicyPref_", 1:5), paste0("Q35_PolicyPref_", 6:10))
ip <- paste0("Q33_IssuePriority_", 1:4)
am <- c(minage = "age", mingender = "gender", mineduc = "education", minparents = "parents", minoccup = "occupation",
        minparty = "party_member", minaccount = "accountability", minpolicy = "policy")
x <- fread(file.path(raw, "TechnocratsData.tab"), encoding = "UTF-8",
           select = c("ResponseId", "vignette", "task", "selected", "Country", "Durationinseconds", names(am),
                      "Q1_Gender", "Q2_Age", "Q4_Education", "Q17_AttentionCheckCJE", "ALL_weights", ip, pp))
stopifnot(nrow(x) == 96920, x[, .N, ResponseId][, all(N == 10)])
x[, id := as.integer(factor(ResponseId, levels = unique(ResponseId)))]
x[, tk := (vignette + 1L) %/% 2L][, profile := 2L - vignette %% 2L]
stopifnot(x[, uniqueN(task), tk][, all(V1 == 1)], x[, sum(selected), .(id, tk)][, all(V1 == 1)])
for (v in names(am)) x[, paste0("attr_", am[[v]]) := trimws(as.character(get(v)))]
ac <- paste0("attr_", am)
x[, bad := any(is.na(.SD) | .SD == ""), .SDcols = ac, by = .(id, tk)]
stopifnot(x[bad == TRUE, .N] == 6)
x <- x[bad == FALSE]
d <- x[, .(id, task = as.integer(tk), profile = as.integer(profile), choice = as.integer(selected))]
d[, (ac) := x[, .SD, .SDcols = ac]]
d[, trial_post := x$task]
d[, cov_gender := c(Male = "male", Female = "female", Other = "other")[x$Q1_Gender]]
d[, cov_age_group := x$Q2_Age][, cov_education := x$Q4_Education][, cov_survey_weight := x$ALL_weights]
d[, cov_attention_pass := fifelse(x$Q17_AttentionCheckCJE == "Minister of Sport", 0L,
                           fifelse(x$Q17_AttentionCheckCJE == "Failed for softlaunch respondents", NA_integer_, 1L))]
d[, cov_duration_sec := x$Durationinseconds]
for (i in 1:4) d[, paste0("cov_issue_priority_", i) := x[[ip[i]]]]
for (i in 1:10) d[, paste0("cov_policy_pref_", i) := x[[pp[i]]]]
for (v in grep("^cov_(issue|policy)", names(d), value = TRUE)) d[get(v) == "", (v) := NA]
cc <- c(France = "fr", Germany = "de", Italy = "it", Poland = "pl", Spain = "es", UK = "uk")
for (k in names(cc)) {
  o <- d[x$Country == k]
  setorder(o, id, task, profile)
  cat(k, nrow(o), uniqueN(o$id), "\n")
  fwrite(o, file.path(out, paste0("panel_2023_technocrats_", cc[[k]], ".csv")))
}
