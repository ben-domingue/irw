##Asylum-seeker conjoint, 2022 wave (15 European countries) from
##Bansak, K., Hainmueller, J., & Hangartner, D. (2023). Europeans' support for refugees of
##varying background is stable over time. Nature, 620(7975), 849-854.
##https://doi.org/10.1038/s41586-023-06417-6 (open access, PMC10447233)
##Replication data: Harvard Dataverse doi:10.7910/DVN/FTL1MM (v2), CC0 1.0. Files read (from
##replication_materials.zip): data/conjoint_data_2022.csv, data/respondent_data_2022.csv,
##with data/conjoint_data_codebook.txt and data/respondent_data_codebook.txt. The code/
##folder was read as text, not run.
##Usage: Rscript bansak_2023.R <dir holding the two 2022 .csv files> <output dir>
##
##The deposit also holds the 2016 wave (conjoint_data_2016.csv, 18,030 respondents). That is
##the experiment already in IRW as bansak_2016_asylum (doi:10.7910/DVN/KL0FDF, same
##design and count), so it is NOT rebuilt here.
##bansak_2023_asylum_2022: online survey (Respondi and partners, May-June 2022) of about
##  1,000 respondents in each of Austria, Czech Republic, Denmark, France, Germany, Greece,
##  Hungary, Italy, Netherlands, Norway, Poland, Spain, Sweden, Switzerland, United Kingdom.
##  ONE TABLE with cov_country: the authors pool the countries, the design is the same
##  everywhere, and the deposit holds only the English master labels (as in
##  bansak_2016_asylum). Each respondent saw 5 pairs of asylum-seeker profiles (task A-E,
##  prof A1, A2, B1, ... -> task 1-5, profile 1-2), 9 attributes; level text is the
##  deposit's English labels (language skills appear as "Fluent" / "Broken" / "None"; the
##  respondent's national language was named on screen, per the paper). The 2022 design
##  adds Ukraine as an origin. Attribute order was randomized across respondents and fixed
##  across a respondent's five pairs (paper, Methods), but the order is not in the deposit.
##  No randomization restrictions are documented.
##  Outcomes: choice = pref, forced choice of the one applicant the respondent would prefer
##    to be allowed to stay (no opt-out; every pair has exactly one chosen profile).
##    rating = rate, 1 = "absolutely send the applicant back" (codebook; the paper says
##    "definitely send the applicant back") ... 7 = "definitely allow the applicant to
##    stay"; higher = more favourable, raw scale kept. Exact question wording is in the
##    article's Supplementary Information, not retrieved. ratebin (rate > 4) is dropped.
##  trial_frame: one of four frames shown at the start of the survey (general,
##    mediterranean, afghanistan, ukraine; wording in the SI); respondent-level.
##  Covariates (source codes, see the respondent codebook): cov_country, cov_gender,
##    cov_age, cov_home_born, cov_educ_eisced (1-7), cov_emp_status (text), cov_inc_decile,
##    cov_ideo (0 left - 10 right), cov_feel_therm_* (0-100: compatriots, Afghanistan,
##    Eritrea, Iraq, Kosovo, Pakistan, Syria, Ukraine), cov_asy_change_home,
##    cov_asy_change_europe, cov_immig_change_home (-2 greatly decrease .. 2 greatly
##    increase), cov_cosmo_1..4, cov_nat_1..4 (-2..2; cosmo_1 is reverse-coded in the
##    source, as documented), cov_eu_view, cov_nato_view, cov_rus_polec_threat (0-2),
##    cov_rus_milit_threat (0-4), cov_nato_intervene, cov_rus_invas_threat;
##    cov_survey_weight (weight: age, gender, education margins) and cov_survey_weight_alt
##    (alt_weight: also ideology). Dropped: cosmo_index and nat_index (derived), the
##    Qualtrics ResponseIds (re-keyed to integers). 120 respondents have no weight (blank
##    cov_survey_weight) in the deposit.
##  10 respondents (100 profiles) have no attribute levels in the deposit and are dropped:
##  14,966 respondents kept. The paper reports 14,976 for 2022, which counts them.
##Spot-check: weighted forced-choice AMCE of Ukraine vs the mean of the other six origins
##  = 5.5 pp (vs Syria 4.95 pp, SE 0.61, clustered by id), matching the paper's 5.5 pp.
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "conjoint_data_2022.csv"))
r <- fread(file.path(raw, "respondent_data_2022.csv"))
stopifnot(uniqueN(k$ResponseId) == 14976, k[, .N, ResponseId][, all(N == 10)], setequal(k$ResponseId, r$ResponseId))
attrs <- c(cconsist = "asylum_testimony", cgender = "gender", corigin = "country_of_origin", cage = "age",
           cjob = "previous_occupation", cvulner = "vulnerability", creason = "reason_for_migrating",
           creligion = "religion", clang = "language_skills")
bad <- k[is.na(corigin), unique(ResponseId)]
stopifnot(length(bad) == 10, k[ResponseId %in% bad, all(is.na(cconsist) & is.na(clang))])
k <- k[!ResponseId %in% bad]
stopifnot(!anyNA(k[, names(attrs), with = FALSE]))
ids <- data.table(ResponseId = sort(unique(k$ResponseId)))[, id := seq_len(.N)]
k <- merge(k, ids, by = "ResponseId")
d <- k[, .(id, task = match(task, LETTERS[1:5]), profile = as.integer(substr(prof, 2, 2)),
           choice = as.integer(pref), rating = as.integer(rate))]
stopifnot(k[, all(substr(prof, 1, 1) == task)])
for (v in names(attrs)) d[, paste0("attr_", attrs[[v]]) := k[[v]]]
d[, ResponseId := k$ResponseId]
rv <- c("cty", "gender", "age", "home_born", "educ_EISCED", "emp_status", "inc_decile", "ideo",
        grep("^feel_therm_", names(r), value = TRUE), "asy_change_home", "asy_change_europe", "immig_change_home",
        paste0("cosmo_", 1:4), paste0("nat_", 1:4), "eu_view", "nato_view", "rus_polec_threat", "rus_milit_threat",
        "nato_intervene", "rus_invas_threat", "weight", "alt_weight")
rr <- r[, c("ResponseId", "frame", rv), with = FALSE]
setnames(rr, rv, paste0("cov_", tolower(rv)))
setnames(rr, c("frame", "cov_cty", "cov_weight", "cov_alt_weight"), c("trial_frame", "cov_country", "cov_survey_weight", "cov_survey_weight_alt"))
d <- merge(d, rr, by = "ResponseId")[, ResponseId := NULL]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(d$id) == 14966, nrow(d) == 149660)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bansak_2023_asylum_2022.csv"))
