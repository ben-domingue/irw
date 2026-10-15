##Crowdshipping versus traditional parcel delivery, trust rating, Netherlands, from
##Cebeci, M. S., Tapia, R. J., Kroesen, M., de Bok, M., & Tavasszy, L. (2023). The effect of trust on the choice for
##crowdshipping services. Transportation Research Part A, 170, 103622. https://doi.org/10.1016/j.tra.2023.103622
##Data: 4TU.ResearchData doi:10.4121/b1cd5e55-c3c2-4d5b-8ec7-58f071f53b6e.v2, CC BY-NC-SA 4.0 (4TU record licence).
##Files read: "Choice_dataset_for upload.csv" (';'-separated) and readme.md. Level text and wording from the paper (Table 1,
##Table 2) and the MSc thesis it comes from (repository.tudelft.nl uuid:ed098831-c73e-4e11-b143-ed87f20afc2c: Tables 3.1,
##3.2, Figure 3.2, the survey screen); the deposit stores 0/1 and numeric codes.
##Usage: Rscript cebeci_2023.R <dir holding "Choice_dataset_for upload.csv"> <output dir>
##
##Online survey, Netherlands, April-May 2021 (students and their networks, plus the Delft station); 248 responses, 215
##complete = the 215 respondents here, 1720 choice observations = 8 tasks each, as the paper. Two unlabelled alternatives per
##task: Crowdshipping delivery (levels vary by design; profile 1, left column of Fig 3.2) and Traditional delivery (fixed
##levels, profile 2). The traditional alternative shows displayed levels, so it is a profile (attr_service holds the label).
##Outcomes: choice = "From the available delivery options below, select the one that fits your preference most" /
##"Would you consider making use of this crowdshipping service?" Yes = crowdshipping (file code 1), "No (I would use
##traditional delivery)" = traditional (file code 2): verified by sign: crowdshipping chosen more at low cost, 4 stars, 1000 euro
##insurance, 3% damage. Forced choice between the two, no opt-out. rating_trust: "Based on the above mentioned scenario, how
##much would you trust crowdshipping?" 1 Strongly distrustful, 2 Distrustful, 3 Neutral, 4 Trustful, 5 Strongly trustful
##(5-point scale as in Fig 3.2; direction higher = more trust). It rates the crowdshipping service, so it is stored on profile 1
##and is NA on profile 2.
##Fixed blocked design: orthogonal fractional factorial, 16 profiles in 2 blocks, one block per respondent (trial_block).
##Task = row order within respondent (the file has no task index: INFERRED, task_source = inferred; every respondent has
##exactly 8 rows). Attributes (crowdshipping | traditional): delivery time ("Next day delivery"|"Same day delivery" | Next day),
##cost ("5|7|10|12€" | 10€; euro sign after the number as on the card), tracking ("Only main steps can be seen in the app/website" | "Real-time driver tracking by the
##app/website" ; traditional main steps), reputation ("Two stars" | "Four stars"; traditional "Three stars" read off the star icons
##in Fig 3.2 of the thesis), insurance ("Up to 500€|1000€"; traditional 750€), possibility of damage ("1 in 20 damaged
##delivery (5%)" | "1 in 30 damaged delivery (3%)"; traditional "1 in 25 (4%)"). Coding of the deposit: Sdd 1 = same day, Trck 1 =
##real-time, Rpt 1 = four stars, Ins 1 = 1000, Dmg 1 = 3% (Tables 1 and 3.1; the signs of a quick logit agree).
##Restrictions: none documented. Level weights: orthogonal design, levels equally frequent by construction but no statement.
##Covariates: GENDER, Age, OCCUP, EDU, INCM are binary regroupings (age 18-25 vs older, student vs working/other, master/PhD
##vs other, income below vs above 500 EUR) whose 0/1 direction is not given in the readme: kept as codes (_code).
##Dropped: nothing else. Respondent key re-keyed 1..215 (the deposit ID is already a plain number).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "Choice_dataset_for upload.csv"), sep = ";")
stopifnot(nrow(x) == 1720, uniqueN(x$ID) == 215, x[, .N, ID][, all(N == 8)], x$choice %in% 1:2, x$trust %in% 1:5, !anyNA(x))
x[, id := match(ID, sort(unique(ID)))]
x[, task := seq_len(.N), by = ID]
cs <- x[, .(id, task, trial_block = Block,
  attr_delivery_time = ifelse(Sdd == 1, "Same day delivery", "Next day delivery"),
  attr_delivery_cost = paste0(Cst, "\u20ac"),
  attr_tracking = ifelse(Trck == 1, "Real-time driver tracking by the app/website", "Only main steps can be seen in the app/website"),
  attr_reputation = ifelse(Rpt == 1, "Four stars", "Two stars"),
  attr_insurance = ifelse(Ins == 1, "Up to 1000\u20ac", "Up to 500\u20ac"),
  attr_damage = ifelse(Dmg == 1, "1 in 30 damaged delivery (3%)", "1 in 20 damaged delivery (5%)"),
  chosen = choice, rating_trust = trust,
  cov_gender_code = GENDER, cov_age_code = Age, cov_occupation_code = OCCUP, cov_education_code = EDU, cov_income_code = INCM)]
p1 <- cs[, .(id, task, profile = 1L, choice = as.integer(chosen == 1), attr_service = "Crowdshipping delivery",
  attr_delivery_time, attr_delivery_cost, attr_tracking, attr_reputation, attr_insurance, attr_damage, rating_trust,
  cov_gender_code, cov_age_code, cov_occupation_code, cov_education_code, cov_income_code, trial_block)]
p2 <- cs[, .(id, task, profile = 2L, choice = as.integer(chosen == 2), attr_service = "Traditional delivery",
  attr_delivery_time = "Next day delivery", attr_delivery_cost = "10\u20ac",
  attr_tracking = "Only main steps can be seen in the app/website", attr_reputation = "Three stars",
  attr_insurance = "Up to 750\u20ac", attr_damage = "1 in 25 damaged delivery (4%)", rating_trust = NA_integer_,
  cov_gender_code, cov_age_code, cov_occupation_code, cov_education_code, cov_income_code, trial_block)]
d <- rbind(p1, p2); setorder(d, id, task, profile)
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .(attr_delivery_time, attr_reputation)]))
fwrite(d, file.path(out, "cebeci_2023_crowdshipping_trust.csv"))
