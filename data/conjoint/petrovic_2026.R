##AI-employability-score hiring conjoint (Serbia) from
##Petrović, N., Kuzmanović, M., Anđelković Labrović, J., Kovačević, I., & Llorens, A. (2026).
##Data for: How much weight does an AI score carry in hiring? Qualification conflict and
##evaluator heterogeneity in a choice-based conjoint experiment [Data set]. Zenodo.
##https://doi.org/10.5281/zenodo.20703547 (accompanying manuscript not yet published; no article DOI)
##Licence: CC BY 4.0 (Zenodo record licence). The record description adds "Use is subject to the
##condition that no attempt be made to re-identify participants."
##File read: conjoint_data_anonymized (1).xlsx (saved as cj.xlsx), all four sheets, read with
##readxl as text: "Model matrix" (design dummies + choice), "Very raw responses" (first-stage pick
##and second-stage response), "Individual preferences" (only its header row, which names every
##dummy's level: "A1L2: Pol: Zensko" ...), "Respondents" (covariates).
##Usage: Rscript petrovic_2026.R <raw dir> <output dir>
##
##432 participants (students at the University of Belgrade, recruited for course credit per the
##record), 8 choice tasks (QES = task) of 4 hypothetical job candidates (ALT 1-4 = profile),
##5 attributes, Serbian display. The export format (Model matrix / Very raw responses / segments)
##is Conjointly's; ALT 5 in the model matrix is the "none" row (all dummies 0, ASC 0), not a
##candidate, so it is not a profile.
##Outcomes (wording not deposited):
##  choice: the forced first-stage pick among the 4 candidates ("Very raw responses"
##    alternative_seq_order); one per task, no opt-out.
##  choice_commit: the dual-response outcome the model matrix records: 1 on the picked candidate
##    if the participant then said they would actually advance that candidate (second-stage
##    response 1), all 0 if not (second-stage 0 = the model matrix's "none", 392 of 3,456
##    tasks). Verified: model-matrix RES on ALT 1-4 equals pick x second-stage in every task.
##Attributes and levels: level text = the level names in the "Individual preferences" header
##(the design's level names in the survey tool; L1 = the all-zero reference in the model matrix):
##  gender (Pol): No info / Zensko / Musko
##  education (Obrazovanje): Nema informacije / Filozofski fakultet / Elektrotehnički fakultet
##  age (Uzrast): Nema info / 24 godine / 32 godine / 40 godina
##  hobby (Hobi): No info / Bavi se sportom / Bavi se umetnošću / Voli da čita / Bastovanstvo /
##    Filmovi / Sah
##  ai_score (Skor zaposlivosti): 7% / 23% / 40% / 57% / 74% / 91%
##The "No info"/"Nema informacije"/"Nema info" levels are the design's no-information levels;
##whether the screen showed that text or left the row empty is not documented, so the stored
##text is kept as named (not "(not shown)"). Diacritics are as in the source (Zensko, Musko,
##Sah without them). No restrictions are documented; attribute order unknown.
##Covariates (Respondents sheet, answer text in Serbian): cov_age (Q5), cov_gender (Q6 Žensko =
##female, Muško = male, Drugo = other, "Ne želim da ogovorim" (prefer not to answer) = NA),
##cov_education (Q7), cov_employment (Q8), cov_hobbies (Q9, multi-select as listed),
##cov_hiring_experience (Q10, multi-select), cov_field_of_study (Q11), cov_position (Q12),
##cov_ai_in_hiring (Q19), numeric 1-5 items kept raw with their English short labels
##(anchors not deposited): cov_q13_ai_familiarity, cov_q14_ai_usage, cov_q15_ai_decision_making,
##cov_q16_ai_recommendation_satisfaction, cov_q17_ai_advice_verification,
##cov_q18_ai_tools_understanding, cov_q20_experience_rating ("N/A" -> NA), cov_q21_ai_candidate_
##assessment, cov_q22_ai_assessment_objectivity, cov_q23_confidence_assessment,
##cov_q24_ai_job_candidate_assessment; cov_wave2 (the export's "Segment Wave 2" flag, 1/0).
##Dropped: the other derived "Segment" dummies, the HB part-worths, STR (task string id).
##participant_id is already a sequential pseudonym (re-keyed anyway).
suppressMessages(library(readxl)); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "cj.xlsx")
rd <- function(s) { x <- suppressMessages(read_excel(f, s, col_names = FALSE, col_types = "text"))
  x <- as.data.table(x); h <- unlist(x[3]); x <- x[-(1:3)]; setnames(x, make.unique(as.character(h))); x }
