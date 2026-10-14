##Single-profile conjoint on armed non-state actors ("Axis of Resistance"), four Middle East samples, from
##Yamao, D., & Suechika, K. (2025). Measuring public support for armed non-state actors at war: a comparative
##study of the case of the Axis of Resistance. Deposit title; no article DOI found (conference paper,
##Kyushu University). Replication data: Harvard Dataverse doi:10.7910/DVN/MBMSYI, CC0 1.0.
##Files read: cj_data_Iraq.csv, cj_data_Lebanon.csv, cj_data_Palestine.csv, cj_data_Yemen.csv (saved as
##iraq.csv, leb.csv, pal.csv, yem.csv); conjoint.Rmd and cj_analysis_Iraq.Rmd, descriptive_statistics.Rmd as text.
##Usage: Rscript yamao_2025_armed_actors.R <dir holding the four csv> <output dir>
##
##Four tables, one per sample (Iraq 1,066, Lebanon 1,035, Palestine 104, Yemen 1,323 respondents), because the
##Patron level shows each country's own government ("Iraqi government", "Lebanese government", "Palestinian
##government", "Yemeni government"); the authors pooled them only after recoding to "Own government", which is not the
##displayed text. Output tables: yamao_2025_armed_iraq / _lebanon / _palestine / _yemen.
##Design: each respondent sees 5 tasks, each ONE profile (profile = 1) of a hypothetical armed non-state actor with 4
##attributes (activity, armament, patron, service provision), attribute ROW ORDER randomized per task and recorded
##(attrpos_*). Outcome rating = `selected`, an integer 1-5 per profile (the authors' regression outcome). The deposit
##has NO questionnaire and no paper: the question wording, the meaning of 1 and 5 and the direction are NOT
##documented (title and analysis name it "support"); stored raw. Rows with missing rating are dropped (113 / 176 /
##35 / 295 rows). The authors' na.exclude also drops rows with NA in any other column; here only the rating matters.
##Level text as stored (e.g. "Reconstruction of infrastracture" is the source's spelling). Online panel (Qualtrics,
##Jan 2025); the authors split pre/post a ceasefire (17 Jan 2025): trial_period "pre" if RecordedDate <= 2025-01-16.
##Randomization restrictions and level probabilities are not documented (all combinations occur).
##Covariates: cov_gender from D1 (authors' recode: 1 Male, 2 Female; the file's `Gender` column differs from D1 for
##about 20 respondents and is not used), cov_age_group from D2 (authors' recode: 1 18-20, 2 21-30, 3 31-40, 4 41-50, 5 51-60,
##6 60+; 6 is not labelled in the authors' recode of the Iraq file but the descriptive file lists "60-").
##PII FOUND: LocationLatitude / LocationLongitude (constant panel-level values, dropped), RecordedDate (reduced to
##the period flag). Dropped: all other questionnaire items (Q*), the `Age` column (does not match D2), Finished.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
bands <- c("18-20", "21-30", "31-40", "41-50", "51-60", "60-")
one <- function(f, name) {
  x <- fread(file.path(raw, f), na.strings = c("NA", ""))
  x <- x[!is.na(selected)]
  stopifnot(x[, .N, .(respondentIndex, task)][, all(N == 1)], all(x$profile == 1))
  d <- x[, .(id = as.integer(factor(respondentIndex)), task = as.integer(task), profile = 1L, rating = as.integer(selected),
             attr_activity = Activity, attr_armament = Armament, attr_patron = Patron, attr_service = Service,
             attrpos_activity = as.integer(Activity.rowpos), attrpos_armament = as.integer(Armament.rowpos),
             attrpos_patron = as.integer(Patron.rowpos), attrpos_service = as.integer(Service.rowpos),
             cov_gender = c("male", "female")[D1], cov_age_group = bands[D2],
             trial_period = fifelse(as.Date(substr(RecordedDate, 1, 10)) <= as.Date("2025-01-16"), "pre", "post"))]
  stopifnot(!anyNA(d$attr_activity), !anyNA(d$attr_patron), d[, uniqueN(id)] >= 100)
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("yamao_2025_armed_", name, ".csv")))
  cat(name, d[, uniqueN(id)], nrow(d), "\n")
}
one("iraq.csv", "iraq"); one("leb.csv", "lebanon"); one("pal.csv", "palestine"); one("yem.csv", "yemen")
