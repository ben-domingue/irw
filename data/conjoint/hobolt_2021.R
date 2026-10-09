##BBC Director-General and lodger conjoints (Great Britain, 2017) from
##Hobolt, S. B., Leeper, T. J., & Tilley, J. (2021). Divided by the vote: Affective
##polarization in the wake of the Brexit referendum. British Journal of Political Science,
##51(4), 1476-1493. https://doi.org/10.1017/S0007123420000125
##Replication data: Harvard Dataverse doi:10.7910/DVN/35M5CV, CC0 1.0, no restricted files.
##Files read: bbc-data-raw.sav and lodger-data-raw.sav (Dataverse "original format" downloads;
##SPSS value labels give the level text). Read as text: README.md, bbc-/lodger-analysis-cleaning.R,
##bbc-/lodger-script.docx (the survey scripts: level lists, randomization code, screen HTML,
##question wording), bbc-/lodger-analysis.pdf. The deposit's other studies (BES, tracker,
##YouGov, Sky) are not conjoints and are not used.
##Usage: Rscript hobolt_2021.R <raw dir> <output dir>
##
##TWO TABLES (different attribute sets, separate fieldings; the authors analyse each alone):
##  hobolt_2021_brexit_bbc_dg: "Imagine that you are deciding who to appoint as the next
##    Director General of the BBC. You have received the following information about two
##    applicants and need to make a decision between them." 1,635 respondents (wave 2, fielded
##    2017-10/11 per respdate). choice = "Which of the two applicants would you prefer as the
##    next Director General of the BBC?" Attributes: name, age (32-68 years old), experience
##    (BBC years), degree, politics (2017 election support), eu (referendum campaign support),
##    occupation.
##  hobolt_2021_brexit_lodger: "Imagine that you have a spare room that you want to rent out to a
##    lodger. ..." 1,669 respondents (wave 1). choice = "Which of
##    the two lodgers would you prefer?" Attributes: name, age (19-44 years old), occupation,
##    volunteer, politics (2017 vote), eu (referendum vote), hobby.
##Each respondent saw 5 pairs (QPAIR1-5 -> task), profile 1 = left column (name_seen1_*),
##profile 2 = right (name_seen2_*). Forced choice: the answer is a name, mapped to the profile
##carrying that name (as the authors' cleaning script does); no opt-out, no rating. Every task
##was answered (8,175 and 8,345 chosen profiles, as in the analysis PDFs).
##Randomization (survey scripts): each profile's age/experience/degree/politics/eu/occupation
##(BBC) or age/occupation/volunteer/politics/eu/hobby (lodger) is drawn uniformly and
##independently for each pair; the 10 names are drawn WITHOUT REPLACEMENT from 11 (James, Tom,
##John, Steve, Chris, Paul, Claire, Sarah, Kate, Becky, Jenny), so no name repeats within a
##respondent. The name is the column heading; the six other attributes are table rows shown
##without row labels, in an order shuffled once per respondent and kept for all 5 pairs
##(list_table; row1_1..row6_1 store the order) -> attrpos_ columns (name has no position).
##The authors do not code the names by gender, so there is no crosswalk entry.
##Level text = SPSS value labels (= the script's level lists); repeated spaces squeezed (the
##lodger level "Helps out at  the local Catholic church" is displayed by HTML as one space).
##Covariates (SPSS value labels; Skipped/Not Asked -> NA, Refused/Prefer not to say -> NA): cov_age (Age, years),
##cov_gender (Gender 1 Male/2 Female), cov_age_group (AgeGroup), cov_region (Region_2GOR),
##cov_social_grade (SocialGrade), cov_education (Education_Level, highest qualification),
##cov_party_id (partyid_2017 "Generally speaking, do you think of yourself as Labour,
##Conservative, Liberal Democrat or what?"), cov_vote_euref (VoteEURef), cov_vote_2017 (Vote2017),
##cov_brexit_identity (rl3 "... do you think of yourself as: A Leaver / A Remainer / Neither /
##Don't know"), cov_survey_weight (BBC `Weight`, lodger `W8`; the analysis PDFs show unweighted
##main results). Timing, media use and work items are dropped. The fieldwork company is not
##named in the deposit.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(v) { r <- as.character(as_factor(v, levels = "labels")); r[r %in% c("Skipped", "Not Asked", "Refused", "Prefer not to say")] <- NA; r }
build <- function(file, attrs, wvar, outfile) {
  x <- read_sav(file.path(raw, file))
  n <- nrow(x)
  L <- list()
  for (t in 1:5) for (p in 1:2) {
    d <- data.table(id = as.integer(x$ID), task = t, profile = p)
    nm <- x[[sprintf("name_seen%d_t%d", p, t)]]
    d[, attr_name := lab(nm)]
    q <- as.integer(zap_labels(x[[sprintf("QPAIR%d", t)]]))
    other <- as.integer(zap_labels(x[[sprintf("name_seen%d_t%d", 3 - p, t)]]))
    stopifnot(all(q == as.integer(zap_labels(nm)) | q == other))
    d[, choice := as.integer(q == as.integer(zap_labels(nm)))]
    for (v in attrs) d[, paste0("attr_", v) := gsub(" +", " ", lab(x[[sprintf("%s_seen%d_t%d", v, p, t)]]))]
    L[[length(L) + 1]] <- d
  }
  d <- rbindlist(L)
  stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyDuplicated(x$ID))
  ## attribute row positions (fixed per respondent): row k shows attribute row k_1
  rowlab <- c(Age = "age", Experience = "experience", Degree = "degree", Politics = "politics", EU = "eu",
              Occupation = "occupation", Volunteering = "volunteer", Hobby = "hobby")
  pos <- data.table(id = as.integer(x$ID))
  for (v in attrs) pos[, paste0("attrpos_", v) := NA_integer_]
  for (k in 1:6) {
    r <- rowlab[x[[sprintf("row%d_1", k)]]]
    stopifnot(!anyNA(r))
    for (v in attrs) pos[r == v, paste0("attrpos_", v) := k]
  }
  stopifnot(!anyNA(pos))
  cv <- data.table(id = as.integer(x$ID),
    cov_age = as.integer(zap_labels(x$Age)), cov_gender = c("male", "female")[match(as.integer(zap_labels(x$Gender)), 1:2)],
    cov_age_group = lab(x$AgeGroup), cov_region = lab(x$Region_2GOR), cov_social_grade = lab(x$SocialGrade),
    cov_education = lab(x$Education_Level), cov_party_id = lab(x$partyid_2017), cov_vote_euref = lab(x$VoteEURef),
    cov_vote_2017 = lab(x$Vote2017), cov_brexit_identity = lab(x$rl3), cov_survey_weight = as.numeric(x[[wvar]]))
  cv[!(cov_age %between% c(16L, 110L)), cov_age := NA]
  d <- merge(merge(d, pos, by = "id"), cv, by = "id")
  ## re-key ids 1..n in source order (source IDs are already small integers; re-keyed for safety)
  d[, id := match(id, sort(unique(id)))]
  setcolorder(d, c("id", "task", "profile", "choice"))
  setorder(d, id, task, profile)
  stopifnot(uniqueN(d$id) == n)
  fwrite(d, file.path(out, outfile))
}
build("bbc-data-raw.sav", c("age", "experience", "degree", "politics", "eu", "occupation"), "Weight", "hobolt_2021_brexit_bbc_dg.csv")
build("lodger-data-raw.sav", c("age", "occupation", "volunteer", "politics", "eu", "hobby"), "W8", "hobolt_2021_brexit_lodger.csv")
