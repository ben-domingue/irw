##Circular-product choice experiment (Swiss Environmental Panel, wave 8) from
##Brügge, C. (2024). Replication data: Circular products resonate well with diverse consumers.
##Evidence from a choice experiment in Switzerland [Data set]. Harvard Dataverse. (The article
##was not found on 2026-10-08; the deposit says it accompanies a paper under review.)
##Replication data: Harvard Dataverse doi:10.7910/DVN/YKVLTR, CC0 1.0, no restricted files.
##Files read: w8_conjoint.csv (one row per respondent x round x product, written by the
##authors' data_structuring_ce_paper.R) and w7_w8_subgroups.csv (same rows plus respondent
##covariates). data_structuring_ce_paper.R, data_analysis_ce_paper.R and summary_stats.R were
##read as text: they hold the German value labels of the panel file (not deposited), the
##authors' English recodes of every level, and the covariate labels.
##Usage: Rscript brugge_2024.R <dir holding the two csv files> <output dir>
##
##3,413 panel members (Swiss Environmental Panel wave 8, 2022, survey arm w8_surveyarm == 1)
##were randomly assigned one product type (trial_product_type: Smartphone / TV / Washing
##machine; 1,145 / 1,150 / 1,118) and chose between 2 products (source `product` 1/2 =
##profile) in 4 rounds (source `round` = task), 6 attributes. Exactly one product chosen per
##round (checked): forced choice, no opt-out. The question wording is not deposited
##(paraphrased from the variable name w8_conjoint_buy: which product would you buy).
##Attribute text: the panel's German value labels are templates that hold all three products'
##values, e.g. 'Preis: {[180 CHF] (Smartphone) // [250 CHF] (Fernseher) // [470 CHF]
##(Waschmaschine)}'; the deposit stores the authors' English recodes ('180 / 250 / 470 CHF').
##This table keeps the authors' English text but resolves price and functional duration to the
##value of the respondent's own product (Smartphone first, TV second, washing machine third
##in every template): attr_price e.g. "180 CHF", attr_functional_duration e.g. "2 years".
##attr_env_production_impact Very low / Medium / Very high ('Sehr niedrige / Mittlere / Sehr
##hohe Umweltbelastung'), attr_energy_efficiency A / C / E / G ('Energieeffizienzklasse X'),
##attr_recyclability Not recyclable / Limited recyclable / Recyclable, attr_repairability Not
##repairable at all / Repairable to a limited degree / Repairable. ONE TABLE: the product arm
##is a between-respondent randomization within one experiment and the authors pool it (main
##AMCE/MM on all respondents, by product_type in a further figure).
##Attribute order: the authors dropped the panel's per-round attribute-order variables
##(r1attr..r4attr), so order was recorded in the panel file but is not in the deposit.
##Respondents with any missing conjoint answer were dropped by the authors before deposit.
##Covariates: cov_age (2022 minus year of birth w8_q1, computed by the authors),
##cov_gender (w8_q2: 1 Female, 2 Male, 3 Other; summary_stats.R), cov_education (w7_q5, text
##from summary_stats.R: None / Obligatory schooling / Apprenticeship, vocational school,
##commercial (middle) school / Matura, vocational school-leaving certificate / Higher
##technical/vocational training (e.g. federal certificate, master's diploma) / University of
##Applied Sciences, University of Education / University, ETH / Other), cov_household_income
##(w7_q40x1, monthly bands, text from summary_stats.R), cov_left_right (w7_q26, 1-11 as stored;
##the authors cut 1-3 = left, 9-11 = right; labels not deposited).
##Dropped: the other w8/w7 attitude items (no wording deposited), all derived variables
##(env_attitudes_*, political_ideology, importance_*, prefs_*, swiss_economy, Income, Age,
##*_recoded*, ce_index, ce_category, wtp_*). PubId is the panel's public respondent id (not a
##platform id) and is kept. The authors' survey weight (w8_weights_raking, in
##sep_w8_research_weighted.RData) is not deposited.
##N: 3,413 respondents (article not available to check).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "w8_conjoint.csv"), encoding = "UTF-8")
g <- fread(file.path(raw, "w7_w8_subgroups.csv"), encoding = "UTF-8")
stopifnot(s[, .N, PubId][, all(N == 8)], s[, .N, .(PubId, round, product)][, all(N == 1)], s[, uniqueN(product_type), PubId][, all(V1 == 1)])
k <- match(s$product_type, c("Smartphone", "TV", "Washing machine")); stopifnot(!anyNA(k))
pick <- function(x, unit) { p <- strsplit(sub(paste0(" ", unit, "$"), "", x), " / ", fixed = TRUE)
  stopifnot(all(lengths(p) == 3)); paste(mapply(function(v, i) v[i], p, k), unit) }
d <- data.table(id = as.integer(s$PubId), task = as.integer(s$round), profile = as.integer(s$product), choice = as.integer(s$choice),
                attr_price = pick(s$Price, "CHF"), attr_functional_duration = pick(s[["Functional duration"]], "years"),
                attr_env_production_impact = s[["Env. production impact"]], attr_energy_efficiency = s[["Energy efficiency"]],
                attr_recyclability = s$Recyclability, attr_repairability = s$Repairability, trial_product_type = s$product_type)
stopifnot(!anyNA(d), all(nzchar(as.matrix(d[, .SD, .SDcols = patterns("^attr_")]))))
r <- g[!duplicated(PubId)]
stopifnot(all(r$w8_q2 %in% 1:3), all(r$Education %in% c(1:8, NA)), all(r$w7_q40x1 %in% c(1:10, NA)))
edu <- c("None", "Obligatory schooling", "Apprenticeship, vocational school, commercial (middle) school",
         "Matura, vocational school-leaving certificate",
         "Higher technical/vocational training (e.g. federal certificate, master’s diploma)",
         "University of Applied Sciences, University of Education", "University, ETH", "Other")
inc <- c("Under 2’000 CHF", "2001 to 4000 CHF", "4001 to 6000 CHF", "6001 to 8000 CHF", "8001 to 10‘000 CHF",
         "10’001 to 12‘000 CHF", "12’001 to 14‘000 CHF", "14’001 to 16’000 CHF", "16’001 to 18’000 CHF", "Above 18’000 CHF")
cv <- r[, .(id = as.integer(PubId), cov_age = as.integer(age), cov_gender = c("female", "male", "other")[w8_q2],
            cov_education = edu[Education], cov_household_income = inc[w7_q40x1], cov_left_right = as.integer(w7_q26))]
d <- merge(d, cv, by = "id", all.x = TRUE)
stopifnot(nrow(d) == nrow(s), d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "brugge_2024_circular_products.csv"))
