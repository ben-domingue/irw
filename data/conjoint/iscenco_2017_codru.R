##Choice experiment on the Codru Nature Reserve (Moldova), Phase II (final surveying), from
##Moldovan Environmental Governance Academy (MEGA): The Codru Quest, Economic Valuation of the Ecosystem Services of the
##Codru Protected Area (2017 project; final report and methodology on megageneration.com). Data set: Iscenco, A.,
##de Kruiff, T., Fausto, F., & Ungureanu, E. The Codru Quest data [Data set], Mendeley Data (version 2).
##(No journal article; doi field empty.)
##Data: Mendeley Data doi:10.17632/f4cdcfs4dg.2, CC BY 4.0 (Mendeley public API, data_licence). Files read:
##"MEGA - The Codru Quest - Final Dataset.xlsx" (sheet "Phase II - Final": 3,186 rows = 177 respondents x 6 choice sets
##x 3 scenarios) and "MEGA - The Codru Quest - Socio-economic Data.xlsx" (sheets Labels and Variables: the value labels
##used below). Level wording and design from "The Codru Quest Methodology" PDF (megageneration.com, Tables 2, 5, 7).
##Usage: Rscript iscenco_2017_codru.R <dir holding Final.xlsx and Socio.xlsx (names containing "Final" and "Socio")> <output dir>
##
##Face-to-face survey of 177 Moldovan residents (90 city residents, 87 village residents; the authors analysed them
##together and separately; one table, cov_residence records where they live) in 2017. Each of 6 choice sets: Scenario 0
##(status quo = the current state, no price) and Scenarios 1 and 2 (alternatives); the status quo is shown with its
##attribute levels, so it is a profile (profile 1), not an opt-out. Exactly one scenario chosen per set (checked).
##Fixed blocked design: all respondents saw the same 6 choice sets (the methodology kept 6 of 8 sets, Table 7). The
##file's Choiceset gives the order, assumed the order shown.
##Attributes (methodology Table 5): total territory of the Codru Nature Reserve in ha (5175; 5300; 5425), number of
##species of plants conserved (1000; 1050; 1100), number of species of insects conserved (8000; 8500; 9000), presence of
##symbolic species (small-flowered black hawthorn and stag beetle; representatives observed during a visit: 2; 4; 6),
##visitor price in MDL (0; 30; 60; 90; 120). The dataset stores dummy columns "Area 0/125/250" (increase over 5175),
##"Plants 0/50/100" (over 1000), "Insects 0/500/1000" (over 8000), "Representatives 2/4/6": mapped to the totals.
##Outcome: choice of one of the three scenarios (the question: choose between the status quo and the alternatives).
##Follow-up per set: "How certain are you in your choice of the scenario above?" (Very uncertain ... Very certain,
##Don't know): kept as trial_choice_certainty (task level text; NA where no certainty answer is coded).
##Restrictions: methodology says 2 of 8 sets were dropped as not realistic (design restriction on realism); level
##weights: fixed design, not a probability design -> unknown.
##Covariates kept (codebook: the Socio-economic file's Labels sheet): cov_gender, cov_birth_year (0 = missing -> NA),
##cov_education (answer text), cov_residence (city / on the outskirts of a city / village), cov_environmental_org
##(involved in an environmental organization: yes/no/don't know).
##Dropped: all attitude and behaviour survey answers (q01-q15), marital status, occupation, Phase I (see below).
##NOT BUILT: Phase I (Datasets.xlsx, 95 respondents, pilot with different attribute levels: insects 0/40/80, "few /
##medium / abundant symbolic" species) = a separate experiment with fewer than 100 respondents: held.
##N vs paper: 177 respondents; the methodology states the survey reached 201 respondents (Phase I + II plus the pilot).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ff <- list.files(raw, pattern = "[.]xlsx$", full.names = TRUE)
fin <- grep("Final", basename(ff), value = FALSE)[1]; soc <- grep("Socio", basename(ff))[1]
x <- as.data.table(read_excel(ff[fin], sheet = "Phase II - Final", guess_max = 1e5))
lab <- as.data.table(read_excel(ff[soc], sheet = "Labels", col_names = FALSE))
setnames(lab, c("var", "code", "txt", names(lab)[-(1:3)]))
L <- function(v) { z <- lab[var == v]; setNames(z$txt, z$code) }
stopifnot(nrow(x) == 3186, uniqueN(x$Id) == 177, x[, .N, Id][, all(N == 18)], x[, sum(Choice), .(Id, Choiceset)][, all(V1 == 1)],
  x[Scenario == 1, all(Price == 0 & `Area 0` == 1 & `Plants 0` == 1 & `Insects 0` == 1 & `Representatives 2` == 1)])
area <- function(z) ifelse(z[["Area 0"]] == 1, "5175 ha", ifelse(z[["Area 125"]] == 1, "5300 ha", "5425 ha"))
plants <- function(z) ifelse(z[["Plants 0"]] == 1, "1000 species", ifelse(z[["Plants 50"]] == 1, "1050 species", "1100 species"))
ins <- function(z) ifelse(z[["Insects 0"]] == 1, "8000 species", ifelse(z[["Insects 500"]] == 1, "8500 species", "9000 species"))
rep <- function(z) ifelse(z[["Representatives 2"]] == 1, "2 representatives", ifelse(z[["Representatives  4"]] == 1, "4 representatives", "6 representatives"))
cert <- x[, ifelse(`Very uncertain` == 1, "Very uncertain", ifelse(Uncertain == 1, "Uncertain", ifelse(`Neither certain nor uncertain` == 1,
  "Neither certain nor uncertain", ifelse(Certain == 1, "Certain", ifelse(`Very certain` == 1, "Very certain", ifelse(`Don't know` == 1, "Don't know", NA))))))]
x[, cert := cert]
d <- x[, .(id = match(Id, sort(unique(Id))), task = as.integer(Choiceset), profile = as.integer(Scenario), choice = as.integer(Choice),
  attr_territory = area(.SD), attr_plant_species = plants(.SD), attr_insect_species = ins(.SD), attr_symbolic_species_observed = rep(.SD),
  attr_visitor_price = paste(as.integer(Price), "MDL"),
  cov_gender = ifelse(gender == 1, "male", ifelse(gender == 2, "female", NA_character_)),
  cov_birth_year = ifelse(birth >= 1900 & birth <= 2010, as.integer(birth), NA_integer_),
  cov_education = unname(L("educ")[as.character(educ)]), cov_residence = unname(L("city")[as.character(city)]),
  cov_environmental_org = unname(L("env_org")[as.character(env_org)]), trial_choice_certainty = cert)]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^task$|^profile$")]), d[, .N, .(id, task)][, all(N == 3)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
  !anyNA(d$cov_education))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "iscenco_2017_codru_reserve.csv"))
