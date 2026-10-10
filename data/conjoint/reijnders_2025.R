##Co-creation (citizen participation) conjoint, Belgium, from
##Reijnders, L. (2025). Survey + conjoint experiment co-creation in Belgium [Data set]. Zenodo.
##https://doi.org/10.5281/zenodo.15130509 (no associated article found in the record).
##Licence: CC BY 4.0 (Zenodo record), open access, no other terms.
##File read: "BoCoDigital GPS + Conjoint_March 11, 2025_08.56.sav" (saved as d.sav; Qualtrics SPSS
##export, 1,686 rows, one per respondent; variable and value labels in Dutch).
##Usage: Rscript reijnders_2025.R <raw dir> <output dir>
##
##Belgian adults (Qualtrics, anonymous link; survey offered in Dutch and French), after a video on
##citizen co-creation, compared 2 pairs of participation initiatives (tasks 1-2, profiles
##"Initiatief 1/2"), shown as a grid with 4 attributes in fixed order (question text of C1/C2:
##"Kanaal", "Niveau", "Impact", "Co-creatie fase"). Level text = the Qualtrics conjoint export
##fields <attribute-GUID>.<task>.<profile>_CBCONJOINT, matched to the attribute names through the
##[Field-...] placeholders in the C1/C2 question text:
##  attr_channel (Kanaal, a8aab806): Digitaal / Analoog / Hybride ...
##  attr_level   (Niveau, 4349b533): Op Vlaams niveau ... / Op lokaal niveau ...
##  attr_impact  (Impact, 456955f4): Adviserend ... / Bindend ...
##  attr_phase   (Co-creatie fase, 1ccb1002): Meedenken / Meebeslissen / Meediscussiëren ...
##The export stores the Dutch level text for every respondent, but 457 of the 1,140 respondents
##with a usable conjoint took the survey in French (Qualtrics UserLanguage FR) and saw a French
##version that is not saved (the level "Op Vlaams niveau" may even have read differently for
##them). Their displayed text is unknown, so ONLY the Dutch-language respondents are kept
##(683 respondents); the French-language respondents are dropped.
##Outcomes (same tasks, one table):
##  choice (C1/C2): "Hier zijn twee verschillende voorbeelden van participatie initiatieven te zien.
##    Aan welk participatie initiatief zou je het liefst willen deelnemen?" Initiatief 1 / 2, forced.
##  choice_results / choice_process / choice_trust (CONJNT_Q1_1..3 for task 1, CONJNT_Q2_1..3 for
##    task 2): "Vergelijk de twee hierboven getoonde initiatieven op basis van de volgende
##    stellingen." - "Welk van deze twee participatie initiatieven zal leiden tot de beste
##    resultaten?" / "In welk van de participatie initiatieven zal het proces het beste verlopen?"
##    / "Welk van deze twee participatie initiatieven zal het vertrouwen van deelnemers in de
##    betrokken overheid het meest versterken?" Initiatief 1 / Initiatief 2 / Geen verschil
##    (OPT-OUT: "no difference" = 0 on both profiles).
##Tasks with no answer to any of the four questions are omitted (respondents who left the survey);
##one respondent (unfinished, version 9) answered both forced choices but has no saved attribute
##levels; both tasks are dropped. A task answered only in part keeps NA in the unanswered outcome on both profiles.
##trial_design_version = vers_CBCONJOINT (Qualtrics conjoint design version).
##Covariates: the questionnaire exists in two parallel blocks, unprefixed and "M_"-prefixed (same
##questions; which block a respondent got is in cov_block, "M" or "main"; the meaning of the M
##block is not documented). Merged across blocks: cov_age (Vraag 1, "16 jaar" -> 16), cov_gender
##(Vraag 2: Man -> male, Vrouw -> female, X -> other, "Zeg ik liever niet" -> NA), cov_occupation
##(Vraag 3 answer text), cov_education (Vraag 4 answer text), cov_home_language (Vraag 5, labelled
##MIGRANT in the file, answer text), cov_video_check (TESTVRAAG "Wat studeert deze studente volgens
##de video?", answer text; correct answer not documented), cov_language (Qualtrics UserLanguage),
##cov_duration_sec (whole survey, Qualtrics Duration), cov_finished (Qualtrics Finished, 0/1).
##Dropped: ResponseId, panel ids (p_id, psid, linkname, l), REMARKS (free text), the other survey
##blocks (video intentions, attitudes), derived NPS groups.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_sav(file.path(raw, "d.sav"))
stopifnot(nrow(s) == 1686, !anyDuplicated(s$ResponseId))
q <- attr(s$C1, "label")
gu <- c(channel = "a8aab806", level = "4349b533", impact = "456955f4", phase = "1ccb1002")
nm <- c(channel = "Kanaal\\[Field-a8aab806", level = "Niveau\\[Field-4349b533", impact = "Impact\\[Field-456955f4", phase = "Co-creatie fase\\[Field-1ccb1002")
stopifnot(all(sapply(nm, grepl, x = q)))
col <- function(g, t, p) grep(paste0(g, "_.*\\.", t, "\\.", p, "_CBCONJOINT$"), names(s), value = TRUE)
lab <- function(x) as.character(as_factor(x, levels = "labels"))
pick <- function(a, b) fifelse(is.na(a), b, a)
age <- as.integer(sub(" jaar$", "", pick(lab(s$AGE), lab(s$M_AGE))))
sex <- pick(lab(s$SEX), lab(s$M_SEX))
cv <- data.table(
  cov_block = fifelse(!is.na(s$M_SEX) | !is.na(s$M_AGE), "M", fifelse(!is.na(s$SEX) | !is.na(s$AGE), "main", NA_character_)),
  cov_age = age, cov_gender = c(Man = "male", Vrouw = "female", X = "other")[sex],
  cov_occupation = pick(lab(s$OCCSTAT), lab(s$M_OCCSTAT)), cov_education = pick(lab(s$EDUCATION), lab(s$M_EDUCATION)),
  cov_home_language = pick(lab(s$MIGRANT), lab(s$M_MIGRANT)), cov_video_check = pick(lab(s$TESTVRAAG), lab(s$M_TESTVRAAG)),
  cov_language = as.character(s$UserLanguage), cov_duration_sec = as.numeric(s$Duration__in_seconds_),
  cov_finished = as.integer(s$Finished))
