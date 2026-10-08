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
##Qualtrics columns). Attribute ORDER was randomized once per respondent (the same order in all
##of a respondent's tasks, checked in the data): attrpos_<attr> = the row
##(1-6) at which the attribute appeared (F-<task>-<pos> holds the attribute name).
##Sample: the authors' filter (consent "I AGREE", not typing REMOVE at debrief) leaves 2,254
##rows; a task is kept when its choice question was answered: 2,076 respondents (the authors'
##Study1_Final.csv has 2,077, one with no answered choice; the article says "nearly 2,100"). Partial completers keep
##the tasks they answered. Attention-check failures are kept (cov_attention_pass_1/_2).
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
##Covariates from Study1_Final.csv: cov_party_id (pid3, the authors' recode of Lucid's
##political_party, written out per Study1_Final_Codebook.txt "D=Democrat, I=Independent,
##R=Republican, O=Other"; Study1_DataPrep.R L22-28 counts Independent/Other leaners as
##Democrat/Republican), cov_gender (gender, Final codebook "1=Male, 2=Female", written
##male/female), cov_income (codes 1-6), cov_age (years), cov_ideology (1 very conservative - 7
##very liberal), cov_region (Lucid code, unlabelled), cov_attention_pass_1 / cov_attention_pass_2
##(attention1/attention2, Final codebook "correctly answered the first/second attention check
##question": 1 = passed, 0 = failed). cov_education is Lucid's own education question from
##Study1_Raw.csv (the authors' educ collapses it to 5 groups), as the answer text of
##Study1_Raw_Codebook.txt "education" (1 Some high school or less ... 8 Doctoral degree, -3105
##None of the above); the one respondent with the undocumented code 10 is blank.
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
pl <- c(D = "Democrat", I = "Independent", R = "Republican", O = "Other")  # Study1_Final_Codebook.txt, pid
el <- c("1" = "Some high school or less", "2" = "High school graduate", "3" = "Other post high school vocational training",
        "4" = "Completed some college, but no degree", "5" = "Associate's degree", "6" = "Bachelor's degree",
        "7" = "Master's degree", "8" = "Doctoral degree", "-3105" = "None of the above")  # Study1_Raw_Codebook.txt, education
stopifnot(all(f$pid3 %in% names(pl)), all(f$gender %in% 1:2), all(f$attention1 %in% 0:1), all(f$attention2 %in% 0:1))
cv <- unique(f[, .(ResponseId, cov_party_id = unname(pl[pid3]), cov_gender = c("male", "female")[gender], cov_income = income, cov_age = age,
                   cov_ideology = ideology, cov_region = region, cov_attention_pass_1 = attention1, cov_attention_pass_2 = attention2)])
stopifnot(!anyDuplicated(cv$ResponseId), all(r$education %in% c(names(el), "10")))
cv[, cov_education := unname(el[r$education[match(ResponseId, r$ResponseId)]])]
d <- cv[d, on = "ResponseId"]
ids <- unique(r$ResponseId); d[, id := match(ResponseId, ids)][, ResponseId := NULL]
stopifnot(uniqueN(d$id) == 2076, !anyDuplicated(d[, .(id, task, profile)]), d[, .N, .(id, task)][, all(N == 3)],
          d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setcolorder(d, c("id", "task", "profile", "choice", "rating", at, paste0("attrpos_", an)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "miller_2024_backsliding_travel.csv"))
