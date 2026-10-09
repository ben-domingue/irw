##Campaign-finance disclosure conjoints (candidate and ballot-initiative) from
##Robinson, T. S. (2022). When do voters respond to campaign finance disclosure? Evidence from
##multiple election types. Political Behavior. https://doi.org/10.1007/s11109-021-09766-y
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZQDC1D, CC0 1.0. Files read (Dataverse
##"original format" downloads): cand_control_final.csv, cand_treat_final.csv, initiative_final.csv.
##Attribute levels are stored as text in the data; the screenshots in the article's supplementary
##material (Appendix D, Figures D1-D2) show the displayed layout and question wording.
##Usage: Rscript robinson_2022.R <dir holding the three csv files> <output dir>
##
##CESS Online US subject pool (Nuffield College), 18 Feb - 8 Mar 2019, residents of states with
##ballot initiatives (Appendix A); 390 eligible subjects (article). Every subject did both
##experiments (order randomized, article). Two tables, because the two experiments have different
##profiles and outcomes:
##
##1. robinson_2022_cf_candidates: pairs of candidates for state governor (Candidate A = profile 1,
##   B = 2), 5 campaign-finance attributes (total donations, average donation, origin of donations,
##   largest donor, proportion of funds from largest donor). Subjects were randomly assigned
##   (article) to see 3 more attributes (party, ideology, previously held elected office:
##   cand_treat_final) or not (cand_control_final); one table with trial_arm, the 3 extra
##   attributes are "(not shown)" in the control arm. Up to 6 rounds per subject (round = task).
##   choice = vote: "If you had to choose, which candidate would you vote for?" (Candidate A /
##   Candidate B; no opt-out). The 1-7 approval rating of each candidate shown in Fig. D1 is not in
##   the deposit.
##2. robinson_2022_cf_initiatives: one round per initiative issue (4 issues, order randomized;
##   trial_issue keeps the source codes: marij = marijuana legalisation, wage = minimum wage
##   increase, enviro = carbon emissions tax, bond = sewage bond issuance, per the article; only
##   the marijuana title and description are shown in Fig. D2). The display order of the issues
##   was not saved: task numbers follow the fixed order marij, wage, enviro, bond (task inferred,
##   not the order shown). Each round shows the Support
##   campaign (profile 1, left column) and the Opposition campaign (profile 2) with the same 5
##   finance attributes. choice = vote: "If you had to choose, would you vote for or against this
##   initiative?" (For = the Support profile chosen, Against = Opposition chosen; no opt-out).
##   rating = rate: "On a scale from 1 to 7, where 1 indicates that you strongly disapprove of the
##   campaign and 7 indicates that you strongly approve of the campaign, how would you rate the two
##   sides of the campaign?" (1 strongly disapprove ... 7 strongly approve).
##
##Restrictions: the article says levels were "randomized with minimal restrictions to prevent
##implausible attribute-level combinations", e.g. a $1 million average donation never goes with
##$100,000 to $200,000 total donations (no such row in any file). INCOMPLETE ROUNDS: 218 control,
##219 treatment and 103 initiative rounds hold only one of the two profiles (the analysis files
##keep them: 2,068 / 2,089 / 3,003 rows = the article's N), and in 81 + 107 + 46 of them the
##remaining profile was not the one chosen, so the missing profile was seen (and often chosen).
##Our reading (inferred, not stated by the author) is that profiles violating the rule were
##dropped after fielding. Only rounds with both profiles and exactly one choice are kept here.
##Attribute order: not stated (the two screenshots list attributes in different orders); none saved.
##Covariates (answer text as stored): cov_gender (Female/Male; "Transgender", "Other: Transgender",
##"Other:" = other; "Prefer not to say", "Other: Prefer not to say" and blank = NA), cov_age (whole
##numbers 18-100 kept), cov_ethnicity, cov_state, cov_education, cov_employment, cov_vote2016,
##cov_vote2016_choice, cov_party_id (party_id text; "Prefer not to say" = NA), cov_ideology (0-10
##as stored; end labels not in the deposit), cov_ballot_vote, cov_ballot_good, cov_contribute,
##cov_quiz_score (SC0: score on the 3 factual questions about the briefing text, 100 per correct
##answer, Appendix A). Dropped: pk (undocumented derived score), group (= trial_arm).
##participantid (subj_<n>, already anonymous) re-keyed to n, the same across both tables.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) fread(file.path(raw, f), na.strings = c("NA"))
covs <- function(s) {
  g <- s$gender
  gender <- fifelse(g == "Female", "female", fifelse(g == "Male", "male",
            fifelse(g %in% c("Transgender", "Other: Transgender", "Other:"), "other", NA_character_)))
  stopifnot(all(g %in% c("Female", "Male", "Transgender", "Other: Transgender", "Other:", "Prefer not to say",
                         "Other: Prefer not to say", "", NA)))
  ag <- suppressWarnings(as.integer(s$age)); ag[!(ag >= 18 & ag <= 100)] <- NA
  pid <- s$party_id; pid[pid %in% c("Prefer not to say", "")] <- NA
  txt <- function(x) { x <- as.character(x); x[x == ""] <- NA; x }
  data.table(cov_gender = gender, cov_age = ag, cov_ethnicity = txt(s$ethnic), cov_state = txt(s$state),
             cov_education = txt(s$educ), cov_employment = txt(s$employ), cov_vote2016 = txt(s$vote2016),
             cov_vote2016_choice = txt(s$vote2016_choice), cov_party_id = pid, cov_ideology = as.integer(s$ideology),
             cov_ballot_vote = txt(s$ballot_vote), cov_ballot_good = txt(s$ballot_good),
             cov_contribute = txt(s$contribute), cov_quiz_score = as.integer(s$SC0))
}
fin <- function(s) data.table(attr_total_donations = s$total, attr_average_donation = s$average,
                              attr_origin_of_donations = s$origin, attr_largest_donor = s$largest,
                              attr_largest_donor_share = s$prop)

## 1. candidates
cc <- rd("cand_control_final.csv"); ct <- rd("cand_treat_final.csv")
cc[, `:=`(party = "(not shown)", cand_ideology = "(not shown)", office = "(not shown)")]
s <- rbind(ct, cc, use.names = TRUE)
stopifnot(all(s$group %in% c("control", "treat")), all(s$cand %in% c("A", "B")))
d <- data.table(id = as.integer(sub("subj_", "", s$participantid)), task = as.integer(s$round),
                profile = match(s$cand, c("A", "B")), choice = as.integer(s$vote), fin(s),
                attr_party = s$party, attr_ideology = s$cand_ideology, attr_previous_office = s$office,
                trial_arm = fifelse(s$group == "treat", "party, ideology and office shown", "finance only"),
                covs(s))
k <- d[, .(n = .N, np = uniqueN(profile), ch = sum(choice)), .(id, task)][n == 2 & np == 2 & ch == 1, .(id, task)]
cat("candidate rounds kept", nrow(k), "of", uniqueN(d[, .(id, task)]), "\n")
d <- d[k, on = .(id, task)]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^choice$")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "robinson_2022_cf_candidates.csv"))

## 2. initiatives
s <- rd("initiative_final.csv")
stopifnot(all(s$camp %in% c("Support", "Oppose")), all(s$issue %in% c("marij", "wage", "enviro", "bond")))
d <- data.table(id = as.integer(sub("subj_", "", s$participantid)), trial_issue = s$issue,
                profile = match(s$camp, c("Support", "Oppose")), choice = as.integer(s$vote),
                rating = as.integer(s$rate), fin(s), covs(s))
k <- d[, .(n = .N, np = uniqueN(profile), ch = sum(choice)), .(id, trial_issue)][n == 2 & np == 2 & ch == 1, .(id, trial_issue)]
cat("initiative rounds kept", nrow(k), "of", uniqueN(d[, .(id, trial_issue)]), "\n")
d <- d[k, on = .(id, trial_issue)]
# the display order of the 4 issues was randomized and not saved: task follows a fixed issue order (inferred)
d[, task := match(trial_issue, c("marij", "wage", "enviro", "bond"))]
setcolorder(d, c("id", "task", "profile"))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^choice$|^rating$")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "robinson_2022_cf_initiatives.csv"))
