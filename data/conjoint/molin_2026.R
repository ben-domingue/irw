##Is vacation destination a positional good? context-dependent stated choice, from
##Molin, E., Quesada, J., Yoo, S., & van Wee, B. (2026). Is vacation destination a positional good? European Journal of
##Transport and Infrastructure Research, 26(3). https://doi.org/10.59490/ejtir.2026.26.3.8137
##Data: 4TU.ResearchData doi:10.4121/81910815-0b19-4304-872d-6c31255c8e61.v1 (Molin, 2026), CC0.
##Files read: "destination positionality.sav" (SPSS value labels), README.txt, "codebook vacation positionality.pdf".
##The article page was not reachable (DOI not yet resolving), so the question wording is the deposit description's paraphrase.
##Usage: Rscript molin_2026.R <dir holding "destination positionality.sav"> <output dir>
##
##Online sample recruited mainly from a student's network, Nov 2020 (205 responded, 159 complete = the 159 here: 79
##choosing for themselves, 80 choosing for a family member, trial_choosing_for). Before the experiment each respondent
##ranked five destinations (Western Europe, Eastern Europe, South America, Oceania, East Asia). Each respondent then
##answered 18 choice sets (fixed design, all 18 present for everyone), each of two hypothetical vacation alternatives
##(profile = ALTERNATIVE 1/2), described by destination, travel cost and door-to-door travel time, given a context: the
##rank of the destination chosen by relevant others (friends). Forced choice between the two, no opt-out.
##Outcome (choice): choose between the two vacation alternatives (paraphrase of the deposit description; for the
##"family member" half, choosing for a family member).
##Attributes: attr_destination_rank: the deposit stores the destination as the position of that destination in the
##respondent's OWN ranking (DR, reverse coded: 5 = most attractive, 1 = least attractive; only ranks 1, 3, 5 are used). The
##screens named the region (e.g. Western Europe), but the region is not stored and the respondent's ranking is not in the
##file, so the level is stored as the displayed meaning "Own rank k of 5" (LABELS: rank-coded). attr_travel_cost
##"1000|1500|2000 Euro" (codebook), attr_travel_time "k hours" (door to door; the levels differ by destination rank, e.g.
##2/3/4 hours for rank 5, 6/9/12 for rank 3, 6/9/10/12/15/20 for rank 1, as in the data).
##trial_others_destination_rank = DRO, the context (same in both alternatives of a set): "Own rank k of 5" for the
##destination chosen by others, k = 2, 3, 4. trial_choosing_for from VERSION (README: 1 own choice, 2 choice for family member).
##Restrictions: travel time levels depend on the destination (see above); otherwise none documented. Level weights: unknown.
##Covariates: cov_age (years), cov_gender (1 Male, 2 Female; the 3 = "Missing Value" of 5 respondents is NA),
##cov_income (SPSS value labels: yearly net household income band text; the PDF codebook repeats a typo for code 5).
##Task = CHOICESET (recorded; display order not stated). Respondent id = ID (already 1..159). Dropped: RD, DRxRD (derived).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_sav(file.path(raw, "destination positionality.sav")))
stopifnot(nrow(x) == 5724, uniqueN(x$ID) == 159, x[, .N, ID][, all(N == 36)], x$DR %in% c(1, 3, 5), x$DRO %in% 2:4)
inc <- attr(x$INCOME, "labels"); inc <- setNames(names(inc), inc)
rk <- function(k) paste0("Own rank ", k, " of 5", ifelse(k == 5, " (most attractive)", ifelse(k == 1, " (least attractive)", "")))
d <- x[, .(id = as.integer(ID), task = as.integer(CHOICESET), profile = as.integer(ALTERNATIVE), choice = as.integer(CHOICE),
  attr_destination_rank = rk(DR), attr_travel_cost = paste(COST, "Euro"), attr_travel_time = paste(TIME, "hours"),
  cov_age = as.integer(AGE), cov_gender = c("male", "female", NA)[as.integer(GENDER)],
  cov_income = unname(inc[as.character(as.integer(INCOME))]),
  trial_others_destination_rank = paste0("Own rank ", DRO, " of 5"),
  trial_choosing_for = ifelse(as.integer(VERSION) == 1, "own choice", "family member"))]
stopifnot(!anyNA(d[, .(attr_destination_rank, attr_travel_cost, attr_travel_time)]), d[, sum(choice), .(id, task)][, all(V1 == 1)],
  d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "molin_2026_vacation_positional.csv"))
