##Democratic-principles candidate conjoint (US donors and public) from
##Carey, J., Clayton, K., Helmke, G., Nyhan, B., Sanders, M., & Stokes, S. (2020). Who will
##defend democracy? Evaluating tradeoffs in candidate support among partisan donors and voters.
##Journal of Elections, Public Opinion and Parties. https://doi.org/10.1080/17457289.2020.1790577
##Replication data: Harvard Dataverse doi:10.7910/DVN/MRWYC2, CC0 1.0. Files read:
##BLW_Wave_8_Conjoint__Donors.csv (Qualtrics export), MICH0038_B_output.dta and
##MICH0033_B_output.sav (YouGov; "original format" downloads), candidate_names.xlsx (authors'
##name -> race/gender groups). BLW_Wave_8_Conjoint_-_Donors.docx (questionnaire),
##MICH0033_B_codebook.pdf, MICH0038_B_codebook.pdf, _README.md and scripts 01, 02, 09 were read
##as text (not run). The article was not read.
##Usage: Rscript carey_2020_democracy.R <raw dir> <output dir>
##
##One attribute set, three separate samples/fieldings -> three tables (the paper contrasts
##donors with the public; the October 2018 public sample is an appendix replication):
##  carey_2020_democracy_donors     Bright Line Watch wave 8 donor sample, Qualtrics, 28 Feb - 17 Apr 2019 (start dates)
##  carey_2020_democracy_public     YouGov MICH0038 "Bright Line Watch 6 - Conjoint", 12-18 Mar 2019
##  carey_2020_democracy_public_oct YouGov MICH0033 "Bright Line Watch 5 - Conjoint", 24-31 Oct 2018
##Each respondent saw 10 pairs of hypothetical candidates ("Suppose the two individuals below are
##candidates in an upcoming election", Candidate 1 / Candidate 2 columns, donors questionnaire),
##8 attributes: name (signals race and gender: names from Butler & Homola 2017; the authors'
##candidate_names.xlsx groups them as Black/Latino/White x female/male), party (Democrat/
##Republican), and six platform statements, each with two levels, stored as displayed, e.g.
##elections "Supports/Opposes new legislation to require voters to show state-issued ID at the
##polls.", investigations, compromise, courts, discrimination, taxes ("Platform: Limited
##government" in the donor export). Race is not stored as an attribute because it was shown
##only through the name; the YouGov cand<k>_race design variable is dropped.
##Outcome choice: donors Q3.4, Q3.7, ..., Q3.31 "Based on the information above, which of the
##following two candidates would you be more likely to support?" Candidate 1 / Candidate 2.
##YouGov conjoint1..10 "Conjoint screen <k> candidate choice" (Candidate 1 / Candidate 2; the
##question wording is not in the YouGov codebooks; presumably the same item). No opt-out;
##unanswered screens are omitted.
##Attribute order: donors, name and party are rows 1-2 (F-<t>-1/2, fixed) and the six platform
##rows (K-<t>-<k>) are in an order randomized once per respondent (identical in all 10 tasks,
##checked): attrpos_* = 2 + k for the platform attributes. YouGov files do not record order.
##Restrictions and level weights are not documented. Three donor respondents answered
##screens whose attribute levels were not saved (blank F-/K- fields; the authors drop them as
##"odd observations", 01_read_data_donors.R): dropped entirely.
##Samples: the authors drop respondents who did not consent, live outside the US, are under
##18 (donors) or answer surveys insincerely "most of the time"/"always" (take_serious /
##Q10.3 = 4, 5). Here non-consenters and under-18s (donors) are dropped; the others are kept
##with cov_state / cov_take_serious so the authors' sample can be rebuilt.
##Covariates, donors (Qualtrics codes mapped with the questionnaire docx): cov_age_group (Q2.1),
##cov_gender (Q4.4 1 Male, 2 Female, 3 Other), cov_ideology (Q4.5), cov_party_id (Q4.6
##Republican/Democrat/Independent/Something else), cov_education (Q8.2), cov_race (Q8.5),
##cov_hispanic (Q8.4), cov_trump_approval (Q8.7), cov_take_serious (Q10.3), cov_us_resident
##(Q4.3 < 52, i.e. one of the 50 states or DC: 1/0), cov_finished, cov_duration_sec
##(Q_TotalDuration). YouGov (value-label text; "skipped"/"not asked" -> NA): cov_survey_weight
##(weight), cov_age, cov_gender, cov_education (educ7), cov_party_id (pid3), cov_party_id7
##(pid7), cov_ideology (ideo7), cov_state (inputstate), cov_trump_approval (approve_trmp),
##cov_political_interest (polinterest), cov_take_serious.
##Dropped: Qualtrics ResponseID and YouGov caseid (re-keyed 1..N in file order), dates, page
##timers, free-text comments (Q10.5 / comments, race_other, pid3_t), knowledge items, birthyr,
##religion and other YouGov profile items.
library(data.table); library(haven); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
plat <- c("Platform: Elections" = "elections", "Platform: Investigations" = "investigations",
          "Platform: Compromise" = "compromise", "Platform: Courts" = "courts",
          "Platform: Discrimination" = "discrimination", "Platform: Limited government" = "taxes")
