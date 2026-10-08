##Judicial-candidate conjoint (US state supreme court elections) from
##Kennedy, M., Nelson, M. J., & Heidt-Forsythe, E. (2025). Gender stereotypes and candidate
##qualifications in judicial elections. Political Research Quarterly, 78(1).
##https://doi.org/10.1177/10659129241275458 (online 2024-10-12)
##Replication data: Harvard Dataverse doi:10.7910/DVN/JVIARV, CC0 1.0. File read:
##KNH_GenderConjoint_Prolific.tab, original-format download KNH_GenderConjoint_Prolific.csv
##(raw Qualtrics export, wide: header row, question-text row, ImportId row, 997 responses).
##The authors' KNH_PRQ_Prolific_ConjointCode.R was read as text (not run) for the coding of
##the outcomes. The article itself was not reachable (publisher and repository both blocked
##automated access), so nothing here is checked against its text.
##Usage: Rscript kennedy_2025.R <dir holding the .csv> <output dir>
##
##997 Prolific respondents (all Finished = 1, Progress = 100; fielded 2022-06), 10 tasks each
##of two hypothetical candidates ("Candidate 1" / "Candidate 2") for a state high court seat,
##5 attributes: prior political experience, education, gender, occupation, newspaper
##endorsement. Levels are the Qualtrics display text (curly apostrophe kept). Attribute order
##was randomized per respondent and held fixed across that respondent's 10 tasks; it is kept
##as attrpos_* (1 = top row). No randomization restrictions are documented; every level
##combination occurs.
##Outcomes (one experiment, both asked on the same screen):
##  choice = "Which candidate do you prefer?" Candidate 1 / Candidate 2, no opt-out. In tasks
##           4 and 7 the exported question text reads "Which job offer do you prefer?",
##           apparently a leftover Qualtrics label; the authors treat those tasks like the rest.
##           15 tasks (from 2 respondents) have no choice recorded; there choice is left blank
##           (both profiles), while the ratings are kept.
##  rating = "How qualified is Candidate 1 [2] to be a state high court justice?" 4-point item.
##           The source codes 1 (most qualified) to 4 (least qualified); the response-option
##           wording is not in the deposit. As in the authors' code (rating = 5 - code) the
##           scale is reversed here so that 4 = most qualified, 1 = least qualified.
##Covariates keep the source's Qualtrics codes; the answer-option labels are NOT in the
##deposit, so the reserved covariates whose codes cannot be fully mapped carry a _code suffix:
##  cov_gender_code ("How do you describe yourself?"): 1 male and 2 female per the authors'
##    code (Female = 1 for gender 2, 0 for gender 1; 3-5 set to NA), 4 "Prefer to self-describe"
##    (export column gender_4_TEXT); what 3 and 5 are is not in the deposit.
##  cov_party_id_code (source pid1, "Generally speaking, do you usually think of yourself as a
##    Democrat, a Republican, an independent, or what?"): 1 Democrat, 2 Republican per the
##    authors' code; 3 and 4 are both coded independent there, which of them is "independent"
##    and which "other" is not in the deposit.
##  cov_education_code (source degree, "What is the highest grade or year of school you have
##    completed?", 1-8; the authors' code makes 7-8 "College Degree", 1-6 "No College Degree").
##Strength/lean follow-ups (codes kept): cov_party_strength_dem (source pid2, "Would you call
##yourself a strong Democrat or a not very strong Democrat?"), cov_party_strength_rep (pid3, the
##same for Republicans), cov_party_lean (pid4, "Do you think of yourself as closer to the
##Republican Party or to the Democratic Party": 1 Republican, 2 Democrat, 3 neither, per the
##authors' code); cov_polinterest 1-2 high, 3-4 low (authors' code).
##cov_birth_year (yyyy), cov_state (Qualtrics 50 states + DC + PR list), cov_hispanic,
##cov_race and cov_mobilization (multi-select, comma-separated codes as text),
##cov_marital, cov_child18, cov_votefreq, cov_ideology (1-7), cov_sexism_1-5,
##political-knowledge items cov_knowgender_1/2 (numeric guesses), cov_knowgov, cov_knowleg,
##cov_knowct, cov_knowlastsay, cov_attention1 (instructed-response attention check: "select
##FoxNews.com and NBC.com"; multi-select codes as text, kept as is because the code of each
##website is not in the deposit, so it is not recoded to cov_attention_pass).
##Dropped: IP address, latitude/longitude, Prolific ID, Qualtrics ResponseId, free-text gender
##self-description, the free-text closing comment, page timers, dates, durations. Respondent
##ids are re-keyed 1..997 in file order. Two Prolific IDs appear twice (995 distinct IDs for
##997 responses); both responses of each are kept, as in the authors' analysis.
##Count: 997 respondents, 9,970 tasks (the article's N was not checked). Spot check: the female
##choice AMCE (lm, clustered by id) is +0.098 (SE 0.008) and the female rating AMCE +0.015
##(SE 0.009), matching the abstract (women preferred, not rated more qualified).
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "KNH_GenderConjoint_Prolific.csv")
x <- fread(f, colClasses = "character", encoding = "UTF-8")[-(1:2)]
stopifnot(nrow(x) == 997, all(x$Finished == "1"))
x[, id := .I]
att <- c("Prior Political Experience" = "political_experience", "Education" = "education", "Gender" = "gender",
         "Occupation" = "occupation", "Newspaper Endorsement" = "endorsement")
rows <- list()
for (t in 1:10) for (p in 1:2) {
  d <- data.table(id = x$id, task = t, profile = p)
  ch <- x[[paste0("choice_", t)]]
  d[, choice := fifelse(ch == "", NA_integer_, as.integer(ch == as.character(p)))]
  d[, rating := 5L - as.integer(x[[sprintf("qual%d_%d", p, t)]])]
  for (j in 1:5) {
    nm <- x[[sprintf("F-%d-%d", t, j)]]; lv <- x[[sprintf("F-%d-%d-%d", t, p, j)]]
    stopifnot(all(nm %in% names(att)))
    for (k in names(att)) {
      w <- nm == k
      d[w, paste0("attr_", att[[k]]) := lv[w]]
      d[w, paste0("attrpos_", att[[k]]) := j]
    }
  }
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows, use.names = TRUE)
setcolorder(d, c("id", "task", "profile", "choice", "rating", paste0("attr_", att), paste0("attrpos_", att)))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr")]), !anyNA(d$rating), d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)])
num <- c(yearborn = "birth_year", state = "state", gender = "gender_code", hisp = "hispanic", degree = "education_code", marstat = "marital",
         child18 = "child18", polinterest = "polinterest", votefreq = "votefreq", ideo = "ideology", pid1 = "party_id_code", pid2 = "party_strength_dem",
         pid3 = "party_strength_rep", pid4 = "party_lean", sexism_1 = "sexism_1", sexism_2 = "sexism_2", sexism_3 = "sexism_3", sexism_4 = "sexism_4",
         sexism_5 = "sexism_5", knowgender_1 = "knowgender_1", knowgender_2 = "knowgender_2", knowgov = "knowgov",
         knowleg = "knowleg", knowct = "knowct", knowlastsay = "knowlastsay")
txt <- c(race = "race", mobil = "mobilization", ATTENTION1 = "attention1")
cv <- data.table(id = x$id)
for (v in names(num)) cv[, paste0("cov_", num[[v]]) := suppressWarnings(as.numeric(x[[v]]))]
for (v in names(txt)) cv[, paste0("cov_", txt[[v]]) := fifelse(x[[v]] == "", NA_character_, x[[v]])]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kennedy_2025_judicial_candidates.csv"))
