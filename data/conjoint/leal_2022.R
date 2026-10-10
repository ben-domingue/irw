##Cyberattack-attribution conjoint (US, MTurk) from
##Leal, M., & Musgrave, P. (2022). Cheerleading in cyberspace: How the American public
##judges attribution claims for cyberattacks. Foreign Policy Analysis, 18(2), orac003.
##https://doi.org/10.1093/fpa/orac003
##Replication data: Harvard Dataverse doi:10.7910/DVN/MVDDKX, CC0 1.0, no restricted files.
##Files read: TheCyber2019AnalysisData.dta (original-format download of
##TheCyber2019AnalysisData.tab; the authors' cleaned long file: outcomes, caseid, task, choice)
##and TheCyber2019MergedDataNoHeadersAnonymized.csv (the raw anonymized wave 1 + wave 2 export:
##attribute text as displayed, covariate answer text). Question wording and grid layout from
##"Wave 2 Questionnaire.docx" (Qualtrics export, "2019 04 08 The Cyber Conjoint Study
##Revised"); covariate wording from "Wave 1 Questionnaire.docx"; sample rules from the
##authors' "Conjoint Data Cleaning.do" (read as text, not run).
##Usage: Rscript leal_2022.R <raw dir> <output dir>
##
##1,233 MTurk respondents (US citizens) who had completed a wave-1 threat survey and came back
##for wave 2 (spring 2019). Each saw 5 tasks ("Scenario Pair A".."E"), each a side-by-side grid of
##two hypothetical network intrusions (Scenario 1 = profile 1, Scenario 2 = profile 2). Grid rows,
##in this fixed order: "What was attacked?" (attr_target), "What were the economic damages?"
##(attr_economic_damage), "Did anyone die?" (attr_deaths), "Who does the intelligence community
##think carried out the attack?" shown as "<type> from <origin>" (attr_perpetrator_type,
##attr_perpetrator_origin), "What does the intelligence community think was the purpose of the
##attack?" (attr_purpose), "How confident is the intelligence community in their evaluation?"
##(attr_intel_confidence), "Do independent computer security experts agree with the intelligence
##community's evaluation?" shown as "They <level>" (attr_experts), "What do senior policymakers
##think about the intelligence community's evaluation?" shown as "<policymaker> <reaction>"
##(attr_policymaker, attr_policymaker_reaction). Levels are the raw export's F-<task>-<profile>-<k>
##fields, as displayed (the authors' Stata labels shorten two; not used).
##Outcomes, all ratings of each profile (ONE table: all are asked about the same pairs):
##  rating_confidence: "On a scale of 0 to 100, where 0 indicates no confidence and 100 indicates
##     complete confidence, how confident are you in the intelligence community's assessment of
##     who was responsible for each attack?" slider per scenario, 0 = Not confident, 100 =
##     Complete confidence.
##  rating_severity: "On a scale of 0 to 100, where 0 indicates "not severe" and 100 indicates
##     "very severe", how would you rate the severity of each event?" 0..100.
##  rating_support_<measure>: "For scenario 1 [2] only: Would you approve of each of the following
##     measures against those the intelligence community believes to be the perpetrators? You may
##     support any, all, or none of these responses." Would support / Would not support, stored
##     1 / 0 (the authors' coding) for: diplomatic ("Condemn through diplomatic channels"),
##     sanctions ("Apply economic sanctions"), cyberespionage ("Intensify cyberespionage"),
##     cyberattacks ("Conduct cyberattacks"), airstrikes ("Conduct airstrikes"), do_nothing ("Do
##     nothing"). Asked only when the origin is NOT "the United States" (display logic).
##     When the origin IS "the United States" the question is instead "...Would you approve of
##     each of the following sentences for those believed to be the perpetrators?":
##     community_service ("Community service"), fine ("A large monetary fine"), prison ("A short
##     prison term"), life_sentence ("A life sentence"), death_penalty ("The death penalty"),
##     no_punishment ("No punishment"). So each support column is NA by design on the other kind
##     of profile (and NA where an item was skipped).
##  No choice between the two scenarios was asked; there is no choice column.
##Restrictions: none is documented, but some type x origin pairs never occur (observed): "A group
##of terrorists" only from Iran, Russia or the United States; "A government agency" never from
##the United States. Other attributes look independent and roughly uniform (target, damages,
##deaths shares are visibly unequal, e.g. economic "Minimal" 1,795 vs "Billions" 4,057 raw
##profiles; level_weights observed).
##Sample: the authors' cleaning is reproduced to recover their caseid: drop respondents whose
##wave-1 and wave-2 education differ, whose birth years differ, or whose gender differs (Stata
##missing-value semantics kept), number the remaining rows (caseid = row), keep the caseids in the
##authors' analysis file (which also dropped 12 who gave identical support answers on every task,
##and wave-1-only respondents). The link is verified: every attribute level of every profile in
##the raw export matches the authors' coded level in the analysis file (stopifnot below).
##Covariates (wave-1 answer text from the raw export, wave 1 questionnaire): cov_birth_year (Q4
##"In what year were you born?"; the authors' age = 2019 - this); cov_gender (Q5 Male/Female/
##"Other (please specify)" -> male/female/other; the free-text specification is dropped);
##cov_education (Q9 text); cov_race (Q11, multiple choice, comma-joined text); cov_hispanic (Q13
##Yes/No); cov_party_id (Q15 "Generally speaking, do you usually think of yourself as a
##Republican, Democrat, Independent, or what?" Republican/Democrat/Independent/Other);
##cov_party_strength (Q17/Q19 Strong/Not very strong); cov_party_lean (Q21 Republican/
##Democratic); cov_ideology (Q23, 7 points + Don't know, text); cov_ideology_forced (Q25
##Liberal/Conservative); cov_therm_<country> (Q35 feeling thermometer 0-100: usa, russia, uk,
##china, india, france, north_korea, germany, japan, iran, israel, south_korea, vietnam, canada,
##brazil); cov_threat_<item> (Q27 text: Critical threat / Important, but not critical / Not
##important: nk_nuclear, cyber, terrorism, iran_nuclear, china_military, financial_crisis,
##islamic_fundamentalism, russia, epidemics, immigrants, china_disputes, climate);
##cov_cyber_foreign (Q28), cov_cyber_us (Q29), cov_cyber_worried (Q30), cov_cyber_prepared (Q31),
##all as answer text; cov_duration_sec = wave-2 survey duration in seconds. Empty answers are NA.
##Dropped: dates, MTurk completion codes (random survey codes, not worker IDs), consent, the
##gender/race free text, wave-1 Q32-Q36 (responsibility, attack likelihood, country cyber-threat
##items), the wave-2 introductory single-vignette questions (Q3.x, one fixed example), wave-2
##repeated demographics, and all derived variables (dummies, warmth/threat matches, unified DVs).
##No survey weight. No attention item beyond the authors' straight-lining rule. No repeated task.
##The deposit's CCES 2018 module experiment (CCES18_UMB_STATA13Trimmed) is a one-factor survey
##experiment, not a conjoint; not built.
##N: 1,233 respondents x 5 tasks x 2 profiles = 12,330 rows, as in the analysis file.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "TheCyber2019AnalysisData.dta")))
m <- fread(file.path(raw, "TheCyber2019MergedDataNoHeadersAnonymized.csv"), colClasses = "character", na.strings = NULL)
num <- function(x) suppressWarnings(as.numeric(x))
neq <- function(x, y) fifelse(is.na(x) & is.na(y), FALSE, fifelse(is.na(x) | is.na(y), TRUE, x != y))  # Stata `!=` with missing
fem <- function(x) fifelse(x == "Female", 1, fifelse(x == "Male", 0, NA_real_))
m <- m[!(m$wave2q22 != "" & m$wave1q9 != m$wave2q22)]
m <- m[!(neq((2019 - num(m$wave2q21)) - (2019 - num(m$wave1q4)), 0) & !is.na(num(m$wave2q21)))]
m <- m[!(neq(fem(m$wave2q23), fem(m$wave1q5)) & !is.na(fem(m$wave2q23)))]
m[, caseid := .I]
m <- m[caseid %in% k$caseid]
stopifnot(nrow(m) == uniqueN(k$caseid), nrow(k) == nrow(m) * 10)
# raw attribute text, long by task x profile
fld <- c("target", "economic_damage", "deaths", "intel_confidence", "perpetrator_type", "perpetrator_origin", "purpose",
         "experts", "policymaker", "policymaker_reaction")
