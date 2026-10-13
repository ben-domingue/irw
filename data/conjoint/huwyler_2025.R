##MP side-income transparency vignette experiment (seven European countries) from
##Huwyler, O., Bailer, S., & Giger, N. (2025). Transparency matters: The positive effect of
##politicians' side income disclosure on voters' perceptions. European Journal of Political
##Research.
##https://doi.org/10.1017/S1475676525100303 (open access, CC BY 4.0; read)
##Replication data: Harvard Dataverse doi:10.7910/DVN/I6VM9P, CC0 1.0. File read:
##Transparency_Survey.rds (one data.frame, one row per respondent). Read as text only:
##Readme.txt, Transparency_ReplicationScript.R.
##Usage: Rscript huwyler_2025.R <dir holding the .rds> <output dir>
##
##Omnibus online survey (Bilendi panels, quotas on age, gender, education), 29 May - 21 September 2021,
##in Switzerland (German and French versions), Belgium (Dutch, French), Germany, France, the UK,
##the Netherlands and Poland. Each respondent saw ONE fictitious Tweet (an image: an MP from the
##respondent's own national parliament posts a screenshot of their "Transparency Observatory"
##profile), so task = 1, profile = 1. No respondent id is usable (the deposit's Qualtrics
##ResponseId is dropped): id = row number of the source file.
##Factors (article Table 1 and pp. 6-8; level text is the article's English description, since the
##Tweets were translated and adapted per country and are only in the online appendix, not read):
##  attr_mp_gender      Female / Male (transp_vignette_gender F/M; the MP's name, "common first and
##                      last name combinations" per country, footnote 6)
##  attr_board_type     Company / Public interest group (orgtype C/P)
##  attr_board_seats    1 / 5 (seats)
##  attr_side_income    No disclosure / Unsalaried (pro bono) / 20% of the parliamentary salary /
##                      150% of the parliamentary salary (income IT/PB/20/150). Transparent MPs
##                      present an A rating, non-transparent MPs object to disclosure on privacy
##                      grounds and get an E rating (the two are confounded by design).
##RESTRICTIONS: 12 of the 16 org x seats x income cells were fielded (no pro bono company seats,
##no 5 seats with 20% income), each vignette shown to 1/12 of respondents, crossed with MP gender
##(24 cells, 672-701 respondents each). Hence level weights are unequal by design (income: no
##disclosure 1/3, 150% 1/3, 20% 1/6, pro bono 1/6).
##One table: the seven countries saw the same design, and the authors pool them with country fixed
##effects (country-specific level text cannot be shared, so the English descriptions are stored).
##Outcomes (two ratings of the same MP, 0-10, stored raw; wording paraphrased from p. 8; exact
##wording only in the appendix):
##  rating_trust = transp_trust, trustworthiness of the MP, 0-10 (higher = more trustworthy)
##  rating_vote  = transp_vote, whether the respondent can imagine voting for the MP, 0-10
##  The order of the two questions was randomized: trial_item_order (transp_itemorder).
##Rows with neither outcome (255) are omitted: 16,241 respondents. The article reports "more
##than 14,100 complete observations" (its models also need covariates and drop gender "prefer not
##to say").
##Covariates: cov_country (CH, BE, DE, FR, GB [source "EN"], NL, PL), cov_survey_language
##(Q_Language), cov_gender (f/m -> female/male; "prefer not to say" -> NA), cov_age (age as stored),
##cov_birth_year, cov_isced11 (ISCED 2011 level, as stored), cov_tertiary_edu (text),
##cov_left_right (left_right_1, 0-10 as stored; anchors not in deposit), cov_interest_in_pol (raw
##1-4), cov_duration_sec (whole-survey Duration (in seconds)), cov_manicheck_transparent /
##cov_manicheck_seats (the authors' correct/incorrect codings of the two manipulation checks).
##PII in the deposit, DROPPED: IPAddress, LocationLatitude/LocationLongitude, ResponseId, start/end
##timestamps, and free-text fields (job titles, employers, party write-ins, comments). Also dropped:
##all other omnibus modules, derived transparency dummy and vignette code (redundant).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "Transparency_Survey.rds")))
stopifnot(nrow(s) == 16496L)
s[, id := .I]
s <- s[!(is.na(transp_trust) & is.na(transp_vote))]
inc <- c(IT = "No disclosure", PB = "Unsalaried (pro bono)", `20` = "20% of the parliamentary salary",
         `150` = "150% of the parliamentary salary")
d <- s[, .(id = as.integer(id), task = 1L, profile = 1L,
           rating_trust = as.integer(transp_trust), rating_vote = as.integer(transp_vote),
           attr_mp_gender = c(F = "Female", M = "Male")[as.character(transp_vignette_gender)],
           attr_board_type = c(C = "Company", P = "Public interest group")[as.character(transp_vignette_orgtype)],
           attr_board_seats = as.character(transp_vignette_seats),
           attr_side_income = inc[as.character(transp_vignette_income)],
           trial_item_order = transp_itemorder,
           cov_country = c(CH = "CH", BE = "BE", DE = "DE", FR = "FR", EN = "GB", NL = "NL", PL = "PL")[as.character(country)],
           cov_survey_language = Q_Language,
           cov_gender = c(f = "female", m = "male")[as.character(gender)],
           cov_age = as.integer(age), cov_birth_year = as.integer(year_of_birth),
           cov_isced11 = as.integer(isced11), cov_tertiary_edu = tertiary_edu,
           cov_left_right = as.integer(left_right_1), cov_interest_in_pol = as.integer(interest_in_pol),
           cov_duration_sec = as.integer(Duration..in.seconds.),
           cov_manicheck_transparent = transp_manicheck_istransp_correct,
           cov_manicheck_seats = transp_manicheck_numbseat_correct)]
for (v in c(grep("^attr_", names(d), value = TRUE), "cov_country", "trial_item_order")) stopifnot(!anyNA(d[[v]]))
stopifnot(d$attr_board_seats %in% c("1", "5"), uniqueN(d[, .(attr_board_type, attr_board_seats, attr_side_income)]) == 12L,
          d[, all(rating_trust %in% c(0:10, NA) & rating_vote %in% c(0:10, NA))])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "huwyler_2025_side_income.csv"))
