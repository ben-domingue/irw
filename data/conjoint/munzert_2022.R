##COVID-19 vaccine prioritization conjoint (Brazil, Germany, Italy, Poland, US) from
##Munzert, S., Ramirez-Ruiz, S., Çalı, B., Stoetzer, L. F., Gohdes, A., & Lowe, W. (2022).
##Prioritization preferences for COVID-19 vaccination are consistent across five countries.
##Humanities and Social Sciences Communications, 9, 439. https://doi.org/10.1057/s41599-022-01392-1
##Replication data: Harvard Dataverse doi:10.7910/DVN/OAMAOE, CC0 1.0. File read: conjoint_df.rds.
##Read as text only: README.md, 01-main-text.R, 02-appendix.R, supplemental-appendix.pdf (Supp. Figs 4-5
##screenshots, Supp. Table 4); article full text (Europe PMC PMC9735138).
##Usage: Rscript munzert_2022.R <dir holding conjoint_df.rds> <output dir>
##
##Respondi online panels, 8 Sep - 9 Dec 2020 (article n = 4,366; 4,365 respondents in the file),
##4 forced-choice tasks (time 1-4) of two persons (cand a/b = Person A/B), 7 attributes. One table
##with cov_country: the authors pool the five samples (sample-size weighted) and the attribute set is
##shared. Respondents saw the survey in their language (Q_Language: DE, EN, IT, PL, PT-BR); the
##deposit stores the levels in English and the outcome wording is the English instrument (Supp. Fig 5):
##"Please look at the profiles of the two persons thoroughly and then make your decision. Note: Please
##assume that the vaccine is both safe and effective [...] Which person would you prioritize for access
##to the vaccine?" Person A / Person B, forced choice. choice = pat_pref.
##Attributes (article: "The attribute levels were completely randomized. The order of the attributes was
##randomized between participants so they would see attributes in the same ordering for all profiles";
##order not recorded): Gender (Male/Female), Age (27/42/61/76), Has children (Yes/No), Job (Unemployed,
##Cook, Professor, Physician, Nurse, and Teacher ONLY in the German survey), Citizenship, Pre-existing
##condition (Yes/No), Early registration for vaccination (Yes/No). Citizenship is stored as the authors'
##labels "Country" (citizen of the respondent's country; the US screenshot shows "US") and "Other Country"
##(non-citizen); the displayed text in each country is not deposited.
##Cleaning: the file repeats the conjoint rows of 237 respondents 2-6 times (a covariate join: the
##repeats carry identical conjoint values but conflicting covariates, e.g. leftright NA vs 4); conjoint
##rows are de-duplicated, and a covariate that takes more than one non-missing value across a
##respondent's repeats is set NA. 120 tasks (67 respondents) with no recorded choice are dropped; 11
##respondents have no choice at all, leaving 4,354 respondents = Supp. Table 4 "N Clusters" (pooled).
##Covariates (text from the factor labels in the .rds): cov_country, cov_language (Q_Language),
##cov_birth_year ("What is your year of birth?"; "Please select..." -> NA), cov_gender ("Please state your
##gender." Male/Female/Other -> male/female/other), cov_education (English answer text as stored),
##cov_health_condition, cov_precondition, cov_leftright (1 furthest left - 11 furthest right),
##cov_trust_* (1 not trust at all - 5 complete trust: fedgov, stategov, sci, media, hc). Dropped: the
##derived political_lean, trust_cat_*, trust_institutions_pca, the duplicate "Has children" column,
##children_household (missing for most), ResponseId/personid (re-keyed), and `weight`, which is not a
##survey weight but the per-country sample-size weight used to pool the countries.
##Spot check: LPM of choice on the attributes weighted by `weight` gives Nurse +0.30, Physician +0.29,
##Teacher +0.16, precondition +0.14 vs Unemployed (Supp. Table 4 pooled: 0.30, 0.29, 0.16, 0.14); US
##sample unweighted: Nurse 0.33, Physician 0.31, age 76 0.20 (table: 0.33, 0.32, 0.20).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "conjoint_df.rds")))
for (v in names(s)) if (is.factor(s[[v]])) set(s, j = v, value = as.character(s[[v]]))
conj <- c("personid", "time", "cand", "Age", "Citizenship", "EarlyRegistration", "Gender", "Children", "Job", "Precondition", "pat_pref", "country", "Q_Language")
cj <- unique(s[, ..conj])
stopifnot(cj[, .N, .(personid, time, cand)][, all(N == 1)])
cj <- cj[!is.na(pat_pref)]
stopifnot(cj[, .N, .(personid, time)][, all(N == 2)], cj[, sum(pat_pref), .(personid, time)][, all(V1 == 1)])
cvars <- c(birthyear = "cov_birth_year", resp_gender = "cov_gender", resp_education = "cov_education",
           resp_health_condition = "cov_health_condition", resp_precondition = "cov_precondition", leftright = "cov_leftright",
           trust_institutions_fedgov = "cov_trust_fedgov", trust_institutions_stategov = "cov_trust_stategov",
           trust_institutions_sci = "cov_trust_sci", trust_institutions_media = "cov_trust_media", trust_institutions_hc = "cov_trust_hc")
one <- function(x) { u <- unique(x[!is.na(x)]); if (length(u) == 1) u else x[NA_integer_][1] }
cv <- s[, lapply(.SD, one), by = personid, .SDcols = names(cvars)]
setnames(cv, names(cvars), cvars)
cv[cov_birth_year == "Please select...", cov_birth_year := NA]
cv[, cov_birth_year := as.integer(cov_birth_year)]
stopifnot(all(cv$cov_gender %in% c("Male", "Female", "Other", NA)))
cv[, cov_gender := c(Male = "male", Female = "female", Other = "other")[cov_gender]]
cv[, cov_education := trimws(gsub("\\s+", " ", cov_education))]
for (v in c("cov_leftright", grep("^cov_trust", names(cv), value = TRUE))) set(cv, j = v, value = as.integer(cv[[v]]))
ids <- data.table(personid = sort(unique(cj$personid)))[, id := .I]
d <- cj[, .(personid, task = as.integer(time), profile = match(cand, c("a", "b")), choice = as.integer(pat_pref),
            attr_gender = Gender, attr_age = Age, attr_has_children = Children, attr_job = Job, attr_citizenship = Citizenship,
            attr_preexisting_condition = Precondition, attr_early_registration = EarlyRegistration,
            cov_country = country, cov_language = Q_Language)]
stopifnot(!anyNA(d))
d <- merge(merge(d, ids, by = "personid"), cv, by = "personid")
d[, personid := NULL]
setcolorder(d, c("id", "task", "profile", "choice"))
stopifnot(uniqueN(d$id) == 4354, d[attr_job == "Teacher", all(cov_country == "Germany")])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "munzert_2022_vaccine_priority.csv"))
