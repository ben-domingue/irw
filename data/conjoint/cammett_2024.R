##Candidate-choice conjoint on clientelism (Lebanon) from
##Cammett, M., Parreira, C., & Atallah, S. (2024). Is clientelism (only) for the poor? Insights on
##class and clientelism from a survey experiment in Lebanon. Journal of Politics.
##https://doi.org/10.1086/732967 (the deposit's replication.R also lists Kruszewska-Eduardo, D.)
##Replication data: Harvard Dataverse doi:10.7910/DVN/QTCNQD, CC0 1.0, no restricted files.
##Files read: data_lebanon.csv (Qualtrics export, one row per respondent); the authors'
##replication.R read as text (not run) for the outcome coding and the English glosses of levels.
##Usage: Rscript cammett_2024.R <raw dir> <output dir>
##
##2,455 respondents (face-to-face tablet survey in Lebanon, fielded Sept-Oct 2017 per the export
##timestamps; enumerator-administered), each saw 4 pairs of parliamentary candidates (Rd_<t>_<A|B>_*
##columns: A = profile 1, B = profile 2), 9 attributes. Level text is the ARABIC text displayed
##(the Qualtrics conjoint columns); label_language ar. English glosses from the authors' recode
##code: gender Woman/Man; political experience None/5 years/15 years; sect Sunni/Shia/Christian;
##relationship with supporters = clientelism (Promises to work hard / Distributes food and cash /
##Arranges medical treatment / Helps family members get jobs / Assists with parking ticket
##cancellations); security speech (Iranian threat / Wahhabi threat / Threat to Christians /
##National security); piety (Rarely / Frequently attends religious services); education (High
##school / University / Post-graduate); party (candidate on the list of your favored party / of a
##party you oppose / of a party you neither support nor oppose); platform (detailed plan for job
##creation / for waste management; discusses waste management / unemployment). The party level is
##relative to the respondent, as displayed.
##Outcome: choice = vote_choice, vote_choice2-4 (1 = candidate A, 2 = B; the authors code
##selected = 1 for the chosen profile). No questionnaire is deposited, so the wording is a
##paraphrase ("which candidate would you vote for"); forced choice, no opt-out (every task has a
##1 or 2). NOT KEPT: rally_<t>_<1|2>, a 1-7 answer per profile whose question, anchors and
##direction are documented nowhere (the article does not analyse it; the authors' code builds an
##inconsistent 0/1 from it). Ben may want it if the instrument turns up.
##trial_prime = the respondent's arm in a priming experiment that came before the conjoint
##(Group/Treat: "none" = Conjoint only, "Activity", "Fear"); the article pools the arms.
##Covariates: cov_sect = the authors' recode of confession (replication.R L28-31: None, Christian,
##Sunni, Shia, Druze, Alawite, Other); cov_sex_code (sex 1/2; no source says which is which),
##cov_age_code (age code 1-45; the authors' code maps code k to birth year 1951+k), cov_household_income_code
##(household_income 5-8) and cov_household_net_income_code (13-21), cov_governorate_code; codes
##kept because no codebook is deposited. cov_duration_sec = Q_TotalDuration (whole survey).
##Dropped: Qualtrics ResponseId (re-keyed), IP address (V6), LocationLatitude/Longitude, surveyor
##and enumerator ids, district and city codes (PII), timers, free text, all other attitude items,
##and the authors' derived variables. No survey weight in the deposit.
##N: 2,455 respondents, 19,640 profile rows; article N not checked (paper not read).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data_lebanon.csv"), na.strings = c("NA", ""))
names(s)[3] <- "ResponseId"
stopifnot(!anyDuplicated(s$ResponseId))
s[, idn := seq_len(.N)]
att <- c(Religion.Sect = "sect", Relationship.with.supporters = "relationship_with_supporters", Security = "security",
         Political.experience = "political_experience", Education = "education", Platform = "platform",
         Piety = "piety", Party = "party", Gender = "gender")
vc <- c("vote_choice", "vote_choice2", "vote_choice3", "vote_choice4")
d <- rbindlist(lapply(1:4, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(id = s$idn, task = t, profile = p, choice = as.integer(s[[vc[t]]] == p))
  for (k in names(att)) x[, paste0("attr_", att[[k]]) := trimws(s[[sprintf("Rd_%d_%s_%s", t, c("A", "B")[p], k)]])]
  x
}))))
stopifnot(all(unlist(s[, ..vc]) %in% 1:2), d[, sum(choice), .(id, task)][, all(V1 == 1)],
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
stopifnot(all(d$attr_gender %in% c("أنثى", "ذكر")))
cov <- data.table(id = s$idn, trial_prime = fifelse(is.na(s$Treat) | trimws(s$Treat) == "", "none", trimws(s$Treat)),
                  cov_sect = c("24" = "None", "25" = "Christian", "26" = "Sunni", "27" = "Shia", "28" = "Druze",
                               "29" = "Christian", "30" = "Christian", "31" = "Christian", "32" = "Christian",
                               "33" = "Christian", "34" = "Christian", "35" = "Christian", "36" = "Alawite",
                               "37" = "Other")[as.character(s$confession)],
                  cov_sex_code = s$sex, cov_age_code = s$age, cov_household_income_code = s$household_income,
                  cov_household_net_income_code = s$household_net_income, cov_governorate_code = s$governorate,
                  cov_duration_sec = as.integer(s$Q_TotalDuration))
stopifnot(all(cov$trial_prime %in% c("none", "Activity", "Fear")), all((cov$trial_prime == "none") == (s$Group == "Conjoint only")))
d <- merge(d, cov, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "cammett_2024_clientelism_lebanon.csv"))
