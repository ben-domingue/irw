##Unscheduled paediatric healthcare discrete choice experiment (parents, Ireland) from
##Nicholson, E., McDonnell, T., Conlon, C., De Brún, A., Doherty, E., & McAuliffe, E. (2023).
##Parent's preferences for unscheduled paediatric healthcare: A discrete choice experiment.
##Health Expectations, 26(5), 1931-1940. https://doi.org/10.1111/hex.13802
##Data: Nicholson, E., McDonnell, T., & McAuliffe, E. (2022). CUPID: Parental preferences for
##unscheduled paediatric healthcare: A Discrete Choice Experiment [Data set]. Zenodo.
##https://doi.org/10.5281/zenodo.6572717, CC BY 4.0 (record licence; no other terms in the files).
##File read: "Stata Data Formatted for DCE.dta" (the authors' long file, one row per respondent x
##choice set x alternative, attribute dummies). Also read as text: Parent_Decision_Making_DCE_Survey.docx
##(Qualtrics print), "Final Parent DCE design.ngd", the survey xlsx header; the article (Europe PMC
##PMC10485340): Methods, Table 1 (attributes and levels), Table 3.
##Usage: Rscript nicholson_2023.R <dir holding the .dta> <output dir>
##
##458 parents of children under 16 in Ireland (Qualtrics research panels, February 2021). 24 choice
##sets in 2 blocks of 12 (Bayesian D-efficient Ngene design); each respondent answered one block
##(source `block`): task = the choice set number within the deck (source task "_01a" -> 1; block 1 =
##tasks 1-12, block 2 = tasks 13-24, so task numbers are the design's choice-set numbers, shown in
##that order per the Qualtrics flow), profile 1 = Service A, 2 = Service B (source suffix a/b,
##acsa). 5 attributes; level text from the authors' dummy names mapped to wording:
##  wait: "Same day", "Next day", "In two days’ time" (survey grid wording)
##  appointment: the article's Table 1 wording ("Appointment between 9:00 AM and 5:00 PM",
##    "Appointment for any time including evening/weekend", "No given appointment but may have to wait
##    for an unknown amount of time to be seen"). The deposited survey .docx is the PILOT version
##    (6 grids per block that do not match the fielded design; walk-in shown as "Walk in with no
##    appointment (unknown wait)"); the article says the appointment wording was changed after the
##    pilot, and the fielded grid text is not deposited, so the article's wording is used.
##  advice: "Telephone advice from healthcare professional about what to do", "No advice" (grid)
##  who: "Your own GP", "Any doctor or nurse", "The practice nurse" (grid)
##  cost: "€0", "€15", "€30", "€45"
##The deposited Ngene .ngd is also an earlier design (2-level appointment attribute); the dta's 24
##sets are constant across respondents (checked) and are used.
##Outcome choice: "choose the service that you would prefer to attend" (paraphrase of the survey
##intro; options Service A / Service B). Forced choice, no opt-out (article Methods); exactly one
##chosen per task (checked). The 12 unanswered sets of the other block are omitted.
##The article analyses 450: it dropped 8 respondents with impossible data (youngest child aged > 18
##or > 1,000 visits in a year). All 458 are kept here; those 8 have cov_youngest_child_age > 18 or
##cov_visits_last_year > 1000 (values kept as recorded).
##Covariates: answer text as stored in the dta (question text from the survey): cov_gender
##(Female/Male -> female/male), cov_age (years, typed; all 20-63), cov_education, cov_employment,
##cov_family_status, cov_ethnicity (selected choice only; the "other, specify" text is dropped),
##cov_n_children, cov_youngest_child_age, cov_healthcare_professional, cov_gms_card (medical card /
##GP visit card / Neither), cov_private_insurance, cov_child_health, cov_child_condition ("Prefer
##not to say" -> NA), cov_visits_last_year, cov_considered_wait/_appointment/_advice/_who/_cost
##(Considered / Not Considered), cov_duration_sec (whole survey). Dropped: Qualtrics ResponseID,
##panel ids psid/pid (PII-like platform ids), dates, empty IP/name/email/lat-long columns, free-text
##fields (ethnicity other, condition other, other characteristics, information source), the health
##literacy items and the authors' derived dummies, class probabilities and interactions.
##No survey weight. Spot check: a conditional logit (choice on the attributes, linear cost, constant for
##Service A) on the 450 analysed respondents reproduces the article's Table 3 exactly (next day 0.609,
##same day 0.935, 9-5 0.264, evening/weekend 0.305, advice 0.237, any doctor/nurse 0.152, own GP
##0.503 vs 0.502, cost -0.015, ASC 0.157; log likelihood -3537).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(zap_labels(read_dta(file.path(raw, "Stata Data Formatted for DCE.dta"))))
x[, tn := as.integer(substr(task, 2, 3))][, ab := substr(task, 4, 4)]
stopifnot(all((x$ab == "a") == (x$acsa == 1)), x[, .N, newid][, all(N == 48)], uniqueN(x$newid) == 458)
x <- x[!is.na(choice)]
stopifnot(x[, .N, newid][, all(N == 24)], x[, all(tn %in% if (block[1] == 1) 1:12 else 13:24), newid]$V1)
one <- function(...) { m <- cbind(...); stopifnot(all(rowSums(m) == 1)); max.col(m) }
d <- x[, .(id = as.integer(newid), task = tn, profile = fifelse(ab == "a", 1L, 2L), choice = as.integer(choice),
           attr_wait = c("Same day", "Next day", "In two days\u2019 time")[one(timely_sameday, timely_nextday, timely_2days)],
           attr_appointment = c("Appointment between 9:00 AM and 5:00 PM", "Appointment for any time including evening/weekend",
                                "No given appointment but may have to wait for an unknown amount of time to be seen")[one(appoint_9to5, appoint_eveweekend, appoint_walkin)],
           attr_advice = c("Telephone advice from healthcare professional about what to do", "No advice")[one(guidance_teleadvice, guidance_noadvice)],
           attr_who = c("Your own GP", "Any doctor or nurse", "The practice nurse")[one(continuity_ownGP, continuity_anyGPnurse, continuity_practicenurse)],
           attr_cost = paste0("€", cost),
           cov_gender = c(Female = "female", Male = "male")[Whatisyourgender], cov_age = as.integer(Whatageareyou),
           cov_education = Whatisyourhighestlevelofed, cov_employment = Whatisyouremploymentstatus,
           cov_family_status = Whatisyourfamilystatus, cov_ethnicity = Whatisyourethnicorcultural,
           cov_n_children = as.integer(Howmanychildrendoyouhave), cov_youngest_child_age = as.numeric(Whatageisyouryoungestchild),
           cov_healthcare_professional = Areyouahealthcareprofessiona, cov_gms_card = Doyouhold,
           cov_private_insurance = Doyouholdprivatehealthinsur, cov_child_health = Howwouldyoudescribeyouryoun,
           cov_child_condition = fifelse(Doesyouryoungestchildcurrent == "Prefer not to say", NA_character_, Doesyouryoungestchildcurrent),
           cov_visits_last_year = as.integer(Approximatelyhowmanytimeshav),
           cov_considered_wait = Pleaseindicatebelowwhichoft, cov_considered_appointment = BP, cov_considered_advice = BQ,
           cov_considered_who = BR, cov_considered_cost = BS, cov_duration_sec = as.integer(Durationinseconds))]
stopifnot(all(x$cost %in% c(0, 15, 30, 45)), !anyNA(d$cov_gender), all(d$cov_age %in% 18:99))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(task, profile, attr_wait, attr_appointment, attr_advice, attr_who, attr_cost)][, uniqueN(paste(task, profile)) == .N])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "nicholson_2023_paediatric_care.csv"))