L <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(caseid = m$caseid, task = t, choice = p)
  for (j in seq_along(fld)) x[, paste0("attr_", fld[j]) := m[[paste0("f", t, p, j)]]]
  x }))))
d <- merge(k, L, by = c("caseid", "task", "choice"))
stopifnot(nrow(d) == nrow(k))
# verify the link: the raw text equals the authors' coded level on every profile
chk <- list(target = c("Large U.S. corporations", "The U.S. banking and financial system", "Hospitals across the United States",
                       "The U.S. power grid", "The U.S. military's computer networks"),
            economic = c("Minimal", "A few million dollars", "Tens of millions of dollars", "Billions of dollars"),
            death = c("No", "One person", "Dozens of people", "Hundreds of people"),
            confidence = c("Somewhat certain", "Highly confident but not certain", "Unanimously confident"),
            aggressortype = c("An individual", "A group of civilian hackers", "A group of terrorists", "A government agency"),
            aggressororigin = c("Israel", "Iran", "North Korea", "Russia", "China", "the United States"),
            purpose = c("No clear motivation", "Stealing sensitive information", "Retaliating for specific U.S. policies",
                        "Disrupting American society generally"),
            indconcur = c("mostly reject it", "have mixed views about it", "mostly agree with it"),
            policymakertype = c("Secretary of Defense Shanahan", "President Trump"),
            policymakerconcur = c("disputed it", "refused to comment", "endorsed it"))
