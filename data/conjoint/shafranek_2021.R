##Roommate-choice conjoint (US college students) from
##Shafranek, R. M. (2021). Political considerations in nonpolitical decisions: A conjoint analysis
##of roommate choice. Political Behavior, 43(1), 271-300. https://doi.org/10.1007/s11109-019-09554-9
##(online 2019)
##Replication data: Harvard Dataverse doi:10.7910/DVN/GUATS6, CC0 1.0, no restricted files.
##File read: conjoint.csv (Dataverse "original format"; one row per profile, 4,100 rows).
##replication.R read as text. The article is paywalled and was not read.
##Usage: Rscript shafranek_2021.R <dir holding conjoint.csv> <output dir>
##
##205 respondents, all college students (year_in_school: first year ... senior), 10 tasks of 2
##hypothetical roommates (20 rows each), 11 attributes: race, sexual orientation (LGBT /
##Straight), religion, party (Democrat / Independent / Republican), political interest,
##cleanliness, music, hobby, weekend social life, value, bedtime. Level text is as stored in the
##deposit (the authors' cjoint attribute list uses the same strings); the displayed wording is not
##documented.
##Task and profile are INFERRED: the file has no task/profile column and its rows cycle through
##the 205 respondents (row k*205 + i is respondent i's k-th row). Within each respondent,
##consecutive rows 1-2, 3-4, ... are taken as the pairs: every one of the 1,977 answered pairs
##then has exactly one chosen profile, while the shifted pairing (2-3, 4-5, ...) gives 0, 1 or 2
##chosen at random. Task order is assumed to follow row order.
##Outcomes (wording unknown; not in the deposit):
##  choice: which of the two roommates the respondent chose; no opt-out. Tasks without a choice
##    (choice blank) are kept when a rating exists.
##  rating: 1-7 rating of each profile; higher = more favourable (chosen profiles average 5.0,
##    unchosen 4.1); anchors unknown. 784 profile ratings are missing.
##Rows with neither outcome are omitted. 2 respondents (40 rows) have no attribute values at all
##(blank in source = missing, not "not shown") and are dropped: 203 respondents, 4,030 rows; 38
##kept tasks have ratings but no choice.
##Restrictions: the authors' cjoint design (replication.R, makeDesign) weights sexual orientation
##LGBT 1/5, Straight 4/5; everything else uniform. Race shares in the data are also unequal
##(White 48%, Asian American 21%, Black 16%, Hispanic 15%), not documented.
##Covariates (respondent answers, as stored): year in school, party (pid3, lean, pid3_withlean),
##age, gender, race (multi-select), own religion, LGBT, hobbies (multi-select), music,
##cleanliness, social life, values, bedtime, importance ranks of 11 roommate traits (*_rank),
##and perceived party association of 15 activities (*_pid).
##Dropped: Qualtrics ResponseId (re-keyed 1..n in order of first appearance), the row index,
##pid_other (free text), the authors' derived match / relative-party / recoded variables
##(traits_*_match, traits_pid_relative, polinterest_r).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "conjoint.csv"), encoding = "UTF-8")
x[, r := rowid(ResponseId)]
d <- data.table(id = match(x$ResponseId, unique(x$ResponseId)), task = (x$r + 1L) %/% 2L,
                profile = 2L - x$r %% 2L, choice = as.integer(x$choice), rating = as.integer(x$rating))
an <- c(race = "traits_race", sexual_orientation = "traits_lgbt", religion = "traits_religion", party = "traits_pid",
        political_interest = "traits_polinterest", cleanliness = "traits_clean", music = "traits_music",
        hobby = "traits_hobby", social = "traits_social", value = "traits_value", bedtime = "traits_bedtime")
for (k in names(an)) d[, paste0("attr_", k) := fifelse(x[[an[[k]]]] == "", NA_character_, x[[an[[k]]]])]
cv <- c("year_in_school", "pid3", "pid_lean", "pid3_withlean", "age", "gender", "race", "r_religious", "r_lgbt",
        "r_hobbies", "r_music", "r_cleanliness", "r_social", "r_values", "r_bedtime",
        grep("_rank$|_pid$", names(x), value = TRUE))
for (v in cv) d[, paste0("cov_", sub("^r_", "own_", v)) := x[[v]]]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][!is.na(V1), all(V1 == 1)])
d[, miss := anyNA(.SD), .SDcols = patterns("^attr_"), by = .(id, task)]
d <- d[miss == FALSE & !(is.na(choice) & is.na(rating))][, miss := NULL]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "shafranek_2021_roommate_choice.csv"))
