##COVID-19 neighbour vignette experiment (Malawi, Zambia) from
##Ferree, K. E., Dulani, B., Harris, A. S., Kao, K., Lust, E., Ahsan Jansson, C., &
##Metheney, E. A. (2023). Symptoms and stereotypes: Perceptions and responses to Covid-19 in
##Malawi and Zambia. Comparative Political Studies, 56(12), 1795-1823.
##https://doi.org/10.1177/00104140231152753
##Replication data: Harvard Dataverse doi:10.7910/DVN/B5WIC9, CC0 1.0. Files read:
##MCSR1.dta, MCSR2.dta (Malawi phone survey rounds 1 and 2), ZCSR1.dta (Zambia phone
##survey). Read as text: "Data Preparation.do" (raw piped texts -> the authors' codes),
##Analysis.do, DATA READ ME.txt, MCSR1_Survey.doc (converted to text; the only deposited
##questionnaire with the vignette). The census files (>380 MB) are not used.
##Usage: Rscript ferree_2023.R <dir holding the three .dta files> <output dir>
##
##Phone surveys; each respondent heard ONE vignette (task = 1, profile = 1): "Now I would
##like you to imagine the following situation. Your neighbor, a {0} {1} {2} who has lived in
##your community for {3} has {4}." (MCSR1 questionnaire Q43), five randomized fill-ins:
##age (25 / 60 year old), gender (man / woman), time in community (many years / a few
##months), family origin (Malawi: Malawian / Mmwenye / Zambian; Zambia: Malawian /
##Tanzanian / Zambian) and symptoms (a badly injured and infected leg / a high fever / a bad
##cough and high fever). The deposit holds the authors' codes; the displayed fill-in text is
##restored from Data Preparation.do, which builds each code from the raw piped string
##(e.g. NeighborSymptoms = 2 if Q_42 == "a high fever"); the remaining (first) level of
##each attribute is any other non-empty string and its text comes from the MCSR1
##questionnaire (25 year old, man, many years, Malawian, a badly injured and infected leg).
##The Malawi round 2 and Zambia questionnaires for this module are not deposited; the
##authors' code reads the same piped strings there, and the Zambia "Malawian" level is
##inferred the same way. Enumerators read the script in the respondent's language (MCSR1
##Q37); only the English text survives.
##Two tables: ferree_2023_covid_neighbor_mw (Malawi rounds 1 and 2, same attribute text,
##pooled by the authors in Pooled_Dataset_MalawiR1R2.dta / Table A28; trial_round = 1/2;
##the rounds are separate samples of the same panel frame and ids are NOT linked across
##rounds) and ferree_2023_covid_neighbor_zm (Zambia; family-origin levels differ).
##Outcomes (0/1, the authors' recodes of the raw answers, which are not deposited):
##  rating_help: "If this person needed you to accompany him/her to the hospital, would you
##    help him/her?" 1 Yes, 0 No; "Don't Know/Refuse to Answer" -> NA.
##  rating_move_freely: "Do you think this person should be allowed to move freely about the
##    community or made to stay at home?" 1 Move freely, 0 Stay at home; DK/refuse -> NA.
##  rating_has_covid: "Do you think this person has Covid-19/the corona virus?" 1 Yes, 0 No;
##    "Not sure what COVID-19/corona virus is" (Zambia: "Don't Know") and refusals -> NA.
##Rows with no outcome at all are omitted.
##Covariates: cov_gender (Gender 0 male / 1 female), cov_age (Age, years; the authors set
##<18 and >100 to missing), cov_education_group (the authors' 4-group recode, value-label
##text), cov_ethnicity (value-label text; "Don't Know/Refuse to Answer" -> NA),
##cov_region (Malawi round 2 only, Q_33 as stored). Round 1 education labels ("Little to No
##Schooling", ..., "Post Secondary Schooling") are harmonised to the round 2 / Zambia labels
##("LittleNoSchooling", ..., "University"): same codes, same four groups in the authors' recode. Dropped: SbjNum (survey subject number,
##re-keyed), derived dummies (OutsiderTreatment, HigherEducation, CtrlAge, *NeighborBias,
##SalientGroup, PreviousRespondent, CashJob), the "willing to have ... as neighbors" items.
##No weights in the deposit. No PII.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f, round, origin) {
  s <- as.data.table(read_dta(file.path(raw, f)))
  num <- function(v) as.integer(zap_labels(s[[v]]))
  lt <- function(v) { x <- as.character(as_factor(s[[v]], levels = "labels")); x[x %in% c("Don't Know/Refuse to Answer", "Don't Know/Refuse to answer")] <- NA; x }
  d <- data.table(sbj = s$SbjNum, task = 1L, profile = 1L,
    rating_help = num("Help"), rating_move_freely = num("MoveFreely"), rating_has_covid = num("HasCovid"),
    attr_age = c("25 year old", "60 year old")[num("NeighborAge")],
    attr_gender = c("man", "woman")[num("NeighborGender")],
    attr_time_in_community = c("many years", "a few months")[num("NeighborTimeInCommunity")],
    attr_family_origin = origin[num("NeighborFamilyOrigin")],
    attr_symptoms = c("a badly injured and infected leg", "a high fever", "a bad cough and high fever")[num("NeighborSymptoms")],
    trial_round = round,
    cov_gender = c("male", "female")[num("Gender") + 1L], cov_age = num("Age"),
    cov_education_group = as.character(as_factor(s$Education, levels = "labels")),
    cov_ethnicity = lt("Ethnicity"))
  if ("Region" %in% names(s)) d[, cov_region := as.character(s$Region)]
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), uniqueN(d$sbj) == nrow(d),
            all(unlist(d[, .(rating_help, rating_move_freely, rating_has_covid)]) %in% c(0:1, NA)))
  d[!(is.na(rating_help) & is.na(rating_move_freely) & is.na(rating_has_covid))]
}
mw <- rbind(rd("MCSR1.dta", 1L, c("Malawian", "Mmwenye", "Zambian")),
            rd("MCSR2.dta", 2L, c("Malawian", "Mmwenye", "Zambian")), fill = TRUE)
zm <- rd("ZCSR1.dta", 1L, c("Malawian", "Tanzanian", "Zambian"))[, trial_round := NULL]
mw[, id := as.integer(frank(list(trial_round, sbj), ties.method = "dense"))]
zm[, id := as.integer(frank(sbj, ties.method = "dense"))]
# round 1 spells the education groups differently from round 2 and Zambia (same four groups,
# same codes); harmonise to the round 2 / Zambia label text
e1 <- c("Little to No Schooling" = "LittleNoSchooling", "Primary Schooling" = "PrimarySchooling",
        "Secondary Schooling" = "SecondarySchooling", "Post Secondary Schooling" = "University")
mw[cov_education_group %in% names(e1), cov_education_group := e1[cov_education_group]]
stopifnot(all(c(mw$cov_education_group, zm$cov_education_group) %in% c(unname(e1), NA)))
for (x in list(list(mw, "mw"), list(zm, "zm"))) {
  d <- x[[1]][, sbj := NULL]; setcolorder(d, c("id", "task", "profile")); setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("ferree_2023_covid_neighbor_", x[[2]], ".csv")))
}
