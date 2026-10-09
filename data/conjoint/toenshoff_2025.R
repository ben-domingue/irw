##Candidate and climate-policy-plan conjoints (Germany, 2021 federal election) from
##Toenshoff, C. L., Mares, I., & Scheve, K. (2025). Compensation, beliefs in state intervention, and
##support for the energy transition. Comparative Political Studies.
##https://doi.org/10.1177/00104140251328009
##Replication data: Harvard Dataverse doi:10.7910/DVN/A0HFY8, CC0 1.0. Files read (Dataverse "original
##format" downloads): rawdata.csv (Qualtrics export, datafile 10818645), weights_data.csv (10818641).
##Read as text only: read_me.txt, preprocessing_data.R, creating_survey_weights.R,
##analysis_candidate_conjoint_final.R, analysis_policy_plan_experiment_final.R. The authors' long files
##(data.cand.final.tab, data.wtp.final.tab) were used only to check this build (same attributes and
##choices); they carry English short labels and no task/profile columns.
##Usage: Rscript toenshoff_2025.R <dir holding rawdata.csv and weights_data.csv> <output dir>
##
##German online panel, fielded 20-26 Sep 2021 (Qualtrics StartDate), survey in German (UserLanguage DE).
##Sample = the authors' analysis sample (preprocessing_data.R): consented, passed the energy attention
##question (attention2 == "Atomkraft"; 57.6% pass rate per the authors) and finished: 2,191 responses.
##Three panel ids (tic) occur twice with different ResponseIds and different answers; like the authors
##(who cluster on ResponseId) each response is kept as its own respondent. The paper's N could not be
##checked (article not accessible); the authors' cleaned files also hold 2,191 respondents.
##Two experiments with different attribute sets -> two tables, same respondents and ids:
##  toenshoff_2025_energy_candidates: 5 tasks x 2 hypothetical Bundestag candidates, 5 attributes
##    (gender, party, energy policy, social/pension policy, migration policy). choice: "Welche dieser
##    beiden Kandidaten/Kandidatinnen würden Sie in der kommenden Bundestagswahl eher wählen? Bitte wählen
##    Sie einen Kandidaten/eine Kandidatin aus, selbst wenn Ihnen keine der beiden Optionen gefällt."
##    Forced choice (Kandidat/in 1 / 2).
##  toenshoff_2025_climate_plans: 5 tasks x 2 climate policy plans, 4 attributes (cost per year,
##    expected effectiveness, compensation, competitiveness measure). choice: "Welchen Plan würden Sie
##    bevorzugen?" Forced choice (Plan 1 / 2). Before this conjoint each respondent was randomized to one
##    of three vignettes (willingnesstopay 1/2/3); stored as trial_vignette with the authors' names from
##    analysis_policy_plan_experiment_final.R ("Control", "Compensation Treatment", "Carbon Tax Treatment").
##    The vignette texts are not in the deposit.
##Task = the loop index of the Qualtrics loop (1..5, prefix of <k>_E1_candchoice / <k>_E4_prefplan and
##choice<k>_*), profile = suffix 1/2 of the embedded fields (= Kandidat/in 1/2, Plan 1/2): RECORDED.
##Attribute text = the German embedded-data strings that were piped into the profiles (leading and
##trailing blanks trimmed; e.g. " CDU/CSU", " Bündnis90/ Grünen "). The spelling slip "bestehenen" in a
##compensation level is kept as displayed. Attribute display order and any randomization restrictions
##are not documented in the deposit (every pair of levels occurs). Level weights OBSERVED for the candidates:
##energy policy "Unterstützt eine Weiterführung ... im derzeit vorgesehenen Tempo" in 40% of profiles, the
##three other levels 20% each; all other attributes near-uniform. Check: energy-policy AMCEs from this
##table equal the authors' data.cand.final.tab estimates (-0.049 slow down, +0.046 low-income subsidies vs
##current speed).
##Covariates (raw export, German answer text as stored): cov_gender (gender, "Was ist Ihr Geschlecht?":
##weiblich -> female, männlich -> male, anderes -> other; mapping by the answer text), cov_birth_year (D1,
##free-typed "Was ist Ihr Geburtsjahr?": only 4-digit years 1900-2005 kept; two full dates of birth and
##other implausible entries set NA), cov_education (D3, highest vocational qualification), cov_region (D5,
##Bundesland), cov_income (income, monthly household net income band), cov_left_right (left_right_4,
##0 = links ... 10 = rechts), cov_vote_intention_2021 (party_2021_2, intended second vote 2021; vote, not
##party identification), cov_duration_sec (Duration (in seconds), whole survey),
##cov_attention_pass_mv_cand / cov_attention_pass_mv_plan (authors' candidateattention / wtpattention:
##1 = at least 2 of 3 mock-vignette quiz items right AND the mock vignette came before that experiment in
##the randomized block order FL_112_DO; rebuilt with the authors' code), cov_survey_weight (authors'
##raking weight from weights_data.csv: gender, age group, income quintile; joined on panel id, identical
##for the 3 duplicated ids).
##Dropped: ResponseId and tic (platform/panel ids; re-keyed to integers in file order), postcode
##(PII), DB2 free-text comments, timing, coal-exit vignette experiment
##(single-factor), authoritarianism and work items, the authors' derived indices and dummies.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "rawdata.csv"), encoding = "UTF-8", colClasses = "character")
r <- r[-(1:2)]
r <- r[Consent == "Ja, ich nehme an der Studie teil" & attention2 == "Atomkraft" & Finished == "TRUE"]
stopifnot(nrow(r) == 2191, uniqueN(r$ResponseId) == 2191, all(r$UserLanguage == "DE"))
r[, id := seq_len(.N)]
## covariates
w <- fread(file.path(raw, "weights_data.csv"))
stopifnot(w[, uniqueN(weights), tic][, all(V1 == 1)])
w <- unique(w)
r[, cov_survey_weight := w$weights[match(tic, w$tic)]]
stopifnot(!anyNA(r$cov_survey_weight))
stopifnot(all(r$gender %in% c("weiblich", "männlich", "anderes")))
by <- suppressWarnings(as.integer(ifelse(grepl("^[0-9]{4}$", r$D1), r$D1, NA)))
by[!is.na(by) & (by < 1900 | by > 2005)] <- NA
mv <- (r$MVQ1 == "Reduktion von Schwefel") + (r$MVQ2 == "Internationale Seeschifffahrts-Organisation") +
  (r$MVQ3 == "Erhöhte Meeresverschmutzung")
