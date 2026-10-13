##Factorial survey of older adults' well-being (Welzijnsmeter, Flanders, 5 monthly waves 2020) from
##Van Loon, V., & Decancq, K. (2026). Who are the worst-off? Objective, subjective, and
##preference-based approaches to measure older adults' well-being. Social Indicators Research.
##https://doi.org/10.1007/s11205-026-03926-5 ; the same experiment is analysed in Van Loon, V., &
##Decancq, K. (2022). Using a factorial survey to estimate the relative importance of well-being
##dimensions according to older people: insights from a repeated survey experiment in Flanders.
##Innovation in Aging, 6(3), igac034. https://doi.org/10.1093/geroni/igac034
##Data: Zenodo doi:10.5281/zenodo.22208794 (concept DOI; version record 22208795), CC BY 4.0, no
##restricted files. File read: Welzijnsmeter_w1-5_vig.dta (Stata value labels used for the levels;
##the _period.dta file is not a vignette file and was not read).
##Usage: Rscript vanloon_2026.R <dir holding the .dta> <output dir>
##
##Adults aged 50+ in Flanders (Dutch; 21 vignette sets answered in French), an online panel
##re-contacted in five waves (May-Dec 2020; 1,003 / 994 / 1,022 / 997 / 991 respondents per wave
##in the file). Each respondent rated 7 text vignettes per wave (vig_run = order 1-7), 6
##attributes with 4 levels: health problems, social relations, engagement (useful or meaningful
##activities), leisure, religiosity/spirituality, household income. ONE TABLE for all waves: same
##attribute set and design, same panel (the 2022 paper analyses the repeated experiment); trial_wave
##marks the wave; id = id_res (the panel's respondent id across waves, re-keyed to integers);
##task = (wave - 1) * 7 + vig_run, i.e. the order in which a respondent saw the vignettes if
##they answered several waves; profile = 1 (one vignette per task).
##Design (2022 paper, via the article): 4^6 = 4,096 possible vignettes; 50 decks of 7 drawn with a
##D-efficient algorithm (SAS %Mktex), respondents randomly assigned to a deck (vig_deck 1-50, any
##wave: kept as trial_deck); dimension order varied across decks (not recorded in the .dta).
##Level text is the .dta value-label text of vig_hea/soc/eng/lei/rel/inc (English): health
##severe / moderately severe / non-severe / no (health problems); the four frequency attributes
##several times per week / once per week / less than once per week / never; income 1500 / 2700 /
##3900 / 5000, which the article gives as total net household income per month in euros: stored as
##"EUR 1500 per month" etc. (unit from the article, not from the labels).
##Outcome: rating = vig, the respondent's 11-point (0-10) satisfaction rating of how much
##well-being the situation would bring about; higher = more well-being. The exact question
##wording and scale anchors are not in the deposit or the open text of the article (paraphrase).
##Not a choice. The own-life items q31-q36/q37 (the respondent's own situation) are covariates of
##the person, not the vignette, and are dropped.
##Covariates: cov_gender (q22 value labels male/female), cov_age (q21, age in years at the wave;
##"." -> NA for 7 rows), cov_language (NL/FR). trial_duplicate_deck = the file's duplicate_deck flag
##("yes" on 35 rows = 5 vignette sets; meaning not documented, kept as is). Dropped: dates, timings,
##the wide-format low*/high* columns, COVID, health, contact, care, work items, open ends.
##No survey weight in the file. N vs paper: the 2022 paper reports 800 baseline respondents (wave
##1) and 781/827/762/764 in waves 2-5; the file has 1,003 wave-1 respondents (a larger sample than
##the paper's analysis set; 1,823 distinct respondents over five waves). Flagged, all kept.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "Welzijnsmeter_w1-5_vig.dta")))
lab <- function(v) as.character(as_factor(v, levels = "labels"))
d <- data.table(id = as.integer(factor(k$id_res)), task = as.integer((k$wave - 1) * 7 + k$vig_run), profile = 1L,
                rating = as.integer(k$vig),
                attr_health = lab(k$vig_hea), attr_social_relations = lab(k$vig_soc), attr_engagement = lab(k$vig_eng),
                attr_leisure = lab(k$vig_lei), attr_religion = lab(k$vig_rel),
                attr_income = paste0("EUR ", lab(k$vig_inc), " per month"),
                trial_wave = as.integer(k$wave), trial_deck = as.integer(k$vig_deck),
                trial_duplicate_deck = ifelse(k$duplicate_deck == "yes", "yes", NA_character_),
                cov_gender = lab(k$q22), cov_age = suppressWarnings(as.integer(k$q21)), cov_language = k$language)
stopifnot(!anyNA(d$rating), !anyNA(d[, .(attr_health, attr_social_relations, attr_engagement, attr_leisure, attr_religion, attr_income)]),
          d[, .N, .(id, task)][, all(N == 1)], all(d$cov_gender %in% c("male", "female")), d[, all(rating %in% 0:10)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "vanloon_2026_older_adults_wellbeing.csv"))
