##Judge conjoint (US) from
##Bracic, A., Israel-Trummel, M., Johnson, T., & Tipler, K. (2023). "Because he is gay": How race,
##gender, and sexuality shape perceptions of judicial fairness. The Journal of Politics, 85(4), 1167-1181.
##https://doi.org/10.1086/723996
##Replication data: Harvard Dataverse doi:10.7910/DVN/WDQB4C, CC0 1.0. File read:
##conjoint_judgesdata.csv (datafile 6646608, ?format=original; raw Qualtrics export, two header rows).
##Read as text only: 00_README.txt, "Code Book.docx" (the Qualtrics survey export, incl. the
##randomization JavaScript), "1_Conjoint Set Up.R".
##Usage: Rscript bracic_2023.R <dir holding conjoint_judgesdata.csv> <output dir>
##
##US online sample (Qualtrics survey, October 2019; Lucid `rid` column), 5,168 rows: 420 declined
##consent (no data). Respondents read a hypothetical employment-discrimination case (Hodges v. Johnson
##Metals) whose type was randomized per respondent across 5 arms (trial_discrim_type: racial, gender,
##religious, sexual orientation, gender identity; trial_case_reason = the piped reason, e.g. "she is
##black"), then saw 5 pairs of judges ("Judge 1 / Judge 2", ..., "Judge 9 / Judge 10"). Task and
##profile are RECORDED (pair<t>_1..7 = left judge, pair<t>_8..14 = right judge; the choice answer
##names the judge). 7 attributes, levels drawn independently and uniformly by Math.random (Code Book
##JavaScript): race (White, Black, Hispanic, Asian American, Native American), gender (Man, Woman),
##sexual orientation (Straight, Gay), nominated by (Democrat, Republican), age (40-80 years old),
##law school ranking (10 levels), previous job (6 levels). Attribute ORDER was randomized once per
##respondent (pair1_15 "Order", reused for pairs 2-5): attrpos_ columns give each attribute's row.
##Outcomes, same tasks, one table:
##  choice: "Which of these judges do you trust more to fairly hear this case on <type>
##    discrimination?" Judge A / Judge B, forced (no opt-out).
##  rating_ideology: "Thinking about politics these days, how would you describe the political
##    viewpoint of the following judges?" stored as the codebook codes 1 = Very liberal ... 7 = Very
##    conservative (the export holds the answer text; mapping from the Code Book option codes).
##  rating_politically_motivated: "Judges are supposed to provide an impartial hearing, but sometimes
##    people think judges are politically motivated. Where would you place these two judges on a scale
##    from impartial to politically motivated?" 1 = Impartial ... 7 = Politically motivated (raw;
##    the authors subtract 1).
##  rating_court_trust: "Imagine one of these judges were nominated to the United States Supreme
##    Court. If they joined the Court, how much would you trust the United States Supreme Court to
##    operate in the best interest of the American people?" codebook codes 1 = Not at all, 2 = Not too
##    much, 3 = A fair amount, 4 = A great deal (export holds text).
##  The Code Book also lists Q232 (qualification 1-7) in block 1 only; it is not in the export.
##Rows with no outcome are omitted (tasks a respondent did not reach). 4,334 respondents answered
##pair 1; 4,042 completed all 5 pairs (the authors' analysis sample, set-up script "N= 4042"); the
##partial respondents are KEPT here with the tasks they answered.
##Dropped (PII FOUND): IPAddress, LocationLatitude/Longitude, zip, Lucid rid, Qualtrics ResponseId;
##free text Q181/Q84/Q91/Q105/Q112 (why trust this judge), Q125_7_TEXT, Q155 (free-text guess of the
##number of justices); Lucid profile codes gender/hhi/ethnicity/hispanic/education/political_party/
##region (no labels in the deposit). id = integer in source row order.
##Covariates (answer text from the export, option lists in the Code Book): cov_age (Lucid profile
##`age`, years), cov_age_group (Q150), cov_education (Q151), cov_gender (Q152 traditional / Q125 new
##question arm: Man -> male, Woman -> female, Non-binary/Agender/Genderfluid/A gender not listed
##here -> other), cov_gender_question (arm: traditional/new), cov_race (Q154 multi-select, ";"-joined
##answer text), cov_party_scale (Q156, 1 = Democrat ... 7 = Republican, only the ends labelled; not
##the ANES 7-point item, so not cov_party_id7), cov_ideology (Q161), cov_religious_attendance (Q121),
##cov_income (Q122), cov_lgb (Q120), cov_transgender (Q119), cov_trump_approval (Q126),
##cov_scotus_term_knowledge (Q118 answer), cov_duration_sec (whole survey, Duration (in seconds)).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "conjoint_judgesdata.csv")
h <- names(fread(f, nrows = 0))
s <- fread(f, skip = 2, header = FALSE, col.names = make.unique(h), colClasses = "character", encoding = "UTF-8")
stopifnot(nrow(s) == 5168)
s[, id := .I]
cq <- c("Q124", "Q83", "Q90", "Q104", "Q111"); iq <- c("Q5", "Q87", "Q94", "Q108", "Q115")
pq <- c("Q81", "Q88", "Q95", "Q109", "Q116"); tq <- c("Q82", "Q89", "Q96", "Q110", "Q117")
ideo <- c("Very liberal", "Liberal", "Slightly liberal", "Moderate", "Slightly conservative", "Conservative", "Very conservative")
trust <- c("Not at all", "Not too much", "A fair amount", "A great deal")
an <- c("race", "gender", "sexual_orientation", "nominated_by", "age", "law_school_ranking", "previous_job")
disp <- c("Race", "Gender", "Sexual Orientation", "Nominated by", "Age", "Law School Ranking", "Previous Job")
nz <- function(x) fifelse(x == "", NA_character_, x)
rows <- list()
for (t in 1:5) for (p in 1:2) {
  ch <- s[[cq[t]]]
  r <- data.table(id = s$id, task = t, profile = p,
    choice = fifelse(ch == "", NA_integer_, as.integer(ch == paste("Judge", 2 * t - 2 + p))),
    rating_ideology = match(s[[paste0(iq[t], "_", p)]], ideo),
    rating_politically_motivated = as.integer(nz(s[[paste0(pq[t], "_", p)]])),
    rating_court_trust = match(s[[paste0(tq[t], "_", p)]], trust))
  for (k in 1:7) set(r, j = paste0("attr_", an[k]), value = nz(s[[paste0("pair", t, "_", k + 7 * (p - 1))]]))
  ord <- strsplit(s[[paste0("pair", t, "_15")]], ",")
  for (k in 1:7) set(r, j = paste0("attrpos_", an[k]), value = vapply(ord, function(o) match(disp[k], o), 1L))
  stopifnot(all(ch %in% c("", paste("Judge", 2 * t - 1:0))))
  rows[[length(rows) + 1]] <- r
}
d <- rbindlist(rows)
ok <- d[, !(is.na(choice) & is.na(rating_ideology) & is.na(rating_politically_motivated) & is.na(rating_court_trust))]
d <- d[ok]
stopifnot(!anyNA(d$choice), d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr")]))
stopifnot(all(s$Q5_1[s$Q5_1 != ""] %in% ideo), all(s$Q82_1[s$Q82_1 != ""] %in% trust))
stopifnot(d[, uniqueN(paste(attrpos_race, attrpos_age, attrpos_gender, attrpos_previous_job)), id][, all(V1 == 1)])
g <- fifelse(s$Q152 != "", s$Q152, s$Q125)
race <- apply(s[, .(Q154_1, Q154_2, Q154_3, Q154_6, Q154_4, Q154_5)], 1, function(x) { x <- x[x != ""]; if (length(x)) paste(x, collapse = ";") else NA_character_ })
cov <- data.table(id = s$id, cov_age = suppressWarnings(as.integer(s$age)), cov_age_group = nz(s$Q150), cov_education = nz(s$Q151),
  cov_gender = c(Man = "male", Woman = "female", `Non-binary` = "other", Agender = "other", Genderfluid = "other",
                 `A gender not listed here` = "other")[g],
  cov_gender_question = nz(s$genderquestion), cov_race = race, cov_party_scale = as.integer(nz(s$Q156_1)),
  cov_ideology = nz(s$Q161), cov_religious_attendance = nz(s$Q121), cov_income = nz(s$Q122), cov_lgb = nz(s$Q120),
  cov_transgender = nz(s$Q119), cov_trump_approval = nz(s$Q126), cov_scotus_term_knowledge = nz(s$Q118),
  cov_duration_sec = as.numeric(s$`Duration (in seconds)`),
  trial_discrim_type = nz(s$discrimtype), trial_case_reason = nz(s$pipe1))
stopifnot(all(g %in% c("", names(c(Man = 1, Woman = 1, `Non-binary` = 1, Agender = 1, Genderfluid = 1, `A gender not listed here` = 1)))))
d <- merge(d, cov, by = "id")
stopifnot(!anyNA(d$trial_discrim_type), uniqueN(d$id) == 4334, d[, uniqueN(task), id][, sum(V1 == 5)] == 4042)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bracic_2023_judge_fairness.csv"))
