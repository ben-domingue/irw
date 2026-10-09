##Survey-participation factorial vignette (Qatar) from
##Gengler, J. J., Tessler, M., Lucas, R., & Forney, J. (2021). 'Why do you ask?' The nature and impacts
##of attitudes towards public opinion surveys in the Arab World. British Journal of Political Science,
##51(1), 115-136. https://doi.org/10.1017/S0007123419000206
##Replication data: Harvard Dataverse doi:10.7910/DVN/QBPIVL, CC0 1.0, no restricted files.
##Files read: attitudes-replication-anon.tab (original Stata 14 file, saved as anon.dta: one row per
##respondent, raw answer codes with value labels), "Survey Attitudes in the Arab World - Questionnaire
##(English).pdf", readme.txt. Read as text, not run: attitudes-replication-code-conjoint.do,
##"conjoint R replication code.txt". The authors' long file attitudes-replication-conjoint-for-R.dta is
##NOT used: it already reverses the outcome, has no missing outcomes, and repeats 10 caseids.
##Usage: Rscript gengler_2021.R <raw dir> <output dir>
##
##1,685 interviewer-administered respondents in Qatar (Qatari citizens and resident expatriates;
##SESRI, Qatar University). Three vignettes per respondent (Q17-Q19), one profile each; task = 1-3
##in the order asked (sponsor1..3 etc.). Q17: "Now I am going to describe a hypothetical survey that
##someone like you might be asked to participate in. Please tell me how likely you would be to agree
##to participate in such a survey if you were asked. Imagine that the survey was being conducted by
##{SPONSOR} and would take place {MODE}. It would last about {TIMING} and cover important {TOPIC}
##issues facing the country. How likely would you be to participate in such a survey? Would you be
##very likely, somewhat likely, somewhat unlikely, or very unlikely to agree to take part?" Q18 and
##Q19 repeat it ("Now imagine that you were asked to participate in a different survey ..." /
##"Finally, imagine ... another survey ...").
##Attributes, level text from the questionnaire's programming note (sponsor, mode: the codes follow
##its numbered order, as in the authors' R recode University/Government/Company/International Org.
##and Face-to-face/Telephone) and the .dta value labels (timing, topic):
##  attr_sponsor  1 "A university in Qatar", 2 "A Qatari state institution", 3 "A private company in
##                Qatar", 4 "An international agency"
##  attr_mode     1 "in person at your home", 2 "by telephone"
##  attr_timing   1 "about 60 minutes", 2 "about 30 minutes" (in person only), 3 "about 10 minutes",
##                4 "about 20 minutes" (telephone only)  -- RESTRICTION: timing levels depend on mode
##  attr_topic    1 "cultural", 2 "economic", 3 "political"
##Outcome: rating = surveyvig1-3, stored as answered: 1 Very likely, 2 Somewhat likely, 3 Somewhat
##unlikely, 4 Very unlikely (LOWER = more willing; the authors reverse it). Don't know / refused
##(missing in the file: 10, 10 and 9 vignettes) are omitted.
##Covariates: cov_survey_weight (wgt), cov_gender (female 1 = female, 0 = male; interviewer-recorded,
##Q1), cov_age (respage, years, as recorded), cov_education (respeduc value-label text: No formal
##education / Primary or below / Secondary diploma / Vocational diploma / University), cov_region5 and
##cov_region3 (value-label text: origin group Qatar / Arab / West / South Asia / SE Asia / Other; Qatar
##/ Arab / Non-Arab), cov_household (Qatari / Non-Qatari household, value labels), cov_strat
##(sampling stratum code, no labels). No PII in the file.
##N: 1,685 interviewed, 1,680 with at least one answered vignette, 5,026 vignettes (the same row count
##as the authors' long R file); the authors' conjoint models drop respondents with no region3 (157)
##and are weighted by wgt. Paper's N not checked (article not accessible).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "anon.dta"))
stopifnot(nrow(s) == 1685L, !anyDuplicated(s$caseid))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
sp <- c("A university in Qatar", "A Qatari state institution", "A private company in Qatar", "An international agency")
md <- c("in person at your home", "by telephone")
tm <- c("about 60 minutes", "about 30 minutes", "about 10 minutes", "about 20 minutes")
tp <- c("cultural", "economic", "political")
stopifnot(identical(unname(attr(s$timing1, "labels")[3:6]), 1:4 + 0), grepl("60 minutes", names(attr(s$timing1, "labels"))[3]),
          grepl("cultural", names(attr(s$topic1, "labels"))[3]), grepl("Very likely", names(attr(s$surveyvig1, "labels"))[3]))
s$id <- seq_len(nrow(s))
L <- lapply(1:3, function(t) {
  g <- function(v) as.integer(zap_labels(s[[paste0(v, t)]]))
  data.table(id = s$id, task = t, profile = 1L, rating = g("surveyvig"),
             attr_sponsor = sp[g("sponsor")], attr_mode = md[g("mode")], attr_timing = tm[g("timing")], attr_topic = tp[g("topic")])
})
d <- rbindlist(L)[!is.na(rating)]
stopifnot(d$rating %in% 1:4, !anyNA(d),
          d[attr_mode == md[1], all(attr_timing %in% tm[1:2])], d[attr_mode == md[2], all(attr_timing %in% tm[3:4])])
cv <- data.table(id = s$id, cov_survey_weight = as.numeric(s$wgt),
                 cov_gender = ifelse(zap_labels(s$female) == 1, "female", "male"),
                 cov_age = as.integer(zap_labels(s$respage)), cov_education = lab(s$respeduc),
                 cov_region5 = lab(s$region5), cov_region3 = lab(s$region3), cov_household = lab(s$household),
                 cov_strat = as.integer(zap_labels(s$strat)))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gengler_2021_survey_participation.csv"))
