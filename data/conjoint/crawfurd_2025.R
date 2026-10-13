##Two discrete choice experiments with education policymakers (35 countries) from
##Crawfurd, L., Hares, S., Minardi, A., & Sandefur, J. (2025). Understanding education policy
##preferences: Survey experiments with policymakers in 35 developing countries. World
##Development, 196, 107140. (The article reports 931 officials; the .dta has 932 rows.)
##https://doi.org/10.1016/j.worlddev.2025.107140
##Replication data: Harvard Dataverse doi:10.7910/DVN/E0TDA8, CC0 1.0 (depositor Lee Crawfurd).
##Files read (inside education-policymaker-preferences-codes-and-data.zip):
##input/aid_finaldataset.dta; Questionnaire.pdf; do-files "1. Clean and create variables.do",
##"3. DCE 1 - Projects.do", "4. DCE 2 - Outcomes.do" read as text.
##Usage: Rscript crawfurd_2025.R <dir holding aid_finaldataset.dta> <output dir>
##
##932 rows = government officials (CGD survey, Qualtrics, online and in person; English or French),
##two DCEs with different attribute sets = TWO tables:
##  crawfurd_2025_aid_projects (DCE 1): "(k/6) Now I am going to ask you about some
##    hypothetical aid projects. I am going to describe two aid projects and ask you to choose
##    which one you would prefer." Project 1 / Project 2 / "None of these options". Attributes
##    (Qualtrics conjoint fields, English text as stored): attr_project (Computers / Technology,
##    Foundational literacy, Learning Assessment, School construction, Technical and Vocational
##    Education), attr_technical_assistance (None, 1 Full-time Technical Advisor, 2 Full-time
##    Technical Advisors), attr_budget ($30/32/35/37/40 million). 6 tasks.
##  crawfurd_2025_education_outcomes (DCE 2): "There are multiple possible goals of an
##    education system - to provide everyone with basic skills such as literacy, to create
##    dutiful citizens, or to identify the brightest children and prepare them for leadership
##    roles. Imagine you had to choose between the outcomes of two education systems, which do
##    you prefer?" System 1 / System 2 / "None of these options". Attributes: attr_foundational
##    _literacy (row "Gain foundational literacy (%)": 60, 80, 100), attr_secondary_completion
##    ("Complete secondary school (%)": 30, 50, 70), attr_dutiful_citizens ("Dutiful citizens
##    (%)": 70, 80, 90, 100); stored as the source numbers (the row label carries the %). 4 tasks.
##Task = round (dce1_r1..r6 / dce2_r1..r4, rd_<round>_<a|b>_*), profile 1 = A (left), 2 = B.
##choice: A/B -> the chosen profile 1; C ("None of these options") = OPT-OUT, choice 0 on both
##profiles (DCE1 about 6% of tasks, DCE2 about 5%). Blank answers (task not answered) are
##dropped. Attribute values are missing for DCE1 on 176 rows and DCE2 on 50 rows; most of
##them (DCE1 175 online respondents, DCE2 45) nevertheless have an answer, i.e. the levels were
##NOT SAVED; those tasks are dropped (the authors' do-files drop them too: drop if
##rd1_project1=="" / rd1_completesecondaryschool1==.). No in-person respondent (online = 0)
##chose "None" in either DCE (0 of about 340), so the opt-out may not have been offered in
##person; not documented.
##Displayed language: English or French (lang_french); only the English attribute text is
##deposited. Randomization: Qualtrics conjoint; no restrictions or weights documented.
##trial_preamble: the respondent-level randomized survey preamble shown at the start
##(1 Control, 2 DFID, 3 Gates, 4 ADB funding statement; labels from the authors' cleaning do-file).
##Covariates: cov_gender from `male` (1 -> male, 0 -> female; NA = "Rather not say"/missing;
##the authors' do-files use `male` as the gender control), cov_region (regioncode value labels:
##Anglophone Africa, Francophone Africa, Asia/Pacific, Other), cov_agency (agencyid value label
##text), cov_subnational, cov_current_emp, cov_experience (years at the ministry, as stored),
##cov_online (1 = online, 0 = in person), cov_googlelist (sample-frame flag, as stored),
##cov_lang_french, cov_duration_sec (Qualtrics durationinseconds).
##Respondent = row of the .dta (responseid is blank for 3 rows and duplicated for 2; the authors'
##do-files also number rows, `gen id=_n`), re-keyed in row order among DCE respondents.
##Dropped for confidentiality: Qualtrics response ids (responseid, responseid2, resp_id),
##dates, job title (jobtitle/titlecode, e.g. "Minister") and country (country_id; with job title
##and agency it could identify individual senior officials; country codes also carry no labels
##in the deposit). The questionnaire asked name, phone and email; none of these are in the .dta.
##Check: a linear probability model of choice on the three DCE2 percentages (opt-out tasks
##excluded, as in the do-file) gives literacy/secondary and literacy/citizens coefficient ratios
##of 1.16 and 1.47, against the do-file's plotted labels 1.16 and 1.46.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "aid_finaldataset.dta"))
stopifnot(nrow(k) == 932)
lab <- function(x) { v <- as.character(as_factor(x, levels = "labels")); fifelse(v == "", NA_character_, v) }
cv <- data.table(rid = seq_len(nrow(k)),
                 cov_gender = c("female", "male")[as.integer(zap_labels(k$male)) + 1L],
                 cov_region = lab(k$regioncode), cov_agency = lab(k$agencyid),
                 cov_subnational = as.integer(zap_labels(k$subnational)), cov_current_emp = as.integer(zap_labels(k$current_emp)),
                 cov_experience = as.numeric(zap_labels(k$experience)), cov_online = as.integer(zap_labels(k$online)),
                 cov_googlelist = as.integer(zap_labels(k$googlelist)), cov_lang_french = as.integer(zap_labels(k$lang_french)),
                 cov_duration_sec = as.numeric(zap_labels(k$durationinseconds)))
