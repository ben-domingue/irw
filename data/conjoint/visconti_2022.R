##Post-flood candidate conjoint (Paipote, Chile) from
##Visconti, G. (2022). After the flood: Disasters, ideological voting and electoral choices
##in Chile. Political Behavior, 44(4), 1985-2004. https://doi.org/10.1007/s11109-022-09814-1
##Replication data: Harvard Dataverse doi:10.7910/DVN/O1RCGV, CC0 1.0, no restricted files.
##File read: conjoint_paipote_final.dta (Dataverse "original format"; one row per
##respondent x pair x candidate; Spanish level text in Stata value labels). The authors'
##002_conjoint_analysis.R and 004_conjoint_diagnostic.R read as text.
##Usage: Rscript visconti_2022.R <raw dir> <output dir>
##
##210 respondents in Paipote (Copiapó, Atacama), surveyed after the 2015 floods (natural
##experiment: exposure to flood damage). Each saw 8 pairs (task = source `pair`) of
##hypothetical candidates (profile = source `candidate`, 1/2) with 6 attributes, Spanish text
##as displayed: attr_ideology Derecha/Centro/Independiente/Izquierda; attr_profession
##Jardinero(a)/Profesor(a)/Ingeniero(a); attr_gender Hombre/Mujer; attr_age 30/40/50;
##attr_experience Sin experiencia/Concejal/Alcalde; attr_expectations "NO entregar ayuda
##economica"/"Entregar ayuda economica" (whether the candidate is expected to hand out
##economic aid).
##OUTCOME: choice = the source's `selected` (1 = this candidate selected). The question
##wording is NOT in the deposit and the article could not be read (paywalled); the
##deposit describes it as voters "selecting" candidates (an electoral choice). 104 rows
##coded 999 (missing) are dropped; 161 pairs have both candidates 0 (no 999): kept as
##recorded; whether this was an explicit "neither" option or a non-answer cannot be told
##from the deposit (opt-out unknown).
##cov_failed_conjoint = the source's failcon (10 respondents the author drops: "failed
##conjoints"; most of their answers are 999). cov_flood_exposed = the author's treatment
##indicator (damage level a2 > 2); cov_zone 1/2/3 = sampled zone A/B/C (labels from
##survey_paipote_final.dta; the author treats A and C as the affected area). Other survey
##codes (c1-c3, b1, a3, a4) have no labels in the deposit and are dropped.
##Respondent ids are the source's sequential idnum (1-210).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- read_dta(file.path(raw, "conjoint_paipote_final.dta"))
lab <- function(v) { l <- attr(v, "labels"); r <- names(l)[match(as.numeric(v), l)]; stopifnot(!anyNA(r)); r }
d <- data.table(id = as.integer(x$idnum), task = as.integer(x$pair), profile = as.integer(x$candidate),
                choice = as.integer(x$selected),
                attr_ideology = lab(x$atideology), attr_profession = lab(x$atprofession), attr_gender = lab(x$atgender),
                attr_age = lab(x$atage), attr_experience = lab(x$atexperience), attr_expectations = lab(x$atexpectations),
                cov_failed_conjoint = as.integer(x$failcon), cov_flood_exposed = as.integer(x$a2 > 2), cov_zone = as.integer(x$zone))
stopifnot(!anyDuplicated(d[, .(id, task, profile)]), uniqueN(d$id) == 210)
d <- d[choice != 999L]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "visconti_2022_flood_candidates.csv"))
