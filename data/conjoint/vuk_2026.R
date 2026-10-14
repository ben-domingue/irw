##Factorial vignette experiment on participation type x selection mode x policy topic (Spain and Switzerland) from
##Vuk, V. (2026). Can online participation match in-person democratic engagement? Evidence from a cross-national experiment.
##Policy & Internet, 18(3). https://doi.org/10.1002/poi3.70053
##Replication data: Harvard Dataverse doi:10.7910/DVN/UD4JMF, CC0 1.0. Files read: policy_internet_df.tab (saved locally as
##df.csv, the original CSV), MainAnalysis_Policy&Internet.Rmd (saved as main.Rmd; text, not run).
##Usage: Rscript vuk_2026.R <dir holding df.csv> <output dir>
##
##6,031 respondents (Spain 3,030; Switzerland 3,001; the paper says "over 6000"), each rated TWO vignettes (12,062 rows;
##the 12,063-line CSV has one header). 4,040 respondents saw one control vignette and one treated vignette, 1,991 saw two
##treated vignettes. Vignette = a participatory process about one of four policy topics. Three attributes, level text =
##the short tags stored in the deposit: the vignette wording is NOT in the deposit and the article page (Wiley) could not be
##retrieved (HTTP 403), so the attribute level text is the TAGS ONLY (flag for Ben, ruling 10-13):
##  attr_topic: cars / police / community / public (two safety topics, police vs community; two traffic topics, cars vs public)
##  attr_participation: eparticipation (online) / minipublic (in-person) / (not shown)
##  attr_selection: selfselection / sortition / (not shown)
##The control vignette (vignette name starts "control"; treatment == decision == "control") carries no participation process;
##both process attributes are coded "(not shown)" (inferred from the Rmd: treatment "control" and decision "control"). The vignette code
##(e.g. "epalotcars") confirms the 20 cells = 4 topics x (2 participation x 2 selection + control); the 20 names agree with the columns.
##Task = row order within respondent (1, 2), inferred (the deposit has no task column; order of presentation not documented);
##profile = 1. Rating outcomes (raw, 1-10; question wording and anchors not in the deposit):
##  rating_fairness  fairness_score  (1-10)   rating_acceptance  acceptance_score  (1-10)
##Spain and Switzerland are pooled in one table (the authors pool them with a country interaction, and the tag text is shared); cov_country.
##Randomization restrictions: the cells are a full crossing apart from the control cell (selection is undefined without a process).
##Covariates: cov_country, cov_gender (Female/Male as labelled), cov_age (years), cov_education_code (1-6, no mapping in the deposit),
##cov_income_code (1-10, no mapping), cov_polit_ideology (1-11 as stored; endpoints not documented), cov_demo_satisfaction (1-10 as stored),
##cov_topic_safety_code, cov_topic_traffic_code (1/2 per respondent, used by the authors with the topic to define "winner"/"loser" of the
##decision; the respondent's preference per the Rmd, meaning of 1 and 2: 1 = police / cars as the topic is coded).
##Dropped: ResponseId (Qualtrics; re-keyed), region (undocumented codes that differ by country).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "df.csv"))
stopifnot(nrow(d) == 12062, uniqueN(d$ResponseId) == 6031, !anyNA(d))
d[, id := match(ResponseId, unique(ResponseId))]
d[, task := seq_len(.N), by = id]
stopifnot(all(d[, .N, by = id]$N == 2),
  all(d[, uniqueN(topic_safety) == 1 & uniqueN(topic_traffic) == 1 & uniqueN(country) == 1, by = id]$V1),
  all((d$treatment == "control") == (d$decision == "control")))
r <- d[, .(id, task, profile = 1L, rating_fairness = as.integer(fairness_score), rating_acceptance = as.integer(acceptance_score),
  attr_topic = topic,
  attr_participation = fifelse(treatment == "control", "(not shown)", treatment),
  attr_selection = fifelse(decision == "control", "(not shown)", decision),
  cov_country = fifelse(country == "spain", "Spain", "Switzerland"), cov_gender = tolower(gender), cov_age = as.integer(age),
  cov_education_code = as.integer(education), cov_income_code = as.integer(income), cov_polit_ideology = as.integer(polit_ideology),
  cov_demo_satisfaction = as.integer(demo_satisfaction), cov_topic_safety_code = as.integer(topic_safety),
  cov_topic_traffic_code = as.integer(topic_traffic))]
stopifnot(all(r$rating_fairness %in% 1:10), all(r$rating_acceptance %in% 1:10))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "vuk_2026_participation_legitimacy.csv"))
