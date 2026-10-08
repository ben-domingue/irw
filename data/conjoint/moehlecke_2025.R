##Foreign-direct-investment conjoint (Brazil) from
##Moehlecke, C., Fasolin, G. N., & Spektor, M. (2025). Beyond jobs: When citizens reject socially
##irresponsible foreign direct investment. International Studies Quarterly, 69(3), sqaf046.
##https://doi.org/10.1093/isq/sqaf046
##Replication data: Harvard Dataverse doi:10.7910/DVN/JRX8YC, CC0 1.0, no restricted files.
##File read: fulldata_cov1.csv (inside beyondjobs_replication.zip). Variable meanings from the
##authors' beyondjobs_replication_conjoint.R (read as text) and the deposit readme.txt. The
##article and its supplement are paywalled and were not read: the question wording, survey
##firm and fielding details below are therefore NOT from the article.
##Usage: Rscript moehlecke_2025.R <raw dir> <output dir>
##
##2,008 Brazilian online-panel respondents (survey timestamps June 2022), 6 tasks ("set") of two
##firm profiles ("posicion" 1 = Empresa A, 2 = Empresa B), 8 attributes, Portuguese text as
##displayed (from the data; the authors' English labels in brackets):
##  attr_size [Large/Medium-sized], attr_origin [Brazil/China/U.S./Europe/Latin America],
##  attr_mode [partial acquisition/full acquisition/new facilities], attr_sales [domestic
##  market/exports], attr_jobs [many/few jobs in the state], attr_salaries [above/at national
##  average], attr_corruption [has been / never involved in corruption], attr_environment [has /
##  never caused environmental damage].
##Two outcomes on the same tasks (the source stores "Empresa A"/"Empresa B" on the chosen row):
##  choice_state  = P19, the authors' "sociotropic dependent variable (state)";
##  choice_family = P20, the "egotropic variable (oneself and one's family)".
##  Exact wording unknown (paraphrased in the design record). Forced choice: every task has
##  exactly one chosen firm on each outcome.
##Randomization: NOT independent per respondent. The source's design "version" (1-20, kept as
##  trial_version) fixes all 12 profiles: every respondent with the same version saw the same 6
##  pairs (240 version x task x profile cells), 100-103 respondents per version. Only 223 of the
##  960 possible profiles occur; binary levels are exactly balanced (12,048 rows each). Not
##  documented in the deposit. Attribute order not recorded.
##Covariates (Portuguese text as deposited, except cov_gender): cov_gender (source `sex`: Mulher ->
##  female, Homem -> male, as in the authors' code lines 193-194 'sex=="Homem", "Male"' /
##  'sex=="Mulher", "Female"'), cov_age (years), cov_class (NSE A..D-E),
##  cov_region, cov_state, cov_race (P25), cov_education (P26), cov_income (P28, monthly
##  household income bracket), cov_national_attachment_1..3 (P1 "something negative about
##  Brazilian people, how much do you feel it is about you?", P2 "to what extent does being
##  Brazilian influence how you feel about yourself?", P3 "how much do you feel that Brazil's
##  future is also your destiny?"), cov_chauvinism_1..3 (P5 "how superior is Brazil compared to
##  other nations?", P6 "how much better would the world be if foreigners were more like
##  Brazilians?", P7 "how many things about Brazil make you feel ashamed?"), cov_employed
##  (P10), cov_employment_type (P13), cov_sector (P14) (item paraphrases from the authors'
##  code comments), cov_education = P26 answer text (main education question, Portuguese
##  categories as deposited), cov_survey_weight (ponde; the authors run unweighted analyses).
##  No attention check in the deposit; no repeated task.
##Dropped: CodPanelista (panel member ID) and key/numericalId (survey IDs; respondents re-keyed
##  to integers), city, IBGE municipality codes and microregion (quasi-identifiers), device,
##  timestamps/durations, consent item, items whose meaning is not documented (P4, P9A, P11,
##  P15, P16, P18), the municipality-level FDI covariates merged by the authors.
##N: 2,008 complete respondents (status "end"); not compared with the article (unread).
##Spot check: lm(P19 ~ corruption * environment) gives the corruption coefficient -0.2685 noted
##  in the authors' code comment.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "fulldata_cov1.csv"), encoding = "UTF-8")
stopifnot(x[, .N, key][, all(N == 12)], x[, .N, .(key, set, posicion)][, all(N == 1)], all(x$status == "end"))
ids <- unique(x$key)
d <- data.table(id = match(x$key, ids), task = as.integer(x$set), profile = as.integer(x$posicion),
                choice_state = as.integer(x$P19 != "."), choice_family = as.integer(x$P20 != "."))
stopifnot(x[P19 != ".", all(P19 == c("Empresa A", "Empresa B")[posicion])], x[P20 != ".", all(P20 == c("Empresa A", "Empresa B")[posicion])])
an <- c(atr1 = "size", atr2 = "origin", atr3 = "mode", atr4 = "sales", atr5 = "jobs", atr6 = "salaries", atr7 = "corruption", atr8 = "environment")
for (v in names(an)) d[, paste0("attr_", an[[v]]) := x[[v]]]
stopifnot(!anyNA(d), all(d[, unlist(.SD), .SDcols = patterns("^attr_")] != ""))
d[, trial_version := as.integer(x$version)]
cv <- c(age = "age", class = "NSE", region = "REGIAO", state = "ESTADO", race = "P25", education = "P26",
        income = "P28", national_attachment_1 = "P1", national_attachment_2 = "P2", national_attachment_3 = "P3",
        chauvinism_1 = "P5", chauvinism_2 = "P6", chauvinism_3 = "P7", employed = "P10", employment_type = "P13",
        sector = "P14", survey_weight = "ponde")
stopifnot(all(x$sex %in% c("Mulher", "Homem")))
d[, cov_gender := c(Mulher = "female", Homem = "male")[x$sex]]
for (v in names(cv)) d[, paste0("cov_", v) := x[[cv[[v]]]]]
for (v in grep("^cov_", names(d), value = TRUE)) if (is.character(d[[v]])) set(d, i = which(d[[v]] == ""), j = v, value = NA)
stopifnot(d[, sum(choice_state), .(id, task)][, all(V1 == 1)], d[, sum(choice_family), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "moehlecke_2025_fdi.csv"))
