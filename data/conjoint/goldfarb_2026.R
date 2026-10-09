##Sustainable-aviation-fuel flight conjoint from
##Kriner, D., Goldfarb, J. L., Tester, J., & Bhujle, T. (2026). Replication data for: Comfort or
##climate? Consumer trade-offs between sustainable aviation fuel and flight amenities [Data set].
##Harvard Dataverse. The article was not found on 2026-10-08; the .do file name
##("Goldfarb_etal_SAF_JCP") names Goldfarb as first author and points to the Journal of Cleaner
##Production, hence the table name goldfarb_2026.
##Replication data: Harvard Dataverse doi:10.7910/DVN/DOHF01, CC0 1.0, no restricted files.
##File read: Goldfarb_etal_SAF_JCP_replication.dta (Dataverse "original format" download of the
##.tab). The authors' Goldfarb_etal_SAF_JCP_replication.do was read as text. Question text and
##answer labels come from the .dta variable and value labels.
##Usage: Rscript goldfarb_2026.R <dir holding the .dta> <output dir>
##
##1,000 US respondents (Verasight panel; omnibus survey, start dates in the .dta), each choosing
##between 2 flights in 5 tasks ("Which of these two flights would you choose?", Flight 1 /
##Flight 2; forced, exactly one chosen per task, checked). choice_set encodes task*10 + profile.
##6 attributes: Airline (Delta/Frontier/Southwest/United), Fuel type ("Conventional aviation
##fuel produced from petroleum" / "Sutainable aviation fuel produced from biomass", the typo is
##in the source and in the displayed Qualtrics text), Included baggage, Legroom, Seat type,
##Price ($250-$325). Attribute text is taken from the Qualtrics conjoint export columns
##(F-t-k = attribute name at row k of task t, F-t-p-k = its level for profile p) and checked
##against the authors' long-format columns (airline, fuel_type, ...), which agree on every row.
##Attribute row order was randomized per respondent (the F-t-k names are identical across a
##respondent's 5 tasks and vary between respondents); attrpos_<attr> = row 1-6.
##Covariates (.dta value labels): cov_survey_weight (weight); cov_age (age code 1 = 18, so
##code + 17); cov_gender ("What is your gender?" 1 Male = male, 2 Female = female, 3 Prefer not
##to say = NA); cov_education (Education, label text); cov_party_id ("In politics, as of
##today, do you consider yourself a Republican, a Democrat, or an Independent?", label text);
##cov_party_lean (1 Democratic Party, 2 Republican Party, 3 Neither/don't know); cov_ideology
##("Politically, I consider myself:", label text Very Liberal..Very Conservative);
##cov_income (label text); cov_religion (label text); cov_state (label text); cov_region
##(Verasight profile census region, label text); cov_race_<group> 1/0 (check-all-that-apply, 1 = checked, as stored); cov_trump_approve (1 Approve, 2 Disapprove, 3 No opinion);
##cov_vote_2024 (1 I voted, 2 too young, 3 not registered, 4 did not vote), cov_vote_choice_2024
##(1 Harris, 2 Trump, 3 someone else) from the Verasight profile; cov_sciknow_<k> (9
##true/false science items, 1 True 2 False 3 Unsure); cov_sci_know_self (1 Not at all
##knowledgeable .. 7 Very knowledgeable); cov_saf_familiar (1 Not at all informed .. 4 Very
##informed); cov_saf_safe ("Sustainable aviation fuels are safe" 1 Strongly disagree .. 5
##Strongly agree); cov_climate_change (1 "not occurring" .. 5 "established as a serious
##problem, and immediate action is necessary", the authors' re-ordered version of the item).
##Dropped: ZIP code (free text, identifying) and Qualtrics case_id (PII); start/end dates; the
##consent item; the other experiments and items of the omnibus survey (electricity, carbon,
##phosphorus, bioeconomy, land, executive power, place resentment, ...); the *_old orderings of
##recoded items; the authors' derived variables (dem3, gop3, gop5, dem5, party3, female,
##college, trump_approve dummy, sciknow*_correct, sciknow_score, choose_first_flight_*,
##*_n codes). respondent (1-1000) is the deposit's own integer id and is kept.
##N: 1,000 respondents x 5 tasks = 10,000 rows (article not available to check). Spot check:
##the authors' Table 2 model (OLS of choose_flight on the six attributes, clustered by
##respondent) gives SAF +0.069, matching the deposit abstract (SAF "increases the probability
##of selection by approximately seven percentage points").
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "Goldfarb_etal_SAF_JCP_replication.dta")))
stopifnot(k[, .N, respondent][, all(N == 10)], all(k$choice_set %in% outer(1:5 * 10, 1:2, "+")))
d <- data.table(id = as.integer(k$respondent), task = as.integer(k$choice_set) %/% 10L, profile = as.integer(k$choice_set) %% 10L,
                choice = as.integer(k$choose_flight))
