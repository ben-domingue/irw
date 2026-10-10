##Hypothetical Bundestag election outcomes (Germany, Dynata, March 2024) from
##Blais, A., Bol, D., & Plescia, C. (2026). Does support for democracy increase losers' consent?
##Political Studies. https://doi.org/10.1177/00323217261463105
##Replication data: Harvard Dataverse doi:10.7910/DVN/JFJSSP, CC0 1.0, no restricted files, no terms.
##File read: data_2024_03_06_clean.csv (Dataverse "original format" of data_2024_03_06_clean.tab; a
##Qualtrics export). Read as text only: do_file_paper2.do (authors' recodes: Q1 age, Q2 gender, Q3
##education, Q4 region, Q5A-G party likes, Q8A-G democracy-support items, Q9 accept, Q10 protest, flags)
##and the companion article on the same survey, Blais, Bol & Plescia (2026), "What electoral outcomes
##foster electoral consent and dissent?", Politics and Governance 14, 11468 (sample, Figure 1 vignette,
##randomization rules, outcome scales). The Political Studies article itself was not accessible.
##Usage: Rscript blais_2026.R <raw dir> <output dir>
##
##Dynata online panel, German adults, quotas on age, gender, region (hard) and education (soft);
##5,374 rows, 5,370 respondents in the papers (4 with no answer to the fifth accept question; the
##authors drop them, here only that task is missing). Five outcomes per respondent (task 1-5, file
##suffix 1-5 / A-E), one profile each. Vignette (companion article Figure 1, English version; the
##survey was fielded in German, wording in its Appendix 2, not read):
##  "Imagine an election produces the following German Bundestag: CDU/CSU: 39% of seats; AfD: 20% of
##  seats; SPD: ...; Greens: ...; FDP: ...; BSW: ...; The Left: ... After the election, there is a
##  governing coalition between the CDU and the Greens: CDU/CSU: 68% of cabinet seats; Greens: 32% of
##  cabinet seats. The CDU/CSU has the Chancellorship."
##Attributes: attr_seats_<party> = "<n>% of seats" for the seven parties (source <Party>Percentage<t>);
##attr_coalition = the coalition parties joined with " and " in the order CDU/CSU, AfD, SPD, Greens, FDP,
##BSW, The Left (source <Party>InCoalition<t>); attr_chancellor = the Chancellor's party (source
##ChancellorParty<t>). Party names as in the English vignette (Grüne -> Greens, Die Linke -> The Left,
##CDU -> CDU/CSU). A party with 0 seats is stored as "0% of seats": whether such a party was listed
##with 0% or left off the screen is not documented (Ben to decide if that matters).
##Not stored: the cabinet-seat shares, which are a deterministic function of the seat shares and the
##coalition (Gamson's law, rounded) and whose SPD column was not saved for task 1 (SDPCoalitionSeats1 is
##empty; the authors recompute it).
##Randomization (companion article): seat shares drawn around the last five national polls +/- 10 points,
##summing to 100 (verified), no party between 1% and 4% (verified); the government is a random set of
##parties holding >= 51% of seats with unnecessary parties dropped; the Chancellor is the largest
##coalition party (random on ties). So restrictions = yes and the levels are far from uniform.
##trial_flag_bug: the authors' "weird" flag (do file): outcomes that should not have occurred (a
##coalition party with 0 seats, or a coalition holding > 70% of seats), 0.41% of outcomes; the authors
##analyse weird == 0 only.
##Outcomes (companion article; exact wording in its Appendix 2, not read, so paraphrase):
##  rating: how (un)acceptable the respondent would personally find the outcome, 0 = not acceptable at
##    all ... 10 = completely acceptable (source Q9A-E).
##  rating_protest: how likely to participate in a protest contesting the outcome, 0 = very unlikely ...
##    10 = very likely (Q10A-E); asked only when accept < 5, so NA when accept >= 5 (the authors set
##    those to 0; stored raw here as NA).
##Covariates: cov_age (Q1, whole years 18-100 else NA), cov_gender_code (Q2: 1/2/3, no labels
##deposited), cov_education_code (Q3), cov_region_code (Q4), cov_like_<party> (Q5A-G, 0-10 party
##likes, 99 = don't know kept as in the source; party order from the authors' code fav1-fav7),
##cov_democracy_support_<a-g>_code (Q8A-G, 1-5, wording not deposited; the authors sum them into
##dem_sup), cov_duration_sec (Qualtrics Durationinseconds, whole survey).
##PII in the source (dropped): IPAddress, LocationLatitude/LocationLongitude, ResponseId, Dynata psid and
##the panel redirect links/signatures that embed it; recipient name/email columns are present but empty.
##Also dropped: Q6/Q7 (tie-break party picks), Q11-Q13 (no wording or labels), quota groups, the authors'
##derived variables.
##Spot check (printed): share of outcomes rated below the midpoint (companion article: 55%) and share
##with protest > 5 (23%), on unflagged outcomes.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data_2024_03_06_clean.csv"), encoding = "UTF-8", na.strings = "")
stopifnot(nrow(s) == 5374)
s[, id := .I]
src <- c("CDU", "AfD", "SPD", "Grüne", "FDP", "BSW", "DieLinke")
lab <- c("CDU/CSU", "AfD", "SPD", "Greens", "FDP", "BSW", "The Left")
key <- c("cdu_csu", "afd", "spd", "greens", "fdp", "bsw", "the_left")
chan <- c(CDU = "CDU/CSU", AfD = "AfD", SPD = "SPD", "Grüne" = "Greens", FDP = "FDP", BSW = "BSW", "Die Linke" = "The Left")
tasks <- lapply(1:5, function(t) {
  L <- LETTERS[t]
  d <- data.table(id = s$id, task = t, profile = 1L, rating = s[[paste0("Q9", L)]], rating_protest = s[[paste0("Q10", L)]])
  pct <- sapply(src, function(p) s[[paste0(p, "Percentage", t)]])
  inc <- sapply(src, function(p) s[[paste0(p, "InCoalition", t)]] %in% "yes")
  stopifnot(rowSums(pct) == 100, !any(pct > 0 & pct < 5))
  for (k in seq_along(src)) d[, (paste0("attr_seats_", key[k])) := paste0(pct[, k], "% of seats")]
  d[, attr_coalition := apply(inc, 1, function(r) paste(lab[r], collapse = " and "))]
  d[, attr_chancellor := unname(chan[s[[paste0("ChancellorParty", t)]]])]
  cab <- rowSums(pct * inc)
  zero_in <- rowSums(inc & pct == 0) > 0
  d[, trial_flag_bug := as.integer(zero_in | cab > 70)]
  d
})
d <- rbindlist(tasks)
d <- d[!is.na(rating)]
stopifnot(!anyNA(d$attr_chancellor), all(d$attr_coalition != ""), all(d$rating %in% 0:10),
          all(d$rating_protest %in% c(0:10, NA)), d[rating >= 5, all(is.na(rating_protest))])
age <- s$Q1
cv <- data.table(id = s$id, cov_age = as.integer(ifelse(age >= 18 & age <= 100, age, NA)),
                 cov_gender_code = as.integer(s$Q2), cov_education_code = as.integer(s$Q3), cov_region_code = as.integer(s$Q4))
likes <- c(Q5A = "cdu_csu", Q5B = "afd", Q5C = "spd", Q5D = "greens", Q5E = "fdp", Q5F = "bsw", Q5G = "the_left")
for (v in names(likes)) cv[, (paste0("cov_like_", likes[[v]])) := as.integer(s[[v]])]
for (k in letters[1:7]) cv[, (paste0("cov_democracy_support_", k, "_code")) := as.integer(s[[paste0("Q8", toupper(k))]])]
cv[, cov_duration_sec := as.integer(s$Durationinseconds)]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "blais_2026_losers_consent.csv"))
k <- d[trial_flag_bug == 0]
message("respondents ", uniqueN(d$id), "; rows ", nrow(d), "; flagged ", sum(d$trial_flag_bug),
        "; unflagged ", nrow(k), "; accept < 5: ", round(mean(k$rating < 5), 3),
        "; protest > 5: ", round(mean(fcoalesce(k$rating_protest, 0L) > 5), 3))
