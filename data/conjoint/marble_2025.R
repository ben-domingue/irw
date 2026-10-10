##Run-for-office election-scenario conjoint among US state and local officials from
##Marble, W., Lee, N., & Bram, C. (2025). Stepping up the political ladder: How the burden of
##fundraising limits candidate entry. Political Behavior. https://doi.org/10.1007/s11109-025-10108-5
##Replication data: Harvard Dataverse doi:10.7910/DVN/J3WJMB, CC0 1.0. Files read: Clean.RDS (the
##authors' respondent-level file, Qualtrics export merged with CivicPulse panel fields) and
##Response_with_CP.RDS (1,060 rows; only for the raw text of ideo5, which Clean.RDS has recoded
##with NA and "Not sure" -> 3; matched on ResponseID).
##Wording from survey_instrument.pdf ("Omnibus Elite Survey_February_2017"); levels from the
##F-t-k / F-t-p-k Qualtrics fields as displayed. The authors' Clean_reshaped.RDS is not used because
##it collapses opponent experience and ideology levels.
##Usage: Rscript marble_2025.R <dir holding Clean.RDS and Response_with_CP.RDS> <output dir>
##
##CivicPulse "Omnibus Elite Survey" (Feb 2017) of US local elected officials, staff and some state
##legislators: 985 rows in Clean.RDS, of whom 807 were shown the scenarios. Each saw 3 tasks of 2
##"election scenarios for a seat in a [state legislature | state senate]" (that seat text is
##trial_seat; state senate shown to 61 respondents), 5 attributes: annual salary, fundraising
##needed ("You'd need to raise:"), opponent's experience, opponent's campaign advertising, opponent's
##ideology. Attribute row order randomized once per respondent (the row labels F-t-k are identical
##across a respondent's 3 tasks; stopifnot below): attrpos_ = row 1-5.
##Two outcomes per scenario (grid questions, both scenarios on one screen; order of the two
##questions randomized, conjoint_question_order, and response-option order randomized,
##conjoint_answer_order -> cov_question_order / cov_answer_order):
##  rating          = "How interested would you be in running in each election?"
##                    1 Not interested, 2 Slightly, 3 Somewhat, 4 Moderately, 5 Very interested.
##  rating_winprob  = "If you were to run, how likely is it that you would win in each election?"
##                    1 Very unlikely, 2 Moderately unlikely, 3 50/50, 4 Moderately likely, 5 Very likely.
##  Both coded here from the option text in the order shown in negative_first (the Qualtrics codes
##  flip with the option order, so the export's text is used, not codes). The authors code interest
##  -2..2 and winprob 5/25/50/75/95 (02_reshape_conjoint.R); both are monotone in these codes.
##Each answer sits in one of 4 Qualtrics copies (.1_p, .1_p.1, .1_p.2, .1_p.3) per order arm; the
##script takes the single non-empty copy (stopifnot at most one).
##Restrictions (preanalysis_plan.pdf, p. 2-3): opponents always held the ideology opposed to the
##respondent's: self-identified liberals saw only moderate/somewhat/very conservative opponents,
##conservatives only moderate/somewhat/very liberal ones, moderates the full range (so "Moderate" is
##~29% of profiles). Other attributes: no rule documented; level weights not documented. The PAP
##also says the state senate seat was shown only to current state legislators. Levels as displayed,
##whitespace trimmed ("Never held elected office " has a trailing space in the export).
##Covariates: cov_type (Type), cov_level (Level), cov_elected (Elected 1/0), cov_party_id (PID_3 text;
##"Other party (Please specify):" kept as text, the specify text is not in the deposit), cov_gender
##(Gender Male/Female/Other -> male/female/other), cov_education (Education text), cov_birth_year
##(Born), cov_ideo5 (raw ideo5 text from Response_with_CP.RDS), cov_state (state_ab). Dropped:
##CP_ID (CivicPulse panel ID), ResponseID/responseid (Qualtrics), population/urban share/government
##expenditure of the official's jurisdiction (with state and type these point to one government),
##job/income/fundraising-history items, free-text *_TEXT fields, merged state salary/fundraising
##contextual variables, authors' derived age/college/run_interest. No survey weight.
##Rows with neither rating are omitted. Count check: 807 respondents saw the tasks; those with any
##rating are kept: 745 respondents, 4,297 rows (687 rated all 6 scenarios). The PAP reports 734
##responses collected Feb 23 - Apr 20, 2017 (the 02 script comment says "around ~700"); 745 vs 734
##not reconciled. Spot check (lm with respondent FE, interest rescaled 0-1, SE clustered by id):
##fundraising $300,000 vs $25,000 = -0.149 (SE 0.013), salary $80,000 vs $15,000 = +0.060.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "Clean.RDS")))
r0 <- as.data.table(readRDS(file.path(raw, "Response_with_CP.RDS")))
stopifnot(all(x$ResponseID %in% r0$ResponseID), !anyDuplicated(r0$ResponseID))
x[, ideo_raw := r0$ideo5[match(x$ResponseID, r0$ResponseID)]]
x[, rid := .I]
anames <- c("Annual salary:" = "salary", "You'd need to raise:" = "fundraising",
            "Opponent's experience:" = "opp_experience", "Opponent's campaign advertising:" = "opp_advertising",
            "Opponent's ideology:" = "opp_ideology")
