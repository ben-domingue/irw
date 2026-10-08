##Resume conjoints (China) from
##Pan, J., & Zhang, T. (2023). Does ideology influence hiring in China? Evidence from two
##randomized experiments. Political Science Research and Methods, 11(1), 63-79.
##https://doi.org/10.1017/psrm.2021.77
##Replication data: Harvard Dataverse doi:10.7910/DVN/CLZZTW, CC0 1.0, no restricted files.
##Files read: HRSurvey.csv, Pretest1_SelectTreatment.csv. Codebook: ReadMe.txt (variable
##definitions); Main_rep.R / Appendix_rep.R and their logs read as text, not run.
##Usage: Rscript pan_2023.R <raw dir> <output dir>
##
##TWO TABLES (different attribute sets and samples). Not built from this deposit: the resume
##AUDIT (a field experiment sent to employers, ResumeAudit.csv) and pretest 2
##(Pretest2_ManipulationCheck.csv: one manipulated factor, the study group, so not a conjoint).
##The deposit has no questionnaire: outcome wording and level text below are the ReadMe's
##English variable definitions (respondents read Chinese resumes), so they are paraphrases,
##not the displayed text.
##
##pan_2023_hiring_managers (HRSurvey.csv): 506 hiring managers in China, each shown 3
##hypothetical resumes; reported callback per resume (Y: 1 = would call back, 0 = no), stored
##as rating 0/1 (each resume judged on its own; 0-3 callbacks per respondent). Attributes
##(ReadMe definitions): extracurricular study group = the ideology treatment (comic group,
##apolitical / Socialism with Chinese Characteristics study group, political conformity /
##Western political philosophy study group, non-conformity), each respondent saw each of the
##three once (all 6 orders occur about equally), so this attribute is BLOCKED within
##respondent, not independently randomized; GPA rank (top 5% of cohort / not top 5%),
##gender, CCP membership, explicit political statement bullet in the extracurricular
##section (included / not; in the audit resumes this is "sovereignty takes precedence over
##human rights" or its reverse, not documented for the survey), STEM major (yes / no),
##university (985 elite / not 985 elite). Task = row order within respondent (one resume per
##task, profile = 1): INFERRED, not verifiable; the varied allegiance order suggests the file
##keeps the display order. Respondent ids are already 1..506 (Qualtrics-style name
##ResponseId, but not platform IDs). Covariates: cov_gender (female; ReadMe (10) "=1 if
##identified as woman, =0 otherwise": 1 = female, 0 = male), age, non-Han, urban hukou, CCP
##member, has direct reports, sector; the authors' dummy sets for work experience, HR
##experience, hukou region, education and income are collapsed back into one text column each
##(every respondent falls in exactly one group; income is missing for 36 respondents).
##cov_education uses the ReadMe (24)-(26) wording: "High school or below", "Bachelor",
##"Graduate degree" (the authors' three groups; the raw answer options are not deposited).
##No survey weight, attention check or duration in the deposit (ReadMe).
##Spot check: lm(rating ~ study group) reproduces the log's non-conformity effect, -6.7% of
##the conformity callback rate (.852) (Log_main.txt: -6.728538).
##
##pan_2023_resume_pretest (Pretest1_SelectTreatment.csv): 121 respondents (sample not
##described in the deposit), each rating 10 hypothetical job applicants (profiles A-K, no I)
##on three 1-10 scales: rating_merit = academic merit, rating_connections = strength of
##government connections, rating_conformity = political conformity to the CCP regime (higher
##= more). Three binary attributes, levels as the ReadMe defines them: master's major
##(Scientific Socialism and Communist Movements / International Politics), highlighted courses
##(socialism courses / Western political philosophy courses, course titles in the level text),
##extracurricular (Socialism with Chinese Characteristics study group + "sovereignty takes
##precedence over human rights" / Western political philosophy study group + "human rights
##takes precedence over sovereignty"). Task = profile letter order (A = 1 .. K = 10),
##profile = 1; whether the letter is the display order is not documented. All 8 combinations
##occur with about equal frequency. No bare `rating` column: the three ratings are equal
##questions about the same profiles.
##Spot check: lm(rating_conformity ~ extracurricular) reproduces the log's Table A2 estimate
##(.490, Log_appendix.txt).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
## --- hiring-manager survey
h <- fread(file.path(raw, "HRSurvey.csv"))
stopifnot(h[, .N, ResponseId][, all(N == 3)], uniqueN(h$ResponseId) == 506,
          h[, uniqueN(resume_allegiance), ResponseId][, all(V1 == 3)])
