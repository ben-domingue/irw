##E-bike policy-package conjoint (Netherlands) from
##Pickering, S. (2026). Replication data for: Public opinion towards e-bike policy packages: A
##conjoint experiment in the Netherlands [Data set]. Harvard Dataverse.
##https://doi.org/10.7910/DVN/K4D9GP (deposited 2026-05-19; no article found in Crossref, so the
##deposit is cited).
##Replication data: Harvard Dataverse doi:10.7910/DVN/K4D9GP, CC BY 4.0, no restricted files, no terms.
##Files read: replication_data.csv (Dataverse original of replication_data.tab). Also read as text:
##replication_code.r (factor levels, outcome labels and covariate value labels).
##Usage: Rscript pickering_2026.R <raw dir> <output dir>
##
##1,309 Dutch respondents (panel not named in the deposit), 3 tasks (choice_task) of 2 policy
##packages (option A = profile 1, B = profile 2), 5 attributes. Four questions about the same pair,
##each a forced pick of one package (exactly one chosen per task on every outcome; no opt-out). Names
##follow the authors' outcome labels (replication_code.r); the question wording is not in the deposit:
##  choice                     preferred_standard            "Preferred standard"
##  choice_increase_use        more_likely_increase_use      "More likely to increase e-bike use"
##  choice_more_restrictive    more_restrictive              "More restrictive for the individual"
##  choice_more_intervention   more_government_intervention  "Requires more government intervention"
##Attributes (text as stored, in English; the authors' level order): who (Registration or licence
##required / No registration or licence required), where (Mixed traffic 50 km/h / Shared
##carriageway 30 km/h / Physically separated cycle paths), enforcement (No enforcement / Police
##checks, low fines / Speed checks, moderate fines / Camera surveillance, high fines), access (No
##subsidies / Reduced price for low income households / Interest-free loans for switchers), safety
##(Helmet strongly recommended / Helmet mandatory / No helmet obligation). Respondents in the
##Netherlands probably saw Dutch; the displayed language is not documented. No source documents
##restrictions, level probabilities or attribute order; the crosstabs show no missing combinations.
##Dropped: the *_code duplicates of the attributes, university (derived from education),
##leftRight_refused / libTrad_refused (flags whose "prefer not to say" is NA in the score).
##Covariates (labels from replication_code.r unless stored as text): cov_gender (woman 0 Men -> male,
##1 Women -> female), cov_age_group (ageCat_label), cov_region (East/North/South/West),
##cov_education (education_label Low/Medium/High; the source's education measure as labelled in the
##data), cov_income (incomeCat_label; NA = "Not reported / don't know" in the authors' table),
##cov_commute ("Primary travel mode"), cov_own_car ("Household car access"), cov_ebike_frequency,
##cov_children, as label text; numeric as stored: cov_trust_general (1-7), cov_risk (0-10),
##cov_comparative_household, cov_retro_household, cov_retro_national (1-5), cov_left_right (0-10,
##NA = prefer not to say), cov_lib_trad (0-10 open/liberal to traditional/national),
##cov_trust_government, cov_trust_parliament, cov_trust_municipal, cov_trust_police (1-7).
##cov_survey_weight = weight (the authors' default analysis is unweighted, use_weights <- FALSE).
##N: 1,309 respondents; no article to compare.
##Spot check: the authors' unweighted AMCE model (lm, SEs clustered by respondent) on choice runs on
##this table (e.g. No enforcement vs camera surveillance -0.097, SE 0.017); no published numbers to compare.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "replication_data.orig"))
stopifnot(all(x$option %in% c("A", "B")), x[, .N, .(respondent_id, choice_task)][, all(N == 2)])
d <- data.table(id = as.integer(x$respondent_id), task = as.integer(x$choice_task), profile = match(x$option, c("A", "B")),
                choice = x$preferred_standard, choice_increase_use = x$more_likely_increase_use,
                choice_more_restrictive = x$more_restrictive, choice_more_intervention = x$more_government_intervention,
                attr_who = x$who, attr_where = x$where, attr_enforcement = x$enforcement, attr_access = x$access, attr_safety = x$safety)
for (o in grep("^choice", names(d), value = TRUE)) stopifnot(d[, sum(get(o)), .(id, task)][, all(V1 == 1)])
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(nzchar(d[[v]])))
lv <- function(v, l) { v <- as.character(v); stopifnot(all(v %in% c(names(l), NA))); unname(l[v]) }
stopifnot(all(x$woman %in% 0:1))
d[, cov_gender := c("male", "female")[x$woman + 1L]]
d[, `:=`(cov_age_group = x$ageCat_label, cov_region = x$region, cov_education = x$education_label,
         cov_income = fifelse(x$incomeCat_label == "", NA_character_, x$incomeCat_label))]
d[, cov_commute := lv(x$commute, c("1" = "Not working/studying outside home", "2" = "Walking", "3" = "Regular bicycle",
                                     "4" = "E-bike or speed pedelec", "5" = "Car as driver", "6" = "Car as passenger",
                                     "7" = "Public transport", "8" = "Moped or scooter", "9" = "Other"))]
d[, cov_own_car := lv(x$ownCar, c("1" = "Household car, respondent usually drives",
                                  "2" = "Household car, respondent usually does not drive", "3" = "No household car"))]
d[, cov_ebike_frequency := lv(x$ebikeFrequency, c("1" = "Never", "2" = "Less than once per month", "3" = "1-3 times per month",
                                                  "4" = "1-3 times per week", "5" = "4-6 times per week", "6" = "Almost every day"))]
d[, cov_children := lv(x$children, c("1" = "No children in household", "2" = "At least one child under 12",
                                     "3" = "Only children aged 12 or older"))]
d[, `:=`(cov_trust_general = x$trustGeneral, cov_risk = x$risk_score, cov_comparative_household = x$comparativeHousehold,
         cov_retro_household = x$retroHousehold, cov_retro_national = x$retroNational, cov_left_right = x$leftRight_score,
         cov_lib_trad = x$libTrad_score, cov_trust_government = x$trustInstitutions_1, cov_trust_parliament = x$trustInstitutions_2,
         cov_trust_municipal = x$trustInstitutions_3, cov_trust_police = x$trustInstitutions_4, cov_survey_weight = x$weight)]
stopifnot(all(is.na(x$leftRight_score) == (x$leftRight_refused == 1)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pickering_2026_ebike_policy.csv"))
cat(nrow(d), uniqueN(d$id), "\n")
