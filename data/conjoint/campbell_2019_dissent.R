##MP-choice conjoints on legislator dissent (UK, Studies 2 and 3) from
##Campbell, R., Cowley, P., Vivyan, N., & Wagner, M. (2019). Legislator dissent as a valence
##signal. British Journal of Political Science, 49(1), 105-128.
##https://doi.org/10.1017/S0007123416000223 (online 2016)
##Replication data: Harvard Dataverse doi:10.7910/DVN/3YCVOF, CC0 1.0, no restricted files,
##no terms. Files read: study2data.rds, study3data.rds (long data frames, one row per
##respondent x task x MP). Not built: study1data.rds (observational survey), appendixAdata.rds
##(split-sample vignette, one attribute varied for one MP only: not a conjoint).
##Design facts and wording from the accepted manuscript (Durham Research Online 18391, read via
##the Internet Archive): Study 2 section pp. 19-21, Study 3 section pp. 25-26, footnotes 62, 72,
##73, Figure 1 (screenshot of a Study 2 task); the authors' replication code was read as text.
##Usage: Rscript campbell_2019_dissent.R <raw dir> <output dir>
##
##Two experiments, two tables (different attribute sets and fieldings; the article analyses
##them separately):
##campbell_2019_dissent_frequency (Study 2): YouGov, 5-6 December 2012, 1,899 British voters.
##  Intro: "In the next few questions, we will ask you to compare two example MPs. We will call
##  them MP 1 and MP 2. For each pair of MPs, please say which one you would personally prefer to
##  have as your MP in the House of Commons." Each MP shown as (Figure 1, levels in bold):
##  "MP 1 has been a <party> MP for <tenure>" / "<He|She> spends on average <5-n> day(s) of a
##  5-day week reviewing and working on national policies in Parliament, and" / "The remaining
##  <n> day(s) working on local constituency issues." / "<He|She> <dissent> speaks out or votes
##  against <his|her> party leadership."
##  attr_ text = the bold level: attr_party Conservative/Labour; attr_tenure "3 years"/"10
##  years"/"21 years" (mp.tenure); attr_constituency_days "1 day".."4 days" (mp.const, the
##  constituency days: the authors' labels "MP constituency work (baseline = 1 day)"; the
##  parliament days are 5 minus this and are not stored separately); attr_dissent
##  never/rarely/sometimes/often (mp.rebellion); attr_gender He/She (the pronoun is the only sex
##  cue; mp.sex female -> "She", male -> "He").
##  choice: "Based on this information, which ONE of these two MPs would you prefer to have as
##  your MP in the House of Commons?" MP 1 / MP 2, a response was required (fn 62): no opt-out.
##campbell_2019_dissent_type (Study 3): YouGov, 24-25 September 2013, 1,919 British voters.
##  Same format; attributes party (Conservative/Labour), constituency days (1-4, as above), sex
##  (data stores the pronoun She/He), and two new ones (article pp. 25-26): motivation, "when
##  considering policy matters" the MP mainly thinks about "own personal views" or
##  "constituents' views" (mp.views personal/constituents; the stored text follows the article
##  and the authors' plot labels; the exact sentence is not reproduced in the article); type of
##  dissent when these "views on policy differ from those of the party leadership":
##  "nevertheless tends not to speak out" / "tends to speak out at internal party meetings, but
##  not publicly" / "tends to speak out at internal party meetings and also publicly" (mp.dissent
##  tends not to / internal only / internal and external, mapped to the article's quoted text).
##  No tenure attribute. choice: as Study 2 without "in the House of Commons" (fn 73); no
##  opt-out.
##Randomization: "completely independent randomization, such that all possible combinations of
##  attribute values were equally likely in expectation" (p. 20, Study 2; Study 3 has "a similar
##  format"). Attribute order fixed (fn 72 gives the bullet position of the dissent attribute
##  in each study; Figure 1).
##task = choicetask ("Choice task 1".."5", recorded). profile is INFERRED: the source has no
##  MP 1/MP 2 column; profile = order of appearance of the two rows of a task in the file
##  (Study 2 rows are interleaved across respondents, so this order may not be the screen
##  position). Every task has exactly two rows and exactly one chosen MP (checked).
##Covariates (deposited factors as text): cov_gender (profile.gender, YouGov profile sex,
##  "Female\n"/"Male\n" -> female/male), cov_age_group (Study 2 age.group3 band text),
##  cov_age_left_education (Study 2 educ, as deposited), cov_qual_code (qual 1-4, the deposit
##  carries no labels for it), cov_income_group (Study 2), cov_social_grade, cov_region,
##  cov_follow_politics (Study 2), cov_pid_strength (Study 2 pid.strength, the authors' party
##  id x strength text), cov_lr_self_group (Study 2 lr.self.group3, authors' grouping),
##  cov_party_group (Study 3 pid, the authors' four-way party id grouping), cov_efficacy_external,
##  cov_efficacy_internal (Study 3 raw 5-point answers), cov_newspaper (Study 3 qpaper),
##  cov_survey_weight (w8, YouGov weight).
##Dropped: the authors' respondent-x-MP derived variables (same.party, mp.congstr,
##  pidstrength.mpparty, mpparty.lrgroup3, rightofcon, leftoflab, mp.copartisan, mp.cong3) and
##  collapsed recodes (effic.ext/effic.int, paper).
##N: 1,899 x 10 = 18,990 rows (Study 2) and 1,919 x 10 = 19,190 rows (Study 3) match the article.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
gnd <- function(x) c("Female\n" = "female", "Male\n" = "male")[as.character(x)]
prep <- function(s) {
  s[, task := as.integer(sub("Choice task ", "", as.character(choicetask)))]
  s[, profile := seq_len(.N), .(id, task)]
  stopifnot(s[, .N, .(id, task)][, all(N == 2)], s[, sum(mp.preferred), .(id, task)][, all(V1 == 1)],
            s[, uniqueN(task), id][, all(V1 == 5)], !anyNA(s$mp.preferred))
  s
}
## Study 2
s <- prep(as.data.table(readRDS(file.path(raw, "study2data.rds"))))
stopifnot(uniqueN(s$id) == 1899)
d2 <- s[, .(id = as.integer(id), task, profile, choice = as.integer(mp.preferred),
            attr_party = as.character(mp.party),
            attr_tenure = paste(mp.tenure, "years"),
            attr_constituency_days = paste(mp.const, fifelse(mp.const == 1L, "day", "days")),
            attr_dissent = as.character(mp.rebellion),
            attr_gender = c(female = "She", male = "He")[as.character(mp.sex)],
            cov_gender = gnd(profile.gender), cov_age_group = as.character(age.group3),
            cov_age_left_education = as.character(educ), cov_qual_code = as.integer(as.character(qual)),
            cov_income_group = as.character(income), cov_social_grade = as.character(social.grade),
            cov_region = as.character(region), cov_follow_politics = as.character(follow.pol),
            cov_pid_strength = as.character(pid.strength), cov_lr_self_group = as.character(lr.self.group3),
            cov_survey_weight = w8)]
