##Odd-profile conjoints (eye-tracking lab study; candidate and immigrant scenarios) from
##Bansak, K., & Jenke, L. (2025). Odd profiles in conjoint experimental designs: Effects on
##survey-taking attention and behavior. Political Analysis, 33(4), 315-338.
##https://doi.org/10.1017/pan.2025.1 (open access, CC BY)
##Replication data: Harvard Dataverse doi:10.7910/DVN/6PXYGY, CC0 1.0. Files read (inside
##replication_materials.zip, itself inside the deposited zip):
##data/candidate/resp-trial_candidate_conj.csv, data/immigrant/resp-trial_immigrant_conj.csv.
##Also read as text: readme.txt, data/variable_codebook.txt,
##code/helper_functions/preprocess_conj_data_*.R (not run), and the article (Cambridge HTML).
##Usage: Rscript bansak_2025.R <dir holding the candidate/ and immigrant/ folders> <output dir>
##
##147 participants of the Duke Fuqua Behavioral Research subject pool (65% students),
##June 15 - September 9, 2022, eye-tracked in the lab. Each completed BOTH scenarios (order
##randomized): 60 pairs of hypothetical US political candidates and 60 pairs of hypothetical
##immigrants applying for US residency. TWO TABLES (different attribute sets):
##  bansak_2025_odd_profiles_candidate: 145 participants, 8 attributes (age, gender, party,
##    prior political experience, job, education, two issue positions; iss1 = taxes on the
##    wealthy, iss2 = gun control, per the authors' code).
##  bansak_2025_odd_profiles_immigrant: 142 participants, 8 attributes (age, gender,
##    language, migration type, origin, job, education, reason for settling).
##A few participants have fewer than 60 trials (56-59); kept as deposited.
##task = trialnums (1-60), profile = 1/2 (cand1*/cand2*, the first/second profile in the
##table): recorded. choice = candchoice/immigchoice (preferred profile, forced choice; one
##per task, checked). Wording not in the deposit or the article text (the article: respondents
##chose their "preferred profile"; paraphrase in the design record).
##Within-subject design conditions (blocks of 15 trials, block order randomized):
##trial_condition = treatnum as text (Normal, Incongruent, Nonsensical, Combined per the
##codebook); trial_block = treat_iter (1-4, position of the condition in the respondent's
##sequence). RESTRICTIONS: the level SETS depend on the condition (article sec. 3.1: "varying
##the degree of oddness across the four designs required changing the attribute levels and/or
##attributes themselves across conditions"); the Normal condition's sets contain no "odd"
##(incongruent or nonsensical) combinations, which the other conditions allowed (authors'
##code lists them, e.g. a 25-year-old Governor/Senator/Representative or medical doctor).
##E.g. candidate age 25 occurs only in Nonsensical/Combined, 41 only in Normal/Incongruent;
##so the pooled level shares are unequal (25 and 41 about 12% each). Within a condition the
##article says levels "were randomized independently and uniformly" (checked: every level pair
##occurs, max/min level share <= 1.19 within each condition). Attribute order: "randomized
##order across respondents and conditions but held fixed for the duration of the condition
##for each respondent" (article), i.e. one order per respondent x condition block; not
##recorded. Profiles were shown as a table, two columns x eight rows (article, Figure A.1).
##No task is repeated (checked: no task repeats an earlier pair, same or swapped).
##No survey weight (lab sample; none in the deposit).
##No respondent covariates are deposited. The eye-tracking measures (resp-trial_*_fix.csv:
##fixation counts and durations per attribute) are not included; use the deposit.
##Dropped: nothing identifying; subjid (anonymized lab id) is kept as id.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cond <- c("1" = "Normal", "2" = "Incongruent", "3" = "Nonsensical", "4" = "Combined")
build <- function(f, pre, chv, at, n_id, tab) {
  s <- fread(file.path(raw, f), colClasses = list(character = paste0(pre, rep(1:2, each = length(at)), at)))
  stopifnot(uniqueN(s$subjid) == n_id, !anyDuplicated(s[, .(subjid, trialnums)]), all(s[[chv]] %in% 1:2))
  rows <- lapply(1:2, function(p) {
    d <- data.table(id = as.integer(s$subjid), task = as.integer(s$trialnums), profile = p, choice = as.integer(s[[chv]] == p))
    for (x in at) { v <- s[[paste0(pre, p, x)]]; stopifnot(!anyNA(v), all(v != "")); d[, paste0("attr_", x) := v] }
    d[, trial_condition := unname(cond[as.character(s$treatnum)])][, trial_block := as.integer(s$treat_iter)]
  })
  d <- rbindlist(rows)
  stopifnot(!anyNA(d$trial_condition), d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(tab, ".csv")))
}
build("candidate/resp-trial_candidate_conj.csv", "cand", "candchoice",
      c("age", "gender", "party", "polex", "job", "educ", "iss1", "iss2"), 145, "bansak_2025_odd_profiles_candidate")
build("immigrant/resp-trial_immigrant_conj.csv", "immig", "immigchoice",
      c("age", "gender", "lang", "migtype", "origin", "job", "educ", "settling"), 142, "bansak_2025_odd_profiles_immigrant")
