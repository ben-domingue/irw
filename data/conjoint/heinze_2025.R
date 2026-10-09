##Village-president (sarpanch) vignette experiment, North Maharashtra, from
##Heinze, A. R. (2025). Democratic deepening or elite persistence? How local elites adapt to
##electoral reform in rural India. American Political Science Review.
##https://doi.org/10.1017/S0003055425101068
##Replication data: Harvard Dataverse doi:10.7910/DVN/QGH7P4, CC0 1.0, no restricted files.
##File read: data/raw/survey_experiment.tab (Dataverse "original format" download,
##survey_experiment.csv). Wording from documentation/instruments/survey-experiment-survey.docx
##(Qualtrics export with ${e://Field/Sar_*} placeholders) and documentation/codebook.docx; the
##filled-in vignette text and the four conditions from the article (open access), section on the
##vignette experiment. The authors' code/clean.R (read as text) gives their 0/1 codings.
##Usage: Rscript heinze_2025.R <raw dir> <output dir>
##
##2x2 factorial vignette, one vignette (task 1, profile 1) per respondent, in-person survey of
##voters. Article text: "Now, I'll tell you about the president of a village council here in
##Maharashtra. [Bharti/Rohit] [Marathe/Kamble] is a 42-year old [female/male] president. [She/he]
##is a [Maratha/Dalit] president, in a village where more than half of people are Maratha.
##[She/he] has been the president of the village council for one year." Gender and caste were
##randomized independently with equal probabilities (simple randomization to four presidents).
##Each factor was shown through several words that move together: gender = first name Bharti
##(female) / Rohit (male) + "female/male" + pronoun; caste = surname Kamble (Dalit) / Marathe
##(Maratha) + "Dalit/Maratha". attr_gender stores "female"/"male" and attr_caste
##"Dalit"/"Maratha" (the category words as displayed); the source records only the name
##fields (sarpanchgender bharti/rohit, sarpanchcaste kamble/marathe), mapped by the article.
##Outcomes (ratings, 0/1 judgements about the single president; coding as clean.R):
##  rating_authority (q9.2.1) "...do you think that a president like [name] would be the one
##     who is the most active in taking village decisions, or do you think it would be someone
##     else?" 1 = Sarpanch, 0 = Someone else.
##  rating_resign (q9.2.3) "Imagine that influential people in this village ask [name] to resign
##     from their post as sarpanch. Do you think that a president like [name] would accept this
##     request and resign, or would [she/he] resist the request?" 1 = Resign, 0 = Resist.
##  rating_backlash (q9.2.4) "Now imagine that [name] becomes quite powerful as a sarpanch. ...
##     Do you think that [name] would likely face backlash from influential people in the
##     village? For example, threats, bullying, or violence?" 1 = Yes, it is likely, 0 = No.
##Follow-up select-all and free-text items are not in the deposit.
##Covariates as answer text (instrument wording): cov_location_type (1.2), cov_age (2.1, years),
##cov_gender (2.2 Male/Female; no "Other" in data), cov_religion (2.3), cov_caste (2.4),
##cov_education (2.5, e.g. "up to 10th grad" as in the instrument), cov_voted_2019 (3.2 Yes/No),
##cov_knowledge_local_politics (4.15), cov_women_vote_norm (10.1, percent of locality who think
##it appropriate that women vote, 0-100). No survey weight in the deposit. No IDs in the deposit;
##id = row number in the source file.
##Dropped: 2 respondents with no recorded condition ("NA NA", as clean.R) and 6 with all three
##outcomes missing. N = 2,360; the article reports 2,347 (likely after dropping missing
##covariates for the adjusted OLS; not checked). Spot check: authority means by condition
##reproduce the article (Rohit Marathe 0.77, Bharti Marathe 0.74, Rohit Kamble 0.63, Bharti
##Kamble 0.58).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "survey_experiment.csv"), na.strings = c("", "NA"))
s[, row := .I]
s <- s[!is.na(sarpanchgender) & !is.na(sarpanchcaste)]
yn <- function(x, one, zero) { stopifnot(all(x %in% c(one, zero, NA))); fifelse(x == one, 1L, 0L) }
d <- data.table(id = s$row, task = 1L, profile = 1L,
                rating_authority = yn(s$q9.2.1, "Sarpanch", "Someone else"),
                rating_resign = yn(s$q9.2.3, "Resign", "Resist"),
                rating_backlash = yn(s$q9.2.4, "Yes, it is likely", "No, it is not likely"))
stopifnot(all(s$sarpanchgender %in% c("bharti", "rohit")), all(s$sarpanchcaste %in% c("kamble", "marathe")))
d[, attr_gender := fifelse(s$sarpanchgender == "bharti", "female", "male")]
d[, attr_caste := fifelse(s$sarpanchcaste == "kamble", "Dalit", "Maratha")]
stopifnot(all(s$q2.2 %in% c("Male", "Female")))
d[, `:=`(cov_location_type = s$q1.2, cov_age = as.integer(s$q2.1), cov_gender = tolower(s$q2.2), cov_religion = s$q2.3,
         cov_caste = s$q2.4, cov_education = s$q2.5, cov_voted_2019 = s$q3.2, cov_knowledge_local_politics = s$q4.15,
         cov_women_vote_norm = as.integer(s$q10.1_1))]
d <- d[!(is.na(rating_authority) & is.na(rating_resign) & is.na(rating_backlash))]
stopifnot(nrow(d) == 2360L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "heinze_2025_sarpanch_vignette.csv"))
