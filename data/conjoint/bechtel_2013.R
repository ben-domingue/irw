##Global climate agreement conjoint (France, Germany, UK, US; 2012) from
##Bechtel, M. M., & Scheve, K. F. (2013). Mass support for global climate agreements depends on
##institutional design. Proceedings of the National Academy of Sciences, 110(34), 13763-13768.
##https://doi.org/10.1073/pnas.1306374110
##Replication data: Harvard Dataverse doi:10.7910/DVN/UGZ2BY (the authors' own archive), CC0 1.0.
##The same data are re-hosted (as pnas_cjoint / SetupPNAS-All) in Ratkovic & Tingley's replication
##archive doi:10.7910/DVN/RNMB1Q (CC0); this script reads the originator's file instead.
##File read: bechtel_scheve_pnas.dta (Dataverse "original format"). Variable meanings from Readme.doc;
##wording and level text from the article (Table 1) and SI Appendix (PNAS-2013-Bechtel-Scheve_SI.pdf),
##both in the deposit. The authors' .do file was read as text, not run.
##Usage: Rscript bechtel_2013.R <dir holding bechtel_scheve_pnas.dta> <output dir>
##
##YouGov internet samples, summer 2012: 2,000 each in France, Germany and the UK, 2,500 in the US
##(8,500 = the article's N; 68,000 agreements). 4 comparisons of 2 agreements per respondent, 6
##attributes, levels "randomly assigned" for each agreement (SI p.3); no restrictions stated. The order
##of the dimensions was randomized per respondent and fixed across the 4 comparisons; the deposit's
##cj_order holds an undocumented code for that order (696 distinct values), so no attrpos_ is built.
##One table per country. The article pools the four countries (Fig. 2), but the cost and sanction
##levels were shown in each country's currency and amount (Table 1 footnote: "values are given in
##order for France, Germany, the United Kingdom, and the United States"), and respondents saw French,
##German or English, so the level text cannot be shared.
##Outcomes (SI p.2):
##  choice = choice_cj. "For each comparison we would like to know which of the two agreements you
##           prefer. ... Regardless of your overall evaluation, please indicate which alternative you
##           prefer over the other." Forced choice, no opt-out; exactly one chosen per pair (checked).
##  rating = rating_cj. "If you could vote on each of these agreements in a referendum, how likely is it
##           that you would vote in favor or against each of the agreements? Please give your answer on
##           the following scale from definitely against (1) to definitely in favor (10)." 10 =
##           definitely in favor. Stored as answered (the article rescales it to 0-100).
##task = conjoint (recorded). profile = row order within respondent x conjoint (inferred; the deposit
##has no position column; each pair has exactly 2 rows and exactly one chosen).
##Attribute text: the deposit's value labels are the French amounts with a mangled euro sign and
##abbreviations ("Prop. to current emissions"), so levels are written from the article's Table 1 and
##the SI figure labels: cost "EUR 28".."EUR 141" (France), "EUR 39".."EUR 193" (Germany), "£15".."£75"
##(UK), "$53".."$267" (US), each followed by " per month" as in the deposit's labels; sanctions
##"None" or the country's amount + " per household and month" (deposit label "per hh and month");
##distribution, participation, emissions and monitoring as in Table 1 / the deposit labels ("20 of
##192", "40% of current emissions", "Your government"). Text is English for all four countries; the
##exact French/German screen text is not in the deposit. The euro sign is written "EUR" as in the SI.
##Covariates: cov_survey_weight = weight; cov_age; cov_ideology (0 = left .. 10 = right); cov_female
##(1 = female); cov_income (country-specific income bands, codes as in Readme.doc); cov_education
##(the country's own education-group variable: FR 1 = CAP/BEP or less, 2 = Bac to Bac+2, 3 = Bac+3 or
##more; DE and UK 1 = 16 years or fewer, 2 = 17-19, 3 = 20 or more; US 1 = HS or less, 2 = some
##college, 3 = college graduate, 4 = postgraduate); cov_know_defense and cov_know_term (political
##knowledge items, 1 = correct); cov_attention_pass (1 = passed the attention test).
##Dropped: the authors' median-split indicators (recip_s_high_group, support_iec_high_group,
##ewill_pay_high, reductions_important, right, inc_high_group, educ_high), incon (derived
##rating/choice inconsistency flag), gender (duplicate of female), cj_order (undocumented code).
##The source ID is a 9-digit panel respondent number; re-keyed to integers in file order.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "bechtel_scheve_pnas.dta"))))
stopifnot(nrow(s) == 68000L, uniqueN(s$ID) == 8500L, s[, .N, .(ID, conjoint)][, all(N == 2)])
s[, profile := seq_len(.N), .(ID, conjoint)]
cost <- list(fr = paste("EUR", c(28, 56, 84, 113, 141)), de = paste("EUR", c(39, 77, 116, 154, 193)),
             uk = paste0("£", c(15, 30, 45, 60, 75)), us = paste0("$", c(53, 107, 160, 213, 267)))
sanc <- list(fr = paste("EUR", c(6, 17, 23)), de = paste("EUR", c(8, 23, 31)), uk = paste0("£", c(3, 9, 12)),
             us = paste0("$", c(11, 32, 43)))
dist <- c("Only rich countries pay", "Proportional to current emissions", "Proportional to history of emissions",
          "Rich countries pay more than poor countries")
mon <- c("Your government", "Independent commission", "United Nations", "Greenpeace")
educ <- c(fr = "educgr_fr", de = "educgr_ge", uk = "educgr_uk", us = "educgr_us")
for (cc in names(cost)) {
  x <- s[country == match(cc, c("fr", "de", "uk", "us"))]
  ids <- unique(x$ID)
  d <- x[, .(id = match(ID, ids), task = as.integer(conjoint), profile = as.integer(profile),
             choice = as.integer(choice_cj), rating = as.integer(rating_cj),
             attr_cost = paste(cost[[cc]][cost_cj], "per month"), attr_cost_distribution = dist[distrib_cj],
             attr_participating_countries = c("20 of 192", "80 of 192", "160 of 192")[ctries_cj],
             attr_emissions_covered = c("40% of current emissions", "60% of current emissions", "80% of current emissions")[emissions_cj],
             attr_sanctions = c("None", paste(sanc[[cc]], "per household and month"))[sanctions_cj],
             attr_monitoring = mon[monitoring_cj],
             cov_survey_weight = weight, cov_age = as.integer(age), cov_ideology = as.integer(ideology),
             cov_female = as.integer(female), cov_income = as.integer(income), cov_education = as.integer(get(educ[[cc]])),
             cov_know_defense = as.integer(gknow1), cov_know_term = as.integer(gknow3),
             cov_attention_pass = as.integer(attentioncheck_pass))]
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^choice$|^rating$")]), d[, sum(choice), .(id, task)][, all(V1 == 1)],
            d[, all(rating %in% 1:10)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("bechtel_2013_climate_agreements_", cc, ".csv")))
}
