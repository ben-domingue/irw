##US Supreme Court nominee conjoint (Sen 2013 survey) as deposited with
##Acharya, A., Blackwell, M., & Sen, M. (2018). Analyzing causal mechanisms in survey experiments.
##Political Analysis, 26(4), 357-378. https://doi.org/10.1017/pan.2018.19
##(the experiment is first reported in Sen, M. (2017). How political signals affect public support
##for judicial nominations: Evidence from a conjoint experiment. Political Research Quarterly,
##70(2), 374-393. https://doi.org/10.1177/1065912917695229)
##Replication data: Harvard Dataverse doi:10.7910/DVN/KHE44F, CC0 1.0, no restricted files, no terms.
##File read: Judicial_Nominations_FINAL.tab (datafile 3123595, ?format=original: a raw Qualtrics
##export whose first data row holds the (truncated) question texts). scotus-replication.R and
##README.md read as text, not run. The deposit's other experiment (tw-replication-dvn.tab, a
##Tomz-Weeks replication) is a separate table, acharya_2018_democratic_peace (acharya_2018_democratic_peace.R).
##Usage: Rscript acharya_2018.R <dir holding Judicial_Nominations_FINAL.csv> <output dir>
##
##December 2013, Survey Sampling International nonprobability online sample matched to US adults
##on age, gender, race and geography (ABS 2018 fn. 6). "We're now going to show you a series of
##profiles of potential candidates to the U.S. Supreme Court." Each respondent rated six single
##nominee profiles ("Suppose the following person was a potential candidate for nomination to the
##U.S. Supreme Court."), one profile per task (profile = 1).
##Two BETWEEN-SUBJECT ARMS, pooled by the authors (scotus-replication.R rbinds them), so ONE table
##with trial_arm: "nonpartisan" (Q10-Q15 rate the Qualtrics conjoint profiles NP-1..NP-6, seven
##attributes) and "partisan" (Q16-Q21 rate P-1..P-6, the same seven plus "Party leaning"). In the
##nonpartisan arm attr_party_leaning = "(not shown)". The authors' code pairs Q10..Q15 with
##NP-1..NP-6 and Q16..Q21 with P-1..P-6; task = that index (block order of the questions).
##Attributes (level text as displayed, from the export): previous work experience, gender, age,
##race or ethnicity, previous judicial clerkship experience, legal education (law school rank),
##religion, party leaning. Attribute ROW ORDER was randomized once per respondent (identical across
##that respondent's six profiles; checked): attrpos_<attribute> = row 1-7 (1-8 partisan arm).
##The Qualtrics generator also stored an "Issue area" field per profile (NP-k-1-Issue) that is
##piped only into later questions Q23/Q24 ("Suppose the following Justice will participate in a
##case involving <issue> ..."), not into the Q10-Q21 profiles; not kept. NOT KEPT: Q23.1-Q24.6
##(trust in the justice in an issue-specific case): answered by respondents of both arms about NP
##and P profiles they had not necessarily rated, the profile display for those questions is not
##documented and the instrument is not deposited; they are not analysed in either paper.
##Outcomes (5-point answer text, coded 1-5 here, higher = more favourable; the authors' code orders
##the levels the same way): question texts from the export, truncated by Qualtrics at "...":
##  rating           Q.2 "On a scale from strongly oppose to strongly support, where would you place
##                   your level of support for..." 1 Strongly oppose ... 5 Strongly support
##  rating_qualified Q.3 "On a scale from highly unqualified to highly qualified, where would you place
##                   your assessment of thi..." 1 Highly unqualified ... 5 Highly qualified
##  rating_trust     Q.4 "On a scale from strongly mistrust to strongly trust, how much would you trust
##                   that this potential ca..." 1 Strongly mistrust ... 5 Strongly trust
##A blank answer is NA; tasks with all three blank are omitted, as are respondents with no rating.
##Randomization: no restrictions documented; levels look independent and near-uniform except
##clerkship (Did not serve / Served) and gender, which are 2-level attributes.
##Covariates (answer text as exported, blank = NA): cov_age (Q1.2 "How old are you?", years;
##"Under 18" -> NA), cov_education (Q2.1), cov_state (Q2.2), cov_gender (Q2.3 Female/Male ->
##female/male), cov_race (Q2.4), cov_party_id7 (Q2.5 "Generally speaking, do you usually think of
##yourself as:" 7 answer texts, e.g. "A Strong Democrat", "An Independent who leans Republican"),
##cov_religion (Q2.6), cov_income (Q2.7), cov_court_awareness (Q3.1). Dropped: ResponseID, the
##panel id `pid` (respondents re-keyed 1..N in file order), dates, the knowledge and legitimacy
##batteries, Q5-Q8 and Q25-Q31 items, the free-text comment Q31.1. No survey weight.
##N: ABS report 1,650 respondents (886 partisan / 764 nonpartisan; the authors keep rows with a
##non-blank education answer). This table keeps respondents with at least one rating: 1,567
##(800 partisan, 4,782 rows; 767 nonpartisan, 4,588 rows). The partisan arm is ~86 short of the
##article's 886, presumably assigned respondents who rated nothing. No numeric estimate is given
##in the article text to reproduce (results are in figures).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "Judicial_Nominations_FINAL.csv"), encoding = "UTF-8", colClasses = "character")
s <- s[-1]
s[, rid := .I]
anames <- c(`Previous work experience` = "work_experience", Gender = "gender", Age = "age",
            `Race or ethnicity` = "race", `Previous judicial clerkship experience` = "clerkship",
            `Legal education` = "legal_education", Religion = "religion", `Party leaning` = "party_leaning")
