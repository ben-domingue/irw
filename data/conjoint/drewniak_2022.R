##ECLS (ECMO) initiation and withdrawal factorial surveys (physicians, Germany and Switzerland) from
##Drewniak, D., Brandi, G., Buehler, P. K., Steiger, P., Hagenbuch, N., Stamm-Balderjahn, S.,
##Schenk, L., Rosca, A., & Krones, T. (2022). Key factors in decision making for ECLS: A
##binational factorial survey. Medical Decision Making, 42(3), 313-325.
##https://doi.org/10.1177/0272989X211040815 (open access, PMC8918869)
##Data: Zenodo record 6805813 (doi:10.5281/zenodo.6805813), "Factorial Survey: Decision Making
##for Extracorporeal life support (ECLS)", CC BY 4.0. Files read: ECLS_Start.dta, ECLS_Stop.dta.
##No codebook ships; level wording and outcome wording are from the article (Methods, Tables 1-2,
##read via Europe PMC full text). Stata value labels give the short level names.
##Usage: Rscript drewniak_2022.R <dir holding ECLS_Start.dta and ECLS_Stop.dta> <output dir>
##
##TWO TABLES, one per scenario (different factor sets, separate designs and analyses in the
##article); the same respondents answered both (all 470 Stop ids are among the 513 Start ids;
##id is the same respondent in both tables):
##  drewniak_2022_ecls_start: willingness to INITIATE ECLS, 7 factors (age, circuit, treatment
##    costs, therapeutic goal, resources, comorbidities, neurological outcome).
##  drewniak_2022_ecls_stop: readiness to WITHDRAW running ECLS, 8 factors (age, circuit, days on
##    ECLS, withdrawal criteria, patient condition, therapeutic goal, comorbidities, neurological
##    outcome).
##FIXED BLOCKED DESIGN (article): D-efficient resolution IV fractions via SAS %mktex, 120
##initiation vignettes in 24 decks and 180 withdrawal vignettes in 36 decks of 5 (%mktblock);
##respondents randomly assigned to a deck. RESTRICTION: "the unrealistic combination of an 80-
##or 90-year-old patient bridged to transplant was excluded" (checked: never occurs), so age
##and therapeutic-goal shares are unequal. trial_deck = deck, trial_vignette = vid (vignette id).
##TASK ORDER IS NOT RECORDED: the files hold no display-order variable, and Stop rows are in
##arbitrary order. task = rank of vid within respondent (1-5), NOT the order shown; profile = 1
##(one vignette per task).
##N: the deposit holds 513 (Start) and 470 (Stop) respondent ids, more than the article's 420
##physicians: the article excluded respondents treating paediatric patients only (3), a medical
##student (1) and those not directly involved in ECLS (127) before analysis, and also counts
##1,713 / 1,711 initiation and 1,521 withdrawal ratings, fewer than here. The exclusions are not
##applied (no flag variable reproduces them); cov_user ("Direkt an ECMO Anwendung beteiligt?") and
##cov_work (professional field; 120 Start rows are perfusionists) allow approximating them.
##Rows with neither rating are omitted (Start 28, Stop 17), leaving 510 (2,453 vignettes) and
##467 (2,261) respondents; a missing single rating stays NA.
##Outcomes (article, "Dependent Measures"; the survey was in German, French and Italian, the
##article gives English translations), each 1 = "not correct at all" to 6 = "fully correct":
##  Start: rating_self "From my point of view, ECLS/ECMO should be used in this patient";
##         rating_clinic "In my clinic, ECLS/ECLS would be used in this patient".
##  Stop:  rating_self "From my point of view, the ECLS/ECLS treatment should be discontinued";
##         rating_clinic "In my clinic, the ECLS/ECLS treatment would be discontinued".
##  (higher = more agreement; for Stop that means more readiness to withdraw). The order of the
##  two statements was randomized between respondents: trial_statement_order (source order /
##  orderaus: 1 = self first, 2 = clinic first; value labels Selbst>Fremd, Fremd>Selbst).
##Attribute text: the English vignette wording of article Tables 1-2 (a translation; the German,
##French and Italian display text is not deposited), matched to the Stata value labels; the
##table's own "..." ellipses are dropped. Age is "35-year-old" etc.; days are "2 days ago." etc.
##Covariates: cov_country (Germany/Switzerland), cov_gender (sex: Weiblich -> female, Männlich ->
##male), cov_age (ageresp, "Alter Befragte", as deposited), cov_clinic_group (kliniknew, an
##anonymized hospital-group number), cov_finished (V10), and every other respondent item as
##answer text from the value labels (German) or as stored when unlabelled (guide*, edu*, fach*,
##erwpul..paedkard 0/1 ticks; berufserf years). Dropped: StartDate/EndDate (V8, V9), consent
##(Q001), edustr (free-text specialty name), birth (year of birth; its value labels in
##ECLS_Start.dta are a mislabelled copy of the age-factor labels, and ageresp already holds age).
##No survey weight.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(h, v) { x <- as.character(as_factor(h[[v]], levels = "labels")); x[is.na(h[[v]])] <- NA; trimws(x) }
recode <- function(x, map) { stopifnot(all(x %in% names(map))); unname(map[x]) }
como <- c("No comorbidities" = "There are no other comorbidities.",
          "Pancreatic CA" = "Six months ago, a Kausch-Whipple operation with curative intent was performed on the patient due to a pancreas CA.",
          "Colon carcinoma" = "The patient has a solitary metastatic colon carcinoma.",
          "Kidney failure" = "The patient has had kidney failure requiring dialysis for 6 months.")
