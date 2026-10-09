##Trade-partner conjoint (US, MTurk) from
##Carnegie, A., & Gaikwad, N. (2022). Public opinion on geopolitics and trade: Theory and
##evidence. World Politics, 74(2), 167-204. https://doi.org/10.1017/S0043887121000265
##Replication data: Harvard Dataverse doi:10.7910/DVN/4DE06H, CC0 1.0, no restricted files.
##Files read: US_SurveyData_insheet.csv (tab-separated despite the name; saved as us.csv) and
##"Codebook of Variables.docx" (question wording, covariate codes). US_SurveyAnalysis.do read as
##text. The India files hold only the vignette experiment (readme), so no India table.
##Usage: Rscript carnegie_2022.R <dir holding us.csv> <output dir>
##
##US respondents (Amazon MTurk; 1,209 rows in the deposit, 1,208 with conjoint answers), 5 paired
##conjoint tasks ("five conjoint experiments", codebook) comparing two countries, Country A
##(profile 1) and Country B (profile 2). Six attributes, level text as displayed (f-columns hold
##the attribute label and the two countries' levels for each row of the table):
##  attr_alliance "Country alliance with America:" (Ally of America / Adversary of America)
##  attr_military_size "Current military size of other country:" (Much smaller / A little smaller
##     than the American military)
##  attr_military_growth "Trade will increase the size of the military of the other country by:"
##     (No change in size / A little / A lot)
##  attr_conflict "Trade will change the likelihood the other country engages in conflict with
##     the US by:" (Likelihood stays the same / decreases a little / decreases a lot)
##  attr_us_economy "Impact of trade on US economy:" (Helps a little / Neither helps nor hurts /
##     Hurts a little)
##  attr_government "Government type of other country:" (Democracy / Not a democracy)
##Row order of the attributes was randomized once per respondent (the same order in all 5 tasks,
##checked); attrpos_<name> = the row (1-6). Column layout: f<t><k> = label of row k in task t,
##f<t>1<k> / f<t>2<k> = Country A / B level in that row.
##Outcomes (codebook wording):
##  choice = q7<t>, "Which country should America increase trade with?" Country A (1) / B (2);
##     forced, exactly one per task.
##  rating = q8<t>_1 / q8<t>_2, "How much would you support or oppose increasing trade with
##     Country A [B]" 1 = oppose .. 10 = support, raw.
##Level weights are unequal (Adversary 75% of profiles, "Likelihood stays the same" 50%); no
##source seen states the probabilities (article not read: paywalled) -> observed.
##Restriction (observed in the data, not documented in the deposit): an "Ally of America" always
##has conflict level "Likelihood stays the same" (the decrease levels occur only for adversaries;
##checked in the script); estimate the conflict AMCE within adversaries.
##Covariates (codes -> text from the codebook): cov_gender (1 male, 0 female); cov_age; cov_education_code (educ 1-6, codebook
##labels only the ends: 1 "did not graduate from high school" .. 6 "Postgraduate degree");
##cov_religion, cov_race, cov_income, cov_party_id ("Strong Republican" .. "Strong Democrat"),
##cov_liberal (1 Very Conservative .. 5 Very Liberal, numeric), cov_foreign_interest,
##cov_job_security, cov_occupation_cat, cov_marital_status (text from the codebook lists).
##Dropped: mturkcode (a numeric survey code; re-keyed to integers in file order), the free-text
##occupation, the race/female dummies, the authors' averaged scales (dove, isolation,
##internationalism, nationalism, ethnocentrism), and the separate single-factor vignette
##experiment (adversary/military/peace/democracy_treat, support_trade*), a different design.
##N: 1,208 respondents with conjoint answers (paper N not checked). No weight. No repeated task.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "us.csv"), sep = "\t", na.strings = c("", "NA"))
s[, id := .I]
lab <- c("Country alliance with America:" = "alliance", "Current military size of other country:" = "military_size",
         "Trade will increase the size of the military of the other country by:" = "military_growth",
         "Trade will change the likelihood the other country engages in conflict with the US by:" = "conflict",
         "Impact of trade on US economy:" = "us_economy", "Government type of other country:" = "government")
