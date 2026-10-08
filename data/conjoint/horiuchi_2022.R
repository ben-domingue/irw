##Two rating conjoints on social desirability bias (fully vs partially randomized designs) from
##Horiuchi, Y., Markovich, Z., & Yamamoto, T. (2022). Does conjoint analysis mitigate social
##desirability bias? Political Analysis, 30(4), 535-549. https://doi.org/10.1017/pan.2021.30
##Replication data: Harvard Dataverse doi:10.7910/DVN/4WDVDB, CC0 1.0. File read: inside
##ReplicationPackage_v2.tar.gz, study1/data/study1-wave1.RDS, study1/data/study1-wave2.RDS,
##study2/data/study2.RDS (raw Qualtrics exports). Read as text: README.pdf, the study1/study2
##scripts, and the survey instruments (study*/documents/*survey instruments.pdf).
##Usage: Rscript horiuchi_2022.R <raw dir holding ReplicationPackage/> <output dir>
##
##Two tables (different products, attribute sets and samples):
##horiuchi_2022_sdb_shoes (Study 1, MTurk, wave 1 Dec 1-2 2018, conjoint in wave 2 Dec 8-14 2018)
##  3,075 respondents rated 20 pairs of athletic shoes, 10 attributes: Brand, Color, Gel Cushioning,
##  Model Year, Ave. Customer Review, Best Seller, Eco-Friendly Materials, Weight, Price, Shipping.
##  Outcome (instrument Q3.4/Q3.5 etc.): rating = "How likely are you to purchase shoe 1?" (and
##  shoe 2), Very Unlikely (1) ... Very Likely (7), stored 1-7 as in the authors' recode.
##  Arms (trial_design, the authors' names, blocked on wave-1 covariates = cov_block):
##  "treat random" / "control random" = fully randomized; "treat constrained" = only Eco-Friendly
##  Materials differs between the two shoes in a task; "control constrained" = only Gel Cushioning
##  differs (README/paper design; checked in the data below). In every arm the focal attribute
##  (Eco-Friendly in "treat", Gel Cushioning in "control") differs between the two shoes in every
##  task (observed); the other attributes are free in the random arms. Attribute order randomized per
##  respondent and constant across tasks (attrpos_*, recorded).
##  One MTurk ID that answered wave 2 twice is dropped (3,073 respondents remain).
##  Covariates: the raw wave-1 answers matched on the MTurk ID (then dropped): cov_age_group
##  (Q2.4), cov_race (Q2.7), cov_party_id (Q2.8 "Generally, do you usually think of yourself as a
##  Republican, a Democrat, an Independent, or something else?", wave-1 instrument), cov_env_1..5 (Q3.1 environment items) and
##  cov_sd_1..8 (Q6.1 social-desirability items), as the text answered.
##horiuchi_2022_sdb_candidates (Study 2, Prolific, Dec 3-6 2020)
##  Respondents rated 10 pairs of hypothetical congressional candidates from their own party
##  (trial_candidate_party; the pair is explicitly "not competing against each other").
##  8 attributes: Previous Profession, Undergraduate Degree, Residency, Past Political Experience,
##  Gender, Age, Race, Scandal (None / Sexual Harassment). Outcome (text_below field):
##  rating = "How likely or unlikely do you think you would be to vote for each candidate from the
##  [Democratic/Republican] Party instead of the candidate from the [other] Party in each of the
##  two elections?" Very Likely ... Very Unlikely, stored 1-7 with 7 = Very Likely (authors' recode).
##  Arms: trial_design "treat random" (fully randomized) / "treat constrained" (only Scandal
##  differs between the two candidates); in BOTH arms exactly one candidate per pair has the
##  sexual-harassment scandal (observed in the data); trial_prime = 1 if shown the face-to-face-interview
##  prime (Q6.2) before the tasks. Attribute order randomized per respondent (attrpos_*).
##  Kept: Finished == TRUE respondents with at least one rating (the authors further drop those
##  failing attention check Q4.1, flagged here as cov_attention_pass_1 (1 = selected exactly "Every
##  day" and "Never" as instructed), and one with missing income; cov_attention_pass_2 = second
##  attention check Q36.1, 1 = selected exactly "Donald Trump" and "Joe Biden" as instructed, NA if
##  unanswered; the authors' step02_check_response_quality.R reads both as acheck1/acheck2).
##  Covariates: raw text of Q3.2 age band (cov_age_group), Q3.3 education (cov_education), Q3.4
##  gender "With which gender do you most identify?" (cov_gender: Man = "male", Woman = "female",
##  Other = "other", study2 instrument), Q3.5 race, Q3.6 party ID (cov_party_id: "Generally, do you
##  usually think of yourself as a Republican, a Democrat, an Independent, or something else?"),
##  Q3.7-Q3.9 strength/lean follow-ups, Q3.10 ideology, Q3.11 income.
##  Neither study deposits a survey weight; Qualtrics durations are not kept. No task is repeated;
##  profiles shown as attribute tables (instruments: "Please examine each table carefully").
##Dropped everywhere: MTurk IDs (Q2.1, MID, WorkerId), PROLIFIC_PID, STUDY_ID, SESSION_ID,
##IPAddress, LocationLatitude/Longitude, ResponseId (respondents re-keyed), timing and free-text
##comment fields, and the authors' derived indicators. PII FOUND in the deposit: IP addresses
##and GPS coordinates (study2.RDS), MTurk/Prolific worker IDs (all three .RDS files).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rp <- file.path(raw, "ReplicationPackage")
lik <- c("Very Unlikely" = 1L, "Unlikely" = 2L, "Somewhat Unlikely" = 3L, "Neither Likely Nor Unlikely" = 4L,
         "Neither Likely nor Unlikely" = 4L, "Somewhat Likely" = 5L, "Likely" = 6L, "Very Likely" = 7L)
