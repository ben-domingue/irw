##Civil servants' error-handling paired vignette choice experiment (Germany) from
##Fischer, C., & Weißmüller, K. S. (2024). What determines civil servants' error response? Evidence
##from a conjoint experiment. American Review of Public Administration, 54(8), 747-770.
##https://doi.org/10.1177/02750740241267941
##Data: OSF project "Handling Errors in Public Organizations" (https://osf.io/j38p6/,
##doi:10.17605/OSF.IO/J38P6), CC BY 4.0 (node licence). Files read: data/2024_Error_Handling_RawData_
##for_STATA.dta (raw respondent file, saved as raw.dta), data/2024_Error_Handling_AnalyticalData_for_R.csv
##(only to verify the design transcription), metadata/operationalization_OSF.docx (vignette and level
##text, English and German). Read as text, not run: code/2024_STATA_Error_Handling_Analysis.do,
##code/2024_R_script_Error_Handling_Analysis.R.
##Usage: Rscript fischer_2024.R <raw dir> <output dir>
##
##276 German civil servants (online survey; the authors compute age as 2021 - birth year). After a
##vignette (a municipal employee, Frau or Herr Müller, realises a construction quote was left out of a
##tender recommendation; German text in the docx, Appendix A.2), each respondent saw 4 of 18 fixed
##choice sets, each of two options (A = profile 1, B = profile 2). Each option combines three error
##characteristics (A1 error type: skill-, rule- or knowledge-based; A2 party aggrieved: internal /
##external; A3 error magnitude: low / high costs) with the protagonist's response (B1 communication:
##hiding / reporting; B2 action: ignoring / correcting). The 18 sets are a FIXED design, transcribed
##from the .do file's "replace e_type_0 = 1 if task_A==1 & (tasknumber==...)" lines (every set and
##option gets exactly one level per attribute); the authors' analytic CSV keeps only the chosen
##option's levels and matches the transcription in all 1,104 rows (stopifnot below) for party,
##magnitude and action -- EXCEPT the error-type labels: the .do labels e_type_0 "skill-based" and
##e_type_1 "rule-based" (as does the docx coding, [0=skill-based] [1=rule-based]), while the R
##analytic CSV calls the same rows "rulebased" and "skillbased" (one-to-one swap; knowledge-based
##agrees). This table follows the .do + docx; the CSV (used for the R figures) may carry swapped
##labels, or the .do may. UNRESOLVED: the two deposit files disagree. Which 4 sets a
##respondent saw is random (265 distinct sets of 4; no blocks); display order is NOT recorded:
##task = 1..4 in ascending set number (task_source inferred), trial_choiceset = the set (1-18).
##Between subjects, the protagonist is "Frau Müller" (raw columns BG..BX, 139 respondents) or "Herr
##Müller" (CE_ChoiceTask*_1, 137); stored as attr_protagonist (same on both profiles) and substituted
##into the level text. Level text = the German original (docx table B.2; the bracketed level codes and
##line breaks removed, sentences joined by a space). English translation in docx table B.1.
##Outcome: choice = the option chosen (raw code 1 = A, 2 = B per the .do file). The question wording
##is not in the deposit or the docx (paraphrased in design_outcomes); forced choice, no opt-out.
##Dropped respondents: 3 who answered only 3 sets (rows 26, 48, 74, dropped by the authors too).
##N: 276 respondents, 1,104 observations = the article's abstract (N = 276, Obs. = 1,104).
##Covariates (labels from the .do file's label define lines): cov_gender (1 male, 2 female, 3 diverse ->
##male/female/other), cov_birth_year (year code + 1901, the .do's recode 105 = 2006 ...), cov_education
##and cov_jobtraining (German label text per the .do's second label define), cov_tenure (befristet
##tarif / unbefristet tarif / verbeamtet), cov_pay_grade (eingrupp: mittleren / gehoben / höheren
##Dienst), cov_leader (Führungskraft / keine Führungskraft), cov_streetlevel (Klientenkontakt / Kein
##Klientenkontakt), cov_fulltime (workhours 1 = full time -> 1, else 0, as the .do), cov_workexp_all /
##cov_workexp_public (years, as typed; "13,5" -> 13.5), cov_duration_sec (survey duration),
##cov_realism (scenario realism rating 1-7, from the version-specific column; wording not deposited),
##scale items as exported, 1-7 (Appendix C: 1 = totally disagree, 7 = totally agree):
##cov_psm_1..12, cov_ieo_1..10, cov_md_1..8, cov_eac_1..11; cov_emc1_*_code / cov_emc2_*_code keep the
##raw export codes (1,2,3,5,6,7,8: Qualtrics codes skip 4; mapping to the 7-point scale not documented).
##Dropped: attention-test items (no key), the PD risk items (codes 1/3, undocumented), all *_TEXT free
##text. No direct identifiers in the deposited raw file.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "raw.dta"))))
stopifnot(nrow(s) == 279L)
s[, rid := .I]
s <- s[!rid %in% c(26L, 48L, 74L)]
# --- fixed design (from the .do file): level index per set for option A and B
lv <- function(A, B) list(A = A, B = B)
setlv <- function(spec) { x <- rep(NA_integer_, 18); for (k in names(spec)) x[spec[[k]]] <- as.integer(k); stopifnot(!anyNA(x)); x }
des <- list(
  type = lv(setlv(list("0" = c(1,4,7,8,10,13,16), "1" = c(2,5,9,12,14,17), "2" = c(3,6,11,15,18))),
            setlv(list("0" = c(9,11,14,17,18), "1" = c(1,3,4,7,13,15), "2" = c(2,5,6,8,10,12,16)))),
  party = lv(setlv(list("0" = c(1,2,7,8,9,11,12,13,14,15), "1" = c(3,4,5,6,10,16,17,18))),
             setlv(list("0" = c(3,4,5,6,12,16,17,18), "1" = c(1,2,7,8,9,10,11,13,14,15)))),
  magnitude = lv(setlv(list("0" = c(1,2,4,5,6,8,9,11,13,14,15,16,17,18), "1" = c(3,7,10,12))),
                 setlv(list("0" = c(7,10,12,14), "1" = c(1,2,3,4,5,6,8,9,11,13,15,16,17,18)))),
  communication = lv(setlv(list("0" = c(1,2,4,5,6,7,10,13,14,15,16,17,18), "1" = c(3,8,9,11,12))),
                     setlv(list("0" = c(1,2,3,4,5,8,9,12,15,16,18), "1" = c(6,7,10,11,13,14,17)))),
  action = lv(setlv(list("0" = c(1,2,4,5,6,10), "1" = c(3,7,8,9,11,12,13,14,15,16,17,18))),
              setlv(list("0" = c(3,8,12,15,16,18), "1" = c(1,2,4,5,6,7,9,10,11,13,14,17)))))
