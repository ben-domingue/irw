##Low-salience policy proposals (US): instrument x public support x effectiveness x promoter x timing, from
##Treger, C. (2022). Before the party hijacks: The limited role of party cues in appraisal of low-salience policies: Experimental
##evidence. Public Opinion Quarterly, 86(4), 955-967. https://doi.org/10.1093/poq/nfac044 (README of the deposit)
##Replication data: Harvard Dataverse doi:10.7910/DVN/TQN6ZN, CC0 1.0. Files read: Treger_Before_the_party_hijacks_replication_data.dta
##(datafile 14281561, Stata original: the .tab on Dataverse is its ingest; 21,920 rows = 1,370 respondents x 16 profiles, 98 variables),
##README.txt and Treger_Before_the_party_hijacks_questionnaire.txt (as text). Respondent ids are already stripped of platform ids
##by the depositor (rid1 renumbered 1-1,370).
##Usage: Rscript treger_2022.R <dir with the .dta> <output dir> [file name; default Treger_Before_the_party_hijacks_replication_data.dta]
##
##Design (README, questionnaire): online paired conjoint, Lucid, 17 Sep - 28 Oct 2019, 1,370 US adults (nonprobability, designed to be
##nationally representative). Each respondent saw 8 pairs of low-salience policy proposals (16 profiles), the two proposals of a pair on
##the same issue, four domains with two issues each (safety: riding an electric bicycle / swimming; health: nutrition / smoking; welfare:
##retirement savings / working hours; morals: euthanasia / pornography); a respondent saw one issue per domain, in two consecutive pair-slots (pairs 1-2 safety, 3-4 health, ...; trial_policy_goal).
##Randomized attributes:
##  policy instrument  : Info, Default/Decision, Tax/Restriction, Ban/Mandate (labels of `coer`; the displayed proposal wording is
##                       in `policy_`, kept as trial_policy_text),
##  reported public support: 20%-30%, 35%-45%, 55%-65%, 75%-85%, unknown (pub_support_),
##  reported effectiveness: Somewhat effective, Effective, Very effective, Unknown (effectiveness_),
##  promoter: Democrat politician, Republican politician, Federal government, Member of Congress, Non-governmental organization (NGO),
##            Private company (promoter_),
##  implementation: A year from now, 3 years from now (implementation_; the text variables are used, not the numeric imp, whose
##            code/sign differs between the codebook and the printed tables according to the README).
##Task = the pair, the tens digit of `proposal` (1-8; 11,12 = pair 1 ...); profile = the units digit (1, 2). The data say pairs 1-2 are the
##safety domain, 3-4 health, 5-6 welfare, 7-8 morals (so each domain gives two pairs), but the order in which pairs were shown is not
##documented (the questionnaire block order is nutrition, smoking, riding, swimming, retirement, working hours, euthanasia, pornography,
##which differs): task is the deposit's pair index, not a verified display order.
##Outcomes: choice (`choice_`: the preferred proposal of the two; exactly one per pair in all 10,960 pairs; no opt-out) and rating
##(`support_`, 1-7, support for the proposal, rated separately for each proposal; the questionnaire gives only "rate each of the proposals
##separately" and the README "Support for the proposal, 1 to 7", with `supported` = 5-7 as the article's outcome: question wording and
##anchors are not in the deposit, paraphrase; higher = more support, stored as is). `supported` is derived and dropped.
##Randomization restrictions: none documented. Level probabilities: not documented (level shares near equal).
##Covariates (labels from the .dta value labels): cov_gender, cov_age_group (18-24..65+), cov_education (labelled categories of `edu`),
##cov_party_id (party: Democrat, Republican, Independent, other), cov_ideology (ideo, 1 Liberal .. 7 Conservative; only the end points are
##labelled in the questionnaire), cov_region, cov_race, cov_household_income (hhi labels), cov_attention_pass (Q60 asked to tick both
##"not interested at all" and "slightly interested", i.e. codes 4 and 5: pass = "4,5").
##The article analyses only Democrats (N = 469) and Republicans (N = 455); this table keeps all 1,370 respondents including
##Independents/others (cov_party_id lets users subset).
##Dropped: all survey metadata (status, progress, ... ), issue-importance items q63-q70, religion/religiosity/class (codes unlabelled in
##the data), the per-item q12-q59 raw columns, derived dummies. PII: the depositor already removed rid/responseid/dates/duration; none
##left. The README and questionnaire name the author's and depositor's contact emails: not copied.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- if (length(a) >= 3) a[3] else "Treger_Before_the_party_hijacks_replication_data.dta"
d <- as.data.table(read_dta(file.path(raw, f)))
stopifnot(nrow(d) == 21920, uniqueN(d$rid1) == 1370, all(d[, .N, rid1]$N == 16))
lab <- function(v) as.character(as_factor(d[[v]]))
t <- data.table(id = as.integer(d$rid1), task = as.integer(d$proposal %/% 10), profile = as.integer(d$proposal %% 10),
  choice = as.integer(d$choice_), rating = as.integer(d$support_),
  attr_policy_instrument = lab("coer"), attr_public_support = d$pub_support_, attr_effectiveness = d$effectiveness_,
  attr_promoter = d$promoter_, attr_implementation = d$implementation_,
  trial_policy_goal = lab("po_goal"), trial_policy_domain = lab("po_domain"), trial_policy_text = d$policy_,
  cov_gender = lab("gender"), cov_age_group = lab("age"), cov_education = lab("edu"), cov_party_id = lab("party"),
  cov_ideology = as.integer(d$ideo), cov_region = lab("region"), cov_race = lab("race"), cov_household_income = lab("hhi"),
  cov_attention_pass = as.integer(as.character(d$attention) == "4,5"))
stopifnot(all(t[, .(s = sum(choice)), .(id, task)]$s == 1), all(t$profile %in% 1:2), !anyNA(t[, .(choice, rating, attr_policy_instrument)]))
ac <- grep("^attr_", names(t), value = TRUE); stopifnot(!anyNA(t[, ..ac]))
setorder(t, id, task, profile)
fwrite(t, file.path(out, "treger_2022_policy_party_cues.csv"))
