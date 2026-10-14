##Wartime-conduct vignette experiments (MTurk survey with 3 factors; college-lab survey with 2 factors) from
##Chu, J. A., Holmes, M., & Traven, D. (2020). Inferring intentions from consequences: How moral judgments shape citizen perceptions
##of wartime conduct. Journal of Experimental Political Science, 8(2). https://doi.org/10.1017/xps.2020.7
##Replication data: Harvard Dataverse doi:10.7910/DVN/YQP2UG, CC0 1.0. Files read: S2_mturk.dta (saved locally as s2.dta), S1_college.dta (s1.dta),
##replication_knobe.do (rep.do; text, not run), ReadMe.pdf. The online appendix (vignette text, question wording) is not in the deposit and could
##not be retrieved, so attribute level text is the LABELS the deposit/do-file carry (LABELS: tags only; flag for Ben, ruling 10-13).
##Usage: Rscript chu_2020.R <dir holding s1.dta and s2.dta> <output dir>
##
##Two tables (two separately fielded surveys with different attribute sets; the authors present the MTurk survey as the main study and the
##college survey as an appendix replication, so they are not pooled):
##  chu_2020_intent_consequences_mturk (Survey 2, MTurk, N = 783): one vignette per respondent, 2 x 2 x 2 between-subject
##    (cells 94-102): attr_consequence (value labels of t_negframe: "Positive Consequence" / "Negative Consequence"),
##    attr_target (t_unesco: 0 = "Civilian" scenario, 1 = "UNESCO" scenario; the do-file's plot labels "Civilian-Low", "UNESCO-High";
##    the do-file's comment "Scenario is Civilian when t_unesco == 0"), attr_severity (t_severity: 0 = "Low", 1 = "High"; same plot labels).
##  chu_2020_intent_consequences_college (Survey 1, university lab, N = 328): 2 x 2: attr_consequence, attr_target.
##Outcomes (raw; wording, scale anchors and direction are NOT in the deposit): rating_intentionality = dv_intend6 (1-6; the do-file labels
##it "Intentionality Evaluation"; the negative-consequence frame raises it: means 4.7 vs 3.0 in Survey 2, so higher = more intentional is
##assumed), rating_immoral = dv_immoral6 (1-6; higher = more immoral by the variable name; dv_moral6 is its exact mirror 7 - x and is dropped),
##rating_responsible = dv_responsible5 (Survey 2 only, 1-5; Survey 1's dv_responsible has unknown coding and is dropped, as are the
##dichotomized dv_immoral2, dv_intend2, dv_moral2). No opt-out. One task, one profile per respondent, id = row order.
##Dropped: demographics with unlabelled codes (race, education6, income, state, vote, pid_lean, republican3, cons3, conservative7, military
##family), manipulation/attention checks (Survey 1 pass_check, fail_check, manip_check), t_negframe_female/t_negframe_unesco
##(interactions), savedeath. Covariates kept: cov_gender (female: 1 = female per the variable name; note the do-file's figure legend
##says "Male, N=328 / Female, N=165" for female == 0/1, which conflicts with the data, where female == 1 has 328 rows in Survey 2: legend taken as
##mislabelled), cov_age (years).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cons <- c("Positive Consequence", "Negative Consequence"); tgt <- c("Civilian", "UNESCO"); sev <- c("Low", "High")
g <- function(x) as.integer(zap_labels(x))
d2 <- as.data.table(read_dta(file.path(raw, "s2.dta")))
stopifnot(nrow(d2) == 783, all(d2$t_negframe %in% 0:1), all(d2$t_severity %in% 0:1), all(d2$t_unesco %in% 0:1))
r2 <- d2[, .(id = .I, task = 1L, profile = 1L, rating_intentionality = g(dv_intend6), rating_immoral = g(dv_immoral6),
  rating_responsible = g(dv_responsible5),
  attr_consequence = cons[g(t_negframe) + 1L], attr_target = tgt[g(t_unesco) + 1L], attr_severity = sev[g(t_severity) + 1L],
  cov_gender = c("male", "female")[g(female) + 1L], cov_age = g(age))]
stopifnot(all(r2$rating_intentionality %in% 1:6), all(r2$rating_immoral %in% 1:6), all(r2$rating_responsible %in% 1:5))
setorder(r2, id, task, profile); fwrite(r2, file.path(out, "chu_2020_intent_consequences_mturk.csv"))
d1 <- as.data.table(read_dta(file.path(raw, "s1.dta")))
stopifnot(nrow(d1) == 328, all(d1$t_negframe %in% 0:1), all(d1$t_unesco %in% 0:1))
r1 <- d1[, .(id = .I, task = 1L, profile = 1L, rating_intentionality = g(dv_intend6), rating_immoral = g(dv_immoral6),
  attr_consequence = cons[g(t_negframe) + 1L], attr_target = tgt[g(t_unesco) + 1L],
  cov_gender = c("male", "female")[g(female) + 1L], cov_age = g(age))]
stopifnot(all(r1$rating_intentionality %in% 1:6), all(r1$rating_immoral %in% 1:6))
setorder(r1, id, task, profile); fwrite(r1, file.path(out, "chu_2020_intent_consequences_college.csv"))
