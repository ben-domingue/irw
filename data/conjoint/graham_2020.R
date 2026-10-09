##Candidate choice experiment on undemocratic behaviour from
##Graham, M. H., & Svolik, M. W. (2020). Democracy in America? Partisanship, polarization, and the
##robustness of support for democracy in the United States. American Political Science Review,
##114(2), 392-409. https://doi.org/10.1017/S0003055420000052
##Replication data: Harvard Dataverse doi:10.7910/DVN/EEARKA, CC BY 4.0. Files read:
##data_experiment.csv (one row per respondent x scenario x candidate perspective), key_policy.csv
##and key_lucid.csv (label keys). Design and attribute text: randomization_1.pdf and
##randomization_2.pdf (Appendix B tables), appendix_survey_candChoice.pdf (screenshot),
##codebook.pdf. The Montana precinct analysis in the deposit is not an experiment.
##Usage: Rscript graham_2020.R <dir holding the files> <output dir>
##
##Lucid sample, wave 2 of a two-wave survey (wave 1 rated policies and democracy items); 1,682
##respondents in the deposit (1,680 and 19,413 scenarios after the drops below), 13 two-candidate scenarios each (Appendix B: scenarios 1-13 have a
##party label; scenarios 14-16, without party labels or with two undemocratic candidates, are not
##in the deposit). Each scenario appears twice in the source, once from each candidate's
##perspective (candNum 1/2, c_ = that candidate, o_ = opponent); each row here is one candidate.
##profile = screen position (c_onLeft = 1, shown as "Candidate 1", = profile 1; position by coin
##flip). task = matchNum, the scenario number, which the codebook says is NOT the display order
##(task inferred; the display order was not saved).
##Outcomes (screenshot):
##  choice        = c_win, "Which candidate do you prefer?" (Candidate 1 / Candidate 2; no opt-out).
##                  262 scenarios with no answer are dropped.
##  rating_turnout = c_vote, "Would you vote in this election?" (1 = Yes, 0 = No), asked once per
##                  scenario and repeated on both profiles (as in the source); NA when unanswered.
##Attributes (text as displayed; Appendix B): age ("<n> years old"), gender, race, profession and
##years of experience (displayed together as "<profession> for <n> years"; stored as two columns),
##party, an economic position (education finance E1-E4 or tax T1-T4), a social position
##(immigration I1-I4 or marijuana M1-M4) and a democracy-related line (generic, undemocratic or
##negative-valence act). Both candidates in a scenario take positions in the same two areas.
##  Democracy text is built from the Appendix B templates with [own party] = the candidate's party
##  and [opposite party] = the other, matching the filled-in sentences in key_dem.csv (e.g. "Said
##  the Republican governor should ban far-left group rallies in the state capital.").
##  Tax text: respondents in states lacking an income, sales or corporate tax saw state-specific
##  wordings of the tax positions (appendix: "slight modifications that fit the policies to the
##  status quo"; key_policy.csv lists them), but no deposited source says which wording went to
##  which state. Scenarios in the tax area for respondents whose `tax` is not "normal" are
##  therefore DROPPED (both profiles; 2,217 scenarios of 340 respondents, 2,191 of them answered),
##  since their displayed
##  tax text cannot be recovered without guessing. Their other scenarios (education finance area)
##  are kept; trial_tax_status keeps the source value (normal / noincome / noincome,nosales /
##  noincome,nocorp).
##Restrictions (Appendix B): a fixed set of 16 party pairings and policy-area combinations per
##respondent; 4 scenarios with two generic candidates, 9 with one generic and one undemocratic or
##negative-valence candidate (each undemocratic act once per respondent); policy positions p = .25
##within area; race and profession drawn with unequal probabilities; 20 men and 12 women per
##respondent; experience = age minus 20-30. "Police officer" occurs in the data but not in the
##Appendix B profession list (kept).
##Spot check: in scenarios with one undemocratic candidate, that candidate is chosen in 38% (weighted),
##the roughly 12-point penalty the paper reports.
##Survey weight: weight (deposit weights.csv/weights.R, raking to ACS) -> cov_survey_weight.
##Covariates (source text unless noted): cov_age, cov_gender (Male/Female -> male/female),
##cov_educ6 (the authors' 6-category education recode as stored), cov_state, cov_race,
##cov_hispanic, cov_hhi, cov_ideo, cov_trump, cov_party_id7 (Party7 text, line breaks -> space),
##wave-1 policy ratings cov_rate_E1 ... cov_rate_T4 (0-100 as stored), cov_knowl_* (0/1),
##cov_auth_* (answer text), cov_voteduty (-3..3 as stored). Dropped: the authors' derived
##variables (distances, ranks, squares, dummies, diff_*, folded/lean party, rescaled 0-1 democracy
##items, scale totals), the duplicate id.1 and st columns. id is the deposit's integer id.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cols <- c("id", "weight", "matchNum", "candNum", "c_win", "c_vote", "c_Party", "c_p1_code", "c_p2_code", "c_dem_code",
          "c_dem_codeLR", "c_sex", "c_race", "c_pro", "c_age", "c_exper", "c_onLeft", "tax", "age", "gender", "educ",
          "state", "race", "hispanic", "hhi", "ideo", "trump", "Party7",
          "E1", "E2", "E3", "E4", "I1", "I2", "I3", "I4", "M1", "M2", "M3", "M4", "T1", "T2", "T3", "T4",
          "knowl_ryan", "knowl_roberts", "knowl_merkel", "knowl_putin", "knowl_spend", "knowl_house",
          "knowl_senate_party", "knowl_senate_term", "auth_respect", "auth_manners", "auth_obey", "auth_behave", "voteduty")
