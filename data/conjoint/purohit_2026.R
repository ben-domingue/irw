##Bureaucrat conjoint on village politicians (Telangana, India) from
##Purohit, B. (2026). Bureaucratic discretion against female politicians. Comparative Political
##Studies. Advance online publication. https://doi.org/10.1177/00104140261448427
##Replication data: Harvard Dataverse doi:10.7910/DVN/LEGBP2, CC0 1.0. File read:
##bdodata_conjoint_replication.tab (Dataverse "original format" download, a CSV). Wording from
##the deposit README and the authors' bdo_conjoint.R (read as text, not run); the article itself
##(paywalled) was not read.
##Usage: Rscript purohit_2026.R <dir holding bdodata_conjoint_replication.csv> <output dir>
##
##purohit_2026_bureaucrat_help: an ELITE sample. 221 Block Development Officers (BDOs/MPDOs,
##  sub-district bureaucrats in Telangana; the survey interviewed 253, the conjoint file holds
##  221), up to 4 tasks of 2 hypothetical sarpanch (village head) profiles: 206 respondents
##  have 4 tasks, 11 have 3, 4 have 2 (1,730 rows, as in the authors' Table D1). 4 attributes,
##  as labelled in the deposit (the README lists the same levels): gender (Male / Female),
##  reservation of the seat (UR / BC / SC, i.e. unreserved, Backward Class, Scheduled Caste),
##  education (5th grade / 12th grade), family background (Politics / Business / Social
##  Service). Whether the screen showed these short labels or longer text (and in English or
##  Telugu) is not documented in the deposit.
##  Outcome: choice = conjoint_work ("Sarpanch 1" / "Sarpanch 2") matched to the profile. The
##  README describes it as which sarpanch the bureaucrat "would be more likely to help" / "get
##  work done" for; the exact wording is in the article, not the deposit. Forced choice, no
##  opt-out (every task has an answer). task = round, profile = Candidate (1 = Sarpanch 1).
##  Attribute order and randomization restrictions not documented.
##  Covariate: cov_gender (respondent_gender, stored as text Male / Female -> male / female).
##  No survey weight in the deposit. The descriptive file
##  (bdodata_descriptive_replication) with age, birth state, education, caste and the years the
##  officer joined government and became BDO is NOT merged: in a population of a few hundred
##  named officials those together could identify people. Response.ID (Qualtrics) is replaced
##  by integers in file order.
##  Spot check: lm(choice ~ gender + education + family + reservation) reproduces Table D1
##  (GenderFemale -0.111, Education5th grade -0.143).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "bdodata_conjoint_replication.csv"))
stopifnot(nrow(s) == 1730, s[, .N, .(Response.ID, round)][, all(N == 2)], all(s$Candidate %in% 1:2),
          all(s$conjoint_work %in% c("Sarpanch 1", "Sarpanch 2")), all(s$respondent_gender %in% c("Male", "Female")))
s[, id := match(Response.ID, unique(Response.ID))]
d <- s[, .(id, task = as.integer(round), profile = as.integer(Candidate),
           choice = as.integer(conjoint_work == paste("Sarpanch", Candidate)),
           attr_gender = Gender, attr_reservation = Reservation, attr_education = Education,
           attr_family_background = Family.Background, cov_gender = tolower(respondent_gender))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(d$id) == 221)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "purohit_2026_bureaucrat_help.csv"))
