##River restoration with large wood: choice experiment in a German representative survey, from
##Gapinski, C. M., Hermes, J., & von Haaren, C. (2021). Why people like or dislike large wood in rivers: a
##representative survey of the general public in Germany. River Research and Applications, 37(2), 187-197.
##https://doi.org/10.1002/rra.3743 (that article analyses group 1 only; groups 2 and 3 are "in preparation").
##Data: Gapinski, Hermes & von Haaren (2021), Leibniz Universitaet Hannover data repository
##doi:10.25835/0071779, CC BY 3.0 (CKAN licence_id CC-BY-3.0, "Creative Commons Attribution 3.0 Germany").
##Files read (from German_riverine_landscape_survey.zip): R_ChExp_Total_Sample.csv (semicolon-separated),
##Overview.docx and Questionaire_instructions.pdf (read as text for the displayed German wording).
##Usage: Rscript gapinski_2021.R <dir holding R_ChExp_Total_Sample.csv> <output dir>
##
##2,100 adults (online panel by Eresult GmbH, Germany-wide representative quotas, early 2018), 8 choice tasks each,
##three cards per task: "Zustand HEUTE" (status quo) and Alternatives A and B. The status quo card shows its own
##levels (grassland, no deadwood, good recreation usability, 0 EUR), so it is a PROFILE (profile 1 = status quo,
##2 = A, 3 = B, as the cards are laid out left to right) and there is no opt-out: exactly one card is chosen in
##every task (verified). Outcome (choice): "Wählen Sie eine Karte aus" among the three cards ("choose the
##alternative you like best; you may also choose the current state"), questionnaire section 3.
##Attributes (German text from the questionnaire's example card and attribute pop-ups; the deposit stores English
##tags "1 grassland", "2 little" etc. that are mapped back to it): land use of the floodplain, deadwood amount in
##the watercourse, usability for recreation, property tax per household and year. The two ecosystem-service rows
##(trout population, self-purification) are "additional information" that vary by information split and are
##determined by the deadwood level, not separate attributes (the authors do not evaluate them): they are not
##stored. trial_info_format = the split: qualitative (ordinal ratings), quantitative (cardinal values) or monetary
##(EUR) ecosystem-service information, shown to 743 / 648 / 709 respondents (between respondents). The three splits
##share the same cards and the deposit ships a pooled "Total_Sample" file; this table pools them.
##Task = the number after "_" in idCSet (1..8, the order of the choice situations; every respondent has 1..8).
##Restrictions: none documented; 32 SPSS orthogonal cards, 8 per respondent in blocks; Alt A/B land use and tax
##levels are unbalanced between A and B (e.g. tax -90 mainly on A), so level weights are observed.
##Covariates: cov_gender (m -> male, w -> female), cov_age_group (age band text as stored, German), cov_state_code
##(bula, federal-state abbreviation as stored; no codebook), cov_income_band (einkom, household net monthly income
##band text as stored, EUR). Dropped: school/education codes, leisure-activity flags, derived dummies and
##utility-model columns (LW:/LU:/UR:/CO/ASC), income midpoints.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "R_ChExp_Total_Sample.csv"), sep = ";", encoding = "UTF-8")
stopifnot(nrow(x) == 50400, uniqueN(x$id) == 2100)
x[, task := as.integer(sub(".*_", "", idCSet))]
stopifnot(x[, uniqueN(task), id][, all(V1 == 8)], x[, all(sub("_.*", "", idCSet) == id)])
lu <- c("1 grassland" = "Überwiegend Grünland", farmland = "Überwiegend Ackerbau", forest = "Überwiegend Wald", urban = "Überwiegend Siedlung/Bebauung")
dw <- c("1 none" = "Kein Totholz", "2 little" = "gering", "3 inter" = "mittel", "4 much" = "hoch")
rc <- c("1 poor" = "Schlecht nutzbar", "2 moderate" = "Mäßig nutzbar", "3 good" = "Gut nutzbar", "4 very good" = "Sehr gut nutzbar")
taxtxt <- function(t) fifelse(t == 0, "+/- 0 € unverändert", fifelse(t > 0, paste0("+", t, " € (mehr Steuern)"), paste0("-", abs(t), " € (weniger Steuern)")))
d <- x[, .(id = as.integer(id), task, profile = c(SQ = 1L, AltA = 2L, AltB = 3L)[Alt], choice = as.integer(choice),
  attr_land_use = unname(lu[landuse]), attr_deadwood = unname(dw[deadwood]), attr_recreation_usability = unname(rc[recuse]),
  attr_tax_per_household_year = taxtxt(tax),
  trial_info_format = sub("^[0-9] ", "", infotype),
  cov_gender = c(m = "male", w = "female")[sex], cov_age_group = age, cov_state_code = bula,
  cov_income_band = fifelse(einkom == "", NA_character_, einkom))]
stopifnot(!anyNA(d[, .(attr_land_use, attr_deadwood, attr_recreation_usability, attr_tax_per_household_year, profile)]),
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 3)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gapinski_2021_river_large_wood.csv"))
