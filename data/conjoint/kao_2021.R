##Covid-19 compliance vignette experiment (Malawi) from
##Kao, K., Lust, E., Dulani, B., Ferree, K. E., Harris, A. S., & Metheney, E. (2021). The ABCs of
##Covid-19 prevention in Malawi: Authority, benefits, and costs of compliance. World Development,
##137, 105167. https://doi.org/10.1016/j.worlddev.2020.105167
##Replication data: Harvard Dataverse doi:10.7910/DVN/P7YSQA ("Replication Data (raw)", GLD), CC0
##1.0, no restricted files.
##Files read: AuthorityComplianceExperiment_Covid_rawData.tab (Dataverse "original format"
##download, .dta with text answers) and RawData_Codebook_GLD_Malawi_Covid_Authority.pdf (read as
##page images; its text layer is damaged). DataCleaning_GLD_Malawi_Covid_2020.do was read as text.
##Vignette wording and design from the article (PMC7455236, Section 3 and Table 1).
##Usage: Rscript kao_2021.R <dir holding AuthorityComplianceExperiment_Covid_rawData.dta> <output dir>
##
##Single-profile factorial vignette ("single-profile conjoint", article) in the GLD-IPOR phone
##survey of Malawians, May 2020 (sampling frame: phone numbers from the 2016 and 2019 LGPI
##surveys). Each respondent heard ONE vignette (task = profile = 1): "If (many people in your
##area are / a few people in your area are / no one in your area is) sick with Covid-19 and (the
##head of your district hospital / your Traditional Authority / your {religious leader}) asked
##everyone to (stay at home except for essential needs / not gather in groups of more than 50
##people including religious services, weddings, and funerals / frequently wash their hands with
##soap and water)." Three factors, three levels each, "Randomly Chosen - equally likely"
##(codebook). Level text as stored in the data (Q_69, Q_70, Q_71), e.g. attr_prevalence "many
##people in your area are", attr_action "do not gather in groups of more than 50, including
##religious services, weddings, and funerals".
##DROPPED ARM: the religious-leader level was piped from the respondent's religion (Pastor /
##Priest / Sheikh / "religious leader in your district"; codebook note **), the data store it as
##the template "your {0}", and religion is not in the deposit, so the displayed text is not
##saved. Per the IRW rule those 1,510 respondents are dropped; the remaining 3,131 are a random
##two-thirds by design (3,131). The authority factor therefore has 2 levels here.
##Outcomes (codebook wording; asked in a fixed order; "Don't Know/Refuse to Answer" -> NA):
##  choice = Q_73 "Would you be likely to comply with the instructions from {Authority}?" Yes = 1,
##    No = 0 (single-profile accept/reject: opt_out = yes).
##  rating_others_comply = Q_74 "Just to remind you, {Prevalence of Covid-19} in your area are sick
##    with Covid 19, and {Authority} asked everyone to {Action}. When thinking about others in your
##    area complying with the request from {Authority}, would you say that most, some, a few or
##    none would be likely to comply?" stored 1 None, 2 A few, 3 Some, 4 Most (text in the source;
##    numbered here in that order).
##  rating_has_right = Q_75 "Do you think that {Authority} has the right to ask that you {Action}?"
##    1 Yes, 0 No.
##  rating_lessen_risk = Q_76 "Do you think that you will be less likely to get Covid 19 if you
##    {Action}?" 1 Yes, 0 No.
##  rating_will_monitor = Q_77 "Do you think that {Authority} would know/monitor if you {Action}?"
##    1 Yes, 0 No.
##  (Q_75-Q_77 were preceded by the reminder "IF RESPONDENT NEEDS A REMINDER".)
##Covariates (codebook): cov_gender (Q_22 Male/Female; Don't Know/Refuse -> NA), cov_age (Q_23,
##999 -> NA), cov_education (Q_24 answer text; Refuse to answer -> NA), cov_district (Q_25),
##cov_ethnicity (Q_33 answer text; Don't Know/Refuse -> NA; "Other (specify)" kept as text, the
##specify text Q_33_S dropped), cov_trust_<target> (T_Q_93_k "How much do you trust each of the
##following, or haven't you heard enough to say?": government (Government of Malawi),
##opposition_parties, covid_committee (Special Cabinet Committee on Covid 19),
##district_hospital_head, religious_leader, who (World Health Organization), traditional_authority;
##answer text Not at all / Just a little / Somewhat / A lot / Haven't heard enough to say.;
##Refuse to Answer -> NA), cov_best_understands_<target> (A_Q_94_k "Which of the following do you
##think best understands the coronavirus?" multi-select 1/0: traditional_authority,
##religious_leader, district_hospital_head, none), cov_confidence_health_system (Q_98 "Do you have
##confidence in the public/government health system's ability to handle the Covid 19 crisis?") and
##cov_agree_lockdown (Q_99 "Do you agree with the government's recent attempt to implement a
##lockdown?"), both Yes / No / "Don't Know/Refuse to Answer" as stored (the source merges the two).
##SbjNum (the survey's subject number) re-keyed to integers in file order. No survey weight.
##N: 4,641 in the deposit = the article's final sample; 3,131 outside the religious-leader arm, of
##whom 6 answered Don't Know/Refuse to all five outcomes and are omitted: 3,125 kept. choice is NA
##for the remaining Don't Know/Refuse answers to Q_73. Spot check (not compared with a published
##number): a linear model of choice on the three factors gives stay at home -0.11 and handwashing
##+0.07 vs not gathering, in line with the article's finding that costly actions get less compliance.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "AuthorityComplianceExperiment_Covid_rawData.dta")))
stopifnot(!anyDuplicated(k$SbjNum), all(k$Q_70 %in% c("the head of your district hospital", "your Traditional Authority", "your {0}")))
k[, id := seq_len(.N)]
k <- k[Q_70 != "your {0}"]
dk <- "Don't Know/Refuse to Answer"
yn <- function(x) { stopifnot(all(x %in% c("Yes", "No", dk))); fifelse(x == "Yes", 1L, fifelse(x == "No", 0L, NA_integer_)) }
stopifnot(all(k$Q_74 %in% c("None", "A few", "Some", "Most", dk)))
d <- k[, .(id, task = 1L, profile = 1L, choice = yn(Q_73), rating_others_comply = match(Q_74, c("None", "A few", "Some", "Most")),
           rating_has_right = yn(Q_75), rating_lessen_risk = yn(Q_76), rating_will_monitor = yn(Q_77),
           attr_prevalence = Q_69, attr_authority = Q_70, attr_action = Q_71)]
