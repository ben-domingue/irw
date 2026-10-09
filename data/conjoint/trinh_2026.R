##Factorial survey on wealth transfers between siblings (Germany) from
##Trinh, N. A., Tisch, D., & Schechtl, M. (2026). The (in)appropriateness of inequality: A factorial
##survey experiment on wealth transfers within families. Social Forces.
##https://doi.org/10.1093/sf/soag010
##Replication data: OSF osf.io/pj7s3 (doi:10.17605/OSF.IO/PJ7S3), CC BY-NC 4.0 (node licence). File
##read: "replication files/data/TrinhTischSchechtl_2026.dta" (inside replication files.zip). Read as
##text: readme.pdf, 01_sample.do, 03_analyses_main.do. The article (OUP page) gives design and wording.
##Usage: Rscript trinh_2026.R <dir holding TrinhTischSchechtl_2026.dta> <output dir>
##
##Kantar online survey, 9-29 Dec 2022, adults 40+ in Germany: a representative sample (1,400) and an
##affluent oversample (>= EUR 110,000 financial wealth or self-employed; 1,592), 2,992 respondents x
##4 vignettes = 11,968 ratings (article; file has the same counts). One table with cov_subsample: the
##authors pool both samples in the main models and the vignettes are identical.
##Design (article): full factorial 2x2x3x3x3x3x2 = 648 vignettes, D-efficient blocking (SAS %MktEx)
##into 81 decks of 4 per transfer type, 162 decks; transfer type (gift / inheritance) varies only
##between respondents (fixed blocked design; trial_deck = deck). Each respondent rated one deck.
##task = vig_order (the position in which the vignette was shown; each respondent has a permutation
##of 1-4; vignr is the position within the deck); profile = 1.
##Displayed text (German, in the file's `vignette`), e.g. "Christian hat eine fünf Jahre ältere
##Schwester / Christians Schwester arbeitet im Familienbetrieb, Christian hat eine festen Job woanders.
##/ Die Eltern der Geschwister haben in den letzten Jahren den größten Teil ihres Vermögens wie folgt
##an die beiden Kinder verschenkt [vererbt]: / ... den Familienbetrieb erhalten. / ... das Haus, in dem
##die Eltern wohnten, erhalten. / ... eine große Geldsumme erhalten." Levels are stored as the
##authors' English value labels (e.g. "Focal cash", "Both cash", "Sibling cash"), not the German
##sentences: attr_focal_gender (Focal male/Focal female; shown through the focal child's first name
##and the sibling noun: a son always has a sister, a daughter a brother -- checked), attr_name (the
##first name shown, nested in gender, 4 per gender), attr_birth_order (Focal firstborn / Focal
##younger), attr_job, attr_cash, attr_house, attr_business, attr_transfer (Gift / Inheritance).
##Outcome: rating = vig_eval, "Ist der Anteil den [Name] bekommen hat, Ihrer Meinung nach..." (article:
##"is the share that [name] received too little, appropriate, or too much?"), 11 points -5 (too little)
##.. 0 (appropriate) .. +5 (too much), stored as answered. No opt-out.
##Covariates: cov_age (years), cov_gender (gender: Männlich -> male, Weiblich -> female, Divers ->
##other; .dta value labels), cov_education (highest_education value-label text; "Keine Angabe" -> NA),
##cov_subsample (representative / affluent), cov_relationship, cov_children, cov_income, cov_wealth,
##cov_work, cov_work_selfemployed, cov_employees (value-label text), cov_migrant, cov_homeowner,
##cov_received_gift, cov_made_gift (0/1 as labelled No/Yes), cov_interview_time (qtime, "Total Interview
##Time", unit not documented). Dropped: the authors' recodes (female, educ, emp, rich, selfemployed,
##soloselfemployed, income_num, wealth_num, focal_female), hid_Group_allocation*, id_vig, block,
##question, vignette (text, summarized above). No survey weight (article).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "TrinhTischSchechtl_2026.dta")))
stopifnot(nrow(k) == 11968, uniqueN(k$id_resp) == 2992, k[, .N, id_resp][, all(N == 4)],
          k[, all(sort(vig_order) == 1:4), id_resp][, all(V1)], k[, uniqueN(inheritance), id_resp][, all(V1 == 1)])
stopifnot(all(grepl("Schwester", k$vignette) == (k$focal_male == 1)), all(grepl("vererbt", k$vignette) == (k$inheritance == 1)))
lab <- function(x) { y <- as.character(as_factor(x, levels = "labels")); y }
d <- k[, .(id = as.integer(id_resp), task = as.integer(vig_order), profile = 1L, rating = as.integer(vig_eval),
           attr_focal_gender = lab(focal_male), attr_name = name_focal, attr_birth_order = lab(focal_firstborn),
           attr_job = lab(job), attr_cash = lab(cash), attr_house = lab(home), attr_business = lab(business),
           attr_transfer = lab(inheritance), trial_deck = as.integer(deck),
           cov_age = as.integer(age), cov_gender = c(`1` = "male", `2` = "female", `3` = "other")[as.character(as.integer(gender))],
           cov_education = lab(highest_education), cov_subsample = lab(subsample),
           cov_relationship = lab(relstatus), cov_children = lab(children), cov_income = lab(income), cov_wealth = lab(wealth),
           cov_work = lab(work), cov_work_selfemployed = lab(work_selfemployed), cov_employees = lab(employees),
           cov_migrant = as.integer(migrant), cov_homeowner = as.integer(homeowner), cov_received_gift = as.integer(received_gift),
           cov_made_gift = as.integer(made_gift), cov_interview_time = as.numeric(qtime))]
d[cov_education == "Keine Angabe", cov_education := NA]
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
stopifnot(all(d$rating %in% -5:5), !anyNA(d$cov_gender))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "trinh_2026_family_wealth_transfers.csv"))