m <- rd("Model matrix"); v <- rd("Very raw responses"); p <- rd("Individual preferences"); r <- rd("Respondents")
m[, names(m) := lapply(.SD, as.numeric)]
v[, names(v) := lapply(.SD, as.integer)]
stopifnot(nrow(m) == 17280L, uniqueN(m$participant_id) == 432L, nrow(v) == 3456L)
## level names from the preferences header: "A1L2: Pol: Zensko"
hd <- grep("^A[0-9]L[0-9]+:", names(p), value = TRUE)
lev <- data.table(code = sub(":.*", "", hd), level = trimws(sub("^[^:]+:[^:]+: *", "", hd)))
lev[, `:=`(att = as.integer(sub("A([0-9])L.*", "\\1", code)), l = as.integer(sub(".*L", "", code)))]
anames <- c("gender", "education", "age", "hobby", "ai_score")
stopifnot(nrow(lev) == 3 + 3 + 4 + 7 + 6)
pr <- m[ALT %in% 1:4]
d <- pr[, .(id = as.integer(participant_id), task = as.integer(QES), profile = as.integer(ALT), res = as.integer(RES))]
for (k in 1:5) {
  dummies <- lev[att == k & l > 1, code]
  M <- as.matrix(pr[, ..dummies]); stopifnot(all(rowSums(M) <= 1))
  lv <- ifelse(rowSums(M) == 0, 1L, max.col(M) + 1L)
  d[, paste0("attr_", anames[k]) := lev[att == k][match(lv, l), level]]
}
stopifnot(!anyNA(d))
setnames(v, c("set_seq_order", "alternative_seq_order", "participant_id", "second_stage_response"), c("task", "pick", "id", "commit"))
d <- merge(d, v, by = c("id", "task"))
stopifnot(all(d$pick %in% 1:4), all(d$commit %in% 0:1))
d[, choice := as.integer(profile == pick)]
d[, choice_commit := as.integer(profile == pick & commit == 1L)]
stopifnot(all(d$choice_commit == d$res))          # model matrix agrees with the two-stage record
d[, c("pick", "commit", "res") := NULL]
## covariates
q <- function(pat) { j <- grep(pat, names(r), fixed = TRUE); j <- j[!grepl("Option", names(r)[j])]; stopifnot(length(j) == 1); r[[j]] }
g <- q("Q6: _ Gender Question")
cv <- data.table(id = as.integer(r$participant_id), cov_age = as.integer(q("Q5: _ Age Question")),
  cov_gender = c("female", "male", "other")[match(g, c("Žensko", "Muško", "Drugo"))],
  cov_education = q("Q7: _ Education Level"), cov_employment = q("Q8: _ Employment Status Survey"),
  cov_hobbies = q("Q9: _ Hobby Preferences Survey"), cov_hiring_experience = q("Q10: _ Employment Process Experience"),
  cov_field_of_study = q("Q11: _ Field of Study"), cov_position = q("Q12: _ Current/Last Organizational Position"),
  cov_ai_in_hiring = q("Q19: _ AI in Hiring Process"))
stopifnot(all(g %in% c("Žensko", "Muško", "Drugo", "Ne želim da ogovorim")))
nq <- c(q13_ai_familiarity = "Q13:", q14_ai_usage = "Q14:", q15_ai_decision_making = "Q15:",
        q16_ai_recommendation_satisfaction = "Q16:", q17_ai_advice_verification = "Q17:",
        q18_ai_tools_understanding = "Q18:", q20_experience_rating = "Q20:", q21_ai_candidate_assessment = "Q21:",
        q22_ai_assessment_objectivity = "Q22:", q23_confidence_assessment = "Q23:", q24_ai_job_candidate_assessment = "Q24:")
for (n in names(nq)) { z <- q(nq[[n]]); z[z == "N/A"] <- NA; cv[, paste0("cov_", n) := as.integer(z)] }
cv[, cov_wave2 := as.integer(r[["Segment  Wave 2"]])]
cv[!(cov_age %between% c(16L, 110L)), cov_age := NA]
d <- merge(d, cv, by = "id", all.x = TRUE)
stopifnot(uniqueN(d$id) == 432L, d[, sum(choice), .(id, task)][, all(V1 == 1)])
d[, id := match(id, sort(unique(id)))]
setcolorder(d, c("id", "task", "profile", "choice", "choice_commit"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "petrovic_2026_ai_hiring_score.csv"))
