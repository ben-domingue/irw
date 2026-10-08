##Tax-reform package conjoint (Germany, 2021) from
##Becker, B., Castanho Silva, B., & Lierse, H. (2025). Taxing your cake and growing it too: Public
##beliefs on the dual benefits of progressive taxation. Journal of Public Policy, 46, 1-20.
##https://doi.org/10.1017/S0143814X25100858
##Replication data: Harvard Dataverse doi:10.7910/DVN/R5SDWN, CC0 1.0. File read:
##replication_data_jpp.csv. Variable meanings from README.pdf; wording and level text from the
##article's Table 1 (open access, CC BY). analysis.Rmd read as text, not run.
##Usage: Rscript becker_2025.R <dir holding replication_data_jpp.csv> <output dir>
##
##921 respondents in the deposit (Lucid online sample with quotas on age, gender and region, fielded
##during the 2021 German federal election campaign), 5 comparisons of 2 tax-reform packages, 3
##attributes (personal income, inheritance and corporate tax), 5 levels each. The article reports
##1,360 completes and 146 removed for failing the attention check (so about 1,214 analysed); the
##deposit has 921 and the gap is not explained (not fixed here).
##task and profile come from candidate_number (README: 1 = first package of the first comparison,
##2 = second package of the first comparison, ...): task = (candidate_number + 1) %/% 2, profile =
##2 - candidate_number %% 2. Recorded, not inferred.
##Outcomes (Table 1: "To which of the reform packages do the following statements apply more?";
##forced choice Reform 1 / Reform 2, no opt-out; exactly one package chosen in every pair):
##  choice_inequality = reduneq, "Contributes to the reduction of economic inequality."
##  choice_growth     = incgrow, "Contributes to the growth of the economy."
##There is no general preference question, so there is no plain `choice` column.
##Attribute text: respondents saw German; the deposit stores the authors' short English codes
##("Income - Top Increase"); these are mapped to the English level text of the article's Table 1
##("Increase for high incomes", "General increase", "No change", "General decrease", "Decrease for
##high incomes"; "large bequests" for inheritance, "large corporations" for corporate tax). Package
##features were "filled randomly"; no restrictions are stated. The order of the three tax rows was
##varied by participant but is not in the deposit (no attrpos_).
##Covariates: cov_left_right (0 left - 10 right), cov_income_percentile and cov_wealth_percentile (0-100,
##share of German households believed to be below the respondent), cov_firm_size (1 = 1-9, 2 = 10-99,
##3 = 100-999, 4 = 1,000+ employees). Dropped: the authors' recodes lr.r, high_inc, high_wealth,
##large_comp. The source id is a UUID-style respondent key; re-keyed to integers in file order.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "replication_data_jpp.csv"))
stopifnot(s[, .N, id][, all(N == 10)], s[, uniqueN(candidate_number), id][, all(V1 == 10)])
lev <- function(x, top) {
  y <- sub("^(Income|Inheritance|Corporate) - ", "", x)
  out <- c("General Increase" = "General increase", "General Decrease" = "General decrease", "No change" = "No change",
           "Top Increase" = paste("Increase for", top), "Top Decrease" = paste("Decrease for", top))[y]
  stopifnot(!anyNA(out)); unname(out)
}
ids <- unique(s$id)
d <- s[, .(id = match(id, ids), task = as.integer((candidate_number + 1L) %/% 2L), profile = as.integer(2L - candidate_number %% 2L),
           choice_inequality = as.integer(reduneq), choice_growth = as.integer(incgrow),
           attr_income_tax = lev(einkom, "high incomes"), attr_inheritance_tax = lev(erbsch, "large bequests"),
           attr_corporate_tax = lev(untern, "large corporations"),
           cov_left_right = lr, cov_income_percentile = hh_inc, cov_wealth_percentile = hh_wealth, cov_firm_size = size_organization)]
stopifnot(d[, .(a = sum(choice_inequality), b = sum(choice_growth)), .(id, task)][, all(a == 1 & b == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "becker_2025_tax_packages.csv"))
