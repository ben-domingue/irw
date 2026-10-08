##Electoral-malfeasance candidate conjoint (Romania, 2016 local elections) from
##Mares, I., & Visconti, G. (2020). Voting for the lesser evil: Evidence from a conjoint
##experiment in Romania. Political Science Research and Methods, 8(2), 315-328.
##https://doi.org/10.1017/psrm.2019.12
##Replication data: Harvard Dataverse doi:10.7910/DVN/MJKCHZ, CC0 1.0, no restricted files.
##Files read: conjoint_Romania.dta and survey_Romania.dta (Dataverse "original format"
##downloads). Read as text, not run: 000_readme.txt, 001_conjoint_analysis.R,
##003_survey_analysis.R, 004_conjoint_diagnostics.R. Attribute text: the article's online
##appendix (Cambridge supplementary PDF S2049847019000128sup001.pdf), Table A1 "Full vignettes".
##The questionnaire is not deposited; the article itself was not accessible (paywalled).
##Usage: Rscript mares_2020.R <dir holding the two .dta files> <output dir>
##
##502 Romanian eligible voters (non-probability sample in 30 localities of 8 counties, survey
##"implemented in 2016" before the local elections), 5 pairs of hypothetical mayoral
##candidates, 7 attributes. 502 respondents / 5,020 profiles, as in appendix Table A3.
##task = pair, profile = candidate (recorded); the respondent id is the value label of idnum
##(= the survey file's idnum and the leading digits of `code`), re-keyed as is (1-502).
##Outcome: choice from `selected` (1 = candidate 1, 2 = candidate 2, 3 = neither). Code 3 is
##not documented, but the authors' outcome is 0 for both candidates in those 257 of 2,510
##tasks, so it is treated as an OPT-OUT (choice = 0 on both profiles). The question wording
##is not in any accessible source; the authors call the outcome "Electoral Choice" (appendix
##Table A3). selected matches the survey file's p1-p5 for every task.
##Attribute text: the file's short English labels (e.g. "100 RON") are replaced by the full
##English text of appendix Table A1. The survey language is not stated (fielded in Romania;
##only the English text survives). RESTRICTION (Table A1 fn 1): every pair has exactly one
##incumbent mayor and one candidate without experience as mayor, order within the pair
##randomized (checked: one incumbent per task). Other attributes: no rule or probabilities
##stated; attribute order not documented.
##Covariates: cov_gender (gender 1 = male, 2 = female per 003_survey_analysis.R comment),
##cov_age (years, as stored), cov_birth_year (survey file birthyear), cov_education (answer text
##from the 003_survey_analysis.R comment: 1 No school, 2 Primary, 3 Middle school, 4 Professional
##school, 5 High School, 6 Post-secondary school, 7 College and graduate school), cov_urban
##(1 = urban, 0 = rural, per the same file), cov_county (two-letter county code, survey file).
##No source labels ethnicity, income or party (codes incl. 99): kept as cov_ethnicity_code,
##cov_income_code, cov_party_code. Dropped: the authors' dummies (rural, female, male, romana,
##highschool, nohighschool, less900ron, more900ron, nopartisan, partisan, morethan45years,
##lessthan45years), corrupt (undocumented locality-level flag), ocupation (codes, no labels),
##locality (village names; quasi-identifying in small places). No survey weight. No task repeated.
##Spot check: lm(choice ~ attributes), SEs clustered by id, reproduces appendix Table A3
##(see return).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "conjoint_Romania.dta")))
v <- as.data.table(read_dta(file.path(raw, "survey_Romania.dta")))
s[, rid := as.integer(as.character(as_factor(idnum)))]
stopifnot(uniqueN(s$rid) == 502, s[, .N, rid][, all(N == 10)], s[, all(rid == code %/% 100)],
          s[, all((code %/% 10) %% 10 == pair & code %% 10 == candidate)],
          s[, uniqueN(selected), .(rid, pair)][, all(V1 == 1)], s[, sum(atexp == 2), .(rid, pair)][, all(V1 == 1)])
lab <- function(x) { y <- as.character(as_factor(x)); stopifnot(!anyNA(y)); y }
rc <- function(x, map) { y <- unname(map[x]); stopifnot(!anyNA(y)); y }
s <- merge(s, v[, .(rid = as.integer(idnum), birthyear, counties)], by = "rid", all.x = TRUE)
stopifnot(!anyNA(s$counties))
d <- s[, .(id = rid, task = as.integer(pair), profile = as.integer(candidate),
           choice = as.integer(selected == candidate),
           attr_gender = rc(lab(atgen), c(Male = "Male", Female = "Female")),
           attr_experience = rc(lab(atexp), c(
             Challenger = "The candidate does NOT have previous experience as mayor",
             Incumbent = "The candidate is currently serving as mayor")),
           attr_investigation = rc(lab(atinte), c(
             Clean = "Currently, there is NO legal action against the candidate on issues of political integrity",
             Investigated = "The candidate is currently being investigated by the General Anticorruption Agency",
             Sentenced = "The candidate was sentenced for previous acts of corruption by the courts")),
           attr_vote_buying = rc(lab(atmita), c(
             "No money offer" = "The candidate did NOT offer money or social assistance from the municipality in exchange for the vote",
             "100 RON" = "Candidate offered 100 RON in exchange for the vote",
             "Social assistance" = "Candidate offered social assistance from the municipality in exchange for the vote")),
           attr_threat = rc(lab(atinti), c(
             "No threat" = "During the campaign, the candidate has NOT threatened non-supporters with cutting their municipal social assistance benefits",
             "Threat to non-supporters" = "During the campaign, the candidate has threatened non-supporters with cutting their municipal social assistance benefits")),
           attr_public_policy = rc(lab(atpol), c(
             "No promises" = "The candidate has NOT made any promises to improve roads in the locality or to renovate school buildings",
             "Renovate schools" = "During the campaign, the candidate pledged to renovate schools buildings in the locality",
             "Renovate schools and roads" = "During the campaign, the candidate pledged to improve roads and renovate school buildings in the locality")),
           attr_income = rc(lab(atven), c(
             "No high income" = "Candidate does NOT have a high income and lives from their own salary",
             "High income" = "The candidate has a high income that originates in a business that they manage")),
           cov_gender = rc(as.character(gender), c("1" = "male", "2" = "female")),
           cov_age = as.integer(age), cov_birth_year = as.integer(birthyear),
           cov_education = rc(as.character(education), c("1" = "No school", "2" = "Primary", "3" = "Middle school",
             "4" = "Professional school", "5" = "High School", "6" = "Post-secondary school", "7" = "College and graduate school")),
           cov_urban = as.integer(urban), cov_county = as.character(counties),
           cov_ethnicity_code = as.integer(ethnicity), cov_income_code = as.integer(income), cov_party_code = as.integer(party))]
stopifnot(identical(d$choice, as.integer(s$outcome)), d[, sum(choice), .(id, task)][, all(V1 <= 1)],
          d[, sum(choice), .(id, task)][, sum(V1 == 0)] == 257)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mares_2020_lesser_evil.csv"))
