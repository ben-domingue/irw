##Welfare-state reform conjoint (Japan) from
##Brazzill, M., Magara, H., & Yanai, Y. (2020). When voters favour the social investment welfare
##state. Japanese Journal of Political Science, 21(4), 194-205.
##https://doi.org/10.1017/S1468109920000122
##Replication data: Harvard Dataverse doi:10.7910/DVN/5NC2AV, CC0 1.0, no restricted files.
##File read: jjps_si_japan_brazzill-magara-yanai.csv. Codebook: ..._codebook.pdf; the authors'
##.Rmd (and its knitted .pdf) read as text, not run.
##Usage: Rscript brazzill_2020.R <dir holding the .csv> <output dir>
##
##Online survey of Japanese adults (Qualtrics, sample from Rakuten Insight, 4-8 March 2019).
##1,506 respondent IDs, 3 tasks of 2 policy packages (2 kept, see Outcome); task and profile are RECORDED. 8 attributes
##(codebook; the paper's Table 2, not deposited, has the wording): government spending on
##education, on promoting women's employment, on childcare, on social security; income tax,
##sales tax, corporate tax (each "increase" / "decrease" / "sq" = status quo); government debt
##("noIncrease" / "gradualDecrease" / "immediateDecrease"). Levels are kept exactly as stored
##(the authors' English codes; respondents saw Japanese text that is not in the deposit).
##Outcome: choice = selected, "the profile was selected as preferable" (codebook); question
##wording not deposited. TASK 3 IS DROPPED: its `selected` column duplicates task 2's (identical
##chosen position for all 981 respondents with both; its 121 "neither" rows are exactly the
##respondents with task 2 missing) while its profiles differ, so its real answers are not in the
##deposit (asserted below; the authors' AMCE models include it). Of tasks 1-2, unanswered tasks
##(selected missing) are omitted: 686 tasks; 1,274 respondents answered at least one task, and
##every answered task has exactly one package selected.
##Randomization: restrictions, level weights and attribute order are not documented; level
##shares are close to equal (every attribute within 1.13x) and no combination is missing.
##Covariates (codebook labels applied): cov_age_group (10s .. 80s, as stored), cov_gender
##("female"/"male" as stored; codebook: "Other" was offered but chosen by no one), cov_occupation
##(ISCO major groups, students, unemployed), cov_employment_type, cov_education (the stored short
##codes replaced by the codebook's educ option text: junior-high -> "Junior high school (9th
##Grade)", highschool -> "High school graduate", hs+ -> "High school + vocational school",
##some college -> "Some college", bachelor -> "Bachelor's degree", master+ -> "Master's degree or
##higher"; codebook p.2, matched in the codebook's order as the authors' .Rmd groups them,
##lines 118-120; "elementary" does not occur), cov_social_values
##and cov_economic_values (1-4 codes, 5 = don't know/refused; wording in the codebook),
##cov_income (household income bracket as stored, in 10,000 yen). Dropped: emp_other_detail
##(free text).
##Spot check: no numeric results are deposited (AMCEs only as figures). lm(choice ~ education +
##childcare + income tax), tasks 1-2: increase vs decrease +.14 (education), +.12 (childcare);
##income-tax increase vs decrease -.12. With the copied task 3 these were about a third as large.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "jjps_si_japan_brazzill-magara-yanai.csv"))
stopifnot(uniqueN(s$ID) == 1506, s[, .N, .(ID, task, profile)][, all(N == 1)])
## Task 3's `selected` is a copy of task 2's: same chosen position for every respondent who has both, and
## the 121 task-3 "neither" rows are exactly the respondents whose task 2 is missing, although the task-3
## profiles differ from task 2's. Task 3's real answers are not in the deposit, so task 3 is dropped.
ch <- dcast(s[!is.na(selected)], ID + task ~ profile, value.var = "selected")
w <- dcast(ch[, .(ID, task, pos = fifelse(`1` == 1, 1L, fifelse(`2` == 1, 2L, 0L)))], ID ~ task, value.var = "pos")
stopifnot(w[!is.na(`2`) & !is.na(`3`), all(`2` == `3`)], w[is.na(`2`) & !is.na(`3`), all(`3` == 0L)],
          w[!is.na(`1`) & !is.na(`2`), mean(`1` == `2`) < .6])
s <- s[task != 3 & !is.na(selected)]
stopifnot(s[, .N, .(ID, task)][, all(N == 2)], s[, sum(selected), .(ID, task)][, all(V1 == 1)])
occ <- c("Managers", "Professionals", "Technicians and Associate Professionals", "Clerical Support Workers",
         "Services and Sales Workers", "Skilled Agricultural, Forestry and Fishery Workers",
         "Craft and Related Trades Workers", "Plant and Machine Operators, and Assemblers",
         "Elementary Occupations", "Armed Forces Occupations", "Students", "Unemployed")
emp <- c("Regular Employees", "Part-time and Temporary Workers", "Dispatched Workers from Temporary Labour Agency",
         "Contract and Entrusted Employees", "Self-Employed and Family Workers", "Other")
edu <- c("elementary" = "Elementary school (6th Grade) or less", "junior-high" = "Junior high school (9th Grade)",
         "highschool" = "High school graduate", "hs+" = "High school + vocational school",
         "some college" = "Some college", "bachelor" = "Bachelor\u2019s degree", "master+" = "Master\u2019s degree or higher")
stopifnot(all(s$educ %in% names(edu)))
d <- s[, .(id = as.integer(ID), task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected),
           attr_education_spending = govedu, attr_womens_employment_spending = govfem,
           attr_childcare_spending = govccare, attr_social_security_spending = govssec,
           attr_income_tax = inctax, attr_sales_tax = salestax, attr_corporate_tax = corptax, attr_government_debt = govdebt,
           cov_age_group = age, cov_gender = gender, cov_occupation = occ[occupation], cov_employment_type = emp[emp_type],
           cov_education = edu[educ], cov_social_values = as.integer(socialv), cov_economic_values = as.integer(economicv),
           cov_income = as.character(income))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "brazzill_2020_social_investment.csv"))