neuro <- c("Inconspicuous" = "The patient's central neurological findings are normal.",
           "Damage possible" = "Severe central neurological damage cannot be ruled out.",
           "Damage certain" = "Severe central neurological damage is assumed to be certain.")
transplant <- "The patient is urgently listed for a lung/heart transplant (U)."
skip <- c("id", "vid", "V8", "V9", "V10", "country", "kliniknew", "Q001", "order", "orderaus", "self", "other", "deck",
          "age", "days", "condition", "cost", "criteria", "zustand", "bridge", "resource", "como", "neuro",
          "sex", "birth", "ageresp", "edustr")
build <- function(f, scen) {
  h <- read_dta(file.path(raw, f))
  keep <- !(is.na(h$self) & is.na(h$other))
  h <- h[keep, ]
  d <- data.table(id = as.integer(h$id), vid = as.integer(h$vid), profile = 1L,
                  rating_self = as.integer(h$self), rating_clinic = as.integer(h$other),
                  attr_age = paste0(lab(h, "age"), "-year-old"))
  if (scen == "start") {
    d[, attr_circuit := recode(lab(h, "condition"), c("Severe ARDS" = "with severe ARDS", "Cardiogenic shock" = "in cardiogenic shock"))]
    d[, attr_costs := recode(lab(h, "cost"), c(covered = "The treatment costs are covered.", "not covered" = "The treatment costs are not covered."))]
    d[, attr_goal := recode(lab(h, "bridge"), c(Decision = "The cause of the lung/heart failure is unknown and a final treatment plan has not yet been established.",
        Recovery = "The patient is not a transplant candidate. The organ damage appears to be reversible, but drug therapies are inadequate.", Transplant = transplant))]
    d[, attr_resources := recode(lab(h, "resource"), c("No resource problem" = "There are currently no problems with the resources to operate ECLS/ECMO on your ward.",
        "Resource scarcity" = "There is currently a shortage of beds on your ward."))]
    ord <- "order"
  } else {
    d[, attr_circuit := recode(lab(h, "condition"), c("Severe ARDS" = "VV-ECLS/ECMO due to severe ARDS", "Cardiogenic shock" = "VA-ECLS/ECMO due to cardiogenic shock"))]
    d[, attr_days := paste0(lab(h, "days"), " days ago.")]
    d[, attr_criteria := recode(lab(h, "criteria"), c("Not defined" = "No criteria for ECLS/ECMO withdrawal have been defined.",
        "Defined but not fulfilled" = "Withdrawal criteria were defined before ECLS/ECMO was started. However, these have not yet been fulfilled.",
        "Defined and fulfilled" = "Withdrawal criteria were defined before ECLS/ECMO was started. The criteria are fulfilled."))]
    d[, attr_condition := recode(lab(h, "zustand"), c(Improved = "The patient's condition has improved since ECLS/ECMO was started.",
        Worsened = "The patient's condition has worsened since ECLS/ECMO was started.", Unchanged = "The patient's condition has not changed since ECLS/ECMO was started."))]
    d[, attr_goal := recode(lab(h, "bridge"), c(Decision = "The initial indication for ECLS/ECMO therapy was to determine the cause of the lung/heart failure and to define a final therapy concept for the patient.",
        Recovery = "The patient is not a transplant candidate. The organ damage appeared to be reversible, but drug therapies were inadequate.", Transplant = transplant))]
    ord <- "orderaus"
  }
  d[, attr_comorbidities := recode(lab(h, "como"), como)][, attr_neurological := recode(lab(h, "neuro"), neuro)]
  d[, trial_deck := as.integer(h$deck)][, trial_vignette := vid][, trial_statement_order := as.integer(h[[ord]])]
  d[, cov_country := lab(h, "country")]
  sx <- lab(h, "sex"); stopifnot(all(sx %in% c("Weiblich", "Männlich", NA)))
  d[, cov_gender := c(Weiblich = "female", "Männlich" = "male")[sx]]
  d[, cov_age := as.integer(h$ageresp)][, cov_clinic_group := as.integer(h$kliniknew)][, cov_finished := as.integer(h$V10)]
  for (v in setdiff(names(h), skip)) {
    if (is.labelled(h[[v]])) d[, paste0("cov_", v) := lab(h, v)] else d[, paste0("cov_", v) := as.numeric(h[[v]])]
  }
  d[, task := frank(vid, ties.method = "first"), id][, vid := NULL]
  setcolorder(d, c("id", "task", "profile"))
  stopifnot(!anyDuplicated(d[, .(id, task)]), d[, all(rating_self %in% c(1:6, NA)) && all(rating_clinic %in% c(1:6, NA))],
            !anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, .N, id][, all(N <= 5)],
            !d[attr_age %in% c("80-year-old", "90-year-old"), any(attr_goal == transplant)],
            d[, uniqueN(trial_deck), id][, all(V1 == 1)], all(d$trial_statement_order %in% 1:2))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("drewniak_2022_ecls_", scen, ".csv")))
}
build("ECLS_Start.dta", "start")
build("ECLS_Stop.dta", "stop")
