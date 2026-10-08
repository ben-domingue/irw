##New-Resident immigrant conjoint (Taiwan) from
##Kao, J. C., & Liu, A. H. (2025). Racial identities, linguistic proficiency, and public
##attitudes towards immigrants: Evidence from two surveys in Taiwan. Political Research
##Quarterly, 78(2), 701-719. https://doi.org/10.1177/10659129251319737
##Replication data: Harvard Dataverse doi:10.7910/DVN/TTAE29, CC0 1.0, no restricted files.
##File read: immigration.dta (Dataverse "original format" download). The authors'
##Replication++Immigration++PRQ.do and .R were read as text (not run). No codebook or
##questionnaire ships, and the article (SAGE, open access) could not be fetched from here, so
##outcome wording, survey firm and dates are NOT confirmed.
##Usage: Rscript kao_2025.R <raw dir> <output dir>
##
##2,088 Taiwanese respondents (record), 5 pairs (task = round 1-5; profile 1 = "Person A",
##2 = "Person B") of hypothetical immigrant ("New Resident") profiles, 4 attributes: country of
##origin (Vietnam / Hong Kong / China / Ukraine), ethnicity (Hakka / Cantonese), occupation/visa
##status (Spouse / Blue Collar / White Collar / Refugee), Mandarin proficiency (Can Speak /
##Cannot Speak). Each attribute also has the level "No Info" (about a fifth to a third of
##profiles); the authors relabel it "None-stated ...", which suggests that attribute was simply
##not mentioned, but the deposit does not say what was displayed, so the authors' "No Info"
##label is kept as text rather than blanked. attr_* hold the authors' English Stata value
##labels; respondents saw Chinese text (not deposited). Restriction (the authors'
##constraint(country#ethnic)): Ukraine only with ethnicity "No Info" (never Hakka or Cantonese).
##ONE TABLE, kao_2025_new_residents, with three forced choices about the same pairs (no opt-out):
##  choice (source selected_immigration / immigration; the authors' "Admission"),
##  choice_health_insurance (selected_nih / nih; "Health Insurance", i.e. National Health
##    Insurance), choice_mother_tongue (selected_mother_tongue; "Mother Tongue", presumably
##    mother-tongue instruction). Exact question wording not available (see above).
##Missing answers: the authors drop every row missing any of the three outcomes (2,013
##respondents with at least one complete task). Here a row is kept if it has at least one of
##the three outcomes (outcomes missing individually stay NA): 2,075 respondents; 13
##respondents answered no task at all.
##Covariates: cov_gender_code (source `female`, CODES 0/1 kept: no label, codebook or recode
##code confirms which value is female, so the codes are not mapped to text); cov_age_group_code,
##cov_education_code, cov_income (source CODES 0-4, 0-6, 0-4; no labels deposited, so the band
##and answer text are unknown and the codes are kept under _code names); cov_region
##(central/east/north/south, from the source's four region dummies); cov_party_id (the
##source's `party` text as stored, incl. "I do not support any of these party"; the refusal
##"Prefer not to answer" -> NA; the authors' do-file L166-171 treats it as party ID); cov_father_* / cov_mother_* (parent's
##group: hakka, minnan, mainlander, aborigine, newresident, other; 0/1 as in the source);
##cov_proficiency_* (mandarin, minnan, hakka, aborigine, seasia, english, other; source codes
##0-3, 0 = none per the authors' code, higher = more proficient presumably); cov_visit_*
##(mainland, hk, sea, usa; source codes 0-10, 0 = never); cov_work_* (0/1); cov_tw_economy
##(-1/0/1). No survey weight in the deposit. Dropped: the authors' A_/B_ attribute dummies, person_A/person_B profile indexes,
##dupindicator (Stata expansion flag), the "Person A/B" answer strings (recoded into the
##outcomes). record is re-keyed to 1..n.
##Count vs paper: not checked (article not reachable). The authors' complete-case sample from
##this file is 2,013 respondents / 18,600 profile rows. Spot check (descriptive only): admission
##marginal means by origin on that sample are lowest for China (0.42) vs 0.52-0.56 for Vietnam,
##Hong Kong and Ukraine, in line with the abstract; no reported number was compared.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "immigration.dta")))
stopifnot(nrow(k) == 20880, k[, .N, .(record, round, profile)][, all(N == 1)])
lab <- function(x) as.character(as_factor(x))
d <- k[, .(src = record, task = as.integer(round), profile = as.integer(profile),
           choice = as.integer(selected_immigration), choice_health_insurance = as.integer(selected_nih),
           choice_mother_tongue = as.integer(selected_mother_tongue),
           attr_country = lab(country), attr_ethnicity = lab(ethnic), attr_visa = lab(visa), attr_mandarin = lab(mandarin))]
## check the outcome coding against the "Person A/B" strings
stopifnot(k[!is.na(selected_immigration), all(selected_immigration == as.integer((immigration == "Person A") == (profile == 1)))])
reg <- c("central", "east", "north", "south")
rm <- as.matrix(k[, paste0("region_", reg), with = FALSE]); stopifnot(all(rowSums(rm) == 1))
d[, cov_gender_code := as.integer(k$female)][, cov_age_group_code := as.integer(k$age)][, cov_education_code := as.integer(k$education)]
d[, cov_income := as.integer(k$income)][, cov_region := reg[max.col(rm)]][, cov_party_id := fifelse(k$party %in% c("", "Prefer not to answer"), NA_character_, k$party)]
for (p in c("father", "mother")) for (g in c("hakka", "minnan", "mainlander", "aborigine", "newresident", "other"))
  d[, paste0("cov_", p, "_", g) := as.integer(k[[paste0(p, "_", g)]])]
for (g in c("mandarin", "minnan", "hakka", "aborigine", "seasia", "english", "other"))
  d[, paste0("cov_proficiency_", g) := as.integer(k[[paste0("proficiency_", g)]])]
for (g in c("mainland", "hk", "sea", "usa")) d[, paste0("cov_visit_", g) := as.integer(k[[paste0("visit_", g)]])]
for (g in c("mainland", "hk", "sea", "usa")) d[, paste0("cov_work_", g) := as.integer(k[[paste0("work_", g)]])]
d[, cov_tw_economy := as.integer(k$tw_economy)]
outs <- c("choice", "choice_health_insurance", "choice_mother_tongue")
d <- d[rowSums(!is.na(d[, ..outs])) > 0]
for (o in outs) stopifnot(d[!is.na(get(o)), sum(get(o)), .(src, task)][, all(V1 == 1)])
stopifnot(d[, .N, .(src, task)][, all(N == 2)], uniqueN(d$src) == 2075)
stopifnot(d[attr_country == "Ukraine", all(attr_ethnicity == "No Info")])
d[, id := match(src, sort(unique(src)))][, src := NULL]
setcolorder(d, c("id", "task", "profile", outs))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kao_2025_new_residents.csv"))
