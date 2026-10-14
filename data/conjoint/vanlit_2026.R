##Vignette experiment on government status x consistency of parliamentarians' democratic defence (Netherlands) from
##van Lit, J., Meijers, M. J., & van Ham, C. (2026). Credible resistance or political ploy? How government status and consistency shape
##citizen perceptions of parliamentarians' democratic defence. Journal of European Public Policy. https://doi.org/10.1080/13501763.2026.2659798
##Replication data: Harvard Dataverse doi:10.7910/DVN/Z3MO0N, CC0 1.0. Files read: crediguv.tab (CSV original, saved locally as d.csv),
##"data preparation.R" (prep.R) and "main analysis.R" (main.R) (text, not run).
##Usage: Rscript vanlit_2026.R <dir holding d.csv> <output dir>
##
##4,847 Dutch online-panel respondents (the paper reports 4,785), one vignette each, 2 x 2 between-subject (1,202-1,218 per cell):
##treatment_group 1-4 = Inconsistent Government / Consistent Government / Inconsistent Opposition / Consistent Opposition (prep.R labels):
##  attr_party_status: Government / Opposition (the defending parliamentarian's party);  attr_consistency: Consistent / Inconsistent.
##The vignette text and the question wording are NOT in the deposit and the article (T&F) could not be retrieved (403): the level text is the
##authors' condition labels (LABELS: tags only; flag for Ben, ruling 10-13).
##Outcome: rating_credibility = dv_main, 1-7 (the plotting code limits the axis to 1-7); it is the paper's main outcome (credibility of the
##democratic defence, per the title and abstract), so "higher = more credible" is assumed; wording and anchors unknown. No opt-out.
##Not kept: the next-actions battery (dv_nxt_*), mediators (mv_info, mv_mand, mv_ploy), manipulation and attention checks, political
##attitudes and trust, knowledge items, occupation dummies and free text, ResponseId / To_weight (re-keyed).
##Covariates: cov_survey_weight (weight; mean 1; missing for 760 respondents, left NA), cov_birth_year (byear), cov_gender_code (sex, 1/2: the
##deposit does not map the codes), cov_education_code (edu_3_rec, 3 levels, unmapped). One task, one profile per respondent, id = row order.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "d.csv"))
stopifnot(nrow(d) == 4847, all(d$treatment_group %in% 1:4))
d <- d[!is.na(dv_main)]
stopifnot(nrow(d) == 4785)
r <- d[, .(id = .I, task = 1L, profile = 1L, rating_credibility = as.integer(dv_main),
  attr_party_status = c("Government", "Government", "Opposition", "Opposition")[treatment_group],
  attr_consistency = c("Inconsistent", "Consistent", "Inconsistent", "Consistent")[treatment_group],
  cov_survey_weight = weight, cov_birth_year = as.integer(byear), cov_gender_code = as.integer(sex), cov_education_code = as.integer(edu_3_rec))]
stopifnot(all(r$rating_credibility %in% 1:7))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "vanlit_2026_democratic_defence_status.csv"))
