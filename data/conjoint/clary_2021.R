##Pakistani legislative-candidate paired conjoint (foreign policy toward India), from
##Clary, C., & Siddiqui, N. (2021). Voters and foreign policy: Evidence from a conjoint experiment
##in Pakistan. Foreign Policy Analysis, 17(2), orab001. https://doi.org/10.1093/fpa/orab001
##(paywalled; not read: OUP 403 here).
##Replication data: Harvard Dataverse doi:10.7910/DVN/96J0CP, CC0 1.0. Files read:
##clary_siddiqui_fpa_replication.tab (Dataverse "original format" .dta, for the value labels) and
##clary-siddiqui_fpa_replication.do + clary_siddiqui_replication_log.smcl (as text).
##Usage: Rscript clary_2021.R <dir holding rep.dta> <output dir>   (rep.dta = the original .dta)
##
##1,990 respondents (Dataverse description: "1,990 respondents conducted in Pakistan in
##October-November 2015"), face-to-face in Punjab, Khyber Pakhtunkhwa and Sindh (do-file: 50/20/30%),
##3 tasks (set) x 2 candidates (candidate); 11,940 rows, exactly one chosen per task (checked).
##Outcomes: choice = forced (the forced-choice pick between the two candidates; wording not
##deposited); rating = likert, 1-7 as recorded. The do-file quotes the paper: "Candidates supporting
##friendly relations with India were rated 0.01 points lower", i.e. higher = rated more favourably;
##the anchors and wording are not deposited.
##Four survey versions (file: 1 Punjab, 2 KPK, 3 Sindh Urban, 4 Sindh Rural; one per respondent)
##show different party sets, and the Sindh Urban version shows the candidate's ethnic group
##(ethnic) in place of the biradari attribute: biradari is missing on exactly every version-3 row
##and ethnic on exactly every other row, so the missing attribute is "(not shown)" (a design pattern
##inferred from that complementarity; no source states it). The authors pool the versions
##(do-file: pooled reg forced india, with province splits) -> one table, trial_version.
##CODED ATTRIBUTES (#3474). The .dta value labels are truncated to 8 characters and there is no
##codebook or questionnaire, so every attribute keeps the deposit's codes:
##  attr_party_code: the label as deposited (PPP, PML-N, PTI, Indep., ANP, PML-F, MQM; party names,
##    one-to-one with the codes 1,2,3,4,11,22,44; the displayed form, Urdu text or symbol, unknown)
##  attr_biradari_code: 1, 2 (labels "Your bir" and "Your bir": both truncated "Your biradari...";
##    which is co-biradari is not documented)
##  attr_ethnic_code: 1 "Sindhi", 2 "Mohajir-", 3 "Pathan" (candidate ethnic group; Sindh Urban only)
##  attr_campaign_code: 1 "Hired go", 2 "ran a pe" (truncated labels)
##  attr_agenda_code: 1 "Favor yo", 2 "reduce c", 3 "favor yo", 4 "improve" (truncated labels)
##  attr_india_code: 1 "A hard l" (hard line toward India), 2 "Friendly" (friendly relations with
##    India; the do-file comments name the two levels this way)
##No source says whether combinations were restricted or how attribute order was set.
##Covariates: cov_gender (gender: 0 Male = male, 1 Female = female, .dta value labels), cov_age
##(age, years), cov_rural (0 Urban, 1 Rural), cov_province (Punjab / KPK / Sindh, value labels),
##cov_party_id (close_to_party "Which political party do you fe[el closest to]", value-label text;
##99 "NR / DK" kept as text because it mixes refusal and don't know), cov_vote_party (same labels),
##and codes whose labels are truncated or mis-encoded: cov_ethnicity_code (1 Muhajir, 2 Punjabi,
##3 Sindhi, 4 Baloch, 5 Saraiki, 6 Pathan, 7 Other, 99 NR/DK per the readable fragments and the
##do-file), cov_income_code (1-6 increasing bands, 98 NR), cov_education_code (1 Illiterate,
##2 Madressa, 3 Primary, 4 Middle, 5 Matriculation, 6 Intermediate, 7 Graduate, 8 Masters, 99 NR/DK,
##from the truncated labels), cov_india_threat_code (q50 "How serious of a threat is India": 1 very
##serious .. 4 not serious, 99 NR/DK).
##No survey weight. No exclusions. new_id is already a 1..n integer.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "rep.dta"))
z <- as.data.table(zap_labels(k))
stopifnot(nrow(z) == 11940L, uniqueN(z$new_id) == 1990L)
lab <- function(v) as.character(as_factor(k[[v]], levels = "labels"))
d <- data.table(id = as.integer(z$new_id), task = as.integer(z$set), profile = as.integer(z$candidate),
                choice = as.integer(z$forced), rating = as.integer(z$likert))
stopifnot(all(d$rating %in% 1:7), d[, sum(choice), .(id, task)][, all(V1 == 1L)], d[, .N, .(id, task)][, all(N == 2L)])
pl <- lab("party"); stopifnot(!anyNA(pl), uniqueN(pl) == uniqueN(z$party))
d[, attr_party_code := pl]
ns <- "(not shown)"
stopifnot(all(is.na(z$biradari) == (z$file == 3)), all(is.na(z$ethnic) == (z$file != 3)))
d[, attr_biradari_code := fifelse(is.na(z$biradari), ns, as.character(z$biradari))]
d[, attr_ethnic_code := fifelse(is.na(z$ethnic), ns, as.character(z$ethnic))]
for (v in c("campaign", "agenda", "india")) { stopifnot(!anyNA(z[[v]])); d[, paste0("attr_", v, "_code") := as.integer(z[[v]])] }
d[, trial_version := c("Punjab", "KPK", "Sindh Urban", "Sindh Rural")[z$file]]
stopifnot(!anyNA(d$trial_version), d[, uniqueN(trial_version), id][, all(V1 == 1L)])
stopifnot(all(z$gender %in% 0:1))
d[, cov_gender := c("male", "female")[z$gender + 1L]]
d[, cov_age := as.integer(z$age)]
d[, cov_rural := as.integer(z$rural)]
d[, cov_province := lab("province")]
d[, cov_party_id := lab("close_to_party")]
d[, cov_vote_party := lab("vote_party")]
d[, cov_ethnicity_code := as.integer(z$ethnicity)]
d[, cov_income_code := as.integer(z$income)]
d[, cov_education_code := as.integer(z$education)]
d[, cov_india_threat_code := as.integer(z$q50)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "clary_2021_pakistan_candidates.csv"))
