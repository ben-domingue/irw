##Recidivism-algorithm conjoint (three US online samples) from
##Kennedy, R. P., Waggoner, P. D., & Ward, M. M. (2022). Trust in public policy algorithms.
##The Journal of Politics, 84(2), 1132-1148. https://doi.org/10.1086/716283
##Replication data: Harvard Dataverse doi:10.7910/DVN/8JFNSN, CC0 1.0, no restricted files.
##Files read: ConjointExperiment1.csv, ConjointExperiment2.csv, ConjointExperiment3.csv (Dataverse
##"original format"); wording, scales and codes from "Codebook for Trust in Public Policy
##Algorithms.docx"; pooling from study_4_conjoint_experiments.R (read as text, not run). The article
##and its supplement were not read (paywalled).
##Usage: Rscript kennedy_2022.R <raw dir> <output dir>
##
##Respondents compared 5 pairs (task 1-5) of algorithms that forecast criminal recidivism (profile 1
##= "Choice 1", 2 = "Choice 2"), 8 attributes, level text as stored in the Qualtrics export:
##number of factors, cases used, margin of error, developer, accuracy (e.g. "69% of those forecast
##TO COMMIT a crime DID COMMIT a crime"), human involvement, weights given to factors, data location.
##Attribute order was randomized once per respondent (F-<task>-<pos> names identical across a
##respondent's tasks); attrpos_ gives the row (1-8).
##One table: the three files share the attribute set and levels, and the authors pool them for the
##main results ("Full Data"; MTurk and Lucid subsets in the SI). cov_sample says which fielding:
##  "MTurk 2018-03-22" (ConjointExperiment1, 751), "Lucid 2019-03-16" (ConjointExperiment2) and
##  "Lucid 2019-04-16" (ConjointExperiment3; the codebook calls it the second wave of the second
##  experiment). Ids are re-keyed per file (no respondent links across files).
##Outcomes (codebook; the question stems are not deposited, so wording is a paraphrase):
##  choice: C<t>_1, "algorithm profile chosen by respondent: Choice 1, Choice 2"; forced choice.
##  rating: C<t>1 / C<t>2, rating of each algorithm, 1 "Definitely Would Not Use" .. 7 "Definitely
##          Would Use", stored as the number (higher = more willing to use).
##Restrictions: none documented; level weights not documented.
##Dropped: tasks with neither a choice nor a rating: tasks 4-5 of 30 file-1 respondents (who also
##  lack all demographics; the export does not say why) and all tasks of 29 / 41 respondents in
##  files 2 / 3. Kept: 751 + 504 + 495 = 1,750 respondents, 8,690 tasks. ResponseId (Qualtrics id)
##  and Finished (all TRUE) dropped.
##Covariates: cov_gender (file 1 text Male/Female/Transgender -> male/female/other; files 2-3 codes
##  1 Male, 2 Female per codebook); cov_age (whole-number ages 18-110 kept; file 1 has one "2626",
##  set NA, which the authors read as 26); cov_education (answer text: file 1 as exported, files 2-3
##  from the codebook code list; code -3105 in file 2 is undocumented -> NA; the two samples used
##  different option lists); cov_party_id (file 1 partisanid text, "Don't know or decline to state"
##  -> NA as a refusal; files 2-3 political_party code text from the codebook, a 10-category
##  strength/leaning list); cov_party_lean, cov_party_strength (file 1 leanpid / strongpid text).
##  No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs <- c("Number of factors the algorithm uses to make a recommendation." = "n_factors",
           "Number of cases used to create the algorithm." = "n_cases",
           "Estimated margin of error of probability estimates." = "margin_of_error",
           "Who developed the algorithm." = "developer",
           "Estimated accuracy of the algorithm based on the cases used to create it." = "accuracy",
           "Human involvement in final estimate (if any)." = "human_involvement",
           "Amount of weight given to different factors." = "factor_weights",
           "Location from which data to create the algorithm was collected." = "data_location")
edu2 <- c("Some high school or less", "High school graduate", "Other post high school vocational training",
          "Completed some college, but no degree", "Associate's degree", "Bachelor's degree",
          "Master's or professional degree", "Dcotorate degree")
pid2 <- c("Strong Democrat", "Not very strong Democrat", "Independent Democrat", "Independent - neither",
          "Independent Republican", "Other - leaning Democrat", "Other - neither", "Other - leaning Republican",
          "Not very strong Republican", "Strong Republican")
