##Venezuelan/Peruvian migrant conjoint (Colombia) from
##Argote, P., & Daly, S. Z. (2024). The formation of attitudes toward immigration in
##Colombia. International Interactions, 50(2), 370-384.
##https://doi.org/10.1080/03050629.2024.2309999
##Replication data: Harvard Dataverse doi:10.7910/DVN/0K48FZ, CC0 1.0. File read:
##ipsos_rep.dta (Dataverse "original format" download of ipsos_rep.tab). The deposit's
##README.docx and .do files and output tables were read as text; nothing was run.
##Usage: Rscript argote_2024.R <dir holding ipsos_rep.dta> <output dir>
##
##Face-to-face Ipsos survey of Colombian adults. ONE task of two hypothetical migrant
##profiles per respondent (source column `contest` = profile 1/2), 8 two-level attributes.
##No codebook or questionnaire ships and the article is paywalled, so:
##  - Level TEXT is the authors' English labels from the .dta variable labels of their
##    dummy columns (exp8_<attr>_1/_2 labelled "Venezuela"/"Peru", "Low-skilled"/
##    "High-skilled", "Less than 40"/"More than 40", "Male"/"Female", "Alone"/"With family",
##    "Right"/"Left", "Yes"/"No", "Political asylum"/"Economic opportunities"); each code of
##    exp8_<attr> maps 1:1 to one dummy (checked). Respondents saw Spanish text that the
##    deposit does not contain. Attribute names (country of origin, skills, age, gender,
##    travelling alone/with family, ideology, Colombian relatives, reason for migrating)
##    follow the authors' coefplot headings and table notes ("No Colombian relatives").
##  - Outcome wording is not in the deposit. choice = choice_exp8 (which migrant preferred;
##    exactly one of the two chosen whenever answered). rating = support_exp8, 1-7; its
##    direction is INFERRED: chosen profiles average 4.7, unchosen 3.0, and the authors'
##    support AMCEs have the same signs as the choice AMCEs, so 7 = most support.
##  - Attribute order and randomization restrictions are not documented.
##Rows: 1,515 respondents (2 rows each). 5 have no attributes (dropped). Kept: profiles
##with choice or rating; choice is missing (not an opt-out) for 423 rows answered only on
##support. 1,429 respondents kept; 1,214 answered the choice (2,428 rows) and 2,811 rows
##carry support, matching the Obs. counts of the authors' Table D1 (2,428 / 2,811). The
##article's total N is not checked (paywalled).
##Covariates (source codes, Ipsos variable names in brackets): cov_age (years, [EDAD]
##continuous), cov_female (gender 2; the authors' balance table uses gender==2 as
##"Female"), cov_urban (urban_cat 1; the authors use urban_cat==1 as "Urban"), cov_nse
##(socio-economic stratum code, 0-6 [NSE]), cov_education (code 1-7 [D3A], labels not in
##the deposit; higher = more education is implied by the authors' "college" dummy but not
##verified), cov_region (Ipsos region, text, accents repaired).
##Dropped: respondent_serial (in some rows it holds an entire raw survey record, including
##a phone number, an email address and free text, so it is replaced by integer ids), the
##authors' dummies and derived variables (exp8_*_1/2, female1/2, nse_*, college, left,
##right, low_income, unemployed*, *_no_missing, response, non_response, response_hat, ipw),
##municipio/departamento (and their encodings), f2_1, number_ven and frequency_ven
##(Ipsos items I4/I5 with no labels in the deposit).
##Spot-check: lm(choice ~ 8 attributes) with SEs clustered by respondent reproduces all 8
##estimates and SEs of the authors' Table D1 column 1 (e.g. Venezuela -0.067 (0.020),
##Low-skilled -0.107); lm(rating ~ same) reproduces all 8 of column 3 (Venezuela -0.334).
suppressMessages({library(haven); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(zap_labels(read_dta(file.path(raw, "ipsos_rep.dta"))))
stopifnot(nrow(k) == 3030, k[, .N, respondent_serial][, all(N == 2)])
k[, id := rleid(respondent_serial)]
stopifnot(uniqueN(k$id) == 1515, k[, .(s = sort(contest)), id][, all(s == 1:2)])
lv <- list(country = c("Venezuela", "Peru"), skills = c("Low-skilled", "High-skilled"), age = c("Less than 40", "More than 40"),
           gender = c("Male", "Female"), travelling = c("Alone", "With family"), ideology = c("Right", "Left"),
           colombian_relatives = c("Yes", "No"), reason = c("Political asylum", "Economic opportunities"))
src <- c(country = "exp8_country", skills = "exp8_skill", age = "exp8_age", gender = "exp8_gender", travelling = "exp8_number",
         ideology = "exp8_ideology", colombian_relatives = "exp8_relatives", reason = "exp8_reasons")
for (v in names(src)) for (j in 1:2) stopifnot(all(k[get(src[[v]]) == j][[paste0(src[[v]], "_", j)]] == 1))
k <- k[!is.na(exp8_country)]
d <- k[, .(id, task = 1L, profile = as.integer(contest), choice = as.integer(choice_exp8), rating = as.integer(support_exp8))]
for (v in names(src)) d[, paste0("attr_", v) := lv[[v]][k[[src[[v]]]]]]
fixenc <- function(x) { y <- iconv(x, "UTF-8", "latin1"); y <- ifelse(is.na(y), x, y); y[y == ""] <- NA; y }
d[, `:=`(cov_age = as.integer(k$age_continuous), cov_female = as.integer(k$gender == 2), cov_urban = as.integer(k$urban_cat == 1),
         cov_nse = as.integer(k$nse), cov_education = as.integer(k$education), cov_region = fixenc(k$region))]
d <- d[!is.na(choice) | !is.na(rating)]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)],
          d[!is.na(choice), .N] == 2428, d[!is.na(rating), .N] == 2811, all(d$rating %in% c(1:7, NA)))
ids <- unique(d$id); d[, id := match(id, ids)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "argote_2024_migrants_colombia.csv"))
