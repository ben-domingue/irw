##Italian debt-reduction / party-agenda conjoint ("trilemma", Experiment 2) from
##Aspide, A., & DiGiuseppe, M. (2025). The mass politics of public debt, immigration, and
##austerity. Journal of European Public Policy, 33(7), 2010-2038.
##https://doi.org/10.1080/13501763.2025.2510523
##Replication data: Harvard Dataverse doi:10.7910/DVN/GRLIQN, CC0 1.0, no restricted files.
##File read: trilemma.csv (Qualtrics export, 3 header rows: names, question text, ImportId).
##Full_Script.R read as text for the authors' processing (cjoint::read.qualtrics, drop_na(selected)).
##Experiment 1 (sl.xlsx, single-factor information experiment) is not a conjoint and is not used.
##Usage: Rscript aspide_2025.R <raw dir> <output dir>
##
##Italian online respondents (Qualtrics, July 2024; UserLanguage IT). Each saw 8 pairs of party
##agendas ("Partito A"/"Partito B", ...; profile 1 = left column) with 4 attributes, then a 9th
##task that REPEATS task 1 with the two columns swapped (question text of task9_0: the left
##party shows [Field-F-1-2-*], the right [Field-F-1-1-*]); task 9 has trial_repeat_of = 1 and its
##profile 1 is task 1's profile 2. Outcomes, Italian wording from the export's question row:
##  choice = task<t>_0 "Quale tra questi due partiti voterebbe?" (1 = left, 2 = right); forced
##          choice, no opt-out.
##  rating = t<t>_p1 / t<t>_p2 (task 9: Q217/Q218) "Da 0 (per niente) a 10 (totalmente), quanto
##          è d'accordo con l'agenda politica A?" 0-10, 10 = fully agree; stored as exported.
##Attributes (Italian level text as displayed, from the F-t-p-k fields): debt_reduction
##("Riduzione del debito", 9 levels), defence ("Difesa", 5), civil_rights ("Diritti e tutela dei
##cittadini", 6), energy ("Indipendenza energetica", 4). The export doubles a non-breaking space
##after accented letters ("capacità  militare"); the   is removed. Attribute row order
##was randomized once per respondent (F-1-k is the same in all 8 tasks, verified): attrpos_*.
##Randomization restrictions: none documented; level shares look uniform within attribute.
##Kept: respondents with a choice in task 1 (the authors drop_na(selected)); tasks without a
##choice are omitted. Dropped: Qualtrics ResponseId (re-keyed to integers in export order), dates,
##panel IDs in column `m` (96 respondents; platform IDs), `p`, consent/screening items, timing
##clicks, the NPS_GROUP columns (Qualtrics-derived).
##Covariates (the export holds codes; no codebook maps them, so codes keep a _code suffix):
##cov_age (Età, years as typed; implausible values -> NA), cov_gender_code (Genere, codes 1-4),
##cov_education_code (1-6; Experiment 1's labelled file orders the same six categories Nessun
##titolo .. Laurea o post-laurea, but the mapping is not stated for this file), cov_income_code
##(1-10), cov_left_right (0 = left .. 10 = right), cov_region_code, cov_eu_vote2024_code ("Per
##quale partito ha votato alle elezioni Europee lo scorso Giugno 2024?"; a vote, not party id),
##cov_att_check_code (correct answer "Altri quotidiani", code not documented),
##cov_duration_sec (whole survey). No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "trilemma.csv"), header = FALSE, encoding = "UTF-8", colClasses = "character")
h <- as.character(x[1]); q <- as.character(x[2])
stopifnot(grepl("\\[Field-F-1-2-1\\]\\s*\\[Field-F-1-1-1\\]", q[h %in% "task9_0"]))
s <- x[-(1:3)]; setnames(s, make.unique(ifelse(is.na(h) | h == "", paste0("X", seq_along(h)), h)))
s <- s[task1_0 %in% c("1", "2")]
s[, rid := .I]
fx <- function(v) gsub(" ", "", v, fixed = TRUE)
an <- c("Riduzione del debito" = "debt_reduction", "Difesa" = "defence", "Diritti e tutela dei cittadini" = "civil_rights",
        "Indipendenza energetica" = "energy")
for (t in 2:8) for (k in 1:4) stopifnot(all(s[[paste0("F-", t, "-", k)]] == s[[paste0("F-1-", k)]]))
stopifnot(all(sapply(1:4, function(k) all(s[[paste0("F-1-", k)]] %in% names(an)))))
L <- list()
for (t in 1:9) for (p in 1:2) {
  tt <- if (t == 9) 1L else t; pp <- if (t == 9) 3L - p else p
  ch <- s[[paste0("task", t, "_0")]]
  rt <- if (t == 9) s[[c("Q217", "Q218")[p]]] else s[[paste0("t", t, "_p", p)]]
  r <- data.table(rid = s$rid, task = t, profile = p, choice = fifelse(ch %in% c("1", "2"), as.integer(ch == as.character(p)), NA_integer_),
                  rating = as.integer(fifelse(rt == "", NA_character_, rt)), trial_repeat_of = if (t == 9) 1L else NA_integer_)
  for (k in 1:4) {
    nm <- an[s[[paste0("F-1-", k)]]]
    for (v in unique(nm)) {
      w <- which(nm == v)
      r[w, paste0("attr_", v) := fx(s[[paste0("F-", tt, "-", pp, "-", k)]][w])]
      r[w, paste0("attrpos_", v) := k]
    }
  }
  L[[length(L) + 1]] <- r
}
d <- rbindlist(L, use.names = TRUE)
d <- d[!is.na(choice)]
stopifnot(d[, sum(choice), .(rid, task)][, all(V1 == 1)], all(d$rating %in% c(0:10, NA)))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr")]), !any(d[, unlist(.SD), .SDcols = patterns("^attr_")] == ""))
cv <- function(v) { v[v == ""] <- NA; v }
age <- suppressWarnings(as.integer(s$age)); age[!is.na(age) & (age < 18 | age > 100)] <- NA
cov <- data.table(rid = s$rid, cov_age = age, cov_gender_code = as.integer(cv(s$gender)), cov_education_code = as.integer(cv(s$education)),
                  cov_income_code = as.integer(cv(s$income)), cov_left_right = as.integer(cv(s$left_right)),
                  cov_region_code = as.integer(cv(s$region)), cov_eu_vote2024_code = as.integer(cv(s$party)),
                  cov_att_check_code = as.integer(cv(s$att_check)), cov_duration_sec = as.integer(s$`Duration (in seconds)`))
d <- merge(d, cov, by = "rid")
setnames(d, "rid", "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating", "trial_repeat_of", paste0("attr_", an), paste0("attrpos_", an)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "aspide_2025_debt_austerity.csv"))
