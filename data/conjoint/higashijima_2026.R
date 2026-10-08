##Immigrant-admission conjoint (Kazakhstan) from
##Higashijima, M., Igarashi, A., & Woo, Y. (2026). Do Muslim citizens welcome fundamentalist
##Muslim immigrants? Evidence from a conjoint experiment in Kazakhstan. Political Behavior.
##https://doi.org/10.1007/s11109-026-10177-0 (open access, CC BY-NC-ND 4.0; not readable
##from here, publisher login wall; NOT read)
##Replication data: Harvard Dataverse doi:10.7910/DVN/GJFYGX, CC0 1.0. Files read:
##kazakh_alldata_conjoint.csv (long file: one row per respondent x task x profile, English
##attribute text) and Data_MainSurvey.csv (wide file; respondent labels only). Also read as
##text: Marginal_AMCE.R, Projoint.R (the authors' analysis, not run).
##Usage: Rscript higashijima_2026.R <dir holding the two csv files> <output dir>
##
##3,000 adults across 17 regions of Kazakhstan, interviewer-administered (interviewer codes,
##PSUs), fielded January-February 2021 (TimeStart), in Russian (2,435) or Kazakh (565).
##3 tasks x 2 hypothetical immigrants ("Immigrant 1" / "Immigrant 2"), 10 attributes:
##education, gender, ethnicity, language, reason for coming, profession, job experience,
##religion, intended stay, legal status. task = `which` (_1.._3), profile = `WHICH`
##(_R1/_R2): recorded. Attribute text is the authors' English labels as stored in the long
##file (the Russian/Kazakh display text is not deposited); the long file's spellings are
##kept ("specialised", "Illegal entry"; the authors' R code spells them differently).
##Outcomes (same tasks, one table):
##  choice = `chosen` (from choice1-3, which immigrant was chosen: Immigrant 1 or 2; forced
##           choice, exactly one per task, checked; consistent with `choice` in every row).
##  rating = `rate` (ENGQ50, a 1-7 rating of each immigrant). Wording and anchors are not in
##           the deposit; chosen profiles average 4.3 vs 3.3, so higher = more favourable
##           (inferred). The authors call it the "rating measure" (Appendix C).
##  rating_sim = `sim` (ENGQ51, a second 1-7 rating of each immigrant). Wording, anchors and
##           meaning are NOT documented in the deposit ("sim" presumably similarity; not
##           verifiable). Chosen 3.1 vs not chosen 2.6.
##Randomization restrictions (authors' code: "two-way constraint", EDUCATION*JOB and
##ETHNICITY*LANGUAGE): in the data, computer programmer, doctor, financial analyst and
##research scientist occur only with university or postgraduate education, and Russian
##ethnicity occurs only with "Kazakh and Russian", "Russian and broken Kazakh" or "Russian
##and no Kazakh". Level probabilities are not documented; the shares are unequal (Russian
##ethnicity 762 profiles vs about 2,150 for the others; the four high-skill professions about
##570 vs about 1,970; university/postgraduate 1.5x the other education levels), which is what
##uniform draws under the two constraints would give. Attribute order is not documented or
##recorded, nor how the profiles were shown (interviewer-administered). No task is repeated
##(checked). No survey weight, attention check or duration in either file.
##All respondents are kept (the article analyses Muslim respondents, respondent_religion ==
##"Islam": 2,097 of 3,000 here).
##Covariates (labels from Data_MainSurvey.csv): cov_gender ("Are you male or female?",
##answer text Male/Female, lowercased to male/female), cov_age (AGE, years 18-75), cov_ethnicity,
##cov_region, cov_interview_language (RUS/KAZ), cov_religion (the authors' respondent_religion:
##Islam / Christinanity [sic] / No religion / blank = missing).
##Dropped: QUESTIONNAIREID/IdAnkety (survey UUIDs; re-keyed to integers), interviewer code,
##PSU, locality names, timestamps and all other survey items. The respondent name and phone
##columns (RESP1/RESP2; "ФИО РЕСПОНДЕНТА", "ТЕЛЕФОН РЕСПОНДЕНТА") are present but EMPTY in
##both files (checked). The survey also carried a protest-event conjoint (EVENT_ATTR_*), not
##part of this article; not built.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "kazakh_alldata_conjoint.csv"), encoding = "UTF-8")
m <- fread(file.path(raw, "Data_MainSurvey.csv"), encoding = "UTF-8", select = c(1, 6), col.names = c("IdAnkety", "lang"))
m2 <- fread(file.path(raw, "Data_MainSurvey.csv"), encoding = "UTF-8",
            select = c("IdAnkety", "Are you male or female?", "AGE", "What do you consider to be your ethnicity?", "Region"))
setnames(m2, c("IdAnkety", "gender", "age", "ethnicity", "region"))
m <- m[m2, on = "IdAnkety"]
stopifnot(nrow(s) == 18000, uniqueN(s$IdAnkety) == 3000, all(s$IdAnkety == s$QUESTIONNAIREID), nrow(m) == 3000,
          all(s$IdAnkety %in% m$IdAnkety))
s[, task := as.integer(sub("^_", "", which))][, profile := as.integer(sub("^_R", "", WHICH))]
ids <- unique(s$IdAnkety)
d <- s[, .(id = match(IdAnkety, ids), task, profile, choice = as.integer(chosen), rating = as.integer(rate),
           rating_sim = as.integer(sim),
           attr_education = EDUCATION, attr_gender = GENDER, attr_ethnicity = ETHNICITY, attr_language = LANGUAGE,
           attr_reason = REASON, attr_profession = JOB, attr_experience = EXPERIENCE, attr_religion = RELIGION,
           attr_stay = STAY, attr_legal_status = VISA, IdAnkety, rr = respondent_religion)]
stopifnot(s[, all(chosen == as.integer(choice == profile))])
d <- m[d, on = "IdAnkety"]
stopifnot(all(m$gender %in% c("Male", "Female")))
d[, `:=`(cov_gender = tolower(gender), cov_age = as.integer(age), cov_ethnicity = ethnicity, cov_region = region,
         cov_interview_language = lang, cov_religion = rr)]
d[, c("IdAnkety", "gender", "age", "ethnicity", "region", "lang", "rr") := NULL]
at <- grep("^attr_", names(d), value = TRUE)
stopifnot(!anyNA(d[, ..at]), d[, all(sapply(.SD, function(x) all(x != ""))), .SDcols = at],
          !anyDuplicated(d[, .(id, task, profile)]), d[, .N, id][, all(N == 6)],
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, all(rating %in% 1:7 & rating_sim %in% 1:7)])
setcolorder(d, c("id", "task", "profile", "choice", "rating", "rating_sim"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "higashijima_2026_muslim_immigrants.csv"))
