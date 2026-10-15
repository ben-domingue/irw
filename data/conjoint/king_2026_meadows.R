##Urban wildflower meadows choice experiment from
##King, P., Pett, T. J., Goddard, M. A., Lundhede, T. H., Austen, G. E., Davies, Z. G., & Dallimer, M. (2026).
##Understanding public preferences for urban wildflower meadows. Journal of Environmental Management.
##https://doi.org/10.1016/j.jenvman.2026.131156
##Deposit: Zenodo doi:10.5281/zenodo.23374961 (version record; concept DOI 10.5281/zenodo.23374960), Zenodo licence
##"mit-license", repository LICENSE = MIT License. File read: Meadows-v1.0.1.zip -> Data/database_Meadows_Anonymised_Weighted.csv
##(the 474-respondent analytic sample; the other file, 563 respondents, is the unfiltered export), Data/Meadows_Codebook.csv and
##Meadows_FullSurveyPrintUpdated.pdf (questionnaire, choice cards p. 215-217).
##Usage: Rscript king_2026_meadows.R <dir holding database_Meadows_Anonymised_Weighted.csv> <output dir>
##
##474 park visitors (face to face, 11 parks in Leeds, Bristol, Edinburgh). Each saw 6 tasks of 4 options A, B, C and D (D = the
##current situation); 12 cards in a fixed two-block design (each respondent sees the six cards of one block; "card" gives the card).
##Fixed blocked design, 2 blocks of 6 sets; the deposit gives no level probabilities. Option D is shown with levels (no change in
##plants, native share, pollinators, appearance and GBP 0), so it is a profile and there is no opt-out: exactly one of 4 chosen.
##Outcome: choice = "Which ONE of the following options would you choose?" (A/B/C/D).
##Attribute text follows the choice cards in the questionnaire PDF. The deposit stores dummies; the base level of each attribute is
##the current situation shown for option D. Plants: "No change in number of plant species" / "An additional 5 plant species" /
##"An additional 10 plant species". Native: "No change: half of plant species are native" / "An increase to three-quarters native plant
##species" / "A decrease to a quarter native plant species". Pollinators: "No change: low quality for pollinating insects" / "Medium
##quality for pollinating insects" / "High quality for pollinating insects". Appearance is shown as a photograph only; the text is
##our paraphrase of the photograph (flowers in white only / white, yellow and blue / white, yellow, blue, pink and red; current = plain
##green grass). Cost: "GBP n per year" (card: "Additional council tax cost per year to your household", GBP sign).
##Covariates: cov_gender (codebook: 0 = Female, 1 = Male, confirmed against the thesis sample table), cov_age_group (AgeLevel band floors
##18/25/35/45/55/65 -> the questionnaire's bands), cov_income_midpoint (the authors' GBP band midpoint, household income before tax),
##cov_city (codebook), cov_meadow_type (codebook Type), cov_park (Clean_Park_ID), cov_education_code / cov_employment_code (codes kept: the
##codebook does not list code order explicitly), cov_survey_weight (the authors' entropy-balancing weight "Weights", constant within
##respondent). Dropped: row-index artifacts, duplicate columns, effects/dummy codings, the authors' derived dummies, attitudinal guesses and
##site measurements, CNS scale, the always-status-quo flag, the second binary weight. ID is the authors' randomly reassigned respondent ID.
##Count check: 474 respondents x 6 tasks = the paper's analytic N per the codebook (563 recruited).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "database_Meadows_Anonymised_Weighted.csv"))
stopifnot(uniqueN(d$ID) == 474, d[, .N, ID][, all(N == 6)], d[, uniqueN(Task), ID][, all(V1 == 6)])
cost <- function(x) sprintf("GBP %d per year", as.integer(x))
rows <- list()
for (k in 1:4) {
  s <- c("A", "B", "C", "D")[k]
  g <- function(n) d[[paste0(n, "_", s)]]
  p5 <- g("Plants_5"); p10 <- g("Plants_10")
  nd <- g("Native_Decrease"); ni <- g("Native_Increase")
  pm <- g("PollinatorQuality_Medium"); ph <- g("PollinatorQuality_High")
  aw <- g("Appearance_W"); ab <- g("Appearance_WYB"); ar <- g("Appearance_WYBPR")
  stopifnot(all(p5 + p10 <= 1), all(nd + ni <= 1), all(pm + ph <= 1), all(aw + ab + ar <= 1))
  rows[[k]] <- data.table(id = as.integer(d$ID), task = as.integer(d$Task), profile = k,
    choice = as.integer(d$choice == k),
    attr_plants = fifelse(p5 == 1, "An additional 5 plant species", fifelse(p10 == 1, "An additional 10 plant species", "No change in number of plant species")),
    attr_native = fifelse(ni == 1, "An increase to three-quarters native plant species", fifelse(nd == 1, "A decrease to a quarter native plant species", "No change: half of plant species are native")),
    attr_pollinators = fifelse(ph == 1, "High quality for pollinating insects", fifelse(pm == 1, "Medium quality for pollinating insects", "No change: low quality for pollinating insects")),
    attr_appearance = fifelse(ar == 1, "Flowers in white, yellow, blue, pink and red (photograph)", fifelse(ab == 1, "Flowers in white, yellow and blue (photograph)", fifelse(aw == 1, "Flowers in white only (photograph)", "No change: plain green grass (photograph)"))),
    attr_cost = cost(d[[paste0("cost", s)]]),
    trial_card = as.integer(d$card))
}
r <- rbindlist(rows)
cv <- unique(d[, .(id = as.integer(ID),
  cov_gender = c("female", "male")[Gender + 1L],
  cov_age_group = c("18-24", "25-34", "35-44", "45-54", "55-64", "65 or more")[match(AgeLevel, c(18, 25, 35, 45, 55, 65))],
  cov_income_midpoint = as.integer(Income),
  cov_education_code = as.integer(Education), cov_employment_code = as.integer(Employment),
  cov_city = c("Leeds", "Bristol", "Edinburgh")[city],
  cov_meadow_type = c("Control", "Perennial", "Annual")[Type],
  cov_park = Clean_Park_ID, cov_survey_weight = Weights)])
stopifnot(nrow(cv) == 474, !anyNA(cv$cov_gender), !anyNA(cv$cov_age_group))
r <- merge(r, cv, by = "id")
stopifnot(r[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(r[, .(attr_plants, attr_native, attr_pollinators, attr_appearance, attr_cost)]))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "king_2026_urban_meadows.csv"))
