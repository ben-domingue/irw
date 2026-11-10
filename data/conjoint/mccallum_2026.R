##Wine choice experiment with pesticide-risk information (United States and Switzerland), from the deposit
##"Data and code for 'Consumers' valuation for wine with pesticide risk information: Evidence from a cross-country experiment'"
##(McCallum, Agossadou, Siegrist, Finger & Nayga, Australian Journal of Agricultural and Resource Economics; article year taken as 2026 from the
##deposit date; no article DOI located 2026-11-10) (Zenodo doi:10.5281/zenodo.23371216, CC BY 4.0).
##Files read: data.csv (long format, 3 rows per choice set) and Code-DCE-wine-paper-AJARE.R (read as text: dummy names for the levels, the
##authors' filters, the no-buy coding).
##Usage: Rscript mccallum_2026.R <dir holding data.csv> <output dir>
##
##Two online samples, 1,587 respondents x 12 choice sets: United States (source == "US", 825 respondents) and Switzerland (source == "CH", 762).
##The authors estimate separate models per country (mxl_pref.us / mxl_pref.sw) and the "Domestic" level of the country-of-origin attribute
##means a different country in each sample, so there is ONE TABLE PER SAMPLE (not pooled): mccallum_2026_wine_us, mccallum_2026_wine_ch.
##Each choice set shows two wine alternatives (alt 1, 2) described by price (8, 16, 24 or 32), organic (yes/no), fungus-resistant grape
##variety (yes/no), country of origin (Domestic, Chile, France, Australia) and quality (Acceptable, Good, Excellent), plus a fixed
##no-buy alternative (alt 3, all attributes 0), which is the opt-out and is not a profile. Respondents were randomized between subjects
##to an information treatment (control, healthinfo, envinfo, combinedinfo) stored as trial_infotreat.
##LABELS: the deposit stores numeric codes and no questionnaire; the displayed wording is not in the deposit. Level text is taken from the
##authors' code (dummy names Domestic/Chile/France/Australia, Accept.q/Good.q/Excell.q, plot labels "Organic" and "Fungi-resistant"); for
##the two yes/no attributes the text "Organic"/"Not organic" and "Fungus-resistant"/"Not fungus-resistant" is inferred from the variable
##names. Price is the bare number: the currency and display format are not documented (the US sample is presumably dollars; the Swiss
##sample's currency is not stated). The displayed attribute text, order and wording of the question are unknown.
##Outcome: choice = Choice (1 on the chosen wine); choice sets where the no-buy alternative was chosen have choice = 0 on both wines.
##Exactly one of the three alternatives is chosen per set (verified). Wording of the question: not in the deposit.
##Authors' analysis sample: the deposit already contains only respondents with finished == 1, consent, screening and oath all 1. The authors'
##robustness analyses (code L1560) drop speeders (speeder_hinfo / einfo / combinedinfo == 1) and the attribute-non-attendance flags
##(ignore_*) mark ignored attributes; per Ben's ruling (2026-11-10) no respondent is dropped: the speeder flags are kept as cov_speeder_*,
##the trap question as cov_trap_quest (codes 1 and 3 as recorded; which code is a pass is not documented), and the reproduction rule is
##"drop rows with any cov_speeder_* == 1".
##Covariates: cov_gender (Female/Male/Other as text), cov_age (years), cov_education (educlevel text: "<bachelor degree" / ">=bachelor degree"),
##cov_household_income (hh_inc2 text; bins differ by country), cov_duration (the `duration` column as recorded; unit not documented, probably
##minutes), cov_speeder_*, cov_trap_quest. Dropped: derived scales (NEP, CFC, ANA), attribute-attendance flags, dummies, residence codes,
##state/canton codes, other attitude items. No weights; no PII (pid, source and platform fields are not read; ids are re-keyed).
##Respondent count vs paper: not checked (article not located). Restrictions: none documented (orthogonal-looking design, shares equal:
##price 4,761 sets per level per alt; levels uniform).
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "data.csv"))
stopifnot(nrow(d) == 57132, d[, uniqueN(id)] == 1587, all(d[, .N, .(id, Question)]$N == 3))
chosen <- d[, .(n = sum(Choice)), .(id, Question)]; stopifnot(all(chosen$n == 1))
d[, chosen_alt := alt[Choice == 1], .(id, Question)]
p <- d[alt %in% 1:2]
p[, `:=`(task = as.integer(Question), profile = as.integer(alt),
         attr_price = as.character(price),
         attr_organic = fifelse(organic == 1, "Organic", "Not organic"),
         attr_fungus_resistant = fifelse(fresistant == 1, "Fungus-resistant", "Not fungus-resistant"),
         attr_country_of_origin = c("Domestic", "Chile", "France", "Australia")[country],
         attr_quality = c("Acceptable", "Good", "Excellent")[quality],
         choice = as.integer(Choice))]
stopifnot(!anyNA(p$attr_country_of_origin), !anyNA(p$attr_quality), p[, sum(choice), .(id, task)][, all(V1 <= 1)])
p[, `:=`(cov_gender = fifelse(gender %in% c("Female", "Male", "Other"), tolower(gender), NA_character_),
         cov_age = fifelse(age >= 18 & age <= 100, as.integer(age), NA_integer_),
         cov_education = educlevel, cov_household_income = hh_inc2, cov_duration = duration,
         cov_speeder_hinfo = as.integer(speeder_hinfo), cov_speeder_einfo = as.integer(speeder_einfo),
         cov_speeder_combinedinfo = as.integer(speeder_combinedinfo), cov_trap_quest = as.integer(trap_quest),
         trial_infotreat = infotreat)]
nm <- c("id", "task", "profile", "choice", "attr_price", "attr_organic", "attr_fungus_resistant", "attr_country_of_origin", "attr_quality",
        grep("^cov_", names(p), value = TRUE), "trial_infotreat")
for (s in c("US", "CH")) {
  x <- p[source == s]; x[, id := as.integer(factor(id))]
  x <- x[, ..nm]; setorder(x, id, task, profile)
  cat(s, x[, uniqueN(id)], nrow(x), "\n")
  fwrite(x, file.path(out, paste0("mccallum_2026_wine_", tolower(s), ".csv")))
}
