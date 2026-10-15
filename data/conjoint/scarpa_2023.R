##Two choice experiments on natural flood management (NFM) contracts with 348 farmers in northern England, from
##Scarpa, R., Aftab, A., & Leppert, D. J. (2023). Stated choices of hypothetical land management schemes from 348
##farmers in the north of England and associated socio-economic covariates, 2022. NERC EDS Environmental
##Information Data Centre. https://doi.org/10.5285/1409404f-564f-43c5-81dd-00339a674dc8
##Licence: Open Government Licence (EIDC catalogue record, licences uri eidc.ac.uk/licences/ogl/plain; access
##limitation "noLimitations"). No associated article is listed, so no paper N is available for comparison.
##Files read: data/ne-_w007495-_1_experiment1.csv and ..._experiment2.csv (inside the public data package zip),
##supporting-documents/ne-_w007495_1_dictionary.csv and ne-_w007495-_1_survey.pdf (read as text: the displayed
##choice cards CE1T1-T8 and CE3T1-T8).
##Usage: Rscript scarpa_2023.R <dir holding the two experiment csv files> <output dir>
##
##348 farmers (Cumbria, Durham, Northumberland; online, invited face to face or by phone; Qualtrics, 2022; GBP 50
##transfer). The same 348 respondents did both experiments, 8 choice situations each (Choice.situation = task),
##two contracts per situation (Option A = contract1, Option B = contract2) plus "I want neither A nor B" (opt-out).
##choice: 1 = A, 2 = B, 0 = neither (the dictionary's opt-out code). Outcome wording: "Which of the available
##options do you prefer?" with the card's neither option.
##Two tables, one per experiment (different attribute sets), the survey's scheme 1 and scheme 3 (the survey's
##scheme 2, a tradable flood mitigation scheme, is not in the deposit):
##  scarpa_2023_nfm_contracts: type of NFM feature (set-aside with natural regeneration / planted woodland),
##    location (in-field / field boundary / river edge), quality of land, size (1/20 or 1/10 ha), annual payment
##    (GBP 200-500). The cards also print the payment per hectare, a function of payment and size, not stored.
##    Quality: the cards show ONE land-quality text for both options of a task (verified for the eight example
##    cards), while the file has contract1.quality and contract2.quality as exact complements (1 - x in all 2,784
##    rows). The displayed text is therefore taken from contract1.quality (0 = prime grazing land or high yielding
##    crops, 1 = rough grazing, wet, steep, rocky or in dip etc., per the dictionary) for both profiles.
##  scarpa_2023_nfm_corridors: NFM feature type, number of neighbours coordinated with (none/one/two), width of the
##    connecting corridors (10/20 m), one-off coordination bonus (shown as GBP 0 when no neighbours: the file keeps a
##    placeholder bonus level on coord = 0 rows that the survey cards do not show, e.g. CE3T1 option A), annual
##    payment per 100 m (GBP 200-500).
##Restrictions (observed): the two options of a task always differ in feature type and, in experiment 2, in corridor
##width; in experiment 1 the two options always have opposite quality codes (see above). Data values are in
##thousands (0.5 = 500 sq m / GBP 500). Level weights: payment levels equal, other attributes balanced (observed
##shares are exactly equal blocks of 348): "unknown" (no probabilities stated).
##Covariates (dictionary): cov_gender (female 1/0), cov_age (2022 - birth year, as the deposit computes it),
##cov_education (edu_attain text: 0 no academic qualification/other ... 4 postgraduate degree), cov_farm_hectares
##(Q6), cov_farm_product (Q11 text: 1 cereals ... 7 mixed). Dropped: remaining farm and attitude covariates.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e1 <- fread(file.path(raw, "ne-_w007495-_1_experiment1.csv"))
e2 <- fread(file.path(raw, "ne-_w007495-_1_experiment2.csv"))
stopifnot(nrow(e1) == 2784, nrow(e2) == 2784, uniqueN(e1$ID) == 348, identical(e1$ID, e2$ID), identical(e1$Choice.situation, e2$Choice.situation))
stopifnot(all(e1$choice %in% 0:2), all(e2$choice %in% 0:2), e1[, all(contract1.quality + contract2.quality == 1)])
edu <- c("No academic qualification/other", "GCSEs or equivalent", "A levels or equivalent", "Undergraduate degree", "Postgraduate degree")
prod <- c("cereals", "general cropping", "grazing (non-dairy)", "pigs and poultry", "horticulture", "grazing (dairy)", "mixed")
cov <- function(e) e[, .(cov_gender = c("male", "female")[female + 1L], cov_age = as.integer(age), cov_education = edu[edu_attain + 1L],
                        cov_farm_hectares = hectare, cov_farm_product = prod[product])]
gbp <- function(v) paste0("£", round(v * 1000))
long <- function(e, f) {
  rbindlist(lapply(1:2, function(k) {
    g <- function(n) e[[paste0("contract", k, ".", n)]]
    cbind(data.table(id = e$ID, task = e$Choice.situation, profile = k, choice = as.integer(e$choice == k)), f(e, g), cov(e))
  }))
}
f1 <- function(e, g) data.table(
  attr_nfm_feature = c("Planted Woodland", "Set-aside with Natural Regeneration")[g("type") + 1L],
  attr_location = c("In-field", "River Edge", "Field Boundary")[g("location") + 1L],
  attr_land_quality = c("Prime grazing land or high yielding crops", "Rough grazing, wet, steep, rocky or in dip etc.")[e$contract1.quality + 1L],
  attr_size = fifelse(g("area") == 0.5, "1/20 of a hectare", "1/10 of a hectare"),
  attr_annual_payment = gbp(g("payment")))
f2 <- function(e, g) data.table(
  attr_nfm_feature = c("Planted woodland", "Natural regeneration")[g("type") + 1L],
  attr_neighbours_connected = c("None", "One neighbour", "Two neighbours")[g("coord") + 1L],
  attr_corridor_width = c("10 meters", "20 meters")[g("width") + 1L],
  attr_coordination_bonus = fifelse(g("coord") == 0, "£0", gbp(g("bonus"))),
  attr_annual_payment_per_100m = gbp(g("payment")))
for (z in list(list(e1, f1, "scarpa_2023_nfm_contracts"), list(e2, f2, "scarpa_2023_nfm_corridors"))) {
  d <- long(z[[1]], z[[2]])
  stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]), d[, sum(choice), .(id, task)][, all(V1 <= 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(z[[3]], ".csv")))
}
