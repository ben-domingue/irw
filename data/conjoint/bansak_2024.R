##Algorithmic vs human decision-maker conjoints (pre-trial release; bank loans) from
##Bansak, K., & Paulson, E. (2024). Public attitudes on performance for algorithmic and
##human decision-makers. Preprint, OSF/SocArXiv. https://doi.org/10.31219/osf.io/pghmx
##Replication data: Harvard Dataverse doi:10.7910/DVN/1QWTHN, CC0 1.0. Files read (inside
##replication_materials.zip): data/conjdat_crime.csv, data/conjdat_loans.csv, data/respdat.csv;
##data/variable_codebook.txt and the preprint (Research Design, Materials and Methods,
##Figures 1 and 9-11) read for wording and display.
##Usage: Rscript bansak_2024.R <dir holding conjdat_*.csv and respdat.csv> <output dir>
##
##9,030 US adults (Qualtrics panel, quotas; only respondents passing two attention checks
##were kept by the authors). Each respondent was randomized to ONE scenario, so the deposit
##gives two experiments with different attribute texts, analysed separately in the paper:
##TWO tables, bansak_2024_algorithm_dm_crime (4,787 in the file) and
##bansak_2024_algorithm_dm_loans (4,243). 10 pairs of decision-maker (DM) profiles each.
##Three respondents per scenario (60 rows each file) have no attribute values ("collection
##error", authors' helper process_conjdata.R drops them) and are dropped: 4,784 and 4,240
##respondents, exactly the n of the paper's Table 1.
##Profiles were tables (Figures 1, 9-11): column header "Performance of JUDGE/MANAGER/ALGORITHM
##(A/B)", rows DEFENDANT CRIME RATE or LOAN DEFAULT RATE, WHITE FALSE POSITIVE RATE, MINORITY
##FALSE POSITIVE RATE, shown as percentages ("13%" crime; "2.5%", "9.0%" loans). Stored:
##  attr_decision_maker: "JUDGE" (crime) / "MANAGER" (loans) / "ALGORITHM", from source `type`
##    (human/algo), the header word in the paper's figures.
##  attr_crime_rate (or attr_default_rate), attr_white_fpr, attr_minority_fpr: the source
##    integers/halves formatted as in the figures ("%d%%" crime, values 10-50; "%.1f%%" loans,
##    values 0-10 in steps of 0.5; the paper says "integers" for loans but the data hold halves).
##  attr_developer: who developed the algorithm ("private firms" / "university researchers",
##    the source text), shown in the scenario text; "(not shown)" for human DMs.
##  attr_locale: "in your jurisdiction" / "in a large U.S. city" (crime, cplace) or
##    "at your bank" / "in a large U.S. city" (loans, bplace), source text, scenario framing.
##  Developer and locale were randomized per respondent (constant over a respondent's tasks).
##trial_matchup: the between-respondent DM-type arm (humans / algos / faceoff); in faceoff
##one DM is human and one an algorithm, and trial_forder records which came first
##(randomized between respondents). Rates were "uniformly and independently randomized".
##Outcomes (wording paraphrased in the paper; the instrument is not deposited):
##  choice = pref: which DM in the pair the respondent would prefer making decisions (forced).
##  rating = rate: performance rating of each DM, 1 (very bad) to 7 (very good) (the
##    preregistration osf.io/twu4h says 1-6; the data and paper are 1-7).
##Covariates from respdat.csv (text as stored): cov_age, cov_gender (Female -> female, Male ->
##male, Non-binary / third gender and Prefer to self-describe -> other, Prefer not to say -> NA),
##cov_education, cov_party_id (party: Democrat/Republican/Independent/Other/No preference),
##cov_rep_str, cov_dem_str, cov_party_lean, cov_state, cov_hispanic, cov_race, cov_income,
##cov_duration_sec (survey duration; the source stores minutes, x 60), the post-task belief and
##priority rankings (cov_priority_*, cov_ratelow_*, cov_fair_*: ranks 1-3 as stored) and
##cov_ai_enthu / cov_ai_worry (answer text). Qualtrics ResponseId re-keyed to integers. No
##survey weight in the deposit. Derived unfairness (|MFPR - WFPR|) is not stored.
##Check: in the faceoff arm the human DM is chosen 7.6 (crime) and 4.3 (loans) percentage
##points more often than the algorithm, with 1,567 / 1,416 respondents: as in the paper.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "respdat.csv"), encoding = "UTF-8")
stopifnot(!anyDuplicated(r$ResponseId))
gmap <- c("Female" = "female", "Male" = "male", "Non-binary / third gender" = "other",
          "Prefer to self-describe" = "other", "Prefer not to say" = NA)
