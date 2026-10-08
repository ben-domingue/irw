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
##1,506 respondent IDs, 3 tasks of 2 policy packages; task and profile are RECORDED. 8 attributes
##(codebook; the paper's Table 2, not deposited, has the wording): government spending on
##education, on promoting women's employment, on childcare, on social security; income tax,
##sales tax, corporate tax (each "increase" / "decrease" / "sq" = status quo); government debt
##("noIncrease" / "gradualDecrease" / "immediateDecrease"). Levels are kept exactly as stored
##(the authors' English codes; respondents saw Japanese text that is not in the deposit).
##Outcome: choice = selected, "the profile was selected as preferable" (codebook); question
##wording not deposited. Unanswered tasks (selected missing) are omitted: 1,090 tasks; 1,320
##respondents answered at least one task. In 121
##answered tasks neither package is selected; whether the question offered "neither" is not
##documented (the authors keep these tasks in their AMCE models).
##Randomization: not documented; level shares are close to equal.
##Covariates (codebook labels applied): cov_age_group (10s .. 80s), cov_gender, cov_occupation
##(ISCO major groups, students, unemployed), cov_employment_type, cov_education, cov_social_values
##and cov_economic_values (1-4 codes, 5 = don't know/refused; wording in the codebook),
##cov_income (household income bracket as stored, in 10,000 yen). Dropped: emp_other_detail
##(free text).
##Spot check: no numeric results are deposited (AMCEs only as figures); lm(choice ~ attributes)
##gives +.03 for increased education and childcare spending vs status quo, -.06 for an income-tax
##increase.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "jjps_si_japan_brazzill-magara-yanai.csv"))
stopifnot(uniqueN(s$ID) == 1506, s[, .N, .(ID, task, profile)][, all(N == 1)])
s <- s[!is.na(selected)]
stopifnot(s[, .N, .(ID, task)][, all(N == 2)], s[, sum(selected), .(ID, task)][, all(V1 <= 1)])
occ <- c("Managers", "Professionals", "Technicians and Associate Professionals", "Clerical Support Workers",
         "Services and Sales Workers", "Skilled Agricultural, Forestry and Fishery Workers",
         "Craft and Related Trades Workers", "Plant and Machine Operators, and Assemblers",
         "Elementary Occupations", "Armed Forces Occupations", "Students", "Unemployed")
emp <- c("Regular Employees", "Part-time and Temporary Workers", "Dispatched Workers from Temporary Labour Agency",
         "Contract and Entrusted Employees", "Self-Employed and Family Workers", "Other")
d <- s[, .(id = as.integer(ID), task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected),
           attr_education_spending = govedu, attr_womens_employment_spending = govfem,
           attr_childcare_spending = govccare, attr_social_security_spending = govssec,
           attr_income_tax = inctax, attr_sales_tax = salestax, attr_corporate_tax = corptax, attr_government_debt = govdebt,
           cov_age_group = age, cov_gender = gender, cov_occupation = occ[occupation], cov_employment_type = emp[emp_type],
           cov_education = educ, cov_social_values = as.integer(socialv), cov_economic_values = as.integer(economicv),
           cov_income = as.character(income))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "brazzill_2020_social_investment.csv"))
