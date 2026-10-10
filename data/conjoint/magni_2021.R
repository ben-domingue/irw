##LGBT-candidate conjoints in the US, the UK and New Zealand from
##Magni, G., & Reynolds, A. (2021). Voter preferences and the political underrepresentation of
##minority groups: Lesbian, gay, and transgender candidates in advanced democracies. Journal of
##Politics, 83(4), 1199-1215. https://doi.org/10.1086/712142
##Replication data: Harvard Dataverse doi:10.7910/DVN/8VBGXO, CC0 1.0, no restricted files.
##Files read: US-LGBT-Conj.csv, UK-LGBT-Conj.csv, NZ-LGBT-Conj.csv (Dataverse "original format"
##downloads of the .tab files). Level text is in the data; question wording and design from the
##article (author copy, "Experiment design"); the authors' US/UK/NZ-Conj-JOP.R scripts were read
##as text (not run) for the meaning of the columns. No questionnaire is deposited.
##Usage: Rscript magni_2021.R <raw dir> <output dir>
##
##Online samples by Cint, fall 2018, census quotas for gender, age, region and education.
##Respondents were told that the party they were most likely to vote for was considering two
##people as candidates for the lower house in their district and chose between them in five
##pairs (article; the NZ file has SIX pairs for every respondent, kept: task 6 is not a repeat of
##an earlier pair). THREE TABLES, one per country: the authors estimate and report each country
##separately and several attribute level sets differ (race, religion, political experience).
##  magni_2021_lgbt_candidates_us  (1,829 respondents in the file)
##  magni_2021_lgbt_candidates_uk  (1,122)
##  magni_2021_lgbt_candidates_nz  (1,287)
##Eight attributes, levels as stored in the export (CJ-1-REC_1..8): attr_race, attr_sexual_
##orientation, attr_religion, attr_age, attr_health, attr_political_experience, attr_education,
##attr_gender. Attribute row order was randomized per task and is recorded (CJ-1-REC_17, the
##ordered list of attribute names): attrpos_<attribute> = row position 1-8.
##Outcomes:
##  choice: "Which of these two candidates would you be more likely to vote for?" (forced choice,
##     no opt-out; article).
##  rating: a 1-7 rating of each candidate (CJ-1-Rat-1_1). Its wording and anchors are not
##     deposited or reported; stored raw. It correlates positively with being chosen (r = 0.33 to
##     0.39), so higher appears to be more favourable, but this is not documented.
##  NOT KEPT: the mechanism items ("In your opinion, which of these two candidates ... is more
##     liberal [UK/NZ: left-leaning]? ... would you prefer to have as a neighbor? ... has better
##     chances to win the election?", plus two more unreported items, UK "SocProgr" and
##     "ThreatTradit"). They are coded 1/2 (candidate) or 0, and what 0 means (neither, don't
##     know, or not asked) is not documented: 0 occurs on 25-60% of tasks, scattered within
##     respondents. Recoverable from the source if a codebook turns up.
##Task and profile are rebuilt from ROW ORDER: each respondent has 10 (NZ 12) consecutive rows,
##two per task in the order shown; CJ-1-Choice is the candidate chosen in the task (1/2) and
##CJ-1-ChoiceDummy whether this row was chosen, so profile = Choice if chosen, else 3 - Choice
##(verified: every task gets profiles 1 and 2, and both rows of a task share the attribute order
##string). Tasks with no recorded choice cannot be positioned and are dropped (US 64, UK 61,
##NZ 38 tasks). UK respondent 119 tasks 4-5 hold random strings instead of levels (e.g. "Xgprq")
##and are dropped.
##Covariates (answer text as exported; blank = NA): cov_birth_year (YOB), cov_gender (GenderID
##Man/Woman/Other -> male/female/other; the free-text specification is dropped), cov_race
##(multiple choice, comma-joined), cov_education, cov_household_income (bracket text),
##cov_religious (Yes/No), cov_religion (asked of the religious), cov_religiosity, cov_voted,
##cov_vote_choice (vote in the last national election, not party identification),
##cov_sexual_orientation, cov_know_lgbt ("KnowLGBT", Yes/No), cov_job_insecurity; US only:
##cov_party_id (PartyID Democrat/Independent/Republican), cov_ideology (7-point text); UK and NZ:
##cov_ideology_economic and cov_ideology_social (0-10 sliders, PolIdeol-Eco_1 / PolIdeol-Soc_1;
##anchors not documented). Dropped: ResponseId (Qualtrics response IDs), timing and click
##counts, all *_TEXT free-text fields. No survey weight in the deposit.
##Restrictions: none; the article says the eight characteristics were "fully randomized"
##(independently). Level shares are unequal: Straight 2/3 and Healthy 3/7 everywhere; UK White
##1/2 and Not religious 1/2; NZ White 2/3 and Not religious 1/2 (level_weights observed).
##N: respondents = article (US 1,829, UK 1,122, NZ 1,287) before the dropped tasks; the tables
##keep 1,827 / 1,120 / 1,285 (two respondents per country had no recorded choice at all).
##Spot check: OLS of choice on all attribute dummies (straight and man as baselines) gives gay
##-0.067 / -0.046 / -0.033 and transgender -0.110 / -0.107 / -0.085 (US / UK / NZ), the article's
##6.7, 4.6, 3.3 and 11, 10.7, 8.5 point penalties.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
anames <- c("Race" = "race", "Sexual Orientation" = "sexual_orientation", "Religion" = "religion", "Age" = "age",
            "Health" = "health", "Political Experience" = "political_experience", "Education" = "education", "Gender" = "gender")
