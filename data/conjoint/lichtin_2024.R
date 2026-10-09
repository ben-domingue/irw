##Public-transport policy factorial survey (Swiss Mobility Panel, wave 4) from
##Lichtin, F. M., Smith, E. K., Axhausen, K. W., & Bernauer, T. (2024). How much should public
##transport services be expanded, and who should pay? Experimental evidence from Switzerland.
##Transport Policy, 158, 64-74. https://doi.org/10.1016/j.tranpol.2024.08.016
##Replication data: OSF g7k8m ("The future of public transport design in a post-pandemic World"),
##https://osf.io/g7k8m/, node licence CC0 1.0 Universal. Files read: replication material/
##LichtinSmithAxhausenBernauer_PT_DATA.RData (df_fact; saved as PT_DATA.RData) and the
##pre-registration Lichtin_Smith_Axhausen_Bernauer_Public_Transport_Experiment_Pre-reg_W4.pdf
##(design, English level text, outcome wording, German Qualtrics print-out). The Readme calls the
##.RData "a data extract" of the Swiss Mobility Panel (full data to be released on SWISSUbase);
##the OSF extract itself carries CC0 and no terms.
##Usage: Rscript lichtin_2024.R <dir holding PT_DATA.RData> <output dir>
##
##7,442 respondents of wave 4 of the Swiss Mobility Panel (registry sample of Swiss residents 18+,
##online, Nov 2022 - Feb 2023, survey in German, French, Italian or English) each read ONE policy
##proposal (task = profile = 1): a full factorial of 4 attributes, 3 x 3 x 3 x 2 = 54 designs,
##shown as four bullet sentences (prereg section 9, Qualtrics fields Taktfahrplan/Region/Billette/
##Beitrag, fixed order). The deposit has no respondent id; one row = one respondent (prereg: "each
##respondent is presented with one potential policy design"), so id = row number.
##Level text = the prereg's English instrument sentences, mapped from the deposit's short labels:
##  attr_connections  Increase of Connections -> "The number of connections per day will be
##    increased (the 'fixed interval' timetable will be expanded)."; Today's Connections -> "The
##    number of connections per day remains the same as today (...)"; Demand-based Connections ->
##    "The number of connections will be reduced at times when demand is low and increased ...".
##  attr_peripheral_regions  Expanded / Today's / Demand-based Coverage -> the three
##    "Public transport connections to peripheral regions ..." sentences.
##  attr_ticket_prices  10-20% Increase / No Change / 10-20% Reduction -> "... will become 10-20%
##    more expensive." / "... will remain the same as today ..." / "... 10-20% less expensive."
##  attr_public_contribution  Increase 1bn CHF / Reduce 1bn CHF -> "Increase (Reduction) of the
##    annual public sector contribution to public transport from today's CHF 9 billion to CHF 10
##    (8) billion."
##(The prereg table and its example vignette word the "no change" ticket level slightly
##differently: "less expensive" vs "cheaper"; the table wording is used.)
##Outcomes (prereg wording, English master; respondents saw their survey language):
##  choice = w4_q60x1 "Imagine you had to decide today only on this proposal in a popular vote,
##    would you vote for or against it?" 1 = Vote for, 0 = Vote against (authors' 0/1 coding with
##    value labels); single proposal, so voting against is the outside option (opt_out = yes).
##  rating = w4_q60x2 "Please indicate, how much do you support or oppose this proposal?" 1
##    Strongly oppose .. 7 Strongly support.
##trial_info_arm = w4_split: 1 "Full info" (long instructions explaining each attribute before the
##proposal) / 2 "Short info" (short instructions); the proposal text was the same (prereg
##E1_long/E1_short). The authors' main analyses use both arms (df_fact) and restrict to 12
##"fully plausible" designs (n = 1,634 in the article); the table keeps all 54 designs.
##Covariates (deposit codings): cov_survey_weight = w4_weights_raking (the authors' raking
##weight); cov_residence (are_cities Urban/Suburban/Rural); cov_car_owner (Car: Yes/No);
##cov_left_right (lr, 0 left .. 10 right); cov_income_quintile (inc_pc_quint_char Q1-Q5, per
##capita income); cov_access_road_tertile / cov_access_pt_tertile (T1-T3). Dropped: the
##municipality-level PT accessibility score and decile (OeV_Erreichb_EWAP, access_pt_dec: close
##to a location identifier), pt_use and pt_connection_quality (codes without labels in the
##deposit), w4_q72 (= lr) and the authors' duplicated relabelled columns.
##N: 7,442 rows; the article's n = 1,634 is the plausible-design subset (here 1,634 too: see
##stopifnot). No attention check, no repeat.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "PT_DATA.RData"), envir = e); x <- as.data.table(e$df_fact)
m <- function(v, map) { v <- as.character(v); stopifnot(all(v %in% names(map))); unname(map[v]) }
conn <- c("Increase of Connections" = "The number of connections per day will be increased (the ‘fixed interval’ timetable will be expanded).",
          "Today's Connections" = "The number of connections per day remains the same as today (the ‘fixed interval’ timetable is maintained but not further expanded).",
          "Demand-based Connections" = "The number of connections will be reduced at times when demand is low and increased at times when demand is high (dismantling of the ‘fixed interval’ timetable).")