sc <- list(c("Strongly oppose", "Oppose", "Neither support nor oppose", "Support", "Strongly support"),
           c("Highly unqualified", "Unqualified", "Neither qualified nor unqualified", "Qualified", "Highly qualified"),
           c("Strongly mistrust", "Mistrust", "Neither trust or mistrust", "Trust", "Strongly trust"))
code <- function(v, lev) { stopifnot(all(v %in% c("", lev))); r <- match(v, lev); r }
build <- function(pref, k, q, arm, natt) {
  r <- data.table(rid = s$rid, task = k, profile = 1L, trial_arm = arm,
                  rating = code(s[[paste0("Q", q, ".2")]], sc[[1]]),
                  rating_qualified = code(s[[paste0("Q", q, ".3")]], sc[[2]]),
                  rating_trust = code(s[[paste0("Q", q, ".4")]], sc[[3]]))
  for (j in 1:natt) {
    nm <- s[[paste0(pref, "-", k, "-", j)]]; lv <- s[[paste0(pref, "-", k, "-1-", j)]]
    stopifnot(all(nm %in% names(anames)), all(lv != ""))
    for (an in names(anames)) {
      hit <- nm == an
      if (any(hit)) { r[hit, paste0("attr_", anames[[an]]) := lv[hit]]; r[hit, paste0("attrpos_", anames[[an]]) := j] }
    }
  }
  r
}
L <- list()
for (k in 1:6) {
  L[[length(L) + 1]] <- build("NP", k, 9 + k, "nonpartisan", 7)
  L[[length(L) + 1]] <- build("P", k, 15 + k, "partisan", 8)
}
d <- rbindlist(L, fill = TRUE)
d[trial_arm == "nonpartisan", attr_party_leaning := "(not shown)"]
d <- d[!(is.na(rating) & is.na(rating_qualified) & is.na(rating_trust))]
stopifnot(d[, uniqueN(trial_arm), rid][, all(V1 == 1)])  # arms are between subjects
for (an in anames) stopifnot(!anyNA(d[[paste0("attr_", an)]]))
stopifnot(d[trial_arm == "nonpartisan", all(is.na(attrpos_party_leaning))], d[trial_arm == "partisan", !anyNA(attrpos_party_leaning)])
stopifnot(d[, uniqueN(paste(attrpos_work_experience, attrpos_gender, attrpos_age, attrpos_race)), rid][, all(V1 == 1)])
blank <- function(v) fifelse(v == "", NA_character_, v)
cv <- s[, .(rid, cov_age = suppressWarnings(as.integer(Q1.2)), cov_education = blank(Q2.1), cov_state = blank(Q2.2),
            cov_gender = c(Female = "female", Male = "male")[Q2.3], cov_race = blank(Q2.4), cov_party_id7 = blank(Q2.5),
            cov_religion = blank(Q2.6), cov_income = blank(Q2.7), cov_court_awareness = blank(Q3.1))]
stopifnot(all(s$Q1.2 %in% c("", "Under 18", as.character(18:99))), all(s$Q2.3 %in% c("", "Female", "Male")))
d <- merge(d, cv, by = "rid")
ids <- sort(unique(d$rid)); d[, id := match(rid, ids)][, rid := NULL]
setcolorder(d, c("id", "task", "profile", "rating", "rating_qualified", "rating_trust", "trial_arm",
                 paste0("attr_", anames), paste0("attrpos_", anames)))
setorder(d, id, task, profile)
print(d[, .(respondents = uniqueN(id), rows = .N), trial_arm])
fwrite(d, file.path(out, "acharya_2018_scotus_nominees.csv"))