nm <- function(s) gsub("_+$", "", gsub("[^a-z0-9]+", "_", tolower(s)))
## stack one Qualtrics conjoint block: fields <L><sep><task><sep><attr> (attribute name) and
## <L><sep><task><sep><profile><sep><attr> (level); ratings in rcols[[task]][profile]
stack_block <- function(x, L, sep, ntask, nattr, rcols) {
  rbindlist(lapply(seq_len(ntask), function(t) rbindlist(lapply(1:2, function(p) {
    d <- data.table(row = seq_len(nrow(x)), task = t, profile = p,
                    rating = unname(lik[as.character(x[[rcols[[t]][p]]])]))
    for (k in seq_len(nattr)) {
      an <- x[[paste(L, t, k, sep = sep)]]
      lv <- x[[paste(L, t, p, k, sep = sep)]]
      d[, paste0("A", k) := an][, paste0("V", k) := lv]
    }
    d
  }))))
}
widen <- function(s, nattr) {
  long <- rbindlist(lapply(seq_len(nattr), function(k)
    s[, .(row, task, profile, attr = get(paste0("A", k)), level = get(paste0("V", k)), pos = k)]))
  long[, attr := nm(attr)]
  lv <- dcast(long, row + task + profile ~ attr, value.var = "level")
  ps <- dcast(long, row + task + profile ~ attr, value.var = "pos")
  an <- setdiff(names(lv), c("row", "task", "profile"))
  setnames(lv, an, paste0("attr_", an)); setnames(ps, an, paste0("attrpos_", an))
  merge(merge(unique(s[, .(row, task, profile, rating)]), lv), ps)
}

## ---------------- Study 1 -----------------
w2 <- as.data.table(readRDS(file.path(rp, "study1/data/study1-wave2.RDS")))
w1 <- as.data.table(readRDS(file.path(rp, "study1/data/study1-wave1.RDS")))
arms <- c(Q3 = "treat random", Q4 = "control random", Q5 = "treat constrained", Q6 = "control constrained")
lets <- c(Q3 = "A", Q4 = "B", Q5 = "C", Q6 = "D")
s1 <- rbindlist(lapply(names(arms), function(q) {
  x <- w2[!is.na(get(paste0(q, ".4"))) & get(paste0(q, ".4")) != ""]
  rc <- lapply(1:20, function(t) paste0(q, ".", c(4, 5) + 4 * (t - 1)))
  s <- widen(stack_block(x, lets[[q]], ".", 20, 10, rc), 10)
  s[, `:=`(rid = x$ResponseId[row], mid = toupper(trimws(x$MID[row])), cov_block = as.integer(x$block[row]), trial_design = arms[[q]])][, row := NULL]
}))
s1 <- s1[!is.na(rating)]
dupw <- s1[, uniqueN(rid), mid][V1 > 1, mid]   # one MTurk ID answered wave 2 twice: dropped
s1 <- s1[!mid %in% dupw]
## check the constrained arms: only the focal attribute differs within a task
dif <- function(arm) { z <- s1[trial_design == arm]; ac <- grep("^attr_", names(z), value = TRUE)
  sapply(ac, function(v) z[, uniqueN(get(v)), .(rid, task)][, mean(V1 > 1)]) }
