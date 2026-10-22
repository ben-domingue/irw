##Congressional candidate conjoint with randomized news and information environment from
##Funck, A. S., & McCabe, K. T. (2022). Partisanship, information, and the conditional effects
##of scandal on voting decisions. Political Behavior, 44(3), 1389-1409.
##https://doi.org/10.1007/s11109-020-09670-x
##Replication data: Harvard Dataverse doi:10.7910/DVN/0IN4PX, CC0 1.0, no restricted files.
##File read: candlongfin.tab, downloaded in its original format (candlongfin.csv; one row per
##respondent x candidate profile). Read as text: readme.txt and the authors' repfilescandal.Rmd,
##which is the only documentation of the variables (there is no codebook).
##Usage: Rscript funck_2022.R <dir holding candlongfin.csv> <output dir>
##
##2,135 US respondents (Qualtrics; the deposit documents neither the panel nor the fielding
##dates), 3 tasks of 2 hypothetical congressional candidates, 6 profiles each: 12,810 rows.
##32 tasks (64 rows) where neither profile has a choice are dropped (the design is forced
##choice, so a task with no chosen profile cannot be stored); 61 of those rows carried
##ratings, which are lost with them. Four respondents lose all three tasks, so the table has
##2,131 respondents, 6,373 tasks and 12,746 rows.
##The candidate's number within the respondent is recorded twice, as `time` (1-6) and as the
##`.1`-`.6` suffix of `X`; the two always agree. task is that number paired up (1-2, 3-4, 5-6)
##and profile is its parity (odd = first of the pair). Whether the first of a pair was shown on
##the left is not documented. The Rmd's first-task subset is `time < 3` (line 711), which fixes
##the reading of `time`.
##
##Design. Party and recent news are shown to everyone; the other eight characteristics are
##shown or withheld by the information environment, randomized PER TASK (`info.p`:
##low = 0 characteristics, medium = 3, high = 8; Rmd line 55). A characteristic that was not
##displayed is the reserved text "(not shown)" (the source writes "Not Shown").
##trial_info_environment holds low / medium / high. Every task pairs one Democrat with one
##Republican. Level shares are unequal for race (White 0.50, the three others ~0.17) and
##profession (Lawyer 0.34, Business owner 0.22, the rest ~0.11); gender, immigration,
##abortion, spending, religion and age are near-uniform.
##attrpos_ is the rank of the characteristic among those DISPLAYED, blank when it was not
##displayed: the deposit records one random order of all eight characteristics per respondent
##(the `.n` columns, a permutation of 1-8, constant across that respondent's tasks), and the
##displayed subset keeps its relative order.
##
##Outcomes, all about the same tasks, so one table:
##  choice: a vote between the two candidates, forced (exactly one profile per task).
##  rating_shares_views, rating_good_morals, rating_cares: how much the respondent agreed that
##    the candidate shares their views / has good morals / cares about people like them. The
##    deposit stores these rescaled to 0-0.25-0.5-0.75-1 (`shares.ps`, `moral.ps`, `cares.ps`),
##    i.e. a 5-point agree scale mapped to 0-1; they are kept as stored, not rescaled back.
##The question wordings are the Rmd's descriptions (Rmd lines 48 and 62), hence marked as
##paraphrases in design_outcomes.csv. The same instrument was re-fielded by Miller & Ziegler
##(2024) (doi:10.7910/DVN/JQOPNW, built here as miller_2024_scandal_candidates), whose
##Qualtrics print-out gives the vote question as "If this election were being held in your
##district, would you vote for Candidate A or Candidate B?" and the three agree items on a
##1 = Strongly disagree to 5 = Strongly agree scale. Those are that study's own materials, so
##they are recorded as evidence rather than as this table's wording.
##
##Covariates. cov_age_group (`agecat`), cov_income (`inc`, answer text), cov_abortion,
##cov_immigration, cov_spending (the respondent's own position, answer text; "-99" -> NA),
##cov_race (rebuilt from the deposit's mutually exclusive whitenh / blacknh / hisp / asiannh
##dummies -> white / black / hispanic / asian; 57 respondents are 0 on all four and are NA).
##`partydtr` (7-point party identification), `edu3` and `ideoltc` ship as bare codes with no
##codebook, so they keep the codes under cov_party_id7_code, cov_education_code and
##cov_ideology_code. trial_time_sec is `time.p`, the seconds spent on the task (identical on
##both profiles of a task). Dropped: the authors' rescaled copies (`partydtr.s`, `incn.s`),
##the party dummies (`dem`, `rep`, `demrep`), the race dummies themselves, the `op*` columns
##(the other profile's attributes and ratings, already rows of the same task), the `.shown`
##flags (recoverable from "(not shown)") and the raw `.n` order columns.
##PII / identifiers dropped: the Qualtrics ResponseId, re-keyed to 1..n in first-appearance
##order. No survey weight ships with the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "candlongfin.csv"))
stopifnot(nrow(s) == 12810L, uniqueN(s$ResponseId) == 2135L)