one <- function(file, sample) {
  x <- fread(file.path(raw, file), na.strings = c("", "NA"), colClasses = "character")
  stopifnot(all(x$Finished == "TRUE"))
  x[, id := .I]
  rows <- list()
  for (t in 1:5) for (p in 1:2) {
    d <- data.table(id = x$id, task = t, profile = p,
                    choice = fifelse(is.na(x[[paste0("C", t, "_1")]]), NA_integer_,
                                     as.integer(x[[paste0("C", t, "_1")]] == paste("Choice", p))),
                    rating = as.integer(substr(x[[paste0("C", t, p)]], 1, 1)))
    for (k in 1:8) {
      nm <- attrs[x[[sprintf("F-%d-%d", t, k)]]]
      stopifnot(!anyNA(nm))
      lv <- x[[sprintf("F-%d-%d-%d", t, p, k)]]
      stopifnot(!anyNA(lv))
      d[, paste0("nm", k) := nm][, paste0("lv", k) := lv]
    }
    rows[[length(rows) + 1]] <- d
  }
  d <- rbindlist(rows)
  long <- melt(d, id.vars = c("id", "task", "profile", "choice", "rating"), measure.vars = patterns("^nm", "^lv"),
               variable.name = "pos", value.name = c("nm", "lv"))
  long[, pos := as.integer(pos)]
  w <- dcast(long, id + task + profile + choice + rating ~ nm, value.var = "lv")
  setnames(w, attrs, paste0("attr_", attrs))
  pz <- dcast(long, id + task + profile ~ nm, value.var = "pos")
  setnames(pz, attrs, paste0("attrpos_", attrs))
  w <- merge(w, pz, by = c("id", "task", "profile"))
  w <- w[w[, .(keep = any(!is.na(choice)) | any(!is.na(rating))), .(id, task)], on = .(id, task)][keep == TRUE][, keep := NULL]
  age <- suppressWarnings(as.numeric(x$age))
  cv <- data.table(id = x$id, cov_sample = sample, cov_age = fifelse(!is.na(age) & age == round(age) & age >= 18 & age <= 110, as.integer(age), NA_integer_))
  if (file == "ConjointExperiment1.csv") {
    stopifnot(all(x$gender %in% c("Male", "Female", "Transgender", NA)))
    cv[, cov_gender := c(Male = "male", Female = "female", Transgender = "other")[x$gender]]
    cv[, cov_education := x$education]
    cv[, cov_party_id := fifelse(x$partisanid %like% "decline", NA_character_, x$partisanid)]
    cv[, cov_party_lean := x$leanpid][, cov_party_strength := x$strongpid]
  } else {
    stopifnot(all(x$gender %in% c("1", "2")))
    cv[, cov_gender := c("male", "female")[as.integer(x$gender)]]
    cv[, cov_education := edu2[match(x$education, as.character(1:8))]]
    stopifnot(all(x$political_party %in% as.character(1:10)))
    cv[, cov_party_id := pid2[as.integer(x$political_party)]]
    cv[, cov_party_lean := NA_character_][, cov_party_strength := NA_character_]
  }
  merge(w, cv, by = "id")
}
f <- c("ConjointExperiment1.csv", "ConjointExperiment2.csv", "ConjointExperiment3.csv")
s <- c("MTurk 2018-03-22", "Lucid 2019-03-16", "Lucid 2019-04-16")
parts <- lapply(1:3, function(i) one(f[i], s[i]))
off <- cumsum(c(0L, sapply(parts, function(z) max(z$id)))[1:3])
for (i in 1:3) parts[[i]][, id := id + off[i]]
d <- rbindlist(parts)
stopifnot(d[!is.na(choice), .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)],
          d[, .N, .(id, task)][, all(N == 2)])
setcolorder(d, c("id", "task", "profile", "choice", "rating", grep("^attr_", names(d), value = TRUE),
                 grep("^attrpos_", names(d), value = TRUE)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kennedy_2022_policy_algorithms.csv"))
print(d[, .(resp = uniqueN(id), rows = .N, tasks = uniqueN(paste(id, task))), cov_sample])
print(d[, .(nachoice = sum(is.na(choice)), narating = sum(is.na(rating)))])
