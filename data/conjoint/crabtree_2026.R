##Civilian-perpetrated violence conjoint (US) from
##Crabtree, K. (2026). Racial identity and evaluations of civilian-perpetrated violence in the
##United States. Political Behavior. https://doi.org/10.1007/s11109-026-10173-4
##Replication data: Harvard Dataverse doi:10.7910/DVN/MBANSJ, CC0 1.0, no restricted files
##(one zip). File read: main_analyses.csv from the zip. The authors' replication script
##("Racial Identity and Civilian Perpetrated Violence.R") was read as text for outcome meaning.
##data_weights.csv (white respondents only, entropy-balancing weights `wgt` the author computed
##for a robustness analysis) is not used: an analysis weight, not a survey weight.
##The article is paywalled; no questionnaire, codebook or README is deposited.
##Usage: Rscript crabtree_2026.R <raw dir holding main_analyses.csv> <output dir>
##
##957 US respondents (495 Black, 462 White, as deposited), each shown 7 pairs (choiceNum =
##task, recorded) of descriptions of an act of violence (descripNum = profile 1/2, recorded).
##Seven attributes, stored as the level text in the deposit (the author's labels, e.g. "Arab
##Man", "Fifteen Casualties"; the full sentence respondents read is not deposited, so these may
##be short labels of the displayed text): attr_perpetrator (Man / Arab / Asian / Black /
##Hispanic / White Man), attr_target (People / Arab / Asian / Black / Hispanic / White People),
##attr_tactic (Violence, Knife, Car, Shooting, Bombing), attr_location (No Location Specified,
##Public Area, Community Center, House of Worship, School), attr_casualties (No .. Fifteen
##Casualties), attr_motivation (No Clear Motivation, Personal Grievance, Mental Health Issues,
##Hate, Political Ideology, Religious Ideology), attr_label (Attack, Random Attack, Senseless
##Violence, Hate Crime, Act of Terrorism). "No Location Specified"/"No Clear Motivation" are
##kept as stored (whether such a clause was omitted or displayed is not documented).
##Outcomes (wording not deposited; paraphrases from the variable names and the author's code):
##  choice_anger = anger_Y: which of the two descriptions made the respondent angrier (author's
##     axis label "Less Angry .. More Angry"); exactly one per task, no opt-out.
##  choice_punish = punish_Y: which perpetrator should be punished more ("Less Punitive .. More
##     Punitive"); exactly one per task, no opt-out.
##  rating_punish = punish_score1 (description 1) / punish_score2 (description 2), 1-5, raw;
##     the author's histogram labels it "Support for Life in Prison for Violence Description" and
##     rescales it 0-1 with higher = more punitive (consistent with the data: in 2,829 of 3,113
##     tasks with unequal scores the profile chosen in choice_punish has the higher score).
##     Anchor wording unknown.
##Restrictions: none documented; all two-way level pairs occur. Level weights not documented.
##Covariates (text as deposited; blank -> NA): cov_race (respondent race; sample is Black and
##White respondents only), cov_gender (Female/Male/Other -> female/male/other), cov_party
##(Democrat/Independent/Republican; question wording unknown, so not cov_party_id),
##cov_education, cov_ideology, cov_media_attention, cov_change_violence,
##cov_justify_violence, cov_black_racial_attach / cov_black_linked_fate (asked of Black
##respondents), cov_white_racial_attach / cov_white_linked_fate (asked of White respondents).
##Dropped: Qualtrics ResponseId (re-keyed to integers in order of appearance), row indices,
##anger_preference / punish_preference (the chosen description number, = the choice columns).
##N = 957 respondents x 7 tasks; the paper's N could not be checked (paywalled).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "main_analyses.csv"), na.strings = c("", "NA"))
s[, id := match(ResponseId, unique(ResponseId))]
stopifnot(s[, .N, .(id, choiceNum)][, all(N == 2)], s[, .N, id][, all(N == 14)],
          all(s$descripNum %in% 1:2), !anyDuplicated(s[, .(id, choiceNum, descripNum)]))
d <- s[, .(id, task = as.integer(choiceNum), profile = as.integer(descripNum),
           choice_anger = as.integer(anger_Y), choice_punish = as.integer(punish_Y),
           rating_punish = as.integer(ifelse(descripNum == 1, punish_score1, punish_score2)),
           attr_perpetrator = perp, attr_target = target, attr_tactic = tactic, attr_location = location,
           attr_casualties = casualty, attr_motivation = motivation, attr_label = label,
           cov_race = race, cov_gender = tolower(gender), cov_party = party, cov_education = education,
           cov_ideology = ideology, cov_media_attention = media_attention,
           cov_change_violence = change_violence, cov_justify_violence = justify_violence,
           cov_black_racial_attach = black_racial_attach, cov_black_linked_fate = black_linked_fate,
           cov_white_racial_attach = white_racial_attach, cov_white_linked_fate = white_linked_fate)]
# outcomes: one chosen per task, chosen number agrees with the *_preference column, scores 1-5
stopifnot(d[, .(a = sum(choice_anger), p = sum(choice_punish)), .(id, task)][, all(a == 1 & p == 1)],
          all(s[anger_Y == 1, anger_preference == descripNum]), all(s[punish_Y == 1, punish_preference == descripNum]),
          all(d$rating_punish %in% 1:5), all(d$cov_gender %in% c("female", "male", "other")))
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(nzchar(d[[v]])))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "crabtree_2026_civilian_violence.csv"))
