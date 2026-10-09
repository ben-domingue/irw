##Political-participation factorial vignette (Zambia, July-August 2021) from
##Jöst, P., Krönke, M., Lockwood, S. J., & Lust, E. (2024). Drivers of political participation:
##The role of partisanship, identity, and incentives in mobilizing Zambian citizens. Comparative
##Political Studies, 57(9), 1441-1474. https://doi.org/10.1177/00104140231194064
##Replication data: Harvard Dataverse doi:10.7910/DVN/XZVS5B, CC0 1.0, no restricted files.
##File read: Data_for_Replication_Dofile1.dta (Dataverse "original format", saved as data1.dta;
##1,536 rows, one per respondent; .dta value labels give the level text). Read as text:
##Codebook.pdf, DriversOfParticipation_ReplicationDofile.do and ...Dofile2.do, and the article
##(open-access version, KOPS Konstanz; vignette text pp. 1454-1455, Tables 2-3).
##Const_Data_For_Replication_Dofile2.dta (a constituency-merged version used for one robustness
##table) is not used.
##Usage: Rscript jost_2024.R <raw dir> <output dir>
##
##Zambian Election Panel Survey wave 2, by phone, 15 July-10 August 2021 (Lusaka, Eastern and
##Muchinga provinces); n = 1,536 as in the paper. Each respondent heard ONE vignette (task 1,
##profile 1), presentation = text, read by the interviewer after "We realize that campaigns are
##in session, but for right now, I'd like you to consider a hypothetical situation.":
##  "I'd like you to imagine that [authority] is urging you to [activity]. The candidate is a
##  [co-ethnic / not co-ethnic] [man/woman] running for parliament as the [co-party / other
##  party] candidate. {He/she} was [born here/born in a different region] {and/but} [currently
##  lives ...]. Your [authority] is keen on you {activity}, [sanctioning_leader]. [sanctioning_
##  community]. [social_benefit] and [payment]." (article p. 1454-1455)
##11 attributes, all "randomized with equal probability" (article p. 1454): activity, authority,
##ethnicity, partisanship, sanctioning_leader, sanctioning_community, social_benefit, payment,
##origin, residence, gender. Level text = the .dta value labels, verbatim; "{0}" in the
##sanctioning and social-benefit labels is where the script inserted the activity phrase
##(attr_activity). The article's vignette lists "your neighbor" as an authority, but the data,
##codebook and Table 2 have "local religious leader"; the data labels are kept.
##*** attr_ethnicity and attr_partisanship are RELATIVE levels: respondents heard their own
##ethnic group / preferred party piped in ("Co-ethnic", "Party you feel close to"), or a randomly
##chosen other group / party ("Not co-ethnic", "Party you do not feel close to"); the group or
##party actually named was not saved. Partisanship shares are 843/693 and payment 812/724,
##more unequal than chance alone would usually give; no source explains it.
##Outcomes (article Table 3, codebook), all stored RAW (1 = most likely / most):
##  rating: "How likely are you to spend a day {helping campaign for a parliamentary candidate /
##    attending a community meeting ...}?" (q1y) 1 very likely, 2 somewhat likely, 3 not very
##    likely, 4 not likely at all. LOWER = MORE WILLING (the authors reverse it to 0-1).
##  rating_leader_sanction: "How likely is it that your {Authority} would treat you better or
##    worse in the future, depending on whether or not you {Activity}?" (q4y), same 1-4 scale.
##  rating_community_sanction: "How likely do you think it is that other members of your village
##    or neighbor would treat you better or worse in the future, depending on whether or not you
##    {Activity}?" (q5y), same 1-4 scale.
##  rating_enjoy: "How much do you think you would enjoy {Activity}?" (q6y) 1 very much,
##    2 somewhat, 3 not much, 4 not at all.
##  rating_authority_support: "Do you think your {Authority} would support an MP candidate such
##    as the one described here?" (q3y) 1 Yes, 2 No.
##"Don't Know/Refuse to Answer" (not read out; q1y/q4y/q5y code 5, q6y 5-6, q3y 3-4) -> NA.
##6 respondents whose activity and sanctioning/social-benefit levels are missing in the source
##are dropped (1,530 kept); no respondent ID in the deposit, so id = row order.
##Covariates (.dta value labels; refusals -> NA): cov_age (demo_q3, years), cov_gender (demo_q4),
##cov_urban (demo_q12), cov_education (demo_q26), cov_income_situation (demo_q30),
##cov_ethnicity (PD_q2), cov_vote_intention (q36, "If the parliamentary elections were held
##tomorrow, which party's candidate would you vote for?"; vote intention, not party ID),
##cov_ever_participated (q8y "Have you ever attended a meeting to express community concerns to
##an MP or campaignned for an MP candidate?"). q7y (whether the assigned authority ever asked
##the respondent) is dropped. No survey weight in the deposit.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(file.path(raw, "data1.dta")))
stopifnot(nrow(x) == 1536L)
lab <- function(v, na = character()) { r <- trimws(as.character(as_factor(v, levels = "labels"))); r[r %in% na] <- NA; r }
num <- function(v) as.integer(zap_labels(v))
d <- data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L)
r4 <- function(v, ok = 1:4) { z <- num(v); z[!(z %in% ok)] <- NA; z }
d[, rating := r4(x$q1y)]
d[, rating_leader_sanction := r4(x$q4y)]
d[, rating_community_sanction := r4(x$q5y)]
d[, rating_enjoy := r4(x$q6y)]
d[, rating_authority_support := r4(x$q3y, 1:2)]
at <- c(activity = "Activity", authority = "Authority", ethnicity = "CoEthnic", partisanship = "Partisanship",
        sanctioning_leader = "SanctioningLeader", sanctioning_community = "SanctioningCommunity",
        social_benefit = "SocialBenefit", payment = "Payment", origin = "Origin", residence = "Residence", gender = "Gender")
for (v in names(at)) d[, paste0("attr_", v) := lab(x[[at[[v]]]])]
d[, `:=`(cov_age = num(x$demo_q3),
         cov_gender = c("male", "female")[match(num(x$demo_q4), 1:2)],
         cov_urban = lab(x$demo_q12, "Don't Know/Refuse to Answer"),
         cov_education = lab(x$demo_q26, "Refuse to Answer"),
         cov_income_situation = lab(x$demo_q30, "Don't Know/Refuse to Answer"),
         cov_ethnicity = lab(x$PD_q2, "Don't Know/Refuse to Answer"),
         cov_vote_intention = lab(x$q36, c("Refuse to Answer", "Refuse to Answe")),
         cov_ever_participated = lab(x$q8y, "Refused to answer"))]
d[!(cov_age %between% c(16L, 110L)), cov_age := NA]
miss <- d[, Reduce(`|`, lapply(.SD, is.na)), .SDcols = patterns("^attr_")]
stopifnot(sum(miss) == 6L)
d <- d[!miss]
d <- d[!(is.na(rating) & is.na(rating_leader_sanction) & is.na(rating_community_sanction) & is.na(rating_enjoy) & is.na(rating_authority_support))]
d[, id := seq_len(.N)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "jost_2024_zambia_participation.csv"))