int_lv <- c("not interested", "slightly interested", "somewhat interested", "moderately interested", "very interested")
win_lv <- c("Very unlikely", "Moderately unlikely", "50/50", "Moderately likely", "Very likely")
pick1 <- function(cols) {           # single non-empty copy across the Qualtrics duplicates
  m <- as.matrix(x[, ..cols]); m[is.na(m)] <- ""
  stopifnot(all(rowSums(m != "") <= 1))
  apply(m, 1, function(r) if (any(r != "")) r[r != ""] else NA_character_)
}
rows <- list()
for (t in 1:3) for (p in 1:2) {
  d <- data.table(rid = x$rid, task = t, profile = p)
  for (k in 1:5) {
    lab <- trimws(x[[sprintf("F.%d.%d", t, k)]]); lev <- trimws(x[[sprintf("F.%d.%d.%d", t, p, k)]])
    shown <- lab != ""
    stopifnot(all(lab[shown] %in% names(anames)))
    for (an in anames) {
      w <- shown & anames[lab] == an
      d[w, paste0("attr_", an) := lev[w]]
      d[w, paste0("attrpos_", an) := k]
    }
  }
  ic <- grep(sprintf("^conjoint%d_interest\\.1_%d(\\.[0-9])?$", t, p), names(x), value = TRUE)
  wc <- grep(sprintf("^conjoint%d_prob\\.1_%d(\\.[0-9])?$", t, p), names(x), value = TRUE)
  stopifnot(length(ic) == 4, length(wc) == 4)
  iv <- tolower(trimws(pick1(ic))); wv <- trimws(pick1(wc))
  stopifnot(all(is.na(iv) | iv %in% int_lv), all(is.na(wv) | wv %in% win_lv))
  d[, rating := match(iv, int_lv)][, rating_winprob := match(wv, win_lv)]
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows, fill = TRUE)
# attribute order fixed within respondent across tasks
ord <- unique(d[!is.na(attrpos_salary), .(rid, attrpos_salary, attrpos_fundraising, attrpos_opp_experience,
                                          attrpos_opp_advertising, attrpos_opp_ideology)])
stopifnot(!anyDuplicated(ord$rid))
d <- d[!(is.na(rating) & is.na(rating_winprob))]
stopifnot(d[, all(!is.na(attr_salary) & !is.na(attr_fundraising) & !is.na(attr_opp_experience) &
                  !is.na(attr_opp_advertising) & !is.na(attr_opp_ideology))])
x[, gsex := fifelse(Gender == "Male", "male", fifelse(Gender == "Female", "female", fifelse(Gender == "Other", "other", NA_character_)))]
cv <- x[, .(rid, trial_seat = conjoint_leg, cov_question_order = conjoint_question_order,
            cov_answer_order = conjoint_answer_order, cov_type = Type, cov_level = Level,
            cov_elected = as.integer(Elected), cov_party_id = PID_3, cov_gender = gsex,
            cov_education = Education, cov_birth_year = as.integer(Born),
            cov_ideo5 = fifelse(ideo_raw == "", NA_character_, ideo_raw), cov_state = state_ab)]
d <- merge(d, cv, by = "rid")
setcolorder(d, c("rid", "task", "profile", "rating", "rating_winprob"))
d[, id := match(rid, sort(unique(rid)))][, rid := NULL]
setcolorder(d, "id")
setorder(d, id, task, profile)
cat("respondents:", uniqueN(d$id), " rows:", nrow(d), " shown tasks:", sum(x$F.1.1 != ""), "\n")
fwrite(d, file.path(out, "marble_2025_run_for_office.csv"))
