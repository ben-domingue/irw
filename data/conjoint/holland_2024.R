##Migrant-reception conjoint (Colombia: Colombian and Venezuelan respondents) from
##Holland, A. C., Peters, M. E., & Zhou, Y.-Y. (2024). Left out: How political ideology
##affects support for migrants in Colombia. The Journal of Politics, 86(4), 1291-1303.
##https://doi.org/10.1086/729943
##Replication data: Harvard Dataverse doi:10.7910/DVN/PZZB1Z, CC0 1.0, no restricted files.
##Files read: colombia_clean.RDS and venezuelans_clean.RDS (Dataverse downloads). Design and
##wording from Colombia_Paper.Rnw / Colombia_SI.Rnw (read as text, not run) and the deposited
##Colombia_Paper.pdf. No questionnaire or codebook ships.
##Usage: Rscript holland_2024.R <raw dir> <output dir>
##
##Face-to-face Qualtrics-offline survey by CNC in Cali and Cucuta, Aug-Oct 2019: 1,005
##Colombian citizens (household sample) and 1,612 Venezuelan migrants. TWO TABLES, one per
##sample, because the authors analyse them separately (main-text Figure 2 = Colombians; SI
##Figure S5 = Venezuelans; separate cjoint::amce fits, never pooled):
##  holland_2024_migrants_col (1,003 respondents), holland_2024_migrants_ven (1,608); 2 and 4
##  respondents answered none of the 5 tasks and so have no rows.
##Each respondent saw 5 pairs (task 1-5; rd_<task>_a = profile 1, rd_<task>_b = profile 2) of
##migrant profiles with 7 attributes, all randomized independently with no restriction
##visible in the data: identity (origin), gender, race, skill level, probability of
##employment, reason for leaving, partisanship. attr_* hold the AUTHORS' ENGLISH labels as
##stored in the deposit; respondents saw Spanish text, which is not deposited. Note the article
##describes origin as "IDP from Valle del Cauca / IDP from Norte de Santander / Venezuelan",
##the data as "Colombians displaced from around Cali / Cucuta" and "Venezuelans".
##Outcome: choice, forced choice, no opt-out: respondents "selected which migrant they would
##prefer to stay in their city and receive housing and employment assistance" (article; exact
##Spanish wording not deposited). Source con<task> = 1 (profile a) / 2 (profile b). Tasks with no
##answer are omitted (Colombians 29 tasks, Venezuelans 44). In the Colombian file the reason-for-
##leaving level of task 3, profile b is missing for 51 respondents (source rows 955-1005); those
##51 task-3 pairs are dropped, as the authors' drop_na() does (the respondents' other tasks stay).
##Covariates kept: cov_gender (source `male` 0/1; Colombia_SI.Rnw L382-385 and L721-724 label
##0 = Female, 1 = Male -> female/male), cov_city (Cali / Cucuta), cov_left_right (pol_ideo,
##"Ideologia (izquierda / derecha)", 1 = left .. 10 = right; Venezuelans have 194 missing),
##cov_pilot_test (source pilot_test 0/1; the authors keep pilot-flagged interviews in every
##analysis, so they are kept here too). Age, education, etc. are stored as unlabelled codes and
##are dropped. No survey weight is deposited or described. DROPPED for privacy: the deposit's public files contain respondents' names,
##phone numbers, street addresses, neighbourhoods, IP addresses, GPS coordinates, Qualtrics
##response IDs and free text; none of it is read into the output. id = row number of the source
##file (the authors' own id), re-keyed within each table.
##Counts: the files hold 1,005 Colombians and 1,612 Venezuelans, matching the article (N=1,612
##Venezuelans stated; "1,000 Colombians" rounded); 1,003 and 1,608 answered at least one task.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
feat <- c(identity = "Identity of Migrant", gender = "Gender", race = "Race", skill = "Skill Level",
          employment = "Probability of Employment", reason = "Reason for Leaving", partisanship = "Partisanship")
build <- function(file) {
  s <- as.data.table(readRDS(file.path(raw, file)))
  s[, id := .I]
  stopifnot(s$male %in% 0:1)
  d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
    x <- data.table(id = s$id, task = t, profile = p, con = as.integer(s[[paste0("con", t)]]))
    for (f in names(feat)) x[, paste0("attr_", f) := s[[paste0("rd_", t, "_", c("a", "b")[p], "_", feat[[f]])]]]
    x
  }))))
  d[, miss := rowSums(is.na(.SD)) > 0, .SDcols = patterns("^attr_")][, miss := any(miss), .(id, task)]
  d <- d[!is.na(con) & !miss][, choice := as.integer(con == profile)][, c("con", "miss") := NULL]
  cv <- s[, .(id, cov_gender = c("female", "male")[as.integer(male) + 1L], cov_city = city, cov_left_right = as.integer(pol_ideo),
              cov_pilot_test = as.integer(pilot_test))]
  d <- merge(d, cv, by = "id")
  stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
            !anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
  setcolorder(d, c("id", "task", "profile", "choice"))
  setorder(d, id, task, profile)
  d
}
col <- build("colombia_clean.RDS"); stopifnot(uniqueN(col$id) == 1003)
ven <- build("venezuelans_clean.RDS"); stopifnot(uniqueN(ven$id) == 1608)
fwrite(col, file.path(out, "holland_2024_migrants_col.csv"))
fwrite(ven, file.path(out, "holland_2024_migrants_ven.csv"))
