##Valence framing in a train-choice experiment (UK), from
##Barnes, O., Hess, S., & Hancock, T. (2025). Valence framing in multi-attribute decision-making. University of Leeds
##Research Data Leeds Repository. https://doi.org/10.5518/1709, CC BY 4.0 (repository record). The associated working
##paper is the PsyArXiv preprint doi 10.31234/osf.io/3xh6t (version 2), not read: no paper N to compare.
##Files read: valence_frame_survey_v1.xlsx .. v8.xlsx (sheets "data" and "dictionary") and
##valence_frame_survey_covariates.xlsx (sheets "covariates_data" and "dictionary").
##Usage: Rscript barnes_2025.R <dir holding the nine xlsx files> <output dir>
##
##410 online respondents (UK; START/DURATION in the covariates), 16 forced choices each between two UNLABELLED train
##alternatives (Train 1, Train 2), no opt-out ("Which would you choose?", opt1/opt2). Ngene-type design of 12 blocks;
##each respondent saw 4 of the 8 framing versions (v1-v8, the 2x2x2 of the three frames below) in random order, 4 tasks
##of each version. The version files hold one respondent's 4 tasks of that version each (SEQ 1-4).
##Frames: seat availability risky-choice frame (v1-4 "seats taken"/"chance of not getting a seat"; v5-8 "seats
##free"), service quality attribute frame ("dissatisfied" v1,2,5,6 vs "satisfied" v3,4,7,8), CO2 goal frame ("miss out
##on saving" v1,3,5,7 vs "save" v2,4,6,8): stored as trial_frame_seats / trial_frame_quality / trial_frame_co2, with
##trial_version = the file number.
##Attributes (displayed text from each file's dictionary sheet, one dictionary per version; HTML stripped): travel cost
##(GBP 30-50), travel time (2 h .. 2 h 40), seat availability (one text per train: x3 "N of the 200 seats will be
##taken/free" in one alternative and x4 "N% chance of (not) getting a seat" in the other; the unused one is coded 6),
##service quality, CO2 emissions (x6, a relative statement "By choosing Train 1, you will miss out on saving 6kg of CO2
##emissions compared to Train 2" or "Equal CO2 emissions for both trains", stored in ONE train's column only and coded
##6 in the other; the tree equivalent x7 "worth 1.5 trees a month" is appended to the statement). A column coded 6
##(not displayed in that train's column) is written "(not shown)". The CO2 statement is really task-level.
##Task order is INFERRED: the covariates' treatment_choice lists the 4 versions in the order shown; absolute task =
##(position of the version in that list - 1) * 4 + SEQ (the dictionary says SEQ is the order within the file). Checked:
##each respondent's four file versions equal their treatment_choice set. task_source = inferred.
##Dropped: 4 RIDs (167, 215, 245, 257) with 1-3 tasks and no covariate record (incomplete); 4 tasks with no choice
##(pref1 NA) from 4 respondents. Level weights: the design file is not deposited; shares observed.
##Covariates (covariates dictionary): cov_age_group (Age band text), cov_gender (1 Male, 2 Female, 3 other),
##cov_income_band (personal annual income band, GBP), cov_risk_willingness (0-10, "In general, how willing are you to take
##risks?"), cov_duration_sec (DURATION, survey duration), cov_speeder_flag (authors' flag: below a third of the median
##time). Respondent id re-keyed to 1..410 in RID order.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
clean <- function(s) trimws(gsub("\\s+", " ", gsub("<[^>]*>", " ", s)))
rd <- function(f, s, ...) suppressMessages(as.data.table(read_excel(file.path(raw, f), sheet = s, ...)))
dic <- function(v) {
  y <- rd(paste0("valence_frame_survey_v", v, ".xlsx"), "dictionary", col_names = FALSE)[, 2:4]
  setnames(y, c("a", "b", "c")); cur <- NA_character_; out <- list()
  for (i in seq_len(nrow(y))) {
    if (!is.na(y$a[i])) { cur <- if (grepl("^a[12]_x[1-7]$", y$a[i])) y$a[i] else NA_character_; next }
    if (!is.na(cur) && !is.na(y$b[i]) && grepl("^[0-9]+$", y$b[i]))
      out[[length(out) + 1]] <- data.table(v = v, var = cur, code = as.integer(y$b[i]), label = if (is.na(y$c[i])) "" else clean(y$c[i]))
  }
  rbindlist(out)
}
D <- rbindlist(lapply(1:8, dic))
X <- rbindlist(lapply(1:8, function(v) { x <- rd(paste0("valence_frame_survey_v", v, ".xlsx"), "data"); x[, v := v] }), fill = TRUE)
cv <- rd("valence_frame_survey_covariates.xlsx", "covariates_data")
stopifnot(nrow(cv) == 410, uniqueN(cv$RID) == 410)
X <- X[RID %in% cv$RID]
stopifnot(X[, .N, RID][, all(N == 16)])
# task order from treatment_choice
tc <- cv[, .(RID, ord = strsplit(treatment_choice, ",")), by = .I][, .(v = as.integer(ord[[1]]), pos = 1:4), by = RID]
stopifnot(tc[, .N, RID][, all(N == 4)])
X <- merge(X, tc, by = c("RID", "v"))
stopifnot(nrow(X) == 6560)
X[, task := (pos - 1L) * 4L + SEQ]
stopifnot(X[, uniqueN(task), RID][, all(V1 == 16)])
X <- X[!is.na(pref1)]
LK <- setNames(D$label, paste(D$v, D$var, D$code))
txt <- function(vv, vr, cd) unname(LK[paste(vv, vr, cd)])
mk <- function(k) {
  p <- function(n) paste0("a", k, "_", n)
  seats <- fifelse(X[[p("x3")]] != 6, txt(X$v, p("x3"), X[[p("x3")]]), txt(X$v, p("x4"), X[[p("x4")]]))
  co2 <- fifelse(X[[p("x6")]] == 6, "(not shown)", txt(X$v, p("x6"), X[[p("x6")]]))
  tr <- txt(X$v, p("x7"), X[[p("x7")]])
  co2 <- fifelse(co2 != "(not shown)" & !is.na(tr) & tr != "", paste0(co2, "; ", tr), co2)
  data.table(RID = X$RID, task = X$task, profile = k, choice = as.integer(X$pref1 == k), v = X$v,
    attr_travel_cost = txt(X$v, p("x1"), X[[p("x1")]]), attr_travel_time = txt(X$v, p("x2"), X[[p("x2")]]),
    attr_seat_availability = seats, attr_service_quality = txt(X$v, p("x5"), X[[p("x5")]]), attr_co2_emissions = co2)
}
d <- rbind(mk(1), mk(2))
stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]), d[, all(attr_seat_availability != "")])
fr <- function(vr, cd, pat) sapply(1:8, function(v) grepl(pat, LK[[paste(v, vr, cd)]]))
d[, trial_version := v]
d[, trial_frame_seats := c("seats free", "seats taken")[1 + fr("a1_x3", 1L, "taken")[v]]]
d[, trial_frame_quality := c("satisfied", "dissatisfied")[1 + fr("a1_x5", 1L, "dissatisfied")[v]]]
d[, trial_frame_co2 := c("save", "miss out")[1 + fr("a1_x6", 1L, "miss out")[v]]]
d[, v := NULL]
ag <- c("Under 18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+")
inc <- c("£0", "£1 - £9999", "£10000 - £19999", "£20,000 - £29,999", "£30000 - £39999", "£40000 - £49999", "£50000 - £59999",
         "£60000 - £69999", "£70000 - £79999", "£80000+")
c2 <- cv[, .(RID, cov_age_group = ag[Age], cov_gender = c("male", "female", "other")[Gender], cov_income_band = inc[Income],
             cov_risk_willingness = as.integer(risk_preference) - 1L, cov_duration_sec = DURATION,
             cov_speeder_flag = as.integer(!is.na(`Speeder Flag`)))]
d <- merge(d, c2, by = "RID")
d[, id := match(RID, sort(unique(RID)))][, RID := NULL]
d <- d[, c("id", setdiff(names(d), "id")), with = FALSE]
# drop tasks left with one profile (cannot happen: pref1 non-NA drops whole tasks)
stopifnot(d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "barnes_2025_valence_framing.csv"))
