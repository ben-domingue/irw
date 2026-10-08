##International-crisis resolve conjoint (public vs private threats) from
##Takei, M. (2024). Audience costs and the credibility of public versus private threats in
##international crises. International Studies Quarterly, 68(3), sqae091.
##https://doi.org/10.1093/isq/sqae091
##Replication data: Harvard Dataverse doi:10.7910/DVN/2DCTJW, CC0 1.0. File read (inside
##ISQ_Takei_2024.zip): ISQ_public threat_Takei.dta. Read as text: ISQ Replication Takei.do,
##ISQ_Weighted Analysis_2024.R, ISQ_Final Version_Appendix_Takei.pdf (appendix).
##Usage: Rscript takei_2024.R <raw dir holding the unzipped ISQ_Takei_2024/ folder> <output dir>
##
##1,203 US Prolific respondents (February 2023, per the article), 8 disputes x 2 countries
##(19,248 rows, matching appendix Table 1). Design adapted from Kertzer, Renshon & Yarhi-Milo
##(2021). Outcomes (article text, quoting the Kertzer et al. instrument it adopted):
##  rating = CountryA/B_t_Rate: "Given the information available, what is your best estimate about
##           whether Country A will stand firm in this dispute, ranging form 0 percent to 100
##           percent?" (0-100, higher = more likely to stand firm; the authors' `rate` is this/100).
##  choice = CountryA/B_t: which of the two countries is more likely to stand firm (article fn. 6
##           gives Kertzer et al.'s wording "If you had to choose between them, which of the two
##           countries is more likely to stand firm?"); forced choice, exactly one per pair.
##task/profile: each row of the .dta carries exactly one non-missing wide block (threat<t><A/B>
##...), which gives task t and profile A=1/B=2; the long attribute codes, rate and choice were
##checked against that block for every row.
##Level text = the displayed sentence fragments in appendix Tables 3-4 (the stems "In the current
##crisis, the country...", "The leader...", "The domestic public and elites...", "At the time,
##the country was..." are not repeated). Codes -> fragments follow the long-file Stata labels
##(e.g. threat 0 = Private, 1 = Public, 2 = No Verbal Threat). NOTE: the wide popular<t><A/B>
##columns equal the long `unpopular` code on every row; the long label (1 = Unpopular), which the
##authors' models use, is followed.
##Restrictions: none (appendix p.7: no restrictions on combinations, so e.g. "the United States"
##can be "a dictatorship"; the authors' robustness check drops such profiles).
##Dropped: the authors' derived variables (inattention flags, threat_hawk_female, threeway) and
##the wide duplicates. Covariates keep the appendix codings: cov_male, cov_age (1 = 18-24 ...
##6 = 65+), cov_white, cov_ideology (1 = extremely conservative ... 7 = extremely liberal),
##cov_income (1-9), cov_democrat. The survey weights in the appendix were computed on the fly
##and are not deposited.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "ISQ_Takei_2024", "ISQ_public threat_Takei.dta")
if (!file.exists(f)) f <- file.path(raw, "ISQ_public threat_Takei.dta")
x <- as.data.table(zap_labels(read_dta(f)))
x[, task := NA_integer_][, profile := NA_integer_]
for (t in 1:8) for (p in c("A", "B")) {
  i <- which(!is.na(x[[sprintf("threat%d%s", t, p)]]))
  x[i, task := t][i, profile := if (p == "A") 1L else 2L]
  stopifnot(all(abs(x[[sprintf("Country%s_%d_Rate", p, t)]][i] / 100 - x$rate[i]) < 1e-4),
            all(x[[sprintf("Country%s_%d", p, t)]][i] == x$choice[i]))
}
stopifnot(!anyNA(x$task), x[, .N, .(id, task, profile)][, all(N == 1)])
m <- function(v, labs) labs[as.character(v)]
d <- data.table(id = as.integer(x$id), task = x$task, profile = x$profile, choice = as.integer(x$choice),
                rating = as.integer(round(x$rate * 100)))
d[, attr_threat := m(x$threat, c("0" = "has made a threat through secret diplomatic channels that they will use force if the other country does not back down. Since this threat has been made privately, none of the public of the country knows the existence and content of the threat",
                                "1" = "has made a public threat that they will use force if the other country does not back down. Since this threat has been made publicly, many of the public of the country know the existence and content of the threat",
                                "2" = "has yet to make any statements"))]
d[, attr_mobilization := m(x$mobl, c("0" = "has not mobilized troops", "1" = "has mobilized troops"))]
d[, attr_hawkishness := m(x$hawk, c("0" = "prefer peaceful solutions", "1" = "prefer military solutions"))]
d[, attr_popularity := m(x$unpopular, c("0" = "is popular domestically", "1" = "is unpopular domestically"))]
d[, attr_capability := m(x$capability, c("0" = "does not have a very powerful military", "1" = "has a very powerful military"))]
d[, attr_stakes := m(x$stake, c("0" = "low", "1" = "high"))]
d[, attr_regime := m(x$regime, c("0" = "a dictatorship", "1" = "a democracy"))]
d[, attr_foreign_relations := m(x$foreign, c("0" = "an adversary of the United States", "1" = "an ally of the United States", "2" = "the United States"))]
d[, attr_leader_gender := m(x$female, c("0" = "He", "1" = "She"))]
d[, attr_time_in_office := m(x$newleader, c("0" = "has been in power for many years", "1" = "recently took office"))]
d[, attr_military_experience := m(x$milexp, c("0" = "does not have experience in the military", "1" = "has served in the military briefly", "2" = "had a long career in the military"))]
d[, attr_past_initiator := m(x$initiator, c("0" = "it was challenged", "1" = "it initiated the crisis"))]
d[, attr_past_other_state := m(x$identity, c("0" = "ally of the United States", "1" = "adversary of the United States"))]
d[, attr_past_outcome := m(x$outcome, c("0" = "the country ultimately stood firm", "1" = "the country ultimately backed down"))]
d[, attr_past_leader := m(x$leadchange, c("0" = "led by the same leader as the one in the current dispute", "1" = "led by a different leader than the one in the current dispute"))]
for (v in c("Male", "Age", "White", "Ideology", "Income", "Democrat")) d[, paste0("cov_", tolower(v)) := as.integer(x[[v]])]
stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]), d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "takei_2024_public_threats.csv"))
