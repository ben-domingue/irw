##Crowding discomfort in the Santiago Metro: stated-choice experiment, from the Zenodo deposit "Crowding perception
##survey in the Metro system, Santiago, Chile" (Tirachini).
##Article: Tirachini, A., Hurtubia, R., Dekker, T., & Daziano, R. A. (2017). Estimation of crowding discomfort in public
##transport: Results from Santiago de Chile. Transportation Research Part A, 103, 311-326, doi:10.1016/j.tra.2017.06.008
##(the deposit asks users to cite this paper).
##Deposit: doi:10.5281/zenodo.10663440 (concept doi 10.5281/zenodo.10663439), CC BY 4.0 (Zenodo record licence cc-by-4.0).
##Files read: crowdingData2014_final.xls, sheet "data guide" (the codebook) and sheet "data" (one row per respondent x task).
##Usage: Rscript tirachini_2017.R <dir holding the xls> <output dir>
##
##Sample: 413 distinct respondent IDs, Metro users in Santiago, 6 tasks each (2,478 rows). The data guide says ID runs
##"1 to 393" but the file has 413 (IDs 394-413 are all tablet-administered interviews, Tablet = 1); the extra 20 are kept
##and the mismatch is flagged: the article's N was not checked (paywalled). Each respondent saw one of two blocks of six
##tasks (Block1 = 1: tasks 1-6; 0: tasks 7-12; the file stores Task 1-6 within the block, trial_block) in one of three
##formats randomised between respondents (Type 1 = text, 2 = photo, 3 = diagram/plan; trial_crowding_format).
##Design: pivot design around the respondent's reported trip time (Ttorig, minutes in steps of 5), but the absolute travel
##times shown (TT1, TT2, minutes, 3.75-75) are stored per alternative, so they are used as the displayed levels.
##Each task: two metro alternatives (profile 1, 2), forced choice (Choice 1 or 2 = alternative chosen), no opt-out.
##Attributes (3): travel time (minutes, absolute, as stored), crowding level (CR1/CR2, codes 0-5, "crowding increasing in
##level; matches the 6 different descriptions" per the data guide), and standing (ST1/ST2, 1 = standing; 0 stored as
##"Seated", the complement; the article analyses sitting vs standing).
##LABELS: codes only for crowding. The six crowding descriptions (text; matching photos and diagrams) are in an
##accompanying Word file that is not in the deposit, and the article (paywalled) was not read; the crowding attribute is
##stored as "Crowding level k" with k the stored code 0-5 (increasing crowding per the data guide). Data guide also gives
##density (passengers per square metre, units not stated) recodes 0-0-1-2-4-6 for levels 1-6 of its 1-6 numbering.
##Missing choice (-9999): 11 tasks, dropped entirely (both profiles); no other missing.
##Covariates: cov_gender (GEN 1 = male, 0 = female, data guide), cov_age (EDAD, years, continuous), cov_education_code
##(EDU 1-6; the guide labels only 1 = no education, 2 = primary school, 6 = post graduate), cov_income_band_clp
##(ING household income band in pesos from the guide; -9999 -> NA), cov_car_owner (AUTO 1 = car owner).
##Dropped: IPAddress (PII FOUND, in the data sheet, masked/multiple per tablet), dates, status, trip details, smartphone
##items, the many survey-platform columns, crowding dummies and density recodes (derived), PSM scale, calibration items.
##Restrictions on combinations and level probabilities: not documented. No survey weight.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- suppressMessages(as.data.table(read_excel(file.path(raw, "crowd.xls"), sheet = "data", .name_repair = "unique_quiet")))
stopifnot(nrow(d) == 413 * 6, uniqueN(d$ID) == 413, d[, .N, ID][, all(N == 6)], all(d$Task %in% 1:6))
d <- d[Choice %in% 1:2]
stopifnot(nrow(d) == 413 * 6 - 11, all(d$CR1 %in% 0:5), all(d$CR2 %in% 0:5), all(d$ST1 %in% 0:1), all(d$ST2 %in% 0:1))
mk <- function(k) data.table(id = d$ID, task = as.integer(d$Task), profile = k, choice = as.integer(d$Choice == k),
  attr_travel_time = paste(d[[paste0("TT", k)]], "minutes"),
  attr_crowding_level = paste("Crowding level", d[[paste0("CR", k)]]),
  attr_standing = ifelse(d[[paste0("ST", k)]] == 1, "Standing", "Seated"),
  trial_crowding_format = c("Text", "Photo", "Diagram")[d$Type], trial_block = as.integer(d$Block1),
  cov_gender = ifelse(d$GEN == 1, "male", ifelse(d$GEN == 0, "female", NA)), cov_age = as.integer(d$EDAD),
  cov_education_code = as.integer(d$EDU),
  cov_income_band_clp = c("Less than 200,000", "200,000-400,000", "400,000-600,000", "600,000-800,000", "800,000-1,000,000", "1,000,000-1,500,000", "More than 1,500,000")[ifelse(d$ING %in% 1:7, d$ING, NA)],
  cov_car_owner = as.integer(d$AUTO))
o <- rbind(mk(1L), mk(2L))
setorder(o, id, task, profile)
stopifnot(o[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(o$attr_travel_time), o[, uniqueN(cov_age), id][, all(V1 == 1)])
dir.create(out, showWarnings = FALSE, recursive = TRUE)
fwrite(o, file.path(out, "tirachini_2017_metro_crowding.csv"))
