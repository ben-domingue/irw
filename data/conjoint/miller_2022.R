##Lobbyist access-targeting conjoint (members of Congress as profiles) from
##Miller, D. R. (2022). On whose door to knock? Organized interests' strategic pursuit of access
##to members of Congress. Legislative Studies Quarterly, 47(1), 157-192 (online 2021-01-23).
##https://doi.org/10.1111/lsq.12328
##Replication data: Harvard Dataverse doi:10.7910/DVN/YWTALO, CC0 1.0, no restricted files.
##Files read: LDAsurveydata.csv (one row per respondent x task x profile, level text stored),
##resp_data.csv (respondent covariates, linked by ResponseID), design.dat (the Hainmueller et
##al. design-generator file: levels, weights, restrictions). Read as text only: README.txt,
##CODEBOOK.txt, ReplicationCode_Main.R. sample_data.csv (lobbying-report amounts and client
##categories of the whole sample frame) is not used.
##Usage: Rscript miller_2022.R <raw dir> <output dir>
##
##Survey of lobbyists sampled from Lobbying Disclosure Act reports. 991 respondents have conjoint
##rows; each had 2 tasks (issue ACR and SCA, two policy scenarios; the abbreviations are not
##expanded in the deposit) of 2 members of Congress (uniqid mem1 / mem2 = profile 1 / 2).
##task = 1 for ACR, 2 for SCA; the deposit does not record which was shown first (inferred).
##trial_issue = ACR / SCA; trial_stage = the legislative stage of the proposal (committee /
##floor), randomized per task and the same for both profiles (stopifnot), which the author
##analyses as a respondent-varying attribute.
##Attributes (level text = data = design.dat): attr_pty Democrat/Republican; attr_num_const
##(latent district support for the interest) Very low/Low/Moderate/High; attr_seniority
##Freshman/1 term/3 terms/7 terms; attr_position Support/Oppose/Undeclared; attr_cmte (on the
##committee of jurisdiction) Yes/No; attr_mov (margin of victory) Less than 10%/10% to 20%/
##20% to 30%/More than 30%; attr_pac No/Yes; $100/Yes; $500/Yes; $1000; attr_cosponsor Yes/No;
##attr_cmteldr None/Subcommittee chair/Subcommittee ranking member. Variable names, not the
##displayed row labels, are the only attribute names in the deposit.
##Weights (design.dat): uniform within every attribute. Restrictions (design.dat): no
##subcommittee leadership unless on the committee; Democrats can be Subcommittee chair but not
##ranking member, Republicans ranking member but not chair; a cosponsor always has position
##Support.
##Outcomes (CODEBOOK.txt; exact question wording not in the deposit):
##  choice = "whether respondent chose member as more attractive target", one of the two; no
##           opt-out (exactly one chosen in every answered task).
##  rating = "respondent's five-point ordinal level of interest in meeting with the member",
##           1-5 as stored; anchors not documented (chosen profiles average 4.4, unchosen 3.5,
##           so higher = more interest).
##Tasks with neither outcome are dropped (657 tasks), leaving 670 respondents (= the rows of
##resp_data.csv; paper N not checked); 18 tasks have rankings but no choice
##(choice NA on both profiles) and 15 have a choice with one or both rankings missing; 1 profile
##row with neither outcome (its task has no choice, the other profile is ranked) is dropped.
##Covariates from resp_data.csv (all 670 kept respondents match), answer text as
##stored: cov_gender (Female/Male -> female/male), cov_age_group, cov_education, cov_race,
##cov_income, cov_ideology, cov_party_id (PID3), cov_party_id7 (PID7, the branched party
##question's answer text), cov_years_experience, cov_position (CurrPosition, the author's
##categories), cov_prev_member_congress / _cong_staff / _pres_appointee / _civil_servant /
##_eop / _other (1 = the respondent ticked that previous-experience option, 0 = not), and
##cov_prev_none (PrevExp_None, 0/1 as stored). Respondent IDs are Qualtrics ResponseIDs,
##re-keyed to integers in order of first appearance.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "LDAsurveydata.csv"), na.strings = c("NA", ""))
r[, mem := sub("^[A-Z]+_mem([0-9])_.*$", "\\1", uniqid)]
stopifnot(all(r$mem %in% c("1", "2")), all(r$issue %in% c("ACR", "SCA")),
          r[, .N, .(respondent, issue, mem)][, all(N == 1)],
          r[, uniqueN(stage), .(respondent, issue)][, all(V1 == 1)])
r[, id := match(respondent, unique(respondent))]
d <- r[, .(id, task = match(issue, c("ACR", "SCA")), profile = as.integer(mem), choice = as.integer(choice),
           rating = as.integer(ranking), attr_pty = pty, attr_num_const = num_const, attr_seniority = seniority,
           attr_position = position, attr_cmte = cmte, attr_mov = mov, attr_pac = PAC, attr_cosponsor = cosponsor,
           attr_cmteldr = cmteldr, trial_issue = issue, trial_stage = stage, respondent)]
d[, keep := any(!is.na(choice) | !is.na(rating)), .(id, task)]
d <- d[keep == TRUE][, keep := NULL]
stopifnot(d[, .(n = .N, s = sum(choice), na = sum(is.na(choice))), .(id, task)][, all(n == 2 & (na == 2 | (na == 0 & s == 1)))],
          all(d$rating %in% c(1:5, NA)), !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          d[attr_cmte == "No", all(attr_cmteldr == "None")],
          d[attr_pty == "Democrat", !any(attr_cmteldr == "Subcommittee ranking member")],
          d[attr_pty == "Republican", !any(attr_cmteldr == "Subcommittee chair")],
          d[attr_cosponsor == "Yes", all(attr_position == "Support")])
d <- d[!(is.na(choice) & is.na(rating))]   # 1 profile row: its task has no choice and only the other profile was ranked
p <- fread(file.path(raw, "resp_data.csv"), na.strings = c("NA", ""))
stopifnot(!anyDuplicated(p$ResponseID))
yn <- function(x) as.integer(!is.na(x) & x != "No")
cv <- p[, .(respondent = ResponseID, cov_gender = tolower(Gender), cov_age_group = Age, cov_education = Education,
  cov_race = Race, cov_income = Income, cov_ideology = Ideology, cov_party_id = PID3, cov_party_id7 = PID7,
  cov_years_experience = Years_Experience, cov_position = CurrPosition,
  cov_prev_member_congress = yn(PrevExp_MemCongress), cov_prev_cong_staff = yn(PrevExp_CongStaff),
  cov_prev_pres_appointee = yn(PrevExp_PresApp), cov_prev_civil_servant = yn(PrevExp_Bureaucrat),
  cov_prev_eop = yn(PrevExp_EOP), cov_prev_other = yn(PrevExp_Other), cov_prev_none = as.integer(PrevExp_None))]
stopifnot(all(cv$cov_gender %in% c("female", "male", NA)))
d <- merge(d, cv, by = "respondent", all.x = TRUE)[, respondent := NULL]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "miller_2022_lobbyist_access.csv"))
