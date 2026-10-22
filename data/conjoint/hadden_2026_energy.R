##Energy-project conjoint in three emerging economies (three tables) from
##Hadden, J., & Alkon, M. "Home Field Advantage: How Developer Identity Shapes Public Opinion about
##Energy Projects in Major Emerging Economies" (working paper; no article DOI yet).
##Replication data: Harvard Dataverse doi:10.7910/DVN/XNCX0V, CC0 1.0, deposited 2026-10-14, no
##restricted files. File read: "Home Field Advantage Data Cleaned Prepped.rdata" (object `bb`,
##73,272 rows x 350 columns, 3,053 respondents). Read as text only: "Home Field Advantage Analysis.R".
##Usage: Rscript hadden_2026_energy.R <dir holding the .rdata> <output dir>
##
##One experiment fielded in India, South Africa and Turkey -> THREE tables, one per country, because
##the populations and the display language differ (Turkey saw a Turkish instrument; the Indian and
##South African files carry the English text). Each respondent appears in one country only.
##
##`counter` runs 1..24 within a respondent and is the only task/profile key in the deposit:
##  counters 1-16 are EIGHT PAIRED-CHOICE tasks (`chosen` 0/1, exactly one 1 per pair, verified);
##  counters 17-24 are EIGHT SINGLE-PROFILE tasks rated on `support` and `protest` (-2..2).
##So task = 1..8 from ceiling(counter/2) for the choice tasks and 9..16 for the rating tasks, and
##profile = 1, 2 within a choice task (file row order) and 1 for a rating task. Both are INFERRED:
##the deposit stores no task or profile column. `trial_task_type` records which kind a task is.
##A rating task's rows have no `choice` and a choice task's rows have no rating, as fielded.
##
##Attributes are stored as displayed text, bilingual by sample (five attributes):
##  attr_project_type (coal / gas / solar / wind), attr_proximity (in your community / another),
##  attr_destination (where the electricity goes), attr_electricity (amount, with the "enough to
##  power about N homes" gloss as shown), attr_developer (the developer's country).
##`attr_developer` is NOT uniform by design: the domestic developer is drawn about half the time and
##each of the five foreign developers about a tenth (level_weights = observed). All 110 pairs of
##levels across attributes occur in every country sample, but no source documents the randomization,
##so `restrictions` stays unknown.
##
##The deposit ships no questionnaire and no codebook, so the outcome WORDING IS UNKNOWN for all three
##outcomes and the rating anchors are unknown; `design_outcomes.csv` records that rather than a guess.
##The rating columns keep the source's own -2..2 coding, unrescaled and unreversed.
##
##Covariates keep the source's own answer text, which is Turkish in the Turkish sample.
##`Age` holds a YEAR OF BIRTH, so it is `cov_birth_year` and no age is computed from it. `Gender` is
##mapped to the reserved female/male/other coding from the source's own answer text (Kadin/Female ->
##female, Erkek/Male -> male, Diger / Other-prefer-not-to-respond -> other, blank -> NA). Dropped:
##the wide per-task response columns (c1Q..c8Q, p*Q*), every m*D / m*F dummy coding, the derived
##female/urban/employed/Educ_Level dummies, `gc` (constant 1), `rowindic` (constant 1), and
##`StartDate`. PII dropped: LocationLatitude, LocationLongitude and ResponseId (ids are re-keyed
##1..n per country in first-appearance order).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "Home Field Advantage Data Cleaned Prepped.rdata"), envir = e)
bb <- as.data.table(get("bb", e))
stopifnot(nrow(bb) == 73272, uniqueN(bb$ResponseId) == 3053, all(bb$counter %in% 1:24))

ATTRS <- list(type = "project_type", Prox = "proximity", dest = "destination",
              elec = "electricity", dev = "developer")
