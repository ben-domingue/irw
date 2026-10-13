##Charging-station choice experiment (Switzerland) from
##Brückmann, G., & Bernauer, T. (2023). An experimental analysis of consumer preferences towards
##public charging infrastructure. Transportation Research Part D, 121, 103626.
##https://doi.org/10.1016/j.trd.2023.103626
##Replication data: Zenodo doi:10.5281/zenodo.18232567 (concept DOI; record 18232568), CC BY 4.0.
##Files read: dataforupload_chargerconjoint230206.dta (value labels), SurveyInstrumentForPublishing.pdf,
##TRD103626corrected.pdf (article, Table 3), ReplicationCodeTRD2023.do (text only, not run).
##Not used: meansandsdsandmaxwait.dta; the reservation vignette columns (preisreservierung, wait,
##wait22, reserve*, waitlongshort, wait2) belong to the separate Q19 reservation question.
##Usage: Rscript brueckmann_2023.R <dir holding the .dta> <output dir>
##
##2,831 Swiss car holders (panel survey, Oct-Nov 2020; 950 with a BEV in the household, 1,881 without,
##as in the paper), 5 tasks of 2 charging stations, forced choice ("Welche Ladestation würden Sie
##nutzen?", Station A or B; no opt-out). The paper's 5 attributes are shown in this order: waiting time
##until the station is free (2 or 3 equally likely values, always including 0 min), charging time,
##energy source, surroundings (amenities), price for a full charge. Display language German; the
##level text here is the English value-label text of the .dta (energy: Nuclear/Hydro/Solar/Wind; price
##"CHF 5"..."CHF 30"; queueing "0 or 5 or 10 min"). The amenities labels in the .dta are only
##"no"/"yes"; they are stored as the article's Table 3 text: "None (paved parking lot)" and
##"Shop, coffee shop, small patch of grass with bench and washrooms" (the instrument's German text shows
##"Kleine Rasenfläche mit Parkbank und WC" or "Shop, Café, kleine Rasenfläche mit Parkbank und WC",
##i.e. the lower level may omit the shop; the wording in the article is used). Charging time is
##30/60/120 min in the data (Table 3 says 30/60/90; the instrument and data say 120): stored as
##"30 min" etc.
##Task and profile: the long file has T = "_t<task>_c<2|3>". Task is the number after _t; the two profiles
##are _c2 -> 1 and _c3 -> 2 (assumed to be Station A and B: inferred, so profile_source = inferred);
##exactly one chosen per task verified. The row order of the file is shuffled.
##Covariates: cov_gender from the authors' dummy `female` (0 = male, 1 = female; article "Dummy for gender =
##female"); cov_birth_year (year of birth); cov_political_left_right (0 left to 10 right; "Rather not say"
##= NA); cov_household_income (value-label text; "Rather not say/DK" = NA); cov_bev_in_household (BEV / No
##BEV); cov_panel_sample (BEVs / Conventional Cars panel). `higheduc` (derived dummy) is dropped.
##No survey weight in the deposit. No PII.
##Count check: 2,831 respondents x 10 = 28,310 rows. Spot check: mean choice by price is monotone falling.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "dataforupload_chargerconjoint230206.dta")))
lab <- function(v) as.character(as_factor(k[[v]], levels = "labels"))
d <- data.table(id = as.integer(factor(k$id)), task = as.integer(sub("^_t([0-9]+)_c[23]$", "\\1", k$T)),
                profile = as.integer(sub("^_t[0-9]+_c([23])$", "\\1", k$T)) - 1L, choice = as.integer(k$choice))
d[, attr_queueing_time_min := lab("Queueingtime")]
d[, attr_charging_time := paste(as.integer(k$Chargingtime), "min")]
d[, attr_energy_source := lab("Energy")]
d[, attr_amenities := c("None (paved parking lot)", "Shop, coffee shop, small patch of grass with bench and washrooms")[as.integer(k$Amenities)]]
d[, attr_price := lab("Price")]
d[, cov_gender := c("male", "female")[k$female + 1L]]
d[, cov_birth_year := as.integer(k$year)]
d[, cov_political_left_right := as.integer(zap_labels(k$pol))]
d[, cov_household_income := lab("hhinc")]
d[, cov_bev_in_household := lab("BEVinhousehold")]
d[, cov_panel_sample := lab("ea")]
stopifnot(!anyNA(d[, .(id, task, profile, choice, attr_queueing_time_min, attr_charging_time, attr_energy_source, attr_amenities, attr_price)]),
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, id][, all(N == 10)], uniqueN(d$id) == 2831)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "brueckmann_2023_charging_stations.csv"))
