##Electric-vehicle purchase choice experiment (US) from
##Zou, T., Khaloei, M., & MacKenzie, D. (2020). Effects of charging infrastructure
##characteristics on electric vehicle preferences of new and used car buyers in the United
##States. Transportation Research Record, 2674(12), 165-175.
##https://doi.org/10.1177/0361198120952792
##Replication data: Harvard Dataverse doi:10.7910/DVN/MOT6PN ("2019 EV infrastructure and
##purchase choice survey"), CC0 1.0, no restricted files. Files read: "Data - 2019 EV
##infrastructure and purchase choice survey.csv" (original format of the .tab) and the
##Dictionary xlsx (original format; variable meanings and answer codes). Design facts and the
##screen layout are from the authors' 2019 manuscript (UW ResearchWorks, handle 1773/45289,
##TRB paper 20-05154): Table 1 (attribute levels) and Figure 1 (screenshot of a task).
##Usage: Rscript zou_2020.R <dir holding data.csv> <output dir>
##
##983 US car owners recruited on MTurk (SurveyMonkey, 28 June-9 July 2019), 6 choice tasks
##each. A discrete choice experiment: every task shows two options side by side, a gasoline
##car (left, profile 1) and an electric version of it (right, profile 2), and the respondent
##picks one. The gasoline car has DISPLAYED attributes (price, fuel cost, range) that are fixed
##by design, so it is a profile, not an opt-out. Respondents first chose whether their next car
##would be new or used and then saw that arm (trial_car_type new/used; the option header reads
##"Used Gasoline Car" / "Used EV" in Figure 1, "New ..." by analogy in the other arm; attr_option
##stores "Gasoline Car" / "EV").
##Outcome: choice (bichoice 1 = buy EV -> profile 2, 0 = buy gas car -> profile 1). Wording not
##in the deposit or manuscript: paraphrase. Forced choice between the two, no opt-out.
##Attribute text is rebuilt from the deposit's values with the templates of Figure 1:
##  attr_price "$17,000": EV = priceshow; gasoline = 0.85 x the respondent's budget (numprice;
##    "$50,000 or more" = 50,000), Table 1. The EV price is 0.7/0.85/1.0 x budget.
##  attr_fuel_cost "$12 per 100 miles" (gasoline) / "$4 per 100 miles" (EV), fixed.
##  attr_range "400 miles" (gasoline, fixed) / "<range> miles" (EV: 100-400).
##  attr_slow_charging_home "<home_chg> min walk from home", attr_slow_charging_work
##    "<work_chg> min walk from workplace" (0-20 min), attr_fast_charging_time "<fasttime> min
##    from empty to full charge" (5/15/30/60; Table 1 writes 60 as "1h"),
##  attr_fast_charging_town "Available within <town> min drive from any place in town",
##  attr_fast_charging_highway "Available at every <highway> miles on highway".
##  The charging rows are blank for the gasoline car in Figure 1: "(not shown)".
##  The text of levels absent from Figure 1 is NOT verified: 0 minutes ("0 min walk from
##  home"), 60 minutes, and "Not available" for town ("no"; dictionary: "not available in
##  town") and highway ("no"; Table 1: "Not available") are written "Not available in town" /
##  "Not available on highway".
##trial_design_row = `comb`, the row of the full factorial the task came from (240 tasks of an
##orthogonal fractional design, 6 assigned at random per respondent). Task order: the file has
##no display-order column; task = row order within respondent (INFERRED, order shown unknown).
##Covariates (dictionary answer text): cov_gender (1 male, 0 female), cov_race ("Prefer not to
##answer" -> NA), cov_state, cov_license, cov_education (edu), cov_employment, cov_income
##(hsincome), cov_household_size, cov_housing, cov_residence, cov_move_3yr, cov_cars_owned,
##cov_new_cars_owned, cov_evs_owned, cov_new_evs_owned (counts), cov_home_parking_* 0/1 (a
##multi-select: attached garage, detached garage, driveway or carport, assigned space, on
##street), cov_home_evse, cov_work_parking, cov_work_evse, cov_buy_car_3yr, cov_daily_miles
##(dmileage), cov_long_trips_month (long_dist), cov_gas_cost_month (gascost, $), cov_budget
##(price, the budget answer text), cov_age (age in years, computed by the authors as 2019 -
##birth year per the dictionary).
##Dropped: home ZIP codes (rzip, zipcode) and the ZIP-derived PopDensity (identifying); free
##text hp6 ("other parking, specify"); derived variables (priceprop, orphan, used_car_owner,
##used_ev_owner, ev_owner, freq = 6); `scenario` (a serial within arm; `comb` kept).
##N: 983 respondents, as in the paper (533 used-car buyers per manuscript Table 2; 2,700 and
##3,198 tasks for new and used buyers, as in Table 3).
##Spot check: the used-buyer binomial logit of manuscript Table 3 reproduces from this table
##(price difference EV - gasoline -0.1176 per $1,000, SE 0.0165; range 0.0035; walk from home
##-0.0605 vs -0.0603; log-likelihood -2056.5), which also confirms the gasoline price rule.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data.csv"))
stopifnot(nrow(s) == 5898, s[, .N, subject][, all(N == 6)], all(s$bichoice %in% 0:1), all(s$used %in% 0:1))
s[, task := seq_len(.N), subject]
stopifnot(all(abs(s$priceshow / s$numprice - s$priceprop) < 1e-9))
money <- function(x) paste0("$", formatC(x, format = "d", big.mark = ","))
lab <- function(v, l) { v <- as.integer(v); stopifnot(all(v %in% seq_along(l))); l[v] }
ns <- "(not shown)"
g <- s[, .(id = as.integer(subject), task, profile = 1L, choice = as.integer(bichoice == 0), attr_option = "Gasoline Car",
           attr_price = money(round(0.85 * numprice)), attr_fuel_cost = "$12 per 100 miles", attr_range = "400 miles",
           attr_slow_charging_home = ns, attr_slow_charging_work = ns, attr_fast_charging_time = ns,
           attr_fast_charging_town = ns, attr_fast_charging_highway = ns)]
