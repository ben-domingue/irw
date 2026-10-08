##Populist-statement politician conjoints (US samples 1 and 2, UK sample 3) from
##Neuner, F. G. (2025). Can (thin) populism be manipulated without manipulating host ideology?
##Evidence from a conjoint validation approach. Journal of Experimental Political Science, 1-15.
##https://doi.org/10.1017/XPS.2025.10018
##Replication data: Harvard Dataverse doi:10.7910/DVN/JIUPOU, CC0 1.0, no restricted files.
##Files read: Prolific_US_Raw.csv (samples 1 and 2) and Prolific_UK_Raw.csv (sample 3)
##(?format=original; Qualtrics exports with 2 extra header rows). ReadMe.txt and script_02-04.R
##read as text (not run). Question wording, answer codes and the vignette layout from the US
##survey instrument on OSF (doi:10.17605/OSF.IO/NUAVW, "Survey Instrument for US Studies.pdf");
##the UK instrument on OSF was not downloadable (403).
##Usage: Rscript neuner_2025.R <dir holding Prolific_*_Raw.csv> <output dir>
##
##Prolific samples; the analysis keeps Finished == 1 (script_02/03/04), as here: sample 1 (US,
##`Sample` ONE) 699, sample 2 (US, TWO) 704, sample 3 (UK) 730 finished respondents; 41 finished
##UK respondents have no conjoint answers at all and 40 of them drop out (no outcome), leaving 690.
##Each respondent compared 6 pairs of hypothetical politicians. Text vignette (instrument):
##"Please read the statements from two hypothetical politicians and then answer the questions
##below. Politician 1: <people-centrism> <anti-elitism> <filler> Politician 2: ..." In sample 2 the
##politician's party was shown in brackets after "Politician 1" ("Politician 1 (Democrat): ...");
##in samples 1 and 3 the party is drawn but not shown (ReadMe), so attr_partisanship is "(not
##shown)" there. Sample 2 therefore has a different displayed attribute set, and sample 3 a
##different country and ideology question, so there are three tables:
##neuner_2025_populism_us1, neuner_2025_populism_us2, neuner_2025_populism_uk.
##Attributes: Conjoint SDT columns F-<pair>-<politician>-<k>; k = 1 people-centrism, 2 anti-
##elitism, 3 filler, 4 partisanship (attribute names F-<pair>-<k> are the same for every
##respondent: fixed order, as in the instrument's sentence). People-centrism and anti-elitism have
##a control level with no statement (empty in the export): the sentence was left out by design,
##stored as "(not shown)". Text otherwise exactly as displayed.
##Outcomes (the same four forced choices and four ratings for every pair):
##  "Based on the above information, which politician do you think is more likely to:" Politician 1
##  / Politician 2, for: choice_listen "Say that politicians should always listen to the people"
##  (pair<t>_choice_1), choice_crooked "Say that many people in the political class are crooked"
##  (_choice_2), choice_immigration "Say that immigration should be reduced" (_choice_3),
##  choice_conservative "Have conservative ideology" (_choice_4). No opt-out.
##  rating_listen / rating_crooked / rating_immigration: "How likely do you think the two
##  politicians are to say that '...'? - Politician 1/2", 1 Not at all likely, 2 A little likely,
##  3 Somewhat likely, 4 Very likely, 5 Extremely likely.
##  rating_ideology: US "How liberal or conservative do you think the two politicians are?" 1 Very
##  liberal .. 5 Very conservative; UK "How politically left or right do you think the two
##  politicians are?" 1-5 (UK end labels not available; ReadMe/appendix H say the wording differs).
##Covariates: cov_birth_year (yearborn as entered, when > 1000; one US value implies age 152, kept
##as recorded), cov_age (yearborn when the respondent typed an age instead of a year, < 1000; the
##authors use 2024 [UK 2025] - yearborn or the typed age), cov_gender (1 Male, 2 Female, 3 Other -> male/female/other; US
##instrument, authors' recode in both countries), cov_attention_pass (attent_vignette_out == 4
##"movies" topic, the authors' `attentive`; NA if unanswered). US only: cov_race, cov_education,
##cov_income (instrument answer text; "Prefer not to answer" -> NA), cov_party_id (pid0:
##Republican / Democrat / Independent). UK only: cov_party_id (pid0 1-10 -> the authors' labels
##Conservative, Labour, Liberal Democrat, SNP, Plaid Cymru, Reform UK, UKIP, Green Party, Other,
##None, script_03), cov_race_code, cov_education_code, cov_income_code (UK codes kept: the authors'
##label lists were written for consecutive codes but education and income use 1,2,3,5,6, and the
##race labels are the US ones, so no checked source maps them).
##Dropped: ResponseId (re-keyed), browser metadata, free text (open_end, *_TEXT), populism
##attitude items and other survey items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs <- c("people_centrism", "anti_elitism", "filler", "partisanship")
ch <- c(listen = 1, crooked = 2, immigration = 3, conservative = 4)
rt <- c(listen = "people", crooked = "elite", immigration = "immigration", ideology = "ideology")
lab <- function(x, l) { r <- unname(l[x]); r[x == ""] <- NA; r }
build <- function(x, s, show_party, tab, cov) {
  x <- x[Finished == "1"]
  x[, id := .I]
  rows <- rbindlist(lapply(1:6, function(t) rbindlist(lapply(1:2, function(p) {
    d <- data.table(id = x$id, task = t, profile = p)
    for (nm in names(ch)) { v <- x[[sprintf("%s_pair%d_choice_%d", s, t, ch[[nm]])]]; set(d, j = paste0("choice_", nm), value = fifelse(v == "", NA_integer_, as.integer(v == as.character(p)))) }
    for (nm in names(rt)) { v <- x[[sprintf("%s_pair%d_%s_%d", s, t, rt[[nm]], p)]]; set(d, j = paste0("rating_", nm), value = suppressWarnings(as.integer(v))) }
    for (k in 1:4) { v <- trimws(x[[sprintf("F-%d-%d-%d", t, p, k)]]); set(d, j = paste0("attr_", attrs[k]), value = fifelse(v == "", "(not shown)", v)) }
    if (!show_party) d[, attr_partisanship := "(not shown)"]
    d
  }))))
  for (t in 1:6) stopifnot(all(x[[sprintf("F-%d-1", t)]] == "People-centrism"), all(x[[sprintf("F-%d-2", t)]] == "Anti-elitism"),
                           all(x[[sprintf("F-%d-3", t)]] == "Filler"), all(x[[sprintf("F-%d-4", t)]] == "Partisanship"))
  oc <- grep("^(choice|rating)_", names(rows), value = TRUE)
  rows <- rows[rowSums(!is.na(rows[, ..oc])) > 0]
  for (nm in names(ch)) { cc <- paste0("choice_", nm); z <- rows[, .(s = sum(get(cc)), n = sum(!is.na(get(cc)))), .(id, task)]; stopifnot(all(z$n %in% c(0, 2)), all(z[n == 2]$s == 1)) }
  stopifnot(all(unlist(rows[, lapply(.SD, function(v) all(v %in% c(NA, 1:5))), .SDcols = patterns("^rating_")])))
  d <- merge(rows, cov(x), by = "id")
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(tab, ".csv")))
}
byr <- function(yb) { y <- suppressWarnings(as.integer(yb)); fifelse(y > 1000, y, NA_integer_) }
age <- function(yb) { y <- suppressWarnings(as.integer(yb)); fifelse(y < 1000, y, NA_integer_) }
att <- function(v) fifelse(v == "", NA_integer_, as.integer(v == "4"))
g3 <- c("1" = "male", "2" = "female", "3" = "other")
us_cov <- function(x) x[, .(id, cov_birth_year = byr(yearborn), cov_age = age(yearborn), cov_gender = lab(gender, g3),
  cov_race = lab(race, c("1" = "White", "2" = "Black", "3" = "Hispanic", "4" = "Asian", "5" = "Other")),
  cov_education = lab(educ, c("1" = "Some high school", "2" = "High school graduate", "3" = "Some college", "4" = "College graduate", "5" = "Some graduate school", "6" = "Graduate school degree")),
  cov_income = lab(income, c("1" = "Under $20,000", "2" = "$20,001 – $50,000", "3" = "$50,001 – $100,000", "4" = "$100,001 – $150,000", "5" = "Above $150,000", "6" = NA)),
  cov_party_id = lab(pid0, c("1" = "Republican", "2" = "Democrat", "3" = "Independent")),
  cov_attention_pass = att(attent_vignette_out))]
