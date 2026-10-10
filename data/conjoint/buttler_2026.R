##Hiring factorial survey (job-candidate vignettes rated by recruiters; DE, NO, PL, RO) from
##Buttler, D., Imdorf, C., Bjornshagen, V., et al. (2026). Hiring discrimination in the
##organisational context: A harmonized factorial survey dataset from four European countries
##(Germany, Norway, Poland, Romania). Scientific Data, 13, 896.
##https://doi.org/10.1038/s41597-026-07187-2 (PATHS2INCLUDE, Horizon Europe 101094626)
##Data: OSF node 74q69, doi:10.17605/OSF.IO/74Q69, CC BY 4.0 (node licence; no stricter
##statement in the files). File read: hiring_discrimination_dataset.dta. Also read:
##codebook.xlsx, questionnaire_for_codebook.pdf (pdftotext) and the data descriptor (Nature HTML;
##Methods "Vignette dimensions and design", "Response scales", "Data Records").
##hiring_discrimination_dataset.xlsx (same data) not used.
##Usage: Rscript buttler_2026.R <dir holding hiring_discrimination_dataset.dta> <output dir>
##
##2,506 recruiters (online panels A-E plus the project's own recruitment; panel names
##anonymized by the depositors) in Germany (758), Norway (441), Poland (689) and Romania (618)
##each rated 6 vignettes describing a fictional candidate for a job the respondent chose (ICT
##technician, office clerk, secretary, bookkeeping clerk, sales worker; cov_job). Respondents
##with more than one quality flag were already excluded by the depositors (codebook); one flag is
##kept (cov_sum_of_flags, cov_flag_comment). One vignette = one task with one profile
##(task = vorder, the display order, randomized per respondent; profile = 1).
##ONE TABLE with cov_country: the descriptor presents one harmonized dataset (vignettes nested in
##respondents nested in countries), one codebook, one English set of level labels and the same
##design (144 vignettes, 24 decks) in every country.
##FIXED BLOCKED DESIGN: SAS %Mktex Resolution IV fraction of 144 vignettes (D-efficiency 86.46%),
##24 decks ("versions") of 6, decks randomly assigned to respondents, vignette order randomized
##within deck (descriptor); every deck x vignette number holds one fixed combination (checked).
##trial_deck = deck, trial_vignette = vignette number within the deck.
##Attributes (8; codebook value labels = the English level text; "all the variables' values are
##presented in English" (descriptor); the German/Norwegian/Polish/Romanian display text is not
##deposited, so label_language = en):
##referral, gender, country of origin, where educated, host-language level, partnership,
##parenthood, type of experience. Country of origin level 3 ("other ethnic group" in the value
##labels) is stored as the nationality the codebook says was shown: Syrian (Norway, Germany),
##Nepali (Romania), Belarusian (Poland). Level 1 stays "native" (the codebook does not give the
##displayed wording). The codebook's "rises a preschool-aged child" spelling is kept.
##RESTRICTION (stated in the descriptor: "two implausible cases were ruled out by design";
##checked in the data): native candidates are always educated in the host country and always at
##proficient (C2) language level, so education and language shares are 2:1.
##Outcomes (questionnaire section 6, English master):
##  rating_interview (d11): "How likely is that you will invite this person for the interview
##    given the needs and characteristics of your organisation/ organisation you recruit for?
##    (0 - very unlikely; 10 - very likely)". Stored 0-10 (the codebook's "1-10" is wrong; data
##    and questionnaire have 0).
##  rating_employ (d12): "How likely is that this person would be employed ..." same scale.
##    The order of d11/d12 was randomized per respondent (trial_d1_order: 1 = d11 first).
##  rating_final_comparison (d2), raw codes 0/1/2: after the six vignettes the two candidates
##    with the highest d11 were shown side by side ("If you had to choose one of the two
##    candidates presented below, which candidate would you prefer for the position of (chosen
##    job) ...? [Based on d11 score]"); ties for the top two were broken at random (descriptor).
##    Codebook labels: 0 not chosen (not in the comparison), 1 best candidate, 2 2nd best
##    candidate; every respondent has exactly one 1 and one 2. The 1-coded candidate never has a
##    lower d11 than the 2-coded one (equal d11 in 1,580 of 2,506 respondents), so whether 1 is
##    the respondent's pick or partly the d11 ranking is not stated; kept raw as a rating, not a
##    choice (it compares profiles across tasks, and its pair is not randomized).
##Covariates (answer text from the .dta value labels, identical to codebook.xlsx): cov_country,
##cov_gender (sex: Female -> female, Male -> male, Other -> other, "I don't want to categorise
##myself by gender" -> NA), cov_age_group (age band text), cov_tertiary_degree (edulvl,
##"Educational level (tertiary degree)", Yes/No), cov_duration_sec (total_time, whole survey),
##cov_panel (source, anonymized panel letter), cov_job, and every other respondent-level
##question under its source name as answer text (recruitment channels rch*, information
##sources rt*, others involved rcper*, jbtitle, organisation and position items, eduhr, child,
##ethn, social-desirability items sdr1-5). trial_duration_sec = vign_time (seconds on this
##vignette). No survey weight in the deposit. id = source respondent id (integer, not a
##platform id).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
h <- read_dta(file.path(raw, "hiring_discrimination_dataset.dta"))
lab <- function(v) { x <- as.character(as_factor(h[[v]], levels = "labels")); x[is.na(h[[v]])] <- NA; trimws(x) }
country <- lab("country")
stopifnot(nrow(h) == 15036, setequal(unique(country), c("Germany", "Norway", "Poland", "Romania")))
nat <- lab("x3_nat")
other <- c(Germany = "Syrian", Norway = "Syrian", Poland = "Belarusian", Romania = "Nepali")[country]
nat[nat == "other ethnic group"] <- other[nat == "other ethnic group"]
d <- data.table(id = as.integer(h$id), task = as.integer(h$vorder), profile = 1L,
                rating_interview = as.integer(h$d11), rating_employ = as.integer(h$d12),
                rating_final_comparison = as.integer(h$d2),
                attr_referral = lab("x1_ref"), attr_gender = lab("x2_sex"), attr_origin = nat,
                attr_education_location = lab("x4_educ"), attr_language_level = lab("x5_lglvl"),
                attr_partnership = lab("x6_part"), attr_parenthood = lab("x7_child"),
                attr_experience = lab("x8_exptyp"),
                trial_deck = as.integer(h$deck), trial_vignette = as.integer(h$vignr),
                trial_d1_order = as.integer(h$d1_order), trial_duration_sec = as.numeric(h$vign_time),
                cov_country = country)
