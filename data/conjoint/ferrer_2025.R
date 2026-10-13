##Liberal-democracy conjoint (7 countries) from
##Ferrer, S., Hernandez, E., Prada, E., & Tomic, D. (2025). The value of liberal democracy: Assessing citizens' commitment to
##democratic principles. European Journal of Political Research, 64(4). https://doi.org/10.1111/1475-6765.70021
##Replication data: Harvard Dataverse doi:10.7910/DVN/GA9WBR, CC0 1.0. Files read: conjoint_general_final.dta (datafile 10992063,
##downloaded as the original Stata file, 90 MB; read with haven) and analysis_general_conjoint.do (as text; the readme.rtf files
##are boilerplate). Usage: Rscript ferrer_2025.R <dir holding conjoint_general_final.dta> <output dir>
##
##12,903 respondents in Hungary (2,301), Israel (1,501), Poland (1,500), Portugal (1,501), Spain (2,300), Sweden (1,500), UK (2,300)
##(country counts from the file), 5 tasks x 2 hypothetical countries (profiles), 7 attributes: elections, media, protests,
##judges, parliament, laws, and the income of the hypothetical country's citizens. All six institutional attributes have two levels.
##The file is one row per respondent x task x profile (129,030 rows = 12,903 x 5 x 2). Its column `round` is the task (1-5) and,
##counter-intuitively, its column `country` (1 or 2) is the profile position; `Country` is the respondent's country.
##Outcomes: select (1 = chosen; exactly one of the two chosen in every task: checked) and like (0-10 rating of the profile;
##567 missing, kept as NA). The question wording is not in the deposit (variable names select / like only) -> the design record gives a
##paraphrase; higher like = more liked (assumed from the name). No opt-out.
##Level text. Respondents saw their own language (Spanish, Portuguese, Polish, Hungarian, Hebrew, Swedish, English). The authors
##pool the countries (country fixed effects) after recoding each text to a binary level with Stata `encode` (the 14 distinct texts of an
##attribute sorted alphabetically, then the index lists in analysis_general_conjoint.do lines 32-90). That recode is reproduced here
##(C-locale sort), checked to give exactly one text per class in every country, and each class is stored as the UK (English)
##text that UK respondents saw: the texts are translations of one English master. attr_income is the authors' relative income level,
##recovered as the rank of the displayed amount within the country (0.8, 0.9, 1.0, 1.1, 1.25 times the average income, as in the
##do-file income_c recode; checked against the amount ratios); the amount actually displayed (local currency) is trial_income_shown.
##Attribute order and any restrictions are not documented (all level combinations occur). No covariates, no weight in the deposit.
##Count check: the Crossref abstract gives no N; the seven country samples sum to 12,903 as in the file. Not verified against the article text.
##Dropped: ResponseId (Qualtrics, re-keyed to an integer), Flow (all "Completed").
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_dta(file.path(raw, "conjoint_general_final.dta")))
stopifnot(nrow(d) == 129030, uniqueN(d$ResponseId) == 12903, d[, .N, ResponseId][, all(N == 10)])
setnames(d, c("country", "round"), c("profile", "task"))
stopifnot(d[, .N, .(ResponseId, task, profile)][, all(N == 1)], d[, sum(select), .(ResponseId, task)][, all(V1 == 1)])
cls <- list(
  elections  = list(`1` = c(1, 4, 5, 7, 9, 12, 14), `0` = c(2, 3, 6, 8, 10, 11, 13)),
  media      = list(`1` = c(1, 3, 7, 9, 10, 11, 13), `0` = c(2, 4, 5, 6, 8, 12, 14)),
  protest    = list(`1` = c(1, 4, 6, 10, 11, 12, 14), `0` = c(2, 3, 5, 7, 8, 9, 13)),
  laws       = list(`1` = c(1, 4, 6, 8, 9, 11, 13), `0` = c(2, 3, 5, 7, 10, 12, 14)),
  parliament = list(`1` = c(2, 4, 7, 9, 10, 12, 14), `0` = c(1, 3, 5, 6, 8, 11, 13)),
  judges     = list(`1` = c(2, 4, 6, 8, 9, 12, 14), `0` = c(1, 3, 5, 7, 10, 11, 13)))
for (v in names(cls)) {
  u <- sort(unique(d[[v]]), method = "radix"); stopifnot(length(u) == 14)
  cl <- integer(14); cl[cls[[v]][["1"]]] <- 1L; cl[cls[[v]][["0"]]] <- 0L
  map <- data.table(txt = u, cls = cl)
  chk <- merge(unique(d[, .(Country, txt = get(v))]), map, by = "txt")
  stopifnot(chk[, .(n = .N, k = uniqueN(cls)), Country][, all(n == 2 & k == 2)])
  uk <- chk[Country == "UK"]
  d[, (paste0("attr_", v)) := uk$txt[match(map$cls[match(get(v), map$txt)], uk$cls)]]
}
num <- function(s) as.numeric(gsub("[^0-9]", "", s))
d[, amt := num(income)]
d[, rk := frank(amt, ties.method = "dense"), by = Country]
stopifnot(d[, uniqueN(rk), Country][, all(V1 == 5)])
rel <- c(0.8, 0.9, 1, 1.1, 1.25)
chk <- unique(d[, .(Country, rk, amt)])[, .(ratio = amt / amt[rk == 3], rk), Country]
stopifnot(chk[, all(abs(ratio - rel[rk]) < 0.04)])
lab <- c("0.8 times avg. income", "0.9 times avg. income", "Avg. income", "1.1 times avg. income", "1.25 times avg. income")
d[, attr_income := lab[rk]]
r <- d[, .(id = match(ResponseId, unique(ResponseId)), task = as.integer(task), profile = as.integer(profile), choice = as.integer(select), rating = as.integer(like),
           attr_elections, attr_media, attr_protests = attr_protest, attr_judges, attr_parliament, attr_laws, attr_income,
           cov_country = fcase(Country == "Hungary", "HU", Country == "Israel", "IL", Country == "Poland", "PL", Country == "Portugal", "PT",
                               Country == "Spain", "ES", Country == "Sweden", "SE", Country == "UK", "GB"),
           trial_income_shown = trimws(income))]
setorder(r, id, task, profile)
stopifnot(!anyNA(r[, grep("^attr_", names(r)), with = FALSE]), !anyNA(r$cov_country))
fwrite(r, file.path(out, "ferrer_2025_liberal_democracy.csv"))
cat(file.size(file.path(out, "ferrer_2025_liberal_democracy.csv")) / 1e6, "MB\n")