d_tc <- dif("treat constrained"); d_cc <- dif("control constrained")
stopifnot(names(which(d_tc > 0)) == "attr_eco_friendly_materials", names(which(d_cc > 0)) == "attr_gel_cushioning")
w1[, mid := toupper(trimws(WorkerId))]
w1 <- w1[!duplicated(mid)]
cv1 <- w1[, c(list(mid = mid, cov_age_group = Q2.4, cov_race = Q2.7, cov_party_id = Q2.8),
              setNames(lapply(1:5, function(i) get(paste0("Q3.1_", i))), paste0("cov_env_", 1:5)),
              setNames(lapply(1:8, function(i) as.character(get(paste0("Q6.1_", i)))), paste0("cov_sd_", 1:8)))]
s1 <- merge(s1, cv1, by = "mid", all.x = TRUE)
s1[, id := as.integer(factor(rid))][, c("mid", "rid") := NULL]
setcolorder(s1, c("id", "task", "profile", "rating"))
setorder(s1, id, task, profile)
fwrite(s1, file.path(out, "horiuchi_2022_sdb_shoes.csv"))

## ---------------- Study 2 -----------------
x <- as.data.table(readRDS(file.path(rp, "study2/data/study2.RDS")))
x <- x[Finished == TRUE & !is.na(type)]
qn <- c(3, 6, 9, 12, 15, 18, 21, 24, 27, 30)
rc <- lapply(1:10, function(t) paste0("Q7.", qn[t], "_", 1:2))
s2 <- widen(stack_block(x, "K", "-", 10, 8, rc), 8)
s2 <- s2[!is.na(rating)]
s2[, `:=`(rid = x$ResponseId[row], trial_design = x$type[row], trial_prime = as.integer(x$Treatment[row]),
          trial_candidate_party = x$party[row], cov_attention_pass_1 = as.integer(x$Q4.1[row] == "Every day,Never"),
          cov_attention_pass_2 = as.integer(x$Q36.1[row] == "Donald Trump,Joe Biden"))]
for (q in c("3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10", "3.11"))
  s2[, paste0("cov_q", sub(".", "_", q, fixed = TRUE)) := x[[paste0("Q", q)]][row]]
setnames(s2, c("cov_q3_2", "cov_q3_3", "cov_q3_4", "cov_q3_5", "cov_q3_6", "cov_q3_7", "cov_q3_8", "cov_q3_9", "cov_q3_10", "cov_q3_11"),
         c("cov_age_group", "cov_education", "cov_gender", "cov_race", "cov_party_id", "cov_dem_strength", "cov_rep_strength",
           "cov_party_lean", "cov_ideology", "cov_income"))
stopifnot(all(s2$cov_gender %in% c("Man", "Woman", "Other", NA)))
s2[, cov_gender := c(Man = "male", Woman = "female", Other = "other")[cov_gender]]
z <- s2[trial_design == "treat constrained"]
ac <- grep("^attr_", names(z), value = TRUE)
d2 <- sapply(ac, function(v) z[, uniqueN(get(v)), .(rid, task)][, mean(V1 > 1)])
stopifnot(names(which(d2 > 0)) == "attr_scandal")
s2[, row := NULL]
s2[, id := as.integer(factor(rid))][, rid := NULL]
setcolorder(s2, c("id", "task", "profile", "rating"))
setorder(s2, id, task, profile)
fwrite(s2, file.path(out, "horiuchi_2022_sdb_candidates.csv"))