## ---- donors
q <- fread(file.path(raw, "BLW_Wave_8_Conjoint__Donors.csv"), colClasses = "character", encoding = "UTF-8", header = TRUE)
q <- q[-1]                                    # second header row (question text)
stopifnot(nrow(q) == 649, uniqueN(q$V1) == 649)
q <- q[Q1.1 == "1" & Q2.1 != "1"]             # consent; not under 18
q[, rid := seq_len(.N)]
rows <- list()
for (t in 1:10) for (p in 1:2) {
  x <- data.table(id = q$rid, task = t, profile = p,
                  attr_name = trimws(q[[sprintf("F-%d-%d-1", t, p)]]), attr_party = trimws(q[[sprintf("F-%d-%d-2", t, p)]]))
  stopifnot(all(q[[sprintf("F-%d-1", t)]] %in% c("Name", "")), all(q[[sprintf("F-%d-2", t)]] %in% c("Partisanship", "")))
  for (k in 1:6) {
    nm <- plat[q[[sprintf("K-%d-%d", t, k)]]]
    lv <- trimws(q[[sprintf("K-%d-%d-%d", t, p, k)]])
    for (v in plat) {
      w <- which(nm == v)
      if (!paste0("attr_", v) %in% names(x)) x[, c(paste0("attr_", v), paste0("attrpos_", v)) := list(NA_character_, NA_integer_)]
      set(x, w, paste0("attr_", v), lv[w]); set(x, w, paste0("attrpos_", v), 2L + k)
    }
  }
  ans <- q[[paste0("Q3.", 1 + 3 * t)]]
  x[, choice := fifelse(ans == "", NA_integer_, as.integer(ans == as.character(p)))]
  rows[[length(rows) + 1]] <- x
}
d <- rbindlist(rows)
for (k in 1:6) for (t in 2:10) stopifnot(identical(q[[sprintf("K-1-%d", k)]], q[[sprintf("K-%d-%d", t, k)]]))
d <- d[!is.na(choice)]
bad <- d[attr_name == "" | is.na(attr_elections), unique(id)]
stopifnot(length(bad) == 3)
d <- d[!id %in% bad]
stopifnot(!anyNA(d), all(as.matrix(d[, .SD, .SDcols = patterns("^attr_")]) != ""), d[, sum(choice), .(id, task)][, all(V1 == 1)])
lab <- function(x, l) { x <- suppressWarnings(as.integer(x)); l[x] }
cv <- q[, .(id = rid,
  cov_age_group = lab(Q2.1, c("Under 18", "18 - 24", "25 - 34", "35 - 44", "45 - 54", "55 - 64", "65 - 74", "75 - 84", "85 or older")),
  cov_gender = lab(Q4.4, c("male", "female", "other")),
  cov_ideology = lab(Q4.5, c("Very conservative", "Somewhat conservative", "Slightly conservative", "Moderate; middle of the road",
                             "Slightly liberal", "Somewhat liberal", "Very liberal")),
  cov_party_id = lab(Q4.6, c("Republican", "Democrat", "Independent", "Something else")),
  cov_education = lab(Q8.2, c("Did not graduate from high school", "High school diploma or the equivalent (GED)", "Some college",
                              "Associate’s degree", "Bachelor’s degree", "Master’s degree", "Professional or doctorate degree")),
  cov_race = lab(Q8.5, c("White", "Black or African American", "American Indian or Alaska Native", "Asian/Pacific Islander",
                         "Multi-racial", "Hispanic/Latino/Chicano/a", "Other")),
  cov_hispanic = lab(Q8.4, c("Yes", "No")),
  cov_trump_approval = lab(Q8.7, c("Strongly approve", "Somewhat approve", "Somewhat disapprove", "Strongly disapprove")),
  cov_take_serious = lab(Q10.3, c("Never", "Rarely", "Some of the time", "Most of the time", "Always")),
  cov_us_resident = fifelse(Q4.3 == "", NA_integer_, as.integer(suppressWarnings(as.integer(Q4.3)) < 52)),
  cov_finished = as.integer(V5), cov_duration_sec = suppressWarnings(as.integer(Q_TotalDuration)))]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "carey_2020_democracy_donors.csv"))