for (j in seq_along(chk)) stopifnot(all(chk[[j]][as.integer(d[[names(chk)[j]]]) + 1L] == d[[paste0("attr_", fld[j])]]))
o <- data.table(id = as.integer(d$caseid), task = as.integer(d$task), profile = as.integer(d$choice),
                rating_confidence = as.numeric(d$confident), rating_severity = as.numeric(d$severe))
sup <- c(diplomatic = "diplomatic", sanctions = "sanctions", cyberespionage = "cyberespionage", cyberattacks = "cyberattack",
         airstrikes = "airstrikes", do_nothing = "intnothing", community_service = "communitysvc", fine = "fine", prison = "prison",
         life_sentence = "lifesentence", death_penalty = "deathpenalty", no_punishment = "domnothing")
for (s in names(sup)) o[, paste0("rating_support_", s) := as.integer(d[[sup[[s]]]])]
for (f in fld) o[, paste0("attr_", f) := d[[paste0("attr_", f)]]]
# display logic: international measures only for foreign origins, sentences only for US origin
us <- o$attr_perpetrator_origin == "the United States"
stopifnot(all(is.na(as.matrix(o[us, paste0("rating_support_", names(sup)[1:6]), with = FALSE]))),
          all(is.na(as.matrix(o[!us, paste0("rating_support_", names(sup)[7:12]), with = FALSE]))))
# covariates
na <- function(x) fifelse(x == "", NA_character_, x)
r <- m[match(d$caseid, m$caseid)]
stopifnot(all(r$wave1q5 %in% c("Male", "Female", "Other (please specify)", "")))
o[, `:=`(cov_birth_year = as.integer(num(r$wave1q4)),
         cov_gender = c(Male = "male", Female = "female", "Other (please specify)" = "other")[r$wave1q5],
         cov_education = na(r$wave1q9), cov_race = na(r$wave1q11), cov_hispanic = na(r$wave1q13),
         cov_party_id = na(r$wave1q15), cov_party_strength = na(fifelse(r$wave1q17 != "", r$wave1q17, r$wave1q19)),
         cov_party_lean = na(r$wave1q21), cov_ideology = na(r$wave1q23), cov_ideology_forced = na(r$wave1q25))]
th <- c("usa", "russia", "uk", "china", "india", "france", "north_korea", "germany", "japan", "iran", "israel", "south_korea",
        "vietnam", "canada", "brazil")
for (i in seq_along(th)) o[, paste0("cov_therm_", th[i]) := num(r[[paste0("wave1q35_", i)]])]
tr <- c("nk_nuclear", "cyber", "terrorism", "iran_nuclear", "china_military", "financial_crisis", "islamic_fundamentalism",
        "russia", "epidemics", "immigrants", "china_disputes", "climate")
for (i in seq_along(tr)) o[, paste0("cov_threat_", tr[i]) := na(r[[paste0("wave1q27_", i)]])]
o[, `:=`(cov_cyber_foreign = na(r$wave1q28), cov_cyber_us = na(r$wave1q29), cov_cyber_worried = na(r$wave1q30),
         cov_cyber_prepared = na(r$wave1q31), cov_duration_sec = num(r$wave2durationinseconds))]
o[, cov_gender := unname(cov_gender)]
stopifnot(o[, .N, id][, all(N == 10)], all(o$rating_confidence %between% c(0, 100), na.rm = TRUE))
setorder(o, id, task, profile)
fwrite(o, file.path(out, "leal_2022_cyber_attribution.csv"))