e <- s[, .(id = as.integer(subject), task, profile = 2L, choice = as.integer(bichoice == 1), attr_option = "EV",
           attr_price = money(priceshow), attr_fuel_cost = "$4 per 100 miles", attr_range = paste(range, "miles"),
           attr_slow_charging_home = paste(home_chg, "min walk from home"),
           attr_slow_charging_work = paste(work_chg, "min walk from workplace"),
           attr_fast_charging_time = paste(fasttime, "min from empty to full charge"),
           attr_fast_charging_town = fifelse(town == "no", "Not available in town", paste0("Available within ", town, " min drive from any place in town")),
           attr_fast_charging_highway = fifelse(highway == "no", "Not available on highway", paste0("Available at every ", highway, " miles on highway")))]
stopifnot(all(s$town %in% c("5", "10", "15", "no")), all(s$highway %in% c("30", "50", "70", "no")))
tr <- s[, .(id = as.integer(subject), task, trial_car_type = fifelse(used == 1, "used", "new"), trial_design_row = comb)]
cv <- unique(s[, .(id = as.integer(subject),
  cov_gender = fifelse(gender == 1, "male", "female"),
  cov_race = fifelse(race == "Prefer not to answer", NA_character_, race), cov_state = state_answer, cov_license = license,
  cov_education = lab(edu, c("Less than high school", "Graduated from high school", "Some College/Technical school training",
                             "2-Year College Degree (Associates)", "4-Year College Degree (BA, BS)", "Master's Degree",
                             "Professional Degree (MD, JD)", "Doctoral Degree")),
  cov_employment = lab(employment, c("Employed, working full-time", "Employed, working part-time", "Student", "Not employed", "Retired", "Other")),
  cov_income = lab(hsincome, c("Under $25,000", "$25,000-$49,999", "$50,000-$74,999", "$75,000-$99,999", "$100,000-$124,999",
                               "$125,000-$149,999", "$150,000-$174,999", "$175,000-$199,999", "$200,000 and up")),
  cov_household_size = lab(hhsize, c("1", "2", "3", "4", "5 or more")),
  cov_housing = lab(housit, c("Owned/Purchasing (i.e. housing with a mortgage)", "Renting", "Provided by employer (private or military)", "Other")),
  cov_residence = lab(residence, c("Single-family house (detached house)", "Townhouse (attached house)", "Multi-family house (3 or fewer apartments)",
                                   "Building with 3 or fewer apartments/condos", "Building with 4 or more apartments/condos",
                                   "Mobile home/trailer", "Dorm or institutional housing", "Other")),
  cov_move_3yr = lab(move, c("Yes", "No", "Not sure")),
  cov_cars_owned = all_car, cov_new_cars_owned = new_car, cov_evs_owned = ev, cov_new_evs_owned = new_ev,
  cov_home_parking_attached_garage = as.integer(!is.na(home_parking)), cov_home_parking_detached_garage = as.integer(!is.na(hp2)),
  cov_home_parking_driveway = as.integer(!is.na(hp3)), cov_home_parking_assigned_space = as.integer(!is.na(hp4)),
  cov_home_parking_on_street = as.integer(!is.na(hp5)),
  cov_home_evse = lab(home_evse, c("Yes", "No", "I don't know")),
  cov_work_parking = lab(work_parking, c("Designated parking space", "Job-provided parking lot with unassigned spaces (free or paid)",
                                         "Paid parking in a commercial lot or garage", "On-street", "I don't drive to work", "Other")),
  cov_work_evse = lab(work_evse, c("Yes", "No", "I don't know")),
  cov_buy_car_3yr = lab(buycar, c("Yes", "No", "Not sure")),
  cov_daily_miles = dmileage, cov_long_trips_month = long_dist, cov_gas_cost_month = gascost,
  cov_budget = trimws(price), cov_age = as.integer(age))])
stopifnot(nrow(cv) == 983)
d <- merge(merge(rbind(g, e), tr, by = c("id", "task")), cv, by = "id")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "zou_2020_ev_purchase.csv"))
