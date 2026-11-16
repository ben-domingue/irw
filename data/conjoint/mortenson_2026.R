##Candidate conjoint after democracy-framing videos (US Congress candidates), from the deposit
##"Framing Democracy at the Ballot Box" (candidate conjoint x framing videos), depositor Chloe Mortenson (University of Pennsylvania), per the Dataverse citation metadata; no article located 2026-11-10
##(Harvard Dataverse doi:10.7910/DVN/PUPXPU, CC0 1.0; no article DOI; fielded 13-26 May 2026).
##Files read: candidate_conjoint_deidentified.tab (wide Qualtrics export, 3 header rows: names, question text,
##ImportIds) and codebook_raw_variables.tab (variable text and value lists).
##Usage: Rscript mortenson_2026.R <dir holding candidate_conjoint_deidentified.tab> <output dir>
##
##US online sample (Qualtrics export, English); 3,243 rows in the file, 1,442 reached the conjoint. Respondents
##were randomized to a framing-video arm before the conjoint (column `condition`: control, econ, policy, speech,
##checks; the codebook names these arms only by the column names timer_econ/policy/speech/check* and the
##`vidrecall` options: economic wellbeing, government responsiveness, freedom of expression, checks and balances;
##the mapping of arm to video is inferred from those names). The arm is stored as trial_arm (as coded in the
##source). The conjoint itself is a Qualtrics CBC design (vers_CBCONJOINT 1-260 = pre-generated design versions
##(a fixed blocked design with 260 versions)), 6 tasks x 2 profiles of candidates for U.S. Congress, 7 attributes:
##economic policy, immigration policy, position on free speech, position on executive authority (each a sentence,
##2 levels), political party (Democrat/Republican), gender (Female/Male), race/ethnicity (Black/Hispanic/White).
##The level text is the text displayed (feature<k>.<task>.<profile>_CBCONJOINT); the attribute shown in row
##position k is named in feature<k>.DISPLAY_NAME, constant over a respondent's tasks: the order of attributes is
##randomized per respondent and recorded (attrpos_ = 1..7 position from the top).
##Outcomes on the same tasks:
##  choice: "If an election were held today, which of these candidates would you vote for? Please select one."
##    (columns C1-C6, 1 = Candidate Profile 1, 2 = Profile 2; forced, no opt-out).
##  trial_support_strength: follow-up "How strong or weak is your support for the candidate you just selected?"
##    (DC60-DC64, DC79: Strong support / Weak support), a task-level answer about the chosen candidate.
##Tasks without an answer are dropped; respondents with no complete task are dropped (51 reached the conjoint
##without answering): 1,391 respondents; 1,351 completed all 6 tasks.
##Covariates: cov_gender (female/male/other from the gender item; "Other, please describe" -> other),
##cov_age (years; values outside 18-100 set NA), cov_education (answer text), cov_race, cov_hispanic (answer text;
##free-text "Something else" content is not in the file), cov_party_id (answer text of the party item),
##cov_ideology (the political-issues self-placement item idpol, answer text), cov_duration_sec (Duration in seconds,
##whole survey), cov_attention_pass (1 when the instructed-response item `check` = "Purple"; the file holds only
##that value, so a failure cannot be told from a missing answer: NA otherwise).
##Dropped: StartDate/EndDate/RecordedDate, Status, IP-related fields, timers, ResponseId (re-keyed), consent,
##video checks and reactions, other attitudes, the free-text parts. No weights in the file. PII FOUND: none (the
##codebook says ResponseId is a random public participant ID; the export says Status "IP Address" but holds no IP).
##Respondent count vs paper: no paper; the triage note's "N = 1,234" is not reproduced (1,391 answered a task).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "candidate_conjoint_deidentified.tab"), quote = "\"", fill = TRUE)
d <- d[-(1:2)]
x <- d[feature0.DISPLAY_NAME != ""]
stopifnot(nrow(x) == 1442, x[, uniqueN(ResponseId)] == 1442)
attrs <- c("Economic Policy" = "economic_policy", "Immigration Policy" = "immigration_policy",
           "Position on Free Speech" = "free_speech", "Position on Executive Authority" = "executive_authority",
           "Political Party" = "party", "Gender" = "gender", "Race/Ethnicity" = "race_ethnicity")
x[, id := .I]
rows <- list()
for (t in 1:6) {
  cc <- c("C1", "C2", "C3", "C4", "C5", "C6")[t]; sc <- c("DC60", "DC61", "DC62", "DC63", "DC64", "DC79")[t]
  for (p in 1:2) {
    r <- x[, .(id, task = t, profile = p, resp = get(cc), strength = get(sc), arm = condition)]
    for (a2 in attrs) { r[, (paste0("attr_", a2)) := NA_character_]; r[, (paste0("attrpos_", a2)) := NA_integer_] }
    for (k in 0:6) {
      nm <- attrs[x[[paste0("feature", k, ".DISPLAY_NAME")]]]
      stopifnot(!anyNA(nm))
      lv <- x[[sprintf("feature%d.%d.%d_CBCONJOINT", k, t, p)]]
      for (a2 in unique(nm)) {
        w <- which(nm == a2)
        set(r, w, paste0("attr_", a2), lv[w]); set(r, w, paste0("attrpos_", a2), k + 1L)
      }
    }
    rows[[length(rows) + 1]] <- r
  }
}
d2 <- rbindlist(rows, fill = TRUE)
d2 <- d2[resp %in% c("1", "2")]
d2[, n := .N, .(id, task)]; d2 <- d2[n == 2]
d2[, choice := as.integer(as.character(profile) == resp)]
stopifnot(d2[, sum(choice), .(id, task)][, all(V1 == 1)])
ac <- grep("^attr_", names(d2), value = TRUE); stopifnot(!anyNA(d2[, ..ac]), uniqueN(d2$attr_party) == 2)
cv <- x[, .(id, cov_gender = fcase(gender == "Female", "female", gender == "Male", "male", gender != "", "other"),
            cov_age = {a <- suppressWarnings(as.integer(age)); fifelse(a >= 18 & a <= 100, a, NA_integer_)},
            cov_education = fifelse(educ == "", NA_character_, educ), cov_race = fifelse(race == "", NA_character_, race),
            cov_hispanic = fifelse(hisp == "", NA_character_, hisp), cov_party_id = fifelse(party == "", NA_character_, party),
            cov_ideology = fifelse(idpol == "", NA_character_, idpol),
            cov_duration_sec = as.integer(`Duration (in seconds)`),
            cov_attention_pass = fifelse(check == "Purple", 1L, NA_integer_))]
d2 <- merge(d2, cv, by = "id")
d2[, id := as.integer(factor(id))]
d2[, trial_arm := arm]; d2[, trial_support_strength := fifelse(strength == "", NA_character_, strength)]
stopifnot(d2[, uniqueN(is.na(trial_support_strength)), .(id, task)][, all(V1 == 1)])
nm <- c("id", "task", "profile", "choice", sort(grep("^attr_", names(d2), value = TRUE)), sort(grep("^attrpos_", names(d2), value = TRUE)),
        grep("^cov_", names(d2), value = TRUE), "trial_arm", "trial_support_strength")
d2 <- d2[, ..nm]
setorder(d2, id, task, profile)
fwrite(d2, file.path(out, "mortenson_2026_democracy_frames.csv"))
