##Presidential policy-vignette experiment, wave 1 (president x topic x way of pursuing the policy) from
##Goehring, B., & Lowande, K. (2024). Public responses to unilateral policymaking. Journal of Experimental Political Science.
##https://doi.org/10.1017/xps.2024.3
##Replication data: Harvard Dataverse doi:10.7910/DVN/VXH3BK, CC0 1.0. Files read: jeps-replication-files/input-data/complete-data-v3.Rda
##(saved locally as d.Rda; data frame `dt`), README.txt, jeps-replication-1.R (r1.R; text, not run).
##Usage: Rscript goehring_2024.R <dir holding d.Rda> <output dir>
##
##4,350 US adult citizens (Lucid panel, fielded 7-9 Sept 2020), one wave-1 vignette each, 2 x 3 x 15 between-subject, fully crossed,
##near-equal cells (president x topic 119-162; topic x condition 72-131):
##  attr_president: President Obama / President Trump (the vignette's actor).
##  attr_action (condition.w1): "position" = the president's stated position only; "congress" = "He endorsed a bill and worked with
##    Congress."; "order" = "He acted alone by signing an executive order." The first and the sentence stems of the other two are
##    taken from the published article's endangered-species example (the article states the wording only for that topic); the position-only
##    level is a PARAPHRASE ("Position only: supported the policy; no action described").
##  attr_topic (topic.w1): 15 policy topics (carbon emissions, contractor pay, farm payments, foreign aid and abortion, foreign workers,
##    gun violence research, LGBT, policing and military surplus, public lands, Russian sanctions, student loans, trade, water rules,
##    weapon sales to Saudi Arabia, wildlife). The deposit stores only these short tags and the full per-topic vignette text is in the paper's
##    SI (not retrievable here): LABELS: tags only for attr_topic. Whether the president strengthened or weakened the policy
##    (Obama: strengthen, Trump: weaken, per the article's example) is built into the text and not a separate column.
##Wave 2 (a second vignette about whether the action succeeded or failed, ~1,970 recontacted respondents, condition.w2/outcome) is NOT built:
##it is a follow-up on the same topic with an added win/fail attribute (a different attribute set).
##Outcomes (7-point, levels from the stored factor order 1 = Strongly disapprove ... 7 = Strongly approve; higher = more approval;
##exact question wording is only described in the article):
##  rating_topic_handling   topic.approve.w1: assessment of the president's handling of the policy topic (paraphrase)
##  rating_president_approval  pres.approve.w1: overall approval of the president (paraphrase)
##One respondent with neither outcome is omitted (4,349 kept of 4,350). No opt-out. Dropped: vote intention/turnout (categorical, not a profile rating) and the derived binaries, the manipulation checks
##(manip.*), the second wave, attention-check/flag columns (the authors analyse all 4,350), recontact variables.
##Covariates: cov_gender (sex), cov_age, cov_education (text), cov_income (text band), cov_race (ethnicity, text), cov_hispanic (0/1),
##cov_region, cov_party_id (partisanship: Independent / Democrat / Republican; 3 categories as stored), cov_duration_sec (duration.w1, the wave-1 survey).
##PII FOUND and dropped: ip.address (both waves), lat/long (both waves), zip, respondent/Qualtrics IDs (rid.*, qualtrics.rid.*), start/end timestamps.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "d.Rda"), e); d <- as.data.table(e$dt)
stopifnot(nrow(d) == 4350, !anyNA(d$condition.w1), !anyNA(d$topic.w1), !anyNA(d$president.w1))
ch <- function(x) as.character(x)
act <- c(position = "Position only: supported the policy; no action described", congress = "He endorsed a bill and worked with Congress.",
         order = "He acted alone by signing an executive order.")
r <- d[, .(id = .I, task = 1L, profile = 1L,
  rating_topic_handling = as.integer(topic.approve.w1), rating_president_approval = as.integer(pres.approve.w1),
  attr_president = paste("President", ch(president.w1)), attr_action = act[ch(condition.w1)], attr_topic = ch(topic.w1),
  cov_gender = tolower(ch(sex)), cov_age = as.integer(age), cov_education = ch(education), cov_income = sub("^[0-9]+: ", "", ch(income)),
  cov_race = ch(ethnicity), cov_hispanic = as.integer(hispanic), cov_region = ch(region), cov_party_id = ch(partisanship),
  cov_duration_sec = as.integer(duration.w1))]
r <- r[!(is.na(rating_topic_handling) & is.na(rating_president_approval))]
stopifnot(nrow(r) == 4349, all(r$rating_topic_handling %in% c(1:7, NA)), all(r$rating_president_approval %in% c(1:7, NA)))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "goehring_2024_unilateral_policy.csv"))
