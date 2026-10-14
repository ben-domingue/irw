##Social-spending trade-off conjoint (Germany, Italy, UK) from
##Bremer, B., & Burgisser, R. (2022). Public opinion on welfare state recalibration in times of austerity: Evidence from
##survey experiments. Political Science Research and Methods, 11(1), 34-52. https://doi.org/10.1017/psrm.2021.78
##Replication data: Harvard Dataverse doi:10.7910/DVN/7ERIFH, CC0 1.0. File read: df_cj_psrm_replication.Rdata (object df_cj,
##task-level), readme.rtf, 2_figures_conjoint_main.R (text, not run); design and level text from the article (Cambridge OA
##PDF, Section 3.2 and Table 2). The split-sample experiment (df_split_psrm_replication.Rdata) is a different design (single
##policy statements, respondent level) and is not built.
##Usage: Rscript bremer_2022.R <dir holding df_cj_psrm_replication.Rdata, saved as cj.Rdata> <output dir>
##
##3,716 online-panel respondents (Qualtrics; DE 1,266, IT 1,250, UK 1,200; eligible voters, quota on gender and age),
##5 tasks x 2 profiles, 6 attributes = spending on training for the unemployed (ALMP), childcare services, education,
##unemployment benefits (PLMP), child benefits, old-age pensions, each "Decrease spending" / "No change" /
##"Increase spending" (article Table 2; the data tags are Decrease / No change / Increase).
##Attribute level text taken from the article (Table 2); the deposit stores short tags ("Decrease", "Increase").
##Countries pooled with cov_country (the authors pool them with country checks; the attribute text is shared).
##Restrictions (article): zero-sum packages ("a (more or less) budget-neutral reform"): 588 of the 729 combinations are
##excluded, 141 remain, drawn with equal probability; attribute order randomized per respondent and held across the five
##tasks (not recorded in the deposit, so no attrpos_ columns). Outcomes:
##  choice = selected: pick one of the two fiscal packages (forced choice, exactly one per task, no opt-out)
##  rating = rating, how likely the respondent is to support each package, 0-10 (raw; 0 = least likely, 10 = most likely;
##           the wording/anchors are in the article's Appendix C, which was not available, so labelled as a paraphrase).
##Task and profile are the deposit's own columns. Respondent id re-keyed over (country, Response.ID); the Qualtrics
##Response.ID is dropped (PII-like). Covariates: cov_country, cov_survey_weight (wgt, NA for 116 respondents), plus
##cov_retired and cov_children_u10 (0/1), and code columns cov_education_code (1-3), cov_income_tercile_code (1-3),
##cov_ideology_code (1-3) whose labels are not in the deposit. Dropped: eduben, workctr (derived constituency flags), speed,
##screen, the Qualtrics "conjoint" import-id factor.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "cj.Rdata"), envir = e); d <- as.data.table(e$df_cj)
stopifnot(nrow(d) == 37160)
d[, key := paste(country, Response.ID)]
d[, id := match(key, unique(key))]
pol <- c(Training = "ALMP", Childcare = "Childcare", Education = "Education", Unemployment = "PLMP", `Child benefits` = "Child.benefits", Pensions = "Pensions")
nm <- c(training_for_unemployed = "ALMP", childcare_services = "Childcare", education = "Education", unemployment_benefits = "PLMP",
        child_benefits = "Child.benefits", old_age_pensions = "Pensions")
lv <- c(`No change` = "No change", Decrease = "Decrease spending", Increase = "Increase spending")
r <- d[, .(id, task, profile, choice = as.integer(selected), rating = as.integer(rating))]
for (k in names(nm)) r[[paste0("attr_", k)]] <- unname(lv[as.character(d[[nm[[k]]]])])
r[, `:=`(cov_country = d$country, cov_survey_weight = d$wgt, cov_retired = as.integer(d$retired), cov_children_u10 = as.integer(d$children_u10),
         cov_education_code = as.integer(d$education_c), cov_income_tercile_code = as.integer(d$income_brackets_three),
         cov_ideology_code = as.integer(d$ideology))]
stopifnot(!anyNA(r[, grep("^attr_|^choice|^rating", names(r)), with = FALSE]), r[, sum(choice), by = .(id, task)][, all(V1 == 1)])
setorder(r, id, task, profile)
fwrite(r, file.path(out, "bremer_2022_social_spending.csv"))
