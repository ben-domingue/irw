##Independent-candidate conjoint (Chile, Netquest panel wave 1, Oct-Nov 2021) from
##Argote, P., & Visconti, G. (2023). Anti-elite attitudes and support for independent candidates.
##PLOS ONE, 18(10), e0292098. https://doi.org/10.1371/journal.pone.0292098
##Replication data: Harvard Dataverse doi:10.7910/DVN/XGHULL, CC0 1.0, no restricted files.
##File read: wave1.dta (Dataverse "original format" download of wave1.tab). Read as text only:
##01_results.do, 02_results_weights.do. Design facts and level text from the open-access article
##(Data and design section, Table 1) and its S1 File (Appendices B, D, H).
##Not the same experiment as argote_2025_ideology_candidates_chile (wave 2 of the same panel,
##deposit KJPMMS: other attributes, other respondents' tasks).
##Usage: Rscript argote_2023.R <dir holding wave1.dta> <output dir>
##
##3,965 Chilean adults (Netquest online panel, October 29 - November 20 2021; quotas on age, gender,
##socio-economic status and region). 5 tasks (`set`) of two hypothetical presidential candidates
##(`posicion` 1/2), both RECORDED; 39,650 rows. 4 attributes:
##  attr_coalition: the authors' own .dta value labels, stored as they are: "Center-Right",
##    "Center-Left", "Left", "Right", "Independents". These are the authors' one-to-one labels for the
##    displayed coalitions, not the displayed text. The article says respondents saw Chile's four
##    coalitions (Chile Podemos Más, Nuevo Pacto Social, Apruebo Dignidad, Frente Social Cristiano) or
##    "Independent (No party or coalition)" (Table 1), but no deposited file says which label is which
##    coalition, so the coalition names are not stored. Weighted 50% independent / 12.5% per
##    coalition (article; data shares 0.50 / 0.12).
##  attr_occupation: Lawyer / School teacher / Street Vendor (value labels; article "lawyer,
##    teacher, or street vendor"); attr_age: 35/45/55/65; attr_gender: Man / Woman (article Table 1;
##    value labels Male / Female).
##Respondents saw Spanish; the Spanish screen text is not deposited, so levels are English.
##Outcome: choice = the authors' choice_clean (1 = this candidate chosen). The raw answer column
##(choice_) is empty in the deposit. Respondents could refuse to vote for either candidate (S1
##Appendix H: "outcome = 0 for both profiles"): 6,908 of 19,825 tasks have no candidate chosen;
##646 respondents chose neither in all 5 tasks (the authors' choice_clean2 sets those NA; their
##choice_ninguno = share of "ninguno" tasks matches). Question wording is not deposited.
##trial_design_version = `version` (1-20, constant within respondent; undocumented);
##trial_priming = `celda`, a priming experiment shown before the conjoint (Control, Representation,
##Malfeasance, Inequality; value labels; S1 Appendix B).
##Covariates: cov_gender from the authors' `female` (1 = female; value label "Female"; it disagrees
##with the panel's `sex` for 14 respondents); cov_age (years); cov_anti_elite = the authors' populism2
##(1 = chose "The main division in society is between the people and the elite" over "... between the
##left and the right", article p. 4); cov_will_of_people = populism1 (1 = "legislators should follow
##the will of the people when making laws" over "... their own knowledge and opinions");
##cov_duration_sec (`duration`, whole wave-1 survey, = 60 x duration_min); cov_survey_weight =
##weight_joint (census cell weight, article p. 7) and cov_weight_rake = weight_rake2 (raking weight;
##NA for 1,097 rows); the main estimates are unweighted. Codes without labels (agerecode, nse,
##education, region, device) are not kept.
##Dropped: key, numericalid, codpanelista (panel IDs; id re-keyed in source order), timestamps,
##access count, status, badwordsvariables; the authors' many derived dummies/interactions, ipw,
##merge artefacts (country, m_chile, counts).
##N: the deposit has 3,965 respondents; the article's main model uses choice_clean on all of them.
##Spot check: OLS of choice on independent vs coalition + the other attributes gives independent vs
##coalition +12.4 points (article: 12.3, 95% CI 11.4-13.4; close, not exact).
suppressMessages({library(haven); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "wave1.dta"))
stopifnot(identical(names(attr(k$atr1, "labels")), c("Center-Right", "Center-Left", "Left", "Independents", "Right")),
          identical(names(attr(k$atr2, "labels")), c("Lawyer", "School teacher", "Street Vendor")),
          identical(names(attr(k$atr3, "labels")), c("35", "45", "55", "65")),
          identical(names(attr(k$atr4, "labels")), c("Male", "Female")),
          identical(names(attr(k$celda, "labels")), c("Control", "Representation", "Malfeasance", "Inequality")),
          all(is.na(k$choice_)))
z <- function(x) as.integer(zap_labels(x))
coal <- c("Center-Right", "Center-Left", "Left", "Independents", "Right")  # the .dta value labels, as they are
d <- data.table(rkey = k$key, task = z(k$set), profile = z(k$posicion), choice = z(k$choice_clean),
                attr_coalition = coal[z(k$atr1)],
                attr_occupation = c("Lawyer", "School teacher", "Street Vendor")[z(k$atr2)],
                attr_age = c("35", "45", "55", "65")[z(k$atr3)],
                attr_gender = c("Man", "Woman")[z(k$atr4)],
                trial_design_version = z(k$version),
                trial_priming = c("Control", "Representation", "Malfeasance", "Inequality")[z(k$celda)],
                cov_gender = c("male", "female")[z(k$female) + 1L], cov_age = z(k$age),
                cov_anti_elite = z(k$populism2), cov_will_of_people = z(k$populism1),
                cov_duration_sec = as.integer(k$duration),
                cov_survey_weight = as.numeric(k$weight_joint), cov_weight_rake = as.numeric(k$weight_rake2))
stopifnot(!anyNA(d[, .(task, profile, choice, attr_coalition, attr_occupation, attr_age, attr_gender, cov_gender)]),
          !anyDuplicated(d[, .(rkey, task, profile)]), d[, .N, rkey][, all(N == 10)],
          d[, sum(choice), .(rkey, task)][, all(V1 <= 1)])
d[, id := match(rkey, unique(rkey))][, rkey := NULL]
setcolorder(d, c("id", "task", "profile"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "argote_2023_independent_candidates.csv"))
