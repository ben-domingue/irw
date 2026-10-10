##Public-servant choice conjoints (China) from
##Zhang, Y., & Wang, H. (2024). Symbolic bureaucratic representation and client cooperation:
##Experimental insights from four daily public service scenarios in China. Public
##Administration. https://doi.org/10.1111/padm.13042
##Replication data: Harvard Dataverse doi:10.7910/DVN/BGT4ZB, CC0 1.0. Files read:
##Replication_data_PublicAdiministration.tab (Dataverse tab-delimited download of the .dta,
##datafile 10547931; no Stata value labels survive in it). Read as text, not run:
##Appendix A_Questionaire.docx (Chinese questionnaire + English translation) and
##Replication_Code_PublicAdiministration.do.
##Usage: Rscript zhang_2024_bureaucrat.R <dir holding the .tab> <output dir>
##
##1,600 Chinese online respondents (quota on age band: 400/480/400/320), four paired
##scenarios ("experiments" 1-4 in the questionnaire), one task each, 2 public servants (A/B)
##per task. Two tables, because experiment 4 uses a different attribute set:
##  zhang_2024_bureaucrat_cooperation: experiments 1-3 (task = source `round` 1-3;
##    trial_scenario = traffic stop / subway ID check / government service hall), attributes
##    sex, age (4 bands), accent, wearing a Party badge. Same attribute set, population and
##    fielding, so one table; the authors estimate each scenario separately.
##  zhang_2024_hotline_operator: experiment 4 (source round 4; task = 1, it was the 4th
##    scenario shown), 12345 hotline operator: sex, age as heard (young / older), accent,
##    AI chatbot vs human.
##profile = last digit of source `profile_order` (11,12,...,42 = round*10 + profile). Exactly
##one profile chosen in every task (no opt-out).
##Outcomes (questionnaire wording; Chinese original, the docx English translation is quoted):
##  choice  = Cooperation_choice, e.g. "Which traffic police officer would you like to
##            cooperate with?" (exp 4: "Which phone operator would you like to continue
##            discussing your needs with?"), forced A/B.
##  rating  = Cooperation_willingness, "To what extent are you willing to cooperate with ...
##            A/B? (On a ten-point scale, with 1 being low and 10 being high)" (exp 3: likelihood
##            of going to counter A/B), 1-10, higher = more willing.
##  rating_protect = Perceived_active_representation, "To what extent do you believe ... A/B
##            would protect your interests?", 1-10, higher = more.
##Attribute text is the Chinese text in the questionnaire grid. The tab file holds codes only;
##the mapping to text comes from the authors' own derived variables in the same file:
##  Sex 1 = 男性 (male), 2 = 女性: Same_gender = 1 exactly when Sex equals respondent gender,
##    and the authors' `female` dummy is 1 for gender 2.
##  Age 1-4 = 20岁到29岁 / 30岁到39岁 / 40岁到49岁 / 50岁或以上: Same_age_cohort = 1 exactly
##    when Age equals Age_sample, whose bands the .do file titles give (Age_sample 1 = "18 to
##    29 years old" ... 4 = "50 years of age or older").
##  NL (exp 4) 1 = 听起来年轻 (sounds young), 2 = 听起来年龄较大: Same_age_cohort = 1 for NL 1
##    with Age_sample 1-2 and NL 2 with Age_sample 3-4 (NL1/NL2 dummies).
##  Party 1 = 是 (wears badge), 2 = 否: Same_party_affiliation = 1 for Party 1 x CCP member and
##    Party 2 x non-member.
##  Human (exp 4) 1 = 人工智能机器人 (AI chatbot), 2 = 真人 (human): Human_voice = 1 iff Human = 2.
##  Accent 1/2/3 = 本地口音 / 外地口音 / 标准普通话 (local / non-local / standard Mandarin).
##    INFERRED from the questionnaire order only: Same_accent = 1 exactly when Accent equals the
##    respondent's `accent` (Q26 local dialect / hometown dialect / Mandarin, same order), which
##    ties the two codings together but does not itself name them.
##Attribute order was randomized ("顺序和水平随机化", questionnaire) but is not recorded; no source
##documents restrictions or level probabilities (shares near-equal).
##Covariates: cov_age (age, years), cov_gender (authors' `female` dummy: 1 = female, 0 = male),
##cov_age_group (Age_sample quota band, text from the .do titles), cov_province (text),
##cov_ccp_member (authors' 0/1), cov_han (0/1, Han), cov_birth_local (0/1),
##cov_year_residence (Q28, years in the city; NA for locals), cov_pullover, cov_id_check,
##cov_hall, cov_hotline (0/1, prior experience, Q29-32). Coded without a codebook (keep codes):
##cov_education_code (edu 1-5), cov_accent_code (respondent's dialect 1-3), cov_area_code (1-4,
##undocumented). No survey weight.
##Dropped: the authors' dummies (Sex1/2, Age1-4, NL1/2, Accent1-3, Party1/2, Human1,
##Human_voice, Pull_over/ID_check/Hall/Hotline, male), congruence flags (Same_*,
##Sex_same_*), the duplicate `gender` code (kept as cov_gender) and profile_order.
##Count: 1,600 respondents, 6,400 tasks; the .do file's figure titles give N by age band
##(e.g. "18 to 29 years old: N=800"), which counts rows, not people. Article not checked.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "Replication_data_PublicAdiministration.tab"))
stopifnot(nrow(s) == 12800, uniqueN(s$id) == 1600, s[, .N, id][, all(N == 8)])
## the mapping checks described above
stopifnot(s[, all((female == 1) == (gender == 2))], s[, all(Same_gender == (Sex == gender))],
          s[round < 4, all(Same_age_cohort == (Age == Age_sample))],
          s[round == 4, all(Same_age_cohort == ((NL == 1) == (Age_sample <= 2)))],
          s[round < 4, all(Same_party_affiliation == ((Party == 1) == (CCP_member == 1)))],
          s[round == 4, all(Human_voice == (Human == 2))], s[, all(Same_accent == (Accent == accent))],
          s[, all(profile_order %/% 10 == round)])
