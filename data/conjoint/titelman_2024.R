##Realistic Conservative-vs-Labour candidate choice (party label shown or hidden) from
##Titelman, N., & Lauderdale, B. E. (2024). The effects of party labels on vote choice with
##realistic candidate differentiation. Political Science Research and Methods.
##https://doi.org/10.1017/psrm.2024.20
##Replication data: Harvard Dataverse doi:10.7910/DVN/0WMHSD, CC0 1.0, no restricted files.
##Files read: Data_Exp08.tab (the analysis file, one row per respondent x task), Levels_Exp3.tab
##and Levels_Exp3a.tab (attribute question and level text). Read as text: the authors'
##Party_Labels_Effect_PSRM.Rmd and ..._Appendix.Rmd (design, code recodes), prompt1.png /
##prompt2.png (screenshots of one task without and with party labels). Not used:
##Data_Exp0_AB8.tab (the authors' subset of 873 respondents with derived A/B difference terms).
##Usage: Rscript titelman_2024.R <raw dir> <output dir>
##
##YouGov, British Election Study online panel, fielded 7-14 October 2021; 1,636 respondents
##(808 with party labels, 828 without, as in the article), 5 tasks each ("Candidate Choice 1..5",
##key exp1a..e = task 1..5), two candidates per task (profile 1 = Candidate A, left column;
##profile 2 = Candidate B). One candidate is always drawn from a model of 2017 Conservative
##candidates and the other from a model of Labour candidates (RAB + BES data, MICE-imputed);
##which party is A is randomized per task (candidate_Party_ProfileA). Whole profiles, not single
##attributes, were randomized, so levels are jointly distributed as among real candidates
##(article: AMCEs lose their design-based interpretation) -> restrictions = yes.
##Party-label arm (qsplit 1 = "Party Label", 2 = "No Party Label", authors' Rmd recode) is
##randomized per respondent and kept as trial_party_label; in the no-label arm the Party row
##was not displayed, so attr_party = "(not shown)".
##Outcome: choice, "If these were the only two candidates standing for Parliament in your
##constituency, which would you vote for?" Candidate A / Candidate B / I am not sure / I would
##not vote (screenshots). chosen_Candidate 1 = A, 2 = B, 3 = not sure, 4 = would not vote
##(verified: codes 1/2 match chosen_Candidate_Party against the A-side party in all 5,636
##decided tasks; 3/4 have no chosen party). candidate_Party_ProfileB is NOT used: it repeats
##ProfileA in every row (a deposit bug); B is always the other party. Opt-out: 2,544 of 8,180 tasks, choice 0 on both
##profiles; which opt-out was picked is kept as trial_no_choice (text), NA when a candidate
##was chosen.
##Attributes (question text in the screenshots; level text from Levels_Exp3*.tab and
##screenshots; code -> level from the authors' appendix recodes and the scale anchors shown):
##  attr_party       Conservative Party / Labour Party / (not shown)
##  attr_age         "<n> years old"
##  attr_sex         Sex_*: 0 Male, 1 Female (appendix Rmd recode)
##  attr_left_right  LR_* 0-10 self-placement ("smaller values more left, larger values more
##                   right"). Displayed as a band word plus the number, e.g. "Centre right (6)",
##                   "Left (2)", "Centre left (4)", "Centre (5)"; Levels_Exp3a lists the bands
##                   Left, Centre left, Centre, Centre right, Right, but no source gives the cut
##                   points for 0, 1, 3, 7-10. STORED AS THE NUMBER ONLY ("6"); the band word
##                   respondents also saw is not reconstructed.
##  attr_eu_vote     Brexit_*: 0 Voted to remain, 1 Voted to leave (appendix recode 0 Remain 1 Leave)
##  attr_councillor  ExperienceCouncil_*: 1 Has been elected a local councillor, 0 Has never ...
##  attr_born_constituency  BornConst_*: 1 Born in constituency, 0 Not born in constituency
##  attr_local_cuts  CutsSpending_* 1-5 ("not gone far enough (1) or too far (5)"), Levels_Exp3 order
##  attr_environment Environment_* 1-5, same anchors
##  attr_redistribution  Redistribution_* 1-5 ("1 (disagree) to 5 (agree)")
##  attr_immigration ImmigrationEcon_* 1-7 ("good (7) or bad (1)"); doubled spaces in the
##                   Levels file are collapsed (HTML display collapses them).
##Attribute order: randomized within three blocks (age/sex; constituency, council, left-right,
##EU vote; four policy issues), once per respondent (MS_order is constant within respondent).
##The permutation is recorded (MS_order) but no source maps its indices to attributes, so no
##attrpos_ columns.
##Covariates (BES panel answers given months/years before; codes kept unless stated):
##cov_age (age_respondent), cov_gender (gender_Respondent 1 Male 2 Female, appendix recode),
##cov_survey_weight (W8, used by the authors), cov_eu_ref_vote (0 Remain, 1 Leave, 2 other;
##authors set 2 to NA), cov_left_right (0-10), cov_immig_econ (1-7), cov_redist (0-10),
##cov_cuts_too_far (1-5), cov_enviro_protection (1-5), cov_local_turnout_retro,
##cov_past_vote_2017 / cov_past_vote_2019 (1 Con, 2 Lab, 3 LD, 4 SNP, 5 Plaid, 7 Green, 9 Other,
##12 Brexit Party, 13 independent; authors' recode; 6 unlabelled), cov_education_code and
##cov_party_id_code (no labels in the deposit), cov_pol_attention (0-10).
##Dropped: BES_id (panel identifier), ID_YouGov (re-keyed; it is already 1..N), synthetic
##candidate ids and row pointers, start/end times, the authors' derived difference/closeness terms.
##Count checks: 1,636 respondents, 808/828 by arm = article. 5 tasks each, no repeats.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "Data_Exp08.tab"))
lv3 <- fread(file.path(raw, "Levels_Exp3.tab"), header = TRUE, encoding = "UTF-8")
lev <- gsub("\\s+", " ", trimws(lv3$Level))
stopifnot(length(lev) == 22)
cuts <- lev[1:5]; env <- lev[6:10]; red <- lev[11:15]; imm <- lev[16:22]
stopifnot(grepl("not gone nearly far enough", cuts[1]), grepl("much too far", env[5]),
          grepl("^Strongly disagrees", red[1]), grepl("^Strongly agrees", red[5]),
          grepl("is bad", imm[1]), grepl("is good", imm[7]))
