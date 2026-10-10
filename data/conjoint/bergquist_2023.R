##COVID-recovery / climate policy-package conjoints (US, Canada, US follow-up) from
##Bergquist, P., de Roche, G., Lachapelle, E., Mildenberger, M., & Harrison, K. (2023). The
##politics of intersecting crises: The effect of the COVID-19 pandemic on climate policy
##preferences. British Journal of Political Science, 53(2), 707-716 (online 2022).
##https://doi.org/10.1017/S0007123422000266
##Replication data: Harvard Dataverse doi:10.7910/DVN/LULYEB, CC0 1.0. Files read:
##conjoint_us.csv, conjoint_canada.csv, conjoint2_us.csv (Qualtrics exports: row 1 = question
##text, row 2 = ImportId, then one row per respondent) and readme-1.txt. analysis.R read as
##text, not run.
##Usage: Rscript bergquist_2023.R <dir holding the three csv files> <output dir>
##
##Three tables, one per fielding, as in the paper (each country and the follow-up are
##estimated separately, and the level text differs: "every American" vs "every Canadian",
##costs $500 billion-$3 trillion in the US vs $25-150 billion in Canada; the follow-up adds a
##sixth attribute, COVID-19 management):
##  bergquist_2023_covid_climate_us   conjoint_us.csv, 5 attributes
##  bergquist_2023_covid_climate_ca   conjoint_canada.csv, 5 attributes; 116 of the respondents
##      took the survey in French (cov_user_language FR-CA) but the stored level text is English
##      for everyone; the French screen text is not deposited.
##  bergquist_2023_covid_climate_us2  conjoint2_us.csv, 6 attributes (follow-up survey)
##Each respondent saw 3 tasks of two packages ("Policy A"/"Policy B"). Layout (readme):
##G-<task>-<k> = name of the attribute in row k, G-<task>-<profile>-<k> = its level. Attribute
##row order was randomized once per respondent (identical in all 3 tasks for every respondent,
##checked); attrpos_* holds the row (1-5 or 1-6). "None" is displayed text and is kept.
##Outcomes (export question text):
##  choice: "Which policy package would you prefer?" (Q260/Q266/Q269; con_choice_t), 1 = Policy
##          A, 2 = Policy B; no opt-out option, but a respondent could skip it (choice NA).
##  rating: "On the scale below, tell us how strongly you support each of these two options with
##          0 corresponding to no support and 100 corresponding to full support." - Policy A/B
##          (Q261_/Q267_/Q270_, con_rate_t_), 0-100.
##A task is kept when its choice or at least one rating was answered; choice stays NA on the few
##tasks with ratings but no choice, and a profile row with neither choice nor rating is omitted. Respondents who never reached the conjoint (no G- values;
##consent declined or broke off) are dropped. trial_page_sec is the Qualtrics page-submit time of
##that task (Q272/Q248/Q273; Q135/Q139/Q143), which the authors sum for their attention split.
##Covariates (export text where the export has text): cov_duration_sec (survey duration),
##climate worry / priority (cov_climate_worry, cov_climate_priority, answer
##text), cov_expcheck / cov_exprecheck (answer to the manipulation check of the earlier text
##experiment, "Exponential growth" = the topic of the text), trial_climateexperiment (arm A/B/C
##of that earlier survey experiment; arm labels not in the deposit), CA: cov_ideology (ideo_1,
##0 far left - 10 far right), cov_user_language. Panel-supplied codes with no codebook in the
##deposit keep their codes: cov_age (years), cov_gender_code, cov_ethnicity_code,
##cov_hispanic_code, cov_education_code (-3105 as stored), cov_political_party_code (1-10; the
##authors' analysis.R collapses 1,2,3,6 = Democrat, 4,7 = Independent, 5,8,9,10 = Republican),
##US2 also cov_hhi_code. US2 asked gender, race/ethnicity and year of birth itself: cov_gender
##(QID4 text: Female/Male/Other -> female/male/other), cov_raceeth (text; "Prefer not to answer"
##-> NA), cov_birth_year (yob).
##Dropped: ResponseId (re-keyed to 1..n in file order), zip (5-digit ZIP code: PII), the consent
##item, the attribute-name columns (kept as attrpos_*).
##No survey weight in the deposit.
##Counts: 1,695 US respondents reached the conjoint (article: US, Lucid, April 2021, n = 1,695),
##1,642 answered at least one task and are in the table; Canada 1,058 (article: Lucid, June 2021,
##n = 1,058), 1,058 in the table; US follow-up (article fn. 2, n not given in the main text) 1,040
##reached the conjoint, 1,022 in the table. Spot check: the choice AMCEs of the three climate-action
##levels vs "None" are positive in all three tables (US +.06/+.11/+.10, Canada +.09/+.18/+.13),
##the direction of the article's Figure 2 (numbers not compared).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) { d <- fread(file.path(raw, f), colClasses = "character")[-(1:2)]; names(d) <- make.unique(names(d)); d }
nz <- function(x) fifelse(trimws(x) == "", NA_character_, x)
build <- function(d, k, ch, rt, pg, cov) {
  d <- d[`G-1-1-1` != ""]
  d[, rid := .I]
  L <- rbindlist(lapply(1:3, function(t) rbindlist(lapply(1:2, function(p) {
    x <- data.table(id = d$rid, task = t, profile = p,
                    choice = as.integer(d[[ch[t]]] == as.character(p)) , chans = d[[ch[t]]] != "",
                    rating = suppressWarnings(as.integer(d[[rt(t, p)]])), trial_page_sec = as.numeric(nz(d[[pg[t]]])))
    for (j in 1:k) {
      nm <- d[[sprintf("G-%d-%d", t, j)]]
      for (an in unique(nm)) { w <- nm == an
        col <- paste0("attr_", gsub("[^a-z0-9]+", "_", tolower(an)))
        x[w, (col) := d[[sprintf("G-%d-%d-%d", t, p, j)]][w]]
        x[w, (sub("^attr_", "attrpos_", col)) := j] }
    }
    x }))))
  L[chans == FALSE, choice := NA_integer_]
  keep <- L[, .(k = any(chans) | any(!is.na(rating))), .(id, task)][k == TRUE, .(id, task)]
  L <- L[keep, on = .(id, task)][, chans := NULL]
  L <- L[!(is.na(choice) & is.na(rating))]
  stopifnot(L[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], L[, uniqueN(is.na(choice)), .(id, task)][, all(V1 == 1)],
            L[, all(is.na(rating) | rating %in% 0:100)])
  ac <- grep("^attr_", names(L), value = TRUE); stopifnot(length(ac) == k, !anyNA(L[, ..ac]), all(L[, ..ac] != ""))
  stopifnot(L[, uniqueN(attrpos_cost), .(id)][, all(V1 == 1)])
  cv <- cov(d); L <- cbind(L, cv[L$id])
  L[, id := match(id, sort(unique(id)))]
  setcolorder(L, c("id", "task", "profile", "choice", "rating", ac, sort(grep("^attrpos_", names(L), value = TRUE))))
  setorder(L, id, task, profile); L
}
cov_common <- function(d) data.table(cov_duration_sec = as.integer(d$`Duration (in seconds)`),
  cov_climate_worry = nz(d$climateworry), cov_climate_priority = nz(d$climatepriority),
  cov_expcheck = nz(d$expcheck), cov_exprecheck = nz(d$exprecheck), trial_climateexperiment = nz(d$climateexperiment))
