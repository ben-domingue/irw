##Policy-collaboration conjoint with US local government officials, from
##Liu, Y. (2024). Partisan collaboration in policy adoption: An experimental study with local
##government officials. Policy Studies Journal, 52(4), 955-967. https://doi.org/10.1111/psj.12551
##Replication data: Harvard Dataverse doi:10.7910/DVN/CJKC4D, CC0 1.0, no restricted files, no terms.
##File read: conjoint.tab (Dataverse "original format" download; long, one row per profile).
##Read as text only: PartisanCollaboration_PSJ.R and Descriptive_PSJ.R (authors' analysis code).
##No codebook or questionnaire ships and the article full text was not reachable (Wiley 403), so
##the outcome wording below is a paraphrase from the article abstract.
##Usage: Rscript liu_2024.R <raw dir> <output dir>
##
##772 municipal officials (IndID), up to 3 pairs of hypothetical collaborative policy programs,
##4 attributes. Task = source PairID (1-3 within respondent, recorded); profile = source
##`Profile` (1/2, recorded). 729 respondents have all 3 pairs; 43 lack one or two (e.g. pairs 1
##and 3 only: the unanswered pair is absent from the deposit, task numbers kept); 2,267 pairs,
##4,534 profile rows.
##Outcome: choice (source `choice`), the official's pick of the program to adopt of the two
##(paraphrase of "likelihood of local policymakers adopting a program"); every pair has exactly
##one chosen profile, so no opt-out.
##Attributes, stored as the text in the data, which is the author's short labels (the displayed
##wording is not in the deposit): resource ("Self vs Partner's Input" in the authors' code:
##250:750 / 500:500 / 750:250), outcome ("Job Creation": 200 Jobs / 500 Jobs / 800 Jobs),
##partisanship (the program's proposer, "Program Proposed By": Democrats / Republicans; the
##authors' "Same Party" attribute is derived from this x respondent party and is not kept),
##trust ("Collaborative Experiences": Bad / Good / No Experience). Restrictions, level weights
##and attribute order are not documented; all 9 resource x outcome cells occur.
##Covariates (from conjoint.tab, constant within respondent): cov_party_id_code (party: the
##authors' code reads 1 = Democrat, 2 = Republican, other = "Other"; 3 vs 4 undocumented, so
##codes kept), cov_ideology (ideo, text from the authors' code: 1 Very Liberal .. 5 Very
##Conservative), cov_race (race: Descriptive_PSJ.R L146-150, 1 White, 2 Black, 3 Hispanic,
##4 Asian, 5 Other), cov_gender_code (gender: the authors' code reads only 2 = Female; 1, 3, 4
##undocumented, so codes kept), cov_age (years), cov_education_code and cov_tenure_code (codes,
##no labels in the deposit; the authors treat educ > 5 as graduate degree and tenure > 2 as
##more than 5 years), cov_elected (1 = "Elected", else "Appointed", authors' code).
##DROPPED: city, county, state and the city's census figures (pop1000, income1000, home1000,
##labor, unemployment, white, black): together with the official's age, sex and race they
##identify a named public official. respondents.tab (also holds city names) is not read; its
##id does not link to IndID.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conjoint.tab"))
stopifnot(nrow(s) == 4534L, uniqueN(s$IndID) == 772L, s[, .N, .(IndID, PairID)][, all(N == 2)], all(s$PairID %in% 1:3))
s[, task := PairID]
lab <- function(x, v) { y <- v[as.character(x)]; unname(y) }
d <- s[, .(id = as.integer(IndID), task = as.integer(task), profile = as.integer(Profile), choice = as.integer(choice),
           attr_resource = resource, attr_outcome = outcome, attr_partisanship = partisanship, attr_trust = trust,
           cov_party_id_code = as.integer(party),
           cov_ideology = lab(ideo, c(`1` = "Very Liberal", `2` = "Liberal", `3` = "Moderate", `4` = "Conservative", `5` = "Very Conservative")),
           cov_race = lab(race, c(`1` = "White", `2` = "Black", `3` = "Hispanic", `4` = "Asian", `5` = "Other")),
           cov_gender_code = as.integer(gender), cov_age = as.integer(age),
           cov_education_code = as.integer(educ), cov_tenure_code = as.integer(tenure),
           cov_elected = fifelse(elected == 1L, "Elected", "Appointed"))]
stopifnot(all(s$ideo %in% 1:5), all(s$race %in% c(1:5, NA)), all(!is.na(s$elected)))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, max(task)] == 3L)
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "liu_2024_partisan_collaboration.csv"))
