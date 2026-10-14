##Judicial-reform scenario experiment (Ukraine sample) from
##Mazepus, H., & Toshkov, D. (2021). Standing up for democracy? Explaining citizens' support for democratic checks
##and balances. Comparative Political Studies. https://doi.org/10.1177/00104140211060285
##Replication data: Harvard Dataverse doi:10.7910/DVN/6HGYSA, CC0 1.0. Files read: data-survey/replicate_exp_survey_ua.csv
##(saved locally as ua.csv), "Translations of the experiment and main measures" .docx (English original of the vignettes,
##RU/UA translations; saved as trans.docx), "2 Replication - analysis UA sample.R" (ua.R; text, not run).
##Usage: Rscript mazepus_2021.R <dir holding ua.csv> <output dir>
##
##577 Ukrainian respondents (weighted online sample, the paper's UA N), one scenario each, a 3 x 2 between-subject
##factorial (columns Situation1-6 = C1-C6 of the translations document, confirmed by ua.R's condition recode):
##  party_info: "one of the political parties in your country wins the majority" (neutral, no party named) / "the
##    political party that you support wins ..." / "the political party that you oppose wins ..."
##  income_performance: "the levels of income of most citizens remained the same as under the previous government" /
##    "... increased by comparison to the levels achieved by the previous government"
##The rest of the scenario is fixed: the government starts a reform of how judges are appointed and dismissed
##(not in the party programme; needs a constitutional change; "needed to get rid of the corrupt judges that were working
##for the previous government"). Level text is the English original in the translations document (the survey ran in
##Russian or Ukrainian; which each respondent saw is not recorded). Level text = the document's English clause.
##One task of one profile per respondent, id = row order. Outcomes (1-7, "using the scale from 1 'not at all' to
##7 'fully'"; higher = more), raw, no opt-out:
##  rating_gov_support   "To what extent would you support this government?" (Q1.1)
##  rating_gov_trust     "... trust this government?" (Q1.2)
##  rating_reform_justified "To what extent do you think the decision to reform the appointment of judges is justified?" (Q1.3)
##  rating_reform_acceptable "... is acceptable?" (Q1.4)
##  rating_vote          "How likely is it that you would vote for this party in the next election?" 1 = not likely at all,
##                       7 = extremely likely (Q1A); the derived dv.index is dropped.
##Dropped: the manipulation checks (M1-M3), democracy-attitude items, trust in institutions, ideology scales, settlement,
##education and status variables. Covariates: cov_gender (sex: 1 male, 2 female, from ua.R), cov_age (years),
##cov_survey_weight (weight_$, mean 1). The Dutch sample in the same deposit (exp_survey_nl_combined.csv, N = 193) is NOT built:
##it records only the party-information arm (the income arm and the per-respondent mix of 2-3 repeated vignettes
##are missing; outcomes are sums over vignettes), so it is not a profile table.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "ua.csv"))
stopifnot(nrow(d) == 577)
S <- as.matrix(d[, paste0("Situation", 1:6), with = FALSE]); stopifnot(all(rowSums(S) == 1))
cond <- max.col(S)
party <- c("One of the political parties in your country wins the majority at a fully competitive and fair election",
           "The political party that you support wins the majority at a fully competitive and fair election",
           "The political party that you oppose wins the majority at a fully competitive and fair election")[(cond + 1) %/% 2]
perf <- c("Under this government, the levels of income of most citizens remained the same as under the previous government",
          "Under this government, the levels of income of most citizens increased by comparison to the levels achieved by the previous government")[2 - cond %% 2]
r <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L,
  rating_gov_support = as.integer(d$Q1.1), rating_gov_trust = as.integer(d$Q1.2), rating_reform_justified = as.integer(d$Q1.3),
  rating_reform_acceptable = as.integer(d$Q1.4), rating_vote = as.integer(d$Q1A),
  attr_party_info = party, attr_income_performance = perf,
  cov_gender = c("male", "female")[d$sex], cov_age = as.integer(d$age), cov_survey_weight = d[["weight_$"]])
stopifnot(!anyNA(r[, 4:8]), all(unlist(r[, 4:8]) %in% 1:7))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "mazepus_2021_judicial_reform_ua.csv"))
