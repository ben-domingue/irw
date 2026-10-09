##Fossil-fuel phase-out policy-package conjoints (Germany: heating and transport) from
##Tröndle, T., Annaheim, J., Hoppe, J., Hanger-Kopp, S., & Patt, A. (2023). Public
##preferences for phasing-out fossil fuels in the German building and transport sectors.
##Environmental Research Communications, 5(8). https://doi.org/10.1088/2515-7620/acec39
##Data: Zenodo record 7803031, doi:10.5281/zenodo.7803031, CC BY 4.0. File read: surveydata.csv
##(Qualtrics export). Read as text, not run: the authors' workflow, Zenodo 8171706 (MIT licence),
##scripts/preprocess/preprocess.R (variable meanings, level translations, covariate codes) and
##report/supplementary.md (questionnaire in English translation, task examples, Notes S1-S3).
##Usage: Rscript trondle_2023.R <raw dir> <output dir>
##
##German online panel survey (Qualtrics, UserLanguage DE; fielded February-March 2022 per the
##StartDate stamps). Respondents saw two paired-conjoint blocks of 5 tasks, heating (choice1-5)
##and private transport (choice6-10), sector order randomized (trial_first_sector, source
##`First`). Each policy package has 4 attributes in a fixed row order (phase-out year,
##purchase measure, use measure, supporting measure); level text is the German displayed
##text as stored in the export (authors' English translations in preprocess.R).
##TWO TABLES, trondle_2023_phaseout_heating and trondle_2023_phaseout_transport: the purchase,
##use and support levels differ between sectors, and the authors analyse each sector separately.
##Outcomes (supplementary Note S1-S3, same in both sectors):
##  choice: "If you had to choose: Which package of measures [framing text] would you rather
##    accept?" Policy package 1 / 2, forced (instructions: "If you do not fully endorse any of the
##    packages, choose the one you would rather adopt"). Source `<k>_pref_h/_t`.
##  rating: "To what extent are you in support or opposition of the respective package of
##    measures?" 1 = Opposed, 2 = Rather opposed, 3 = Neither nor, 4 = Rather support, 5 = Support
##    (source `<k>_support_<s>_1/2`; the authors' preprocess.R codes 4-5 as support). Raw.
##trial_framing: between-subject framing before the experiments and inside the question
##("Phase-out" = "zum Ausstieg aus fossilen Technologien", "Renewables" = "zur Foerderung
##klimafreundlicher Alternativen"; source `Framing`, labels from preprocess.R).
##Kept: response_type == "complete" (as the authors' preprocess.R), 1,874 respondents. The
##supplementary figures report n = 1,777; the cause of the gap is not documented (the workflow
##config names a file surveydata-2023-07-21.csv; the deposit's file may be another export).
##Dropped: tasks whose attribute cells are empty in the export (4 per table; level not saved) or
##that have no choice; return_tic (a hashed panel return token: a platform ID), Qualtrics
##timing/meta columns, the derived Conjoint_Text and display-order (FL_*_DO) columns.
##Covariates (codes -> text from the authors' preprocess.R recodes, checked against the
##questionnaire in supplementary.md): cov_age_group ("18 - 29 years" .. "older than 60 years");
##cov_gender (1 male, 2 female, 3 "diverse" -> other); cov_education (preprocess.R labels, German
##school names kept); cov_party_id ("Which party best represents your political views?"; "None of
##these parties" kept); cov_income (monthly net household income band; "No indication" -> NA);
##cov_town_size; cov_n_adults, cov_n_children (typed numbers as entered); cov_cars_diesel/
##petrol/hybrid/plugin/ev/other (counts as stored, NA = not answered); cov_car_days;
##cov_heating_source (7 = "don't know", per the questionnaire order); cov_building_type;
##cov_tenure; cov_heating_influence; cov_emission_share_transport / _heating (estimated % of
##German CO2 emissions, as typed); cov_climate_<1-6> (1 Disagree .. 5 Agree; items: happening,
##human-caused, affects me, felt today, climate neutral by 2050, phase out fossil fuels);
##cov_responsibility_<gov/individuals/companies> (1 Not responsible .. 5 Responsible);
##cov_trust_<gov/individuals/companies> (1 Do not trust .. 5 Trust); cov_duration_sec (whole
##survey, Qualtrics Duration). No survey weight is deposited.
##Dropped in practice: 4 respondents whose 5 tasks per sector are all empty (1,870 kept).
##Spot check: heating choice AMCEs (lm, SEs clustered by id) are within 0.01 of the authors'
##published amce-choice-heat.csv (Zenodo 8171679), e.g. 0.5 ct/l fuel tax -0.132 vs -0.135,
##subsidies 0.199 vs 0.206, phase-out 2050 -0.064 vs -0.065; the small gaps fit the larger N.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "surveydata.csv"), encoding = "UTF-8", colClasses = "character")
x <- x[response_type == "complete"]
x[, id := seq_len(.N)]
n <- function(v) as.integer(x[[v]])
lk <- function(v, codes, txt) { z <- n(v); stopifnot(all(is.na(z) | z %in% codes)); txt[match(z, codes)] }
cov <- data.table(id = x$id,
  trial_framing = c(P = "Phase-out", R = "Renewables")[x$Framing],
  trial_first_sector = c(H = "Heating", T = "Transport")[x$First],
  cov_age_group = lk("age", 2:6, c("18 - 29 years", "30 - 39 years", "40 - 49 years", "50 - 59 years", "older than 60 years")),
  cov_gender = lk("gender", 1:3, c("male", "female", "other")),
  cov_education = lk("education", c(1:4, 6:8), c("No school diploma", "Volks- or Hauptschulabschluss", "Mittlere Reife", "Abitur",
                                                  "Fachhochschulabschluss", "University degree", "Other degree")),
  cov_party_id = lk("party_pref", 1:7, c("CDU/CSU", "SPD", "FDP", "Die Linke", "Die Grünen", "AfD", "None of these parties")),
  cov_income = lk("income", 1:10, c("< 500 Euro", "500 - 1'000 Euro", "1'000 - 2'000 Euro", "2'000 - 3'000 Euro", "3'000 - 4'000 Euro",
                                    "4'000 - 5'000 Euro", "5'000 - 7'500 Euro", "7'500 - 10'000 Euro", "> 10'000 Euro", NA)),
  cov_town_size = lk("residential_area", 1:7, c("<2'000 inhabitants", "2'000 - 5'000 inhabitants", "5'000 - 20'000 inhabitants",
                                                "20'000 - 50'000 inhabitants", "50'000 - 100'000 inhabitants",
                                                "100'000 - 500'000 inhabitants", "> 500'000 inhabitants")),
  cov_n_adults = n("number_adults"), cov_n_children = n("number_children"),
  cov_cars_diesel = n("number_diesel"), cov_cars_petrol = n("number_gas"), cov_cars_hybrid = n("number_hybrid"),
  cov_cars_plugin = n("number_plugin"), cov_cars_ev = n("number_EV"), cov_cars_other = n("number_other"),
  cov_car_days = lk("car_days", 1:5, c("Never/ exceptionally", "1 - 2 days", "3 - 4 days", "5 - 6 days", "Every day")),
  cov_heating_source = lk("source_h", 1:7, c("Oil", "Gas", "Wood", "Heat pump", "District heating", "Other", "Don't know")),
  cov_building_type = lk("building_type", 1:3, c("New building", "Modernized building", "Old building")),
  cov_tenure = lk("ownership", 1:2, c("Owning", "Renting")),
  cov_heating_influence = lk("influence_h", 1:2, c("Yes", "No")),
  cov_emission_share_transport = n("relevance_t"), cov_emission_share_heating = n("relevance_h"),
  cov_climate_1 = n("climate_change_1"), cov_climate_2 = n("climate_change_2"), cov_climate_3 = n("climate_change_3"),
  cov_climate_4 = n("climate_change_4"), cov_climate_5 = n("climate_change_5"), cov_climate_6 = n("climate_change_6"),
  cov_responsibility_gov = n("responsibility_1"), cov_responsibility_individuals = n("responsibility_2"),
  cov_responsibility_companies = n("responsibility_3"),
  cov_trust_gov = n("trust_1"), cov_trust_individuals = n("trust_2"), cov_trust_companies = n("trust_3"),
  cov_duration_sec = n("Duration (in seconds)"))
