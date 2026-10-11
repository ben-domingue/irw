##Family-ideals factorial vignettes from
##Aassve, A., et al. (2024). Family ideals in an era of low fertility. Proceedings of the National
##Academy of Sciences. https://doi.org/10.1073/pnas.2311847121
##Replication data: Harvard Dataverse doi:10.7910/DVN/LR2B6Y, CC0 1.0, no restricted files.
##File read: "PNAS_AassveEtAl2024.tab" (Stata original, saved as long.dta): 120,846 rows =
##20,141 respondents x 6 vignettes, 8 countries (China, Italy, Japan, Korea, Norway, Singapore,
##Spain, USA). The analysis do-file PNAS_AassveEtAl2024.do (text) gives the experiment variables.
##Not read: PNAS_AassveEtAl2024_wide.tab (same data, wide).
##Usage: Rscript aassve_2024.R <raw dir> <output dir>
##
##Each respondent rated 6 vignettes describing a family (task = `run` 1-6, one profile each) and
##belongs to ONE of two experiments (variable `experiment`), which differ in the attribute set,
##so two tables: aassve_2024_family_ideals_a (experiment 1: 7,985 respondents, 8 attributes: union,
##fertility, income, respect, famcom, extfamcom, genderrole, WLB; outcome A_successfam) and
##aassve_2024_family_ideals_b (experiment 2: 12,156 respondents, the same 8 plus childedu and
##finsupport; outcome B_successfam). The authors pool the eight countries in one mixed model with a
##country intercept (and by country), so each table pools countries with cov_country.
##Level text = the Stata value labels of the long file, which are the authors' short labels, not the
##sentences respondents read (the questionnaire is not in the deposit; the vignettes were shown in
##local languages, not documented): e.g. "Talk freq w. grandp's", "Respected in comunity" (sic).
##Outcome: rating = the family's perceived success, 0-10 (higher = more successful); the wording and
##anchors are not in the deposit (variable name A_/B_successfam only). 47,857 of 47,910 vignettes in
##A and 72,843 of 72,936 in B have a rating; the rest are omitted. No choice, no opt-out.
##Vignettes come from a fixed set: `vigid` (1-1440) and `blockid` are kept as trial_vignette_id /
##trial_block (a blocked fixed design); no source states level probabilities or restrictions.
##Covariates: cov_country (country, English name, from the file), cov_gender (female 0/1),
##cov_age, cov_education_code (edu_self, codes not labelled in the deposit), cov_survey_weight
##(weight; the do-file weights every model with it). Dropped: ResponseId (Qualtrics id, re-keyed),
##pid, derived dummies (highschool, married, nchild*, ...), income, religion.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_dta(file.path(raw, "long.dta")))
stopifnot(nrow(d) == 120846, d[, uniqueN(experiment), ResponseId][, all(V1 == 1)])
lab <- function(x) as.character(as_factor(x))
allat <- c("union", "fertility", "income", "respect", "famcom", "extfamcom", "genderrole", "WLB", "childedu", "finsupport")
build <- function(e, ats, y, name) {
  s <- d[experiment == e]
  ids <- match(s$ResponseId, unique(s$ResponseId))
  o <- data.table(id = ids, task = as.integer(s$run), profile = 1L, rating = as.integer(s[[y]]))
  for (a in ats) { v <- lab(s[[a]]); stopifnot(!anyNA(v)); o[[paste0("attr_", a)]] <- v }
  o[, `:=`(trial_vignette_id = as.integer(s$vigid), trial_block = as.integer(s$blockid),
    cov_country = tools::toTitleCase(s$country), cov_gender = c("male", "female")[s$female + 1L],
    cov_age = as.integer(s$age), cov_education_code = as.integer(s$edu_self), cov_survey_weight = s$weight)]
  stopifnot(o[!is.na(rating), all(rating %in% 0:10)], !anyDuplicated(o[, .(id, task)]))
  o[, cov_country := ifelse(cov_country == "Usa", "USA", cov_country)]
  o <- o[!is.na(rating)]
  setorder(o, id, task, profile); fwrite(o, file.path(out, paste0(name, ".csv")))
  cat(name, uniqueN(o$id), nrow(o), "\n")
}
build(1, allat[1:8], "A_successfam", "aassve_2024_family_ideals_a")
build(2, allat, "B_successfam", "aassve_2024_family_ideals_b")
