##Congressional candidate conjoint with randomized issue positions from
##Leeper, T. J., & Robison, J. (2020). More important, but for what exactly? The insignificant
##role of subjective issue importance in vote decisions. Political Behavior, 42(1), 239-259.
##https://doi.org/10.1007/s11109-018-9494-0
##Replication data: Harvard Dataverse doi:10.7910/DVN/L4XKEZ, CC0 1.0, no restricted files.
##File read: "Conjoint Experiment Data.tab", downloaded in its original format (a Stata .dta
##two-wave Qualtrics export, one row per respondent, no value labels). Read as text:
##"Read Me.txt" and the authors' two Stata analysis files, "Data Analysis - Conjoint Experiment
##(Figure 4 and Online Appendix A).do" (the trait layout and every covariate mapping used here)
##and "Data Analysis - Conjoint Experiment (Fully Stacked Data).do".
##Usage: Rscript leeper_2020.R <dir holding the .dta> <output dir>
##
##US respondents recruited in wave 1 (2016, after the presidential election: the authors compute
##age as 2016 - birth year) and shown the conjoint in wave 2. Of the 1,027 wave-1 respondents,
##735 have conjoint data; each saw 5 tasks of two hypothetical congressional candidates
##(7,350 profiles). Tasks whose choice is missing (-99 or blank, 34-43 per task as the authors'
##do file notes) are dropped, since the choice was forced; their thermometer ratings go with
##them. 191 of the 3,675 tasks go, and with them 10 respondents who answered no task's choice,
##leaving 725 respondents, 3,484 tasks and 6,968 rows.
##
##Design. The 13 attributes of each candidate ship as one pipe-delimited string per profile
##(traits<task><a|b>), in the order the authors document (do file lines 613-618): age, gender,
##race, religion, occupation, party, military service, education, then the candidate's position
##on the Trans-Pacific Partnership, intervention against ISIS, cap and trade, higher taxes on
##the rich, and a pathway to citizenship. The strings hold the DISPLAYED TEXT, so no code
##mapping is needed. Every task pairs one Democrat with one Republican (party is exactly 3,675
##/ 3,675 over the 7,350 profiles) and candidate gender is near-even (Female 3,658, Male 3,692).
##Level shares are unequal for race (White 0.61, African American and Hispanic 0.15 each, Asian
##American 0.09) and religion (Evangelical protestant, Catholic, Mainline protestant and None
##about 0.20 each, Muslim 0.10, Jewish 0.09); age, occupation, party, military service,
##education and the five issue positions are near-uniform. Nothing in the deposit documents
##restrictions or level probabilities, and attribute order is not recorded.
##
##Outcomes, both about the same tasks, so one table:
##  choice: which of the two candidates the respondent chose (profile<task> = 1 or 2; forced).
##  rating_thermometer: a 0-100 feeling thermometer for each candidate (therm<task>_1 for
##    candidate A, therm<task>_2 for candidate B; three of these columns ship as strings with
##    the text "NA", which is read as missing, as the authors' do file does).
##Neither wording survives in the deposit (no survey instrument, no codebook), so the questions
##are recorded as paraphrases from the variable names and the authors' do file.
##
##trial_importance_arm: the wave-1 issue-importance manipulation the authors read off the block
##randomizer (dobrfl_23: "TPP (k)" = baseline, "TPP Low Imp (k)" = low importance, "TPP High Imp
##(k)" = high importance; matched on "Low Imp" / "High Imp" because the strings in the data
##carry inconsistent spacing). It is NA for 7 respondents whose block randomizer is blank.
##trial_time_sec is the seconds on the task (tprof<task>_3).
##
##Covariates, all mapped from the label definitions in the authors' do file (the .dta carries no
##value labels): cov_gender (sex 1 = male, 2 = female), cov_birth_year (the `birth` string, with
##the authors' two repairs: the entry "very good" and "." are missing), cov_education,
##cov_income, cov_race, cov_hispanic, cov_religion, cov_occupation_status, cov_ideology,
##cov_political_interest (interest1 is stored reversed, as the authors' recode shows: 1 =
##Extremely Interested), cov_party_id (the wave-1 question: Republican / Democrat / Independent /
##No Preference), cov_party_id7 (the authors' 7-point build from party + strength + lean),
##cov_voted and cov_vote_choice (2016 vote). "-99" is missing throughout.
##NOT carried: the respondents' own issue positions and importance ratings. Each was asked in
##one of four randomized wordings (path1-path4 and so on) whose scale direction differs, and
##recovering a single column needs the authors' reversal; they are left to the deposit.
##PII / identifiers dropped: the Qualtrics responseid (re-keyed 1..n in file order), the
##free-text race / religion / occupation / vote-choice "other" answers, timestamps and the
##panel ids (psid). No survey weight ships with the deposit.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "Conjoint Experiment Data.dta")))
stopifnot(nrow(s) == 1027L, uniqueN(s$responseid) == 1027L)

