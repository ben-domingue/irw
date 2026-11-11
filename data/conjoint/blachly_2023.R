##Penobscot watershed (Maine) dam-removal choice experiment, from
##Blachly, B., Uchida, E., & Roy, S. G. (2023). Integrating public preferences with biophysical
##production possibilities: an application to ecosystem services from dam removal. Ecology and
##Society, 28(1), 51. https://doi.org/10.5751/ES-13739-280151 (OA, CC BY 4.0)
##Replication data: Harvard Dataverse doi:10.7910/DVN/4STVXI, CC0 1.0. Files read: full_data.csv;
##PenobscotCEanalysis.lim (NLOGIT command file, read as text). Article read for the design and the
##sample choice card (Fig. 2).
##Usage: Rscript blachly_2023.R <dir holding full_data.csv> <output dir>
##
##Mail survey of Penobscot-watershed addresses, Sept-Nov 2018. Each respondent faced 6 choices among
##the status quo ("No Action") and two hypothetical watershed-scale dam removal/upgrade plans (Plan A,
##Plan B), 6 attributes; efficient experimental design (Rose & Bliemer) in 4 versions (blocks).
##Columns: personid = respondent, choice_number = task, alt = profile (1 = Status Quo/No Action,
##2 = New Plan A, 3 = New Plan B, as on the card), choice = chosen.
##Outcome choice: "Which would you choose? check one box ONLY" (Fig. 2). The status quo is shown with
##its own levels, so it is a profile and there is no opt-out.
##SAMPLE: full_data.csv holds 401 respondents in two groups flagged by `lws`. The paper's sample is
##lws = 0 (the .lim file rejects lws = 1; 204 respondents, "1205 choices made by 204 respondents",
##Table 1). The lws = 1 group (197 respondents) has a different status quo (700 salmon, 50 thousand
##homes, 1 million herring) and different level ranges, and no source says who they are, so it is a
##different, undocumented design and is NOT built here.
##19 tasks of the lws = 0 respondents carry -999 in choice on all three alternatives (no answer) and
##are dropped, leaving 1,205 tasks as in the paper (the paper's "204 responses with all 6 choice
##questions completed" is thus slightly loose: 8 of the 204 have fewer than 6).
##LEVEL TEXT is the numbers in the deposit written in the format of the paper's sample card (Fig. 2):
##salmon "14,000 salmon" (number that can be supported by available habitat); likelihood "75%" (that
##salmon will utilize newly available habitat; the status quo shows "-"); hydropower "90 thousand
##homes" (number of homes powered; hydr = 90000); herring "5 million herring" (herr = 5); lake shoreline
##"300 miles lost"; cost "$400" (property tax surcharge, each year for 10 years). The card's small
##second lines ("25% chance of no change to salmon", "2300 remain") are derived from the first line
##and are not stored.
##Restrictions: fixed efficient design; the status quo is fixed (1,500 salmon, -, 155 thousand homes,
##2 million herring, 0 miles lost, $0). trial_version = design version 1-4.
##Dropped: survey_id (mailing id), all questionnaire items (a1a..c9h; no codebook deposited) and the
##authors' derived variables (s_*, dec, ev_*, u_*/l_*, demographic dummies). No covariates kept.
##personid is already 1..n. No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "full_data.csv"))
stopifnot(nrow(k) == 7218L, uniqueN(k$personid) == 401L)
k <- k[lws == 0L]
stopifnot(uniqueN(k$personid) == 204L)
k[, ans := all(choice %in% 0:1), .(personid, choice_number)]
stopifnot(k[ans == FALSE, all(choice == -999L)])
k <- k[ans == TRUE]
stopifnot(k[, sum(choice), .(personid, choice_number)][, all(V1 == 1L)], k[, .N, .(personid, choice_number)][, all(N == 3L)])
big <- function(x) formatC(x, format = "d", big.mark = ",")
d <- data.table(id = as.integer(k$personid), task = as.integer(k$choice_number), profile = as.integer(k$alt),
                choice = as.integer(k$choice))
stopifnot(k[alt == 1L, all(statquo == 1L & prob == 0L & salm == 1500L & cost == 0L)], k[alt != 1L, all(prob > 0L)])
d[, attr_salmon := paste(big(k$salm), "salmon")]
d[, attr_likelihood := fifelse(k$prob == 0L, "-", paste0(k$prob, "%"))]
stopifnot(all(k$hydr %% 1000L == 0L))
d[, attr_hydropower := paste(k$hydr %/% 1000L, "thousand homes")]
d[, attr_herring := paste(k$herr, "million herring")]
d[, attr_lake_shoreline := paste(k$lake, "miles lost")]
d[, attr_cost := paste0("$", k$cost)]
d[, trial_version := as.integer(k$version)]
stopifnot(d[, uniqueN(trial_version), id][, all(V1 == 1L)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "blachly_2023_dam_removal.csv"))
