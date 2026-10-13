##Patterns of democracy and satisfaction with democracy: paired conjoint of political systems, France/Hungary/Italy
##Papp, Z., Navarro, J., Russo, F., & Nagy, L. E. (2024). Patterns of democracy and democratic
##satisfaction: Results from a comparative conjoint experiment. European Journal of Political
##Research, 63(4). https://doi.org/10.1111/1475-6765.12674
##Replication data: figshare doi:10.6084/m9.figshare.22316692, CC BY 4.0. Files read: Italy.dta,
##Hungary.dta, France.dta (value labels give the level text), REPLICATION CODE.do (read as text;
##variable list and attribute wording, lines 28-70).
##Usage: Rscript papp_2024.R <dir holding the three .dta> <output dir>
##
##Online panel samples, 826 (Italy), 808 (Hungary), 813 (France) respondents = 2,447; each saw 4 tasks of
##2 hypothetical countries described by 9 attributes (legislators engage in local matters, economy,
##electoral system proportionality, ballot structure, government ideology, coalition vs one-party,
##majority vs minority, corruption, party-system fragmentation). Forced choice, no opt-out.
##One table, cov_country: the authors fielded the identical experiment in three countries and
##estimate it per country and in common figures; the attribute text is identical across countries.
##Outcomes (the deposit has no questionnaire; wording from the journal abstract page):
##  choice = "On the whole, in which country would you say you would be more satisfied with the way
##           democracy works?" (country A or B).
##  rating = `scale`, a 0-10 satisfaction-with-democracy rating of each country (higher = more
##           satisfied). The deposit gives no wording; scale_A/scale_B hold the same value +1 on the
##           profile shown (99 on the other) and are dropped. Rating wording is a paraphrase.
##Attribute levels are the Stata value labels (they match the .do variable list); two label typos
##in the Italy/Hungary files are corrected ("Economiy growth", "Part lists only"). Randomization
##restrictions and attribute-order randomization are not documented. Respondent covariates:
##cov_gender (labels Male/Female -> male/female), cov_age (years as recorded), cov_education (value-label
##text, the three countries use their own category lists: France has 9 categories, Italy/Hungary 8;
##France "Masters of Equivalent" typo corrected),
##cov_lrscale (0 left - 10 right), cov_polint (0-10 political interest), cov_demsupport ("Democracy may have
##problems but it's better than any other form of government", 0-10 agree), cov_stfdem (satisfaction
##with democracy, 0 extremely dissatisfied - 10 extremely satisfied), cov_stflife (Hungary/Italy only).
##Dropped: the authors' derived variables (congruence, winner, *3 recodes, age5, edu3, group), the
##dummy attribute columns, income, household, vote intention, party (labels not documented as party id),
##temp. Panelist_id is re-keyed to integers within country.
##Respondent counts 826/808/813 are what the data hold; the paper's N could not be fetched.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
res <- list(); k0 <- 0L
for (cn in c("Italy", "Hungary", "France")) {
  x <- as.data.table(read_dta(file.path(raw, paste0(cn, ".dta"))))
  lab <- function(v) as.character(as_factor(x[[v]], levels = "labels"))
  d <- data.table(id = as.integer(factor(x$Panelist_id)) + k0, task = as.integer(x$Task_n), profile = as.integer(x$Profile_n),
                  choice = as.integer(x$choice), rating = as.integer(x$scale))
  k0 <- k0 + uniqueN(x$Panelist_id)
  for (v in c("legislators", "economy", "proportional", "ballot", "ideology", "coalition", "majority", "corruption", "fragmentation")) {
    d[, paste0("attr_", v) := lab(v)]
  }
  d[attr_economy == "Economiy growth", attr_economy := "Economic growth"]   # Italy label typo
  d[attr_ballot == "Part lists only", attr_ballot := "Party lists only"]    # Italy/Hungary label typo
  d[, cov_country := cn]
  d[, cov_gender := tolower(lab("gender"))]
  d[, cov_age := as.integer(x$age)]
  d[, cov_education := sub("^Masters of Equivalent$", "Masters or Equivalent", lab("education"))]
  for (v in c("lrscale", "polint", "demsupport", "stfdem")) d[, paste0("cov_", v) := as.integer(x[[v]])]
  d[, cov_stflife := if ("stflife" %in% names(x)) as.integer(x$stflife) else NA_integer_]
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], nrow(d) == 8 * uniqueN(d$id), !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
  res[[cn]] <- d
}
d <- rbindlist(res)
if (all(is.na(d$cov_stflife))) d[, cov_stflife := NULL]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "papp_2024_democracy_satisfaction.csv"))
