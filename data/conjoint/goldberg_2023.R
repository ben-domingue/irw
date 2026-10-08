##Deliberative citizen forum conjoint (Germany) from
##Goldberg, S., & Bächtiger, A. (2023). Catching the 'deliberative wave'? How (disaffected) citizens
##assess deliberative citizen forums. British Journal of Political Science, 53(1), 239-247.
##https://doi.org/10.1017/S0007123422000059 (online 2022; corrigendum 10.1017/S0007123422000205)
##Replication data: Harvard Dataverse doi:10.7910/DVN/GHHVFV, CC0 1.0. File read:
##conjointdata_BJPolS.csv (datafile 5858445). Read as text only: BJPolS_DeliberativeWave_script.R;
##also the article and its Online Appendix (Cambridge sup001.docx, A1-A4; the article is CC BY 4.0).
##Usage: Rscript goldberg_2023.R <dir holding conjointdata_BJPolS.csv> <output dir>
##
##2,039 German adults (YouGov quota sample, December 2020; article), 6 comparisons of 2 citizen-forum
##scenarios each (24,468 rows = 2,039 x 12, as in the article's Figure 1 note). Task = comparision_table
##(1-6), profile = vignette ("citizen forum 1" = Citizen Forum A = 1, "citizen forum 2" = 2); both
##RECORDED. 9 attributes; the numeric codes are labelled from the authors' factor(labels = ...) calls
##in the script (code k = k-th label), English labels of German display text (Appendix A1 glossary
##"translated from German"): issue (Emissions, Refugees, Currency [crypto currencies], Foreign aid),
##initiative (NGO, Government), recruitment (Random selection, Self-selection), size (Small, Medium,
##Large), composition (Citizens alone, Mixed groups), output (In favor of measure, Against measure),
##consensus (Narrow majority, Clear majority), format (Face-to-face, Online), authorization
##(Recommendation, Referendum [recommendation followed by referendum], Binding decision).
##Article: "attribute values were fully randomized"; attribute order randomized per respondent
##(not recorded) with the policy issue always first. The issue is the same for both scenarios in 3,019
##of 12,234 tasks (no restriction).
##Outcomes (Appendix A2, translated from German):
##  choice: "Which of the two scenarios do you prefer?" (Citizen Forum A, Citizen Forum B); forced, the
##    intro asks respondents to choose "regardless of your overall assessment"; exactly one per task.
##  rating: "In your view, how do you feel about Citizen Forum A/B?" 1 = I don't like it at all ...
##    7 = I like it very much.
##Dropped: the source row number, scenario (= 2*(task-1)+profile), outcome.fav (derived: output vs
##respondent's own measure support), and respondent items whose meaning the deposit does not give
##(q3_1-3, q7_1-4, q21, q22). The article says the sample was weighted, but no weight is deposited.
##Covariates kept (codes as stored; wording from Appendix A4 and the authors' script, which uses
##q2 for satisfaction, q6_1-2 for external efficacy, q13_1-4 for stealth and q12_1-7 + q13_1 for
##populism; the item-to-number order within a battery is not documented):
##  cov_satisfaction_democracy (q2: "How satisfied are you with the way democracy works in Germany?"
##  1 not satisfied at all - 7 very satisfied), cov_external_efficacy_1/_2 (q6_1/q6_2, 1 strongly
##  disagree - 5 strongly agree), cov_populism_1.._7 (q12_1-7, 1-7), cov_stealth_1.._4 (q13_1-4, 1-7).
##trial_screen_seconds: time on that comparison's screen (page_p_screen<t>_timing).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conjointdata_BJPolS.csv"))
stopifnot(nrow(s) == 24468, uniqueN(s$ID) == 2039, s[, .N, ID][, all(N == 12)])
s[, task := as.integer(comparision_table)][, profile := match(vignette, c("citizen forum 1", "citizen forum 2"))]
stopifnot(!anyNA(s$profile), s[, .N, .(ID, task)][, all(N == 2)], s[, uniqueN(profile), .(ID, task)][, all(V1 == 2)])
stopifnot(s[, sum(choice), .(ID, task)][, all(V1 == 1)], all(s$evaluation %in% 1:7))
lv <- function(x, l) { stopifnot(all(x %in% seq_along(l))); l[x] }
d <- s[, .(id = as.integer(ID), task, profile, choice = as.integer(choice), rating = as.integer(evaluation),
  attr_issue = lv(issue, c("Emissions", "Refugees", "Currency", "Foreign aid")),
  attr_initiative = lv(initiative, c("NGO", "Government")),
  attr_recruitment = lv(recruitment, c("Random selection", "Self-selection")),
  attr_size = lv(size, c("Small", "Medium", "Large")),
  attr_composition = lv(composition, c("Citizens alone", "Mixed groups")),
  attr_output = lv(output, c("In favor of measure", "Against measure")),
  attr_consensus = lv(consensus, c("Narrow majority", "Clear majority")),
  attr_format = lv(format, c("Face-to-face", "Online")),
  attr_authorization = lv(authorization, c("Recommendation", "Referendum", "Binding decision")),
  cov_satisfaction_democracy = q2, cov_external_efficacy_1 = q6_1, cov_external_efficacy_2 = q6_2,
  cov_populism_1 = q12_1, cov_populism_2 = q12_2, cov_populism_3 = q12_3, cov_populism_4 = q12_4,
  cov_populism_5 = q12_5, cov_populism_6 = q12_6, cov_populism_7 = q12_7,
  cov_stealth_1 = q13_1, cov_stealth_2 = q13_2, cov_stealth_3 = q13_3, cov_stealth_4 = q13_4)]
tm <- as.matrix(s[, paste0("page_p_screen", 1:6, "_timing"), with = FALSE])
d[, trial_screen_seconds := tm[cbind(seq_len(nrow(s)), s$task)]]
stopifnot(d[, uniqueN(cov_satisfaction_democracy), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "goldberg_2023_citizen_forums.csv"))
