##Reed dance and wetland conservation choice experiment, Eswatini, from
##Mahlalela, L. S. (2024). Stakeholder preferences for ecosystem services provided by wetlands in Eswatini (PhD thesis,
##University of Pretoria), chapter 3. Data: Mahlalela, L., Jourdain, D., Mungatana, E., & Hedemark Lundhede, T. (2024).
##Q-methodology and stated preferences data of stakeholder preferences for ecosystem services. University of Pretoria.
##doi:10.25403/UPresearchdata.25187747.v1, CC BY 4.0 (figshare record licence).
##Files read: Stated_preferences_data_on_wetland_ecosystem_services.xlsx (sheets Data, Choice Sets, Key). The Q-method
##files of the deposit are not a conjoint and were not used. Attribute wording and units come from the thesis
##(repository.up.ac.za handle 2263/94396): Table 3.1, the choice card of Figure 3.3 and section 3.3.5.
##Usage: Rscript mahlalela_2024.R <dir holding the xlsx> <output dir>
##
##Face-to-face interviews with households in Eswatini; 444 respondent rows (thesis: 450 collected; the rows kept are the
##deposit's, including respondents the thesis later treats as protest answers). Each respondent saw 12 choice cards of
##three unlabelled alternatives: Status Quo (always 3% of wetlands conserved, 12 hours of education, 2500 tourists,
##E0) and two programmes. The status quo shows displayed levels, so it is a profile (profile 1); there is no opt-out.
##Outcome (choice): "choose the option you prefer ... only one option in each choice card" (valuation scenario, 3.3.5).
##Fixed design: the 12 cards are the same for every respondent (Bayesian D-efficient, Ngene); the deposit's design sheet
##holds one row per card. The thesis does not say whether card order was randomized: task = card number in the design
##(INFERRED display order; task_source = inferred). Profile order Status Quo, Alternative 1, Alternative 2 is the card layout (Figure 3.3).
##Three split samples differ only in the payment-vehicle paragraph (household tax / voluntary contributions / reduction
##of subsidies): kept as trial_payment_vehicle (Key sheet: 1 Tax, 2 Contributions, 3 Subsidy); the price row is stored as
##E<amount> per year for all three (the card shown in the thesis is the tax version).
##Attributes (displayed text): wetland conservation (card text; the thesis card shows 3% and 6%, the 12% text is the
##Table 3.1 wording with the card's "high probability ... increases" phrasing: INFERRED for 12%), informal education
##("8|12|16 hours"), tourist presence ("1000|2500|5000|7500 tourists"; deposit stores thousands), annual household tax
##("E0|10|20|40|80|120 per year"; Emalangeni, equal to the Rand).
##Respondent key: the deposit ID is not unique (ID 94 appears twice with different answers and 6 IDs between 1 and 449
##are absent), so respondents are re-keyed 1..444 in row order. Restrictions: none documented. Level weights: unknown
##(efficient design, status quo fixed). No covariates in this file. Survey weight: none.
##Dropped: nothing (all 12 cards answered by everyone).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "Stated_preferences_data_on_wetland_ecosystem_services.xlsx")
x <- as.data.table(read_excel(f, sheet = "Data")); cs <- as.data.table(read_excel(f, sheet = "Choice Sets"))
stopifnot(nrow(x) == 444, nrow(cs) == 12, !anyNA(x), all(unlist(x[, 2:13]) %in% 1:3))
x[, id := .I]
wet <- c("3" = "Continue with the conserved 3% of wetlands and there is high probability that reeds supply decreases",
         "6" = "Conserve 6% of wetlands and there is high probability that reeds supply increases",
         "12" = "Conserve 12% of wetlands and there is high probability that reeds supply increases")
pv <- c("1" = "Tax", "2" = "Contributions", "3" = "Subsidy")
res <- rbindlist(lapply(1:12, function(s) rbindlist(lapply(1:3, function(p) {
  v <- function(n) cs[[paste0(n, "_", p)]][s]
  stopifnot(cs[["Choice Set ID"]][s] == s)
  data.table(id = x$id, task = s, profile = p, choice = as.integer(x[[paste("Choice set", s)]] == p),
    attr_wetland_conservation = unname(wet[as.character(v("Wetland Conservation"))]),
    attr_informal_education = paste(v("Informal Education"), "hours"),
    attr_tourist_presence = paste(v("Tourist Presence") * 1000, "tourists"),
    attr_annual_household_tax = paste0("E", v("Price"), " per year"),
    trial_payment_vehicle = unname(pv[as.character(x[["Payment vehicle"]])]))
}))))
stopifnot(!anyNA(res), res[, sum(choice), .(id, task)][, all(V1 == 1)], res[, .N, id][, all(N == 36)])
setorder(res, id, task, profile)
fwrite(res, file.path(out, "mahlalela_2024_reed_dance_wetlands.csv"))