stopifnot(!anyNA(d2[, .SD, .SDcols = patterns("^attr_")]), !anyNA(d2$cov_gender))
setorder(d2, id, task, profile)
fwrite(d2, file.path(out, "campbell_2019_dissent_frequency.csv"))
## Study 3
s <- prep(as.data.table(readRDS(file.path(raw, "study3data.rds"))))
stopifnot(uniqueN(s$id) == 1919)
dis <- c("tends not to" = "nevertheless tends not to speak out",
         "internal only" = "tends to speak out at internal party meetings, but not publicly",
         "internal and external" = "tends to speak out at internal party meetings and also publicly")
d3 <- s[, .(id = as.integer(id), task, profile, choice = as.integer(mp.preferred),
            attr_party = as.character(mp.party),
            attr_constituency_days = paste(mp.const, fifelse(mp.const == 1L, "day", "days")),
            attr_motivation = c(personal = "own personal views", constituents = "constituents' views")[as.character(mp.views)],
            attr_dissent_type = dis[as.character(mp.dissent)],
            attr_gender = as.character(mp.sex),
            cov_gender = gnd(profile.gender), cov_qual_code = as.integer(as.character(qual)),
            cov_social_grade = as.character(social.grade), cov_region = as.character(region),
            cov_party_group = as.character(pid), cov_efficacy_external = as.character(effic.ext.raw),
            cov_efficacy_internal = as.character(effic.int.raw), cov_newspaper = as.character(qpaper),
            cov_survey_weight = w8)]
stopifnot(!anyNA(d3[, .SD, .SDcols = patterns("^attr_")]), !anyNA(d3$cov_gender))
setorder(d3, id, task, profile)
fwrite(d3, file.path(out, "campbell_2019_dissent_type.csv"))
