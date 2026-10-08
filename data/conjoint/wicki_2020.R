##Vehicle-emission policy-package conjoint (Switzerland, December 2017) from
##Wicki, M., Huber, R. A., & Bernauer, T. (2020). Can policy-packaging increase public support for costly
##policies? Insights from a choice experiment on policies against vehicle emissions. Journal of Public
##Policy, 40(4), 599-625. https://doi.org/10.1017/S0143814X19000205 (a corrigendum follows at
##pp. 626-627; not seen).
##Replication data: Harvard Dataverse doi:10.7910/DVN/LUJC8I, CC0 1.0. File read: replication_data.RData
##(Dataverse "original format"; object df_conj_out2). JPP_replication_code.R read as text, not run.
##Wording and level text from the author version of the article (ETH Research Collection,
##20191009_MainDocument_complete.pdf): Sampling/Survey/Experiment sections and Table 1.
##Usage: Rscript wicki_2020.R <dir holding replication_data.RData> <output dir>
##
##IPSOS online quota sample of 2,034 Swiss residents (8-21 December 2017), all 26 cantons, in French,
##German and Italian (the respondent's language is not in the deposit). 2,034 respondents = the article.
##5 tasks x 2 policy-packages ("proposal 1/2"), 9 attributes, all shown in every task. Outcomes:
##  choice = choice, "If you had to decide: Which of the two proposals would you choose?" (forced
##           choice, no opt-out; exactly one per task, checked).
##  rating = rate, "How much do you agree or disagree with proposal 1/2?", 1-7; higher = agree more
##           (packages chosen average 5.0, not chosen 3.4). The end labels are not given.
##Wording is the article's English (survey original in German, French, Italian).
##task = round, profile = policy A/B (recorded). Between-respondent frame (trial_frame): "EV promotion"
##(source ECars) or "emission reduction" (source Emissions), per the article.
##Attribute text: the deposit stores codes _1.._5 with the authors' short labels ("1) No Car Ban").
##They are written out with the English characteristic text of Table 1 (without its "No:"/"Yes:"
##prefix; earmarking levels complete the stem "Revenues from road pricing and car tax are mainly used
##for..."); Table 1 calls the table "a hybrid" of the attribute descriptions and the overview shown, so
##this is the authors' English rendering, not the screen text (originals in SI Tables A12/A13, not
##deposited). Codes map 1:1, in order, to the authors' factor labels in the data (attrib*_lab, e.g.
##_4 = "Public Transportation Price Reduction", _1 = "Fedeal Gov't"), which name the Table 1 levels.
##Attribute order was randomized per respondent and kept for all tasks, but it is not in the deposit.
##Restrictions: the article says characteristics were "randomly assigned for each choice task", but
##the shares are clearly unequal and not independent (implementation year 2045 in 25% of profiles;
##car-registration ban 47%; earmarking for roads only appears with "no road pricing, car tax" in 787
##profiles against about 1,400 for the other three combinations), so restrictions = observed.
##Footnote viii says either road pricing or the car tax is always present; the car tax attribute's
##"no" level keeps the current (cantonal) car tax, and 25% of profiles have neither new measure.
##Covariates: cov_age (years), cov_gender, cov_education (the authors' 4 groups). usagecar (0-7) is
##undocumented and dropped. IDs are the authors' sequential integers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "replication_data.RData"), envir = e)
s <- as.data.table(as.data.frame(e$df_conj_out2))
stopifnot(nrow(s) == 20340L, uniqueN(s$id) == 2034L)
lv <- list(
  energy_label = c("Keep current energy label", "Introduce stricter label to show independently tested fuel consumption and exhaust emissions"),
  registration = c("Keep current registration rules, without taking emission levels into account", "No registration of new cars with high emission levels"),
  road_pricing = c("No introduction of such a user fee", "Introduction of emission- and kilometre-dependent usage fee"),
  car_tax = c("Keep current car tax", "Adjustment and harmonisation of car tax at federal level by scaling it more strongly on emission levels"),
  earmarking = c("construction and maintenance of roads", "construction and maintenance of roads and public transportation infrastructure",
                 "general federal budget from which various government expenditures are paid", "public transportation subsidies to reduce costs of using it"),
  campaign = c("No accompanying information campaign", "Switzerland-wide accompanying information campaign"),
  implementation_year = c("2025", "2030", "2035", "2040", "2045"),
  test_phase = c("Policy-package will be introduced without a test phase", "Policy-package will be introduced beginning with a two years test phase and its evaluation"),
  experts = c("The policy-package is designed and implemented by the government", "The policy-package is designed and implemented by the government with the involvement of non-governmental experts"))
src <- c(energy_label = 2, registration = 1, road_pricing = 3, car_tax = 4, earmarking = 5, campaign = 6, implementation_year = 7, test_phase = 8, experts = 9)
d <- s[, .(id = as.integer(id), task = as.integer(round), profile = match(policy, c("A", "B")), choice = as.integer(choice), rating = as.integer(rate))]
for (v in names(src)) {
  code <- as.integer(sub("_", "", s[[paste0("Attrib", src[[v]])]]))
  lab <- as.character(s[[paste0("attrib", src[[v]], "_lab")]])
  stopifnot(uniqueN(paste(code, lab)) == uniqueN(code), uniqueN(code) == length(lv[[v]]))  # code <-> authors' label is 1:1
  d[, paste0("attr_", v) := lv[[v]][code]]
}
stopifnot(all((s$attrib1_lab == "2) Car Ban") == (s$Attrib1 == "_2")), all((s$attrib2_lab == "2) Tighter Energy Label") == (s$Attrib2 == "_2")))
d[, trial_frame := c(ECars = "EV promotion", Emissions = "emission reduction")[as.character(s$frame)]]
d[, cov_age := as.integer(s$age)][, cov_gender := as.character(s$gender)][, cov_education := as.character(s$edu)]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^trial_")]), d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:7))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wicki_2020_vehicle_emissions.csv"))
