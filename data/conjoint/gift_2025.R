##Speech-scandal candidate vignette experiment (US) from
##Gift, T., & Lastra-Anadón, C. X. (2025). Can politicians say that? What shapes public responses to
##speech scandals? Journal of Experimental Political Science. https://doi.org/10.1017/XPS.2025.10010
##Replication data: Harvard Dataverse doi:10.7910/DVN/DUVWXQ, CC0 1.0. Files read:
##rv-omni-2024-november-b-final-2024-12-09.csv, rv-omni-2024-december-a.csv,
##rv-omni-2024-december-b.csv (three YouGov omnibus polls, tab-separated), Readme.txt,
##MainForbidden_Speech.pdf and RevisedApendixForbidden_Speech.pdf (design, wording, Tables A.1-A.4).
##"20250624 ForbSpeechAnalysis.R" read as text, not run: all code-to-label mappings below come from it.
##Usage: Rscript gift_2025.R <dir holding the three csv files> <output dir>
##
##YouGov US, December 5-19, 2024, 3,162 adults (article: 3,162), stacked from three omnibus polls
##as in the authors' code (cov_omnibus; whether a panelist could sit in two polls is not stated).
##Each respondent read three newspaper-style vignettes (task = round 1-3, recorded), one candidate
##each (profile = 1), about a candidate for state legislature; ~20% of vignettes are the clean
##control with no speech controversy (split = 1). Ten randomized elements; photo, name and party
##always shown; the remark, its context and the politician's response only in treated vignettes,
##so they are "(not shown)" in controls. Duplicate photos and quotes across a respondent's three
##tasks were avoided by YouGov (article fn. 4, 8): a restriction across tasks.
##Attribute text: the screen text is only partly published (Figure 1 example; Tables A.2-A.3 quotes,
##slurs written with asterisks), so levels are the authors' category labels (Table A.1-A.4 wording):
##  attr_name (Table A.4: two names per gender x race; split_name 1/2 = Name 1/2 of the table;
##    the article's Figure 1 example name "Juan García" is not in Table A.4, so the table may not
##    match every fielded name: INFERRED), attr_race (Asian / Black / Hispanic / White; split_race
##    1-4 per the code comments), attr_gender (Woman / Man) and attr_age (Younger (about 40) /
##    Older (about 60)) from split_genderage (1 young woman, 2 young man, 3 older woman, 4 older
##    man; code comments), all three conveyed by the headshot (16 photos) and the name;
##  attr_party (split_party 1 Democrat, 2 Republican; "the Democrat politician" in Figure 1);
##  attr_remark (split_treat_severity: Slur / Stereotype / Dehumanizing language / Denial of
##    discrimination), attr_target (split_treat_identity: Blacks / Hispanics / Asian-Americans /
##    Jews / Muslims / Gays / Women), attr_quote_version (split_treat_quote: Quote 1 / Quote 2 of
##    Tables A.2-A.3), attr_response (split_treat_response, the ten sub-types of Table A.3),
##    attr_timing (split_treat_time: yesterday / five years ago), attr_planned (Planned /
##    Unplanned), attr_history (Has made such comments before / First time).
##Outcomes (article p. 9 and appendix "DV Questions"):
##  choice = cand_consider, "If you had to make a choice without knowing more, would you ever
##           consider voting for this candidate?" 1 = Yes (choice 1), 2 = No (choice 0); single
##           profile, so rejecting is the outside option (opt_out yes).
##  rating_thermometer = FAVOR_therm<k>, feeling thermometer 0 (cold) - 100 (warm); "don't know"
##           (dk_flag = 1, 263 answers) is NA.
##  rating_objectionable = cand_draw<k>, "On a scale of 1 to 7, how objectionable do you think the
##           candidate's behavior is in this case?" 1 Not at all objectionable - 7 The most
##           objectionable I can imagine (higher = MORE objectionable).
##Covariates: cov_survey_weight (YouGov `weight`), cov_omnibus (source poll), cov_birth_year
##(birthyr), cov_gender (gender 1 = male, 2 = female per the code comments; other codes -> NA),
##codes without labels in the deposit: cov_race_code, cov_educ_code, cov_pid3_code (1 Democrat,
##2 Republican per the code; rest undocumented), cov_pid7_code, cov_ideo5_code.
##Dropped: open-ended free text (gift_open, client_question_2, ygb_attn_check_open), interview
##date, the remaining omnibus questions, derived split_combined*/split_*_ext codes.
##Rows: 3,162 x 3 = 9,486. The article reports 3,162 respondents but "a total N of 10,200"
##vignettes, which 3 x 3,162 does not give (perhaps the pre-registered target); not reconciled.
##Spot check: share ruling the candidate out (choice 0) is .22 in controls and .46 / .54 / .62 /
##.69 for denial / stereotype / slur / dehumanizing remarks: dehumanizing language worst, as the
##article reports (contrary to its Prediction 1a).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fs <- c("rv-omni-2024-november-b-final-2024-12-09.csv", "rv-omni-2024-december-a.csv", "rv-omni-2024-december-b.csv")
keep <- c("weight", "birthyr", "gender", "race", "educ", "pid3", "pid7", "ideo5")
s <- rbindlist(lapply(seq_along(fs), function(i) {
  h <- names(fread(file.path(raw, fs[i]), nrows = 0))
  x <- suppressWarnings(fread(file.path(raw, fs[i]), select = c(keep, grep("^split_|^cand_|^FAVOR_", h, value = TRUE))))
  setnames(x, sub("_c[1l](_dk_flag)?$", "\\1", names(x)))
  x[, cov_omnibus := c("November B", "December A", "December B")[i]] }), fill = TRUE)
