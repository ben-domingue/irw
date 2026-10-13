##Committee-composition decision-making experiment from
##Reidinger, V., Leemann, L., & Slapin, J. B. (2026). How descriptive over- and
##under-representation impacts citizens' evaluations of decision-making across policy domains.
##Political Science Research and Methods. https://doi.org/10.1017/psrm.2026.10103
##Replication data: Harvard Dataverse doi:10.7910/DVN/BCYWJK, CC0 1.0, no restricted files, no terms.
##File read: RawData.tab (Qualtrics export of "RawData.csv", answers as text, two header rows:
##question text and ImportId). 01_cleaning.R, 02_prep_data.R, 04_analysis.R and the README were read
##as text only, for variable meanings and the authors' exclusions.
##Usage: Rscript reidinger_2026.R <raw dir> <output dir>
##
##10,101 UK adults (online general-population panel, Qualtrics project "UKGenPop"); all 10,101 rows
##agreed to the consent form and finished. Each respondent read about ONE government committee of 20
##members whose composition was randomized, then about THREE decisions the committee had taken, one on
##each of three policies, shown in a randomized order (policy_nr_child / policy_nr_abor /
##policy_nr_leave = 1,2,3; each of the six orders occurs about 1,600-1,780 times). Per policy the
##committee's decision (approved / not approved) was randomized independently. So the table is one
##respondent x 3 tasks x 1 profile: a task is one policy decision (task = position in which it was
##shown, recorded), and the profile is "this committee took this decision on this policy".
##Attributes (level text = the reminder strings recorded for each respondent):
##  attr_women      women_reminder: "3 women and 17 men" / "10 women and 10 men" / "17 women and 3 men"
##  attr_age        age_reminder: "mostly people older than 60" / "... between the ages of 46 and 60" /
##                  "... between the ages of 30 and 45"
##  attr_parents    parents_reminder: "mostly parents" / "equally parents and non-parents" /
##                  "mostly non-parents"
##  attr_university uni_reminder: "mostly people with a university degree" / "equally people with and
##                  without a university degree"
##  attr_policy     policy of the decision, from the banner text: UNIVERSAL CHILDCARE / MANDATORY
##                  COUNSELING BEFORE ABORTIONS / MENSTRUAL LEAVE FOR WOMEN
##  attr_decision   decision banner "APPROVED" / "NOT APPROVED" (decision_symbol_care / _abortion /
##                  _leave, the text before the check/cross mark). The authors call approval of
##                  childcare and leave, and rejection of mandatory abortion counselling, the
##                  "progressive" outcome; that coding is not used here.
##The four committee attributes are the same for the three tasks of a respondent. The committee was
##always "equally government and opposition members" (constant, not an attribute); the committee
##name appeared as "health and family" or "family and health" (trial_committee_name, randomized
##word order). Whether the order of the composition attributes on screen was randomized is not
##documented in the deposit (the composition_reminder strings list them in varying orders, but that
##is the reminder, not the vignette), so attr_order is unknown and there is no attrpos_ column.
##Outcomes (1-10 sliders/radio, text "1: ..." ... "10: ...", "Prefer not to say" -> NA; kept 1-10,
##higher = more favourable / more agreement):
##  rating_fair   PROCED1_*  "Do you think that the process by which this decision was made was
##                fair?"  1 = Very unfair, 10 = Very fair
##  rating_agree  OUTCO1_*   "To what extent do you agree with the decision that the committee made?"
##                1 = Completely disagree, 10 = Completely agree
##  rating_support_after  OUTCO2_*  "Having seen the decision of the committee, please think again
##                about whether you agree with the following statement: <policy statement>"
##                1 = Completely disagree, 10 = Completely agree (the statement is the pro-policy
##                statement, so higher = more support for the policy itself, whichever way the
##                committee decided)
##Task-level: trial_support_before = SUB_* (the same policy statement, asked before the committee was
##shown; 1-10); trial_committee_name.
##No opt-out (ratings only). Dropped: dates, the manipulation-check answers, open-ended reasons (free text), moral/handout
##items and the authors' derived in/out-group and difference variables. Respondent id = row number.
##Covariates: cov_gender (GENDER: Female / Male; Non-binary -> other; Prefer not to say -> NA),
##cov_birth_year (AGE is the year of birth, "In which year were you born?"), cov_age_group
##(AGE_QUOTAGROUP), cov_education_years (EDUCATION, years of formal education, numeric as recorded),
##cov_university_degree (DEGREE Yes/No), cov_vote_intention (PARTY, party they would vote for; vote
##intention, not party identification), cov_left_right (LEFTRIGHT 0-10 text codes 1-10 as recorded;
##"Do not know"/refusal -> NA), cov_region, cov_urban_rural, cov_parent (CHILD1),
##cov_attention_pass_1 (ATTENTION_HARD == 4, the instructed answer), cov_attention_pass_2
##(ATTENTION_EASY == 8), cov_duration_sec. Free-typed fields and PII: none kept. 4,457 pass check 1
##(the authors flag the rest, "attcheck1_fail"); all respondents are kept here.
##Count check: 10,101 respondents x 3 = 30,303 task rows; 29,986 rows (10,066 respondents) remain
##after dropping tasks with all three ratings missing.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "RawData.tab"), colClasses = "character", na.strings = "", header = TRUE)
r <- r[-(1:2)]   # question-text and ImportId rows
stopifnot(!anyDuplicated(r$ResponseId), all(r$CONSENT == "I agree"))
r[, id := .I]
num <- function(x) { x[x == "Prefer not to say"] <- NA; as.integer(sub("^(\\d+).*", "\\1", x)) }
chk <- function(x, lv) { stopifnot(all(is.na(x) | x %in% lv)); x }
gen <- c(Female = "female", Male = "male", `Non-binary` = "other")
cv <- data.table(id = r$id,
  cov_gender = unname(gen[chk(r$GENDER, c(names(gen), "Prefer not to say"))]),
  cov_birth_year = as.integer(r$AGE),
  cov_age_group = r$AGE_QUOTAGROUP,
  cov_education_years = as.numeric(r$EDUCATION),
  cov_university_degree = chk(ifelse(r$DEGREE == "Prefer not to say", NA, r$DEGREE), c("Yes", "No")),
  cov_vote_intention = ifelse(r$PARTY == "Don't Know / Prefer not to say", NA, r$PARTY),
  cov_left_right = num(ifelse(r$LEFTRIGHT == "Do not know", NA, r$LEFTRIGHT)),
  cov_region = r$REGION,
  cov_urban_rural = ifelse(r$URBANRURAL == "Prefer not to say", NA, r$URBANRURAL),
  cov_parent = chk(ifelse(r$CHILD1 == "Prefer not to say", NA, r$CHILD1), c("Yes", "No")),
  cov_attention_pass_1 = as.integer(r$ATTENTION_HARD == "4"),
  cov_attention_pass_2 = as.integer(r$ATTENTION_EASY == "8"),
  cov_duration_sec = as.integer(r[["Duration (in seconds)"]]))
