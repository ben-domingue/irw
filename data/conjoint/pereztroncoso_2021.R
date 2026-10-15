##Discrete choice experiment on personalised nutrition services, from
##Perez-Troncoso, D., Epstein, D. M., & Castaneda-Garcia, J. A. (2021). Consumers' preferences and
##willingness to pay for personalised nutrition. Applied Health Economics and Health Policy, 19(5),
##757-767. https://doi.org/10.1007/s40258-021-00647-3
##Deposit: Mendeley Data doi:10.17632/kh2btj3btj (version 1), CC BY 4.0. Files read:
##Consumers_pref_and_WTP_AEHP.dta (long file, Stata variable labels) and "statistical analysis.do"
##(the authors' code, read as text).
##Usage: Rscript pereztroncoso_2021.R <dir holding the .dta> <output dir>
##
##Sample: 429 respondents in Spain with recorded choices (the file lists 462; the paper reports 429 valid); 8 choice sets x 2 alternatives
##(A, B), 4 attributes, forced choice (no opt-out; exactly one alternative chosen per set).
##Outcome: choice = the alternative chosen in the set (binary dependent variable `choice`).
##Attributes (Stata variable labels): Personalisation (4 levels), Delivery format (0 traditional/
##physical, 1 digital), Exercise schedule (0 no, 1 included in the plan), Price in EUR (10, 20, 30, 40).
##LABELS: the four personalisation levels are labelled only "Level1".."Level4" in the deposit (pers 0..3)
##and the paper is paywalled, so they are stored as "Level 1".."Level 4"; the other text is taken
##from the variable labels (delivery and exercise wording is the label's, not the on-screen text).
##Respondent validity: 33 of the 462 respondents in the file (verif = 0, failed the verification
##question) have no choice recorded (choice is missing on all their 16 rows); the authors' .do file
##drops them. Rows with no outcome are omitted, leaving 429 respondents as in the paper.
##Fixed blocked design: choice-set ids 1-8 and 9-16 are two blocks (trial_block); each respondent
##saw one block of 8 sets. Task = order of the question id (qid) within respondent (inferred from
##row order; the deposit has the global question id, not a position); profile = `alt` (1 = A, 2 = B).
##Covariates: age (years), gender (`sex`: 1 = woman, 0 = man, variable label), height, weight, weekly
##sport hours, interest in healthy nutrition (0-10), noncommunicable disease (1 = yes), education
##in years, income range (codes, no labels), personal income, duration in seconds, and
##`prob` (percent probability of buying the selected options; one value per respondent, a
##post-task question whose wording is not in the deposit). Household-size columns (hm_*) have
##corrupted labels and are dropped. No survey weight. No identifying columns in the file.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "Consumers_pref_and_WTP_AEHP.dta")))
k[, id := as.integer(factor(pid))]
setorder(k, id, qid, alt)
k[, task := as.integer(factor(qid)), by = id]
k <- k[!is.na(choice)]
k[, id := as.integer(factor(pid))]
k[, task := as.integer(factor(qid)), by = id]
d <- k[, .(id, task, profile = as.integer(alt), choice = as.integer(choice))]
d[, attr_personalisation := paste("Level", k$pers + 1)]
d[, attr_delivery_format := c("traditional/physical", "digital")[k$form + 1]]
d[, attr_exercise_schedule := c("no", "included in the plan")[k$rut + 1]]
d[, attr_price := paste("EUR", k$price)]
d[, trial_block := ifelse(k$cs <= 8, 1L, 2L)]
d[, cov_gender := c("male", "female")[k$sex + 1]]
d[, cov_age := as.integer(k$age)]
d[, cov_height_cm := as.integer(k$height)]
d[, cov_weight_kg := as.integer(k$weight)]
d[, cov_sport_hours_week := as.integer(k$sport)]
d[, cov_interest_healthy_nutrition := as.integer(k$inter)]
d[, cov_noncommunicable_disease := as.integer(k$dis)]
d[, cov_education_years := as.integer(k$educ)]
d[, cov_income_range_code := as.integer(k$income_r)]
d[, cov_personal_income := as.integer(k$pincome)]
d[, cov_duration_sec := as.integer(k$Durationinseconds)]
d[, cov_buy_prob_pct := as.integer(k$prob)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)], !anyNA(d$attr_price),
          d[, uniqueN(trial_block), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pereztroncoso_2021_pers_nutrition.csv"))
