##Refugee return-destination conjoint (Syrian refugees in Lebanon) from
##Ghosn, F., Chu, T. S., Simon, M., Braithwaite, A., Frith, M., & Jandali, J. (2021). The journey
##home: Violence, anchoring, and refugee decisions to return. American Political Science Review,
##115(3), 982-998. https://doi.org/10.1017/S0003055421000344
##Replication data: Harvard Dataverse doi:10.7910/DVN/UGI0MH, CC0 1.0. File read:
##"Dataset for conjoint analyses.tab" (saved as conj.tab). Read as text only: Journey_Home_Appendix.pdf
##(Appendix C questionnaire, "CONJOINT: REPATRIATION"), "Script for conjoint analyses.txt".
##Usage: Rscript ghosn_2021.R <dir holding conj.tab> <output dir>
##
##Face-to-face tablet survey in Arabic of Syrian refugees in Lebanon (2017). A random subset did
##the conjoint: 5 choice occasions (ChoiceOccasion) of two places in Syria (Place A / Place B),
##4 attributes. The file has no profile column: within respondent x occasion the two rows are
##taken as profile 1, 2 in file order (INFERRED; every pair has exactly one chosen row).
##Outcome (Appendix C): intro "I would like you to imagine a person, like yourself, but this person is
##considering a return to Syria. I would like you to consider the following two places in Syria, where
##there is currently no fighting taking place and tell me which place in Syria you think this person
##should go to." then "Now tell me, which place in Syria would you choose to return to?" Place A /
##Place B / Don't know / No response. The deposit holds only answered tasks (every task has one
##chosen place); DK/no-response tasks are absent, so choice is stored as forced (opt_out no) and
##respondents have 1-5 tasks (389 of 417 have all 5).
##Attribute levels: the deposit codes 1-3; text from the questionnaire's numbered options (Appendix C):
##  HarmR       "Chance of harm on route there": 1 Low, 2 Moderate, 3 High
##  ChancePeace "Chance of peaceful situation lasting at least a year": 1 Low, 2 Moderate, 3 High
##  NumPpl      "Number of people you know living there": 1 None, 2 Some, 3 Many
##  Easework    "Ease of finding work": 1 Easy, 2 Moderate, 3 Difficult
##The mapping agrees with the article's findings (lower harm and easier work preferred; peace and
##people known not significant): choice share by code, harm 0.58/0.51/0.40, work 0.53/0.50/0.47.
##Questionnaire is English (survey administered in Arabic). Randomization restrictions and attribute
##order not documented (cjoint run with design = "uniform").
##N: 417 respondents in the file; the article says 406 respondents were each presented with five
##tasks (not reconciled). Covariates are the respondent variables shipped in the conjoint file,
##as the authors coded them (0/1 dummies, no labels in the deposit): cov_gender_code (Gender 0/1;
##which value is female is not documented in this file), cov_exp_violence (ExpViol, experienced
##at least one form of violence, the paper's key moderator), cov_age (years), and the rest under
##their source names. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conj.tab"))
stopifnot(!anyNA(s[, .(ID, ChoiceOccasion, HarmR, ChancePeace, NumPpl, Easework, Chosen)]))
s[, profile := seq_len(.N), .(ID, ChoiceOccasion)]
stopifnot(s[, .N, .(ID, ChoiceOccasion)][, all(N == 2)], s[, sum(Chosen), .(ID, ChoiceOccasion)][, all(V1 == 1)])
lv <- function(x, l) { stopifnot(all(x %in% 1:3)); l[x] }
d <- s[, .(id = as.integer(ID), task = as.integer(ChoiceOccasion), profile = as.integer(profile), choice = as.integer(Chosen),
           attr_harm_on_route = lv(HarmR, c("Low", "Moderate", "High")),
           attr_chance_of_peace = lv(ChancePeace, c("Low", "Moderate", "High")),
           attr_people_known = lv(NumPpl, c("None", "Some", "Many")),
           attr_ease_of_work = lv(Easework, c("Easy", "Moderate", "Difficult")),
           cov_gender_code = as.integer(Gender), cov_exp_violence = as.integer(ExpViol), cov_married = Married,
           cov_have_children = HaveChildren, cov_age = as.integer(Age), cov_employed_2011 = Employed2011,
           cov_currently_employed = CurrentlyEmployed, cov_displacement_years = DispDurYear, cov_living_in_camp = LivinginCamp,
           cov_prewar_income_below200 = PIncomePreWar_L200, cov_registered_un = RegisteredUN,
           cov_didnt_finish_primary = DidntFinishPrimary, cov_didnt_finish_intermediate = DidntFinishInt,
           cov_close_family_lebanon = CloseFamLBN)]
stopifnot(uniqueN(d$id) == 417, nrow(d) == 4084)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ghosn_2021_refugee_return.csv"))