h[, task := seq_len(.N), ResponseId]
stopifnot(all(h$female %in% 0:1))
pick <- function(...) { x <- list(...); lab <- names(x); m <- do.call(cbind, x)
  stopifnot(all(rowSums(m, na.rm = TRUE) <= 1)); r <- lab[max.col(m, ties.method = "first")]
  r[rowSums(m) == 0 | is.na(rowSums(m))] <- NA_character_; r }
al <- c(comic = "Comic study group (apolitical)", Socialism = "Socialism with Chinese Characteristics study group",
        West = "Western political philosophy study group")
d <- h[, .(id = as.integer(ResponseId), task, profile = 1L, rating = as.integer(Y),
           attr_study_group = unname(al[resume_allegiance]),
           attr_gpa_rank = fifelse(resume_highmerit == 1, "Top 5% of cohort", "Not top 5% of cohort"),
           attr_gender = fifelse(resume_male == 1, "Male", "Female"),
           attr_ccp_member = fifelse(resume_ccp == 1, "CCP member", "Not a CCP member"),
           attr_political_statement = fifelse(resume_statement == 1, "Explicit political statement", "No political statement"),
           attr_major = fifelse(resume_STEMMajor == 1, "STEM major", "Non-STEM major"),
           attr_university = fifelse(resume_hightierU == 1, "985 elite university", "Not a 985 elite university"),
           cov_gender = c("male", "female")[female + 1L], cov_age = as.integer(age), cov_non_han = as.integer(nonHan),
           cov_urban_hukou = as.integer(urban), cov_ccp_member = as.integer(ccp), cov_manager = as.integer(manager),
           cov_sector = sector,
           cov_work_experience = pick(`1-3 years` = exp_1_3, `4-7 years` = exp_4_7, `8+ years` = exp_8more),
           cov_hr_experience = pick(`1-3 years` = hrexp_1_3, `4-7 years` = hrexp_4_7, `8+ years` = hrexp_8more),
           cov_hukou_region = pick(East = HukouEast, Middle = HukouMiddle, West = HukouWest),
           cov_education = pick(`High school or below` = hs, Bachelor = bachelor, `Graduate degree` = graduate),
           cov_income = pick(`<=5000 RMB` = inc_low, `5001-8000 RMB` = inc_mid, `8001-20000 RMB` = inc_upmid, `>20000 RMB` = inc_high))]
stopifnot(!anyNA(d$attr_study_group), d[, uniqueN(cov_age), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pan_2023_hiring_managers.csv"))
## --- pretest 1
p <- fread(file.path(raw, "Pretest1_SelectTreatment.csv"))
stopifnot(p[, .N, respondent][, all(N == 10)], p[, uniqueN(profile), respondent][, all(V1 == 10)], uniqueN(p$respondent) == 121)
p[, task := match(profile, c("A", "B", "C", "D", "E", "F", "G", "H", "J", "K"))]
stopifnot(!anyNA(p$task))
e <- p[, .(id = as.integer(respondent), task, profile = 1L, rating_merit = as.integer(merit),
           rating_connections = as.integer(connections), rating_conformity = as.integer(allegiance),
           attr_major = fifelse(marxist_major == 1, "Scientific Socialism and Communist Movements", "International Politics"),
           attr_courses = fifelse(marxist_course == 1,
             "Socialism with Chinese Characteristics; Transnational Socialism; Mao Zedong Thoughts and Socialism with Chinese Characteristics",
             "Study on Western Political Philosophy; History of Western Political Philosophy; Political Regimes in Western Capitalist States"),
           attr_extracurricular = fifelse(marxist_extra == 1,
             "Socialism with Chinese Characteristics Study Group; sovereignty takes precedence over human rights",
             "Western political philosophy study group; human rights takes precedence over sovereignty"))]
setorder(e, id, task, profile)
fwrite(e, file.path(out, "pan_2023_resume_pretest.csv"))
