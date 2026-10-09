##Security-policy candidate conjoint (Mexico) from
##Ventura, T., Ley, S., & Cantu, F. (2024). Voting for law and order: Evidence from a survey
##experiment in Mexico. Comparative Political Studies, 57(2), 551-583.
##https://doi.org/10.1177/00104140231169035
##Replication data: Harvard Dataverse doi:10.7910/DVN/DI1J2G, CC0 1.0 (the authors' GitHub copy
##of the same files carries GPL-3.0, a code licence; the Dataverse deposit governs). File read:
##raw_survey_data.Rdata (one data.frame `d`, loaded into its own environment). codebook.md,
##README.md and clean_survey_data.r were read as text (not run).
##Usage: Rscript ventura_2024.R <dir holding the .Rdata> <output dir>
##
##2,346 Mexican adults (Netquest online panel, respondents selected by LAPOP; Qualtrics,
##March-May 2020, Spanish), 2 tasks of 2 hypothetical candidates, 4 attributes: political
##party (PRI, Morena, PAN, Independiente), security proposal (5), previous experience /
##occupation (5), gender (Mujer/Hombre). Levels are the Spanish text stored in the Qualtrics
##export (f_<task>_<profile>_<row>), i.e. as displayed. Attribute ORDER was randomized once per
##respondent: f_<task>_<row> holds the attribute name shown in row <row>, identical in both
##tasks for every respondent (checked); attrpos_* give the row (1-4).
##Profile 1 = "Candidato A" (f_t_1_k), 2 = "Candidato B" (f_t_2_k), as in clean_survey_data.r.
##Outcome choice = conjointt_outcome ("Candidato A"/"Candidato B"). The question wording is
##not in the deposit (no questionnaire); paraphrase: which candidate would you vote for
##(the paper models "voters' decisions to support candidates"). No opt-out option; -999
##(no answer: 48 task-1 and 57 task-2 answers) are dropped, as in the authors' cleaning
##(missing_id). Randomization restrictions are not documented; all 200 level combinations
##occur; level shares are near-equal (each security and experience level 1,831-1,929 of 9,384 profile slots before dropping no-answers).
##Covariates (answer text as stored, Spanish/English as in the export): cov_gender (gender:
##Female/Male -> female/male), cov_age_group (age band text, e.g. "Entre 18 y 25"),
##cov_education, cov_party_id (positive_partisanship, party the respondent feels close to;
##"No responde" -> NA, "Ninguno"/"No sabe"/"Otro" kept), cov_negative_partisanship,
##cov_crime_victimization, cov_police_victimization (Si/No/No lo se), cov_trust_police (0-10
##as stored), cov_duration_sec (whole-survey duration). "-999" (no answer) -> NA throughout.
##PII in the source, dropped: ipaddress, locationlatitude/longitude, linkrequest (Netquest
##respondent URL), pid (panel id; 8 pids occur twice, rows kept as separate respondents as in
##the authors' analysis), responseid (re-keyed to 1..N in file order). The deposit also holds a
##tweet-sharing experiment whose attributes are stored only as image URLs (no labels): not built.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "raw_survey_data.Rdata"), envir = e)
s <- as.data.table(e$d)
stopifnot(nrow(s) == 2346, uniqueN(s$responseid) == 2346)
s[, rid := seq_len(.N)]
for (k in 1:4) stopifnot(identical(s[[paste0("f_1_", k)]], s[[paste0("f_2_", k)]]))
anames <- c("Partido Político" = "party", "Propuesta para el problema de inseguridad" = "security_proposal",
            "Experiencia previa" = "experience", "Género" = "gender")
rows <- list()
for (t in 1:2) for (p in 1:2) {
  x <- data.table(id = s$rid, task = t, profile = p)
  for (k in 1:4) {
    nm <- anames[trimws(s[[paste0("f_", t, "_", k)]])]
    stopifnot(!anyNA(nm))
    x[, paste0("lvl", k) := s[[paste0("f_", t, "_", p, "_", k)]]][, paste0("nm", k) := nm]
  }
  out_t <- s[[paste0("conjoint", t, "_outcome")]]
  x[, choice := fifelse(out_t == c("Candidato A", "Candidato B")[p], 1L, 0L)][out_t == "-999" | is.na(out_t), choice := NA]
  rows[[length(rows) + 1]] <- x
}
d <- rbindlist(rows)
for (v in anames) {
  d[, paste0("attr_", v) := NA_character_][, paste0("attrpos_", v) := NA_integer_]
  for (k in 1:4) { w <- which(d[[paste0("nm", k)]] == v)
    set(d, w, paste0("attr_", v), d[[paste0("lvl", k)]][w]); set(d, w, paste0("attrpos_", v), k) }
}
d[, c(paste0("lvl", 1:4), paste0("nm", 1:4)) := NULL]
d <- d[!is.na(choice)]
stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
na9 <- function(x) { x <- trimws(as.character(x)); x[x %in% c("-999", "")] <- NA; x }
cv <- s[, .(id = rid, cov_gender = c(Female = "female", Male = "male")[as.character(gender)],
            cov_age_group = na9(age), cov_education = na9(education),
            cov_party_id = na9(positive_partisanship), cov_negative_partisanship = na9(negative_partisanship),
            cov_crime_victimization = na9(crime_victimization), cov_police_victimization = na9(police_victimization),
            cov_trust_police = suppressWarnings(as.integer(na9(trust_police))),
            cov_duration_sec = as.integer(`duration_(in_seconds)`))]
cv[cov_party_id == "No responde", cov_party_id := NA][cov_negative_partisanship == "No responde", cov_negative_partisanship := NA]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ventura_2024_security_candidates.csv"))
