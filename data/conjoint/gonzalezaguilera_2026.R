##Interurban mode choice on the Santiago-Rancagua corridor (Chile): stated-preference experiment, from the Zenodo deposit
##"Stated Preference Survey on Interurban Mode Choice: Santiago-Rancagua Corridor, Chile" (Gonzalez-Aguilera, Guevara,
##Henriquez-Jara & Daziano, 2026). No article DOI in the deposit (doi = "").
##Deposit: doi:10.5281/zenodo.21270302 (concept doi 10.5281/zenodo.21270301), CC BY 4.0 (record licence cc-by-4.0; the repository
##LICENSE is CC BY 4.0). Files read (extracted individually from the deposit's zip Santiago-Rancagua-SP-dataset-v1.0.0.zip):
##data/sp_santiago_rancagua_public.csv, README.md (the data dictionary), docs/figures/example-sp-2mode.png and
##example-sp-3mode.png (screenshots of the Spanish choice screens, read visually), LICENSE. Example code and model output not used.
##Usage: Rscript gonzalezaguilera_2026.R <dir holding the csv> <output dir>
##
##Sample: 420 online-panel respondents (Netquest, May 2026), 13 tasks each = 5,460 rows. Tasks 1-12 are the D-efficient design
##tasks (5,040 rows); task 13 is a dominated attention-check task shown to everyone and is DROPPED here (the dictionary does not say
##which alternative dominates, so no pass/fail covariate is derived). Each respondent was assigned one of six OD designs
##(od_design) by the destination of their last trip, and one of 4 blocks of 13 tasks (block): a fixed blocked design.
##Pivot design: attribute levels were pivoted around average times and costs per OD pair and mode, but the file stores the absolute
##values actually displayed (tt, headway, variability, lmt, cost or cost_reduced), so they are used as the levels.
##Alternatives (labelled; profile 1 = Train, 2 = Coach bus, 3 = Rural bus "Micro", in screen order): the rural bus is offered only in
##designs Buin-BuinZoo-Linderos and Paine (av_micro = 1); elsewhere it has no profile row (not offered). A fixed "No me convence
##ninguna opcion (no viajaria)" option (choice = 4) has no attributes, so it is the opt-out (opt_out = yes), no profile row.
##Choice: "If these were the only options for your habitual trip, which would you choose?" (translated; Spanish screenshot: "Si
##estas fueran las unicas opciones para tu viaje habitual, cual elegirias?"). choice 1/2/3 = train / coach bus / rural bus, 4 = opt-out
##(verified: choice 3 occurs only where av_micro = 1; every task has exactly one choice).
##Attributes (8 per mode, all displayed in the attribute table of the screenshots; wording translated from the Spanish screen):
##  crowding: train and rural bus 1-5 (1 = less than half of seats occupied, nobody standing; 2 = more than half, nobody standing;
##    3 = all seats occupied, few people standing; 4 = all occupied, slight difficulty moving; 5 = all occupied, maximum difficulty
##    moving), coach bus 1-3 (less than half of seats occupied / more than half / all seats occupied, everyone seated) -- dictionary
##    8.3 and screenshots;
##  last-mile time "N min by car / walking / by public transport" (lmt; the access mode shown follows the respondent's last_mile_mode:
##    code 1 walking, 2-3 public transport, 4-7 car or taxi -- the grouping reproduces the dictionary's 22.4 / 42.9 / 34.8%; only the
##    Spanish "en auto" is visible in the screenshots, the walking and public-transport phrases are inferred);
##  frequency "every N min" (headway); air conditioning (with / without A/C); street vendors and musicians on board (usually present /
##    no vendors or musicians; shown for the coach bus too); cost in CLP (cost, or cost_reduced when reduced_fare = 1: the screen
##    adjusted the fare automatically); in-vehicle travel time "N min"; departure variability (0 = departs at exactly the published time,
##    else "up to N min late").
##Attribute order within the table was randomized per respondent (JavaScript in Qualtrics, README section 10) but not stored: attr_order =
##respondent, no attrpos columns. Level probabilities: not stated (D-efficient design).
##Covariates (dictionary codings): cov_age, cov_gender (1 male, 2 female; 3 absent from the sample), cov_income_gse (AB, C1a, C1b, C2,
##C3, D, E), cov_household_size, cov_driving_licence (1 yes, 2 no), cov_cars_household (0-4, 4 = four or more), cov_reduced_fare (0/1),
##cov_destination (text), cov_last_mile_mode (text). trial_od_design and trial_block. Dropped: survey duration, usage frequencies, trip
##purpose, luggage, companion, the 20-item psychometric battery, the 27 satisfaction items, timer. No survey weight. No identifying
##columns (respondent_id is a sequential anonymous number).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "sp_santiago_rancagua_public.csv"))
stopifnot(nrow(d) == 5460, uniqueN(d$respondent_id) == 420, d[, all(task_id == 1:13), respondent_id][, all(V1)])
d <- d[task_id <= 12]
stopifnot(nrow(d) == 5040, all(d$choice %in% 1:4), d[av_micro == 0, !any(choice == 3)], all(d$av_train == 1), all(d$av_bus == 1))
d[, id := respondent_id]
cr5 <- c("Less than half of seats occupied, nobody standing", "More than half of seats occupied, nobody standing",
         "All seats occupied, few people standing", "All seats occupied, slight difficulty moving", "All seats occupied, maximum difficulty moving")
