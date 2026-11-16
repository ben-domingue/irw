##Intersectional representative bureaucracy conjoint (public employees, 4 countries) from
##Thomann, E., Rudolph, L., & Gómez Díaz, J. (2026). Intersectional representative bureaucracy in Europe. Journal of European
##Public Policy. https://doi.org/10.1080/13501763.2026.2756962 (named in the archive's helpfile as forthcoming).
##Replication data: Zenodo doi:10.5281/zenodo.23054130, CC BY 4.0 (record licence). Files read: replication.dta (value labels),
##helpfile.txt, replication.do (text only, not run), Master_Questionnaire-All_Questions-CH-ESP-IRE-DK.pdf (pdftotext).
##Usage: Rscript thomann_2026.R <dir holding replication.dta> <output dir>
##
##2,403 public-service employees (question A6: employee/civil servant) in Ireland (600), Denmark (655), Spain (648) and
##Switzerland (500) (opt-in online panels, 2024; the paper reports 2,402: one respondent more here, not resolved). Each
##respondent saw 10 pairs (task 1-10) of hypothetical EU citizens asking local government about welfare eligibility
##("Individual 1" = profile 1, "Individual 2" = profile 2), 7 attributes: age (25/55), gender (Female/Male), previous profession
##(Salesperson/Medical Doctor), nationality (Bulgarian/French), duration of stay (1 year/4 years), proficiency in the local
##language (Limited/Fluent), job applications submitted last month (5/0). Level text is the Stata value label of
##q_attr<k>_concept<c>_task<t> (the same 1/2 codes carry the same labels for both concepts: stopifnot), which matches the questionnaire
##table (the questionnaire shows "4 Years"/"1 Year" etc.). The scenario text: "Please consider a scenario in which you work for the
##local government. You receive two information requests from two EU citizens ... you only have the time to provide one of the
##individuals with personalized assistance."
##choice: C1 "For which individual will you write a detailed personalized answer?" Individual 1 / Individual 2 (forced, no
##opt-out). The certainty item C2 and C3 are not in the file. Experimental arms of the questionnaire (control, accountability,
##perspective-getting) are NOT recorded in replication.dta, so no trial_ column.
##Countries pooled with cov_country: the authors' main models pool all four (clustered by respondent) and the attribute text is
##shared (English labels). country labels from replication.do ("label define country 1 Ireland 2 Denmark 3 Spain 4 Switzerland";
##confirmed by D3, country of birth). Attribute order: randomized per respondent and kept for the 10 pairs (questionnaire note),
##not recorded; attribute levels fully randomized (questionnaire). Display languages are not stated.
##Covariates: cov_country, cov_age (years), cov_gender (1 Male, 2 Female), cov_sector (A7 public-service sector text),
##cov_birth_country (D3 text). Dropped: A6 (constant), the respondent id (none in the file; id = row number).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- read_dta(file.path(raw, "replication.dta")); stopifnot(nrow(d) == 2403)
an <- c("age", "gender", "profession", "nationality", "duration_of_stay", "language_proficiency", "job_applications")
txt <- function(x) as.character(as_factor(x))
L <- list()
for (t in 1:10) for (p in 1:2) {
  r <- data.table(id = seq_len(nrow(d)), task = t, profile = p, choice = as.integer(as.integer(d[[paste0("C1_task", t)]]) == p))
  for (k in 1:7) {
    x <- d[[sprintf("q_attr%d_concept%d_task%d", k, p, t)]]; x1 <- d[[sprintf("q_attr%d_concept1_task%d", k, t)]]
    stopifnot(identical(attr(x, "labels"), attr(x1, "labels")), all(as.integer(x) %in% 1:2))
    r[[paste0("attr_", an[k])]] <- txt(x)
  }
  L[[length(L) + 1]] <- r
}
o <- rbindlist(L)
stopifnot(all(as.integer(unlist(d[, paste0("C1_task", 1:10)])) %in% 1:2), !anyNA(o))
cv <- data.table(id = seq_len(nrow(d)), cov_country = c("1" = "Ireland", "2" = "Denmark", "3" = "Spain", "4" = "Switzerland")[as.character(as.integer(d$country))], cov_age = as.integer(d$age),
                 cov_gender = c("1" = "male", "2" = "female")[as.character(as.integer(d$gender))],
                 cov_sector = txt(d$A7), cov_birth_country = txt(d$D3))
cv[cov_sector %in% c("Skipped", "Not Asked"), cov_sector := NA]; cv[cov_birth_country %in% c("Skipped", "Not Asked"), cov_birth_country := NA]
o <- merge(o, cv, by = "id"); setorder(o, id, task, profile)
fwrite(o, file.path(out, "thomann_2026_intersectional_bureaucrats.csv"))