TRAITS <- c("age", "gender", "race", "religion", "occupation", "party", "military",
            "education", "tpp", "isis", "captrade", "taxes", "path")
num <- function(x) suppressWarnings(as.numeric(ifelse(as.character(x) %in% c("NA", "", "."), NA, as.character(x))))

rows <- rbindlist(lapply(1:5, function(k) rbindlist(lapply(1:2, function(p) {
  tr <- as.character(s[[paste0("traits", k, c("a", "b")[p])]])
  parts <- tstrsplit(tr, "|", fixed = TRUE)
  stopifnot(length(parts) == 13L)
  d <- as.data.table(setNames(lapply(parts, function(x) trimws(as.character(x))), paste0("attr_", TRAITS)))
  d[, `:=`(responseid = s$responseid, task = k, profile = p,
           chosen = num(s[[paste0("profile", k)]]),
           rating_thermometer = num(s[[paste0("therm", k, "_", p)]]),
           trial_time_sec = num(s[[paste0("tprof", k, "_3")]]),
           traits_raw = tr)]
}))))
rows <- rows[!is.na(traits_raw) & traits_raw != ""]
stopifnot(nrow(rows) == 7350L, uniqueN(rows$responseid) == 735L)

## forced choice: 1 = candidate A, 2 = candidate B; drop tasks with no valid choice
rows[, choice := as.integer(chosen == profile)]
rows[!chosen %in% c(1, 2), choice := NA_integer_]
rows[, keep := sum(!is.na(choice)) == 2L, .(responseid, task)]
rows <- rows[keep == TRUE]
stopifnot(rows[, .N, .(responseid, task)][, all(N == 2L)],
          rows[, sum(choice), .(responseid, task)][, all(V1 == 1L)])

LAB <- list(
  gender = c("1" = "male", "2" = "female"),
  education = c("1" = "<HS", "2" = "HS Grad", "3" = "Some College, No Degree", "4" = "Associate",
                "5" = "Bachelor's", "6" = "Master's", "7" = "Doctoral", "8" = "Professional"),
  income = c("1" = "<10,000", "2" = "10,000-19,999", "3" = "20,000-29,999", "4" = "30,000-39,999",
             "5" = "40,000-49,999", "6" = "50,000-59,999", "7" = "60,000-69,999",
             "8" = "70,000-79,999", "9" = "80,000-89,999", "10" = "90,000-99,9999",
             "11" = "100,000-149,999", "12" = "150,000+"),
  race = c("1" = "White", "2" = "Black", "3" = "Amer. Indian/Alaska Native", "4" = "Asian",
           "5" = "Native Hawaiian/Pacific Islander", "6" = "Other"),
  hispanic = c("1" = "Hispanic", "2" = "Non-Hispanic"),
  religion = c("1" = "Protestant", "2" = "Roman Catholic", "3" = "Mormon", "4" = "Orthodox",
               "5" = "Jewish", "6" = "Muslim", "7" = "Buddhist", "8" = "Hindu", "9" = "Atheist",
               "10" = "Agnostic", "11" = "Something Else", "12" = "Nothing in Particular"),
  occupation = c("1" = "Working (paid employee)", "2" = "Working (self-employed)",
                 "3" = "Not Working (temp laid off)", "4" = "Not Working (looking for work)",
                 "5" = "Not working (retired)", "6" = "Not working (disabled)",
                 "7" = "Not Working (other)", "8" = "Prefer Not to Answer"),
  ideology = c("1" = "Ext. Liberal", "2" = "Moderately Liberal", "3" = "Slightly Liberal",
               "4" = "Moderate", "5" = "Slightly Conservative", "6" = "Moderately Conservative",
               "7" = "Extremely Conservative"),
  party = c("1" = "Republican", "2" = "Democrat", "3" = "Independent", "5" = "No Preference"),
  interest = c("5" = "Not Interested at All", "4" = "Slightly Interested",
               "3" = "Moderately Interested", "2" = "Very Interested", "1" = "Extremely Interested"),
  voted = c("1" = "Voted", "2" = "Did Not Vote"),
  votechoice = c("1" = "Donald Trump", "2" = "Hillary Clinton", "3" = "Evan McMullin",
                 "4" = "Jill Stein", "5" = "Gary Johnson", "6" = "Other"))
