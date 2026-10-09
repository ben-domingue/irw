##Interest-group involvement factorial vignette experiment (UK, US, Germany) from
##Rasmussen, A., & Reher, S. (2023). (Inequality in) interest group involvement and the
##legitimacy of policy-making. British Journal of Political Science, 53(1), 45-64.
##https://doi.org/10.1017/S0007123422000242
##Replication data: Harvard Dataverse doi:10.7910/DVN/GPGWKJ, CC0 1.0, no restricted files.
##File read: RR_BJPOLS_2022.dta (Dataverse "original format" download of RR_BJPOLS_2022.tab).
##Codings and outcome wording from Codebook_RR_BJPOLS_2022.pdf (3 pp.); analysis choices from
##Replication-code_RR_BJPOLS_2022.do (read as text, not run).
##Usage: Rscript rasmussen_2023.R <raw dir> <output dir>
##
##Online samples in the UK, the US and Germany. Each respondent read up to two vignettes about a
##legislative decision preceded by an interest-group consultation, one on a hybrid-car tax
##reduction and one on restricting the sugar content of food (trial_issue), in random order
##(the source's `group`: 1 = hybrid first, 2 = sugar first; task = position of the vignette in
##that order). Three factors were randomized per vignette (codebook): attr_representation
##("Numerical representation of interest group types in consultation": None / Equal
##representation / More cause groups / More business groups), attr_attainment ("Policy
##attainment of interest groups": Against both group types' positions / In line with both group
##types / In line with business groups only / In line with cause groups only) and
##attr_public_support ("Public support for policy decision": 70% against the decision / 55%
##against / 55% support for the decision / 70% support). The cause group is environmental
##groups on the hybrid-car issue and consumer organisations on the sugar issue (codebook,
##res_*_difference). LEVELS ARE THE CODEBOOK'S LABELS, not the vignette wording, which is not
##deposited; respondents in Germany saw German text. One profile per task (profile = 1).
##ONE TABLE, countries pooled (cov_country GB/US/DE): the authors pool them with country fixed
##effects (do-file Table 1) and the level labels are shared.
##Outcomes, six agreement items after each vignette, stored as the deposit codes them:
##0 = strongly disagree, 1 = disagree somewhat, 2 = neither agree nor disagree, 3 = agree
##somewhat, 4 = strongly agree (codebook): rating_fair "The process that led to the policy
##decision was fair."; rating_right "Legislators made the right decision."; rating_actors "When
##making the decision, policy-makers took the views of all relevant actors into account.";
##rating_citizens "Legislators made the decision that is best for the citizens of [country].";
##rating_democratic "The process that led to the decision was democratic"; rating_affected
##"Legislators made the best decision for those who are affected by the policy." No choice.
##Rows: the source has one row per respondent x issue (33,286 rows, 22,039 respondents), but
##5,900 rows have none of the six items (all 2,463 rows with no recorded order among them); they
##are omitted. Respondents with a single vignette all failed a check; most saw only the first
##experiment. Respondents who failed checks are KEPT (the authors drop them for the main models
##and keep them in SI 4): cov_attention_pass = 1 - failedattention ("failed at least one of two
##attention checks", so 1 = passed both), cov_failed_manipulation (1 = failed at least 5 of 8
##manipulation checks).
##Covariates: cov_age (years), cov_gender (female 0/1 -> male/female; codebook),
##cov_ideology (0 = left .. 10 = right), cov_res_econ_bus/env/con and cov_res_repres_bus/env/con
##(agreement that business groups / environmental groups / consumer organisations have high
##economic resources / represent society as a whole, 0-4 as above). Dropped: the authors'
##derived scales (leg_proc, leg_subs, outfav = support for the policy recoded by the decision,
##res_*_difference). No survey weight in the deposit.
##Restrictions: none; the article says "the assignment of values of each attribute is independent
##from the values of the other attributes"; all 64 combinations occur (checked below). Level
##probabilities are not stated. Fielded on Qualtrics panels Jul-Oct 2019 (article).
##N: the article reports 9,357 respondents after the checks (UK 3,048, US 3,179, DE 3,130); this
##table has 16,808 respondents in all, 9,317 of whom passed both checks (40 fewer than the article;
##not resolved).
##Spot check: Table 1 model 1 (leg_proc from the three procedural items, failed respondents
##dropped, with the source's outfav) gives None vs Equal -0.947 as in the article's Figure 2.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "RR_BJPOLS_2022.dta")))
items <- c("fair", "right", "actors", "citizens", "democratic", "affected")
k <- k[rowSums(!is.na(as.matrix(k[, paste0("leg_", items), with = FALSE]))) > 0]
stopifnot(!anyNA(k$group), k[, .N, id][, all(N <= 2)], k[, uniqueN(country), id][, all(V1 == 1)],
          k[, uniqueN(group), id][, all(V1 == 1)], k[, !anyDuplicated(paste(id, issue))])
lv <- function(x, codes, l) { x <- as.integer(x); stopifnot(all(x %in% codes)); l[match(x, codes)] }
d <- data.table(id = as.integer(k$id),
                task = as.integer(fifelse(as.integer(k$group) == as.integer(k$issue), 1L, 2L)),
                profile = 1L)
for (i in items) d[, paste0("rating_", i) := as.integer(k[[paste0("leg_", i)]])]
d[, `:=`(attr_representation = lv(k$repres, 1:4, c("None", "Equal representation", "More cause groups", "More business groups")),
         attr_attainment = lv(k$attain, 1:4, c("Against both group types' positions", "In line with both group types",
                                               "In line with business groups only", "In line with cause groups only")),
         attr_public_support = lv(k$public, 0:3, c("70% against the decision", "55% against", "55% support for the decision",
                                                   "70% support")),
         trial_issue = lv(k$issue, 1:2, c("hybrid car tax reduction", "sugar content restrictions")),
         cov_country = lv(k$country, 1:3, c("GB", "US", "DE")),
         cov_age = as.integer(k$age),
         cov_gender = lv(k$female, 0:1, c("male", "female")),
         cov_ideology = as.integer(k$ideology),
         cov_attention_pass = 1L - as.integer(k$failedattention),
         cov_failed_manipulation = as.integer(k$failedmanipulation))]
for (v in c("res_econ_bus", "res_econ_env", "res_econ_con", "res_repres_bus", "res_repres_env", "res_repres_con"))
  d[, paste0("cov_", v) := as.integer(k[[v]])]
stopifnot(all(unlist(d[, paste0("rating_", items), with = FALSE]) %in% c(0:4, NA)),
          d[, .N, .(attr_representation, attr_attainment, attr_public_support)][, .N] == 64,
          !anyDuplicated(d[, .(id, task)]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "rasmussen_2023_interest_groups.csv"))
