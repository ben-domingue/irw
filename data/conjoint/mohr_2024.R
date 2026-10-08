##Museum visit conjoint (Charlotte, NC) from
##Mohr, Z., Olivares, A., & Piatak, J. (2024). Are public spaces welcoming to all? A conjoint
##experiment on cultural representation and inclusionary practices in museums. Public
##Administration, 102(3), 841-859. https://doi.org/10.1111/padm.12953
##Replication data: Harvard Dataverse doi:10.7910/DVN/IPRSTZ, CC0 1.0. File read:
##final data for analysis.dta (Dataverse "original format" download). Read as text:
##analysis_final.do. No codebook or questionnaire ships; the article (CC BY-NC-ND, Wiley)
##could not be retrieved, so attribute and question wording come only from the Stata labels.
##Usage: Rscript mohr_2024.R <dir holding final.dta> <output dir>
##(the script expects the .dta saved as final.dta)
##
##386 respondents, 6 pairs of hypothetical art-museum visits ("Museum A" / "Museum B"),
##6 attributes: artist (Dale Chihuly / Romare Bearden), exhibition description
##("Juxtaposing" / "Black men"), event (Art History Lecture / Artist Festival), program
##(Cultural Dance Night / Public Tour), cost ($7-$17 in $2 steps), location
##(Uptown/Downtown / Outside center city). These are the Stata value labels, i.e. the
##authors' SHORT labels; the description levels in particular were surely longer on screen.
##The cost labels in the .dta are mis-attached (labels 1-6 vs stored values 7-17); the
##stored dollar amount is used ("$" + value).
##task = source `choice` (1-6), profile = source `Profile` (1 = _a_ = Museum A, 2 = _b_).
##Outcome: choice = source `selected` (y_ = 1 Museum A / 2 Museum B); forced choice between
##two museums, exact question wording not deposited. One task (one respondent) has no answer
##(y_ missing, selected 0 on both) and is dropped: 2,315 tasks.
##Randomization restrictions are not documented; level shares look uniform.
##Covariates (source codes, Stata labels): cov_gender (Q19_OPS: 1 Male, 2 Female, 3 Other),
##cov_party (Q24_OPS: 1 Democrat, 2 Republican, 3 Independent, 4 Other), cov_race (race5cat:
##1 White, 2 Black, 3 Hispanic, 4 Asian, 9 Other), cov_generation (age3: 1 Gen X,
##2 Millenial, 3 Gen Z; the only labelled age measure, age4 is unlabelled), cov_visited_mint
##(Q101: 1 Uptown, 2 Randolph, 3 both, 4 neither), cov_museum_last12m (visit_any: 1 Yes, 2 No,
##the only stored version of Q206). Dropped: consent item Q4_OPS, row ids id2, y_, the
##recode `visit`, age4, and the redundant `profile` string.
##N: the article's sample size could not be checked (article not reachable).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "final.dta")))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
d <- s[, .(id = as.integer(id), task = as.integer(choice), profile = as.integer(Profile),
           choice = as.integer(selected), y = as.integer(zap_labels(y_)),
           attr_artist = lab(artist), attr_description = lab(description), attr_event = lab(events),
           attr_program = lab(programs), attr_cost = paste0("$", as.integer(zap_labels(cost))),
           attr_location = lab(location),
           cov_gender = as.integer(zap_labels(Q19_OPS)), cov_party = as.integer(zap_labels(Q24_OPS)),
           cov_race = as.integer(zap_labels(race5cat)), cov_generation = as.integer(zap_labels(age3)),
           cov_visited_mint = as.integer(zap_labels(Q101)), cov_museum_last12m = as.integer(zap_labels(visit_any)))]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], uniqueN(d$id) == 386)
d <- d[!is.na(y)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[choice == 1, all(y == profile)])
d[, y := NULL]
stopifnot(nrow(d) == 4630, !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mohr_2024_museum_visits.csv"))