scen <- c("交警靠边停车 (traffic stop)", "地铁警察查身份证 (subway ID check)", "政府服务大厅窗口 (government service hall)")
d <- s[, .(id = as.integer(id), task = as.integer(round), profile = as.integer(profile_order %% 10L),
           choice = as.integer(Cooperation_choice), rating = as.integer(Cooperation_willingness),
           rating_protect = as.integer(Perceived_active_representation),
           attr_sex = c("男性", "女性")[Sex], attr_accent = c("本地口音", "外地口音", "标准普通话")[Accent],
           age4 = c("20岁到29岁", "30岁到39岁", "40岁到49岁", "50岁或以上")[Age],
           age2 = c("听起来年轻", "听起来年龄较大")[NL], party = c("是", "否")[Party],
           voice = c("人工智能机器人", "真人")[Human],
           cov_age = as.integer(age), cov_gender = fifelse(female == 1, "female", "male"),
           cov_age_group = c("18-29", "30-39", "40-49", "50+")[Age_sample], cov_province = province,
           cov_ccp_member = as.integer(CCP_member), cov_han = as.integer(han), cov_education_code = as.integer(edu),
           cov_accent_code = as.integer(accent), cov_area_code = as.integer(Area), cov_birth_local = as.integer(birth_local),
           cov_year_residence = as.integer(year_residence), cov_pullover = as.integer(pullover),
           cov_id_check = as.integer(id_check), cov_hall = as.integer(hall), cov_hotline = as.integer(hotline))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, all(rating %in% 1:10 & rating_protect %in% 1:10)])
cv <- grep("^cov_", names(d), value = TRUE)
a1 <- d[task <= 3][, `:=`(attr_age = age4, attr_party_badge = party, trial_scenario = scen[task])]
stopifnot(!anyNA(a1[, .(attr_sex, attr_accent, attr_age, attr_party_badge)]))
a1 <- a1[, c("id", "task", "profile", "choice", "rating", "rating_protect", "trial_scenario",
             "attr_sex", "attr_age", "attr_accent", "attr_party_badge", cv), with = FALSE]
a4 <- d[task == 4][, `:=`(task = 1L, attr_age = age2, attr_voice = voice)]
stopifnot(!anyNA(a4[, .(attr_sex, attr_accent, attr_age, attr_voice)]))
a4 <- a4[, c("id", "task", "profile", "choice", "rating", "rating_protect",
             "attr_sex", "attr_age", "attr_accent", "attr_voice", cv), with = FALSE]
setorder(a1, id, task, profile); setorder(a4, id, task, profile)
fwrite(a1, file.path(out, "zhang_2024_bureaucrat_cooperation.csv"))
fwrite(a4, file.path(out, "zhang_2024_hotline_operator.csv"))
