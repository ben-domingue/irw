##Second-look sentencing factorial vignettes (US) from
##Smith, P., Graham, A., Cullen, F. T., Pickett, J. T., Jonson, C. L., Hannan, K. R., & Pompoco, A.
##(2025). Public support for universal second look sentencing, a research note. Criminology, 63(1),
##280-293. https://doi.org/10.1111/1745-9125.12391
##Replication data: Harvard Dataverse doi:10.7910/DVN/AD1BHL, CC0 1.0, no restricted files. File read:
##SLData - Public.sav (Dataverse "original format" download of SLData - Public.tab; the SPSS value labels
##supply the outcome wording/option text, the .tab holds the vignette text). Public Syntax.R read as text.
##Usage: Rscript smith_2025.R <dir holding SLData.sav> <output dir>
##
##800 YouGov US respondents (2023-07 national sample, weight_main). Each judged 3 hypothetical applications for
##second-look sentencing (task 1-3, one profile each), 8 randomized attributes shown as text: age (15, 20, 25, 30, 35 or
##40-years-old), gender (Female/Male), race (Black/White), crime (4), childhood
##(abuse / no abuse), rehabilitation (completed / not), warden statement, victim statement. Attribute texts are
##stored as shown in the .tab. Randomization restrictions are not documented in the deposit (no codebook or
##survey instrument; header-only evidence).
##Outcome (rating, from q3/q4/q5 "Vignette 1/2/3", SPSS value labels; question stem not in the deposit):
##  rating = judge's decision on the application, 1 Release from prison now, 2 Reduce sentence to 1-2 more years
##  in prison, 3 Deny application but suggest reapplying in 3 years, 4 Deny application permanently.
##  HIGHER = LESS favourable to release; stored as in the source. Not a choice (nothing is chosen among profiles).
##No respondent id is shared: caseid is a panel sample id, so id = row number of the file.
##Dropped: caseid, q2 (global second-look support) and q2_manipulation (message arm of that separate item, not
##a profile attribute), q19_* racial resentment items, employment, marital status, income, ideology, religion,
##region, race of the respondent, start/end times.
##Covariates: cov_gender (gender4: Man = male, Woman = female, Non-binary/Other = other; value labels),
##cov_birth_year (birthyr), cov_education (educ value-label text), cov_party_id7 (pid7 value-label text; "Not sure"
##and "Don't know" kept as answer text), cov_survey_weight (weight_main; all 800 non-missing).
##Count check: N = 800 as in the paper's abstract.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_sav(file.path(raw, "SLData.sav"))
n <- nrow(s)
lab <- function(v) as.character(as_factor(s[[v]], levels = "labels"))
cov <- data.table(id = seq_len(n),
  cov_gender = c("male", "female", "other", "other")[as.integer(zap_labels(s$gender4))],
  cov_birth_year = as.integer(zap_labels(s$birthyr)),
  cov_education = lab("educ"), cov_party_id7 = lab("pid7"),
  cov_survey_weight = as.numeric(s$weight_main))
av <- c(age = "age", gender = "gender", race = "race", crime = "crime", childhood = "childhood",
        rehabilitation = "rehabilitation", warden_statement = "warden_statement", victim_statement = "victim_statement")
L <- lapply(1:3, function(t) {
  d <- data.table(id = seq_len(n), task = t, profile = 1L, rating = as.integer(zap_labels(s[[paste0("q", t + 2)]])))
  for (k in names(av)) d[, paste0("attr_", k) := as.character(s[[paste0("v", t, "_", av[[k]])]])]
  d })
d <- rbindlist(L)
stopifnot(all(d$rating %in% 1:4), !anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
d <- merge(d, cov, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "smith_2025_second_look.csv"))