s[, sfx := as.integer(sub(".*\\.", "", X))]
stopifnot(s[, .N, sfx][, all(N == 2135L)], s[, uniqueN(sfx), ResponseId][, all(V1 == 6L)])
stopifnot(s[, all(as.integer(time) == sfx)])   # `time` is the profile number 1-6
s[, task := (sfx + 1L) %/% 2L]
s[, profile := 2L - sfx %% 2L]

## forced choice: drop tasks where neither profile was chosen
s[, chosen_in_task := sum(!is.na(chosen.p)), .(ResponseId, task)]
stopifnot(s[, .N, .(ResponseId, task)][, all(N == 2L)], s[chosen_in_task > 0L, all(!is.na(chosen.p))])
s <- s[chosen_in_task > 0L]
stopifnot(nrow(s) == 12746L, uniqueN(s$ResponseId) == 2131L)

ATTR <- c(gender = "gender", age = "age", religion = "religion", race = "race",
          profession = "profession", abortion = "abortion", immigration = "immigration",
          spending = "spending")
## attribute order: one permutation of 1..8 per respondent; position among those displayed
P <- as.matrix(s[, paste0(ATTR, ".n"), with = FALSE])
S <- as.matrix(s[, paste0(ATTR, ".shown"), with = FALSE]) == 1L
stopifnot(all(apply(P, 1L, function(x) all(sort(as.integer(x)) == 1:8))),
          s[, uniqueN(do.call(paste, .SD)), ResponseId, .SDcols = paste0(ATTR, ".n")][, all(V1 == 1L)])
pos <- t(sapply(seq_len(nrow(P)), function(i) {
  v <- rep(NA_integer_, length(ATTR))
  k <- which(S[i, ])
  if (length(k)) v[k] <- rank(P[i, k])
  v
}))

d <- data.table(id = as.integer(frank(s$ResponseId, ties.method = "dense")),
                task = s$task, profile = s$profile,
                choice = as.integer(s$chosen.p),
                rating_shares_views = s$shares.ps, rating_good_morals = s$moral.ps,
                rating_cares = s$cares.ps,
                attr_party = as.character(s$party.p), attr_news = as.character(s$news.p))
notshown <- function(x) { x <- as.character(x); fifelse(x == "Not Shown", "(not shown)", x) }
for (nm in names(ATTR)) set(d, j = paste0("attr_", nm), value = notshown(s[[paste0(ATTR[[nm]], ".p")]]))
for (j in seq_along(ATTR)) set(d, j = paste0("attrpos_", names(ATTR)[j]), value = as.integer(pos[, j]))
d[, trial_info_environment := c("0" = "low", "0.5" = "medium", "1" = "high")[as.character(s$info.p)]]
d[, trial_time_sec := s$time.p]

na99 <- function(x) { x <- as.character(x); fifelse(x == "-99", NA_character_, x) }
d[, cov_age_group := as.character(s$agecat)]
d[, cov_income := na99(s$inc)]
d[, cov_abortion := na99(s$abortion)]
d[, cov_immigration := na99(s$immigration)]
d[, cov_spending := na99(s$spending)]
race <- fcase(s$whitenh == 1L, "white", s$blacknh == 1L, "black",
              s$hisp == 1L, "hispanic", s$asiannh == 1L, "asian")
d[, cov_race := race]
d[, cov_party_id7_code := as.integer(s$partydtr)]
d[, cov_education_code := as.integer(s$edu3)]
d[, cov_ideology_code := as.integer(s$ideoltc)]

stopifnot(d[, uniqueN(id)] == 2131L,
          d[, sum(choice), .(id, task)][, all(V1 == 1L)],              # forced choice
          d[, uniqueN(attr_party), .(id, task)][, all(V1 == 2L)],      # one D, one R
          d[, all(attr_party %in% c("Democrat", "Republican"))],
          !anyNA(d[, grep("^attr_", names(d)), with = FALSE]),
          d[, all(trial_info_environment %in% c("low", "medium", "high"))],
          d[trial_info_environment == "low", all(attr_gender == "(not shown)")],
          d[trial_info_environment == "high", all(attr_gender != "(not shown)")],
          d[, uniqueN(trial_info_environment), .(id, task)][, all(V1 == 1L)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "funck_2022_scandal_candidates.csv"))
