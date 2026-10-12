##Politician-profile conjoint (Japan): perceived ideology, from
##Ishima, H., Ashitani, K., & Okada, A. (2026). Confrontation, cooperation, and perceived ideology: Experimental research
##on voters' perceived positions and political competition. Japanese Journal of Political Science.
##https://doi.org/10.1017/S1468109926100449 (authors, journal and year from Crossref)
##Replication data: Harvard Dataverse doi:10.7910/DVN/IXR2EO, CC0 1.0. Files read: ideology_long.csv (CP932,
##datafile 14156967; one row per respondent x task x profile) and manuscript_figure_plots.R (as text). No codebook.
##Usage: Rscript ishima_2026.R <dir holding ideology_long.csv> <output dir>
##
##1,229 Japanese adults (Japanese-language Qualtrics survey), 8 tasks x 2 hypothetical politicians, forced choice of
##one politician (exactly one chosen in every task; 9,832 tasks). Task and profile are recorded (columns task, profile).
##Each respondent was randomly assigned to ONE of three outcome wordings (column `group`): which politician is more
##"left" (left), "liberal" (liberal) or "progressive" (prog); 406/414/409 respondents. The Japanese question text is
##NOT in the deposit (only the codes left/liberal/prog and the analysis code), so the design record's question is a
##paraphrase. `choice` = 1 if the respondent picked that profile as the more left / liberal / progressive politician
##(file column `choice`, which equals the profile number of the respondent's answer in left<t>/liberal<t>/prog<t>;
##checked below). The wording arm is trial_group.
##Attributes (the authors' English codes; the Japanese text shown to respondents is not deposited): coalition
##(with_JCP / not_with_JCP: coalition strategy with the Japan Communist Party), tone (polite / aggressive), issue
##(defense / inequality / surname: the topic of the politician's statement, taken from the codes), age (31, 41, 52, 64, 72),
##career (councilor, doctor, journalist, lawyer, public official, professor, secretary, office worker), gender
##(female / male, the authors' coding of the given name shown), home prefecture (Aichi, Akita, Kagawa, Kyoto, Tokyo).
##A random Japanese surname (file column F_t_p_6) and a given name were also shown; surnames are dropped.
##Attribute order is fixed (F_t_k lists age, career, pref, style, coalition, family, first for every task).
##Randomization restrictions: none documented; attributes look independent (e.g. same issue in 3,317 of 9,832 pairs,
##same career in 1,228, as expected for independent draws). Level weights not documented (shares near equal).
##Dropped: IP address, latitude/longitude, ResponseId, Code (IP/geolocation and Qualtrics ids = PII), timing columns,
##the politeness checks polite<t>_1/2 (undocumented 1-5 ratings), quiz and knowledge scales, reject-party items,
##derived categories (self_cat, soph_cat, age_cat).
##Covariates: cov_gender (female/male; "DK/NA" -> NA), cov_age_group (the band as stored: 10s..70s; "DK/NA" -> NA),
##cov_education (stored text: elementary, high, vocational, college; "DK/NA" -> NA).
##32 rows (2 respondents) are unfinished (Finished = 0) but have every task answered; kept.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "ideology_long.csv"), encoding = "Latin-1", colClasses = list(character = c("gender", "education", "age", "group")))
stopifnot(uniqueN(d$id) == 1229, nrow(d) == 1229 * 16)
## checks: choice is the profile named by the respondent's answer in the group's outcome column
pick <- function(g) { m <- as.matrix(d[, paste0(g, 1:8), with = FALSE]); m[cbind(seq_len(nrow(d)), d$task)] }
ans <- integer(nrow(d))
for (g in c("left", "liberal", "prog")) { i <- which(d$group == g); ans[i] <- pick(g)[i] }
stopifnot(identical(as.integer(d$choice), as.integer(ans == d$profile)))
d[, id := frank(id, ties.method = "dense")]
r <- d[, .(id, task = as.integer(task), profile = as.integer(profile), choice = as.integer(choice),
           attr_coalition = att_coal, attr_tone = att_tone, attr_issue = att_issue, attr_age = as.character(att_age),
           attr_career = att_career, attr_gender = att_gender, attr_home = att_home,
           cov_gender = fifelse(gender %in% c("female", "male"), gender, NA_character_),
           cov_age_group = fifelse(age == "DK/NA", NA_character_, age),
           cov_education = fifelse(education == "DK/NA", NA_character_, education),
           trial_group = group)]
stopifnot(!anyNA(r[, grep("^attr_", names(r)), with = FALSE]), r[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(r, id, task, profile)
fwrite(r, file.path(out, "ishima_2026_perceived_ideology.csv"))
