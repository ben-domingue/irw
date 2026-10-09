##Regional renewable-electricity-system choice experiment (Denmark, Germany, Poland, Portugal) from
##Mey, F., Lilliestam, J., Wolf, I., & Tröndle, T. (2024). Visions for our future regional
##electricity system - citizen preferences in four EU countries. iScience.
##Data: Zenodo doi:10.5281/zenodo.10463074 ("Raw data related to Mey et al (2024)"), CC BY 4.0.
##Covariates from the authors' pre-processed twin, Zenodo doi:10.5281/zenodo.10463114, CC BY 4.0.
##Files read: raw-data-{DEU,DNK,POL,PRT}.csv (conjointly.com exports) from 10463074, and
##survey-data.csv from 10463114. Read as text: the authors' workflow (Zenodo 10463120, MIT):
##report/report.md, scripts/preprocess/national.py, config/default.yaml.
##Usage: Rscript mey_2024.R <dir holding the four raw-data-*.csv and survey-data.csv> <output dir>
##
##Online opt-in panels (bilendi/respondi and partners), 24 Jan - 8 Feb 2022, hard gender quota.
##Each respondent made 8 choices between two hypothetical designs (left/right) of the future
##renewable electricity supply in their region; 6 attributes, "fully randomised design" and attribute
##order randomized across respondents but fixed within respondent (report.md; order not exported).
##Forced choice between the two options (exactly one chosen in every task; no opt-out column).
##Sample: the raw exports hold 4,526 respondents; the authors drop pre-test respondents who
##completed before 2022-01-24 (national.py filter_pre_test, config pre-test-threshold). The raw
##export's completion time is "NULL", so the analytic sample is taken as the respondents present in
##the authors' pre-processed survey-data.csv: 4,103 (DEU 1,031, DNK 1,034, POL 1,023, PRT 1,015;
##report.md "n=4103"). Choices and levels in the two files agree row for row (checked).
##One table with cov_country: the authors pool the four countries in one hierarchical model with
##a country effect, and the exported level labels are the same in all four.
##Attribute text: the conjointly export stores the attribute levels as short English labels
##(technology: Open-field PV / Rooftop PV / Wind; transmission capacity expansion -25%..+75%;
##land requirement 0.5%..8%; share of imports 0%..90%; household price change +0%..+60%;
##ownership Community / Private / Public). Respondents saw the survey in the national language with
##pictograms; that screen text is not in the deposit. task = CHOICE_SET, profile = LABEL (1 = left).
##Covariates (pre-processed file; the authors' English recoding of the national answer options):
##cov_gender (Female/Male/Other -> female/male/other), cov_birth_year (Q4, after the authors' fixes:
##age answers converted to birth year), cov_area (Q6), cov_renewables_nearby (Q7), cov_years_region
##(Q8), cov_education_en (Q9, harmonized English categories), cov_income_en (Q10), cov_climate_concern
##(Q11), cov_party_id (Q12, party name as recoded), cov_importance_social / _cost / _climate /
##_landscape (Q15 O1-O4), cov_q17_origin_country .. cov_q25_deployment (Q17-Q25 agreement items, as
##labelled), cov_region (first-level administrative region from the postcode lookup). Empty strings
##-> NA. Dropped: IP address, city, postcode, latitude/longitude, second/third admin levels, the
##panel's unique respondent code (TIC), free-text feedback (Q26), device fields, the authors'
##aggregated/imputed variables. No survey weight in either file.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
p <- fread(file.path(raw, "survey-data.csv"), encoding = "UTF-8")
att <- c("TECHNOLOGY", "TRANSMISSION", "LAND", "SHARE_IMPORTS", "PRICES", "OWNERSHIP")
r <- rbindlist(lapply(c("DEU", "DNK", "POL", "PRT"), function(cc) {
  x <- fread(file.path(raw, sprintf("raw-data-%s.csv", cc)), encoding = "UTF-8",
             select = c("RESPONDENT_ID", "CHOICE_SET", "LABEL", "CHOICE_INDICATOR", att))
  x[, cov_country := cc]
}))
stopifnot(uniqueN(r$RESPONDENT_ID) == 4526)
r <- r[RESPONDENT_ID %in% p$RESPONDENT_ID]
stopifnot(uniqueN(r$RESPONDENT_ID) == 4103, r[, .N, RESPONDENT_ID][, all(N == 16)])
chk <- merge(r, p[, .(RESPONDENT_ID, CHOICE_SET, LABEL = fifelse(LABEL == "Left", 1L, 2L), C = CHOICE_INDICATOR, T = TECHNOLOGY, O = OWNERSHIP)],
             by = c("RESPONDENT_ID", "CHOICE_SET", "LABEL"))
stopifnot(nrow(chk) == nrow(r), chk[, all(CHOICE_INDICATOR == C & TECHNOLOGY == T & OWNERSHIP == O)])
r[, id := match(RESPONDENT_ID, sort(unique(RESPONDENT_ID)))]
d <- r[, .(id, task = as.integer(CHOICE_SET), profile = as.integer(LABEL), choice = as.integer(CHOICE_INDICATOR),
           attr_technology = TECHNOLOGY, attr_transmission = TRANSMISSION, attr_land = LAND,
           attr_imports = SHARE_IMPORTS, attr_price = PRICES, attr_ownership = OWNERSHIP, cov_country, RESPONDENT_ID)]
nz <- function(x) { x <- trimws(as.character(x)); x[x == ""] <- NA; x }
pc <- unique(p[, .(RESPONDENT_ID,
  cov_gender = c(Female = "female", Male = "male", Other = "other")[Q3_GENDER],
  cov_birth_year = as.integer(Q4_BIRTH_YEAR), cov_area = nz(Q6_AREA), cov_renewables_nearby = nz(Q7_RENEWABLES),
  cov_years_region = as.integer(Q8_YEARS_REGION), cov_education_en = nz(Q9_EDUCATION), cov_income_en = nz(Q10_INCOME),
  cov_climate_concern = nz(Q11_CLIMATE_CONCERN), cov_party_id = nz(Q12_PARTY),
  cov_importance_social = nz(Q15_ATTRIBUTE_IMPORTANCE_O1), cov_importance_cost = nz(Q15_ATTRIBUTE_IMPORTANCE_O2),
  cov_importance_climate = nz(Q15_ATTRIBUTE_IMPORTANCE_O3), cov_importance_landscape = nz(Q15_ATTRIBUTE_IMPORTANCE_O4),
  cov_q17_origin_country = nz(Q17_ORIGIN_COUNTRY), cov_q18_origin_eu = nz(Q18_ORIGIN_EU), cov_q20_transition = nz(Q20_TRANSITION),
  cov_q21_environmental = nz(Q21_ENVIRONMENTAL), cov_q22_climate_protection = nz(Q22_CLIMATE_PROTECTION),
  cov_q23_democratisation = nz(Q23_DEMOCRATISATION), cov_q24_resources = nz(Q24_RESOURCES), cov_q25_deployment = nz(Q25_DEPLOYMENT),
  cov_region = nz(RESPONDENT_ADMIN_NAME1))])
stopifnot(!anyDuplicated(pc$RESPONDENT_ID), all(p$Q3_GENDER %in% c("Female", "Male", "Other")))
d <- merge(d, pc, by = "RESPONDENT_ID")[, RESPONDENT_ID := NULL]
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mey_2024_regional_electricity.csv"))
