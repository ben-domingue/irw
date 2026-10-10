##RADIANT underutilised-crop discrete choice experiments (six DCEs) from
##Chen, J., Mzek, T., & Piras, S. (2025). Dataset of choice experiment surveys assessing consumers'
##and farmers' preferences for five underutilised crops in different European countries [Data set].
##Zenodo. https://doi.org/10.5281/zenodo.15420092 (H2020 project RADIANT, Task 5.3; no journal
##article; related project reports 10.5281/zenodo.7948698, 15574862, 14929731 not read)
##Licence: CC BY 4.0 (Zenodo record licence field); no README with other terms.
##Files read: COBGID.xlsx, COITYP.xlsx, COITPR.xlsx, COESHT.xlsx, COSCBB.xlsx, FAITYP.xlsx, sheets
##"choices" (COESHT: "choice") and "survey"; each file's "metadata" sheet is the codebook for every
##level text and covariate code used below.
##Usage: Rscript chen_2025.R <raw dir> <output dir>
##
##SIX TABLES, one per file: each is a separate DCE with its own product, attributes, country and
##population (the deposit and its metadata keep them apart):
##  chen_2025_ideal_tomato_bg      COBGID consumers, Bulgaria, IDEAL tomato, Oct 2024, n = 336
##  chen_2025_pasta_pea_einkorn_it COITYP consumers, Italy, pasta with yellow pea / einkorn, Jan-Feb 2025, n = 346
##  chen_2025_parmigiano_it        COITPR consumers, Italy, Parmigiano Reggiano (fodder), Feb-Mar 2025, n = 340
##  chen_2025_hanging_tomato_es    COESHT consumers, Spain, hanging tomatoes, Jan 2025, n = 345
##  chen_2025_bere_barley_scot     COSCBB consumers, Scotland, Bere-barley shortbread, Feb-Mar 2024, n = 299
##  chen_2025_legume_farmers_it    FAITYP farmers, Italy, legume rotation plans, Nov 2024, n = 331
##Consumers: online Qualtrics panels (TGM Research; Scotland: Prolific), quota-representative by
##gender and age. Farmers: Qualtrics via IPSOS Europe.
##Design (metadata sheets): fixed blocked design, 36 choice cards in 6 sets of 6 (set k = cards
##6k-5..6k), one set randomly assigned per respondent (trial_choice_set, trial_choice_card). Each
##card had Option 1 (profile 1), Option 2 (profile 2) and "Neither" (option 3, no attributes): the
##Neither alternative is not a profile; choosing it gives choice = 0 on both profiles (opt-out).
##choice = "A dummy identifying the option selected by the respondent in that choice card" (one
##option per card). The question wording itself is not in the deposit (paraphrase).
##task = order of the card in the deposit's rows (ascending card id within the set); the order in
##which cards were displayed is not documented, so task is inferred.
##Farmers only: choice_forced = choice_nosq, "the preferred option if the respondent had selected
##neither in a first instance" (dual response; NA on cards where an option was chosen).
##trial_treated (respondent-level arm): consumers, 1 = "treated by providing them the information
##about underutilised crops"; farmers, 1 = took part in the public good game before the choices.
##Level text = the codebook modality labels (English; e.g. Bere "No lebel" kept as spelled). The
##surveys were fielded in BG, IT, ES and Scotland; the display language is not stated, so the
##English labels may be translations. Prices as in the modalities ("€1.50", "2.00 лв", "£3.50").
##Restrictions: COITPR states one (if the "Parmigiano Reggiano di Montagna" label is present the
##quality selection happens at 20 months minimum): label Yes never occurs with 12 months ageing.
##Other files: none documented; level counts are unequal in several attributes (fixed design).
##Covariates (codebook): cov_gender (1 Female, 2 Male, 3 self-describe/other -> other, -99 -> NA),
##cov_age_group (age band text), cov_education (text; categories differ by country, as in the
##codebook), cov_income_range (text; "Prefer not to say" -> NA), cov_income_perc ("How would you
##assess your household income?" text), cov_duration_sec (survey duration_seconds);
##farmers also cov_highqual_response (the authors' flag for responses passing their restrictive
##checks; 0/1 as stored) and cov_risk_attitude (as stored).
##Dropped: postcodes (BG 4-digit, Scottish outward codes), municipality and province of residence
##(PII / fine geography), free text, timing/click data, all attitude batteries, the PGG sheet.
##Respondent ids are the deposit's own 1..n numbers. No survey weight in the deposit.
##Counts: as the metadata sheets state; COSCBB respondent 279 answered only 2 cards (kept, per the
##metadata). The Zenodo description says 331 farmers of whom 220 are high-quality responses.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
L <- function(x, map) { k <- as.character(x); stopifnot(all(k %in% names(map))); unname(map[k]) }
eur <- function(v) setNames(sprintf("€%.2f", v), as.character(v))
age7 <- c("1" = "18-24 years", "2" = "25-34 years", "3" = "35-44 years", "4" = "45-54 years", "5" = "55-64 years",
          "6" = "65-74 years", "7" = "75 years and over")
