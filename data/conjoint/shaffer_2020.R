##Refugee-group receptivity conjoint of US local elected officials from
##Shaffer, R., Pinson, L. E., Chu, J. A., & Simmons, B. A. (2020). Local elected officials'
##receptivity to refugee resettlement in the United States. Proceedings of the National Academy
##of Sciences, 117(50), 31722-31728. https://doi.org/10.1073/pnas.2015637117
##Replication data: Harvard Dataverse doi:10.7910/DVN/U9IWNR, CC0 1.0, no restricted files.
##File read: cpss_localrefugees_data.csv (Dataverse "original format" download of
##cpss_localrefugees_data.tab). The deposit has no codebook or questionnaire; wording below is
##from the article (the SI Appendix, which has the survey text, could not be retrieved).
##Usage: Rscript shaffer_2020.R <raw dir> <output dir>
##
##CivicPulse online survey of US town, municipal, township and county elected officials (April
##2020). 3 tasks, each a pair of hypothetical refugee groups (Group A = profile 1, Group B =
##profile 2) described by 7 attributes, levels stored as text in the deposit (conjoint_<task>_
##<row>A/B, attribute name in conjoint_<task>_<row>T): Age, Education, Group makeup, Language
##skills, Region of origin, Religion, Sponsored by. Attribute order was randomized once per
##respondent (the T columns give the same order in all 3 tasks for every respondent); the row
##position is kept as attrpos_<name> (1 = top).
##Outcome. Article: respondents "indicated whether they were receptive to either group, group A
##only, group B only, or neither group" settling in their community. One answer per task, stored
##in CPSS_05 (task 1), CPSS_07 (task 2), CPSS_09 (task 3); the a/b suffix is the version with the
##response options in the order neither..either (a) or either..neither (b)
##(conjoint_response_order; respondents saw one version), kept as trial_response_order
##(neither_either / either_neither; NA where the deposit lacks it). The four-way answer is not a
##pick among the profiles (both groups can be accepted), so it is stored as the authors' binary
##"Refugee Group Receptivity": rating = 1 if this group was accepted ("Either group" or
##"Group <this> only"), 0 otherwise. The two ratings of a task recover the answer exactly
##(1/1 either, 1/0 A only, 0/1 B only, 0/0 neither).
##Sample. 688 rows in the file. Kept: the 574 officials with saved attribute levels who answered
##at least one task (the article's N = 574; 534 answered all three). Dropped: 83 with attributes
##but no answer, 22 who answered but whose attribute levels were not saved (levels missing in
##source), 9 with neither. Tasks with no answer are omitted. 3,324 profile rows (1,662 tasks), as
##in the article's regression N.
##Restrictions/level probabilities: not documented in the deposit (article points to SI 1-2).
##Covariates (locality-level, as in the deposit): cov_level (county / municipality / township),
##cov_unemploy_3, cov_college_prop_3, cov_urban_prop_3 (terciles 1-3 of locality unemployment,
##college share, urban share; deposit codes), cov_population_median (deposit values 0 / 0.5 / 1;
##not documented), cov_votes2016_majority_trump (1 = locality majority Trump in 2016),
##cov_survey_weight = weight (the article's SI uses a locality weight for a robustness check;
##the in-text estimates are unweighted). cov_cpss_03 = CPSS_03 as answer text (A few times a
##year ... On a daily basis, Never); its question wording is not in the deposit or the article.
##trial_group_size = group_size (10, 25, 50, 100, 250; respondent-level, NA for 26 kept
##respondents): not documented; it is probably the size of the refugee group named in the
##scenario, but no source says so.
##Check: lm(rating ~ all attributes) clustered by id gives the article's AMCEs (Christian vs Muslim
##+9.6, some college +8.3, business sponsor +7.9, single women +8.8, fluent English +5.8,
##agnostic +3.4; high school 7.8 vs 7.7, family 4.5 vs 4.4, functional English 4.9 vs 4.8).
##Dropped: CP_ID (CivicPulse panel ID; re-keyed to integers in file order), CPSS_10 (free text),
##conjoint_order (an index permutation that duplicates the T columns).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "cpss_localrefugees_data.csv"), na.strings = c("", "NA"))
stopifnot(!anyDuplicated(r$CP_ID), nrow(r) == 688)
r[, id := seq_len(.N)]
ans <- list(r[, fcoalesce(CPSS_05a, CPSS_05b)], r[, fcoalesce(CPSS_07a, CPSS_07b)], r[, fcoalesce(CPSS_09a, CPSS_09b)])
stopifnot(r[, all(is.na(CPSS_05a) | is.na(CPSS_05b)) && all(is.na(CPSS_07a) | is.na(CPSS_07b)) && all(is.na(CPSS_09a) | is.na(CPSS_09b))],
          all(unlist(ans) %in% c(NA, "Either group", "Group A only", "Group B only", "Neither group")))
attrs <- c("Age" = "age", "Education" = "education", "Group makeup" = "group_makeup", "Language skills" = "language_skills",
           "Region of origin" = "region_of_origin", "Religion" = "religion", "Sponsored by" = "sponsored_by")
d <- rbindlist(lapply(1:3, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(id = r$id, task = t, profile = p, ans = ans[[t]])
  for (k in 0:6) {
    nm <- r[[sprintf("conjoint_%d_%dT", t - 1, k)]]
    lv <- r[[sprintf("conjoint_%d_%d%s", t - 1, k, c("A", "B")[p])]]
    for (an in names(attrs)) {
      m <- !is.na(nm) & nm == an
      x[m, paste0("attr_", attrs[[an]]) := lv[m]]
      x[m, paste0("attrpos_", attrs[[an]]) := k + 1L]
    }
  }
  x
}))))
d <- d[!is.na(ans)]
ac <- paste0("attr_", attrs)
d <- d[complete.cases(d[, ..ac])]   # 22 answered without saved levels
stopifnot(d[, all(complete.cases(.SD)), .SDcols = paste0("attrpos_", attrs)])
d[, rating := as.integer(ans == "Either group" | ans == c("Group A only", "Group B only")[profile])]
d[, ans := NULL]
# attribute order constant within respondent
stopifnot(d[, lapply(.SD, uniqueN), by = id, .SDcols = paste0("attrpos_", attrs)][, all(unlist(.SD) == 1), .SDcols = -1])
cv <- r[, .(id, trial_response_order = conjoint_response_order, trial_group_size = group_size,
            cov_cpss_03 = CPSS_03, cov_level = Level, cov_unemploy_3 = Unemploy_3, cov_college_prop_3 = College_prop_3,
            cov_urban_prop_3 = Urban_prop_3, cov_population_median = Population_median,
            cov_votes2016_majority_trump = Votes2016_majority_trump, cov_survey_weight = weight)]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "rating", ac, paste0("attrpos_", attrs)))
stopifnot(uniqueN(d$id) == 574, nrow(d) == 3324)
d[, id := match(id, sort(unique(id)))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "shaffer_2020_local_refugees.csv"))
