##Partisan-loyalty candidate conjoint (Study 1) from
##Mummolo, J., Peterson, E., & Westwood, S. (2021). The limits of partisan loyalty. Political
##Behavior, 43, 949-972. https://doi.org/10.1007/s11109-019-09576-3
##Replication data: Harvard Dataverse doi:10.7910/DVN/J9IJGM, CC0 1.0, no restricted files.
##Files read: survey1_updateddemos.csv (Qualtrics wide export, "original format" download of
##survey1_updateddemos.tab) and updated.weight.frame.1.RData (original of updated.weight.frame.1.tab,
##loaded into its own environment). study1_long.csv was read only to check this build. The
##deposit has no questionnaire and the article was not accessible (paywalled), so outcome
##wording is from the data ("Candidate 1" / "Candidate 2") and the authors' code.
##Usage: Rscript mummolo_2021.R <raw dir> <output dir>
##
##Online sample of Democrats and Republicans (Q1.12; independents were not included), fielded July 2016 (StartDate).
##Each respondent saw 7 pairs of hypothetical candidates ("Candidate 1" = profile 1,
##"Candidate 2" = profile 2) with 8 attributes, levels as displayed (Qualtrics F-<task>-<profile>-<k>):
##party Democrat/Republican; gender Female/Male; race White/African American/Latino;
##healthcare Repeal Obamacare/Support Obamacare; terrorism Prohibit Muslim immigration/No
##religious immigration controls; economy Raise/Lower corporate income taxes; women's
##equality (Do not) Require insurance to cover birth control; illegal immigration Deportation
##of all illegal immigrants/Path to citizenship for illegal immigrants. Attribute ROW ORDER was
##randomized once per respondent and kept for all 7 tasks: attrpos_* = row position (1-8).
##choice = Q6.2..Q6.8 (tasks 1-7), which of the two candidates the respondent chose; forced
##choice, no opt-out (every task answered). No rating.
##Respondents: 3,074 completed rows, one with no conjoint design recorded (dropped); the panel id (psid) repeats (58 surplus rows; one id 28 times),
##i.e. people who took the survey more than once. Only each panel id's first response (by
##StartDate) is kept: 3,015 respondents. The authors' study1_long.csv keeps all 3,073 matched
##rows. Ids are re-keyed to integers in StartDate order; psid, ResponseId, IP and
##recipient fields are dropped.
##Check against study1_long.csv: for every kept respondent the attribute text and selected
##outcome agree with the authors' long file (stopifnot below).
##cov_survey_weight = the authors' raking weight to the 2016 ANES (weights.nes; used for their
##"All - Reweighted" model; present for every kept respondent).
##Covariates kept as the export's answer text: cov_gender (Q1.3, Female/Male lowercased to
##female/male), income, race, hispanic (Q1.4-Q1.6), cov_education (Q1.7), cov_age_group (Q1.8; "Prefer not to
##answer" -> NA), cov_party_id (Q1.12, party identification: Democrat/
##Republican; Q1.14/Q1.15 are its strength follow-ups), party_strength (Q1.14/Q1.15), ideology
##(Q1.16), vote_2016 (Q1.17),
##the respondent's own stance on the conjoint issues (Q2.2, Q2.3, Q2.4, Q81, Q2.8, Q2.9:
##"should (not) raise corporate income taxes" etc.) and their importance (Q3.2, Q3.3, Q3.4,
##Q3.9, Q3.10: Extremely important .. Not that important, No opinion).
##Dropped: Q1.9, Q1.10, Q1.11 (participation), Q1.18-Q1.19, the Q1.20 0-100 sliders and Q4.1-Q4.5
##(targets not documented), the Q5 image-ranking items, the `valence` arm and the post-conjoint
##questions Q6.12/Q80/Q6.13 asked by arm (content not documented), all derived variables.
##Study 2 (8 divisive/low-salience issues, 1,558 respondents in CombinedSurvey2) is NOT built:
##its outcome file conjoint_divisive.csv, read by the authors' study2-analysis.R, is not in the
##deposit, and no choice column for those tasks is in the survey files.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "survey1_updateddemos.csv"), encoding = "UTF-8")
stopifnot(all(s$psid != ""), all(s$Q1.12 %in% c("Democrat", "Republican")))
s[, start := as.POSIXct(StartDate, format = "%m/%d/%y %H:%M", tz = "UTC")][, row := .I]
stopifnot(!anyNA(s$start))
s <- s[`F-1-1` != ""]  # one response has no conjoint design recorded
setorder(s, start, row)
s <- s[!duplicated(psid)]
s[, id := seq_len(.N)]
anames <- c("Political Party" = "party", "Gender" = "gender", "Race/Ethnicity" = "race", "Healthcare" = "healthcare",
            "Terrorism" = "terrorism", "The economy" = "economy", "Women's equality" = "womens_equality",
            "Illegal immigration" = "illegal_immigration")