edu_a <- c("0" = "No educational qualification", "1" = "Primary school", "2" = "Secondary school",
           "3" = "Further education (College)", "4" = "Undergraduate", "5" = "Postgraduate")
edu_it <- c("0" = "No educational qualification", "1" = "Primary school", "2" = "Middle school", "3" = "Professional diploma",
            "4" = "Secondary school diploma", "5" = "Bachelor's degree", "6" = "Master's degree", "7" = "Doctorate")
perc <- c("1" = "We cannot make ends met", "2" = "We face serious economic difficulties", "3" = "We sometimes face difficulties",
          "4" = "We have about what we need", "5" = "We have more than we need", "6" = "We have much more than we need")
inc_it <- c("1" = "Up to €750", "2" = "€751 up to €1000", "3" = "€1251 up to €1500", "4" = "€1501 up to €2000",
            "5" = "€2001 up to €2500", "6" = "€2501 up to €3000", "7" = "€3001 up to €4000", "8" = "€4001 up to €5000",
            "9" = "€5001 up to €7500", "10" = "€7501 or more")
spec <- list(
  COBGID = list(table = "chen_2025_ideal_tomato_bg", sheet = "choices", edu = edu_a,
    inc = c("1" = "Up to 500 лв.", "2" = "500 лв. to 800 лв.", "3" = "800 лв. to 1,200 лв.", "4" = "1,200 лв. to 1,600 лв.",
            "5" = "1,600 лв. to 2,000 лв.", "6" = "2,000 лв. to 2,500 лв.", "7" = "2,500 лв. to 3,000 лв.",
            "8" = "3,000 лв. to 4,000 лв.", "9" = "4,000 лв. to 5,000 лв.", "10" = "5,000 лв. or more"),
    attr = list(variety = list("variety", c("1" = "IDEAL", "2" = "Hybrid between IDEAL and commercial", "3" = "Commercial")),
                organic = list("organic", c("1" = "No", "2" = "Yes")),
                label = list("label", c("1" = "Without label", "2" = "With label")),
                nutr = list("nutritional_value", c("1" = "Low", "2" = "Medium", "3" = "High")),
                access = list("access", c("1" = "Directly from the farmer", "2" = "Local open air market", "3" = "Large supermarket")),
                prox = list("place_of_production", c("1" = "Locally (your province)", "2" = "Elsewhere in Bulgaria (not locally)", "3" = "Outside Bulgaria")),
                cost = list("cost_per_kg", setNames(sprintf("%d.00 лв", 2:7), 2:7)))),
  COITYP = list(table = "chen_2025_pasta_pea_einkorn_it", sheet = "choices", edu = edu_it, inc = inc_it,
    attr = list(ingr1 = list("first_ingredient", c("1" = "Durum wheat", "2" = "Einkorn wheat")),
                ingr2 = list("second_ingredient", c("1" = "Eggs", "2" = "Yellow pea")),
                nutr = list("nutritional_value", c("1" = "Low", "2" = "Medium", "3" = "High")),
                label = list("label", c("1" = "No", "2" = "Yes")),
                envir = list("environmental_impact", c("1" = "Negative", "2" = "Neutral", "3" = "Positive")),
                place = list("place_of_production", c("1" = "Locally (your province)", "2" = "Elsewhere in Italy", "3" = "Outside Italy")),
                price = list("price_250g", eur(c(0.5, 1, 1.5, 2, 2.5, 3))))),
  COITPR = list(table = "chen_2025_parmigiano_it", sheet = "choices", edu = edu_it, inc = inc_it,
    attr = list(feed = list("feed", c("1" = "Alfalfa", "2" = "Mixture of gramineous plants", "3" = "Mixture with leguminous plants")),
                label = list("label_montagna", c("1" = "No (label not present)", "2" = "Yes (label present)")),
                ageing = list("ageing", c("1" = "12 months", "2" = "24 months", "3" = "36 months or more")),
                place = list("purchasing_place", c("1" = "Supermarket", "2" = "From the producer (cheese factory)")),
                envir = list("environmental_impact", c("1" = "CO2 not compensated", "2" = "CO2 compensated")),
                price = list("cost_per_kg", eur(seq(15, 30, 3))))),
  COESHT = list(table = "chen_2025_hanging_tomato_es", sheet = "choice", edu = edu_a,
    inc = c("1" = "Up to 530€", "2" = "531€ up to 1.000€", "3" = "1.001€ up to 1.250€", "4" = "1.251€ up to 1.400€",
            "5" = "1.401€ up to 1.600€", "6" = "1.601€ up to 1.800", "7" = "1.801€ up to 2.100€", "8" = "2.101€ up to 2.500€",
            "9" = "2.501€ up to 3.200€", "10" = "3.200€ or more"),
    attr = list(variety = list("variety", c("1" = "Underutilised variety", "2" = "Commercial variety")),
                cultur = list("cultural_value", c("1" = "Without cultural value", "2" = "With cultural value")),
                access = list("access", c("1" = "Short food supply chain", "2" = "Speciality food shop", "3" = "Supermarket")),
                label = list("label", c("1" = "Without label", "2" = "With label")),
                place = list("place_of_production", c("1" = "Locally (your province)", "2" = "Elsewhere in Spain", "3" = "Outside Spain")),
                cost = list("cost_per_kg", eur(c(1.5, 3.5, 5.5, 7.5, 9.5, 11.5))))),
  COSCBB = list(table = "chen_2025_bere_barley_scot", sheet = "choices", edu = edu_a,
    inc = c("1" = "Up to £900", "2" = "£901 up to £1250", "3" = "£1251 up to £1600", "4" = "£1601 up to £2000",
            "5" = "£2001 up to £2400", "6" = "£2401 up to £3000", "7" = "£3001 up to £3600", "8" = "£3601 up to £4400",
            "9" = "£4401 up to £5900", "10" = "£5901 or more"),
    attr = list(ingr = list("ingredient", c("1" = "Bere flour", "2" = "No bere flour")),
                nutr = list("nutritional_value", c("1" = "Low", "2" = "Medium", "3" = "High")),
                label = list("label", c("1" = "No lebel", "2" = "Label")),
                access = list("access", c("1" = "Short food supply chain", "2" = "Speciality food shop", "3" = "Commercial grocery shop")),
                prox = list("place_of_production", c("1" = "Locally (neighbouring region)", "2" = "Elsewhere in Scotland", "3" = "Outside Scotland")),
                cost = list("cost_per_pack", setNames(sprintf("£%.2f", c(1, 3.5, 6, 8.5, 11, 13.5)), c(1, 3.5, 6, 8.5, 11, 13.5))))),
  FAITYP = list(table = "chen_2025_legume_farmers_it", sheet = "choices",
    edu = c("0" = "No educational qualification", "1" = "Primary education", "2" = "Middle school", "3" = "Professional diploma",
            "4" = "Secondary school diploma", "5" = "Bachelor’s degree", "6" = "Master’s degree", "7" = "Doctorate"),
    inc = c(inc_it[1:2], "3" = "€1,251 up to €1,500", "4" = "€1,501 up to €2,000", "5" = "€2,001 up to €2,500",
            "6" = "€2,501 up to €3,000", "7" = "€3,001 up to €4,000", "8" = "€4,001 up to €5,000", "9" = "€5,001 up to €7,500",
            "10" = "€7,501 or more"),
    attr = list(legume = list("legume", c("1" = "Green pea", "2" = "Yellow pea", "3" = "Chickpea", "4" = "Soybean")),
                percent = list("percent_cereal_land", setNames(paste0(seq(15, 90, 15), "%"), seq(15, 90, 15))),
                sales = list("sales_agreement", c("1" = "None", "2" = "Informal agreement", "3" = "Formal contract")),
                conserv = list("conservation_agriculture", c("1" = "No conservation agriculture",
                  "2" = "Conservation agriculture without free technical assistance", "3" = "Conservation agriculture with free technical assistance")),
                revenue = list("return_per_hectare", setNames(c("€900", "€1,100", "€1,300", "€1,500", "€1,700", "€1,900"), seq(900, 1900, 200))))))
