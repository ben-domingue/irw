##Psychological-contract-violation repair vignette experiments (Studies 1 and 2) from
##Cai, Z. (2026). Psychological contract violation recovery [Data set]. figshare.
##https://doi.org/10.6084/m9.figshare.32664582   (no article DOI in the deposit; Study 3, the weekly field study in
##WeekAllWideForMplus.sav, is longitudinal and not a vignette design, so it is not used.)
##Replication data: figshare doi:10.6084/m9.figshare.32664582 (v2), CC BY 4.0. Files read: "promise and amends.sav"
##(Study 1, saved locally as b.sav) and "promise compenation.sav" (Study 2, a.sav).
##Usage: Rscript cai_2026.R <dir holding a.sav and b.sav> <output dir>
##Writes two tables: cai_2026_contract_repair_s1 and cai_2026_contract_repair_s2.
##
##Chinese full-time employees (Study 1: 257, a sample-service panel; Study 2: 374, WeChat/links), each reading ONE
##vignette in which "Manager Wang" broke a promise (Study 1: a management-training place; Study 2: a year-end bonus)
##and then repaired it; 2 x 2 x 2 between-subject, one task of one profile per respondent. The deposit states the
##design in English; the vignettes and items are in Chinese and are not deposited, so level text below is the
##deposit's English value labels, expanded with the Chinese comprehension-check wording (translated):
##  pre_violation_trust (previolationtrust)  1 Low / 2 High pre-violation trust in the manager
##  repair_tactic (tactic): values 1 Apology and explanation, 2 Compensation (Study 1 label: Amends), 3 Promise
##     making. Only 2 and 3 occur in the data (the abstract's "inducement delivery vs promise revision"), so
##     two levels: Study 2: "Compensation: manager won back your year-end bonus" / "Promise making: manager made
##     another promise about the bonus"; Study 1: "Amends: manager won back your training place" /
##     "Promise-making: manager made another promise about the training place" (translated from the check items).
##  repair_velocity (velocity)  1 Slow / 2 Fast (Study 1 labels: Low/High velocity) repair.
##Checked: tactic matches the comprehension-check answer (Study 2: 354 of 374 chose the matching tactic), the
##high-trust arm has the higher pre-trust check mean, and the Fast arm the higher velocity check mean.
##LABELS: English variable labels and translated check wording only (no vignette text).
##Outcomes: after the repair, ratings of psychological contract violation, 4 items toward the manager (Manager Wang)
##and 4 toward the company (K Company), 1-5; the scale anchors are not in the deposit (agreement with the item,
##assumed 1 = disagree; the Chinese items read "I feel betrayed by ...", "I feel ... violated the contract between
##us", "I am very frustrated by how ... treated me", "I am very angry at how ... treated me"), stored raw, no opt-out.
##The pre-repair (breach) ratings and the trust items are baselines/mediators and are dropped, with all derived
##means/differences ("ManagerViolation_Repair", ...), comprehension checks, timestamps, the source channel and (Study 1)
##the IP-address/city column (PII FOUND, dropped).
##Covariates: cov_gender (1 Male, 2 Female, .sav labels), cov_age_group and cov_education (.sav label text),
##cov_work_years and cov_tenure_years (years, free numeric). Respondent id = row order. No survey weight.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
one <- function(nms, pat) { m <- grep(pat, nms, value = TRUE); stopifnot(length(m) == 1); m }
lab <- function(x) as.character(as_factor(x, levels = "labels"))
build <- function(f, rep_pre, rep_suf, tactic_txt, velocity_txt, pretrust_txt, tabname, n) {
  d <- as.data.table(read_sav(file.path(raw, f))); stopifnot(nrow(d) == n)
  nm <- names(d)
  items <- list(mgr_betrayed = "王经理背叛", mgr_contract_violated = "王经理违反", mgr_frustrated = "王经理对待我的方式感到非常沮丧",
                mgr_angry = "王经理对待我方式感到非常愤怒", org_betrayed = "K公司背叛", org_contract_violated = "K公司违反",
                org_frustrated = "K公司对待我的方式感到非常沮丧", org_angry = "K公司对待我方式感到非常愤怒")
  r <- data.table(id = seq_len(n), task = 1L, profile = 1L)
  for (k in names(items)) r[[paste0("rating_", k)]] <- as.integer(d[[one(nm, paste0(rep_pre, ".*", items[[k]], rep_suf))]])
  r[, attr_pre_violation_trust := pretrust_txt[as.integer(d$previolationtrust)]]
  r[, attr_repair_tactic := tactic_txt[as.integer(d$tactic) - 1L]]
  r[, attr_repair_velocity := velocity_txt[as.integer(d$velocity)]]
  gcol <- one(nm, "^您的性别"); acol <- one(nm, "^您的年龄段"); ecol <- one(nm, "^您的受教育程度")
  wcol <- one(nm, if (f == "a.sav") "^工作经验" else "^您有过多少年的工作经验"); tcol <- one(nm, "^您在当前公司工作了多少年")
  r[, `:=`(cov_gender = c("male", "female")[as.integer(d[[gcol]])], cov_age_group = lab(d[[acol]]), cov_education = lab(d[[ecol]]),
           cov_work_years = as.numeric(d[[wcol]]), cov_tenure_years = as.numeric(d[[tcol]]))]
  stopifnot(all(as.integer(d$tactic) %in% 2:3), !anyNA(r[, grep("^(attr|rating)_", names(r)), with = FALSE]))
  setorder(r, id, task, profile)
  fwrite(r, file.path(out, paste0(tabname, ".csv")))
}
pt <- c("Low pre-violation trust in the manager", "High pre-violation trust in the manager")
build("b.sav", "^r", ".*_A$", c("Amends: manager won back your training place", "Promise-making: manager made another promise about the training place"),
      c("Low velocity of repair", "High velocity of repair"), pt, "cai_2026_contract_repair_s1", 257)
build("a.sav", "", ".*_A$", c("Compensation: manager won back your year-end bonus", "Promise making: manager made another promise about the bonus"),
      c("Slow repair", "Fast repair"), pt, "cai_2026_contract_repair_s2", 374)