rows <- list()
for (t in 1:7) {
  hdr <- as.matrix(s[, paste0("F-", t, "-", 1:8), with = FALSE])
  stopifnot(all(hdr %in% names(anames)), all(hdr == as.matrix(s[, paste0("F-1-", 1:8), with = FALSE])))
  ch <- s[[paste0("Q6.", t + 1)]]
  stopifnot(all(ch %in% c("Candidate 1", "Candidate 2")))
  for (p in 1:2) {
    lev <- as.matrix(s[, paste0("F-", t, "-", p, "-", 1:8), with = FALSE])
    d <- data.table(id = s$id, task = t, profile = p, choice = as.integer(ch == paste("Candidate", p)))
    for (nm in names(anames)) {
      pos <- max.col(hdr == nm)
      d[, paste0("attr_", anames[[nm]]) := lev[cbind(seq_len(nrow(s)), pos)]]
      d[, paste0("attrpos_", anames[[nm]]) := pos]
    }
    rows[[length(rows) + 1]] <- d
  }
}
d <- rbindlist(rows)
# agrees with the authors' long file
l <- fread(file.path(raw, "study1_long.csv"), encoding = "UTF-8")
chk <- merge(d[, .(id, task, profile, choice, attr_party, attr_healthcare, attr_race)],
             l[, .(psid = respondent, task, profile, selected, Political.Party = `Political Party`, Healthcare, Race = `Race/Ethnicity`)][
               s[, .(id, psid)], on = "psid"], by = c("id", "task", "profile"))
chk <- chk[, if (.N == 1) .SD, .(id, task, profile)]  # psids repeated in the long file are ambiguous there
stopifnot(nrow(chk) > 0.95 * nrow(d), chk[, all(choice == selected & attr_party == Political.Party & attr_healthcare == Healthcare & attr_race == Race)])
e <- new.env(); load(file.path(raw, "updated.weight.frame.1.RData"), envir = e)
w <- unique(as.data.table(e$updated.weight.frame.1)[, .(ResponseId = as.character(caseid), w = weights.nes)])
stopifnot(!anyDuplicated(w$ResponseId))
s <- merge(s, w, by = "ResponseId", all.x = TRUE)
s[, party_strength := fifelse(Q1.14 != "", Q1.14, Q1.15)]
cv <- c(Q1.3 = "gender", Q1.4 = "income", Q1.5 = "race", Q1.6 = "hispanic", Q1.7 = "education", Q1.8 = "age_group",
        Q1.12 = "party_id", party_strength = "party_strength", Q1.16 = "ideology", Q1.17 = "vote_2016",
        Q2.2 = "stance_corporate_tax", Q2.3 = "stance_muslim_immigration", Q2.4 = "stance_obamacare",
        Q81 = "stance_birth_control", Q2.8 = "stance_deportation", Q2.9 = "stance_path_to_citizenship",
        Q3.2 = "importance_corporate_tax", Q3.3 = "importance_muslim_immigration", Q3.4 = "importance_obamacare",
        Q3.9 = "importance_birth_control", Q3.10 = "importance_path_to_citizenship")
cs <- s[, c("id", names(cv), "w"), with = FALSE]
setnames(cs, c("id", paste0("cov_", cv), "cov_survey_weight"))
for (v in grep("^cov_", names(cs), value = TRUE)) if (is.character(cs[[v]])) cs[get(v) == "", (v) := NA]
stopifnot(all(cs$cov_gender %in% c("Female", "Male", NA)))
cs[, cov_gender := tolower(cov_gender)]
cs[cov_age_group == "Prefer not to answer", cov_age_group := NA]
d <- merge(d, cs, by = "id")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(d$id) == nrow(s))
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mummolo_2021_partisan_loyalty.csv"))
