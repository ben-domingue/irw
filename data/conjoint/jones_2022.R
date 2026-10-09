##Gay-teacher news-story factorial vignette (Study 2) from
##Jones, P. E. (2022). Respectability politics and straight support for LGB rights.
##Political Research Quarterly, 75(4), 935-949. https://doi.org/10.1177/10659129211035834
##Replication data: Harvard Dataverse doi:10.7910/DVN/4RGSWB, CC0 1.0. File read:
##RespectabilityPolitics_Study2.RData (data.frame Study2.s, loaded into its own environment).
##codebook.pdf and the author's Online Appendix (pejones.org, A2.2 stimuli, A3.2 wording) were read.
##Usage: Rscript jones_2022.R <dir holding the .RData> <output dir>
##
##Study 2 only: 3,541 straight respondents from a Qualtrics opt-in panel (four
##cross-sectional surveys, Dec 2019 - May 2020, pooled by the author; the wave is not in the
##deposit). Each respondent read ONE fictitious news story ("School sued for firing gay
##teacher"), so task = 1 and profile = 1. Study 1 (CCES, n = 880) manipulates a single
##factor (two- vs three-person relationship) and is not a conjoint: not built.
##Full factorial design, six factors randomized (appendix A2.2: gender first, then the other
##five within gender; all 2x2x2x3x3x3 cells occur). Levels are stored as the AUTHOR'S labels
##(the deposit's factor levels), not the story text. The displayed template (appendix A2.2):
##  "A local [elementary/middle/high] school teacher was fired after administrators learned
##  about her [girlfriend/girlfriends] ... [Katelyn McGrath/Mariana Hernandez/Tanisha
##  Washington], 33, ... She has been in [a committed/an open] relationship with [another
##  woman/two other women] for [three/six/ten] years. ... part of [a/an open] same-sex
##  [couple/threesome]" ; male version: his/boyfriend(s), Jake McGrath/Alejandro Hernandez/
##  Tyrone Washington, another man/two other men.
##So attr_gender (Female/Male teacher) was shown through first name and pronouns, attr_race
##(White/Black/Latinx teacher) through the name (McGrath/Washington/Hernandez).
##Outcomes (appendix A3.2; the deposit stores each recoded by the author to 0-1, higher = more
##support for the teacher / LGB rights; kept as deposited, not rescaled back):
##  rating: "If you were deciding this case, would you" Definitely side with the school (0),
##    Probably side with the school (1/3), Probably side with the gay teacher (2/3),
##    Definitely side with the gay teacher (1).
##  rating_similar: "How similar to you did you feel the people described in the news story
##    were? The gay teacher." slider "Not at all similar" (0) to "Extremely similar" (1);
##    stored as k/7, k = 0..7 (eight distinct values).
##  rating_lgb_jobs: "Do you support or oppose laws that would protect lesbian, gay, and
##    bisexual people against job discrimination?" Strongly oppose (0) .. Strongly support (1),
##    4 points. A general policy question asked after the story (the author analyses it as an
##    outcome of the experiment), not a judgement of the teacher.
##Dropped: lgb.rights (author's average of three items, a derived index), lgb (all 0: the
##deposit holds straight respondents only), ResponseId (Qualtrics id; re-keyed to 1..N in file
##order). The emotion and sympathy items in the appendix are not in the deposit.
##Covariates (author's 0-1 recodes, kept as deposited): cov_ideology (very liberal 0 ..
##very conservative 1), cov_pid7_01 (7-point party identity, Strong Democrat 0 .. Strong
##Republican 1; 103 NA). Paper p. 5 gives both directions. No survey weight (code comment:
##"unweighted Qualtrics data").
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "RespectabilityPolitics_Study2.RData"), envir = e)
s <- as.data.table(e$Study2.s)
stopifnot(nrow(s) == 3541, uniqueN(s$ResponseId) == 3541, all(s$lgb == 0))
d <- s[, .(id = seq_len(.N), task = 1L, profile = 1L,
           rating = case.outcome, rating_similar = similar.teacher, rating_lgb_jobs = lgb.jobs,
           attr_relationship_people = as.character(ex_poly), attr_relationship_type = as.character(ex_open),
           attr_gender = as.character(ex_gender), attr_race = as.character(ex_race),
           attr_school = as.character(ex_school), attr_relationship_length = as.character(ex_years),
           cov_ideology = ideo, cov_pid7_01 = pid7)]
stopifnot(!anyNA(d[, .(rating, rating_similar, rating_lgb_jobs)]),
          all(round(d$rating * 3, 6) %in% 0:3), all(round(d$rating_similar * 7, 6) %in% 0:7),
          all(round(d$rating_lgb_jobs * 3, 6) %in% 0:3))
stopifnot(nrow(unique(d[, .SD, .SDcols = patterns("^attr_")])) == 216)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "jones_2022_gay_teacher.csv"))
