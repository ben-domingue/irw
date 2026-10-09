##Four two-factor vignette experiments from the MigCrimeMexSurvey 2021 (Mexico), deposited with
##Berens, S., López García, A. I., & Maydom, B. (2024). Classrooms or crackdowns? How violence affects
##security policy preferences in Mexico. Studies in Comparative International Development, 61(1),
##10-33. https://doi.org/10.1007/s12116-024-09445-z
##Replication data: Harvard Dataverse doi:10.7910/DVN/W1YF9Y, CC0 1.0, no restricted files.
##Files read: "Data ready E5.dta" (Stata original; value labels), "MigCrimeMexSurvey 2021 -
##questionnaire.pdf" (bilingual English/Spanish questionnaire: experiment wording and treatment
##texts), "1_Datapreparation_E5.do" and "2_Analysis_E5.do" read as text (not run).
##Usage: Rscript berens_2024.R <raw dir> <output dir>
##
##2,401 Mexican adults, Pollfish online survey, 31 Dec 2021 - 2 Jan 2022 (readme). The survey ran seven
##single-sentence vignette experiments; the four that randomize TWO factors are built here, one table
##each (different sentences, factors and questions = separate experiments): E1 (Q36, taxes),
##E4 (Q46, demilitarisation proposal), E5 (Q26, crime measures; the article's experiment) and E6
##(Q15 + Q16, new police recruits; two questions about the same sentence = one table, two ratings).
##E2, E3 and E7 vary a single factor and are not conjoint designs. One task and one profile per
##respondent per experiment (task = 1, profile = 1, constant).
##Each factor is a clause inserted into the sentence; its control level is "Empty" (the clause is left
##out), stored as "(not shown)". Level text is the SPANISH clause of the questionnaire's Spanish
##column (respondents answered in Spanish; the Pollfish screens are not deposited, so the
##questionnaire is the closest record of the displayed text). Codes -> clauses: the .dta value
##labels (e.g. Q26_vign2 1 education, 2 employment, 3 prison punitive, 4 prison rehab, 5 zero
##tolerance policing) follow the questionnaire's numbered treatments in every experiment (checked
##below; prep do-file L26-41 swaps 3/4 only in its own derived E5_vign2, which is not used).
##Every factor combination has 200 or 201 respondents in every experiment (a balanced allocation);
##no source states the assignment rule, so restrictions and level weights are "unknown".
##Outcomes (questionnaire, Spanish wording; stored raw, higher = more agreement / more of the asked quantity):
##  E1 rating 1-5 (Muy en desacuerdo ... Muy de acuerdo) to paying more taxes;
##  E4 rating 1-5 agreement with the proposal;
##  E5 rating 1-5 agreement with the statement;
##  E6 rating (Q15) 1-4 faith that the recruits catch criminals (Nada ... Mucho);
##     rating_misconduct (Q16) 1-4 likelihood that the recruits engage in bribery, torture etc.
##     (Nada probable ... Muy probable; higher = LESS favourable).
##Covariates: cov_gender (gender: 1 female, 2 male, .dta labels), cov_birth_year (year_birth),
##cov_age (age, years, as deposited), cov_age_group (age_range labels), cov_education_code (education
##1-6: the deposit has no labels for these codes; the prep do-file only collapses them).
##Dropped: Pollfish respondent ID (re-keyed: id = the deposit's own sequential `id`), TimeStarted/
##TimeFinished, device Manufacturer/OS, City, PostalCode, mobile Provider, Area (geolocation),
##all other survey items and derived variables. Weight is 1 for everyone (no survey weight).
##N: 2,401 respondents in every table; the article's N was not checked.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- haven::read_dta(file.path(raw, "Data ready E5.dta"))
lab <- function(v) { l <- attr(x[[v]], "labels"); setNames(names(l), l) }
stopifnot(identical(unname(lab("Q26_vign2")), c("empty", "education", "employment", "prison punitive", "prison rehab", "zero tolerance policing")),
          identical(unname(lab("Q15_vign2")), c("empty", "military", "private security", "self-defences", "human rights activists", "return migrants")),
          identical(unname(lab("Q36_vign1")), c("empty", "Consumption Taxes", "Income Taxes")),
          identical(unname(lab("Q36_vign2")), c("empty", "Health", "Roads", "Security")),
          identical(unname(lab("Q46_vign1")), c("empty", "PAN", "PRI")),
          identical(unname(lab("Q46_vign2")), c("empty", "state/mun govmnts", "private sector", "citizens")),
          identical(unname(lab("Q26_vign1")), c("empty", "violent municipalities")), identical(unname(lab("Q15_vign1")), c("empty", "female")))
