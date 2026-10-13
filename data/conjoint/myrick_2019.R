##Covert-operation vignette experiments (United States) from
##Myrick, R. (2020). Why so secretive? Unpacking public attitudes toward secrecy and success
##in U.S. foreign policy. The Journal of Politics, 82(3), 828-843. https://doi.org/10.1086/707308
##Replication data: Harvard Dataverse doi:10.7910/DVN/JWJRME, CC0 1.0. Files read: 3_exp1_raw.tab,
##3_exp2_raw.tab, 3_exp2_raw_mcheck.tab (scenario order only), 3_exp3_raw.tab, 3_exp4_raw.tab (raw
##Qualtrics exports, tab-separated, quoted fields), the prepped 2_exp1..4_data.tab (only their caseid
##lists, to define the analysis sample), 1_myrick2019_appendix.pdf (Appendix A: vignette text and
##randomization), 1_myrick2019_dataprep.R (read as text, not run).
##Usage: Rscript myrick_2019.R <dir holding the .tab files, saved without the 2_/3_ prefix, e.g.
##  exp1_raw.tab ...> <output dir>
##
##Four U.S. Lucid samples fielded November 2018, each respondent reading TWO vignettes (a
##dictator scenario and a civil-war-spillover scenario), so task = 1, 2 and profile = 1. Four tables
##(different attribute sets / samples): myrick_2019_covert_exp1 ... _exp4. The analysis sample is the
##authors' (prepped file caseids: the fastest respondents before treatment, "speeders", are dropped):
##1,055 / 1,031 / 1,065 / 1,073 respondents. Raw responseid (Qualtrics response ID), zip code,
##free-text "other" answers and the Lucid code columns are dropped (PII FOUND: Qualtrics response ID
##and 5-digit zip code in the raw exports).
##Vignette (Appendix A, bullet form): "A dictator in [region] is widely known for torturing and
##repressing his people and threatening stability in the region. Rebels ... have been unsuccessful so
##far. After debating different policies, the U.S. government decided to [action]. [secrecy]" or
##"A country in [region] is experiencing a highly destructive civil war ... [action]. [secrecy]".
##Then the rating; then "Now consider the results: No American lives were lost, but there were high
##numbers of civilian casualties. After one year, the operation was ultimately [outcome]", then the
##second rating (experiments 1-3 only; experiment 4 shows everything at once, one rating).
##Randomized per vignette: region (Asia, Africa, Latin America, the Middle East), the action
##(force / money and weapons), secrecy (informed / kept secret), outcome (success / failure).
##Secrecy is a CROSS-OVER within respondent (one vignette secret, the other not), so restrictions =
##yes. The scenario kind (dictator / civil war) is not randomized: it is trial_scenario.
##Order: respondents saw the two vignettes in random order (Appendix A). The order is recorded
##only in 3_exp2_raw_mcheck.tab (rmm_order, same respondents, joined by caseid): experiment 2 has
##task = order shown (task_source recorded). In experiments 1, 3, 4 the order is not recorded and
##task 1 = dictator, task 2 = civil war by question numbering only (task_source = inferred).
##Outcomes (HIGHER = more favourable, 1 Disapprove Strongly, 2 Disapprove Somewhat, 3 Disapprove
##Slightly, 4 Neutral, 5 Approve Slightly, 6 Approve Somewhat, 7 Approve Strongly; the coding is
##the authors' dataprep recode of the text answers; "How much do you approve or disapprove of the
##actions taken by the U.S. government in this situation?"):
##  rating       = ex-ante approval, asked BEFORE the outcome was shown (so attr_outcome had not been
##                 displayed yet), experiments 1-3; in experiment 4 the single rating.
##  rating_after = ex-post approval ("Considering this new information ..."), experiments 1-3.
##The cross-over assignment of secrecy for the civil-war vignette is read from which secrecy-specific
##question was answered (RMM201_nocov = informed, RMM202_cov = kept secret), as the authors' code does.
##Covariates (raw text): cov_gender (malefemale), cov_age (age_sel; one "99 +" in exp3 -> NA), cov_education (educ),
##cov_race (educ text; the mangled "Some other race - Type in race" fixed to "Some other race"),
##cov_income (text band), cov_state, cov_party_id (pid_1 text; "No preference", "Another party" kept as
##text), cov_party_strength (pid_2), cov_party_lean (pid_3), cov_ideology (ideo), cov_political_interest
##(int_pol), cov_duration_sec (duration; experiments 1-3, 4 has none), cov_attention_pass (experiment 2
##only: the authors' passed_mcheck, "what did the government do in the LAST scenario", correct = 1).
##No survey weight. Dropped: start/end times, vote items, nationalism items (nat_1/2), phone-type,
##hhi/region/ethnicity numeric Lucid codes. Counts: Appendix A says n = 1,000 per experiment before
##speeders were dropped ("between 1100-1200 completed"); 1,055-1,073 here are the authors' kept sample.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) { k <- fread(file.path(raw, f), quote = "", sep = "\t", encoding = "UTF-8", colClasses = "character")
  k[, (names(k)) := lapply(.SD, function(x) trimws(gsub("^\"+|\"+$", "", x)))]; k }
lv <- c("Disapprove Strongly" = 1L, "Disapprove Somewhat" = 2L, "Disapprove Slightly" = 3L, "Neutral" = 4L,
        "Approve Slightly" = 5L, "Approve Somewhat" = 6L, "Approve Strongly" = 7L)
