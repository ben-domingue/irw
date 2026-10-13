##Four factorial vignettes from the "Public Goods through Private Eyes" (PGPE) survey of 14 post-communist
##countries: Letki, N. (2025). Public goods through private eyes. Exploring citizens' attitudes to public goods
##and the state in Central Eastern Europe [dataset]. Dane Badawcze UW (Warsaw RepOD Dataverse),
##https://doi.org/10.58132/SBJIW0, CC BY 4.0 (file-level licence "CC BY Creative Commons Attribution License
##4.0" in the Dataverse API; no terms of use/access, no guestbook, no restricted files). The deposit is declared a
##supplement to Gorecki, M. A., & Letki, N. (2020). Social norms moderate the effect of tax system on tax
##evasion: Evidence from a large-scale survey experiment. Journal of Business Ethics, 172, 727-746.
##https://doi.org/10.1007/s10551-020-04502-8 (which uses only vignette F01).
##File read: PGPE_main.dta (Stata original with English value labels, 22,039 respondents x 451 variables),
##PGPE_Master_English_Questionnaire.pdf (vignette wording), PGPE_Project_read_before_using_the_dataset.pdf
##("A03, B02, F01 and G04 are vignettes. A full factorial design was used in all cases; each respondent was
##presented with only one version of the vignette") and PGPE_Project_general_information_1.pdf (sampling,
##weights). Usage: Rscript letki_2025.R <dir holding PGPE_main.dta> <output dir>
##Sample: face-to-face (CAPI/PAPI) national probability surveys, 2013-2014, 1,412-1,879 respondents in each of
##14 countries (Bulgaria, Croatia, Czech Republic, Estonia, Hungary, Latvia, Lithuania, Moldova, Poland, Romania,
##Serbia, Slovakia, Slovenia, Ukraine; Russia has a value label but no rows). Fieldwork: IPSOS (CBOS in Poland).
##TABLES (one per vignette, each a different attribute set; respondents saw one version of every vignette, so
##each table has one row per respondent, task = profile = 1, id = row number of the file, identical across the four tables):
##  letki_2025_park_cleanup     A03  3 x 3 x 3  join an initiative to clean up a local park
##  letki_2025_donation         B02  3 x 4 x 3  give a donation
##  letki_2025_tax_evasion      F01  6 x 4 x 2  not declare cash income to the Tax Office (the article's vignette)
##  letki_2025_bottle_recycling G04  5 x 2 x 3  use a facility to dispose of glass bottles
##Countries are POOLED within each table (cov_country): the experiment is the same, the level text is the English
##MASTER questionnaire text (the value labels), and the authors analyse the pooled sample. The national translations
##the respondents actually read are not in the deposit, so label_language = en. The master text keeps its
##placeholders ("[country]", "[1x single ride public transport ticket in the capital city]"), which were filled in
##locally; they are stored as in the labels.
##Outcome (rating, no choice, no opt-out): "How likely is it that YOU will join / make THIS DONATION / not declare this
##income / be using these facilities?" on CARD: 1 Very likely, 2 Fairly likely, 3 Not very likely, 4 Not likely at all.
##LOWER = MORE LIKELY (kept raw). 998 Don't know and 999 Refusal are set to NA and the row is dropped (rows with no
##outcome are omitted): A03 478, B02 693, F01 2,735, G04 604 respondents lose their row.
##Level text: the value labels of A03_a/b/c, B02_a/b/c, F01_a/b/c, G04_a/b/c. The levels the master questionnaire
##shows as "-" (A03 incentive, level 1) and "--" (F01 penalty level 1, F01 consultation desk level 1) mean the
##clause was left off the vignette: stored as "(not shown)" (Ben 10-07 ruling).
##Randomization restrictions: none (full factorial, independent). Level probabilities are not stated (cell shares are
##close to equal). The attribute order is the fixed slot order of the vignette sentence.
##Covariates: cov_country (COUNTRY value label), cov_birth_year (I04year), cov_age_group (AGE_GROUP label text),
##cov_education (I06 ISCED value label text, 'Don t know'/'Refusal' -> NA), cov_survey_weight (ADweight_tr1b:
##"Combined weights after trimming ESS style", mean 1; the deposit also holds Dweight, ADweight, ADweight_co and
##ADweight_tr, and the read-before-use note names different weight variables, so which weight the authors use is
##not documented). cov_gender is NOT kept: the file has two respondent-sex variables that contradict each other
##(sex: A man/A woman = 9,176/12,863; GENDER man/woman = 11,334/10,705; they agree for only 7,439 of 22,039 rows),
##and neither is documented beyond the interviewer instruction "Code respondent's sex".
##Dropped: all other questionnaire items, interviewer id (J07_an), PSU ids, regional variables, interview date/year,
##exact age (age, computed with decimals).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "PGPE_main.dta"), col_select = c(COUNTRY, starts_with("A03"), starts_with("B02"),
  starts_with("F01"), starts_with("G04"), I04year, AGE_GROUP, I06, ADweight_tr1b)))
s <- s[, .SD, .SDcols = unique(names(s))]
stopifnot(nrow(s) == 22039)
lab <- function(x) { l <- attr(x, "labels"); names(l)[match(as.numeric(x), l)] }
cov <- data.table(id = seq_len(nrow(s)), cov_country = lab(s$COUNTRY), cov_birth_year = as.integer(s$I04year),
  cov_age_group = lab(s$AGE_GROUP), cov_education = lab(s$I06), cov_survey_weight = as.numeric(s$ADweight_tr1b))
cov[cov_education %in% c("Don t know", "Refusal"), cov_education := NA]
stopifnot(!anyNA(cov$cov_country), !anyNA(cov$cov_birth_year), !anyNA(cov$cov_survey_weight), cov[, uniqueN(cov_country)] == 14)
mk <- function(v, attrs, name) {
  d <- data.table(id = cov$id, task = 1L, profile = 1L, rating = as.integer(s[[v]]))
  for (j in seq_along(attrs)) {
    x <- s[[paste0(v, "_", letters[j])]]; t <- lab(x)
    t[t %in% c("-", "--")] <- "(not shown)"
    stopifnot(!anyNA(t))
    d[[paste0("attr_", attrs[j])]] <- t
  }
  nd <- sum(!d$rating %in% 1:4)
  d <- d[rating %in% 1:4]
  d <- merge(d, cov, by = "id"); setcolorder(d, c("id", "task", "profile", "rating")); setorder(d, id)
  fwrite(d, file.path(out, paste0(name, ".csv")))
  cat(name, "rows", nrow(d), "dropped (DK/refusal)", nd, "\n")
}
mk("A03", c("visit_frequency", "others_joining", "incentive"), "letki_2025_park_cleanup")
mk("B02", c("requester", "amount", "purpose"), "letki_2025_donation")
mk("F01", c("tax_rate", "penalty_if_discovered", "consultation_desk"), "letki_2025_tax_evasion")
mk("G04", c("distance", "machine_type", "others_using"), "letki_2025_bottle_recycling")
