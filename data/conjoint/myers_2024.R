##Welfare-recipient stereotype rating conjoint (US, January 2021) from
##Myers, C. D., Zhirkov, K., & Lunz Trujillo, K. (2024). Who is "on welfare"? Validating the use of
##conjoint experiments to measure stereotype content. Political Behavior, 46, 89-110.
##https://doi.org/10.1007/s11109-022-09815-0
##Replication data: Harvard Dataverse doi:10.7910/DVN/6ECD1D, CC0 1.0, no restricted files.
##Files read (from replication_materials.zip): data/data_01_survey.dta (respondents),
##data/data_02_conjoint.dta (profiles and ratings); readme.txt and code/*.do read as text.
##Level text = Stata value labels. The article itself was not accessible (paywall); design facts
##are from the deposit and from the authors' follow-up (Zhirkov, Lunz Trujillo & Myers 2025, JEPS,
##"MZLT", which says its replication "exactly followed" this study's design, fielded January 2021 on
##Lucid; see zhirkov_2025.R for that later table, a different sample).
##Usage: Rscript myers_2024.R <dir holding data/> <output dir>
##
##1,893 Lucid respondents with conjoint data (data_01_survey has 1,895). Each rated up to 30 single
##profiles of a hypothetical person (1,799 rated all 30; 94 rated 22-29: profiles simply absent, no
##missing ratings), task = source `profile` (Conjoint profile no.), profile = 1.
##Outcome: rating = how typical the person described is of welfare recipients, 0-10 (JEPS
##follow-up: "rate 30 profiles total on how typical the person described in the profile is of
##welfare recipients using a 0-10 scale"); higher = more typical. End labels not in the deposit.
##This is a stereotype-content (typicality) rating, not favourability.
##Attributes (7): race (White/Black/Hispanic), gender, marital status, number of children
##(Zero-Three), immigration status, employment status, criminal record (No Criminal Record + 6 specific
##offences; the authors collapse them into drug-related / violent dummies, conj_drugs / conj_vilnt).
##"The value of each attribute in each profile is independently drawn" (JEPS follow-up). Level
##weights: criminal record is "No Criminal Record" on 1/3 of profiles and each offence ~1/9 (data;
##consistent with a no/yes draw then a uniform offence, not documented); other attributes ~uniform.
##Attribute order and presentation are not documented in the deposit.
##trial_instruction_code = `condition` ("Instruction condition", 1 or 2, no value labels): the
##article compares two versions of the task instructions (abstract: "we suggest an improvement in
##the conjoint task instructions"; code_02 estimates Figure 2 separately for condition 1 and 2);
##the wording of the two versions is not in the deposit, so the codes are kept.
##Sample: ALL respondents with ratings are kept. The article analyses non-Hispanic whites
##(`nhwhite == 1`, code_01/code_02: 1,293 with conjoint data); on that subset the Figure 2
##coefficients in data/data_03_Figure2_estimates.txt reproduce exactly (lm of rating on the authors'
##dummies by condition, e.g. Black 0.120 / 0.014, Female 0.173 / 0.205).
##Covariates (value labels -> text): cov_age (years), cov_gender (gender 1 Male / 2 Female ->
##male / female), cov_education (education labels, "Dcotorate degree" [sic] as labelled),
##cov_income (household income bracket label), cov_race (race6 label), cov_hispanic (hispanic
##label), cov_party_id7 (pid7 labels, Strong Democrat .. Strong Republican; the 140 missing are
##NA in the source). Dropped: the authors' derived dummies and indices (female, college, race5,
##nhwhite, pid8/3/2, welfare/welfar2/fire/indiv indices) and the welfare-support items wlfr1-4
##(item wording in readme.txt but no scale labels). respid is already a 1..N integer, kept as id.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- file.path(a[1], "data"); out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "data_01_survey.dta")))
cj <- read_dta(file.path(raw, "data_02_conjoint.dta"))
lab <- function(v) { l <- attr(v, "labels"); unname(setNames(names(l), l)[as.character(as.numeric(v))]) }
cv <- s[, .(id = as.integer(respid), trial_instruction_code = as.integer(condition), cov_age = as.integer(age),
            cov_gender = c(Male = "male", Female = "female")[lab(gender)], cov_education = lab(education),
            cov_income = lab(income), cov_race = lab(race6), cov_hispanic = lab(hispanic), cov_party_id7 = lab(pid7))]
d <- data.table(id = as.integer(cj$respid), task = as.integer(cj$profile), profile = 1L, rating = as.numeric(cj$rate),
                attr_race = lab(cj$attr_race), attr_gender = lab(cj$attr_gend), attr_marital = lab(cj$attr_mrtl),
                attr_children = lab(cj$attr_kids), attr_immigration = lab(cj$attr_imgr), attr_employment = lab(cj$attr_jobs),
                attr_criminal_record = lab(cj$attr_crim))
ac <- grep("^attr_", names(d), value = TRUE)
stopifnot(!anyNA(d[, ..ac]), !anyNA(d$rating), !anyDuplicated(d[, .(id, task)]), all(d$id %in% cv$id))
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "rating", ac, "trial_instruction_code"))
setorder(d, id, task, profile)
stopifnot(uniqueN(d$id) == 1893, nrow(d) == 56655)
fwrite(d, file.path(out, "myers_2024_welfare_stereotypes.csv"))