s <- fread(file.path(raw, "data_experiment.csv"), select = cols)
kp <- fread(file.path(raw, "key_policy.csv"))
std <- kp[!duplicated(code)]                      # first occurrence = standard wording (as in randomization_1.pdf)
stopifnot(nrow(std) == 16, std[code == "T4", full] == "Eliminate the state income tax.")
pol <- setNames(std$full, std$code)
stopifnot(all(s$tax %in% c("normal", "noincome", "noincome,nosales", "noincome,nocorp")))
# state-specific tax wordings have no deposited mapping to states: drop those scenarios (both profiles)
s <- s[!(tax != "normal" & substr(c_p1_code, 1, 1) == "T")]
stopifnot(all(substr(s$c_p1_code, 1, 1) %in% c("E", "T")))
ptext <- function(code) unname(pol[code])
own <- s$c_Party; opp <- ifelse(own == "Democrat", "Republican", "Democrat")
dem <- character(nrow(s))
tmpl <- function(code, i) switch(code,
  g_schedule = "Served on a committee that establishes the state legislature's schedule for each session.",
  g_committee = "Worked on a plan to change the state legislature's committee structure.",
  g_boardElect = "Served on the state's Board of Elections, which handles local, state, and federal elections.",
  g_record = "Submitted a proposal that would change the state's record-keeping laws and practices.",
  g_officestructure = "Served on a subcommittee that reviews the structure of state legislative staff offices.",
  g_procedure = "Served on a committee that approves proposed changes to legislative procedure.",
  g_progEval = "Participated in a working group on using program evaluation to inform policymaking.",
  v_tax = "Was convicted of underpaying federal income taxes.",
  v_affair = "Was reported to have had multiple extramarital affairs.",
  u_journalists = sprintf("Said the %s governor should prosecute journalists who accuse him of misconduct without revealing sources.", own[i]),
  u_banLeftProtest = sprintf("Said the %s governor should ban far-left group rallies in the state capital.", own[i]),
  u_banRightProtest = sprintf("Said the %s governor should ban far-right group rallies in the state capital.", own[i]),
  u_execRule = sprintf("Said the %s governor should rule by executive order if %s legislators don't cooperate.", own[i], opp[i]),
  u_court = sprintf("Said the %s governor should ignore unfavorable court rulings by %s-appointed judges.", own[i], opp[i]),
  u_limitVote = sprintf("Supported a proposal to reduce the number of polling stations in areas that support %ss.", opp[i]),
  u_gerry2 = sprintf("Supported a redistricting plan that gives %ss 2 extra seats despite a decline in the polls.", own[i]),
  u_gerry10 = sprintf("Supported a redistricting plan that gives %ss 10 extra seats despite a decline in the polls.", own[i]),
  NA_character_)
for (i in seq_len(nrow(s))) dem[i] <- tmpl(s$c_dem_codeLR[i], i)
stopifnot(!anyNA(dem), all(dem %in% fread(file.path(raw, "key_dem.csv"))$full))
d <- data.table(id = s$id, task = s$matchNum, profile = ifelse(s$c_onLeft == 1, 1L, 2L),
                choice = s$c_win, rating_turnout = s$c_vote,
                attr_age = paste(s$c_age, "years old"), attr_gender = s$c_sex, attr_race = s$c_race,
                attr_profession = s$c_pro, attr_years_experience = as.character(s$c_exper), attr_party = s$c_Party,
                attr_economic_policy = ptext(s$c_p1_code), attr_social_policy = ptext(s$c_p2_code),
                attr_democracy = dem, trial_tax_status = s$tax)
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, .N, .(id, task)][, all(N == 2)],
          d[, uniqueN(profile), .(id, task)][, all(V1 == 2)])
txt <- function(x) { x <- as.character(x); x[x == ""] <- NA; x }
d[, `:=`(cov_survey_weight = s$weight, cov_age = as.integer(s$age), cov_gender = c(Male = "male", Female = "female")[s$gender],
         cov_educ6 = txt(s$educ), cov_state = txt(s$state), cov_race = txt(s$race), cov_hispanic = txt(s$hispanic),
         cov_hhi = trimws(txt(s$hhi)), cov_ideo = txt(s$ideo), cov_trump = txt(s$trump), cov_party_id7 = gsub("\n", " ", txt(s$Party7)))]
for (v in c("E1", "E2", "E3", "E4", "I1", "I2", "I3", "I4", "M1", "M2", "M3", "M4", "T1", "T2", "T3", "T4")) d[, paste0("cov_rate_", v) := s[[v]]]
for (v in c("knowl_ryan", "knowl_roberts", "knowl_merkel", "knowl_putin", "knowl_spend", "knowl_house", "knowl_senate_party",
            "knowl_senate_term", "auth_respect", "auth_manners", "auth_obey", "auth_behave", "voteduty")) d[, paste0("cov_", v) := s[[v]]]
stopifnot(all(s$gender %in% c("Male", "Female")))
d <- d[!is.na(choice)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "graham_2020_undemocratic_candidates.csv"))