stopifnot(nrow(s) == 3162)
s[, rid := .I]
nm <- list(Man = list(White = c("Thomas Wagner", "Richard Hoffman"), Asian = c("Hung Chen", "Hung Wang"),
                      Black = c("Jermaine Wood", "Jermaine Jackson"), Hispanic = c("Julio Perez", "Alejandro Gonzalez")),
           Woman = list(White = c("Mary Meyer", "Mary Ryan"), Asian = c("Wei Li", "Jian Li"),
                        Black = c("Lakisha Jackson", "Tamika Jackson"), Hispanic = c("Guadalupe Rodriguez", "Guadalupe Garcia")))
ns <- function(x) fifelse(is.na(x), "(not shown)", x)
d <- rbindlist(lapply(1:3, function(k) {
  g <- function(v) s[[sprintf(v, k)]]
  x <- data.table(id = s$rid, task = k, profile = 1L, split = g("split_%d"),
    consider = g("cand_consider%d"), therm = g("FAVOR_therm%d"), dk = g("FAVOR_therm%d_dk_flag"), objection = g("cand_draw%d"),
    attr_race = c("Asian", "Black", "Hispanic", "White")[g("split_race_%d")],
    attr_gender = c("Woman", "Man", "Woman", "Man")[g("split_genderage_%d")],
    attr_age = c("Younger (about 40)", "Younger (about 40)", "Older (about 60)", "Older (about 60)")[g("split_genderage_%d")],
    nmv = g("split_name_%d"), attr_party = c("Democrat", "Republican")[g("split_party_%d")],
    attr_remark = c("Slur", "Stereotype", "Dehumanizing language", "Denial of discrimination")[g("split_treat_severity_%d")],
    attr_target = c("Blacks", "Hispanics", "Asian-Americans", "Jews", "Muslims", "Gays", "Women")[g("split_treat_identity_%d")],
    attr_quote_version = c("Quote 1", "Quote 2")[g("split_treat_quote_%d")],
    attr_response = c("Apology: remorseful", "Apology: woke", "Apology: sorry-I-offended", "Excuse: plead ignorance",
                      "Excuse: misspeak", "Excuse: taken out of context", "Defense: deny wrongdoing", "Defense: play the victim",
                      "Defense: go on the attack", "No comment")[g("split_treat_response_%d")],
    attr_timing = c("Yesterday", "Five years ago")[g("split_treat_time_%d")],
    attr_planned = c("Planned", "Unplanned")[g("split_treat_planned_%d")],
    attr_history = c("Has made such comments before", "First time")[g("split_treat_history_%d")])
  x }))
d[, attr_name := mapply(function(ge, ra, v) nm[[ge]][[ra]][v], attr_gender, attr_race, nmv)]
tr <- c("attr_remark", "attr_target", "attr_quote_version", "attr_response", "attr_timing", "attr_planned", "attr_history")
stopifnot(d[split == 1, all(is.na(as.matrix(.SD))), .SDcols = tr], d[split == 2, !anyNA(as.matrix(.SD)), .SDcols = tr])
for (v in tr) set(d, j = v, value = ns(d[[v]]))
stopifnot(!anyNA(d[, .(attr_race, attr_gender, attr_age, attr_name, attr_party)]), d[, all(consider %in% 1:2)],
          d[, all(objection %in% 1:7)], d[dk == 0, all(therm %in% 0:100)], d[dk == 1, all(is.na(therm))])
d[, choice := as.integer(consider == 1)][, rating_thermometer := fifelse(dk == 1, NA_integer_, as.integer(therm))]
d[, rating_objectionable := as.integer(objection)]
cv <- s[, .(id = rid, cov_survey_weight = weight, cov_omnibus, cov_birth_year = as.integer(birthyr),
            cov_gender = fcase(gender == 1, "male", gender == 2, "female", default = NA_character_),
            cov_race_code = as.integer(race), cov_educ_code = as.integer(educ), cov_pid3_code = as.integer(pid3),
            cov_pid7_code = as.integer(pid7), cov_ideo5_code = as.integer(ideo5))]
d <- merge(d[, c("id", "task", "profile", "choice", "rating_thermometer", "rating_objectionable", "attr_name", "attr_race",
                 "attr_gender", "attr_age", "attr_party", tr), with = FALSE], cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gift_2025_speech_scandals.csv"))