reg <- c("Expanded Coverage" = "Public transport connections to peripheral regions will be expanded.",
         "Today's Coverage" = "Public transport connections to peripheral regions will remain the same as today, but will not be further expanded.",
         "Demand-based Coverage" = "Public transport connections to peripheral regions will be reduced according to demand (reduction of connections, replacement of trains through buses), and at the same time connections will be expanded to regions where demand is higher.")
tick <- c("10-20% Increase" = "Tickets and travel cards (e.g. GA Travelcard, Half Fare Travelcard, Regional Travel Pass) will become 10-20% more expensive.",
          "No Change" = "Prices for tickets and season tickets (e.g. GA Travelcard, Half Fare Travelcard, Regional Travel Pass) will remain the same as today, i.e. they will not become more expensive or less expensive.",
          "10-20% Reduction" = "Tickets and travel cards (e.g. GA Travelcard, Half Fare Travelcard, Regional Travel Pass) will become 10-20% less expensive.")
sub <- c("Increase 1bn CHF" = "Increase of the annual public sector contribution to public transport from today’s CHF 9 billion to CHF 10 billion.",
         "Reduce 1bn CHF" = "Reduction of the annual public sector contribution to public transport from today’s CHF 9 billion to CHF 8 billion.")
stopifnot(identical(attr(x$w4_q60x1, "labels"), c("Vote against" = 0, "Vote for" = 1)), all(x$w4_q60x1 %in% 0:1), all(x$w4_q60x2 %in% 1:7))
d <- data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L, choice = as.integer(x$w4_q60x1), rating = as.integer(x$w4_q60x2),
                attr_connections = m(x$w4_fact_attr_connections, conn), attr_peripheral_regions = m(x$w4_fact_attr_regions, reg),
                attr_ticket_prices = m(x$w4_fact_attr_tickets, tick), attr_public_contribution = m(x$w4_fact_attr_subsidy, sub),
                trial_info_arm = c("Full info", "Short info")[as.integer(x$w4_split)],
                cov_survey_weight = as.numeric(x$w4_weights_raking), cov_residence = as.character(x$are_cities),
                cov_car_owner = as.character(x$car_owner), cov_left_right = as.integer(x$lr),
                cov_income_quintile = as.character(x$inc_pc_quint_char), cov_access_road_tertile = as.character(x$access_road_tert_char),
                cov_access_pt_tertile = as.character(x$access_pt_tert_char))
stopifnot(all(x$w4_split %in% 1:2))
# the authors' 12 "fully plausible" designs give the article's n = 1,634
pl <- paste(x$`Number of Connections`, x$`Network Coverage`, x$`Ticket Prices`, x$`Government Financial Contributions`, sep = "|")
plaus <- c("Increase of Connections|Expanded Coverage|10-20% Increase|Increase 1bn CHF", "Increase of Connections|Today's Coverage|No Change|Increase 1bn CHF",
           "Increase of Connections|Demand-based Coverage|10-20% Increase|Reduce 1bn CHF", "Increase of Connections|Demand-based Coverage|10-20% Reduction|Increase 1bn CHF",
           "Today's Connections|Expanded Coverage|No Change|Increase 1bn CHF", "Today's Connections|Today's Coverage|10-20% Increase|Reduce 1bn CHF",
           "Today's Connections|Today's Coverage|10-20% Reduction|Increase 1bn CHF", "Today's Connections|Demand-based Coverage|No Change|Reduce 1bn CHF",
           "Demand-based Connections|Expanded Coverage|10-20% Increase|Reduce 1bn CHF", "Demand-based Connections|Expanded Coverage|10-20% Reduction|Increase 1bn CHF",
           "Demand-based Connections|Today's Coverage|No Change|Reduce 1bn CHF", "Demand-based Connections|Demand-based Coverage|10-20% Reduction|Reduce 1bn CHF")
cat("plausible designs:", sum(pl %in% plaus), "\n")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lichtin_2024_public_transport.csv"))
