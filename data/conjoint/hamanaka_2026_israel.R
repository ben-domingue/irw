##Regime-attribute conjoint among Jewish Israeli citizens (one table) from
##Hamanaka, S. "Affective Polarization and Support for Democratic Principles in Israel" (working
##paper; no article DOI yet). Replication data: Harvard Dataverse doi:10.7910/DVN/DLAHLC, CC0 1.0,
##no restricted files. File read: affective_Israel2025-1.csv (the 2025 wave, 8,430 rows). Read as
##text only: Affective_Polarization_Democratic_Institutions_2025_replication.R, which supplies the
##two covariate codings used below.
##Usage: Rscript hamanaka_2026_israel.R <dir holding affective_Israel2025-1.csv> <output dir>
##
##The deposit holds TWO experiments. Only the 2025 wave is built here: 843 respondents x 5 tasks x 2
##profiles = 8,430 rows, already long, with `task`, `profile` and `selected` recorded and exactly one
##profile selected in every task (verified). The 2024 wave (Israel_2024_survey.csv) is a WIDE
##Qualtrics export whose levels are Hebrew strings that the authors' 2024 script translates and
##filters; it is a separate table and is left for a later pass (ledgered as todo).
##
##Eleven attributes, stored as the authors' English level labels. Respondents saw a HEBREW
##instrument, so display_language is he while label_language is en; the deposit ships no Hebrew
##level text for this wave. The source's own spellings are kept as stored, including the typos
##"Governemt-controlling" and the attribute name "Unemproyment" (attr_unemployment here, with the
##level text unchanged).
##
##Outcome: `selected` -> `choice`, forced choice between the two profiles (no opt-out). The deposit
##ships no questionnaire, so the WORDING IS UNKNOWN and design_outcomes.csv records that.
##
##Covariates. The replication script maps exactly two things, and those are the two mapped here:
##Q6 -> cov_vote_party (vote_map_2025: 1 Likud ... 11 Raam, 12 "Other_party_not_in_Q4",
##13 "Did_not_vote_or_missing" -- the source combines those two cases in one code) and the eleven
##party thermometers Q4_*/Q3_* -> cov_thermo_<party> with the script's 98/99 treated as item
##nonresponse (NA). Nothing in the deposit maps the demographics (D1-D7) or the remaining attitude
##items, so each keeps its source name with a `_code` suffix and its numeric codes, per the conjoint
##standard. `Finished` is kept as cov_finished (1 = completed).
##PII dropped: ResponseId (ids re-keyed 1..843 in first-appearance order), LocationLatitude,
##LocationLongitude. Also dropped: RecordedDate (response timestamp) and the file's own `respondent`
##and `respondentIndex` grouping columns, which take only eight values and key nothing here.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
TABLE <- "hamanaka_2026_israel_institutions"
d <- fread(file.path(raw, "affective_Israel2025-1.csv"))
stopifnot(nrow(d) == 8430, uniqueN(d$ResponseId) == 843)

ATTRS <- list(Economic.system = "economic_system", Election = "election", Judiciary = "judiciary",
              Leadership = "leadership", Military = "military", Participation = "participation",
              Religious.leaders = "religious_leaders", Social.division = "social_division",
              Social.services = "social_services", State.religion = "state_religion",
              Unemproyment = "unemployment")
VOTE <- c("1" = "Likud", "2" = "Yesh_Atid", "3" = "Shas", "4" = "National_Unity",
          "5" = "Jewish_Power", "6" = "Benett2026", "7" = "UTJ", "8" = "Yisrael_Beiteinu",
          "9" = "Democratim", "10" = "Hadash_Taal", "11" = "Raam",
          "12" = "Other_party_not_in_Q4", "13" = "Did_not_vote_or_missing")
THERMO <- c(Likud = "Q4_1", Yesh_Atid = "Q4_2", Shas = "Q4_3", National_Unity = "Q4_9",
            Jewish_Power = "Q4_4", Benett2026 = "Q4_5", UTJ = "Q4_6", Yisrael_Beiteinu = "Q4_7",
            Democratim = "Q4_8", Hadash_Taal = "Q3_10", Raam = "Q3_11")
DROP <- c("V1", "ResponseId", "RecordedDate", "LocationLatitude", "LocationLongitude",
          "respondent", "respondentIndex", "task", "profile", "selected", "Q6", "Finished",
          names(ATTRS), unname(THERMO))

setorder(d, ResponseId, task, profile)
d[, id := .GRP, ResponseId]
stopifnot(d[, .N, .(id, task)][, all(N == 2L)], d[, sum(selected), .(id, task)][, all(V1 == 1L)])
o <- d[, .(id, task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected))]
for (v in names(ATTRS)) o[, (paste0("attr_", ATTRS[[v]])) := trimws(d[[v]])]
o[, cov_vote_party := unname(VOTE[as.character(d$Q6)])]
for (p in names(THERMO)) {
  x <- suppressWarnings(as.numeric(d[[THERMO[[p]]]]))
  x[x %in% c(98, 99)] <- NA_real_
  o[, (paste0("cov_thermo_", tolower(p))) := x]
}
o[, cov_finished := as.integer(d$Finished)]
rest <- setdiff(names(d), c(DROP, "id"))
for (v in rest) o[, (paste0("cov_", tolower(gsub("[^A-Za-z0-9]+", "_", v)), "_code")) := d[[v]]]
stopifnot(!anyNA(o[, .SD, .SDcols = patterns("^attr_")]), nrow(o) == 8430, uniqueN(o$id) == 843)
setorder(o, id, task, profile)
fwrite(o, file.path(out, paste0(TABLE, ".csv")))
cat(TABLE, nrow(o), "rows", uniqueN(o$id), "respondents", sum(grepl("^attr_", names(o))), "attributes\n")