stopifnot(!anyNA(cov$trial_framing), !anyNA(cov$trial_first_sector))
build <- function(s, ks) {
  d <- rbindlist(lapply(seq_along(ks), function(t) {
    k <- ks[t]; q <- k - (s == "t") * 5L + 1L   # pref/support columns are numbered 2-6 within sector
    pr <- x[[paste0(q, "_pref_", s)]]
    rbindlist(lapply(1:2, function(p) data.table(id = x$id, task = t, profile = p,
      choice = fifelse(pr %in% c("1", "2"), as.integer(pr == as.character(p)), NA_integer_),
      rating = as.integer(x[[paste0(q, "_support_", s, "_", p)]]),
      attr_phaseout_year = x[[paste0("choice", k, "_", s, "timing", p)]],
      attr_purchase = x[[paste0("choice", k, "_", s, "purchase", p)]],
      attr_use = x[[paste0("choice", k, "_", s, "use", p)]],
      attr_support = x[[paste0("choice", k, "_", s, "compensation", p)]])))
  }))
  bad <- d[, .(b = any(attr_phaseout_year == "" | attr_purchase == "" | attr_use == "" | attr_support == "") | anyNA(choice)), .(id, task)][b == TRUE]
  d <- d[!bad, on = .(id, task)]
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% c(1:5, NA)))
  d <- merge(d, cov, by = "id")
  setorder(d, id, task, profile)
  list(d = d, dropped = nrow(bad))
}
h <- build("h", 1:5); t <- build("t", 6:10)
cat("dropped tasks heating", h$dropped, "transport", t$dropped, "\n")
fwrite(h$d, file.path(out, "trondle_2023_phaseout_heating.csv"))
fwrite(t$d, file.path(out, "trondle_2023_phaseout_transport.csv"))
