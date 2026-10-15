##COVID-19 infection risk and train route choice, Netherlands, from
##Shelat, S., van de Wiel, T., Molin, E., van Lint, J. W. C., & Cats, O. (2022). Analysing the impact of COVID-19 risk
##perceptions on route choice behaviour in train networks. PLOS ONE, 17(3), e0264805. https://doi.org/10.1371/journal.pone.0264805
##Data: 4TU.ResearchData doi:10.4121/16896913.v1 (van de Wiel et al., 2021), CC BY-NC-SA 4.0 (4TU record licence).
##Files read: choice_data_for_upload.xlsx (sheets long_trip_choices, short_trip_choices) and readme.md. The stage-1 risk
##rating file (regression_data_for_upload.sav) is a rating experiment on a different attribute set and was not used.
##Level text and wording from the MSc thesis (van de Wiel 2021, repository.tudelft.nl uuid:ad83794c-fc52-41c3-8a27-276187c5b81e):
##Table 3.3 and Figure 3.6 (survey screen, translated into English); the deposit stores numbers only.
##Usage: Rscript shelat_2022.R <dir holding choice_data_for_upload.xlsx> <output dir>
##
##Online survey of Dutch train travellers (quota sample, 2020-21); 408 valid respondents in the paper = 291 (long-trip
##experiment) + 117 (short-trip experiment) here. Respondents usually travelling < 30 min saw the short-trip experiment,
##others the long-trip one. The two experiments share attributes but have different time and cost levels and different
##D-efficient designs, and the authors estimate them separately: TWO TABLES (shelat_2022_covid_train_long / _short).
##Each respondent: 9 choice sets (A..I, fixed D-efficient design, 9 sets per version) of two train trips (Trip 1, Trip 2).
##Sequential opt-out: respondents first pick one trip (forced), then are asked "If offered the choice, would you choose to
##perform the just selected train trip?" (yes/no). The file's Choice codes are 1 = trip 1, 2 = trip 2, and 0, 3, 4 =
##opted out (the three opt-out scenarios of the thesis, other mode / from home / cancel, were asked at the end; which
##code is which is NOT documented, so the code is kept as trial_optout_code). Checked: sets A, C, E of the long file
##(risk 5 on both trips) have 80.6% codes 0/3/4, as the thesis reports (about 80% opt-out). Opt-out has no
##attributes: opt_out = yes, choice = 0 on both profiles. Which trip an opting-out respondent picked first is not stored.
##Outcome (choice): "Please choose the train trip you prefer, based on the price, travel time and your estimation with
##regards to the coronavirus infection risk" plus the opt-out question above (Fig 3.6).
##Attributes (displayed text): price "€3|4.5|6" (short) / "€9|12|15" (long) (euro sign, as in Fig 3.6);
##travel time "10|17|24 minutes" / "35|45|55 minutes"; infection risk ("Your infection risk estimation"): "Very low (1 out
##of 5)" / "Not low, nor high (3 out of 5)" / "Very high (5 out of 5)" (the first two read off Fig 3.6; the third is
##INFERRED by symmetry). The risk level is the respondent's own earlier rating scale, but the level shown is fixed by the design.
##Task = set letter A..I as 1..9 (the thesis says question order was randomized; the position shown is not recorded: INFERRED
##from the set letter, task_source = inferred). Profile 1 = Trip 1 (column _A), profile 2 = Trip 2 (_B).
##Restrictions: all time-cost combinations exist in reality (thesis); no prohibited pairs documented. Level weights: efficient design (unknown).
##Id is the authors' respondent number, unique within each sheet; the same numbers 1..N are used in both sheets, so ids are
##re-keyed 1..291 (long) and 1..117 (short) per table. Eight respondents per sheet have 8 of 9 sets (one set is missing in the file):
##their 9th set is simply absent.
##Covariates kept: cov_age (years). Dropped: Education, Student, TrainUseFrequencyDuringCovid (effects-coded -1/1 derived
##variables with no recoverable category text).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "choice_data_for_upload.xlsx")
risk <- c("1" = "Very low (1 out of 5)", "3" = "Not low, nor high (3 out of 5)", "5" = "Very high (5 out of 5)")
build <- function(sheet, nresp, nrow_) {
  x <- as.data.table(read_excel(f, sheet = sheet))
  stopifnot(nrow(x) == nrow_, uniqueN(x$Id) == nresp, x$Choice %in% 0:4, !anyNA(x))
  x[, id := match(Id, sort(unique(Id)))]
  x[, task := match(Set, LETTERS[1:9])]
  stopifnot(!anyNA(x$task), !anyDuplicated(x[, .(id, task)]))
  one <- function(p) {
    data.table(id = x$id, task = x$task, profile = p, choice = as.integer(x$Choice == p),
      attr_price = paste0("€", x[[paste0("TravelCost_", c("A", "B")[p])]]),
      attr_travel_time = paste(x[[paste0("TravelTime_", c("A", "B")[p])]], "minutes"),
      attr_infection_risk = unname(risk[as.character(x[[paste0("CovidRisk_", c("A", "B")[p])]])]),
      cov_age = as.integer(x$Age),
      trial_optout_code = ifelse(x$Choice %in% c(0, 3, 4), as.integer(x$Choice), NA_integer_))
  }
  d <- rbind(one(1), one(2))
  stopifnot(!anyNA(d[, .(attr_price, attr_travel_time, attr_infection_risk)]), d[, sum(choice), .(id, task)][, all(V1 <= 1)])
  setorder(d, id, task, profile); d
}
fwrite(build("long_trip_choices", 291, 2612), file.path(out, "shelat_2022_covid_train_long.csv"))
fwrite(build("short_trip_choices", 117, 1045), file.path(out, "shelat_2022_covid_train_short.csv"))
