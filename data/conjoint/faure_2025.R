##Climate-migration conjoint (Netherlands) from
##Faure, M., Kantorowicz, J., & Weiss, A. (2025). Is climate change a valid reason for
##migration? Evidence from a conjoint experiment. Journal of Elections, Public Opinion and
##Parties, 36(3), 757-778. https://doi.org/10.1080/17457289.2025.2514195
##Replication data: Harvard Dataverse doi:10.7910/DVN/VFRHWX, CC0 1.0, no restricted files.
##File read: conjoint_dataset.RDS. The authors' conjoint_experiment_final.R (read as text) gives
##the English translations of the levels and the covariate recodes used below. The deposit has
##no codebook or questionnaire, and the article full text could not be retrieved (publisher and
##repository PDF both refused automated access), so outcome wording is a paraphrase.
##Usage: Rscript faure_2025.R <raw dir> <output dir>
##
##1,529 Dutch respondents (quota-representative sample per the abstract), 6 tasks of 2
##hypothetical migrant profiles, 6 attributes. task and profile are the source columns (the
##long file was built by the authors with reshape() over the _1/_2 profile columns; profile 1 =
##the first profile). Every task has exactly one selected profile: forced choice, no opt-out.
##  choice = selected: which of the two migrants the respondent prefers to admit (paraphrase;
##           the wording is not in the deposit).
##Attribute levels are kept in Dutch as displayed (the authors' English in brackets):
##  economische_situatie: In staat om zichzelf te onderhouden (Able to sustain himself/herself),
##    Waarschijnlijk in staat zichzelf te onderhouden (Likely able ...), Onwaarschijnlijk in
##    staat om zichzelf te onderhouden (Unlikely able ...), Niet in staat om zichzelf te
##    onderhouden (Not able ...); geslacht: Man/Vrouw; land_van_herkomst: Maldiven, Myanmar,
##    Nigeria, Pakistan, Syrie (stored as in source, "Syrië"), Vietnam; leeftijd: 18-25 jaar,
##    34-48 jaar, 52-65 jaar, 65 jaar of ouder; onderwijsniveau: Basisschool niet voltooid,
##    Basisschool voltooid, Middelbare school voltooid, Universitair diploma; reden_voor_migratie:
##    Het ontkomen aan politieke/religieuze/etnische vervolging (Escaping persecution), Het
##    verbeteren van economische kansen (Seeking economic opportunities), Vluchten door
##    aardbevingen (earthquake), Vluchten door extreme droogte (drought), Vluchten door
##    overstromingen (flood).
##Restrictions (observed, not documented in the deposit): Maldiven never appears with
##aardbevingen or droogte; Pakistan and Vietnam never with droogte. Other levels look uniform.
##The original Qualtrics export had .rowpos columns (named in the RDS's reshapeLong attribute),
##so attribute order was probably randomized, but those columns are not deposited.
##Covariates: cov_gender (gender_cat Female/Male), cov_age_group (age_cat, "Age " prefix
##removed, e.g. "18-24"), cov_province (place_cat), cov_survey_weight (weight, used by the
##authors in every cregg call). Kept with source codes, meanings from the authors' recodes:
##cov_education_code (no labels anywhere in the deposit), cov_pref_political_1 (0-10, authors
##treat 0-3 as Left, 7-10 as Right), cov_pref_party (party codes 1-18; no labels, the authors
##group them into left/right via a Wikipedia list), cov_pref_climate_1_1 (0-10, climate change a
##serious problem, higher = more serious), cov_pref_climate_2 (importance of ambitious climate
##targets, 1 = very, 2 = fairly, 3/4 = not), cov_pref_climate_change_1/2/3 (0-10: climate change
##man-made / has adverse effects / government should mitigate even if costly),
##cov_pref_climate_pol_1/2/3 (1 = yes, 2 = no: adapt own behaviour to reduce emissions; the
##authors pool 2 and 3 as willingness to invest in high-carbon-footprint companies).
##Dropped: Response.ID (Qualtrics response ID) and the redundant `id` column; respondents are
##keyed by the source's integer `respondent`.
##N = 1,529 (the abstract gives no N; article not checked).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "conjoint_dataset.RDS")))
d <- data.table(id = as.integer(s$respondent), task = as.integer(s$task), profile = as.integer(s$profile),
                choice = as.integer(s$selected))
am <- c(Economische.situatie = "economische_situatie", Geslacht = "geslacht", Land.van.herkomst = "land_van_herkomst",
        Leeftijd = "leeftijd", Onderwijsniveau = "onderwijsniveau", Reden.voor.migratie = "reden_voor_migratie")
for (v in names(am)) { x <- as.character(s[[v]]); stopifnot(!anyNA(x), all(nzchar(x))); d[, paste0("attr_", am[[v]]) := x] }
stopifnot(all(s$gender_cat %in% c("Female", "Male")))
d[, cov_gender := tolower(as.character(s$gender_cat))]
d[, cov_age_group := sub("^Age ", "", as.character(s$age_cat))]
d[, cov_province := as.character(s$place_cat)]
d[, cov_education_code := as.integer(s$education)]
for (v in c("pref_political_1", "pref_party", "pref_climate_1_1", "pref_climate_2", "pref_climate_change_1",
            "pref_climate_change_2", "pref_climate_change_3", "pref_climate_pol_1", "pref_climate_pol_2", "pref_climate_pol_3"))
  d[, paste0("cov_", v) := as.integer(s[[v]])]
d[, cov_survey_weight := s$weight]
stopifnot(d[, .N, id][, all(N == 12)], d[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(d$id) == 1529L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "faure_2025_climate_migrants_nl.csv"))
