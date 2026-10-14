##2x2 vignette on decision favorability x caseworker warmth (Denmark, nursing-home application) from
##Hansen, F. G. (2023). Can warm behavior mitigate the negative effect of unfavorable governmental decisions on
##citizens' trust? Journal of Experimental Political Science, 10(1), 62-75. https://doi.org/10.1017/XPS.2021.23
##(data published 2021). Replication data: Harvard Dataverse doi:10.7910/DVN/KAMSQK, CC0 1.0. File read: data.dta
##("original format", Stata; value labels are Danish and partly mis-numbered: see gender). Codebook_JEPS.pdf and
##replication_main_appendix.R read as text (not run); the article's open-access reader page for the vignette design.
##(Script name hansen_2023_warmth.R: hansen_2023.R belongs to a different paper, P. Hansen 2023.)
##Usage: Rscript hansen_2023_warmth.R <dir holding data.dta> <output dir>
##
##1,613 Danish adults (YouGov web panel, representative on age, gender, education, residence; 25 Feb - 6 Mar 2021).
##ONE written vignette each (task = profile = 1; id = re-keyed integer from caseid, the panel sample id). The respondent
##imagines helping a close relative apply for a place in a Danish nursing home and dealing with a municipal caseworker.
##Two randomized factors (of_treatment and warmth_treatment; treatment_groups 1-4 is consistent with them, 396-406 per arm):
##  attr_decision (of_treatment): the municipality REJECTED (0, unfavorable) or APPROVED (1, favorable) the application.
##  attr_caseworker_warmth (warmth_treatment): 0 low warmth / 1 high warmth. The warmth wording is described in the
##     article ("friendly, kind, likable, good-natured, and warm"; low warmth uses negative items and low-performance cues,
##     e.g. "the caseworker does not seem very likable and good-natured"). The vignette text itself is in Appendix A, which is not
##     in the deposit and was not accessible: level text is PARAPHRASED from the article and the codebook.
##Outcomes (stored raw as in the deposit):
##  rating_trust_caseworker = trust_b, "How much do you personally trust the caseworker to make the right decisions?"
##     0-10 scale recoded by the author to 0-1 (steps of .1; 0 = no trust at all, 1 = completely trust; higher = more trust);
##     97 NA.
##  rating_trust_municipality = trust_m, same wording for "the municipality"; 0-1 as above.
##  rating_inclined_to_complain = q5 "Hvor tilbøjelig er du til at klage over afgørelsen?" (How inclined are you to complain about
##     the decision?) 1 Meget tilbøjelig (very inclined) ... 7 Meget utilbøjelig (very disinclined); 88 = Ved ikke (don't know,
##     kept as 88). HIGHER 1-7 = LESS inclined. Translated wording.
##Dropped: the author's perception items and indices (fair, neutral, unbiased, warm, friendly, likable, competent,
##intelligent, capable; perc_*), the manipulation check attention, derived dummies (age_1, edu), caseid.
##Covariates, mapped from the codebook (Table 1) because the .dta value labels disagree with the data for gender
##(labels Kvinde=1/Mand=2 but the values are 0/1; codebook: 0 = male, 1 = female):
##  cov_gender (0 male, 1 female), cov_age_group (18-34 / 35-54 / 55-69 / 70+), cov_education (1 upper secondary or lower /
##  2 short or medium-cycle higher / 3 long-cycle higher, codebook English wording), cov_ideology_lr (self-placement: 1 right ...
##  5 left per codebook; text from the .dta Danish labels: Højreorienteret, Moderat højreorienteret, Centrum, Moderat
##  venstreorienteret, Venstreorienteret; "don't know"/refused are NA here), cov_elderly_care_user (0 no, 1 yes: has a close
##  relative in a nursing home; 8 NA).
##N: 1,613 respondents = the article (n = 1,613).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "data.dta")))
stopifnot(nrow(k) == 1613, uniqueN(k$caseid) == 1613)
o <- as.integer(k$of_treatment); w <- as.integer(k$warmth_treatment)
stopifnot(identical(as.integer(k$treatment_groups), ifelse(w == 1 & o == 0, 1L, ifelse(w == 1 & o == 1, 2L, ifelse(w == 0 & o == 1, 3L, 4L)))))
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L)
d[, rating_trust_caseworker := round(as.numeric(k$trust_b), 1)]
d[, rating_trust_municipality := round(as.numeric(k$trust_m), 1)]
d[, rating_inclined_to_complain := as.integer(zap_labels(k$q5))]
d[, attr_decision := c("application rejected (unfavorable decision)", "application approved (favorable decision)")[o + 1L]]
d[, attr_caseworker_warmth := c("low warmth (caseworker unfriendly, not very likable and good-natured)", "high warmth (caseworker friendly, kind, likable, good-natured and warm)")[w + 1L]]
g <- as.integer(zap_labels(k$gender)); stopifnot(all(g %in% 0:1))
d[, cov_gender := c("male", "female")[g + 1L]]
d[, cov_age_group := c("18-34", "35-54", "55-69", "70+")[as.integer(zap_labels(k$age))]]
d[, cov_education := c("Upper secondary education or lower", "Short/medium-cycle higher education", "Long-cycle higher education")[as.integer(zap_labels(k$education_rc))]]
ide <- as.integer(zap_labels(k$ideology))
d[, cov_ideology_lr := c("Hojreorienteret", "Moderat hojreorienteret", "Centrum", "Moderat venstreorienteret", "Venstreorienteret")[ide]]
u <- as.integer(zap_labels(k$user))
d[, cov_elderly_care_user := ifelse(u %in% 0:1, u, NA_integer_)]
rc <- grep("^rating_", names(d), value = TRUE)
d <- d[rowSums(!is.na(d[, ..rc])) > 0]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hansen_2023_warmth.csv"))
cat("rows", nrow(d), "\n")
print(d[, .(trust_b = round(mean(rating_trust_caseworker, na.rm = TRUE), 2), trust_m = round(mean(rating_trust_municipality, na.rm = TRUE), 2)), by = .(attr_decision, attr_caseworker_warmth)])