cr3 <- c("Less than half of seats occupied, everyone seated", "More than half of seats occupied, everyone seated", "All seats occupied, everyone seated")
lm <- function(x, m) paste(x, "min", ifelse(m == 1, "walking", ifelse(m %in% 2:3, "by public transport", "by car")))
mk <- function(k, pre, lab, crl) {
  p <- function(v) d[[paste0(pre, "_", v)]]
  rows <- if (pre == "micro") d$av_micro == 1 else rep(TRUE, nrow(d))
  cost <- ifelse(d$reduced_fare == 1, p("cost_reduced"), p("cost"))
  stopifnot(!anyNA(cost[rows]), all(p("crowding")[rows] %in% seq_along(crl)), !anyNA(p("lmt")[rows]), all(p("aircon")[rows] %in% 0:1), all(p("vendors")[rows] %in% 0:1))
  r <- data.table(id = d$id, task = as.integer(d$task_id), profile = k, choice = as.integer(d$choice == k),
    attr_mode = lab,
    attr_crowding = crl[p("crowding")],
    attr_last_mile_time = lm(p("lmt"), d$last_mile_mode),
    attr_frequency = paste("every", p("headway"), "min"),
    attr_air_conditioning = ifelse(p("aircon") == 1, "With air conditioning", "Without air conditioning"),
    attr_street_vendors_musicians = ifelse(p("vendors") == 1, "Usually present", "No street vendors or musicians"),
    attr_cost = paste("CLP", cost),
    attr_travel_time = paste(p("tt"), "min"),
    attr_departure_variability = ifelse(p("arrival_time_variability") == 0, "Departs at exactly the published time", paste("Up to", p("arrival_time_variability"), "min late")),
    trial_od_design = d$od_design, trial_block = as.integer(d$block),
    cov_age = as.integer(d$age), cov_gender = ifelse(d$gender == 1, "male", ifelse(d$gender == 2, "female", NA)),
    cov_income_gse = c("AB", "C1a", "C1b", "C2", "C3", "D", "E")[d$income_gse], cov_household_size = as.integer(d$household_size),
    cov_driving_licence = ifelse(d$has_licence == 1, "Yes", "No"), cov_cars_household = as.integer(d$n_cars_household),
    cov_reduced_fare = as.integer(d$reduced_fare),
    cov_destination = c("Buin / Buin Zoo", "Linderos", "Paine", "Hospital", "San Francisco de Mostazal", "Graneros", "Rancagua", "Machali")[d$destination],
    cov_last_mile_mode = c("Walking", "Urban public transport (city bus)", "Shared taxi (colectivo)", "Regular taxi", "Uber / ride-hailing apps",
                           "Car, as passenger", "Car, as driver", "Bicycle / scooter")[d$last_mile_mode])
  r[rows]
}
o <- rbind(mk(1L, "train", "Train", cr5), mk(2L, "bus", "Coach bus", cr3), mk(3L, "micro", "Rural bus", cr5))
setorder(o, id, task, profile)
stopifnot(o[, sum(choice), .(id, task)][, all(V1 <= 1)], !anyNA(o[, .SD, .SDcols = patterns("^attr_")]),
          o[, .N, .(id, task)][, all(N %in% 2:3)], uniqueN(o$id) == 420)
dir.create(out, showWarnings = FALSE, recursive = TRUE)
fwrite(o, file.path(out, "gonzalezaguilera_2026_interurban_mode.csv"))
