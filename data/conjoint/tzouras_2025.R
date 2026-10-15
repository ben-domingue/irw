##First/last mile mode choice and perceived safety in Athens and Munich: image-based double stated-preference experiment,
##from the Zenodo deposit "Perceived safety and first/last mile mode choices. A dataset from image-based double stated
##preferences experiments" (Tzouras, v2.0).
##Article: Tzouras, P. G. et al. (2024/25), Transportation, doi:10.1007/s11116-024-10487-4 (Zenodo relation "isDescribedBy";
##authors beyond the depositor and the article's N were not checked).
##Deposit: doi:10.5281/zenodo.17779261 (version 2.0; concept doi 10.5281/zenodo.14967129), CC BY 4.0 (record licence cc-by-4.0).
##Files read: choice_dataset_perceivedSafetyChoices_v2.0.csv (the table's rows), README_perceivedSafetyChoices_v2.0.rtf (read
##as text), rating_dataset_perceivedSafetyChoices_v2.0.csv (ONLY the respondent covariates, joined by pid).
##Usage: Rscript tzouras_2025.R <dir holding the csv files> <output dir>
##
##Sample: 173 respondents in the choice file (Athens and Munich, the latter added in v2.0; pid 101-1317; the deposit says 129 + 50),
##2,059 choice rows (up to 12 scenarios each; 166 respondents have 12, 6 have 11, 1 has 1). The deposit describes 2,060
##choices; the file holds 2,059.
##Design (deposit description): in each image scenario of an imaginary road environment respondents first rated how safe they
##would feel to drive a car / ride an e-bike / ride an e-scooter / walk (1 = very unsafe ... 7 = very safe), then answered
##"Your daily route consists of urban roads with traffic conditions like above. Which transport mode would you select, if you
##were aware of the travel time and cost?" The four modes are the labelled alternatives (profile 1-4 = car, e-bike,
##e-scooter, walk, a fixed order here, NOT a recorded screen position: profile_source inferred). A task is one row of the
##choice file in file order (task_source inferred; the file has no scenario index, rows appear in scenario order because
##the four *psafe columns reproduce the rating file's sequence per respondent for 602 of 692 respondent-modes, the rest differing
##by missing ratings). No opt-out (exactly one mode chosen per row; no blank choice).
##Attributes of each alternative: mode (label), travel time, cost. Travel time (minutes): car = cartime (5, 20, 40); the other
##modes derive from the base time acttime (5, 15, 25) by the README rule: e-bike x 1, e-scooter x 4/3, walk x 4 (so e-bike
##5/15/25, e-scooter 6.7/20/33.3, walk 20/60/100; computed by the script, display rounding unknown). Cost (EUR): car = carcost
##(3.5, 5, 6.5; this column is NOT described in the README; EUR assumed, as for the others), e-bike = ebikecost (1.5, 3, 4.5),
##e-scooter = escootcost (0.5, 2, 3.5), walk: no cost column, stored "(not shown)". Level text "<n> minutes" and "EUR <x>".
##The road-environment image attributes (infrastructure type, pavement, obstacles, zebra crossing, vehicle/bike/pedestrian
##density) are NOT in the choice file; they sit in the rating file (one row per respondent x mode x scenario, no scenario
##key) and are not joined, since the join would be by row order only.
##Outcomes: choice = the mode selected (1 on the chosen alternative; the Munich file spells e-scooter "escooter", pooled with
##"escoot"); rating_perceived_safety = the respondent's own 1-7 safety rating for that mode in the scenario (1 = very unsafe,
##7 = very safe; the NA ratings, 74 rows, stay NA).
##Pooling: Athens and Munich pooled with cov_city, as the deposit does; one design and shared level text.
##Covariates joined by pid from the rating file (constant within pid, verified): cov_gender (0 male, 1 female, README),
##cov_age_group_code (README lists "1: <18, 2: 18-30, 3: 31-40, 3: 41-50, 5: 50-65, 6: 65+": code 3 is duplicated and code 1 = 51% of rows is implausible for '<18', so the codes are kept unmapped), cov_education (README text),
##cov_income_band_eur_month (README text), cov_car_owner. 1 respondent in the choice file has no rating-file covariates (NA).
##pid is re-keyed to 1..N. No identifying columns; no survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ch <- fread(file.path(raw, "choice_dataset_perceivedSafetyChoices_v2.0.csv"))
ra <- fread(file.path(raw, "rating_dataset_perceivedSafetyChoices_v2.0.csv"))
stopifnot(nrow(ch) == 2059, uniqueN(ch$pid) == 173)
ch[choice == "escooter", choice := "escoot"]
stopifnot(all(ch$choice %in% c("car", "ebike", "escoot", "walk")))
ch[, task := seq_len(.N), by = pid]
ch[, id := match(pid, sort(unique(pid)))]
cv <- unique(ra[, .(pid, gender, age, education, income, car_own)])
stopifnot(!anyDuplicated(cv$pid))
cv <- cv[match(ch$pid, pid)]
fmt <- function(x) as.character(round(x, 1))
modes <- c("car", "ebike", "escoot", "walk")
labs <- c(car = "Car", ebike = "E-bike", escoot = "E-scooter", walk = "Walk")
mk <- function(k) {
  m <- modes[k]
  tt <- switch(m, car = ch$cartime, ebike = ch$acttime, escoot = ch$acttime * 4 / 3, walk = ch$acttime * 4)
  cs <- switch(m, car = paste("EUR", sprintf("%.2f", ch$carcost)), ebike = paste("EUR", sprintf("%.2f", ch$ebikecost)),
               escoot = paste("EUR", sprintf("%.2f", ch$escootcost)), walk = rep("(not shown)", nrow(ch)))
  data.table(id = ch$id, task = ch$task, profile = k, choice = as.integer(ch$choice == m),
             rating_perceived_safety = as.integer(ch[[paste0(m, "psafe")]]),
             attr_mode = labs[[m]], attr_travel_time = paste(fmt(tt), "minutes"), attr_cost = cs,
             cov_city = ch$city,
             cov_gender = ifelse(cv$gender == 0, "male", ifelse(cv$gender == 1, "female", NA)),
             cov_age_group_code = as.integer(cv$age),
             cov_education = c("no education", "primary", "secondary", "higher", "master")[cv$education + 1L],
             cov_income_band_eur_month = c("no income", "<750 euros/month", "750-1500 euros/month", "1500-2500 euros/month", ">= 2500 euros/month")[cv$income + 1L],
             cov_car_owner = as.integer(cv$car_own))
}
o <- rbindlist(lapply(1:4, mk))
setorder(o, id, task, profile)
stopifnot(o[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(o$attr_travel_time), !anyNA(o$attr_cost),
          ch[, uniqueN(city), pid][, all(V1 == 1)])
dir.create(out, showWarnings = FALSE, recursive = TRUE)
fwrite(o, file.path(out, "tzouras_2025_mode_safety.csv"))