s <- as.data.table(haven::zap_labels(x))
stopifnot(nrow(s) == 2401, !anyDuplicated(s$id), all(s$gender %in% 1:2), all(s$Weight == 1))
ns <- "(not shown)"
txt <- list(
  Q36_vign1 = c(ns, "como el Impuesto al Valor Agregado – IVA (el impuesto que pagamos al comprar artículos y productos de consumo en tiendas o supermercados)",
                "como el Impuesto sobre la Renta - ISR (el impuesto que se aplica a los ingresos percibidos o generados por las personas)"),
  Q36_vign2 = c(ns, "en salud pública", "en construcción y mantenimiento de calles, caminos, rutas y accesos", "en seguridad pública y procuración de justicia"),
  Q46_vign1 = c(ns, "hecha por el PAN", "hecha por el PRI"),
  Q46_vign2 = c(ns, "en colaboración con las autoridades municipales", "en colaboración con el sector privado", "en colaboración con la ciudadanía y las comunidades"),
  Q26_vign1 = c(ns, "en los municipios más violentos del país"),
  Q26_vign2 = c(ns, "y desarrollar más programas de capacitación vocacional y actividades recreativas o culturales para a los jóvenes y adolescentes",
                "y generar más oportunidades de empleo para los jóvenes",
                "como invertir en centros de reclusión, con medidas disciplinarias estrictas y sentencias más largas",
                "e invertir en centros de reclusión, con mejores condiciones de vida y programas de rehabilitación y readaptación social",
                "y sancionar todas las infracciones a la ley, por más insignificantes que parezcan, ordenar redadas, imponer toques de queda y otras políticas de tolerancia cero"),
  Q15_vign1 = c(ns, "del sexo femenino"),
  Q15_vign2 = c(ns, "que antes trabajaban como soldados o sargentos en el Ejército", "que antes trabajaban como escoltas o guardias en empresas de seguridad privada",
                "que antes eran miembros de las autodefensas y policías comunitarias", "que han sido activistas de derechos humanos",
                "que anteriormente trabajaban como migrantes en EE.UU."))
for (v in names(txt)) stopifnot(all(s[[v]] %in% (seq_along(txt[[v]]) - 1L)), length(txt[[v]]) == length(lab(v)))
tx <- function(v) txt[[v]][s[[v]] + 1L]
ag <- lab("age_range")
cv <- s[, .(id = as.integer(id), task = 1L, profile = 1L)]
cov <- s[, .(cov_gender = c("female", "male")[gender], cov_birth_year = as.integer(year_birth), cov_age = as.integer(age),
             cov_age_group = sub(" yrs$", "", ag[as.character(age_range)]), cov_education_code = as.integer(education))]
stopifnot(!anyNA(cov$cov_age_group), cov[, all(cov_birth_year %between% c(1900L, 2005L))])
chk <- function(r, lo, hi) { stopifnot(all(r %in% lo:hi)); as.integer(r) }
tabs <- list(
  berens_2024_taxes_spending = data.table(cv, rating = chk(s$Q36_eval, 1, 5), attr_tax = tx("Q36_vign1"), attr_spending_area = tx("Q36_vign2"), cov),
  berens_2024_demilitarisation = data.table(cv, rating = chk(s$Q46_eval, 1, 5), attr_proposer = tx("Q46_vign1"), attr_collaboration = tx("Q46_vign2"), cov),
  berens_2024_crime_measures = data.table(cv, rating = chk(s$Q26_eval, 1, 5), attr_territory = tx("Q26_vign1"), attr_measure = tx("Q26_vign2"), cov),
  berens_2024_police_recruits = data.table(cv, rating = chk(s$Q15_eval, 1, 4), rating_misconduct = chk(s$Q16_eval, 1, 4),
                                           attr_gender = tx("Q15_vign1"), attr_background = tx("Q15_vign2"), cov))
for (n in names(tabs)) { d <- tabs[[n]]; setorder(d, id, task, profile); fwrite(d, file.path(out, paste0(n, ".csv"))) }
