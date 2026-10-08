##Job-offer conjoint (state democratic backsliding) from
##Nelson, M. J., & Witko, C. (2022). The economic costs of democratic backsliding?
##Backsliding and state location preferences of US job seekers. The Journal of Politics,
##84(2), 1233-1238. https://doi.org/10.1086/715601
##Replication data: Harvard Dataverse doi:10.7910/DVN/YOBUVS, CC0 1.0, no restricted files.
##Files read: DemBacksliding_MTURK.csv and DemBacksliding_Student.csv (originals of the .tab files; raw
##Qualtrics CSVs). JOP_Replication.R read as text: it is the only source of the level labels
##(its recode lines) and of the rating recode. No codebook or questionnaire ships; the article
##(paywalled) was not read.
##Usage: Rscript nelson_2022.R <raw dir> <output dir>
##
##Two samples, analysed SEPARATELY by the authors (separate amce() fits, plotted side by side),
##so TWO TABLES with the same layout:
##  nelson_2022_backsliding_mturk: 736 MTurk workers (Sept 2019).
##  nelson_2022_backsliding_students: students at a large public university (Sept 2019); 381
##    rows in the export, 45 unfinished; the 44 with no answered task are omitted (337 kept).
##Each respondent saw 15 pairs of hypothetical job offers (Job 1 / Job 2) with 6 attributes.
##Task t shows profile 1 from the Qualtrics fields <attr>(2t-1)_DO and profile 2 from
##<attr>(2t)_DO (the authors' code reads them the same way), so task and profile are recorded.
##The _DO value is the index of the randomized level shown.
##Outcomes:
##  choice: accept_t (1 = Job 1, 2 = Job 2), forced choice, no opt-out; wording unknown.
##  rating: offer1_t / offer2_t, a 5-point rating of each offer; wording and anchors unknown.
##    The raw Qualtrics codes are not in scale order; the authors recode 1->5, 2->4, 5->3,
##    3->2, 4->1, and the same recode is applied here, so the stored rating is the authors'
##    1-5. Higher = more favourable is INFERRED (chosen offers average 4.2, unchosen 3.2-3.4).
##Attribute text: the authors' labels from their recode lines, NOT the displayed text (not in
##the deposit): salary ($75,000/$90,000/$105,000), size (10/2,500/500,000 Employees),
##location (Rural Area/College Town/Midsize City/Metro Area), culture (Task Variety/Frequent
##Feedback/Advancement Opportunity/Great Talent), state_partisanship (Strong/Weak Clinton/Trump
##State), backsliding (the authors' code names: VoterID, Unionize, Protest, Governor,
##Redistricting, BikeTrails, Corruption; each stood for a statement about a recent state law
##or event that respondents read; BikeTrails is the placebo per the authors' baseline). Display
##order of attributes and any randomization restrictions are not documented.
##The authors' code has slips the table does NOT reproduce: task 5 choice read from accept_9,
##task 11 profile 2 partisanship from pol2_DO.
##Covariates: cov_birth_year (YRBORN), cov_party_id7_code (CODES 1-7: the authors' 7-point
##party ID built from PID2/PID3/PID4, JOP_Replication.R L16-23; their 3-way recode L507-508
##names 1-3 Democrat, 4 Independent, 5-7 Republican, but no source gives the text of the seven
##points or of the PID questions, so the codes are kept). Other demographics are unlabelled
##Qualtrics codes and are dropped; the export has Qualtrics "Duration (in seconds)" (not kept).
##No survey weight in the deposit.
##PII in the deposit (dropped): IP addresses, latitude/longitude, Qualtrics ResponseId, a
##per-respondent random code (`random`, likely the MTurk completion code). Ids are re-keyed to
##row order.
##N: MTurk 736, students 337 (respondents with any answered task); the article was not checked.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lv <- list(sal = c("$75,000", "$90,000", "$105,000"), size = c("10 Employees", "2,500 Employees", "500,000 Employees"),
           rural = c("Rural Area", "College Town", "Midsize City", "Metro Area"),
           comp = c("Task Variety", "Frequent Feedback", "Advancement Opportunity", "Great Talent"),
           pol = c("Strong Clinton State", "Weak Clinton State", "Weak Trump State", "Strong Trump State"),
           bs = c("VoterID", "Unionize", "Protest", "Governor", "Redistricting", "BikeTrails", "Corruption"))
an <- c(sal = "salary", size = "size", rural = "location", comp = "culture", pol = "state_partisanship", bs = "backsliding")
rec <- c(5L, 4L, 2L, 1L, 3L)  # authors' recode 1=5;2=4;5=3;3=2;4=1
build <- function(file, name) {
  s <- fread(file.path(raw, file))
  s[, id := seq_len(.N)]
  pid <- rep(NA_integer_, nrow(s))
  pid[s$PID2 %in% 1] <- 1L; pid[s$PID2 %in% 2] <- 2L; pid[s$PID4 %in% 2] <- 3L; pid[s$PID4 %in% 3] <- 4L
  pid[s$PID4 %in% 1] <- 5L; pid[s$PID3 %in% 2] <- 6L; pid[s$PID3 %in% 1] <- 7L
  rows <- list()
  for (t in 1:15) for (p in 1:2) {
    j <- 2L * t - 2L + p
    r <- data.table(id = s$id, task = t, profile = p)
    acc <- s[[paste0("accept_", t)]]
    r[, choice := fifelse(is.na(acc), NA_integer_, as.integer(acc == p))]
    r[, rating := rec[s[[paste0("offer", p, "_", t)]]]]
    for (k in names(lv)) { code <- s[[paste0(k, j, "_DO")]]; stopifnot(all(code %in% c(NA, seq_along(lv[[k]])))); r[, paste0("attr_", an[[k]]) := lv[[k]][code]] }
    r[, cov_birth_year := as.integer(s$YRBORN)][, cov_party_id7_code := pid]
    rows[[length(rows) + 1]] <- r
  }
  d <- rbindlist(rows)
  d <- d[!(is.na(choice) & is.na(rating))]
  stopifnot(!anyNA(d[, paste0("attr_", an), with = FALSE]), all(d$choice %in% c(NA, 0:1)))
  stopifnot(d[!is.na(choice), .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
  invisible(d)
}
m <- build("DemBacksliding_MTURK.csv", "nelson_2022_backsliding_mturk")
s <- build("DemBacksliding_Student.csv", "nelson_2022_backsliding_students")
stopifnot(uniqueN(m$id) == 736, uniqueN(s$id) == 337)