na <- function(x) { x <- as.character(x); fifelse(is.na(x) | trimws(x) == "", NA_character_, x) }
build <- function(file, ctry) {
  k <- fread(file.path(raw, file), colClasses = list(character = c("CJ-1-REC_4")))
  setnames(k, gsub("[- ]", "_", names(k)))
  k[, src_row := .I]
  k[, r := seq_len(.N), RespNumber]
  ntask <- if (ctry == "nz") 6L else 5L
  stopifnot(k[, .N, RespNumber][, all(N == 2L * ntask)])
  k[, task := as.integer((r + 1L) %/% 2L)]
  k[, profile := fifelse(CJ_1_ChoiceDummy == 1L, CJ_1_Choice, 3L - CJ_1_Choice)]
  k[, keep := !anyNA(CJ_1_Choice) && setequal(profile, 1:2) && uniqueN(CJ_1_REC_17) == 1L &&
              all(CJ_1_REC_8 %in% c("Man", "Woman", "Transgender")) && all(CJ_1_REC_2 %in% c("Gay", "Straight")) &&
              all(CJ_1_REC_17 != "") && all(sapply(strsplit(CJ_1_REC_17, ","), function(z) setequal(z, names(anames)))),
    .(RespNumber, task)]
  cat(ctry, "tasks dropped:", k[keep == FALSE, uniqueN(paste(RespNumber, task))], "\n")
  k <- k[keep == TRUE]
  stopifnot(k[, sum(CJ_1_ChoiceDummy), .(RespNumber, task)][, all(V1 == 1)])
  d <- data.table(id = as.integer(k$RespNumber), task = k$task, profile = as.integer(k$profile),
                  choice = as.integer(k$CJ_1_ChoiceDummy), rating = as.integer(k$CJ_1_Rat_1_1))
  for (j in 1:8) d[, paste0("attr_", anames[[j]]) := as.character(k[[paste0("CJ_1_REC_", j)]])]
  ord <- strsplit(k$CJ_1_REC_17, ",")
  for (n in names(anames)) d[, paste0("attrpos_", anames[[n]]) := vapply(ord, function(z) match(n, z), 1L)]
  stopifnot(all(d$rating %in% c(1:7, NA)))
  g <- na(k$GenderID); stopifnot(all(g %in% c("Man", "Woman", "Other", NA)))
  d[, `:=`(cov_birth_year = as.integer(k$YOB), cov_gender = c(Man = "male", Woman = "female", Other = "other")[g],
           cov_race = na(k$Race), cov_education = na(k$Educ), cov_household_income = na(k$IncomeH),
           cov_religious = na(k$ReligY_N), cov_religion = na(k$ReligID), cov_religiosity = na(k$Religiosity),
           cov_voted = na(k$Vote_Y_N), cov_vote_choice = na(k$VoteChoice), cov_sexual_orientation = na(k$SexOrient),
           cov_know_lgbt = na(k$KnowLGBT), cov_job_insecurity = na(k$JobInsec))]
  d[, cov_gender := unname(cov_gender)]
  if (ctry == "us") d[, `:=`(cov_party_id = na(k$PartyID), cov_ideology = na(k$PolIdeology))]
  else d[, `:=`(cov_ideology_economic = as.integer(k$PolIdeol_Eco_1), cov_ideology_social = as.integer(k$PolIdeol_Soc_1))]
  d <- d[!(is.na(choice) & is.na(rating))]
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("magni_2021_lgbt_candidates_", ctry, ".csv")))
}
build("US-LGBT-Conj.csv", "us")
build("UK-LGBT-Conj.csv", "uk")
build("NZ-LGBT-Conj.csv", "nz")
