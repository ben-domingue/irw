##Immigrant-admission conjoint (SSI 2014) from
##Berinsky, A. J., Rizzo, T., Rosenzweig, L. R., & Heaps, E. (2020). Attribute affinity: U.S.
##natives' attitudes toward immigrants. Political Behavior, 42(3), 745-768 (online 2018).
##https://doi.org/10.1007/s11109-018-9518-9
##Replication data: Harvard Dataverse doi:10.7910/DVN/FRGHVR, CC0 1.0. File read:
##SSI_conjoint_2014.dta (Dataverse "original format" download). Wording and response codes:
##SSI_conjoint2014_qualtricsreport.pdf in the deposit (Qualtrics results report).
##Usage: Rscript berinsky_2020.R <dir holding the .dta> <output dir>
##
##Only the SSI 2014 study is a conjoint. The deposit's other files are not: YouGov_religion_2013
##(direct questions), Mturk_rel_2013, Mturk15_long and Omnibus15_long (single-vignette survey
##experiments manipulating religion/religiosity of one immigrant). They are not converted.
##
##SSI (Survey Sampling International) online panel, US adults, January 2014. The .dta has 20 rows per respondent (caseid 1-1,737);
##imm_num 1-20 is the immigrant's number in the survey ("Immigrant 1" ... "Immigrant 20"),
##consecutive pairs forming one task, so task = (imm_num + 1) %/% 2 and profile = the source's
##profile column (1 = Immigrant 1/left). Verified: imm_num runs 1..20 in order for every
##respondent and profile == 2 - imm_num %% 2. The Qualtrics report shows two survey branches:
##about 1,385 respondents saw 7 pairs, about 236 saw 10 pairs (the data agree: tasks 8-10 have
##~228 answers). The branch variable is not in the data; it is visible as the number of tasks.
##Tasks a respondent did not answer (no choice and no rating) are omitted:
##1,627 respondents keep at least one answered task (1,623 with a choice). The article reports
##1,571 respondents; the deposit has 1,737 caseids and the difference is not explained (the
##authors' code applies no respondent filter beyond the analysis subsets).
##Per the article, respondents of minority religions (Mormon, Orthodox, Jewish, Muslim, Buddhist,
##Hindu, atheist, agnostic) got 10 pairs, everyone else 7. In the data cov_religion 3-9 got 10
##pairs; agnostics (10) got 7, unlike the article's description. The design asks respondents to act as
##an immigration official choosing whom to admit.
##Six attributes; attribute order was randomized across respondents (the report tabulates the
##attribute name in each row position) but the order is not in the .dta, so no attrpos_*.
##Displayed attribute names: Country of Origin, Language Skills, Attends Religious Services,
##Gender, Religion, Education Level. Level text = the .dta value labels (the displayed text).
##Restriction: an Atheist immigrant always has "Never" for religious attendance; Atheist was
##drawn less often (1,140 of 34,740 profiles) than the other five religions (~6,700 each).
##Outcomes (both asked about every pair):
##  choice = "Please choose one: Immigrant 1 / Immigrant 2" (forced choice, no opt-out; the
##           report does not show the full stem; the authors label it "Immigrant Preferred for
##           Admission to U.S.").
##  rating = "On a scale from 1 to 7, where 1 indicates that the United States should absolutely
##           not admit the immigrant and 7 indicates that the United States should definitely
##           admit the immigrant, how would you rate Immigrant 1 and Immigrant 2?" 7 = definitely
##           admit (higher = more favourable).
##  70 tasks have ratings but no choice (choice blank); 15 tasks have a choice but a rating
##  for one or neither profile. Rows with no outcome are omitted, so one task (rated for one
##  immigrant only, no choice) has a single row.
##Covariates (source codes; wording from the report):
##  cov_gender 1 male 2 female; cov_birth_year (from the Qualtrics year-of-birth code);
##  cov_race_black/asian/white/latino/nativeamerican/middleeast/other: 1 = selected, 0 = not
##  (multi-select; all missing if none selected); cov_education 1 did not graduate HS, 2 HS
##  graduate, 3 some college, 4 2-year degree, 5 4-year degree, 6 postgraduate;
##  cov_religion 1 Protestant 2 Roman Catholic 3 Mormon 4 Orthodox 5 Jewish 6 Muslim 7 Buddhist
##  8 Hindu 9 Atheist 10 Agnostic 11 None; cov_attends 1 more than once a week ... 6 never;
##  cov_believe_god 1 yes 2 no; cov_religion_importance (source codes) 6 extremely, 11 very,
##  7 somewhat, 8 not very, 10 not at all important; cov_other_language_home 1 yes 2 no;
##  cov_employed 1 no 2 yes; cov_ft_* feeling thermometers 0-100 (Protestants, Catholics,
##  Mormons, Orthodox, Jews, Muslims, Buddhists, Hindus, atheists, agnostics, Asians, feminists,
##  business, working class); cov_party_id 1 Democrat 2 Republican 3 Independent 4 other;
##  cov_strong_dem / cov_strong_rep 1 strong 2 not very strong; cov_state 1-52 (the report's
##  list: 50 states alphabetical with D.C. and Puerto Rico); cov_legal_immigration ("number of
##  legal immigrants ... should be" 1 increased a lot ... 5 reduced a lot, asked after the
##  conjoint); cov_deport_illegal ("All illegal immigrants should be deported", 1 agree strongly
##  ... 5 disagree strongly).
##Spot check (2026-10-07): all eight cells of the article's Table 6 (mean ratings rescaled to
##0-1 by respondent and immigrant religiosity, Muslim vs non-Muslim) reproduce to 2 decimals,
##with the cell N of 621 respondents.
##Dropped: sm_index (derived self-monitoring index), imm_num. No survey weight ships.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "SSI_conjoint_2014.dta")))
stopifnot(nrow(s) == 34740, s[, all(imm_num == 1:20), caseid]$V1, all(s$profile == 2 - s$imm_num %% 2))
lab <- function(v) as.character(as_factor(v))
d <- s[, .(id = as.integer(caseid), task = as.integer((imm_num + 1) %/% 2), profile = as.integer(profile),
           choice = as.integer(choice), rating = as.integer(rating),
           attr_country = lab(country), attr_language = lab(language), attr_attends = lab(attends),
           attr_gender = lab(gender), attr_religion = lab(religion), attr_education = lab(education))]
