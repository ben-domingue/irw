##Local party chairs' candidate-viability conjoint (US) from
##Doherty, D., Dowling, C. M., & Miller, M. G. (2019). Do local party chairs think women and
##minority candidates can win? Evidence from a conjoint experiment. The Journal of Politics,
##81(4), 1282-1297. https://doi.org/10.1086/704698
##Replication data: Harvard Dataverse doi:10.7910/DVN/SFTMNO, CC0 1.0, no restricted files.
##File read: replication_data_anon.dta (the authors' anonymized analysis file). Design facts,
##question wording and level text from County_Chairs_RaceGender_Online_Appendix.pdf (section 2,
##Table A4) and build_dataset.do (read as text, not run), which shows how the displayed text was
##coded. read_me.docx documents the anonymization.
##Usage: Rscript doherty_2019.R <raw dir> <output dir>
##
##853 Democratic and Republican county party chairs (online survey of chairs; 62.6% Democrats),
##10 tasks x 2 candidates (task and profile recorded: `task`, `candidate`; 1 = Candidate A) in
##a hypothetical primary for the state legislature in the chair's own party.
##Outcome: choice = `choice_`: "Which candidate do you think would fare best in a
##[Democratic/Republican] primary in the area for which you are responsible as a party
##chairperson?" (forced choice, no opt-out). The follow-up 0-100 item ("about how much better
##do you think [Selected Candidate] would do than [Candidate Not Selected]", 0 = only a little
##better, 100 = a lot better) is not stored: the anonymized file keeps only the authors' signed
##pair-level combination (rel_eval_), which is not a rating of each profile.
##Display: each profile showed the candidate's NAME plus FOUR of 10 attribute rows: three of the
##six background characteristics with equal probability, then a fourth that was another
##background characteristic (1/3), one of the four issues (1/3), or a "friends describe as"
##descriptor (1/3) (Table A4 note). Rows not drawn are stored as "(not shown)" (exactly four
##shown per profile: checked). Level weights are non-uniform (Table A4: e.g. Married 50%,
##military None 75%, Entire life 35%). Row order on screen is not in the file.
##Attributes and the text stored:
##  attr_name: the candidate's full name as displayed (123 names). The names signal gender and
##     race/ethnicity (white, Black, Latinx); the authors' name coding is in build_dataset.do
##     (crosswalk rows for gender, signal "name").
##  attr_marital_status: Single / Married / Remarried / Currently Divorced (as displayed).
##  attr_children: "0".."4"; attr_years_in_area: "5".."20" or "Entire life" (source 25).
##  attr_abortion: Pro-choice / Pro-life; attr_food_stamps: Increased / Decreased / Kept as they
##     are; attr_gun_laws: More strict / Less strict / Kept as they are; attr_paid_family_leave:
##     Supports / Opposes (as displayed).
##  COARSENED (the anonymized file keeps only the authors' class code, not the displayed
##  descriptor; stored as the class with a marker):
##  attr_occupation_class: displayed a specific job (e.g. "Cardiologist"); stored as its class
##     (Table A4): "Lawyer", "Education", "Medicine", "Financial", "Small Business Owner",
##     "Journalism/Media", "Farmer", "Social Programs", each + " (specific job not recorded)".
##  attr_political_experience: "None" or "Held local office (office not recorded)" (Mayor,
##     Member of Town Council / County Board / School Board, Sheriff).
##  attr_military_service: "None" or "U.S. military service (branch not recorded)".
##  attr_friends_describe_as: "compromise descriptor (wording not recorded)" (e.g. "pragmatic")
##     or "principles descriptor (wording not recorded)" (e.g. "uncompromising").
##Covariates: cov_democrat (chair's party; also which primary was described), cov_gender
##(self-reported: .dta/build_dataset.do L207-208 'Female (1=yes)' on the renamed
##whatisyourgender item, appendix p. 2 'reported being female'; 1 -> female, 0 -> male),
##cov_age (the authors' 2016 minus year of birth, build_dataset.do L169-171; the year itself
##is not deposited), cov_education_code (CODES 1 = no HS .. 6 = post-grad: the deposit labels
##only the two ends, 'Education (1=No HS; 6=post-grad)', so the answer text is unknown and the
##codes are kept), cov_income (1 = <$10k .. 14 = $150k+,
##15 = refused), cov_race_white/black/hispanic/other (0/1), cov_recruit_candidates,
##cov_state_local_requests, cov_federal_requests, cov_connect_donors, cov_advise_congress ("how
##common are the following scenarios": 0 = not at all .. 3 = very common, per the appendix
##response options; codes as deposited). The deposit documents no survey weight.
##Dropped: the anonymized county code (fips) and all county-level context variables (the
##authors added random noise to them for anonymity), the chair's name-based gender/Hispanic
##codings, the authors' derived dummies, congruence and "not presented" indicators, and
##rel_eval_. responseid is already an anonymous integer.
##N: 853 respondents, 16,842 rows = the appendix's Table A3 / A5 counts.
##Spot check: LPM of choice on the authors' name codes (female, Black, Latinx), SE clustered
##by respondent: Black -0.084, Latinx -0.093, female +0.014 (Table A5 with full controls:
##-0.087, -0.098, 0.013).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "replication_data_anon.dta"))))
NS <- "(not shown)"
f <- function(x, map) { y <- unname(map[as.character(x)]); stopifnot(all(is.na(x) == is.na(y))); y[is.na(y)] <- NS; y }
occ <- c("Lawyer", "Education", "Medicine", "Financial", "Small Business Owner", "Journalism/Media", "Farmer", "Social Programs")
d <- data.table(id = as.integer(s$responseid), task = as.integer(s$task), profile = as.integer(s$candidate),
                choice = as.integer(s$choice_), attr_name = s$name_,
                attr_occupation_class = f(s$occupation_, setNames(paste(occ, "(specific job not recorded)"), 1:8)),
                attr_political_experience = f(s$experience_, c(`0` = "None", `1` = "Held local office (office not recorded)")),
                attr_military_service = f(s$military_, c(`0` = "None", `1` = "U.S. military service (branch not recorded)")),
                attr_marital_status = f(s$marital_, c(`0` = "Single", `1` = "Married", `2` = "Remarried", `3` = "Currently Divorced")),
                attr_children = f(s$children_, setNames(as.character(0:4), 0:4)),
                attr_years_in_area = f(s$inarea_, c(setNames(as.character(c(5:15, 18, 20)), c(5:15, 18, 20)), `25` = "Entire life")),
                attr_abortion = f(s$prochoice_, c(`1` = "Pro-choice", `0` = "Pro-life")),
                attr_food_stamps = f(s$foodstamp_, c(`0` = "Decreased", `1` = "Kept as they are", `2` = "Increased")),
                attr_gun_laws = f(s$guns_, c(`0` = "Less strict", `1` = "Kept as they are", `2` = "More strict")),
                attr_paid_family_leave = f(s$proleave_, c(`0` = "Opposes", `1` = "Supports")),
                attr_friends_describe_as = f(s$compromise_, c(`1` = "compromise descriptor (wording not recorded)",
                                                              `0` = "principles descriptor (wording not recorded)")),
                cov_democrat = s$democrat, cov_gender = c("male", "female")[s$female + 1], cov_age = s$age, cov_education_code = s$educ, cov_income = s$income,
                cov_race_white = s$r_white, cov_race_black = s$r_black, cov_race_hispanic = s$r_hispanic, cov_race_other = s$r_other,
                cov_recruit_candidates = s$youactivelyrecruitaprospectiveca, cov_state_local_requests = s$candidatesforstateorlocalofficer,
                cov_federal_requests = s$candidatesforfederalofficereques, cov_connect_donors = s$youhelptoconnectcandidateswithdo,
                cov_advise_congress = s$youprovidestrategicadvicetocandi)
a10 <- grep("^attr_", names(d), value = TRUE)[-1]
stopifnot(rowSums(d[, lapply(.SD, `!=`, NS), .SDcols = a10]) == 4,
          s[, all(is.na(marital_) == (marital_np == 1) & is.na(occupation_) == (occupation_np == 1) &
                  is.na(foodstamp_) == (foodstamp_np == 1) & is.na(guns_) == (guns_np == 1))],
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)], !anyNA(d$attr_name), s$female %in% 0:1)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "doherty_2019_party_chairs.csv"))