stopifnot(nrow(d) == 8180, uniqueN(d$ID_YouGov) == 1636, all(d$chosen_Candidate %in% 1:4))
d[, task := match(key, paste0("exp1", letters[1:5]))]
stopifnot(!anyNA(d$task), d[, .N, .(ID_YouGov, task)][, all(N == 1)])
# chosen code 1/2 = side A/B (checked against chosen party)
stopifnot(d[chosen_Candidate == 1, all(chosen_Candidate_Party == candidate_Party_ProfileA)],
          d[chosen_Candidate == 2, all(chosen_Candidate_Party != candidate_Party_ProfileA)],
          d[chosen_Candidate %in% 3:4, all(chosen_Candidate_Party == "NA")])
prof <- function(side) {
  aCon <- (d$candidate_Party_ProfileA == "Conservative") == (side == "A")
  g <- function(v) ifelse(aCon, d[[paste0(v, "_Con_Profile")]], d[[paste0(v, "_Lab_Profile")]])
  x <- data.table(id = d$ID_YouGov, task = d$task, profile = if (side == "A") 1L else 2L,
                  choice = as.integer(d$chosen_Candidate == (if (side == "A") 1L else 2L)))
  x[, attr_party := ifelse(d$qsplit == 1, ifelse(aCon, "Conservative Party", "Labour Party"), "(not shown)")]
  x[, attr_age := paste(g("Age"), "years old")]
  x[, attr_sex := c("Male", "Female")[g("Sex") + 1]]
  x[, attr_left_right := as.character(g("LR"))]
  x[, attr_eu_vote := c("Voted to remain", "Voted to leave")[g("Brexit") + 1]]
  x[, attr_councillor := c("Has never been elected a local councillor", "Has been elected a local councillor")[g("ExperienceCouncil") + 1]]
  x[, attr_born_constituency := c("Not born in constituency", "Born in constituency")[g("BornConst") + 1]]
  x[, attr_local_cuts := cuts[g("CutsSpending")]]
  x[, attr_environment := env[g("Environment")]]
  x[, attr_redistribution := red[g("Redistribution")]]
  x[, attr_immigration := imm[g("ImmigrationEcon")]]
  x[, trial_party_label := ifelse(d$qsplit == 1, "Party Label", "No Party Label")]
  x[, trial_no_choice := c(NA, NA, "I am not sure", "I would not vote")[d$chosen_Candidate]]
  x[, cov_age := d$age_respondent]
  x[, cov_gender := c("male", "female")[d$gender_Respondent]]
  x[, cov_eu_ref_vote := d$euRefVote_Respondent]
  x[, cov_left_right := d$leftRight_Respondent]
  x[, cov_immig_econ := d$immigEcon_Respondent]
  x[, cov_redist := d$redist_Respondent]
  x[, cov_cuts_too_far := d$cutsTooFar_Respondent]
  x[, cov_enviro_protection := d$enviroProtection_Respondent]
  x[, cov_local_turnout_retro := d$localTurnoutRetro_Respondent]
  x[, cov_past_vote_2017 := d$past_vote_2017_Respondent]
  x[, cov_past_vote_2019 := d$past_vote_2019_Respondent]
  x[, cov_education_code := d$education_Respondent]
  x[, cov_party_id_code := d$partyId]
  x[, cov_pol_attention := d$polAttention_Respondent]
  x[, cov_survey_weight := d$W8]
  x
}
o <- rbind(prof("A"), prof("B"))
stopifnot(o[, sum(choice), .(id, task)][, all(V1 <= 1)], o[, uniqueN(attr_party), .(id, task)][, all(V1 %in% 1:2)])
stopifnot(!anyNA(o[, .SD, .SDcols = patterns("^attr_")]))
stopifnot(o[attr_party != "(not shown)", .(uniqueN(attr_party)), .(id, task)][, all(V1 == 2)])
o[, id := match(id, sort(unique(id)))]
setorder(o, id, task, profile)
fwrite(o, file.path(out, "titelman_2024_party_labels.csv"))
cat("rows", nrow(o), "resp", uniqueN(o$id), "optout tasks", o[, sum(choice), .(id, task)][V1 == 0, .N], "\n")
