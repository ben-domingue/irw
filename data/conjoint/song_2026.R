##Immigrant-admission conjoints in Japan and South Korea from
##Song, J., & Woo, Y. (2026). Replication data for: "Public support for migration policies in new
##immigration countries: Evidence from framing and conjoint experiments in East Asia" [Data set].
##Harvard Dataverse. https://doi.org/10.7910/DVN/VCN1BF
##The article (International Political Science Review, per the deposit's code file name) had no
##DOI that could be found on 2026-10-07.
##Replication data: Harvard Dataverse doi:10.7910/DVN/VCN1BF, CC0 1.0. Files read: dataset.tab
##(Dataverse "original format" download, a CSV) and IPSR_code.html (the authors' rendered online
##appendix: variable list, sampling, the attribute table in English/Japanese/Korean and the choice
##question; read as text, no code run).
##Usage: Rscript song_2026.R <dir holding dataset.csv> <output dir>
##
##Two tables, one per country: the authors analyse the samples separately (df_jp / df_kr) and one
##nationality level differs (Japanese respondents saw "Korea", Korean respondents "Japan").
##  song_2026_migrants_japan: Rakuten Insight online panel, 16-18 Aug 2021, 2,511 respondents after
##    the authors' quality screening (as in the appendix).
##  song_2026_migrants_korea: Dynata online panel, 13-22 Oct 2020, 1,991 respondents (as in the
##    appendix).
##Each respondent saw 5 tasks of 2 prospective immigrants, 7 attributes: gender, age (25-65),
##nationality (Japan or Korea, USA, France, China, Vietnam, Philippines), education, previous job,
##purpose (of entry), duration (of stay). attr_* hold the appendix's English level text; respondents
##saw the Japanese or Korean text listed beside it in the appendix. Levels fully randomized (the
##appendix shows uniform level frequencies); attribute order not recorded (no attrpos_).
##Outcome: choice = Outcome. The question (Japanese version, translated): "Below are the profiles of
##two immigrants. Keeping the situation above in mind, please choose the one immigrant whose
##admission you would support. Even if you cannot say clearly, please choose the one you would
##rather admit (none has a history of infectious diseases such as COVID-19)." Forced choice, no
##opt-out.
##trial_framing: the between-respondent framing arm read before the conjoint (Control; Treatment1 =
##government emphasis on marriage migrants; Treatment2 = emphasis on labor migrants).
##Covariates (the deposit's numeric codes; the appendix gives no value labels beyond the missing
##codes, which are set missing here: education 6, urban 4, married 3, children 4, income 999):
##cov_sex, cov_age (years), cov_education, cov_urban, cov_married, cov_children, cov_income,
##cov_survey_weight (post-stratification weight on sex and age; the authors weight all estimates).
##Dropped: ID (Qualtrics ResponseId; ids re-keyed to integers in file order).
##Spot check: the weighted marginal mean for female migrants in the Japanese sample is .518, as in
##the appendix's Table 7.1.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "dataset.csv"))
stopifnot(nrow(s) == 45020, s[, .N, .(ID, Task, Profile)][, all(N == 1)], s[, sum(Outcome), .(ID, Task)][, all(V1 == 1)])
s[, id := match(ID, unique(ID))]
miss <- function(x, code) { x <- as.integer(x); x[x %in% code] <- NA_integer_; x }
for (smp in c("Japanese", "Korean")) {
  k <- s[Sample == smp]
  d <- k[, .(id = match(id, unique(id)), task = as.integer(Task), profile = as.integer(Profile), choice = as.integer(Outcome),
             attr_gender = Sex, attr_age = as.character(Age), attr_nationality = Nationality, attr_education = Education,
             attr_previous_job = PreviousJob, attr_purpose = Purpose, attr_duration = Duration, trial_framing = Group,
             cov_sex = as.integer(R_Sex), cov_age = as.integer(R_Age), cov_education = miss(R_Educ, 6), cov_urban = miss(R_Urban, 4),
             cov_married = miss(R_Married, 3), cov_children = miss(R_Child, 4), cov_income = miss(R_Income, 999),
             cov_survey_weight = weight)]
  stopifnot(d[, .N, id][, all(N == 10)], uniqueN(d$id) == c(Japanese = 2511, Korean = 1991)[[smp]],
            d[, uniqueN(trial_framing), id][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("song_2026_migrants_", c(Japanese = "japan", Korean = "korea")[[smp]], ".csv")))
}
