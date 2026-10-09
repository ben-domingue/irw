##Host-community conjoint among displaced and host households (Kasai, DR Congo) from
##Stoop, N., van der Windt, P., & Weber, S. (2025). Where to flee? Preferences for host
##communities among displaced people in Congo. PLOS ONE, 20. https://doi.org/10.1371/journal.pone.0337530
##Replication data: Harvard Dataverse doi:10.7910/DVN/HGIFXF, CC0 1.0, no restricted files, no
##terms. Files read: where2flee_conjoint.csv and where2flee_data.csv (Dataverse original format),
##codebook.xlsx, README. The authors' replication R script was read as text. Article (open access)
##read for the design.
##Usage: Rscript stoop_2025.R <dir holding the two csv files> <output dir>
##
##1,965 households (one respondent each) from a random sample in 119 localities of the Kasai
##provinces (UNHCR survey by INS interviewers, 24 Nov 2022 - 16 Feb 2023; article "Data"),
##conducted in Tshiluba; profiles shown as drawings by a Congolese artist with level text (article
##Fig 2). Two rounds (tasks) of two host-community profiles; 5 binary attributes. Level text as in
##the deposit (English): economic (job availability), social (church membership), local (family
##ties), cultural (language), political (village meetings). The codebook lists slightly different
##spellings ("Cannot joint join local church", "Attend village meeting") from the data; the data's
##text is kept. Attribute order was "randomized between respondents, but fixed across rounds"
##(article) and is not recorded (no attrpos_).
##Outcomes (same tasks, one table):
##  choice = chosen: "choose which of the two safe host communities they would prefer to live
##    in" after imagining having recently fled violence (article; paraphrase). Forced, no opt-out.
##  rating = ranking: "rank how much they would like to live in each presented host community"
##    (article robustness section; paraphrase), stored 0-4 as in the source (codebook says "1 to 4",
##    but 0 occurs 978 times; 5 values); anchors not documented.
##  rating_economic_contribution, rating_feeling_welcome, rating_feeling_safe,
##  rating_contribute_ideas, rating_trust_community: the five statements each profile was rated on
##    ("I could contribute to the economy of this community", "I would feel welcomed in this
##    community", "I would feel safe in this community", "I could improve this community by
##    bringing in new ideas and cultures", "I could trust the members of this community"), "a
##    five-point Likert scale from 'not at all' to 'strongly agree'" (article), stored 0-4.
##Task = round, profile = pr1/pr2 (recorded). Every task has exactly one chosen profile (checked).
##Household IDs (hashed-looking strings) re-keyed to integers.
##Covariates from where2flee_data.csv (codebook value text): cov_pop_group (Host community / IDP
##/ Returned IDP / Repatriated refugee as stored; the codebook says "Resettled refugee"; blank for
##13 households -> NA), cov_gender (gender Male/Female), cov_married,
##cov_religion, cov_schooled, cov_literacy, cov_working (text as stored), cov_food_insecurity
##(score 0-35), cov_trust (trust_num, 0-10). The authors' median splits and religion/language
##dummies are derived and dropped.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
c <- fread(file.path(raw, "where2flee_conjoint.csv"), encoding = "UTF-8")
p <- fread(file.path(raw, "where2flee_data.csv"), encoding = "UTF-8", na.strings = c("NA", ""))
stopifnot(nrow(c) == 7860, c[, .N, ID_Household][, all(N == 4)], c[, sum(chosen), .(ID_Household, round)][, all(V1 == 1)])
ids <- data.table(ID_Household = sort(unique(c$ID_Household)))[, id := .I]
c <- merge(c, ids, by = "ID_Household")
d <- c[, .(id, task = as.integer(round), profile = as.integer(sub("pr", "", profiles)), choice = as.integer(chosen),
           rating = as.integer(ranking), rating_economic_contribution = as.integer(ranking_economic_contribution),
           rating_feeling_welcome = as.integer(ranking_feeling_welcome), rating_feeling_safe = as.integer(ranking_feeling_safe),
           rating_contribute_ideas = as.integer(ranking_contribute_ideas), rating_trust_community = as.integer(ranking_trust_community),
           attr_economic, attr_social, attr_local, attr_cultural, attr_political, ID_Household)]
stopifnot(d[, all(profile %in% 1:2)], d[, !anyNA(.SD), .SDcols = patterns("^attr_")])
cv <- p[, .(ID_Household, cov_pop_group = fifelse(trimws(pop_group) == "", NA_character_, pop_group), cov_gender = c(Male = "male", Female = "female")[gender],
            cov_married = married, cov_religion = religion, cov_schooled = schooled, cov_literacy = literacy,
            cov_working = working, cov_food_insecurity = food_insecurity, cov_trust = trust_num)]
stopifnot(!anyDuplicated(cv$ID_Household), all(ids$ID_Household %in% cv$ID_Household))
d <- merge(d, cv, by = "ID_Household", all.x = TRUE)[, ID_Household := NULL]
setorder(d, id, task, profile)
cat(nrow(d), uniqueN(d$id), "\n")
fwrite(d, file.path(out, "stoop_2025_host_communities.csv"))
