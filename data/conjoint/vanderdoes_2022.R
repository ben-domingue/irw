##Participatory (neighbourhood) budgeting design conjoint (Netherlands) from
##van der Does, R., & Kantorowicz, J. (2022). Political exclusion and support for democratic
##innovations: Evidence from a conjoint experiment on participatory budgeting. Political
##Science Research and Methods, 11(4), 947-955. https://doi.org/10.1017/psrm.2022.3
##(open access, CC BY 4.0; online February 2022, volume 11 is 2023)
##Replication data: Harvard Dataverse doi:10.7910/DVN/IZ1T9I, CC0 1.0. File read: pb_data.csv
##(Dataverse "original format" download). Also read as text: read_me.txt, pb_script.Rmd
##(the authors' analysis, not run) and the article (Cambridge Core HTML).
##Usage: Rscript vanderdoes_2022.R <dir holding pb_data.csv> <output dir>
##
##3,246 Dutch adults (three Dynata online surveys, February-March 2019, quotas on sex and age;
##pooled as in the article), 6 tasks x 2 neighbourhood budgets (NBs). Task and profile are
##recorded (columns task, profile; profile 1 = left). The article reports 3,246 respondents
##and 38,952 observations: both match. Scenario (article): the municipality runs a
##neighbourhood budget next year; residents submit project ideas and a winning project gets
##EUR 50,000.
##Outcomes (one table, same tasks):
##  choice = `choice`, the preferred NB of the two (forced choice; exactly one per task,
##           checked). Verbatim wording not in the deposit or the article.
##  rating = `selected`, approval of each NB, 1 = completely disapprove ... 7 = completely
##           approve (article).
##Attributes. FOUR of the five randomized attributes are stored, as the authors' English
##labels (Dutch display text is not deposited; "muninipality" typo kept as in the data):
##who can submit a project, what projects are allowed, municipal support, who chooses the
##winning project. The fifth attribute, the WINNING PROJECT shown (one of eight project types,
##e.g. footpaths, playgrounds), is NOT in the deposit: the file holds only the authors'
##derived `outcome_favorability` (Strong if the respondent's own 1-7 rating of the shown
##project type is above 4, else Weak) and a 3-level variant. Being derived from the
##respondent, not displayed text, both are DROPPED. Because each attribute was randomized
##independently, the four stored attributes remain valid comparisons, but the table cannot
##reproduce the authors' favorability results.
##Attribute order was randomized (article) but not recorded. Restrictions are not
##documented; level shares look uniform.
##Covariates (source codes, no labels deposited): cov_education (1-13), cov_sex (1-4; the
##authors' code treats 1 = male, 2 = female), cov_minority (1 = minority, 2 = majority),
##cov_sample (small_cities: 0 = 10 largest municipalities, 1 = middle-sized and small,
##99 = one of the 10 largest; the three surveys), cov_relational_trust and
##cov_external_efficacy (1-7), cov_pref_<project> = the respondent's 1-7 preference for each
##of the eight project types (Dutch names as stored: voetpaden footpaths, fietspaden bike
##paths, speeltuinen playgrounds, pleinen squares, verlichting lighting, verkeersdrempels
##speed bumps, bosjes shrubs, vuilnisbakken litter bins; translations ours).
##Dropped: X1 (row number), responseid (Qualtrics ResponseId; re-keyed to integers in file
##order), the derived higher_education, gender, minorities, disadvataged (all NA) and the two
##favorability variables.
##Spot check: the article's footnote 7 reports minority respondents more likely to choose
##NBs using random selection (Delta +3.9pp); this table gives the minority-minus-majority
##choice-rate difference for "Residents chosen randomly": 0.50 - 0.46 = +3.9pp, reproduced.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "pb_data.csv"))
stopifnot(nrow(s) == 38952, uniqueN(s$responseid) == 3246)
d <- s[, .(id = match(responseid, unique(responseid)), task = as.integer(task), profile = as.integer(profile),
           choice = as.integer(choice), rating = as.integer(selected),
           attr_who_submits = residents_allowed_submit, attr_projects_allowed = projects_allowed,
           attr_municipal_support = support_municipality, attr_who_chooses_winner = choice_winning_project,
           cov_education = as.integer(education), cov_sex = as.integer(sex), cov_minority = as.integer(minority),
           cov_sample = as.integer(small_cities), cov_relational_trust = as.integer(relational_trust),
           cov_external_efficacy = as.integer(external_efficacy))]
for (p in c("voetpaden", "fietspaden", "speeltuinen", "pleinen", "verlichting", "verkeersdrempels", "bosjes", "vuilnisbakken"))
  d[, paste0("cov_pref_", p) := as.integer(s[[p]])]
stopifnot(!anyDuplicated(d[, .(id, task, profile)]), d[, .N, id][, all(N == 12)],
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, all(rating %in% 1:7)],
          !anyNA(d[, .(attr_who_submits, attr_projects_allowed, attr_municipal_support, attr_who_chooses_winner)]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "vanderdoes_2022_participatory_budgeting.csv"))
