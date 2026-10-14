##Candidate-vignette experiment on ideology x party cue (US partisans, in-party and out-party candidates) from
##Lelkes, Y. (2021). Policy over party: Comparing the effects of candidate ideology and party on affective polarization.
##Political Science Research and Methods, 9(1). https://doi.org/10.1017/psrm.2019.18
##Replication data: Harvard Dataverse doi:10.7910/DVN/V7HWP4, CC0 1.0. Files read: data.tab (the tabular data; saved locally as
##data.tab), ms.tex (manuscript source) and appendix.tex (saved as app.tex: vignette wording), replication.R (rep.R; text, not run).
##Usage: Rscript lelkes_2021.R <dir holding data.tab> <output dir>
##
##Respondents: US partisans from a Qualtrics panel (pure independents excluded). Two experiments of the same design were run and
##concatenated by the author (in-party candidate, N = 1,526 rows; out-party candidate, N = 4,272 in the paper): one vignette per
##respondent, id = respondent in row order. Rows with no thermometer (ft NA, 499) are omitted (5,786 rated), and 83 in-party rows that have a
##thermometer but no recorded condition (condition, ideology_condition, party_condition all NA: assignment not saved) are dropped,
##leaving 5,703 respondents (1,296 in-party, 4,407 out-party; the paper's 1,526 + 4,272 = 5,798; difference not explained in the deposit).
##Vignette: a fictitious candidate "William Richardson", 53, businessman (fixed biography; appendix.tex). Two randomized attributes
##(six conditions; "condition" column = the authors' treatment code, confirmed with ideology_condition x party_condition):
##  attr_ideology: "(not shown)" (control and party-only: biography only) / moderate or extreme issue positions on healthcare,
##    abortion and immigration. The positions are the candidate's party side: a Republican candidate gets conservative
##    positions (moderate = Collins-like, extreme = Lee-like), a Democrat liberal ones (Manchin-like / Warren-like).
##    The candidate's party is the respondent's party (in-party experiment) or the other party (out-party experiment).
##    Level text is a SHORT PARAPHRASE of the appendix paragraph ("Extreme conservative issue positions (strongly opposes
##    government-run universal healthcare, strongly pro-life, legal immigration only)" etc.): the appendix paragraphs are
##    long; paraphrased from the article appendix.
##  attr_party: "(not shown)" / "Republican" / "Democrat" (the vignette opens "William Richardson is a [Republican/Democrat]").
##trial_candidate_relation = Inparty / Outparty (the two experiments; the candidate's party relative to the respondent's).
##Candidate party is derived from the respondent's party (party column) and the experiment; the ideology-only cells never name it.
##Outcome: rating_thermometer = feeling thermometer towards the candidate, 0-100 ("0 = cold ... 50 = not particularly warm or
##cold ... 100 = warm"), higher = warmer; raw. No opt-out. One task, one profile per respondent.
##Covariates: cov_party_id (respondent's party: Democrat / Republican, from the panel's party variable), cov_gender (sex),
##cov_age_group (text band), cov_race (text), cov_income (text band).
##Dropped: pidid, ideology (the authors' 0-1 composite), ideo3, extremity-type variables, Qualtrics ResponseID (re-keyed),
##the two Qualtrics metadata rows at the top of data.tab.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "data.tab"), na.strings = c("NaN", ""))
d <- d[-(1:2)][!is.na(ft)]
stopifnot(nrow(d) == 5786); d <- d[!is.na(condition)]
stopifnot(nrow(d) == 5703, !anyNA(d$party), !anyNA(d$ResponseID), uniqueN(d$ResponseID) == nrow(d))
d[, cand_party := fifelse(type == "Inparty", party, fifelse(party == "democrat", "republican", "democrat"))]
stopifnot(!anyNA(d$cand_party))
d[, attr_ideology := fifelse(ideology_condition %in% c("Control"), "(not shown)",
  paste0(ideology_condition, fifelse(cand_party == "republican", " conservative", " liberal"), " issue positions"))]
d[, attr_ideology := fcase(
  attr_ideology == "Extreme conservative issue positions", "Extreme conservative issue positions (strongly opposes government-run universal healthcare, strongly pro-life, legal immigration only)",
  attr_ideology == "Moderate conservative issue positions", "Moderate conservative issue positions (some federal healthcare funding but opposes the individual mandate, generally pro-choice, tougher immigration enforcement but a path to citizenship for some)",
  attr_ideology == "Extreme liberal issue positions", "Extreme liberal issue positions (universal single-payer healthcare, unrestricted abortion rights, pathway to citizenship and the DREAM Act)",
  attr_ideology == "Moderate liberal issue positions", "Moderate liberal issue positions (supports government-run healthcare but no insurance mandate, opposed to abortion, generally favours a pathway to citizenship but supports immigration enforcement)",
  default = attr_ideology)]
d[, attr_party := fifelse(party_condition == "Control", "(not shown)", fifelse(cand_party == "republican", "Republican", "Democrat"))]
stopifnot(!anyNA(d$ideology_condition), !anyNA(d$party_condition))
r <- d[, .(id = .I, task = 1L, profile = 1L, rating_thermometer = as.integer(ft),
  attr_ideology, attr_party, trial_candidate_relation = type,
  cov_party_id = fifelse(party == "democrat", "Democrat", "Republican"), cov_gender = tolower(sex),
  cov_age_group = gsub(" - ", "-", age), cov_race = race, cov_income = income)]
stopifnot(all(r$rating_thermometer %in% 0:100))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "lelkes_2021_candidate_ideology_party.csv"))