stopifnot(all(k$male %in% c(0, 1, NA)), !anyNA(cv$cov_region))
pre <- as.integer(zap_labels(k$preamble)); stopifnot(all(pre %in% 1:4))
pre <- c("Control", "DFID", "Gates", "ADB")[pre]
build <- function(dce, rounds, vars, newnames, name, fmt = as.character) {
  rows <- list()
  for (t in seq_len(rounds)) {
    ans <- as.character(k[[sprintf("dce%d_r%d", dce, t)]])
    for (p in 1:2) {
      x <- data.table(rid = seq_len(nrow(k)), task = t, profile = p, ans = ans, trial_preamble = pre)
      for (j in seq_along(vars)) {
        v <- k[[sprintf("rd_%d_%s_%s", t, c("a", "b")[p], vars[j])]]
        v <- if (is.numeric(v)) ifelse(is.na(v), NA_character_, fmt(as.numeric(v))) else fifelse(as.character(v) == "", NA_character_, as.character(v))
        x[, (paste0("attr_", newnames[j])) := v]
      }
      rows[[length(rows) + 1]] <- x
    }
  }
  d <- rbindlist(rows)
  shown <- d[, !is.na(get(paste0("attr_", newnames[1])))]
  cat(name, "answered tasks with no saved attributes (dropped):", d[!shown & ans %in% c("A", "B", "C"), uniqueN(paste(rid, task))], "in", d[!shown & ans %in% c("A", "B", "C"), uniqueN(rid)], "respondents\n")
  d <- d[shown & ans %in% c("A", "B", "C")]
  stopifnot(!anyNA(d), d[, .N, .(rid, task)][, all(N == 2)])
  d[, choice := as.integer(ans == c("A", "B")[profile])][, ans := NULL]
  stopifnot(d[, sum(choice), .(rid, task)][, all(V1 <= 1)])
  d <- merge(d, cv, by = "rid", sort = FALSE)
  ids <- sort(unique(d$rid)); d[, id := match(rid, ids)][, rid := NULL]
  setcolorder(d, c("id", "task", "profile", "choice"))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
  cat(name, nrow(d), uniqueN(d$id), "optout tasks", d[, sum(choice), .(id, task)][, sum(V1 == 0)], "of", uniqueN(d[, .(id, task)]), "\n")
}
build(1, 6, c("project", "technicalassistance", "budget"), c("project", "technical_assistance", "budget"), "crawfurd_2025_aid_projects")
build(2, 4, c("gainfoundationalliteracy", "completesecondaryschool", "dutifulcitizens"),
      c("foundational_literacy", "secondary_completion", "dutiful_citizens"), "crawfurd_2025_education_outcomes",
      fmt = function(x) as.character(as.integer(x)))
