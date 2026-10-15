##Breast cancer risk prediction service discrete choice experiment (BCAN-RAY) from
##Wright, S. (2025). BCAN-RAY DCE cleaned data for analysis [Data set]. figshare. (no journal article identified in
##the deposit) Data: figshare doi:10.6084/m9.figshare.29597330 (v1, 2025), CC BY 4.0 (figshare API).
##Files read: "BCAN-RAY cleaned DCE data.RDS" (the analysed sample, wide: one row per respondent x task) and, for the
##displayed card wording only, the two header rows (question text) of the twin deposit's raw Qualtrics export
##"BCAN-RAY raw DCE data.csv" (doi:10.6084/m9.figshare.29597318, same author, CC BY 4.0). Usage:
##  Rscript wright_2025.R <dir holding the RDS and raw.csv or the csv> <output dir>
##
##936 women (Prolific-style online sample; the file carries 'ppid' and 'ResponseId', both dropped) who completed a
##10-task DCE: "If you had to choose between the following breast cancer risk prediction services, which would you
##choose? You can also choose not to receive breast cancer risk prediction." Each task: Risk Prediction 1, Risk
##Prediction 2 and "No Risk Prediction" (fixed text: "You would not have your risk of breast cancer predicted /
##You would be invited to breast cancer screening at age 50 / If you were worried about cancer before this, you would
##visit your GP"): no attributes, so an opt-out (opt_out = yes, chosen in 13% of tasks; choice = 0 on both profiles).
##Attributes (displayed card rows): How Risk is Predicted (6 levels, e.g. Questionnaire / Questionnaire and genetic
##test / ... radiofrequency scan ...), How Many Appointments are Needed (One/Two), Location of Appointment (Home,
##Hospital, Your GP, Community Centre, Mobile Van), Possible Times for Appointment (Weekdays only / Weekdays, Evenings
##and Weekends), How Appointments are Booked (Receive a letter with a fixed time / Book a time yourself online or on
##the phone), and "The likelihood you would be estimated to be at high risk" (stored 5/10/15/20; the unit is not
##given in the files, presumably per cent: kept as the stored number).
##Fixed blocked design: 3 versions (trial_version) x 10 tasks. The card text of each version and task is read from the
##raw export's question-text header (column (version-1)*10 + task of the 30 'Q#_1' columns); it agrees with the RDS
##columns for method, appointments and location in all but wording (RDS 'genetic scan' = card 'genetic test' in one
##card; Oxford comma). DISCREPANCY (decide): the RDS's +/-1 codes for times and howapp disagree with the displayed
##card text on 9 cards for times (version 2 tasks 1,2,8,9,10; version 3 tasks 1,3,7,9) and 1
##card for howapp (version 2 task 6); the table follows the displayed text, so the authors' coded design and this
##table differ on those cards. Profile = Risk Prediction 1/2; task = the RDS task (recorded).
##Outcome: choice (1 = Risk Prediction 1, 2 = Risk Prediction 2, 3 = none).
##Covariates: cov_age (years, 18-100 plausible), cov_sex_code (Q8 'What is your sex?', codes undocumented: 1/2).
##Dropped: ppid, ResponseId, start/end dates, durations, all other questionnaire columns, design-derived coded
##columns. Respondent key = the RDS id (1..936). N: 936 respondents (935 distinct ppid values: one Prolific id
##appears twice); the paper is not identified, so N is not compared.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(list.files(raw, pattern = "[.]RDS$", ignore.case = TRUE, full.names = TRUE)[1]))
csv <- list.files(raw, pattern = "[.]csv$", full.names = TRUE)[1]
h <- fread(csv, header = FALSE, nrows = 3, sep = ",", quote = "\"", fill = TRUE)
tx <- unlist(h[2, 18:47]); stopifnot(length(tx) == 30, all(grepl("breast cancer risk prediction services", tx)))
parse1 <- function(s) {
  l <- trimws(strsplit(s, "\n")[[1]]); l <- l[l != ""]
  get <- function(hd) { i <- which(l == hd); stopifnot(length(i) == 1); l[i + 1:2] }
  data.table(profile = 1:2, attr_method = get("How Risk is Predicted"), attr_appointments = get("How Many Appointments are Needed"),
    attr_location = get("Location of Appointment"), attr_times = get("Possible Times for Appointment"), attr_booking = get("How Appointments are Booked"))
}
cards <- rbindlist(lapply(1:3, function(v) rbindlist(lapply(1:10, function(t) cbind(version = v, task = t, parse1(tx[(v - 1) * 10 + t]))))))
stopifnot(nrow(x) == 9360, uniqueN(x$id) == 936, x[, .N, id][, all(N == 10)], x[, uniqueN(version), id][, all(V1 == 1)], x[, all(choice %in% 1:3)])
norm <- function(s) gsub(",? and genetic", " and genetic", gsub("genetic scan", "genetic test", gsub(", and ", " and ", s)))
L <- rbindlist(lapply(1:2, function(p) x[, .(id, version, task, profile = p, choice = as.integer(choice == p), method = get(paste0("method.", p)),
  noapp = c("One", "Two")[get(paste0("noapp.", p))], loc = get(paste0("location.", p)), hr = get(paste0("highrisk.", p)),
  cov_age = ifelse(age >= 18 & age <= 100, as.integer(age), NA_integer_), cov_sex_code = as.integer(Q8))]))
d <- merge(L, cards, by = c("version", "task", "profile"))
stopifnot(nrow(d) == 18720, d[, all(norm(method) == norm(attr_method))], d[, all(noapp == attr_appointments)], d[, all(loc == attr_location)])
d[, `:=`(attr_high_risk_likelihood = as.character(hr), trial_version = version)]
d <- d[, .(id, task = as.integer(task), profile, choice, attr_method, attr_appointments, attr_location, attr_times, attr_booking,
  attr_high_risk_likelihood, cov_age, cov_sex_code, trial_version)]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, sum(choice), .(id, task)][, all(V1 <= 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wright_2025_breast_risk_prediction.csv"))