txt <- list(
  type = c("[X] Müller hatte das Angebot in eine hierfür vorgesehene Datenbank übertragen, dabei aber den falschen Vergabeprozess ausgewählt, sodass das Angebot im Weiteren nicht sichtbar war. Das bedeutet, es war ein Bedienfehler.",
           "[X] Müller hatte sich nicht darangehalten, dass normalerweise die Angebote direkt bei Eingang in eine Datenbank eingepflegt werden sollen. Das bedeutet, es wurde gegen das formale Vorgehen verstoßen.",
           "[X] Müller wusste nicht, dass die Verfahrensweise vorsieht, dass jedes Angebot direkt in einer Datenbank abgelegt werden muss. Das bedeutet, [X] Müller wusste es eben nicht besser."),
  party = c("Durch das übersehene Angebot entstehen möglicherweise Mehrkosten für die Stadtverwaltung, weil das übersehene Angebot möglicherweise wirtschaftlicher gewesen wäre. [X] Müllers Abteilung hat durch die Mehrkosten bei dieser Sanierung im Haushaltsjahr weniger Mittel für andere Projekte zur Verfügung.",
            "Das Unternehmen, das das übersehene Angebot abgegeben hat, hatte mit der Erstellung dieses Angebots und den zugrundliegenden Planungen mit großer Sicherheit einen mehrtägigen Arbeitsaufwand."),
  magnitude = c("Das übersehene Angebot ist allerdings nicht das beste und wäre insofern wahrscheinlich sowieso nicht ausgewählt worden.",
                "Das übersehene Angebot ist eines der besten und hätte den Auftrag erhalten können."),
  communication = c("[X] Müller teilt niemandem mit, dass ein Angebot übersehen wurde.",
                    "[X] Müller informiert bei nächster Gelegenheit die anderen Beteiligten des Vergabeverfahrens über das übersehene Angebot."),
  action = c("[X] Müller bezieht das übersehene Angebot nicht noch nachträglich mit ein.",
             "[X] Müller bezieht das übersehene Angebot noch nachträglich mit ein und erstellt eine neue Empfehlung."))
