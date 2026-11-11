##Mock local prosecutor (district attorney) election conjoint, from
##Sances, M. W. (2026). Unequal competence? Why criminal justice reformers are disadvantaged in local
##elections. Public Opinion Quarterly, 90(3), 697-729. https://doi.org/10.1093/poq/nfag017
##(paywalled; not read: OUP 403 here).
##Replication data: Harvard Dataverse doi:10.7910/DVN/4S1OG9, CC0 1.0. Files read: dataset_voters.tab
##(Dataverse "original format" .dta), codebook_voters.txt, README.pdf, and figure4.do / figure5.do
##(as text: the experiment's analysis code and the authors' level labels).
##Usage: Rscript sances_2026.R <dir holding voters.dta> <output dir>   (voters.dta = the original .dta)
##
##1,011 respondents in two samples (sample: "forthright" = Bovitz Forthright panel, 509; "mturk", 502),
##5 tasks (pair) x 2 candidates (candidate a/b -> profile 1/2). The authors analyse the samples
##separately (figure4.do/figure5.do keep sample == "forthright"; "bovitz" is the main data), so they are
##two tables, one per sample: sances_2026_prosecutors_forthright and sances_2026_prosecutors_mturk.
##Outcome choice = vote: which of the two candidates the respondent votes for (wording not deposited);
##exactly one chosen per answered pair (checked). 8 pairs (16 rows) have no answer and are dropped
##(one respondent answered none). No opt-out.
##Attributes as deposited text (codebook tabulations; respondents saw these words, the figure code
##uses them too): attr_sex (Female/Male), attr_race (African American, Asian American, Hispanic,
##White), attr_education (Ivy League university, Small college, State university), attr_legal_experience
##(Assistant district attorney, Defense attorney, Public defender), attr_age (35-75 years, as the number).
##attr_conviction_rate: 70-100, written "70%".."100%" as in figure4.do's labels; the deposit stores 0
##exactly when the candidate is not an assistant DA (ada == 0, checked one-to-one), i.e. the rate
##was shown only for prosecutors -> "(not shown)" on all other profiles (inferred from that pattern).
##CODED ATTRIBUTES (#3474): the candidate's positions on marijuana legalization, the death penalty and
##three-strikes laws are stored only as -1/0/1 with no labels in the codebook, the .do files or the
##README, and the article is unreachable: attr_marijuana_code, attr_death_penalty_code,
##attr_three_strikes_code keep -1/0/1. Known: the three share one direction (the deposit's derived
##candidate ideology equals -(marijuana + deathpenalty + threestrikes)); which end is the reform
##position and the displayed wording are not documented.
##Randomization restrictions and attribute order: not documented (beyond the conviction-rate rule).
##Covariates: cov_age (age_self), cov_female_self (1 = female, 0 = not; the codebook does not say
##whether 0 is only male), cov_white_self, cov_educ_self_code (0/1, unlabelled), and the respondent's
##own positions cov_marijuana_self_code / cov_death_penalty_self_code / cov_three_strikes_self_code
##(-1/0/1, same coding as the attributes). Dropped: Qualtrics ResponseId (re-keyed 1..n per table),
##pid_self1-4 (unlabelled dummies), the authors' derived ideology/distance/dummy/interaction variables.
##No survey weight.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(zap_labels(read_dta(file.path(raw, "voters.dta"))))
stopifnot(nrow(k) == 10110L, uniqueN(k$responseid) == 1011L, all(k$candidate %in% c("a", "b")))
stopifnot(all((k$convictionrate == 0) == (k$legalexperience != "Assistant district attorney")),
          all(k$convictionrate[k$convictionrate > 0] %in% seq(70, 100, 5)))
stopifnot(all(k$ideology == -(k$marijuana + k$deathpenalty + k$threestrikes)))
k <- k[!is.na(vote)]
for (s in c("forthright", "mturk")) {
  x <- k[sample == s]
  d <- data.table(id = match(x$responseid, sort(unique(x$responseid))), task = as.integer(x$pair),
                  profile = fifelse(x$candidate == "a", 1L, 2L), choice = as.integer(x$vote))
  stopifnot(d[, .N, .(id, task)][, all(N == 2L)], d[, sum(choice), .(id, task)][, all(V1 == 1L)])
  d[, attr_sex := x$sex]
  d[, attr_race := x$race]
  d[, attr_education := x$education]
  d[, attr_legal_experience := x$legalexperience]
  d[, attr_age := as.character(x$age)]
  d[, attr_conviction_rate := fifelse(x$convictionrate == 0, "(not shown)", paste0(x$convictionrate, "%"))]
  for (v in c("marijuana", "deathpenalty", "threestrikes")) stopifnot(all(x[[v]] %in% -1:1))
  d[, attr_marijuana_code := as.integer(x$marijuana)]
  d[, attr_death_penalty_code := as.integer(x$deathpenalty)]
  d[, attr_three_strikes_code := as.integer(x$threestrikes)]
  d[, cov_age := as.integer(x$age_self)]
  d[, cov_female_self := as.integer(x$female_self)]
  d[, cov_white_self := as.integer(x$white_self)]
  d[, cov_educ_self_code := as.integer(x$educ_self)]
  d[, cov_marijuana_self_code := as.integer(x$marijuana_self)]
  d[, cov_death_penalty_self_code := as.integer(x$deathpenalty_self)]
  d[, cov_three_strikes_self_code := as.integer(x$threestrikes_self)]
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("sances_2026_prosecutors_", s, ".csv")))
}
