##Restaurant-choice conjoint on hiring initiatives (US, YouGov) from
##Shi, L., & Denver, M. (2025). The transferal of criminal record stigma in the employment
##context: Evidence from conjoint and vignette experiments. Criminology, 63(1), 89-121.
##https://doi.org/10.1111/1745-9125.12398
##Replication data: Harvard Dataverse doi:10.7910/DVN/UOC2HR, CC0 1.0. File read:
##"Conjoint Data 01.04.25.dta" (Dataverse "original format"); "Data Dictionary.xlsx",
##"Read me.docx" and "Conjoint Do File 02.28.25.do" read as text. The vignette experiment
##in the same deposit (Vignette Data 02.06.25.dta) is a vignette, not a conjoint: not built.
##The article was not read (publisher and preprint pages refused automated access).
##Usage: Rscript shi_2025.R <dir holding "Conjoint Data 01.04.25.dta"> <output dir>
##
##998 YouGov respondents (dictionary: "998 unique values. Each respondent completed five
##tasks, and there are two profiles in each task, leading to 9,980 observations"), 5 pairs
##of restaurants, 5 attributes each "randomly assigned in each profile" (dictionary).
##The file has NO task or profile column: each respondent has exactly 10 consecutive rows,
##and in every consecutive pair exactly one restaurant is preferred, so task and profile
##are INFERRED from row order (checked below).
##Attribute text: the .dta value labels with Stata's numlabel prefix ("1. ") removed:
##distance (10-minute WALK / 20-minute DRIVE), price per person ($ (under $10) ... $$$$
##(over $61)), online reviews about food quality (Excellent / Mixed / Negative), hiring
##initiative (More employees / People who identify as LGBTQ / People with a criminal
##conviction record / Veterans), staff composition (Mostly black and Hispanic / Mostly
##white). The Data Dictionary disagrees with the .dta in two places: it gives staff codes
##the other way round (1 = Mostly white) and calls the worst review "Terrible". The .dta
##labels are kept because the authors' do-file uses them (numlabel) and because Black
##respondents prefer code 1 (weighted 59% vs 42% for code 2), which fits "Mostly black and
##Hispanic". The dictionary's longer LGBTQ text ("[lesbian, gay, bisexual, transgender, or
##queer]") may be what was displayed; not verifiable.
##Outcome: choice = pref, "restaurant preference" (1 = preferred); exact wording not in the
##deposit. Forced choice, no opt-out. Restrictions not documented.
##Check (weighted OLS, SEs clustered by id, as in the do-file): criminal-record hiring
##initiative -0.078 (SE 0.016) vs "More employees", the courtesy stigma the abstract reports;
##no published number was available to compare.
##Covariates: cov_survey_weight (YouGov "Gen Pop Weight"), cov_race (1 White, 2 Black,
##3 Other race). caseid (YouGov case id) re-keyed to integers.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "Conjoint Data 01.04.25.dta"))
s <- as.data.table(zap_labels(k))
stopifnot(nrow(s) == 9980, uniqueN(s$caseid) == 998, s[, .N, caseid][, all(N == 10)],
          rle(as.numeric(s$caseid))$lengths == 10)
s[, r := seq_len(.N), caseid][, task := (r + 1L) %/% 2L][, profile := 2L - r %% 2L]
stopifnot(s[, sum(pref), .(caseid, task)][, all(V1 == 1)])
lab <- function(v) { l <- attr(k[[v]], "labels"); sub("^[0-9]+\\. ", "", names(l)[match(s[[v]], l)]) }
key <- unique(s$caseid)
d <- s[, .(id = match(caseid, key), task = as.integer(task), profile = as.integer(profile), choice = as.integer(pref))]
d[, `:=`(attr_distance = lab("p_distance"), attr_price = lab("p_price"), attr_review = lab("p_review"),
         attr_hiring_initiative = lab("p_initiative"), attr_staff = lab("p_staff"))]
d[, `:=`(cov_survey_weight = s$weight, cov_race = as.integer(s$race_WBO))]
stopifnot(!anyNA(d[, .(attr_distance, attr_price, attr_review, attr_hiring_initiative, attr_staff)]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "shi_2025_restaurant_hiring.csv"))
