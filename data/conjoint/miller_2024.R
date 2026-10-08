##Vacation-destination conjoint (US states, democratic backsliding news) from
##Miller, D. R., & Smith, S. D. (2024). (Small D-democratic) vacation, all I ever wanted? The
##effect of democratic backsliding on leisure travel in the American states. Journal of
##Experimental Political Science, 12, 99-109. https://doi.org/10.1017/xps.2023.40
##(open access, CC BY 4.0)
##Replication data: Harvard Dataverse doi:10.7910/DVN/KA7DLE, CC0 1.0. Files read:
##Study1_Raw.csv (the Qualtrics export; Lucid rid and zip already removed by the authors)
##and Study1_Final.csv (the authors' cleaned file, used for respondent covariates and as a
##cross-check). Also read as text: README.txt, Study1_Raw_Codebook.txt,
##Study1_Final_Codebook.txt, Study1_DataPrep.R (not run).
##Usage: Rscript miller_2024.R <dir holding the two csv files> <output dir>
##
##Study 1 only. Study 2 (Study2_*.csv) is a single-treatment survey experiment (Florida
##treatment vs control), not a conjoint: not built.
##US adults from Lucid, December 2022 (article). 10 tasks x 3 destination profiles, 6
##attributes: average July temperature, most popular tourist attractions, travel time from
##your home (by air), state-level 2020 presidential election result, recent state news,
##destination community type. Task and profile are recorded (F-<task>-<profile>-<pos>
##Qualtrics columns). Attribute ORDER was randomized per task: attrpos_<attr> = the row
##(1-6) at which the attribute appeared (F-<task>-<pos> holds the attribute name).
##Sample: the authors' filter (consent "I AGREE", not typing REMOVE at debrief) leaves 2,254
##rows; a task is kept when its choice question was answered: 2,076 respondents (the authors'
##Study1_Final.csv has 2,077, one with no answered choice; the article says "nearly 2,100"). Partial completers keep
##the tasks they answered. Attention-check failures are kept (cov_attention1/2).
##Outcomes (one table, same tasks), wording from the Qualtrics header row:
##  choice: "At which of these destinations are you most interested in vacationing?"
##          Destination 1 / 2 / 3 / "None of these destinations". OPT-OUT: "None" tasks have
##          choice = 0 on all three profiles.
##  rating: "How interested are you in vacationing at each destination?" 1 = Not at all
##          interested, 2 Slightly, 3 Somewhat, 4 Very, 5 = Extremely interested; blank if
##          that profile's rating was skipped.
##Attribute text as displayed, except: the authors removed an apostrophe from the two
##"voters ability" news levels in the raw file (codebook note 2), so those two levels read
##"voters ability"; and temperatures are stored as shown in the data (64, 67, 72, 78).
##Restrictions are not documented; level shares look uniform.
##Covariates from Study1_Final.csv (codebook codes): cov_pid (D/I/R/O), cov_gender (1 male,
##2 female), cov_income (1-6), cov_age (years), cov_educ (1-5), cov_ideology (1 very
##conservative - 7 very liberal), cov_region (Lucid code, unlabelled), cov_attention1,
##cov_attention2 (1 = passed).
##Dropped: ResponseId (Qualtrics; re-keyed to integers in file order), dates, durations,
##free-text answers (Q46, Q100), the authors' derived race and age-bin dummies.
##Spot check: choice rate for the two "limit" news levels minus the economic-commission
##baseline = -0.033 (SE 0.005, clustered by id); the article reports about 3 points less likely.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "Study1_Raw.csv"), colClasses = "character")
r <- r[-(1:2)][Q31 == "I AGREE" & !Q100 %in% c("REMOVE", "REMOVE ")]
stopifnot(nrow(r) == 2254)
qn <- list(c("Q62", "Q63"), c("Q259", "Q260"), c("Q262", "Q263"), c("Q265", "Q266"), c("Q268", "Q269"),
           c("Q271", "Q272"), c("Q274", "Q275"), c("Q277", "Q278"), c("Q280", "Q281"), c("Q283", "Q284"))
an <- c("Average July Temperature (in degrees Fahrenheit)" = "temperature", "Most popular tourist attractions" = "attractions",
        "Travel time from your home (by air)" = "travel_time", "State-level 2020 presidential election result" = "election_2020",
        "Recent state news" = "recent_news", "Destination community type" = "community")
rl <- c("Not at all interested" = 1L, "Slightly interested" = 2L, "Somewhat interested" = 3L, "Very interested" = 4L,
        "Extremely interested" = 5L)
rows <- list()
for (t in 1:10) for (p in 1:3) {
  ch <- r[[qn[[t]][2]]]; rt <- r[[paste0(qn[[t]][1], "_", p)]]
  stopifnot(all(ch %in% c("", paste("Destination", 1:3), "None of these destinations")), all(rt %in% c("", names(rl))))
  d <- data.table(ResponseId = r$ResponseId, task = t, profile = p, answered = ch != "",
                  choice = as.integer(ch == paste("Destination", p)), rating = unname(rl[rt]))
  for (k in 1:6) {
    nm <- r[[sprintf("F-%d-%d", t, k)]]; lv <- r[[sprintf("F-%d-%d-%d", t, p, k)]]
    for (x in names(an)) { w <- nm == x; d[w, paste0("attr_", an[[x]]) := lv[w]]; d[w, paste0("attrpos_", an[[x]]) := k] }
  }
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows, use.names = TRUE, fill = TRUE)[answered == TRUE][, answered := NULL]
at <- paste0("attr_", an)
stopifnot(!anyNA(d[, ..at]), d[, all(sapply(.SD, function(x) all(x != ""))), .SDcols = at])
f <- fread(file.path(raw, "Study1_Final.csv"))
## cross-check against the authors' cleaned file
chk <- f[!is.na(choice), .(ResponseId, task, profile, fc = choice, fr = rating, ft = as.character(temp), fn = recentnews)][
  d, on = .(ResponseId, task, profile)]
stopifnot(chk[, all(!is.na(fc))], chk[, all(fc == choice)], chk[, all(ft == attr_temperature)], chk[, all(fn == attr_recent_news)],
          chk[, all((is.na(fr) & is.na(rating)) | fr == rating, na.rm = TRUE)])
cv <- unique(f[, .(ResponseId, cov_pid = pid3, cov_gender = gender, cov_income = income, cov_age = age, cov_educ = educ,
                   cov_ideology = ideology, cov_region = region, cov_attention1 = attention1, cov_attention2 = attention2)])
stopifnot(!anyDuplicated(cv$ResponseId))
d <- cv[d, on = "ResponseId"]
ids <- unique(r$ResponseId); d[, id := match(ResponseId, ids)][, ResponseId := NULL]
stopifnot(uniqueN(d$id) == 2076, !anyDuplicated(d[, .(id, task, profile)]), d[, .N, .(id, task)][, all(N == 3)],
          d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setcolorder(d, c("id", "task", "profile", "choice", "rating", at, paste0("attrpos_", an)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "miller_2024_backsliding_travel.csv"))
