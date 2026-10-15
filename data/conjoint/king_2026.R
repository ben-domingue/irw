##Colours, smells and sounds of biodiversity in a new woodland (winter wave): choice experiment, from the Zenodo deposit
##"Replication materials: Stated preferences for the colours, smells, and sounds of biodiversity" (King, Davies et al.; RELATE
##ERC project), the data of King et al., Ecological Economics 108410, doi:10.1016/j.ecolecon.2024.108410.
##Deposit: doi:10.5281/zenodo.20645896 (concept doi 10.5281/zenodo.20645895), licence on the Zenodo record: MIT ("mit-license");
##the repository LICENSE is the MIT License (copyright 2023 Peter King). Recorded verbatim as "MIT License".
##Files read (extracted individually from the deposit's zip WinterPaper-11_06_26B.zip): CEModelData/database_Winter_Step1.csv
##(the table's rows), RELATE Seasonal Questionnaire_word print out.docx (read as text via pandoc: level wording), KDR_Readme.txt,
##and the authors' R scripts (text only: 01_Winter_CleanSurveyData.R, 02_Winter_MNL_ModelZero.R) for the coding. The other files
##of the zip (UK shapefile, AdditionalData.xlsx, Winter_SurveyData.xlsx, model outputs) were not used.
##Usage: Rscript king_2026.R <dir holding database_Winter_Step1.csv> <output dir>
##
##Sample: 1,711 adults in Great Britain (England, Scotland, Wales; quota sample via a survey company, Qualtrics, 25 Jan - 19 Feb
##2021, the winter season), 9 choice tasks each = 15,399 rows in the model file, after the authors' own exclusion (they drop
##respondents who describe their gender "in another way", script line 237). All 1,711 respondents have exactly tasks 1-9.
##Design: in each task two woodland-management options (Option A, Option B = profile 1, 2) and "No change" (profile 3). "No
##change" is shown with its own element levels ("the levels for the elements staying as planned", questionnaire Q93), which the data
##store as zero levels (low variety of sounds, colours and smells, no deadwood, no tax increase), so it is a PROFILE, not an opt-out.
##Exactly one of the three is chosen per task (Choice 1 = A, 2 = B, 3 = No change; verified). Blocks 1 and 2 (trial_block) are the
##two question blocks of the design (a blocked fixed design; level probabilities not stated).
##Attributes (5; coding from the model scripts, wording from the questionnaire):
##  sound variety Sound 0/1/2 = Low / Medium / High variety of sounds (questionnaire headings Q152-155);
##  colour variety 0/1/2 = Low / Medium / High variety of colours; smell variety 0/1/2 = Low / Medium / High variety of smells;
##  deadwood 0/7/15 (amount of deadwood brought in per hectare; the unit is not stated in the questionnaire text; the sound clips
##    and images that illustrated the levels are not in the deposit) -> "0 per hectare", "7 per hectare", "15 per hectare";
##  council tax increase GBP 2/4/10/20/35/60 per year for ten years (questionnaire Q147/Q149; GBP 0 for No change).
##Choice wording (questionnaire): "Which ONE of the above choices would you pick for the new woodland?" Option A / Option B / No change.
##Covariates: cov_age_group (the age band answered, text), cov_education (highest qualification, text), cov_household_income (band,
##text with the pound sign written GBP, "Prefer not to say" -> NA), cov_country (England / Scotland / Wales), cov_area (rural or urban). Dropped: gender (the deposit's
##Gender column is a 0/1 recode whose direction follows the order of first appearance in the raw data, so it cannot be mapped), age in
##years (the authors' ExactAge uses fixed midpoints for people who gave a band), ethnicity, occupation of the chief income earner, the
##map pin (column holds the placeholder "lat: 00.000, lon: 00.000"; PII FOUND, masked), recorded date, durations, ~150 attitude and
##feeling items, derived dummies, visit-history items, free text. No survey weight. Respondent id re-keyed (Respondent 1-1711).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "database_Winter_Step1.csv"), encoding = "Latin-1")
stopifnot(nrow(d) == 15399, uniqueN(d$Respondent) == 1711, d[, all(Task == 1:9), Respondent][, all(V1)],
          all(d$Choice %in% 1:3), all(d$av_A == 1), all(d$av_B == 1), all(d$av_C == 1))
for (v in c("Sound3", "Colour3", "Smell3", "Deadwood3", "Tax3")) stopifnot(all(d[[v]] == 0))
d[, id := match(Respondent, unique(Respondent))]
lv3 <- function(x, w) paste(c("Low", "Medium", "High")[x + 1L], "variety of", w)
dw <- function(x) paste(x, "per hectare")
tx <- function(x) paste("GBP", x, "per year")
mk <- function(k) {
  p <- function(v) d[[paste0(v, k)]]
  stopifnot(all(p("Sound") %in% 0:2), all(p("Colour") %in% 0:2), all(p("Smell") %in% 0:2), all(p("Deadwood") %in% c(0, 7, 15)),
            all(p("Tax") %in% c(0, 2, 4, 10, 20, 35, 60)))
  data.table(id = d$id, task = as.integer(d$Task), profile = k, choice = as.integer(d$Choice == k),
    attr_sound_variety = lv3(p("Sound"), "sounds"), attr_colour_variety = lv3(p("Colour"), "colours"),
    attr_smell_variety = lv3(p("Smell"), "smells"), attr_deadwood = dw(p("Deadwood")), attr_council_tax_increase = tx(p("Tax")),
    trial_block = as.integer(d$Block),
    cov_age_group = d[["How.old.are.you."]], cov_education = d[["Please.select.your.highest.level.of.education.you.have.completed..pick.one.option."]],
    cov_household_income = ifelse(grepl("Prefer not", d[["Please.select.the.income.band.that.represents.your.total..before.tax..yearly.household.income..pick.one.option."]]), NA,
                                  sub("£", "GBP ", gsub("£", "GBP ", d[["Please.select.the.income.band.that.represents.your.total..before.tax..yearly.household.income..pick.one.option."]]))),
    cov_country = d[["Which.country.are.you.currently.living.in."]], cov_area = d[["Would.you.say.the.area.you.live.in.is.generally.rural.or.urban."]])
}
o <- rbind(mk(1L), mk(2L), mk(3L))
setorder(o, id, task, profile)
stopifnot(o[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(o[, .SD, .SDcols = patterns("^attr_")]), o[, uniqueN(trial_block), id][, all(V1 == 1)])
dir.create(out, showWarnings = FALSE, recursive = TRUE)
fwrite(o, file.path(out, "king_2026_biodiversity_woodland.csv"))
