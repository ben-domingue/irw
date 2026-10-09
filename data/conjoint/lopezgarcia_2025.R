##Property-tax (CFPB) proposal conjoint (Haiti) from
##Lopez Garcia, A. I., & Berens, S. (2025). Taxing the wealthy in Haiti: Evidence from a conjoint
##experiment on property tax preferences. World Development, 196, 107193.
##https://doi.org/10.1016/j.worlddev.2025.107193
##Replication data: Harvard Dataverse doi:10.7910/DVN/LMIIRA, CC0 1.0, no restricted files.
##Files read: haiti_apr.dta (Dataverse "original format" download of haiti_apr.tab), Questionnaire.pdf
##(covariate wording), ReadMe; "Data Preparation.do" and "Main Analysis.do" read as text. The
##article was not retrievable (publisher 403). Level text and question wording come from the
##authors' pre-analysis plan (OSF registration 4kev7, "PAP - Taxing Higher Incomes in Haiti.pdf",
##section 6.1, Table 1), named in the deposit ReadMe.
##Usage: Rscript lopezgarcia_2025.R <raw dir> <output dir>
##
##RIWI online survey in Haiti, 12 Dec 2023 - 8 Apr 2024 (ReadMe). 2,003 rows; 2 are empty (no
##id, no answers) and are dropped: 2,001 respondents, each 3 tasks (q01-q03) x 2 tax proposals
##(c1 = A = profile 1, c2 = B = profile 2), 6 attributes, all shown.
##  choice = q0t_tax_evaluation_t0t ("a"/"b"): "Considering the tax proposals below. If you had to
##           choose which proposal, would you prefer: A or B?" (PAP; intro: "please tell us which
##           proposal you support more, even if you either like or dislike both proposals").
##           Forced, no opt-out; one choice per task (checked).
##Attribute text: the deposit stores snake_case codes (e.g. "names_announced_local_radio");
##each is mapped to the English text of PAP Table 1 (code and text match one-to-one; the
##authors' Stata labels in Data Preparation.do agree, e.g. 4 = "foreign ngos"). PAP table
##line breaks undone ("Substantiall y" -> "Substantially"; "Low and -middle-class" -> "Low- and
##middle-class"). The PAP is the pre-fieldwork English text; respondents most likely saw Haitian
##Creole (the questionnaire's filter question is Creole only); the fielded wording is not
##deposited, so the stored text is the PAP's English.
##Attribute order randomized per task (PAP: "the order of attributes will be randomized"), recorded
##in q0t_t0t_order as a 6-letter string (a administers, b beneficiary, c collects, i improvement,
##p purpose, r recognition; every string is a permutation of these letters, checked) ->
##attrpos_<attr> = position 1-6.
##Weight: weight (RIWI post-stratification weight; used as pweight in Main Analysis.do) ->
##cov_survey_weight.
##Covariates: cov_gender (gender), cov_age (age, years), cov_age_group (age_group, "18_24" ->
##"18-24", "65_and_over" -> "65 and over"), cov_education (q08, English answer text of
##Questionnaire.pdf Q8), cov_region (region, department), cov_date (survey date); q06-q07,
##q09-q20 keep the deposit's word codes (e.g. cov_q18_safety = "somewhat_unsafe"), which name the
##questionnaire's answer options. Dropped: uuid (RIWI respondent id; ids re-keyed 1..N in file
##order), city, user agent / OS / device, timestamps, dwell times, RIWI bookkeeping (context,
##answers, count, updated), the consent/instruction fields, and Experiments 2-3 (q04 rental-tax
##discount and q05 donor vignettes: one manipulated factor each, not conjoints).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "haiti_apr.dta"))))
s <- s[uuid != ""]
stopifnot(nrow(s) == 2001, !anyDuplicated(s$uuid))
s[, rid := seq_len(.N)]
mp <- function(x, m) { stopifnot(all(x %in% names(m))); unname(m[x]) }
M <- list(
  administers = c(central_govt = "Taxes will be administered by the central government",
                  municipal_govt = "Taxes will be administered by the municipal (commune) government"),
  collects = c(govt_officers_bureaucrats = "Taxes will be collected door-to-door by government officers / bureaucrats",
               community_leaders_chiefs = "Taxes will be collected door-to-door by notables or community leaders / local chiefs",
               foreign_donors_ngos = "Taxes will be collected door-to-door by foreign donor /NGOs workers",
               local_ngos = "Taxes will be collected door-to-door by local NGOs workers",
               local_church_workers = "Taxes will be collected door-to-door by local churches workers"),
  purpose = c(education_healthcare = "Increased spending in education and healthcare",
              transportation_roads = "Increased spending in transportation and roads",
              public_security = "Increased spending in public security",
              water_sanitation = "Increased spending in water and sanitation",
              waste_collection = "Increased spending in waste collection"),
  improvement = c(immediately = "Substantially improve immediately", "1_year" = "Substantially improve in 1 year",
                  "2_years" = "Substantially improve in 2 years", "5_years" = "Substantially improve in 5 years",
                  "10_years" = "Substantially improve in 10 years"),
  beneficiary = c(extremely_poor = "Extreme poor households", low_income = "Low-income households",
                  low_low_middle_class = "Low- and low middle-class households",
                  low_middle_class = "Low- and middle-class households", everyone = "Everyone"),
  recognition = c(none = "None", plaque_honour = "Taxpayers will receive a plaque of honor.",
                  recognition_seals_pasted = "Recognition seals will be pasted in the exterior of the taxpayers' households.",
                  names_local_paper_social_media = "Taxpayers' names will be published in the local newspaper and social media",
                  names_announced_local_radio = "Taxpayers' names will be announced in the local radio"))