cv[cov_birth_year < 1900 | cov_birth_year > 2010, cov_birth_year := NA]
cv[cov_education_years < 0 | cov_education_years > 40, cov_education_years := NA]
women <- chk(r$women_reminder, c("3 women and 17 men", "10 women and 10 men", "17 women and 3 men"))
age <- chk(r$age_reminder, c("mostly people older than 60", "mostly people between the ages of 46 and 60", "mostly people between the ages of 30 and 45"))
par <- chk(r$parents_reminder, c("mostly parents", "equally parents and non-parents", "mostly non-parents"))
uni <- chk(r$uni_reminder, c("mostly people with a university degree", "equally people with and without a university degree"))
stopifnot(!anyNA(women), !anyNA(age), !anyNA(par), !anyNA(uni),
          all(r$women_committee == c("3" = "3", "10" = "10", "17" = "17")[sub(" .*", "", women)]))
pol <- list(child = c("UNIVERSAL CHILDCARE", "care", "CHILD"), abor = c("MANDATORY COUNSELING BEFORE ABORTIONS", "abortion", "ABOR"),
            leave = c("MENSTRUAL LEAVE FOR WOMEN", "leave", "LEAVE"))
d <- rbindlist(lapply(names(pol), function(k) {
  p <- pol[[k]]
  sym <- r[[paste0("decision_symbol_", p[2])]]
  m <- regmatches(sym, regexec("^(.*): (APPROVED|NOT APPROVED) ", sym)); stopifnot(all(lengths(m) == 3)); m <- do.call(rbind, m)
  stopifnot(all(m[, 2] == p[1]))
  data.table(id = r$id, task = as.integer(r[[paste0("policy_nr_", tolower(p[3]))]]), profile = 1L,
             rating_fair = num(r[[paste0("PROCED1_", p[3])]]), rating_agree = num(r[[paste0("OUTCO1_", p[3])]]),
             rating_support_after = num(r[[paste0("OUTCO2_", p[3])]]),
             attr_women = women, attr_age = age, attr_parents = par, attr_university = uni,
             attr_policy = m[, 2], attr_decision = m[, 3],
             trial_support_before = num(r[[paste0("SUB_", p[3])]]), trial_committee_name = r$topic_committee)
}))
d[, trial_committee_name := chk(trial_committee_name, c("health and family", "family and health"))]
stopifnot(d[, .N, .(id, task)][, all(N == 1)], d[, all(task %in% 1:3)], d[, uniqueN(task), id][, all(V1 == 3)],
          all(unlist(d[, .(rating_fair, rating_agree, rating_support_after)]) %in% c(1:10, NA)))
d <- d[!(is.na(rating_fair) & is.na(rating_agree) & is.na(rating_support_after))]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "reidinger_2026_committee_decisions.csv"))