anames <- c("Airline" = "airline", "Fuel type" = "fuel_type", "Included baggage" = "baggage", "Legroom" = "legroom",
            "Seat type" = "seat_type", "Price" = "price")
long <- c(airline = "airline", fuel_type = "fuel_type", baggage = "baggage", legroom = "legroom", seat_type = "seat", price = "price")
for (v in anames) { d[, paste0("attr_", v) := NA_character_]; d[, paste0("attrpos_", v) := NA_integer_] }
for (t in 1:5) for (pos in 1:6) {
  nm <- k[[sprintf("f_%d_%d", t, pos)]]; stopifnot(all(nm %in% names(anames)))
  for (p in 1:2) {
    lv <- k[[sprintf("f_%d_%d_%d", t, p, pos)]]; r <- which(d$task == t & d$profile == p)
    for (a1 in names(anames)) { rr <- r[nm[r] == a1]; v <- anames[[a1]]
      set(d, rr, paste0("attr_", v), lv[rr]); set(d, rr, paste0("attrpos_", v), pos) }
  }
}
for (v in names(long)) stopifnot(all(d[[paste0("attr_", v)]] == as.character(k[[long[[v]]]])))
stopifnot(!anyNA(d), d[, uniqueN(paste(attrpos_airline, attrpos_fuel_type, attrpos_baggage, attrpos_price)), id][, all(V1 == 1)])
# the per-task Flight 1/2 answers agree with choose_flight
ans <- sapply(1:5, function(t) as.integer(k[[c("saf_choice1", "saf_choice2", "saf_conjoint3", "saf_conjoint4", "saf_conjoint5")[t]]]))
stopifnot(all(d$choice == as.integer(ans[cbind(seq_len(nrow(d)), d$task)] == d$profile)))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
stopifnot(all(k$gender %in% 1:3), all(diff(attr(k$age, "labels")) == 1), attr(k$age, "labels")[1] == 1)
d[, `:=`(cov_survey_weight = as.numeric(k$weight), cov_age = as.integer(zap_labels(k$age)) + 17L,
         cov_gender = c("male", "female", NA)[as.integer(k$gender)], cov_education = lab(k$education), cov_party_id = lab(k$party),
         cov_party_lean = as.integer(zap_labels(k$party_lean)), cov_ideology = lab(k$ideology), cov_income = lab(k$income),
         cov_religion = lab(k$relig), cov_state = lab(k$state), cov_region = lab(k$vs_region))]
for (r in c("native_american", "asian", "black", "hispanic", "white", "race_6")) {
  x <- as.integer(zap_labels(k[[r]])); stopifnot(all(x %in% 0:1)); d[, paste0("cov_race_", sub("race_6", "other", r)) := x] }
cmap <- c(approve = "trump_approve", vs_vote_2024 = "vote_2024", vs_votechoice_2024 = "vote_choice_2024",
          sci_know_self = "sci_know_self", saf_familiar = "saf_familiar", saf_safe = "saf_safe", climate_change = "climate_change",
          setNames(paste0("sciknow_", 1:9), paste0("sciknow", 1:9)))
for (v in names(cmap)) d[, paste0("cov_", cmap[[v]]) := as.integer(zap_labels(k[[v]]))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "goldfarb_2026_aviation_fuel.csv"))
