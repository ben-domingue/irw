##EU defence cooperation cost experiments (25 EU countries): two 2 x 3 factorial vignettes, from
##Mader, M., Neubert, M., Munchow, F., Hofmann, S. C., Schoen, H., & Gavras, K. (2024). Crumbling in the face of cost? How cost
##considerations affect public support for European security and defence cooperation. European Union Politics, 25(3), 483-503.
##https://doi.org/10.1177/14651165241236777 (journal metadata from Crossref)
##Replication data: Harvard Dataverse doi:10.7910/DVN/CLI4OL, CC0 1.0. Files read: EUP_Costs_ReplicationData.RData (datafile 8944506;
##data.frame `dat`, 40,500 rows x 28 columns, loaded into a new environment), README.txt, 08_appendix.R (as text; labels of the
##treatment levels come from its fct_recode calls and figure labels).
##Usage: Rscript mader_2024.R <dir with the RData; optional 3rd arg = file name, default EUP_Costs_ReplicationData.RData> <output dir>
##
##Design: online survey in 25 EU member states (1,500-2,000 respondents each, 40,500 in total; quota samples; the deposit's QCOUNTRY / iso).
##EVERY respondent answered BOTH experiments (question order randomized: Q31_32_order 1/2, kept as trial_question_order; which code
##means which experiment came first is not documented). Each experiment is a 2 x 3 factorial vignette about an EU policy to which
##cost information was added; the authors' levels (the displayed sentence is not in the deposit; same convention as
##levis_2026_carbon_messenger):
##  Experiment 1 (EU military intervention in a crisis): factor 1 = soldiers at risk (SoldiersRisk, "Casualties" in the figures) or
##    nothing added (Control); factor 2 = who pays: the national budget (CountryCost, "National Budget"), a pooled EU budget
##    (SharedCost, "Pooled Budget") or nothing (Control).
##  Experiment 2 (joint defence procurement of aircraft): factor 1 = job cuts (JobCuts, "Job Cuts") or nothing (Control); factor 2 = the
##    same budget factor.
##  A "Control" level means the clause was left out of the description: coded "(not shown)". Cells are balanced (6,616-6,869 each).
##Outcomes (1 per respondent and experiment; the question wording is not in the deposit; paraphrase): costExperiment1_CrisisManagement =
##  support for EU crisis management / military intervention; costExperiment2_Aircraft = support for the joint procurement. Stored as 0, 0.25,
##  0.5, 0.75, 1, a 5-point scale rescaled to 0-1 (the code treats > 0.5 as "Support", < 0.5 as "Oppose", 0.5 as "Neither", and the figure
##  code comments name "Strongly Oppose ... Strongly Support"): higher = more support. Rows with a missing outcome (4,048 and 4,078
##  respondents) are omitted, as the README rule requires (the code does not say why they are missing, likely don't know).
##Table grouping: two tables because the attribute sets and the policy differ; the same row number of the data is the same respondent in
##both (id = row number of `dat`, since the file has no respondent id); the countries are pooled in one table each (the authors pool
##them with country fixed effects; the attribute text is shared): cov_country.
##1 task x 1 profile per respondent. Restrictions: the 2 x 3 cells are fully crossed (all six cells present). level_weights: cell sizes
##near equal (not asserted). No survey weights in the file.
##Covariates: cov_country (iso code), cov_gender (female 0/1: 1 -> female, 0 -> male; the source variable is named female), cov_age
##(years, as recorded), cov_education (authors' three categories: low, medium, high), trial_question_order (1/2).
##Dropped: attitudes, attachment, militarism, threat, quiz, vote, left-right and other covariate scales.
##Count check: 40,500 rows = 40,500 in the file; the paper's N (40,500 from 25 countries) was not fetched.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- if (length(a) >= 3) a[3] else "EUP_Costs_ReplicationData.RData"
e <- new.env(); load(file.path(raw, f), e); d <- as.data.table(e$dat)
stopifnot(nrow(d) == 40500)
d[, id := .I]
cv <- d[, .(id, cov_country = iso, cov_gender = c("male", "female")[female + 1L], cov_age = as.integer(unclass(age)),
            cov_education = as.character(education), trial_question_order = as.character(Q31_32_order))]
bud <- function(x) c(Control = "(not shown)", CountryCost = "National Budget", SharedCost = "Pooled Budget")[as.character(x)]
mk <- function(t1, t2, y, a1, lab1, nm1, nm2, nm) {
  x <- data.table(id = d$id, task = 1L, profile = 1L, rating = d[[y]],
                  a1 = c(Control = "(not shown)", setNames(lab1, a1))[as.character(d[[t1]])], a2 = unname(bud(d[[t2]])))
  setnames(x, c("a1", "a2"), c(nm1, nm2))
  x <- merge(x, cv, by = "id")[!is.na(rating)]
  stopifnot(!anyNA(x[[nm1]]), !anyNA(x[[nm2]]), uniqueN(x[, .(get(nm1), get(nm2))]) == 6)
  setcolorder(x, c("id", "task", "profile", "rating")); setorder(x, id)
  fwrite(x, file.path(out, paste0(nm, ".csv")))
}
mk("costExperiment1_Treat1", "costExperiment1_Treat2", "costExperiment1_CrisisManagement", "SoldiersRisk", "Casualties",
   "attr_casualties", "attr_budget", "mader_2024_eu_military_costs")
mk("costExperiment2_Treat1", "costExperiment2_Treat2", "costExperiment2_Aircraft", "JobCuts", "Job Cuts",
   "attr_job_cuts", "attr_budget", "mader_2024_eu_procurement_costs")