stopifnot(all(is.na(sex) | sex %in% c("Man", "Vrouw", "X", "Zeg ik liever niet")))
dd <- list()
for (t in 1:2) for (p in 1:2) {
  x <- data.table(src = seq_len(nrow(s)), task = t, profile = p,
                  choice = as.integer(zap_labels(s[[paste0("C", t)]]) == p))
  for (k in 1:3) {
    v <- as.integer(zap_labels(s[[paste0("CONJNT_Q", t, "_", k)]]))
    stopifnot(all(v %in% c(0:2, NA)))
    x[, paste0("choice_", c("results", "process", "trust")[k]) := as.integer(v == p)]
  }
  for (g in names(gu)) { cc <- col(gu[[g]], t, p); stopifnot(length(cc) == 1); x[, paste0("attr_", g) := as.character(s[[cc]])] }
  x[, trial_design_version := suppressWarnings(as.integer(as.character(s$vers_CBCONJOINT)))]
  dd[[length(dd) + 1]] <- cbind(x, cv)
}
d <- rbindlist(dd)
d <- d[!(is.na(choice) & is.na(choice_results) & is.na(choice_process) & is.na(choice_trust))]
blank <- d[, any(attr_channel == "" | attr_level == "" | attr_impact == "" | attr_phase == ""), .(src, task)][V1 == TRUE]
stopifnot(nrow(blank) == 2, uniqueN(blank$src) == 1)
d <- d[!blank, on = .(src, task)]
stopifnot(d[, all(attr_channel != "" & attr_level != "" & attr_impact != "" & attr_phase != "")],
          d[, .N, .(src, task)][, all(N == 2)])
for (o in c("choice", "choice_results", "choice_process", "choice_trust"))
  stopifnot(d[, .(n = sum(get(o)), na = sum(is.na(get(o)))), .(src, task)][, all((na == 0 & n <= 1) | na == 2)])
stopifnot(d[!is.na(choice), sum(choice), .(src, task)][, all(V1 == 1)])
d <- d[cov_language == "NL"]
stopifnot(uniqueN(d$src) == 683)
d[, id := match(src, sort(unique(src)))][, src := NULL]
d[, cov_language := NULL]
setcolorder(d, c("id", "task", "profile"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "reijnders_2025_cocreation.csv"))
