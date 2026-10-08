##News-story choice conjoints (headline x outlet), two US samples, from
##Mummolo, J. (2016). News from the other side: How topic relevance limits the prevalence of
##partisan selective exposure. The Journal of Politics, 78(3), 763-773. https://doi.org/10.1086/685584
##Replication data: Harvard Dataverse doi:10.7910/DVN/HQKQCQ, CC0 1.0. Files read ("original
##format" downloads): se.conjoint2.RData (main sample) and se.conjoint.turk2.RData (MTurk sample),
##each holding the authors' long data frame `conj.dta` (one row per respondent x task x profile).
##replication_instructions.pdf and jop_replication_dataverse2.R read as text (not run). The article
##(paywalled) and the author's page (bot wall) were not accessible: question wording below is a
##paraphrase, and the sample providers of the two studies are not stated in the deposit (the code
##compares the main sample with 2012 CCES partisans; the second file is labelled "turk").
##Usage: Rscript mummolo_2016.R <dir holding the .RData files> <output dir>
##
##Partisan respondents (Democrats and Republicans only; every row has dem or rep = 1) choose which
##of two news items they would rather read. Two attributes per profile: attr_headline (33
##headlines = 11 topics x 3 wordings, text as displayed) and attr_source (Fox News / MSNBC /
##USA Today). Main sample: 1,059 respondents x 12 tasks; MTurk: 1,444 x 10 tasks; 2 profiles (A/B)
##per task, task = choice.num, profile 1 = A. Both items in a task always have different topics
##in about 91% of tasks and different outlets in ~66% (no restriction is documented; the authors'
##headline.source.scheme, constant within respondent, takes 6 values and is kept as
##trial_scheme: its meaning is not documented). `rows` (0/1, constant within respondent, about half
##each) is kept as trial_rows; its meaning is not documented (possibly the A/B display layout).
##Separate tables: different samples and fieldings, analysed separately by the author (the
##MTurk file supports the replication analyses).
##  choice: which of the two news items the respondent would choose to read (paraphrase);
##  forced choice: exactly one per task in both files (checked).
##Covariates (authors' coding; no raw demographics in the deposit): cov_gender_code (1 = female, authors' Table 1 "Female"), cov_dem, cov_rep,
##cov_lib, cov_con, cov_student, cov_smoker, cov_lose_weight, cov_senior (over 55), cov_uninsured,
##cov_health_care_job, cov_ba (has a BA), cov_white/cov_black/cov_latino/cov_other_race (authors' Table 1:
##non-Hispanic white, non-Hispanic black, Hispanic/Latino, other race) as 0/1; cov_income
##(household income in $1,000s, category midpoints as coded by the author); cov_age (years).
##cov_gender_code keeps the authors' 0/1 dummy rather than cov_gender, since the deposit does not
##show what 0 includes. Dropped: Qualtrics response ids (re-keyed to integers in respid order),
##derived indicators (topic dummies, fox/msnbc/usa, friend/unfriend source, libdem, conrep, hcip,
##smoker2/3, no.news.std, count).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(f, ntask, nresp, table) {
  e <- new.env(); load(file.path(raw, f), envir = e)
  x <- as.data.table(e$conj.dta)
  x[, respid := as.character(respid)]
  stopifnot(uniqueN(x$respid) == nresp, x[, .N, respid][, all(N == 2 * ntask)], all(x$dem + x$rep == 1))
  x[, id := match(respid, sort(unique(respid)))]
  d <- x[, .(id, task = as.integer(choice.num), profile = c(A = 1L, B = 2L)[as.character(profile)], choice = as.integer(response),
             attr_headline = head, attr_source = as.character(source),
             trial_scheme = as.integer(as.character(headline.source.scheme)), trial_rows = as.integer(rows),
             cov_gender_code = female, cov_dem = dem, cov_rep = rep, cov_lib = lib, cov_con = con, cov_student = student,
             cov_smoker = smoker, cov_lose_weight = lose.weight, cov_senior = senior, cov_uninsured = uninsured,
             cov_health_care_job = hc.worker, cov_ba = BA, cov_white = white, cov_black = black, cov_latino = latino,
             cov_other_race = other.race, cov_income = income, cov_age = age)]
  stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
            d[, uniqueN(profile), .(id, task)][, all(V1 == 2)], !anyNA(d$attr_headline), !anyNA(d$attr_source))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(table, ".csv")))
}
build("se.conjoint2.RData", 12L, 1059L, "mummolo_2016_news_choice")
build("se.conjoint.turk2.RData", 10L, 1444L, "mummolo_2016_news_choice_mturk")
