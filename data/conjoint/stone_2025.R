##Trial-court judge profile experiments (two NORC AmeriSpeak surveys, 2021 and 2023) from
##Stone, A. R., & Olson, M. P. (2025). Elections improve support for state trial court judges
##in the United States. Journal of Law and Courts. https://doi.org/10.1017/jlc.2024.14
##Replication data: Harvard Dataverse doi:10.7910/DVN/MU3Z7A, CC0 1.0, no restricted files, no terms.
##Files read: weidenbaum_survey_2021.RData, weidenbaum_survey_2023.RData, README.txt (variable
##codebook); survey_analysis_2021.R / survey_analysis_2023.R read as text, not run. Level text:
##article Table 1 ("Characteristics of Hypothetical Trial Court Judges and Contexts").
##Usage: Rscript stone_2025.R <raw dir> <output dir>
##
##Each respondent saw ONE hypothetical judge profile (task = 1, profile = 1) with seven attributes,
##"one value from each attribute was randomly assigned" (article, Table 1 note); the order of the
##attributes was randomized (article; not recorded in the deposit, so no attrpos_ columns),
##except that the method of selection always preceded the vote received. Two tables, one per
##fielding (Study One: 1,033 adults, July-Aug 2021; Study Two: 1,224 adults, July 2023), which
##the authors analyse separately; same attributes and levels.
##Codes -> Table 1 text (README codebook gives the code meanings):
##  judge_name 1 James Young, 2 Janet Young; judge_race 1 Black, 2 White, 3 Hispanic;
##  judge_tenure 1/2/3 One year/Five years/Fifteen years; judge_party 1 Republican, 2 Democrat,
##  3 "No partisan information provided" (Table 1's text; whether the row was shown blank or
##  omitted is not documented); judge_sentencing 1/2/3 = an average of 3/6/9 years in prison for
##  burglary ("A typical sentence length for this crime is 6 years"), stored as "3 years" etc.;
##  election_treatment 1 Partisan election, 2 Nonpartisan election, 3 Appointed;
##  judge_margin 1/2/3 = 52/60/80 percent ("Vote received (in last election or in confirmation vote)").
##Outcomes (wording not deposited; README + article give the scales):
##  rating           = judge_support, support for this judge, 1-5, strongly oppose .. strongly support.
##  rating_fairness  = fairness_accused_crime (2021 only), judge's fairness, 1-5, very unfair .. very fair.
##The four state-court legitimacy items (2021) are about the state courts, not the profile, and are
##deposited already reversed/rescaled, so they are not kept; nor are the 2023 efficacy/mechanism
##items or the derived distances. 2021: 71 respondents have no treatment and no outcome (omitted),
##leaving 962; 2023: 52 without judge_support omitted, leaving 1,172.
##Covariates: cov_gender (GENDER value labels 1 Male, 2 Female, 0 Unknown -> NA), cov_race
##(RACETHNICITY value-label text), cov_party_id (respondent_pid / Party: Democrat, Independent,
##Republican, with leaners coded as partisans per README), cov_education (EDUC5 value-label text),
##cov_income4 (INCOME4 value-label text), cov_income (INCOME, 1-18 codes, meanings in README),
##cov_ideology (IDEO 1-5, very liberal .. very conservative, README), cov_married, cov_employed,
##cov_internet (source 0/1), cov_knowledge (Knowledge Level text), cov_state. Dropped: derived
##dummies (black, hispanic, college, democrat, republican), elected_any_court (from state), and the
##binary election indicator. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x) { l <- attr(x, "labels"); as.character(names(l)[match(as.numeric(x), l)]) }
build <- function(f, partyvar, fair) {
  e <- new.env(); load(file.path(raw, f), envir = e); s <- get(ls(e)[1], e)
  for (v in c("RACETHNICITY", "EDUC5", "INCOME4")) s[[v]] <- lab(s[[v]])
  s <- s[!is.na(s$judge_support), ]
  stopifnot(!anyNA(s$judge_name), !anyNA(s$judge_sentencing))
  cd <- function(v) as.integer(as.character(s[[v]]))
  d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L, rating = as.integer(s$judge_support))
  if (fair) d[, rating_fairness := as.integer(s$fairness_accused_crime)]
  d[, attr_name := c("James Young", "Janet Young")[cd("judge_name")]]
  d[, attr_race := c("Black", "White", "Hispanic")[cd("judge_race")]]
  d[, attr_tenure := c("One year", "Five years", "Fifteen years")[cd("judge_tenure")]]
  d[, attr_partisanship := c("Republican", "Democrat", "No partisan information provided")[cd("judge_party")]]
  d[, attr_sentencing := c("3 years", "6 years", "9 years")[cd("judge_sentencing")]]
  d[, attr_selection := c("Partisan election", "Nonpartisan election", "Appointed")[cd("election_treatment")]]
  d[, attr_vote_received := c("52 percent", "60 percent", "80 percent")[cd("judge_margin")]]
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
  g <- as.numeric(s$GENDER); stopifnot(all(g %in% 0:2))
  d[, cov_gender := c(NA, "male", "female")[g + 1]]
  d[, cov_race := s$RACETHNICITY]
  d[, cov_party_id := as.character(s[[partyvar]])]
  d[, cov_education := s$EDUC5]
  d[, cov_income4 := s$INCOME4]
  d[, cov_income := as.integer(s$INCOME)]
  d[, cov_ideology := as.integer(s$IDEO)]
  d[, cov_married := as.integer(s$married)][, cov_employed := as.integer(s$employed)]
  d[, cov_internet := as.integer(s$INTERNET)]
  d[, cov_knowledge := as.character(s[["Knowledge Level"]])]
  d[, cov_state := s$STATE]
  stopifnot(!anyNA(d$cov_race), !anyNA(d$cov_education), !anyNA(d$cov_income4))
  setorder(d, id, task, profile); d
}
d21 <- build("weidenbaum_survey_2021.RData", "respondent_pid", TRUE)
d23 <- build("weidenbaum_survey_2023.RData", "Party", FALSE)
stopifnot(nrow(d21) == 962, nrow(d23) == 1172)
fwrite(d21, file.path(out, "stone_2025_judge_selection_2021.csv"))
fwrite(d23, file.path(out, "stone_2025_judge_selection_2023.csv"))