ord <- strsplit(r$FL_112_DO, "[|]")
pos <- function(p) vapply(ord, function(x) grep(p, x)[1], 1L)
mvp <- pos("Mock_Vignette")
nz <- function(x) { x <- trimws(x); fifelse(x == "", NA_character_, x) }
cv <- data.table(id = r$id,
  cov_gender = c(weiblich = "female", "männlich" = "male", anderes = "other")[r$gender],
  cov_birth_year = by, cov_education = nz(r$D3), cov_region = nz(r$D5), cov_income = nz(r$income),
  cov_left_right = suppressWarnings(as.integer(r$left_right_4)), cov_vote_intention_2021 = nz(r$party_2021_2),
  cov_duration_sec = as.integer(r[["Duration (in seconds)"]]),
  cov_attention_pass_mv_cand = as.integer(mv > 1 & mvp < pos("ExperimentCandidates")),
  cov_attention_pass_mv_plan = as.integer(mv > 1 & mvp < pos("ConditionalWillingnesstoPayVignette/ConjointExperiment")),
  cov_survey_weight = r$cov_survey_weight)
stopifnot(all(cv$cov_left_right %in% c(0:10, NA)), !anyNA(cv$cov_attention_pass_mv_cand))
## long builder
build <- function(qcol, opt, attrs) {
  L <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
    d <- data.table(id = r$id, task = t, profile = p,
                    choice = as.integer(r[[sprintf("%d_%s", t, qcol)]] == opt[p]))
    for (nm in names(attrs)) d[, paste0("attr_", nm) := trimws(r[[sprintf("choice%d_%s%d", t, attrs[[nm]], p)]])]
    d }))))
  stopifnot(L[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(L), L[, all(sapply(.SD, function(x) all(x != ""))), .SDcols = patterns("^attr_")])
  L }
cand <- build("E1_candchoice", c("Kandidat/in 1", "Kandidat/in 2"),
              list(gender = "gender", party = "Partei", energy_policy = "Energiepolitik",
                   social_policy = "Sozialpolitik", migration_policy = "Migrationspol"))
plan <- build("E4_prefplan", c("Plan 1", "Plan 2"),
              list(cost = "Kosten", effectiveness = "Effektivitat", compensation = "Entschadigung",
                   competition = "Wettbewerbsforderung"))
stopifnot(cand[, uniqueN(attr_party)] == 6, cand[, uniqueN(attr_energy_policy)] == 4, plan[, uniqueN(attr_compensation)] == 5,
          plan[, uniqueN(attr_cost)] == 4)
arm <- c("1" = "Control", "2" = "Compensation Treatment", "3" = "Carbon Tax Treatment")[r$willingnesstopay]
stopifnot(!anyNA(arm))
plan[, trial_vignette := arm[id]]
cand <- merge(cand, cv[, !"cov_attention_pass_mv_plan"], by = "id")
plan <- merge(plan, cv[, !"cov_attention_pass_mv_cand"], by = "id")
setorder(cand, id, task, profile); setorder(plan, id, task, profile)
fwrite(cand, file.path(out, "toenshoff_2025_energy_candidates.csv"))
fwrite(plan, file.path(out, "toenshoff_2025_climate_plans.csv"))