rows <- list()
for (t in 1:5) for (p in 1:2) {
  ch <- s[[paste0("q7", t)]]; rt <- s[[sprintf("q8%d_%d", t, p)]]
  d <- data.table(id = s$id, task = t, profile = p, choice = as.integer(ch == p), rating = as.integer(rt))
  for (k in 1:6) {
    nm <- lab[s[[sprintf("f%d%d", t, k)]]]
    stopifnot(!anyNA(nm[!is.na(ch)]))
    lv <- s[[sprintf("f%d%d%d", t, p, k)]]
    for (n in unique(na.omit(nm))) {
      w <- which(nm == n)
      set(d, w, paste0("attr_", n), lv[w]); set(d, w, paste0("attrpos_", n), k)
    }
  }
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows, use.names = TRUE, fill = TRUE)
d <- d[!is.na(choice) | !is.na(rating)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% c(1:10, NA)))
for (n in lab) stopifnot(!anyNA(d[[paste0("attr_", n)]]))
# attribute order is the same in all tasks of a respondent
stopifnot(d[attr_alliance == "Ally of America", all(attr_conflict == "Likelihood stays the same")])
stopifnot(d[, uniqueN(paste(attrpos_alliance, attrpos_conflict, attrpos_government)), id][, all(V1 == 1)])
txt <- function(v, l) { v <- as.integer(v); stopifnot(all(v %in% c(seq_along(l), NA))); l[v] }
cov <- s[, .(id, cov_gender = fifelse(gender == 1, "male", fifelse(gender == 0, "female", NA_character_)),
             cov_age = as.integer(age), cov_education_code = as.integer(educ),
             cov_religion = txt(religion, c("Protestant", "Catholic", "Jewish", "Muslim", "Mormon", "Not religious", "Other")),
             cov_race = txt(race, c("White", "Black/African American", "American Indian or Alaska Native", "Asian",
                                    "Native Hawaiian or other Pacific Islander", "Hispanic")),
             cov_income = txt(income, c("Under $10,000", "$10,000-$24,999", "$25,000-$34,999", "$35,000-$49,999", "$50,000-$64,999",
                                        "$65,000-$84,999", "$85,000-$99,999", "$100,000-$149,999", "$150,000-$174,999",
                                        "$175,000-$199,999", "$200,000-$249,999", "$250,000 and above")),
             cov_party_id = txt(democrat, c("Strong Republican", "Moderate Republican", "Independent", "Moderate Democrat", "Strong Democrat")),
             cov_liberal = as.integer(liberal),
             cov_foreign_interest = txt(foreign_interest, c("Very interested", "Moderately interested", "Slightly interested", "Not interested at all")),
             cov_job_security = txt(secure_job, c("Very secure", "Somewhat secure", "Neither secure nor insecure", "Somewhat insecure", "Very insecure")),
             cov_occupation_cat = txt(occupation_cat, c("Management, business, and financial occupations", "Professional and related occupations",
                                                        "Service occupations", "Sales and related occupations", "Office and administrative support occupations",
                                                        "Farming, fishing, and forestry occupations", "Construction and extraction occupations",
                                                        "Installation, maintenance and repair occupations", "Production occupations",
                                                        "Transportation and material moving occupations", "Other", "Unemployed")),
             cov_marital_status = txt(marital_status, c("Married, living with spouse", "Separated", "Divorced", "Widowed", "Single, never married")))]
stopifnot(all(s$gender %in% c(0, 1, NA)))
d <- merge(d, cov, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating", paste0("attr_", lab), paste0("attrpos_", lab)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "carnegie_2022_trade_partners.csv"))