stopifnot(!anyNA(d[, .(attr_prevalence, attr_authority, attr_action)]), all(nzchar(d$attr_action)))
na_if <- function(x, v) fifelse(x %in% v, NA_character_, x)
stopifnot(all(k$Q_22 %in% c("Male", "Female", dk)))
d[, `:=`(cov_gender = fifelse(k$Q_22 == dk, NA_character_, tolower(k$Q_22)), cov_age = fifelse(k$Q_23 == 999, NA_integer_, as.integer(k$Q_23)),
         cov_education = na_if(k$Q_24, "Refuse to answer"), cov_district = na_if(k$Q_25, ""),
         cov_ethnicity = na_if(k$Q_33, c(dk, "")))]
tr <- c(T_Q_93_1 = "government", T_Q_93_3 = "opposition_parties", T_Q_93_6 = "covid_committee", T_Q_93_7 = "district_hospital_head",
        T_Q_93_8 = "religious_leader", T_Q_93_9 = "who", T_Q_93_10 = "traditional_authority")
for (v in names(tr)) d[, paste0("cov_trust_", tr[[v]]) := na_if(k[[v]], c("Refuse to Answer", ""))]
bu <- c(A_Q_94_1 = "traditional_authority", A_Q_94_2 = "religious_leader", A_Q_94_3 = "district_hospital_head", A_Q_94_4 = "none")
for (v in names(bu)) d[, paste0("cov_best_understands_", bu[[v]]) := as.integer(k[[v]])]
d[, `:=`(cov_confidence_health_system = na_if(k$Q_98, ""), cov_agree_lockdown = na_if(k$Q_99, ""))]
d <- d[!(is.na(choice) & is.na(rating_others_comply) & is.na(rating_has_right) & is.na(rating_lessen_risk) & is.na(rating_will_monitor))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kao_2021_covid_compliance.csv"))