sx <- lab("sex")
stopifnot(all(sx %in% c("Female", "Male", "Other", "I don't want to categorise myself by gender")))
d[, cov_gender := c(Female = "female", Male = "male", Other = "other")[sx]]
d[, cov_age_group := sub(" years$", "", lab("age"))]
d[, cov_tertiary_degree := lab("edulvl")]
d[, cov_duration_sec := as.numeric(h$total_time)]
d[, cov_panel := lab("source")]
d[, cov_job := lab("job")]
d[, cov_sum_of_flags := as.integer(h$sum_of_flags)][, cov_flag_comment := fifelse(h$flag_comment == "0", NA_character_, h$flag_comment)]
rest <- names(h)[match("rchuef", names(h)):match("sdr5", names(h))]
rest <- setdiff(rest, c("age", "sex", "edulvl"))
for (v in rest) d[, paste0("cov_", v) := lab(v)]
stopifnot(!anyNA(d[, .(rating_interview, rating_employ, rating_final_comparison)]),
          d[, all(rating_interview %in% 0:10) && all(rating_employ %in% 0:10)],
          d[, .N, id][, all(N == 6)], !anyDuplicated(d[, .(id, task)]),
          d[, paste(sort(rating_final_comparison), collapse = ""), id][, all(V1 == "000012")],
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          d[, uniqueN(paste(attr_referral, attr_gender, attr_education_location, attr_language_level, attr_partnership,
                            attr_parenthood, attr_experience, sub("Syrian|Belarusian|Nepali", "other", attr_origin))),
            .(trial_deck, trial_vignette)][, all(V1 == 1)],
          d[attr_origin == "native", all(attr_education_location == "in host country" & attr_language_level == "proficient level (C2)")])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "buttler_2026_hiring_vignettes.csv"))