cv <- function(x) unname(lv[x])
cov_of <- function(r, e) {
  race <- sub("^Some other race.*", "Some other race", r$race)
  d <- data.table(caseid = as.integer(r$caseid), cov_gender = c(Male = "male", Female = "female")[r$malefemale],
    cov_age = suppressWarnings(as.integer(r$age_sel)), cov_education = r$educ, cov_race = race, cov_income = r$income, cov_state = r$state_sel,
    cov_party_id = r$pid_1, cov_party_strength = r$pid_2, cov_party_lean = r$pid_3, cov_ideology = r$ideo, cov_political_interest = r$int_pol)
  d[, cov_gender := unname(cov_gender)]
  if ("duration" %in% names(r)) d[, cov_duration_sec := as.integer(r$duration)]
  for (cc in setdiff(names(d), c("caseid", "cov_age", "cov_duration_sec"))) d[get(cc) == "", (cc) := NA]
  d
}
build <- function(e, name) {
  r <- rd(sprintf("exp%d_raw.tab", e)); p <- fread(file.path(raw, sprintf("exp%d_data.tab", e)))
  r <- r[as.integer(caseid) %in% p$caseid]; stopifnot(nrow(r) == uniqueN(p$caseid))
  r[, civ_secret := RMM201_nocov == ""]; stopifnot(all(r$civ_secret == (r$RMM202_cov != "")))
  informed <- "The government informed the American public about the operation."
  one <- function(sc) {
    dd <- sc == "dict"
    t1 <- if (dd) r$RMM101_t1 else r$RMM201_t1
    t2 <- if (dd) r$RMM101_t2 else NA_character_
    if (!dd) t2 <- ifelse(r$civ_secret, "SECRET", informed)
    d <- data.table(caseid = as.integer(r$caseid), trial_scenario = if (dd) "dictator" else "civil war",
      attr_region = if (dd) r$dict_region else r$civ_region)
    if (e == 2) d[, attr_public_opinion := ifelse(t1 == "", "(not shown)", t1)] else d[, attr_action := sub("^send in money", "send money", t1)]
    d[, attr_secrecy := t2]
    d[, attr_outcome := if (dd) r$RMM102_t3 else r$RMM202_t3]
    d[, rating := cv(if (dd) r$RMM101 else ifelse(r$civ_secret, r$RMM202_cov, r$RMM201_nocov))]
    if (e != 4) d[, rating_after := cv(if (dd) r$RMM102 else r$RMM202)]
    d
  }
  d <- rbind(one("dict"), one("civ"))
  ## civil-war secrecy: the exact secret/deceit wording of the dictator vignette in this experiment
  sw <- unique(r$RMM101_t2[r$RMM101_t2 != informed]); stopifnot(length(sw) == 1)
  d[attr_secrecy == "SECRET", attr_secrecy := sw]
  if (e == 3) cat("exp3 secrecy wording for the civil-war vignette is taken from the dictator vignette wording (Appendix A shows the same bracket text)\n")
  d[, task := ifelse(trial_scenario == "dictator", 1L, 2L)]; d[, profile := 1L]
  if (e == 2) {
    m <- rd("exp2_raw_mcheck.tab"); m <- m[, .(caseid = as.integer(caseid), rmm_order, RMM_mcheck_m = RMM_mcheck, RMM101_m = RMM101, dict_region_m = dict_region)]
    r2 <- r[, .(caseid = as.integer(caseid), RMM101, dict_region, RMM_mcheck, civ_secret)]
    j <- merge(r2, m, by = "caseid"); stopifnot(nrow(j) == nrow(r), all(j$RMM101 == j$RMM101_m), all(j$dict_region == j$dict_region_m))
    j[, dict_first := grepl("Myrick3$", rmm_order)]
    j[, mc := ifelse(RMM_mcheck == "I don't know.", "dk", ifelse(grepl("kept the operation completely secret", RMM_mcheck), "secret", "informed"))]
    ## last scenario shown: civil war if dictator first, dictator otherwise; correct answer = secrecy of that scenario
    j[, last_secret := ifelse(dict_first, civ_secret, !civ_secret)]
    j[, pass := as.integer((mc == "secret" & last_secret) | (mc == "informed" & !last_secret))]
    cat("exp2 manipulation-check pass rate (authors' rule):", mean(j$pass), "\n")
    d <- merge(d, j[, .(caseid, dict_first, pass)], by = "caseid")
    d[, task := ifelse(trial_scenario == "dictator", ifelse(dict_first, 1L, 2L), ifelse(dict_first, 2L, 1L))]
    d[, cov_attention_pass := pass]; d[, c("dict_first", "pass") := NULL]
  }
  d <- merge(d, cov_of(r, e), by = "caseid")
  setnames(d, "caseid", "id")
  setcolorder(d, c("id", "task", "profile"))
  stopifnot(!anyNA(d[, grep("^attr_|^rating", names(d), value = TRUE), with = FALSE]))
  setorder(d, id, task, profile)
  cat(name, ": respondents", uniqueN(d$id), "rows", nrow(d), "\n")
  fwrite(d, file.path(out, paste0(name, ".csv")))
  d
}
for (e in 1:4) invisible(build(e, paste0("myrick_2019_covert_exp", e)))
