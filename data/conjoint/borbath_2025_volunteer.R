##Mobilizing-actor vignette experiment (Study 3) from
##Borbath, E., & Hutter, S. (2025). Mobilizing individuals in crisis: The role of civil society organizations in
##volunteer engagement during COVID-19. Journal of Civil Society, 21(4). https://doi.org/10.1080/17448689.2025.2530108
##Replication data: Harvard Dataverse doi:10.7910/DVN/0D9OFW, CC0 1.0. File read: study3_experiment.RData (object
##orig_dat, long format), study3_by_cntry.Rmd (analysis code, read as text); vignette template from the article
##(econstor.eu OA copy) Study 3 section. The deposit's Study 1 and 2 files are observational and not used.
##Usage: Rscript borbath_2025_volunteer.R <dir holding study3_experiment.RData saved as s3.RData> <output dir>
##
##2,798 respondents (Germany 1,000, Italy 898, Poland 900; March 2021 online panel), each answering twice, after two
##randomly selected vignettes (time = 1, 2 is the task order). Vignette (article): "Members of a local civil society
##organization (MOBILIZING ACTOR) feel angry (EMOTION) because of the difficult situation of older people
##(RECIPIENT) in the Corona crisis. To help them, the group is asking for your support." Attributes (levels; the
##deposit stores codes with English variable labels only, the vignette wording by country is not deposited):
##  mobilizing_actor (org): "our friends and acquaintances" / "members of a local aid organization" / "members of
##    a national aid organization" / "representatives of the local administration" (article wording, Study 3)
##  recipient (group_in_need): older people / people in financial difficulties (data labels "old people", "those
##    with financial difficulties"; template says "older people")
##  emotion (emo_displ): anger, fear, sadness, guilt, hope, neutral (data value labels; paraphrased/tags -- only
##    "angry" is quoted in the article). Convergence (emo_convergence) is the authors' randomized treatment:
##    the displayed emotion equals (1) or differs from (2) the respondent's own pre-measured emotion (own_emo), so
##    the displayed-emotion mix is not uniform (guilt 4%, sadness 32%). The match flag is a derived task detail, kept
##    as trial_emotion_matches_own; the respondent's own emotion as cov_own_emotion.
##LABELS: partly tags (emotion; recipient), actor wording from the article text.
##Outcomes (no opt-out): rating = volunteering_DV, "How likely is it that you would volunteer in support of this
##group?", 0 (extremely unlikely) to 10 (extremely likely) (article). rating_donation = donation_DV, "How likely is it
##that you would donate money to support ...?" (variable label; wording by country not deposited), stored 1-11,
##1 = very unlikely, 11 = very likely (value labels), raw. The *_source columns (target group) duplicate
##group_in_need and are dropped.
##Pooled across the three countries with cov_country as the authors do (country fixed effects). Respondent id is
##re-keyed over (country, id). Covariates: cov_country, cov_age (years), cov_gender_code (gndr, 1/2 unlabelled in the
##file), cov_own_emotion (own_emo labels). Dropped: p_0001 URL parameter, lfdn, c_0001 pseudonym, session_id,
##referer/browser/device, e-mail fields, timestamps, quota fields, rts* timing columns and all other survey
##items (PII-like fields dropped: URL parameter, session id, pseudonym, email source). No weights in this file.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "s3.RData"), envir = e); d <- as.data.table(e$orig_dat)
stopifnot(nrow(d) == 5596)
d[, key := paste(cntry, id)]
d[, rid := match(key, unique(key))]
lb <- function(x) { l <- attributes(x)$labels; names(l)[match(as.numeric(x), l)] }
actor <- c("our friends and acquaintances", "members of a local aid organization", "members of a national aid organization", "representatives of the local administration")
recip <- c("older people", "people in financial difficulties")
r <- d[, .(id = rid, task = as.integer(as.character(time)), profile = 1L, rating = as.integer(volunteering_DV), rating_donation = as.integer(donation_DV),
  attr_mobilizing_actor = actor[as.integer(as.character(org))], attr_recipient = recip[as.integer(as.character(group_in_need))],
  attr_emotion = lb(emo_displ),
  trial_emotion_matches_own = c("matches respondent's own emotion", "differs from respondent's own emotion")[as.integer(as.character(emo_convergence))],
  cov_country = as.character(cntry), cov_age = as.integer(age), cov_gender_code = as.integer(as.character(gndr)),
  cov_own_emotion = lb(own_emo))]
stopifnot(!anyNA(r[, .(rating, rating_donation, attr_mobilizing_actor, attr_recipient, attr_emotion)]), r[, .N, by = id][, all(N == 2)])
setorder(r, id, task, profile)
fwrite(r, file.path(out, "borbath_2025_volunteer_mobilization.csv"))