## ---- YouGov
yg <- function(y, file) {
  y <- as.data.table(y)
  stopifnot(uniqueN(y$caseid) == nrow(y))
  y <- y[zap_labels(consent) == 1]
  y[, rid := seq_len(.N)]
  tx <- function(v) { v <- as.character(as_factor(v, levels = "labels")); v[v %in% c("skipped", "not asked", "")] <- NA; trimws(v) }
  rows <- list()
  for (t in 1:10) for (p in 1:2) {
    k <- 2 * (t - 1) + p
    g <- function(s) tx(y[[sprintf("cand%d_%s", k, s)]])
    x <- data.table(id = y$rid, task = t, profile = p, attr_name = g("name"), attr_party = g("party"),
                    attr_elections = g("elect"), attr_investigations = g("invest"), attr_compromise = g("comp"),
                    attr_courts = g("courts"), attr_discrimination = g("discrim"), attr_taxes = g("govt"))
    ans <- tx(y[[paste0("conjoint", t)]])
    stopifnot(all(ans %in% c("Candidate 1", "Candidate 2", NA)))
    x[, choice := as.integer(ans == paste("Candidate", p))]
    rows[[length(rows) + 1]] <- x
  }
  d <- rbindlist(rows)[!is.na(choice)]
  stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)])
  cv <- y[, .(id = rid, cov_survey_weight = as.numeric(weight), cov_age = as.integer(age),
              cov_gender = c(Male = "male", Female = "female")[tx(gender)], cov_education = tx(educ7),
              cov_party_id = tx(pid3), cov_party_id7 = tx(pid7), cov_ideology = tx(ideo7), cov_state = tx(inputstate),
              cov_trump_approval = tx(approve_trmp), cov_political_interest = tx(polinterest), cov_take_serious = tx(take_serious))]
  stopifnot(all(cv$cov_age >= 18 & cv$cov_age <= 99))
  d <- merge(d, cv, by = "id")
  setcolorder(d, c("id", "task", "profile", "choice"))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, file))
}
yg(read_dta(file.path(raw, "MICH0038_B_output.dta")), "carey_2020_democracy_public.csv")
yg(read_sav(file.path(raw, "MICH0033_B_output.sav")), "carey_2020_democracy_public_oct.csv")
