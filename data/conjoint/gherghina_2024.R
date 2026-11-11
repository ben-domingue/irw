##Romanian parliamentary-candidate paired conjoint on electoral clientelism, from
##Gherghina, S., & Saikkonen, I. A.-L. (2024). Partisanship and tolerance for clientelism:
##Evidence from a conjoint experiment in Romania. Political Studies, 72(3), 1250-1266.
##https://doi.org/10.1177/00323217231178994 (OA; read from the Glasgow eprints copy 298515.pdf)
##Replication data: Harvard Dataverse doi:10.7910/DVN/IYDSYP, CC0 1.0. File read:
##RO_conjoint_replication_data.tab (Dataverse "original format" .dta; no value labels, no codebook).
##Usage: Rscript gherghina_2024.R <dir holding data.dta> <output dir>   (data.dta = the original .dta)
##
##1,010 respondents (paper n = 1010), Romanian online panel, May-June 2021, 6 tasks (question) x
##2 candidates (choice = candidate 1/2); 12,120 rows, exactly one chosen per task (checked).
##Outcome choice = votechoice: "If you had to choose between these two candidates in elections, which
##one would you vote for?" (paper p. 1256, English translation; answers 'Candidate 1'/'Candidate 2',
##forced choice, no opt-out).
##"The attribute combinations were not restricted in any way" (paper p. 1256); attribute order not stated.
##CODED ATTRIBUTES (#3474). The deposit stores the five attributes as bare numbers with no value
##labels, codebook or code. Paper Table 1 lists the levels (English translation; shown in Romanian):
##  attr_gender_code 1-2       Female / Male
##  attr_education_code 1-2    Intermediate / High
##  attr_party_code 1-4        PNL / USR-PLUS / PSD / AUR
##  attr_clientelism_code 1-3  did NOT offer welfare benefits or money / offered preferential access
##                             to welfare benefits / offered 250 RON in exchange for the vote
##  attr_policy_code 1-2       did NOT promise jobs / promised to increase the number of jobs
##but no source says which code is which level, so the codes are kept as deposited. (Co-partisan
##choice rates are consistent with party codes following Table 1 order - code 1 highest among PNL
##identifiers, 3 among PSD, 4 among AUR - but that is not a stated mapping and is not applied.)
##Gender is therefore a coded attribute and has no crosswalk rows.
##Dropped: c/c2/c3 (candidate index and derived copies of the choice), dc (a Da/Nu per task whose
##meaning is not documented), question_set (undocumented per-respondent number), free-text
##"_text" answers, and the remaining questionnaire items whose wording is not deposited.
##Covariates (Romanian answer text as deposited): cov_age_group (q15), cov_gender (q17: Masculin =
##male, Feminin = female), cov_county (q19, judet), cov_education (q21), cov_region (region, the
##deposit's four development regions Unu..Patru), cov_close_to_party (q36 Da/Nu), cov_party_id (q38,
##party felt close to, asked of those answering Da; blank otherwise -> NA), cov_vote_2020 (q42, party
##voted for in the 2020 legislative elections, incl. "Nu am votat"). Item meanings for q36/q38/q42 are
##read from the answer sets against the paper's description of the CSES closeness item and the 2020
##vote question (p. 1256-57); the deposit has no codebook.
##No survey weight. No exclusions. responseid re-keyed to 1..n.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(zap_labels(read_dta(file.path(raw, "data.dta"))))
stopifnot(nrow(k) == 12120L, uniqueN(k$responseid) == 1010L)
d <- data.table(id = match(k$responseid, sort(unique(k$responseid))), task = as.integer(k$question),
                profile = as.integer(k$choice), choice = as.integer(k$votechoice))
stopifnot(d[, .N, .(id, task)][, all(N == 2L)], d[, sum(choice), .(id, task)][, all(V1 == 1L)])
src <- c(gender = "gen", education = "educ", party = "partisanship", clientelism = "posclient", policy = "publicpol")
nl <- c(gender = 2L, education = 2L, party = 4L, clientelism = 3L, policy = 2L)
for (v in names(src)) { x <- as.integer(k[[src[[v]]]]); stopifnot(all(x %in% seq_len(nl[[v]]))); d[, paste0("attr_", v, "_code") := x] }
txt <- function(x) { x <- trimws(as.character(x)); x[x == ""] <- NA_character_; x }
d[, cov_age_group := txt(k$q15)]
stopifnot(all(k$q17 %in% c("Masculin", "Feminin")))
d[, cov_gender := fifelse(k$q17 == "Masculin", "male", "female")]
d[, cov_county := txt(k$q19)]
d[, cov_education := txt(k$q21)]
d[, cov_region := txt(k$region)]
d[, cov_close_to_party := txt(k$q36)]
d[, cov_party_id := txt(k$q38)]
d[, cov_vote_2020 := txt(k$q42)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gherghina_2024_clientelism_romania.csv"))
