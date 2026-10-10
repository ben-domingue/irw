##EU rule-of-law sanctions conjoint (Hungary, Poland, Bulgaria) from
##Blauberger, M., Makaradze, S., & Spilker, G. (2025). International sanctions and domestic
##backlash. Exploring public support towards the EU's rule of law enforcement. European Union
##Politics, 27(1), 60-87. https://doi.org/10.1177/14651165251395302
##Replication data: Harvard Dataverse doi:10.7910/DVN/9ZDOWV, CC0 1.0, no restricted files.
##Files read: conjoint_final_Hungary.dta, conjoint_final_Poland.dta, conjoint_final_Bulgaria.dta
##(Dataverse "original format" downloads); Replication_M_B_S_2025.do read as text.
##Usage: Rscript blauberger_2025.R <raw dir> <output dir>
##
##THREE TABLES, one per country: the authors analyse each country separately (separate MM/AMCE
##figures per file in the .do; Bulgaria reported as a further case) and never pool them.
##  blauberger_2025_sanctions_hu (2,018 respondents), _pl (2,010), _bg (2,009).
##Each respondent saw 5 pairs of hypothetical EU sanction proposals against their own country
##with 6 attributes. Outcomes (variable labels; the article was not accessible, so wording is
##paraphrased):
##  choice = `choice` ("proposal forced choice: 1= chosen"); forced, no opt-out.
##  rating = `rating` ("rating of proposal: 1-7"; .do axis title "Support for sanction proposal:
##           1 (no support) to 7 (high support)"); higher = more support.
##Task and profile are INFERRED from row order: each file stacks 10 blocks, each holding respondents
##1..N in order (verified); blocks 2t-1 and 2t are the two profiles of task t (verified: every
##such pair has exactly one chosen profile in all three files, while pairing block t with t+5
##does not). That block 2t-1 was shown on the left is assumed.
##Attributes, text = the .dta value labels (short English labels, not the displayed wording in
##the national language): accusation ("Framing": Misuse of money / Undermine judiciary /
##Discriminate LGBTQI), consequence (Full suspension / Projects only / 50% reduction),
##other_eu_states ("EU States" supporting: 15 of 27 / 20 of 27 / 25 of 27), dom_opposition
##("Domestic Opposition": Pro government / Pro EU / Divided), response ("Procedure": Justify /
##Appeal / Nothing), trigger (based_on_new: Civil society / Annual report / Commission report).
##Covariates (Hungary and Poland only; Bulgaria has none), from .dta value labels:
##cov_gender (Gender 0 Female -> female, 1 Male -> male, missing NA); the authors' dichotomised
##groupings cov_age2 (Young/Old), cov_rural (Urban/Rural), cov_income2 (Poor/Well-off),
##cov_education2 (Low/High), cov_partisanship (Opposition / Fidesz or PIS / None), all as label
##text (cut-points not documented; the raw items are not deposited); cov_blame ("blame
##attribution": EU / Government / Both / DK). No survey weight in the deposit.
##respondent is a running number (kept as id).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(v) as.character(as_factor(v, levels = "labels"))
cc <- c(hu = "Hungary", pl = "Poland", bg = "Bulgaria")
for (cc2 in names(cc)) {
  cn <- cc[[cc2]]
  k <- read_dta(file.path(raw, paste0("conjoint_final_", cn, ".dta")))
  N <- length(unique(k$respondent))
  stopifnot(nrow(k) == 10 * N, all(k$respondent == rep(seq_len(N), 10)))
  blk <- (seq_len(nrow(k)) - 1L) %/% N + 1L
  d <- data.table(id = as.integer(k$respondent), task = (blk + 1L) %/% 2L, profile = 2L - blk %% 2L,
                  choice = as.integer(k$choice), rating = as.integer(k$rating),
                  attr_accusation = lab(k$accusation), attr_consequence = lab(k$consequence),
                  attr_other_eu_states = lab(k$other_EU_states), attr_dom_opposition = lab(k$dom_opposition),
                  attr_response = lab(k$response), attr_trigger = lab(k$based_on_new))
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:7),
            !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
  if ("Gender" %in% names(k)) {
    stopifnot(all(zap_labels(k$Gender) %in% c(0, 1, NA)))
    d[, cov_gender := c("female", "male")[as.integer(zap_labels(k$Gender)) + 1L]]
    d[, `:=`(cov_age2 = lab(k$age), cov_rural = lab(k$Rural), cov_income2 = lab(k$Income), cov_education2 = lab(k$education),
             cov_partisanship = lab(k$partisanship), cov_blame = lab(k$blame))]
  }
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("blauberger_2025_sanctions_", cc2, ".csv")))
}