z <- function(v) as.integer(zap_labels(v))
d[, cov_gender := z(s$gender_resp)]
ag <- z(s$age)  # Qualtrics codes: 1 = 1996, 2-75 = 1973 down to 1900, 97 = 1993, 98 = 1992, 99 = 1995, 100 = 1994, 101-118 = 1991 down to 1974
by <- rep(NA_integer_, length(ag))
by[ag %in% 1] <- 1996L; i <- ag %in% 2:75; by[i] <- 1975L - ag[i]
by[ag %in% 97] <- 1993L; by[ag %in% 98] <- 1992L; by[ag %in% 99] <- 1995L; by[ag %in% 100] <- 1994L
i <- ag %in% 101:118; by[i] <- 1991L - (ag[i] - 101L)
stopifnot(sum(is.na(by)) == sum(is.na(ag)))
d[, cov_birth_year := by]
race <- c("black", "asian", "white", "latino", "nativeamerican", "middleeast", "other")
anyr <- Reduce(`|`, lapply(race, function(v) !is.na(s[[v]])))
for (v in race) d[, paste0("cov_race_", v) := fifelse(anyr, as.integer(!is.na(s[[v]])), NA_integer_)]
covs <- c(education_resp = "education", religion_resp = "religion", attends_resp = "attends", believegod_resp = "believe_god",
          rel_important_resp = "religion_importance", english_resp = "other_language_home", employed_resp = "employed",
          ft_prot = "ft_protestant", ft_cat = "ft_catholic", ft_mor = "ft_mormon", ft_ort = "ft_orthodox", ft_jew = "ft_jewish",
          ft_mus = "ft_muslim", ft_bud = "ft_buddhist", ft_hin = "ft_hindu", ft_ath = "ft_atheist", ft_ag = "ft_agnostic",
          ft_asian = "ft_asian", ft_fem = "ft_feminist", ft_business = "ft_business", ft_workingclass = "ft_workingclass",
          pid = "party_id", strongdem = "strong_dem", strongrep = "strong_rep", state = "state", numbimm = "legal_immigration",
          illegalimm = "deport_illegal")
for (v in names(covs)) d[, paste0("cov_", covs[[v]]) := z(s[[v]])]
d <- d[!is.na(choice) | !is.na(rating)]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, sum(choice), .(id, task)][!is.na(V1), all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "berinsky_2020_immigrant_admission.csv"))