COVS <- c(cov_birth_year = "Age", cov_region = "Region", cov_urban_rural = "Urban.rural",
          cov_marital_status = "Marital_status", cov_children = "Children",
          cov_education = "Education", cov_employment = "Employment", cov_income = "Income",
          cov_class = "Class", cov_occupation = "Occupation",
          cov_climate_community = "Climate_community", cov_climate_concern = "Climate_concern",
          cov_pollution_concern = "Pollution_concern", cov_electricity_satisfaction = "Electricity",
          cov_pol_engage_1 = "Pol_engage_1", cov_pol_engage_2 = "Pol_engage_2",
          cov_pol_engage_3 = "Pol_engage_3", cov_pol_engage_4 = "Pol_engage_4",
          cov_pol_engage_5 = "Pol_engage_5", cov_pol_success = "Pol_success",
          cov_pol_success_2 = "Pol_success.1", cov_pol_approval = "Pol_approval",
          cov_pol_ideology = "pol_ideology", cov_institutions_1 = "Institutions_1",
          cov_institutions_2 = "Institutions_2", cov_institutions_3 = "Institutions_3",
          cov_institutions_4 = "Institutions_4", cov_institutions_5 = "Institutions_5",
          cov_trust = "Trust", cov_cosmopolitanism = "Cosmopolitanism",
          cov_corruption = "Corruption_1", cov_corrupt_people_1 = "Corrupt_people_1",
          cov_corrupt_people_2 = "Corrupt_people_2", cov_corrupt_people_3 = "Corrupt_people_3",
          cov_energy_knowledge = "energy_know", cov_economic_situation = "econ.sit",
          cov_duration_sec = "Duration..in.seconds.")
GENDER <- c("Female" = "female", "Kadın" = "female", "Male" = "male", "Erkek" = "male",
            "Other / Prefer not to respond" = "other",
            "Diğer / Yanıt vermemeyi tercih ediyorum" = "other")
TABLES <- c(India = "hadden_2026_energy_india", "South Africa" = "hadden_2026_energy_south_africa",
            Turkey = "hadden_2026_energy_turkey")

for (cty in names(TABLES)) {
  s <- bb[Country == cty]
  setorder(s, ResponseId, counter)
  s[, id := .GRP, ResponseId]
  s[, task := fifelse(counter <= 16L, as.integer(ceiling(counter / 2)), as.integer(counter - 8L))]
  s[, profile := fifelse(counter <= 16L, as.integer(2L - counter %% 2L), 1L)]
  s[, trial_task_type := fifelse(counter <= 16L, "paired choice", "single profile")]
  ##every paired task has two profiles and exactly one chosen; every rating task has one profile
  stopifnot(s[counter <= 16L, .N, .(id, task)][, all(N == 2L)],
            s[counter <= 16L, sum(chosen), .(id, task)][, all(V1 == 1L)],
            s[counter > 16L, .N, .(id, task)][, all(N == 1L)],
            s[counter <= 16L, !anyNA(chosen)], s[counter > 16L, all(is.na(chosen))],
            s[counter > 16L, !anyNA(support) & !anyNA(protest)])
  o <- s[, .(id, task, profile, choice = as.integer(chosen),
             rating_support = as.integer(support), rating_protest = as.integer(protest))]
  for (v in names(ATTRS)) o[, (paste0("attr_", ATTRS[[v]])) := trimws(s[[v]])]
  for (nm in names(COVS)) {
    x <- s[[COVS[[nm]]]]
    x <- if (is.factor(x)) as.character(x) else x
    if (is.character(x)) { x <- trimws(x); x[x == ""] <- NA_character_ }
    o[, (nm) := x]
  }
  g <- trimws(as.character(s$Gender)); g[g == ""] <- NA_character_
  stopifnot(all(is.na(g) | g %in% names(GENDER)))
  o[, cov_gender := unname(GENDER[g])]
  o[, trial_task_type := s$trial_task_type]
  stopifnot(!anyNA(o[, .SD, .SDcols = patterns("^attr_")]))
  setorder(o, id, task, profile)
  setcolorder(o, c("id", "task", "profile", "choice", "rating_support", "rating_protest",
                   grep("^attr_", names(o), value = TRUE), "trial_task_type"))
  fwrite(o, file.path(out, paste0(TABLES[[cty]], ".csv")))
  cat(TABLES[[cty]], nrow(o), "rows", uniqueN(o$id), "respondents\n")
}