uk_cov <- function(x) x[, .(id, cov_birth_year = byr(yearborn), cov_age = age(yearborn), cov_gender = lab(gender, g3),
  cov_party_id = lab(pid0, setNames(c("Conservative", "Labour", "Liberal Democrat", "SNP", "Plaid Cymru", "Reform UK", "UKIP", "Green Party", "Other", "None"), 1:10)),
  cov_race_code = suppressWarnings(as.integer(race)), cov_education_code = suppressWarnings(as.integer(educ)),
  cov_income_code = suppressWarnings(as.integer(income)), cov_attention_pass = att(attent_vignette_out))]
us <- fread(file.path(raw, "Prolific_US_Raw.csv"), encoding = "UTF-8", colClasses = "character")[-(1:2)]
uk <- fread(file.path(raw, "Prolific_UK_Raw.csv"), encoding = "UTF-8", colClasses = "character")[-(1:2)]
stopifnot(us[Finished == "1", .N, Sample][order(Sample)]$N == c(699, 704), uk[Finished == "1", .N] == 730)
build(us[Sample == "ONE"], "s1", FALSE, "neuner_2025_populism_us1", us_cov)
build(us[Sample == "TWO"], "s2", TRUE, "neuner_2025_populism_us2", us_cov)
build(uk, "s3", FALSE, "neuner_2025_populism_uk", uk_cov)
