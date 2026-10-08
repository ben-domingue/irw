##COVID-19 restriction-policy conjoint (Germany) from
##Hartmann, F., Humphreys, M., Geissler, F., Klueber, H., & Giesecke, J. (2023). Trading liberties:
##Estimating COVID-19 policy preferences from conjoint data. Political Analysis.
##https://doi.org/10.1017/pan.2023.25 (CC BY 4.0; corrigendum doi:10.1017/pan.2023.29)
##Replication data: Harvard Dataverse doi:10.7910/DVN/SVD9SV, CC0 1.0, no restricted files.
##Files read: data/df_long_rep_export.rds (one row per respondent and panel wave; SPSS-style
##labelled columns), data/W4_exp7_vignettes_universe_-_20210831.dta (the 9 policy vignettes:
##vignr -> costs (universality) x restictions (stringency), with German value labels),
##ReadMe.txt. The authors' 0_master.Rmd was read as text (not run): it gives the sample filter,
##the vignette and outcome columns, and the federal-state codes.
##Usage: Rscript hartmann_2023.R <dir holding df_long_rep_export.rds and vignettes_universe.dta> <output dir>
##  (vignettes_universe.dta = the deposit's W4_exp7_vignettes_universe_-_20210831.dta, renamed on download)
##
##Sample: wave 4, Launch Version 4 (Full Launch) or 5 (Refreshment Sample), as in 0_master.Rmd:
##10,525 respondents (= the article's "10,525 respondents between 8 and 22 September 2021").
##The authors then drop 141 respondents flagged pr_error_exp7 = "Wrong Outcome" ("Programming error
##for trust-outcome of Experiment 7") and 14 with vaccination status "Weiss nicht"; the table keeps
##them all, sets rating_trust to NA for the 141 flagged respondents (the flag concerns only that
##outcome), and keeps the flag as cov_pr_error_exp7 (0/1).
##Design (article sec. 2): a 3 x 3 x 3 factorial; each respondent saw two rounds (task 1-2), each a
##pair of policy proposals (profile 1-2 = Vorschlag 1/2; c_0031..c_0034_w4 = vignette numbers).
##Within a round both proposals share the pandemic severity (attr_severity, the displayed German
##text, c_0106/c_0107) and differ in policy stringency and universality (the two vignettes of a
##pair are never identical: checked). Severity differs between the two rounds (checked).
##attr_stringency / attr_universality: the German value labels of the vignette universe with the
##design-role prefix ("Control: " / "Treatment: ") removed, e.g. "minimale Einschraenkungen",
##"3G" (article Table 1: least restrictions (masks) .. most restrictions; most exemptions
##(vaccinated, recovered or tested exempt = 3G), some (2G), fewest ("alle Buerger")). The full
##vignette text is not in the deposit.
##Outcomes (article p. 3; wording paraphrased, scale end labels from the value labels):
##  choice = preferred proposal of the two (v_449/v_458: 1 = Vorschlag 1, as 0_master.Rmd codes it);
##  forced choice, no opt-out.
##  rating = rating of each proposal, 0 "definitiv dagegen" .. 10 "definitiv dafuer" (v_451/452,
##    v_459/460).
##  rating_trust = trust in the federal government if this proposal were implemented, 0 "Ueberhaupt
##    kein Vertrauen" .. 10 "Volles Vertrauen"; asked about ONE proposal per round, drawn at random
##    (c_0108/c_0109); NA on the other proposal.
##  rating_vaccine = likelihood of getting vaccinated under this proposal, 0 "Ich lasse mich mit
##    Sicherheit nicht gegen Corona impfen" .. 10 "... mit Sicherheit ..."; asked only of the 1,665
##    unvaccinated respondents (NA otherwise).
##  The authors divide the 0-10 scales by 10; the table keeps them raw.
##Covariates (value labels of the .rds): cov_gender (v_16 Weiblich/Maennlich/Sonstiges ->
##female/male/other), cov_age (v_15, years), cov_federal_state (v_23 codes 1-16 -> the English state
##names in 0_master.Rmd; -99 -> NA), cov_occupation (v_111 label text), cov_vaccinated (v_28
##Ja/Nein/Weiss nicht), cov_vaccination_intent (v_33 label text; asked of the unvaccinated),
##cov_party_id (v_69 label text; "keiner Partei" kept as text), cov_sample (group: Full Launch /
##Refreshment Sample). No platform IDs; ID (panel numbers) re-keyed to 1..N in source order.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- readRDS(file.path(raw, "df_long_rep_export.rds"))
k <- k[k$wave == 4 & k$group %in% 4:5, ]
stopifnot(nrow(k) == 10525, !anyDuplicated(k$ID))
z <- as.data.table(as_factor(read_dta(file.path(raw, "vignettes_universe.dta"))))
z[, `:=`(universality = sub("^(Control|Treatment): ", "", costs), stringency = sub("^(Control|Treatment): ", "", restictions))]
txt <- function(x) as.character(as_factor(x))
num <- function(x) as.integer(zap_labels(x))
k$id <- seq_len(nrow(k))
vig <- list(c("c_0031_w4", "c_0032_w4"), c("c_0033_w4", "c_0034_w4"))
sev <- c("c_0106", "c_0107"); drw <- c("c_0108", "c_0109"); chv <- c("v_449", "v_458")
rat <- list(c("v_451", "v_452"), c("v_459", "v_460")); vac <- list(c("v_453", "v_454"), c("v_461", "v_462"))
tru <- c("v_455", "v_463")
flag <- num(k$pr_error_exp7)
d <- rbindlist(lapply(1:2, function(t) rbindlist(lapply(1:2, function(p) {
  vn <- as.integer(as.character(k[[vig[[t]][p]]]))
  data.table(id = k$id, task = t, profile = p,
             choice = as.integer(num(k[[chv[t]]]) == p),
             rating = num(k[[rat[[t]][p]]]),
             rating_trust = fifelse(num(k[[drw[t]]]) == p & flag == 0, num(k[[tru[t]]]), NA_integer_),
             rating_vaccine = num(k[[vac[[t]][p]]]),
             attr_severity = txt(k[[sev[t]]]),
             attr_stringency = z$stringency[match(vn, z$vignr)],
             attr_universality = z$universality[match(vn, z$vignr)], vn = vn)
}))))
stopifnot(d[, !anyNA(.SD), .SDcols = c("choice", "rating", "attr_severity", "attr_stringency", "attr_universality")],
          d[, sum(choice), by = .(id, task)][, all(V1 == 1)],
          d[, uniqueN(vn), by = .(id, task)][, all(V1 == 2)],
          d[, uniqueN(attr_severity), by = .(id, task)][, all(V1 == 1)],
          d[, uniqueN(attr_severity), by = id][, all(V1 == 2)],
          d[, all(rating %in% 0:10)])
d[, vn := NULL]
fs <- c("Baden-Wuerttemberg", "Bavaria", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hesse",
        "Mecklenburg-Vorpommern", "Lower Saxony", "North Rhine-Westphalia", "Rhineland-Palatinate",
        "Saarland", "Saxony", "Saxony-Anhalt", "Schleswig-Holstein", "Thuringia")
st <- suppressWarnings(as.integer(k$v_23))
stopifnot(all(st %in% c(-99, 1:16)))
cv <- data.table(id = k$id,
  cov_gender = c("female", "male", "other")[num(k$v_16)],
  cov_age = num(k$v_15),
  cov_federal_state = fs[fifelse(st == -99, NA_integer_, st)],
  cov_occupation = txt(k$v_111), cov_vaccinated = txt(k$v_28),
  cov_vaccination_intent = txt(k$v_33), cov_party_id = txt(k$v_69),
  cov_sample = txt(k$group), cov_pr_error_exp7 = flag)
stopifnot(all(num(k$v_16) %in% 1:3), all(cv$cov_sample %in% c("Full Launch", "Refreshment Sample")))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hartmann_2023_covid_restrictions.csv"))