for (f in names(spec)) {
  sp <- spec[[f]]; path <- file.path(raw, paste0(f, ".xlsx"))
  ch <- as.data.table(read_excel(path, sp$sheet)); sv <- as.data.table(read_excel(path, "survey"))
  if (f == "FAITYP") ch[, percent := round(percent)]
  stopifnot(ch[, .(sum(choice), .N), .(unique_id, choice_card)][, all(V1 == 1 & N == 3)],
            ch[, all(option == rep(1:3, .N / 3))], ch[, all(index == seq_len(.N)), unique_id][, all(V1)])
  ch[, task := match(choice_card, unique(choice_card)), unique_id]
  p <- ch[option %in% 1:2]
  d <- data.table(id = as.integer(p$unique_id), task = p$task, profile = as.integer(p$option), choice = as.integer(p$choice))
  if (f == "FAITYP") {
    stopifnot(p[!is.na(choice_nosq), all(choice == 0)], p[!is.na(choice_nosq), sum(choice_nosq), .(unique_id, task)][, all(V1 == 1)])
    d[, choice_forced := as.integer(p$choice_nosq)]
  }
  for (v in names(sp$attr)) d[, paste0("attr_", sp$attr[[v]][[1]]) := L(p[[v]], sp$attr[[v]][[2]])]
  d[, `:=`(trial_choice_set = as.integer(p$choice_set), trial_choice_card = as.integer(p$choice_card), trial_treated = as.integer(p$treated))]
  cv <- data.table(id = as.integer(sv$unique_id),
    cov_gender = c("1" = "female", "2" = "male", "3" = "other", "-99" = NA_character_)[as.character(sv$gender)],
    cov_age_group = age7[as.character(sv$age)], cov_education = sp$edu[as.character(sv$education)],
    cov_income_range = sp$inc[as.character(sv$income_range)], cov_income_perc = perc[as.character(sv$income_perc)],
    cov_duration_sec = as.integer(sv$duration_seconds))
  stopifnot(all(sv$gender %in% c(1, 2, 3, -99, NA)), all(is.na(sv$education) | as.character(sv$education) %in% names(sp$edu)),
            all(is.na(sv$age) | as.character(sv$age) %in% names(age7)),
            all(is.na(sv$income_range) | as.character(sv$income_range) %in% c(names(sp$inc), if (f == "FAITYP") "11")))
  if (f == "FAITYP") cv[, `:=`(cov_highqual_response = sv$highqual_response, cov_risk_attitude = sv$risk_attitude)]
  d <- merge(d, cv, by = "id", all.x = TRUE)
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(sp$table, ".csv")))
}
