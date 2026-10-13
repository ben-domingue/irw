##Childcare-arrangement discrete choice experiment (Switzerland) from
##Zangger, C., & Widmer, J. (2020). Choosing what is best for one's children? Experimental evidence on
##parents' responsiveness to childcare subsidies and their preferences for different childcare
##arrangements. Early Childhood Research Quarterly, 51, 110-123.
##https://doi.org/10.1016/j.ecresq.2019.10.004
##Data: Mendeley Data doi:10.17632/93d83kfmwg.1 ("Data for: Choosing what is best for one's children?"),
##CC BY 4.0 (licence read from the Mendeley public API). File read: NuN_ECRQ.dta (Stata, value labels
##present; a "reduced dataset to reproduce all the results", missing values not imputed, 540 rows).
##No codebook / questionnaire ships; the variable labels and value labels of the .dta are the source.
##Usage: Rscript zangger_2020.R <dir holding NuN_ECRQ.dta> <output dir>
##Sample: 540 parents in the city of Bern with a child in one of 26 nurseries (idnursery); the paper's abstract
##(not otherwise read) gives 540 parents, matching the 540 rows. Questionnaire in German (470), English (9) or French
##(7) of the 486 kept, on paper or online (qf). Each respondent saw ONE choice
##task: two described childcare alternatives, profile 1 = a nursery and profile 2 = a child minder (the
##alternatives are fixed by type, so profile numbering does not depend on the outcome), plus a third
##option "Private" (a private arrangement, no displayed attributes: the outside option, opt_out = yes).
##Choice: ce_outcome "Which option would you recommend your friend?": Nursery (1), Child minder (2),
##Private (3). Choice = 1 on the chosen profile; Private -> choice 0 on both profiles. 54 respondents
##have no ce_outcome and are dropped (486 respondents remain).
##Attributes of each alternative (levels = the value labels of ce_*1 for the nursery, ce_*2 for the child
##minder): price after subsidies per day-unit as labelled ("55.- Swiss Francs", nursery 55/85/125,
##child minder 35/60/85), distance (about 5/15/25 min), curriculum (playful learning / free play),
##children per caregiver (3/4/5), flexibility for care on other days (rather possible / rather not possible),
##and attr_provider (Nursery / Child minder, the alternative's label). The price attribute has different
##levels for the two types, so a level of attr_price is type specific. The unit of the price (per day?)
##is not stated in the deposit labels.
##Scenario factors (randomised, common to all alternatives of the task, so stored as task-level trial_
##columns, not attributes): trial_reason (reason for taking up employment: not to lose touch to the
##professional field / to support the household financially), trial_earnings (160 or 250 Swiss Francs per
##day), trial_grandparents (grandparents can help out / cannot help out), trial_hours (40% / 60% hours worked).
##Randomization restrictions, level probabilities, attribute order and the full question wording are NOT
##documented in the deposit (the label of ce_outcome is the only wording). The paper (not read) describes
##the design.
##Covariates: cov_gender (value labels man/woman -> male/female), cov_birth_year (yborn),
##cov_education (heduc value label text), cov_household_income (income_hh value label, monthly CHF band),
##cov_language (q_lang: German/English/French), cov_mode (qf: Paper and Pencil / Online).
##Dropped: household composition, relation to child, occupation (ISCO), employment items, nursery id,
##country of birth, free-text "other education/relation", the source ids. id = row order of the file.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "NuN_ECRQ.dta")))
stopifnot(nrow(s) == 540, uniqueN(s$id) == 540)
lab <- function(x) { l <- attr(x, "labels"); y <- names(l)[match(as.integer(x), l)]; y }
s <- s[!is.na(ce_outcome)]; stopifnot(nrow(s) == 486, all(s$ce_outcome %in% 1:3))
s[, rid := .I]
mk <- function(p) {
  sf <- as.character(p)
  r <- data.table(id = s$rid, task = 1L, profile = p, choice = as.integer(s$ce_outcome == p),
    attr_provider = c("Nursery", "Child minder")[p],
    attr_price = lab(s[[paste0("ce_price", sf)]]), attr_distance = lab(s[[paste0("ce_time", sf)]]),
    attr_curriculum = lab(s[[paste0("ce_pedconc", sf)]]), attr_children_per_caregiver = lab(s[[paste0("ce_nchild", sf)]]),
    attr_flexibility = lab(s[[paste0("ce_flex", sf)]]))
  r
}
d <- rbind(mk(1), mk(2))
stopifnot(!anyNA(d))
cv <- data.table(id = s$rid, trial_reason = lab(s$ce_reason), trial_earnings = lab(s$ce_income),
  trial_grandparents = lab(s$ce_supportgranp), trial_hours = lab(s$ce_percent),
  cov_gender = c(man = "male", woman = "female")[lab(s$gender)], cov_birth_year = as.integer(s$yborn),
  cov_education = lab(s$heduc), cov_household_income = lab(s$income_hh),
  cov_language = lab(s$q_lang), cov_mode = lab(s$qf))
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice")); setorder(d, id, task, profile)
stopifnot(d[, sum(choice), id][, all(V1 <= 1)], d[, sum(choice), id][, sum(V1 == 0)] == s[ce_outcome == 3, .N])
fwrite(d, file.path(out, "zangger_2020_childcare.csv"))
