##Welfare deservingness conjoint (US) from
##Diessner, S., Durazzi, N., Filetti, F. D., Hope, D., Kleider, H., Limberg, J., & Tonelli, S.
##(2026). Welfare state deservingness in the era of mass higher education. Public Opinion
##Quarterly. https://doi.org/10.1093/poq/nfag056
##Replication data: Harvard Dataverse doi:10.7910/DVN/UQP5OG, CC0 1.0. File read:
##US Conjoint.csv (Dataverse "original format" download of the .tab; a Qualtrics export with
##one header row). Read as text: readme.txt, replication_diessneretal_poq.R. Question wording,
##sample and design from the article (OUP HTML, read via a summarising fetch).
##Usage: Rscript diessner_2026.R <dir holding us_conjoint.csv> <output dir>
##(the script expects the .csv saved as us_conjoint.csv)
##
##Prolific sample of US adults (quotas on sex, age, party), October 18-28 2024. 4,068 started,
##3,978 finished; the authors analyse 3,916 (finished and Duration > 180 s). Here every
##respondent with at least one answered task is kept (unfinished ones too), with
##cov_finished and cov_duration_sec so the authors' sample can be rebuilt.
##Profiles: two laid-off workers per task ("Worker 1" / "Worker 2"), 4 attributes, levels as
##displayed (Qualtrics F-<task>-<profile>-<k> cells): Age (25/40/55), Gender (Female/Male),
##Education (No college degree/College degree), Parental background (Lower/Middle/Upper class).
##Attribute row order was randomized once per respondent and kept across tasks (checked):
##attrpos_* = row position from the F-<task>-<k> name cells.
##Outcomes (article wording):
##  choice: "which of these two workers would you personally prefer to receive greater income
##    assistance from the government?" Worker 1 / Worker 2, no opt-out (Q2, Q6, Q9, Q12, Q15).
##  rating: "On a scale of 0-10, how much would you support Worker 1 [Worker 2] receiving income
##    assistance from the government?" 0 = Strongly oppose, 10 = Strongly support
##    (Q3_1/Q4_1, Q7_1/Q8_1, Q10_1/Q11_1, Q13_1/Q14_1, Q16_1/Q17_1, worker 1 then worker 2,
##    as in the authors' code). Higher = more support.
##  Task 6 repeats task 1 with the worker order reversed (article). It has no F- cells of its
##  own, so its profiles are task 1's profiles swapped (profile 1 = task 1 worker 2) and its
##  attrpos_ are task 1's; outcomes Q33 (choice), Q34_1/Q35_1 (ratings, assumed worker 1/2
##  like the other tasks). The reversal is supported by the data: Q2 x Q33 = 393/1657 vs
##  1682/259 (83% answer consistently under reversal). trial_repeat = 1 marks task 6.
##  The authors drop it from their main analyses.
##trial_ict_info = 1 if the respondent saw the information screen on ICT and the college
##  labour market before the conjoint (authors: TreatTime_Page Submit present), 0 = control.
##Covariates kept as the answer text (Qualtrics labels): age (years), gender, ethnicity
##  (multi-select, comma-joined), children, education, field of qualification, income,
##  employment, subjective class, trust, left-right, party, 2020 presidential vote, and three
##  0-7 items the authors use (InvestSkillsCollege_7, EasyJobCollege_7, WinnersICT_1;
##  wording not deposited). Dropped: Qualtrics ResponseId (re-keyed to row order),
##  Progress, Consent, timing of the info screens, OpenFeedback (free text).
##Tasks with no choice answer are omitted (ratings may be missing on kept tasks).
##Randomization: the authors' cjoint design uses no constraints; levels uniform (checked).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "us_conjoint.csv"), colClasses = "character", encoding = "UTF-8")
stopifnot(nrow(s) == 4068, s[, uniqueN(ResponseId)] == 4068)
s[, id := seq_len(.N)]
attrs <- c(Age = "age", Gender = "gender", Education = "education", `Parental background` = "parental_background")
qs <- list(c("Q2", "Q3_1", "Q4_1"), c("Q6", "Q7_1", "Q8_1"), c("Q9", "Q10_1", "Q11_1"),
           c("Q12", "Q13_1", "Q14_1"), c("Q15", "Q16_1", "Q17_1"), c("Q33", "Q34_1", "Q35_1"))
rows <- list()
for (t in 1:6) {
  ft <- if (t == 6) 1L else t
  for (p in 1:2) {
    fp <- if (t == 6) 3L - p else p
    d <- s[, .(id, task = t, profile = p, ch = get(qs[[t]][1]), rating = as.integer(get(qs[[t]][p + 1L])))]
    for (k in 1:4) {
      nm <- s[[sprintf("F-%d-%d", ft, k)]]; lv <- s[[sprintf("F-%d-%d-%d", ft, fp, k)]]
      for (an in names(attrs)) {
        hit <- nm == an
        d[hit, paste0("attr_", attrs[[an]]) := lv[hit]]
        d[hit, paste0("attrpos_", attrs[[an]]) := k]
      }
    }
    rows[[length(rows) + 1L]] <- d
  }
}
d <- rbindlist(rows, fill = TRUE)
d <- d[ch %in% c("Worker 1", "Worker 2")]
d[, choice := as.integer(ch == paste("Worker", profile))][, ch := NULL]
d[, trial_repeat := as.integer(task == 6L)]
cv <- s[, .(id, trial_ict_info = as.integer(`TreatTime_Page Submit` != ""),
            cov_finished = as.integer(Finished == "TRUE"), cov_duration_sec = as.integer(Duration),
            cov_age = as.integer(Age), cov_gender = Gender, cov_ethnicity = Ethnicity, cov_children = Children,
            cov_education = Education, cov_qualification = Qualification, cov_income = Income,
            cov_employment = Employment, cov_class = Class, cov_trust = as.integer(Trust_1),
            cov_left_right = as.integer(LeftRight_1), cov_party = Party, cov_vote2020 = President2020,
            cov_invest_skills_college = as.integer(InvestSkillsCollege_7),
            cov_easy_job_college = as.integer(EasyJobCollege_7), cov_winners_ict = as.integer(WinnersICT_1))]
d <- merge(d, cv, by = "id")
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr")]), d[, .N, .(id, task)][, all(N == 2)],
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, all(rating %between% c(0, 10), na.rm = TRUE)])
stopifnot(d[task < 6, uniqueN(paste(attrpos_age, attrpos_gender, attrpos_education)), id][, all(V1 == 1)])
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "diessner_2026_welfare_deservingness.csv"))
