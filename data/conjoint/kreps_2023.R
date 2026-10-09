##AI-enabled technology single-profile conjoint (US) from
##Kreps, S., George, J., Lushenko, P., & Rao, A. (2023). Exploring the artificial intelligence
##"Trust paradox": Evidence from a survey experiment in the United States. PLOS ONE, 18(7),
##e0288109. https://doi.org/10.1371/journal.pone.0288109
##Replication data: Harvard Dataverse doi:10.7910/DVN/EOYDJR, CC0 1.0, no restricted files.
##File read: "MasterData2 (2).tab" as its original Qualtrics CSV export (read here as
##MasterData2.csv; row 1 = column names, row 2 = question text, row 3 = ImportIds, then
##respondents). Read as text, not run: AITrustConjoint_Final_ReplicationKit.Rmd. Design facts
##and the rating scale from the article (Table 1 and "Methods").
##Usage: Rscript kreps_2023.R <raw dir holding MasterData2.csv> <output dir>
##
##1,008 Lucid respondents (October 7-21, 2022; all Finished = 1, all aged 18+), each shown 5
##hypothetical AI applications one at a time (task 1-5, profile 1), 4 attributes, levels as
##exported by Qualtrics (F-<task>-1-<k>): domain (cars, armed drones, general surgery, social
##media content moderation, police surveillance), autonomy, precision, regulation. The article
##says respondents saw "four randomly assigned choice sets"; the export and the authors' Rmd
##have five per respondent, and all five are kept. Attribute row order was the same in every
##task (F-t-1..4 always domain, autonomy, precision, regulation). Randomization restrictions
##not documented (article: 135 = 5x3x3x3 unique scenarios, i.e. all combinations allowed).
##Outcomes, asked after each profile, 5-point Likert, "1 corresponds to 'strongly disagree'
##and 5 to 'strongly agree'" (article), stored raw:
##  rating_support (conjoint_dv_<t>_1): "Do you support the use of AI under these circumstances?"
##  rating_trust   (conjoint_dv_<t>_2): "Do you trust the use of AI under these circumstances?"
##Covariates: cov_age (Lucid `age`, years; the Rmd's age variable), cov_gender_code (Q1 "What
##is your sex?" codes 1/2/3; the Rmd maps only 1 = "Male" and both 2 and 3 to "Female/Other",
##so the codes are kept), cov_education (Q4, the Rmd's text: l.t. HS, High School / GED, Some
##College, 2-year College Degree, 4-year College Degree, Post-Baccalaureate Degree +), cov_race
##(Q3, Rmd text), cov_income (Q19, Rmd text), cov_ideology_code (Q21 "Generally speaking, do you
##think of yourself as...?", codes 1-8; Rmd: 1 Extremely Liberal .. 7 Extremely Conservative,
##and both 4 and 8 "Moderate/Unsure"), cov_party_id_code (Q20 "Generally speaking, do you
##usually think of yourself as a...?", codes 1-5, no labels in the deposit), cov_duration_sec
##(whole survey).
##Dropped: Qualtrics ResponseId and Lucid rid (platform IDs; id re-keyed 1..N in file order),
##ZIP code (zip) and state (Q24), masked IP/name/email/lat-long columns (all "*******"), Lucid
##profile codes (hhi, ethnicity, hispanic, education, political_party, region; unlabelled),
##religion and military items (Q22, Q23; unlabelled), the consent and "read carefully"
##commitment items, and the second experiment that followed the conjoint (Respondent Group
##scenario arm, Q6-Q18 incl. free text Q10/Q11), which is a separate single-factor design.
##No survey weight in the deposit.
##N: the article reports no conjoint N beyond "over 5,000 observations"; 1,008 x 5 = 5,040.
##Spot check: OLS of rating_support on the attributes alone (refs cars, no autonomy, 85%,
##community users) gives full autonomy -0.128, police surveillance 0.150, 99% precision 0.386
##(article Table 2, with demographic controls: -0.132, 0.155, 0.394); rating_trust -0.114,
##0.113, 0.366 (article -0.117, 0.117, 0.374). Close, not exact (controls not added here).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "MasterData2.csv"), colClasses = "character", header = TRUE)[-(1:2)]
stopifnot(nrow(s) == 1008, all(s$Finished == "1"), all(s$IPAddress == "*******"))
s[, id := seq_len(.N)]
nm <- c("domain", "autonomy", "precision", "regulation")
d <- rbindlist(lapply(1:5, function(t) {
  for (k in 1:4) stopifnot(all(s[[sprintf("F-%d-%d", t, k)]] == nm[k]))
  x <- data.table(id = s$id, task = t, profile = 1L,
                  rating_support = as.integer(s[[sprintf("conjoint_dv_%d_1", t)]]),
                  rating_trust = as.integer(s[[sprintf("conjoint_dv_%d_2", t)]]))
  for (k in 1:4) x[, paste0("attr_", nm[k]) := s[[sprintf("F-%d-1-%d", t, k)]]]
  x
}))
stopifnot(all(d$rating_support %in% 1:5), all(d$rating_trust %in% 1:5), !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
stopifnot(all(unlist(d[, lapply(.SD, function(x) all(x != "")), .SDcols = patterns("^attr_")])))
map <- function(x, l) { x <- as.integer(x); stopifnot(all(x %in% seq_along(l))); l[x] }
cv <- s[, .(id, cov_age = as.integer(age), cov_gender_code = as.integer(Q1),
            cov_education = map(Q4, c("l.t. HS", "High School / GED", "Some College", "2-year College Degree",
                                      "4-year College Degree", "Post-Baccalaureate Degree +")),
            cov_race = map(Q3, c("American Indian and Alaskan Native", "Asian", "Black", "Hispanic/Latino",
                                 "Native Hawaiian and Other Pacific Islander", "White, Non-Hispanic")),
            cov_income = map(Q19, c("l.t. 10,000", "10,000 to 24,999", "25,000 to 49,999", "50,000 to 74,999",
                                    "75,000 to 99,999", "100,000+")),
            cov_ideology_code = as.integer(Q21), cov_party_id_code = as.integer(Q20),
            cov_duration_sec = as.integer(`Duration (in seconds)`))]
stopifnot(all(cv$cov_gender_code %in% 1:3), all(cv$cov_ideology_code %in% 1:8), all(cv$cov_party_id_code %in% 1:5))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kreps_2023_ai_trust.csv"))