fcols <- c("BG","BH","BI","BJ","BK","BL","BM","BN","BO","BP","BQ","BR","BS","BT","BU","BV","BW","BX")
L <- list()
for (k in 1:18) {
  m <- s[[paste0("CE_ChoiceTask", k, "_1")]]; f <- s[[fcols[k]]]
  stopifnot(!(m != "" & f != ""))
  v <- ifelse(m != "", m, f); w <- v != ""
  stopifnot(v[w] %in% c("1", "2"))
  if (!any(w)) next
  for (p in 1:2) {
    d <- data.table(rid = s$rid[w], trial_choiceset = k, profile = p, choice = as.integer(v[w] == as.character(p)),
                    attr_protagonist = ifelse(m[w] != "", "Herr Müller", "Frau Müller"))
    for (an in names(des)) {
      code <- des[[an]][[p]][k]
      d[, paste0("attr_", an) := mapply(function(x) txt[[an]][code + 1L], seq_len(.N))]
      d[, paste0("attr_", an) := mapply(function(t, who) gsub("[X]", sub(" Müller", "", who), t, fixed = TRUE), get(paste0("attr_", an)), attr_protagonist)]
      d[, paste0("code_", an) := code]
    }
    L[[length(L) + 1]] <- d
  }
}
d <- rbindlist(L)
stopifnot(d[, .N, rid][, all(N == 8)], uniqueN(d$rid) == 276L, d[, sum(choice), .(rid, trial_choiceset)][, all(V1 == 1)])
# verify against the authors' analytic file (chosen option's levels)
an <- fread(file.path(raw, "analytic.csv"))
ch <- d[choice == 1]
chk <- merge(ch, an[, .(rid = id, trial_choiceset = tasknumber, errorttype, partyaggr, magnitude, correcting)],
             by = c("rid", "trial_choiceset"))
stopifnot(nrow(chk) == 1104L,
          chk$errorttype == c("rulebased", "skillbased", "knowledgebased")[chk$code_type + 1],  # SWAPPED in the CSV, see header
          chk$partyaggr == c("internal", "external")[chk$code_party + 1],
          chk$magnitude == c("low_harm", "high_harm")[chk$code_magnitude + 1],
          chk$correcting == c("ignoring", "correcting")[chk$code_action + 1])
d[, grep("^code_", names(d), value = TRUE) := NULL]
d[, task := frank(trial_choiceset, ties.method = "dense"), rid]
# covariates
num <- function(x) suppressWarnings(as.numeric(sub(",", ".", x)))
lab <- function(x, map, na_ok = character()) { r <- unname(map[as.character(x)]); stopifnot(!anyNA(r[!is.na(x) & x != "" & !x %in% na_ok])); r }
cv <- s[, .(rid,
  cov_gender = lab(gender, c("1" = "male", "2" = "female", "3" = "other")),
  cov_birth_year = as.integer(num(year) + 1901),
  cov_education = lab(education, c("5" = "Volks-/Hauptschulabschluss", "8" = "Mittlere Reife, Realschulabschluss (Fachschulreife)",
                                   "11" = "Polytechnische Oberschule (POS)", "2" = "Fachhochschulreife", "1" = "Abitur, Hochschulreife",
                                   "7" = "Anderer Schulabschluss")),
  cov_jobtraining = lab(jobtraining, c("5" = "Berufsausbildung", "8" = "Meisterbrief",
                                       "11" = "(Fach-)Hochschulstudium: Bachelor, Master, Diplom, Staatsexamen",
                                       "1" = "Abitur (Hochschulreife) oder Berufsausbildung mit Abitur", "2" = "Promotion, Habilitation",
                                       "7" = "Anderer Berufsabschluss"), na_ok = "12"),
  cov_tenure = lab(tenure, c("1" = "befristet tarif", "2" = "unbefristet tarif", "3" = "verbeamtet")),
  cov_pay_grade = lab(eingrupp, c("1" = "mittleren Dienst (bis E8/A8)", "2" = "gehoben Dienst (bis E12/A12)", "3" = "höheren Dienst (ab E13/A13)")),
  cov_leader = lab(leader, c("1" = "Führungskraft", "2" = "keine Führungskraft")),
  cov_streetlevel = lab(streetlevel, c("1" = "Klientenkontakt", "2" = "Kein Klientenkontakt")),
  cov_fulltime = as.integer(workhours == "1"),
  cov_workexp_all = num(workexp_2), cov_workexp_public = num(workexp_4),
  cov_duration_sec = num(Durationinseconds),
  cov_realism = as.integer(num(ifelse(treatment_male != "", treatment_male, Treatment_intro_f))))]
for (sc in list(c("PSM", 12, "psm"), c("IEO", 10, "ieo"), c("MD", 8, "md"), c("EAC", 11, "eac")))
  for (i in seq_len(as.integer(sc[2]))) { x <- as.integer(num(s[[paste0(sc[1], "_", i)]])); stopifnot(x %in% c(1:7, NA)); cv[, paste0("cov_", sc[3], "_", i) := x] }
for (g in 1:2) for (i in 1:8) cv[, paste0("cov_emc", g, "_", i, "_code") := as.integer(num(s[[paste0("EMC", g, "_", i)]]))]
d <- merge(d, cv, by = "rid")
d[, id := match(rid, sort(unique(rid)))][, rid := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "attr_protagonist", "attr_type", "attr_party", "attr_magnitude",
                 "attr_communication", "attr_action", "trial_choiceset"))
setnames(d, c("attr_type", "attr_party"), c("attr_error_type", "attr_party_aggrieved"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "fischer_2024_error_handling.csv"))
