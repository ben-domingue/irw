##Job-choice conjoint on sexual harassment from
##Folke, O., & Rickne, J. (2022). Sexual harassment and gender inequality in the labor market.
##The Quarterly Journal of Economics, 137(4), 2163-2212. https://doi.org/10.1093/qje/qjac018
##Replication data: Harvard Dataverse doi:10.7910/DVN/OHGOEV, CC0 1.0. File read:
##survey_experiment.dta (Dataverse "original format" download). Design: paper Section on the
##survey experiment, Online Appendix Table A6 (levels) and Figure A8 (screenshot: Swedish original
##with the authors' English translation); recode logic from "Data Set Up Survey.do" (read as text).
##Usage: Rscript folke_2022.R <dir holding survey_experiment.dta> <output dir>
##
##Swedish Citizen Panel (Medborgarpanelen), January 2020, employed respondents; 3,976 rows in the
##file (paper: N = 3,987). Each respondent made 3 choices between Job A and Job B shown as a table
##with 4 traits: monthly wage (4 levels), tasks (skill development, 3), flexibility of the schedule
##(3), work environment (6: no specific information, content colleagues, conflicts with the
##manager, and three harassment vignettes: sexist hostility, sexual hostility, unwanted sexual
##attention). Respondents whose workplace is mostly women (q38, or q40 when they have no
##colleagues) saw the "female-dominated" set, where the vignettes have a male victim; the others
##saw the "male-dominated or mixed" set with a female victim (trial_job_set). The paper pools both
##sets (pref_b in the .do), so one table. Levels are the English text stored in the .dta, which
##matches the authors' translation in Figure A8; respondents saw Swedish.
##Randomization: paper -- trait values randomized, wage/tasks/flexibility with equal probability;
##each of the 3 harassment vignettes 11%, each other work-environment value 22% (non-uniform).
##The order of the rows was randomized (unit not stated; order not saved, so no attrpos_).
##choice: "Based on the information in the table, which of the two jobs would you prefer?" (authors'
##translation; options Job A / Job B, no opt-out). The question existed in a computer and a
##cell-phone version (q45/q46 etc.); the answered one is used and its version kept as trial_device.
##Tasks never answered are dropped. The authors' analysis excludes pairs where one job dominates;
##all pairs are kept here.
##Covariates: cov_gender from sex (1 = woman, 2 = man per the .do: gen wom=sex==1); other
##covariates keep the source codes (no value labels deposited): cov_age_group_code (age6),
##cov_education_code (edu, 9 codes), cov_income_code (pinc, monthly wage band), cov_ssyk2
##(2-digit occupation code), cov_workplace_sex_q38 / cov_typical_workplace_sex_q40, and q74/q76/q78/
##q80_1-4 (harassment perceptions and trait importance; wording in .dta variable labels).
##The authors' probability weight (gen_edu2_alder5_w) is built in the .do from population totals
##and is not kept.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(zap_labels(read_dta(file.path(raw, "survey_experiment.dta"))))
x[, id := seq_len(.N)]
q <- list(m = list(c("q45", "q46"), c("q50", "q51"), c("q55", "q56")), k = list(c("q60", "q61"), c("q65", "q66"), c("q70", "q71")))
rows <- list()
for (s in c("m", "k")) for (t in 1:3) {
  qc <- x[[q[[s]][[t]][1]]]; qp <- x[[q[[s]][[t]][2]]]
  stopifnot(!any(!is.na(qc) & !is.na(qp)))
  ans <- ifelse(is.na(qc), qp, qc); dev <- ifelse(!is.na(qc), "computer", ifelse(!is.na(qp), "cell phone", NA))
  for (j in c("a", "b")) {
    g <- function(v) x[[sprintf("%s_%s_%d_%s", v, s, t, j)]]
    rows[[length(rows) + 1]] <- data.table(id = x$id, task = t, profile = match(j, c("a", "b")),
      choice = as.integer(ans == match(j, c("a", "b"))),
      attr_wage = g("lon"), attr_tasks = g("arbetsupg"), attr_flexibility = g("inflytande"), attr_work_environment = g("arbetsmilj"),
      trial_job_set = c(m = "male-dominated or mixed", k = "female-dominated")[[s]], trial_device = dev)
  }
}
d <- rbindlist(rows)[!is.na(choice)]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
          d[, uniqueN(trial_job_set), id][, all(V1 == 1)],
          !anyNA(d[, .(attr_wage, attr_tasks, attr_flexibility, attr_work_environment)]),
          d[, all(attr_wage != "" & attr_work_environment != "")])
cv <- x[, .(id, cov_gender = c("female", "male")[sex], cov_age_group_code = age6, cov_education_code = edu, cov_income_code = pinc,
            cov_ssyk2 = ssyk2, cov_workplace_sex_q38 = q38, cov_typical_workplace_sex_q40 = q40,
            cov_harassment_in_industry_q74 = q74, cov_aware_harassment_cases_q76 = q76, cov_own_risk_q78 = q78,
            cov_importance_no_harassment = q80_1, cov_importance_flextime = q80_2, cov_importance_skills = q80_3, cov_importance_wage = q80_4)]
stopifnot(all(x$sex %in% 1:2))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "folke_2022_harassment_job_choice.csv"))
cat(nrow(d), uniqueN(d$id), d[, uniqueN(paste(id, task))], "\n"); print(d[, .N, attr_work_environment][order(-N)])
