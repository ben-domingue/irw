##IMF-loan conditionality conjoint from
##Heinzel, M., Kern, A., Metinsoy, S., & Reinsberg, B. (2025). Public support for green,
##inclusive, and resilient growth conditionality in International Monetary Fund bailouts.
##International Studies Quarterly, 69(2), sqaf018. https://doi.org/10.1093/isq/sqaf018
##Replication data: Harvard Dataverse doi:10.7910/DVN/6WGMNJ, CC0 1.0, no restricted files,
##no terms. File read: IMF_survey_experiment.dta (Dataverse "original format" download).
##Design and wording from the article (section on the survey experiment, footnote 6) and the
##authors' do-file Heinzel_Metinosy_Kern_Reinsberg_ISQ24.do (read as text). The deposit also
##bundles WVS_TimeSeries_4_0.dta (a re-host of the World Values Survey, not used here) and an
##IMF Monitor conditions file (not used).
##Usage: Rscript heinzel_2025.R <raw dir> <output dir>
##
##YouGov online survey, April 2023, Kenya (539), Argentina (1,103), Pakistan (1,001): 2,643
##respondents in the file; the article reports 2,694 respondents and 5,388 profiles (51 fewer
##here; not resolved). Questionnaire in English (Kenya, Pakistan) and Spanish (Argentina);
##only the English attribute wording is available (article). The authors pool the three
##countries with country fixed effects, and the attribute text is shared, so this is one
##table with cov_country.
##One task: "Let's assume your country is in financial trouble. ... The table below lists two
##hypothetical IMF loans for your country." A table headed "Requires your country to:" with
##columns Loan A and Loan B and a Yes/No cell for each of 8 conditions. profile = the source
##`loan` column (_1 = Loan A = 1, _2 = Loan B = 2; the mapping of _1 to A is inferred from
##the order). Attributes (row wording from the article; the do-file's figure labels shorten
##"Remove taxes on imports" to "Reduce tariffs"); each level is "Yes" or "No" as displayed:
##  attr_open_foreign_investors  "Open up to foreign investors"            (invest)
##  attr_remove_import_taxes     "Remove taxes on imports"                 (tariff)
##  attr_reduce_debt             "Reduce its debt"                         (debt)
##  attr_fight_corruption        "Fight corruption"                        (corrupt)
##  attr_anti_poverty            "Introduce more anti-poverty policies"    (poverty)
##  attr_privatize_soes          "Privatize state-owned companies"         (privatize)
##  attr_fight_climate_change    "Fight climate change"                    (climate)
##  attr_gender_equality         "Improve gender equality"                 (genderequ)
##(value labels 1 = Yes, 2 = No). Randomization scheme not stated; row order not stated.
##No forced choice: each loan is rated.
##  rating_support = support for taking the loan, "on a scale from 1 (strongly oppose) to 6
##                   (strongly support)" (value labels 1 Strongly oppose .. 6 Strongly support).
##  rating_taxes   = willingness to pay more taxes if the country took the loan, "on a scale
##                   from 1 (strongly unwilling) to 6 (strongly willing)" (article fn. 6).
##  rating_cuts    = willingness to endure spending cuts, same 1-6 unwilling..willing labels
##                   (wording not given in the article; value labels).
##Higher = more supportive / willing. Stored as in the source.
##Covariates: cov_country (qcountry: Kenya KE, Argentina AR, Pakistan PK); cov_survey_weight =
##weight (YouGov weights for age, gender, region, education; used in all the authors' models);
##cov_gender (gender_all value labels Male/Female); cov_age_group (age_grp_all label text);
##cov_education = the country's own education question as answer text (DEM4_Ken,
##education_Ar, education_Pak value labels; 42 Pakistani respondents' rows have none -> NA);
##cov_left_right = q4 codes (1 Far left .. 6 Far right; 394 rows NA); cov_region = region
##answer text from the value labels (region_Ken, GeoPC_Region1_Ar, region_Pak);
##cov_duration_sec = endtime - starttime (whole questionnaire).
##Dropped: RecordNo (panel record number), start/end timestamps, income and employment items,
##marital status, natgroup_Pak (its value labels are a Gulf-states template: Emirati, Saudi, ...,
##not Pakistani categories), DEM5_Ken (derived Low/Medium/High), LOC_TYPE_Ken, count_obs*.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "IMF_survey_experiment.dta"))
z <- as.data.table(zap_labels(k))
stopifnot(z[, .N, id][, all(N == 2L)], all(z$loan %in% c("_1", "_2")), z[, uniqueN(loan), id][, all(V1 == 2)])
yn <- function(v) { stopifnot(all(z[[v]] %in% 1:2)); c("Yes", "No")[z[[v]]] }
d <- data.table(id = as.integer(z$id), task = 1L, profile = as.integer(sub("_", "", z$loan)),
  rating_support = as.integer(z$support), rating_taxes = as.integer(z$taxes), rating_cuts = as.integer(z$cuts),
  attr_open_foreign_investors = yn("invest"), attr_remove_import_taxes = yn("tariff"),
  attr_reduce_debt = yn("debt"), attr_fight_corruption = yn("corrupt"), attr_anti_poverty = yn("poverty"),
  attr_privatize_soes = yn("privatize"), attr_fight_climate_change = yn("climate"),
  attr_gender_equality = yn("genderequ"))
stopifnot(all(unlist(d[, .(rating_support, rating_taxes, rating_cuts)]) %in% 1:6))
txt <- function(v) { x <- as.character(as_factor(k[[v]], levels = "labels")); x[is.na(k[[v]])] <- NA; x }
stopifnot(all(z$qcountry %in% 1:3), all(z$gender_all %in% 1:2))
edu <- fcase(z$qcountry == 1, txt("DEM4_Ken"), z$qcountry == 2, txt("education_Ar"), z$qcountry == 3, txt("education_Pak"))
reg <- fcase(z$qcountry == 1, txt("region_Ken"), z$qcountry == 2, txt("GeoPC_Region1_Ar"), z$qcountry == 3, txt("region_Pak"))
dur <- as.numeric(difftime(as.POSIXct(z$endtime, tz = "UTC"), as.POSIXct(z$starttime, tz = "UTC"), units = "secs"))
d[, `:=`(cov_country = c("KE", "AR", "PK")[z$qcountry], cov_gender = c("male", "female")[z$gender_all],
         cov_age_group = txt("age_grp_all"), cov_education = edu, cov_left_right = as.integer(z$q4),
         cov_region = reg, cov_duration_sec = dur, cov_survey_weight = as.numeric(z$weight))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "heinzel_2025_imf_conditionality.csv"))
