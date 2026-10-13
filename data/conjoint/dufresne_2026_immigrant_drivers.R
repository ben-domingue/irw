##Immigrant versus automated drivers, 2x2 vignette experiment (Canada, Japan, USA), from
##Dufresne, Y., Matsubayashi, T., & Turgeon, M. (2026). Automated driving systems versus immigrant drivers as a
##solution to labor shortage. SSRN working paper. https://doi.org/10.2139/ssrn.7120753
##Replication data: Harvard Dataverse doi:10.7910/DVN/LCL4CO, CC0 1.0. File read: pooled_recoded_data.tab
##(Dataverse "original format" download = pooled_recoded_data.dta); analysis.R read as text for the outcome coding.
##Usage: Rscript dufresne_2026_immigrant_drivers.R <dir holding pooled.dta> <output dir>
##
##3,176 respondents in the file, 3,172 with an outcome (Canada 894, Japan 1,195, USA 1,083), ONE vignette each (task = profile = 1; id = row number,
##the Qualtrics ResponseId is dropped). The vignette describes an immigrant driver (a labor-shortage solution) who
##either speaks or does not speak the receiving country's language (attr_language: "Speaks" / "Does not speak") and has or has not
##received driving training from the receiving country (attr_training: "Training from receiving country" /
##"No training from receiving country"); 2x2, between subjects, ~270-300 per cell per country. The level text is the
##authors' condition label (treat_language, treat_training), not the questionnaire wording, which is not deposited.
##choice = value: 1 = prefers the immigrant driver, 0 = prefers the automated driving system (analysis.R L209-210).
##The automated system is a fixed alternative without randomized attributes, so it is not a profile: opt_out = yes
##(choice 0 = the automated system). 4 rows with NA outcome are omitted.
##Countries pooled (the authors pool them with country fixed effects, analysis.R L240) and the attribute text is
##shared (English condition labels): one table, cov_country. The questionnaire was fielded in the local languages
##(English/French Canada, Japanese, English USA; display language not documented: en;ja).
##Covariates: cov_country; cov_gender (woman: 1 = female, 0 = male, authors' binary coding); cov_age (years);
##cov_income_code (income, codes 1-8, no labels in the deposit). Dropped: derived scales/indicators (bluecollar,
##unidegree, scientist_trust, tech_job_prospects, ai_affect, ai_perceived_knowledge, psych_distance), Qualtrics
##ResponseId, the authors' recoded group variables. No survey weight.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "pooled.dta")))
stopifnot(nrow(s) == 3176, uniqueN(s$response_id) == 3176)
s <- s[!is.na(value)]
d <- s[, .(id = .I, task = 1L, profile = 1L, choice = as.integer(value),
           attr_language = treat_language, attr_training = treat_training,
           cov_country = country, cov_gender = c("male", "female")[woman + 1L], cov_age = as.integer(age),
           cov_income_code = as.integer(income))]
stopifnot(d[, uniqueN(attr_language)] == 2, d[, uniqueN(attr_training)] == 2, all(d$choice %in% 0:1))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dufresne_2026_immigrant_drivers.csv"))