stopifnot(all(r$gender %in% names(gmap)))
nz <- function(x) fifelse(x == "", NA_character_, as.character(x))
cv <- r[, .(ResponseId, cov_age = as.integer(age), cov_gender = unname(gmap[gender]),
            cov_education = nz(education), cov_party_id = nz(party), cov_rep_str = nz(rep_str),
            cov_dem_str = nz(dem_str), cov_party_lean = nz(party_lean), cov_state = nz(state),
            cov_hispanic = nz(hispanic), cov_race = nz(race), cov_income = nz(income),
            cov_duration_sec = round(duration * 60, 1),
            cov_priority_rate_low = priority_rate_low, cov_priority_fpr_low = priority_fpr_low,
            cov_priority_fpr_equal = priority_fpr_equal, cov_ratelow_human = ratelow_human,
            cov_ratelow_algo_uni = ratelow_algo_uni, cov_ratelow_algo_firm = ratelow_algo_firm,
            cov_fair_human = fair_human, cov_fair_algo_uni = fair_algo_uni, cov_fair_algo_firm = fair_algo_firm,
            cov_ai_enthu = nz(ai_enthu), cov_ai_worry = nz(ai_worry))]
build <- function(sc) {
  s <- fread(file.path(raw, paste0("conjdat_", sc, ".csv")), encoding = "UTF-8")
  bad <- s[is.na(att_rate) | is.na(att_wfpr) | is.na(att_mfpr), unique(ResponseId)]
  stopifnot(length(bad) == 3)
  s <- s[!ResponseId %in% bad]
  stopifnot(s[, .N, ResponseId][, all(N == 20)], all(substr(s$prof, 1, 1) == s$task))
  human <- if (sc == "crime") "JUDGE" else "MANAGER"
  fmt <- if (sc == "crime") function(x) sprintf("%d%%", as.integer(x)) else function(x) sprintf("%.1f%%", x)
  if (sc == "crime") stopifnot(all(s$att_rate == round(s$att_rate)))
  place <- if (sc == "crime") s$cplace else s$bplace
  stopifnot(!anyNA(place), all(s$type %in% c("human", "algo")))
  d <- data.table(ResponseId = s$ResponseId, task = match(s$task, LETTERS), profile = as.integer(substr(s$prof, 2, 2)),
                  choice = as.integer(s$pref), rating = as.integer(s$rate),
                  attr_decision_maker = fifelse(s$type == "human", human, "ALGORITHM"),
                  rate = fmt(s$att_rate), attr_white_fpr = fmt(s$att_wfpr), attr_minority_fpr = fmt(s$att_mfpr),
                  attr_developer = fifelse(s$type == "human", "(not shown)", s$developer),
                  attr_locale = place, trial_matchup = s$matchup, trial_forder = s$forder)
  setnames(d, "rate", if (sc == "crime") "attr_crime_rate" else "attr_default_rate")
  stopifnot(!anyNA(d$attr_developer), d[, sum(choice), .(ResponseId, task)][, all(V1 == 1)], all(d$rating %in% 1:7))
  d <- merge(d, cv, by = "ResponseId", all.x = TRUE, sort = FALSE)
  stopifnot(!anyNA(d$cov_age))
  ids <- sort(unique(d$ResponseId))
  d[, id := match(ResponseId, ids)][, ResponseId := NULL]
  setcolorder(d, c("id", "task", "profile", "choice", "rating"))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("bansak_2024_algorithm_dm_", sc, ".csv")))
  cat(sc, nrow(d), uniqueN(d$id), "\n")
}
build("crime"); build("loans")
