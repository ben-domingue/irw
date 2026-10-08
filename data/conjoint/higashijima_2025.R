##Election-timing conjoints (Japan) from
##Higashijima, M., Shimizu, N., Washida, H., & Yanai, Y. (2025). Partisan reactions to endogenous
##election timing: Evidence from conjoint experiments in Japan. Political Behavior.
##https://doi.org/10.1007/s11109-025-10106-7
##Replication data: Harvard Dataverse doi:10.7910/DVN/WWKXEU, CC0 1.0. Files read:
##et_survey_2021march.Rds and et_survey_2022jan.Rds (long tibbles: ID, task, profile, selected,
##each attribute as an English factor plus <attr>_jpn with the Japanese text shown).
##analysis_PB_HSWY.qmd was read as text. The article (CC BY-NC-ND, Springer) could not be
##retrieved, so the outcome wording and sample counts are not checked against it.
##Usage: Rscript higashijima_2025.R <dir holding the two .Rds> <output dir>
##
##Respondents compared pairs of hypothetical general-election scenarios (how and why the
##election was called). Two surveys with different attribute sets = two tables:
##  higashijima_2025_election_timing_2021: March 2021, 1,710 respondents, 5 tasks, 8 attributes:
##    remaining term (5 levels), reason for the election (8), economic policy (3), pledge
##    achievement (3), cabinet approval (20%-60%), newspaper evaluation (expected/surprise),
##    economic growth (4 trajectories), opposition coordination (5).
##  higashijima_2025_election_timing_2022: January 2022, 2,577 respondents, 8 tasks, 8 attributes:
##    remaining term (7 levels, 0 to 3 years by half years), reason (8), economic policy (3),
##    how the PM decided (4), cabinet approval, newspaper evaluation, economy (3), opposition (5).
##Level text = the Japanese text shown (<attr>_jpn), except cabinet approval, which the
##deposit stores only as "20%".."60%" (no Japanese column); label_language ja.
##Outcome: choice = `selected` (exactly one profile per task). The question wording is not in
##the deposit and the article could not be read: unknown. The authors analyse it as the
##preferred scenario (marginal means with projoint's measurement-error correction).
##Restrictions (the authors' cjoint constraint lists, qmd L627-641 and L821-839):
##  2021: a remaining term of 0 occurs only with reason "full term" (任期満了のため) and vice
##    versa (holds exactly in the data). Not in the authors' list, but in the data a remaining
##    term of 0 never occurs with newspaper "sudden" (突然の解散と選挙実施; 0 of 292 profiles).
##  2022: remaining term 0 occurs only with how = "term expired" (任期満了のため) and vice versa
##    (holds exactly). The authors' code also forbids remaining term 0 with any reason other
##    than "full term", but the data contain 2,179 such profiles (0 with leader change,
##    no-confidence, ...); "full term" itself occurs only with remaining term 0. Flagged.
##Attribute order is not recorded. Level shares are unequal for remaining term and reason (the
##term-0 level is rare because of the restriction above); no probabilities are documented.
##No survey weight in the deposit. No task repeats an earlier pair (data check).
##Covariates: cov_age (years); cov_party_group: the authors' grouping of party ID (qmd
##L1226-1228, L1396-1398): party codes 1, 4 = "government", 88 = "independent", 2,3,5,6,7 (2022
##also 8, 11) = "opposition", other codes (99 etc.) blank. Raw party, gender and education codes
##are dropped because their value labels are not deposited.
##Dropped: Qualtrics ResponseId (ID, re-keyed to integers), free-text answers (*_TEXT),
##timers, display-order (*_DO_*) columns, knowledge items and the authors' derived scores.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(file, attrs, gov, opp, n_id, n_task, name) {
  s <- as.data.table(readRDS(file.path(raw, file)))
  d <- s[, .(src = ID, task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected))]
  for (v in attrs) {
    j <- paste0(v, "_jpn")
    txt <- if (j %in% names(s)) as.character(s[[j]]) else as.character(s[[v]])
    stopifnot(!anyNA(txt), nrow(unique(data.table(txt, as.character(s[[v]])))) == uniqueN(txt), uniqueN(txt) == uniqueN(s[[v]]))
    d[, paste0("attr_", v) := trimws(txt)]
  }
  pg <- fifelse(s$party %in% gov, "government", fifelse(s$party == 88, "independent", fifelse(s$party %in% opp, "opposition", NA_character_)))
  d[, cov_age := as.integer(s$age)][, cov_party_group := pg]
  stopifnot(uniqueN(d$src) == n_id, d[, .N, src][, all(N == 2 * n_task)], d[, sum(choice), .(src, task)][, all(V1 == 1)])
  d[, id := match(src, sort(unique(src)))][, src := NULL]
  setcolorder(d, c("id", "task", "profile", "choice"))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
  d
}
d1 <- build("et_survey_2021march.Rds", c("remain", "reason", "econ_policy", "achievement", "popularity", "newspaper", "growth", "opposition"),
            c(1, 4), c(2, 3, 5, 6, 7), 1710, 5, "higashijima_2025_election_timing_2021")
stopifnot(d1[attr_remain == "残り任期0年(前回選挙から4年経過)", all(attr_reason == "任期満了のため")], d1[attr_reason == "任期満了のため", all(attr_remain == "残り任期0年(前回選挙から4年経過)")])
d2 <- build("et_survey_2022jan.Rds", c("remain", "reason", "econ_policy", "how", "popularity", "newspaper", "growth", "opposition"),
            c(1, 4), c(2, 3, 5, 6, 7, 8, 11), 2577, 8, "higashijima_2025_election_timing_2022")
stopifnot(d2[attr_remain == "0年", all(attr_how == "任期満了のため")], d2[attr_how == "任期満了のため", all(attr_remain == "0年")],
          d2[attr_reason == "任期満了のため", all(attr_remain == "0年")], d2[attr_remain == "0年" & attr_reason != "任期満了のため", .N] == 2179)