cov_panel <- function(d, g = "gender") data.table(cov_age = as.integer(d$age), cov_gender_code = as.integer(nz(d[[g]])),
  cov_ethnicity_code = as.integer(nz(d$ethnicity)), cov_hispanic_code = as.integer(nz(d$hispanic)),
  cov_education_code = as.integer(nz(d$education)), cov_political_party_code = as.integer(nz(d$political_party)))
P <- c("Q272_Page Submit", "Q248_Page Submit", "Q273_Page Submit")
us <- rd("conjoint_us.csv"); stopifnot(nrow(us) == 1898)
u1 <- build(us, 5, c("Q260", "Q266", "Q269"), function(t, p) paste0(c("Q261_", "Q267_", "Q270_")[t], p), P,
            function(d) cbind(cov_common(d), cov_panel(d)))
ca <- rd("conjoint_canada.csv"); stopifnot(nrow(ca) == 1083)
c1 <- build(ca, 5, c("Q260", "Q266", "Q269"), function(t, p) paste0(c("Q261_", "Q267_", "Q270_")[t], p), P,
            function(d) cbind(cov_common(d), data.table(cov_ideology = as.integer(nz(d$ideo_1)), cov_user_language = d$UserLanguage)))
u2d <- rd("conjoint2_us.csv"); stopifnot(nrow(u2d) == 1295)
u2 <- build(u2d, 6, paste0("con_choice_", 1:3), function(t, p) sprintf("con_rate_%d_%d", t, p), c("Q135_Page Submit", "Q139_Page Submit", "Q143_Page Submit"),
            function(d) { x <- cov_panel(d, "gender.1")
              cbind(data.table(cov_duration_sec = as.integer(d$`Duration (in seconds)`),
                               cov_gender = c(Female = "female", Male = "male", Other = "other")[d$gender],
                               cov_raceeth = fifelse(d$raceeth %in% c("", "Prefer not to answer"), NA_character_, d$raceeth),
                               cov_birth_year = as.integer(nz(d$yob))), x, data.table(cov_hhi_code = as.integer(nz(d$hhi)))) })
fwrite(u1, file.path(out, "bergquist_2023_covid_climate_us.csv"))
fwrite(c1, file.path(out, "bergquist_2023_covid_climate_ca.csv"))
fwrite(u2, file.path(out, "bergquist_2023_covid_climate_us2.csv"))