letter <- c(administers = "a", beneficiary = "b", collects = "c", improvement = "i", purpose = "p", recognition = "r")
L <- list()
for (t in 1:3) for (p in 1:2) {
  q <- sprintf("q%02d", t)
  ev <- s[[sprintf("%s_tax_evaluation_t%02d", q, t)]]; od <- s[[sprintf("%s_t%02d_order", q, t)]]
  stopifnot(all(ev %in% c("a", "b")), all(sapply(strsplit(od, ""), function(x) identical(sort(x), sort(unname(letter))))))
  x <- data.table(id = s$rid, task = t, profile = p, choice = as.integer(ev == c("a", "b")[p]))
  for (k in names(M)) x[, paste0("attr_", k) := mp(s[[sprintf("%s_c%d_%s", q, p, k)]], M[[k]])]
  for (k in names(M)) x[, paste0("attrpos_", k) := regexpr(letter[[k]], od, fixed = TRUE)]
  L[[length(L) + 1]] <- x
}
d <- rbindlist(L)
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
ed <- c(none = "None", primary_incomplete = "Primary incomplete", primary_complete = "Primary complete",
        secondary_incomplete = "Secondary incomplete", secondary_complete = "Secondary complete",
        technical_school_incomplete = "Technical school/Associate degree incomplete",
        technical_school_complete = "Technical school/Associate degree complete",
        university_incomplete = "University (bachelor's degree or higher) incomplete",
        university_complete = "University (bachelor's degree or higher) complete")
na <- function(x) fifelse(x == "", NA_character_, x)
stopifnot(all(s$gender %in% c("female", "male")), all(s$q08_education %in% c(names(ed), "")))
cv <- s[, .(id = rid, cov_survey_weight = weight, cov_gender = gender, cov_age = as.integer(age),
            cov_age_group = sub("_and_over", " and over", sub("^([0-9]+)_([0-9]+)$", "\\1-\\2", age_group)),
            cov_education = fifelse(q08_education == "", NA_character_, unname(ed[q08_education])),
            cov_region = na(region), cov_date = as.character(as.IDate(as.character(date_num), format = "%Y%m%d")),
            cov_q06_living = na(q06_living), cov_q07_house = na(q07_house), cov_q09_civil_status = na(q09_civil_status),
            cov_q10_employment = na(q10_employment_status), cov_q11_race = na(q11_race),
            cov_q12_relatives_abroad = na(q12_relatives_living_abroad), cov_q13_remittances = na(q13_dependent_on_remittance),
            cov_q14_emigration_intention = na(q14_intentions_moving_abroad), cov_q15_class = na(q15_belonging),
            cov_q16_household_income = na(q16_household_income), cov_q17_crime_victim = na(q17_crime_victim),
            cov_q18_safety = na(q18_safety_in_neighborhood), cov_q19_gangs = na(q19_affected_by_gangs),
            cov_q20_more_taxes = na(q20_more_taxes))]
stopifnot(!anyNA(cv$cov_survey_weight), !anyNA(cv$cov_date))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lopezgarcia_2025_haiti_property_tax.csv"))