code <- function(v, key) { x <- as.character(num(s[[v]])); unname(LAB[[key]][x]) }

## the authors' 7-point party identification (do file lines 301-310)
p1 <- num(s$party); p1 <- fifelse(p1 >= 3 & p1 <= 5, 3, p1)
pid <- rep(NA_character_, nrow(s))
pid[p1 == 2 & num(s$dem_strong) == 1] <- "Strong Dem"
pid[p1 == 2 & num(s$dem_strong) == 2] <- "Not Strong Dem"
pid[p1 == 3 & num(s$lean) == 2] <- "Lean Dem"
pid[p1 == 3 & num(s$lean) == 3] <- "Ind./No Pref"
pid[p1 == 3 & num(s$lean) == 1] <- "Lean Rep"
pid[p1 == 1 & num(s$repstrong) == 2] <- "Not Strong Rep"
pid[p1 == 1 & num(s$repstrong) == 1] <- "Strong Rep"

byr <- as.character(s$birth); byr[byr %in% c("very good", ".", "-99", "")] <- NA
cov <- data.table(responseid = s$responseid,
                  cov_gender = code("sex", "gender"),
                  cov_birth_year = suppressWarnings(as.integer(byr)),
                  cov_education = code("education", "education"),
                  cov_income = code("income", "income"),
                  cov_race = code("race", "race"),
                  cov_hispanic = code("hispanic", "hispanic"),
                  cov_religion = code("religion", "religion"),
                  cov_occupation_status = code("occupation", "occupation"),
                  cov_ideology = code("ideology_1", "ideology"),
                  cov_political_interest = code("interest1", "interest"),
                  cov_party_id = code("party", "party"),
                  cov_party_id7 = pid,
                  cov_voted = code("vote", "voted"),
                  cov_vote_choice = code("votechoice", "votechoice"),
                  arm = fcase(grepl("Low Imp", s$dobrfl_23), "low importance",
                              grepl("High Imp", s$dobrfl_23), "high importance",
                              grepl("TPP", s$dobrfl_23), "baseline"))
d <- merge(rows, cov, by = "responseid", all.x = TRUE, sort = FALSE)
d[, id := as.integer(frank(responseid, ties.method = "dense"))]
setnames(d, "arm", "trial_importance_arm")
d[, c("responseid", "chosen", "keep", "traits_raw") := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating_thermometer", paste0("attr_", TRAITS),
                 "trial_importance_arm", "trial_time_sec"))
stopifnot(d[, all(attr_party %in% c("Democrat", "Republican"))],
          d[, uniqueN(attr_party), .(id, task)][, all(V1 == 2L)],
          d[, all(attr_gender %in% c("Female", "Male"))],
          !anyNA(d[, grep("^attr_", names(d)), with = FALSE]),
          d[, all(rating_thermometer >= 0 & rating_thermometer <= 100, na.rm = TRUE)],
          d[, all(trial_importance_arm %in% c("baseline", "low importance", "high importance") |
                  is.na(trial_importance_arm))],
          d[, uniqueN(id)] >= 700L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "leeper_2020_issue_importance.csv"))
