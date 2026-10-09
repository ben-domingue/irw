##Refugee-profile conjoint from
##Charnysh, V., Peisakhin, L., Stoop, N., & van der Windt, P. (2026). Understanding refugee
##assistance: Evidence on Syrian and Ukrainian refugees in Poland. Comparative Political
##Studies (online ahead of print). https://doi.org/10.1177/00104140261448441
##Replication data: Harvard Dataverse doi:10.7910/DVN/JYB2CH, CC0 1.0, no restricted files,
##no terms. File read: data_conjoint.dta (Dataverse "original format" download). Level text
##and outcome meaning from the .dta value/variable labels and the authors' Replication.do
##(read as text; coefplot labels); readme.rtf has no codebook. The questionnaire is not
##deposited.
##Usage: Rscript charnysh_2026.R <raw dir> <output dir>
##
##2,500 respondents, representative face-to-face survey of Polish adults (fall 2022; the
##abstract gives N = 2,500). Each saw 6 tasks of 2 hypothetical refugee profiles: 3 tasks
##about Syrian refugees and then 3 about Ukrainian refugees (the .dta's `conjoint` block
##variable is 0 = Syrian on rows 1-6 and 1 = Ukrainian on rows 7-12 for every respondent;
##whether the block order was fixed or the file is sorted is not documented). The block is
##kept as trial_refugee_origin (Syrian / Ukrainian); it is not randomized per profile.
##5 attributes, two levels each. Level text = the authors' English figure labels in
##Replication.do (coefplot coeflabels), which match the .dta value labels but are fuller
##(value label "Single young mother with child" vs figure "Single young mother of 32 years
##old with child"). The survey was in Polish; the Polish text is not deposited.
##  attr_family    Single young man of 32 years old / Single young mother of 32 years old with child
##  attr_economic  Well off. A programmer / Poor. A cleaner
##  attr_suffering Refugee / Refugee. Had relatives killed by Russia
##  attr_religion  Christian / Muslim
##  attr_skin      White skin, blond hair, blue eyes / Dark skin, black hair, black eyes
##(The .dta value labels carry a stray duplicate label on code 2 for each attribute; only codes
##0/1 occur.) The same suffering text is used for both blocks, as in the authors' labels.
##TASK AND PROFILE ARE INFERRED from row order: the .dta has no task or profile column. Rows
##come in 12 per respondent; consecutive rows (1-2, 3-4, ...) are the pairs. Checked: in all
##9,589 pairs with a recorded choice exactly one profile is chosen, the block is constant
##within each pair, and the authors' forced-choice coding (choice) agrees. Profile 1 = first
##row of the pair; which side it was shown on is not documented.
##Outcomes (wording from the .dta labels; the verbatim Polish questions are not deposited):
##  choice  = forced choice, the preferred refugee profile ("choice dummy excl. 88 & 99";
##            figure axis "preferred refugee profile"). Don't know / refusal are NA: 5,411 of
##            15,000 tasks have no choice. No opt-out option as such.
##  rating_willing = "willingness to host", 1 Strongly opposed to hosting this person,
##            2 Opposed to hosting this person, 3 Willing to host this person, 4 Strongly
##            willing to host this person (88/99 already NA in the file); asked of each profile.
##  rating_food  = "I would donate food or clothes to this individual", 1 Strongly disagree ..
##            5 Agree Strongly; asked only in the first task of each block (tasks 1 and 4).
##  rating_money = "I would donate money to this individual", same scale, tasks 1 and 4.
##  rating_need / rating_crime / rating_burden = 0/1 per profile, labels "is in great need",
##            "increase crime or terrorism", "burden: take our jobs and benefits" (no/yes);
##            tasks 1 and 4; both profiles can be 1, so they are ratings, not choices.
##All ratings are stored as in the source (higher = more willing / agree / yes).
##Covariates: cov_survey_weight = Q0_Weights ("Admin: Weights"; the paper's weighted models);
##cov_gender from Q1_Female (label "Respondent is female": 1 = female, 0 = male; 88/99 do not
##occur); cov_age = age_resp (years); cov_concern_russia = Q43_Concerned codes (1 Not at all
##concerned, 2 Not that concerned, 3 A little concerned, 4 Very concerned; 88/99 -> NA);
##cov_jobs_threat = Q51_Jobs codes (0 "Migrants do jobs that Poles are unwilling to take and
##migrants are not an economic threat", 1 "Migrants are making it more difficult for Poles to
##find jobs"; 88/99 -> NA). trial_treatment = the preceding survey experiment arm (treat1-5
##labels: Control, Suffering Syrians, Suffering Ukrainians, Suffering Syrians + shared
##experience, Suffering Ukrainians + shared experience); it is respondent-level, kept as trial_
##since it is part of the design the paper conditions on.
##Dropped: all *SD standardized copies, conjoint_reverse, derived dummies (higher_education,
##catholic, WW2, concern_job, good_econ_cont, empathyscore_mean: authors' derived scales).
##Rows with no outcome at all are omitted.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "data_conjoint.dta"))
z <- as.data.table(zap_labels(k))
stopifnot(z[, .N, id][, all(N == 12L)], all(z$conjoint %in% 0:1))
z[, r := seq_len(.N), id]
z[, `:=`(task = (r + 1L) %/% 2L, profile = 2L - r %% 2L)]
stopifnot(z[, uniqueN(conjoint), .(id, task)][, all(V1 == 1)],
          z[, all(conjoint == as.integer(task > 3))])
chk <- z[!is.na(choice), .(s = sum(choice), n = .N), .(id, task)]
stopifnot(all(chk$n == 2 & chk$s == 1))
lab <- function(v, l) { stopifnot(all(z[[v]] %in% 0:1)); l[z[[v]] + 1L] }
d <- data.table(id = as.integer(z$id), task = as.integer(z$task), profile = as.integer(z$profile),
  choice = as.integer(z$choice), rating_willing = as.integer(z$willing),
  rating_food = as.integer(z$food), rating_money = as.integer(z$money),
  rating_need = as.integer(z$need_d), rating_crime = as.integer(z$crime_d), rating_burden = as.integer(z$burden_d),
  attr_family = lab("family", c("Single young man of 32 years old", "Single young mother of 32 years old with child")),
  attr_economic = lab("economic", c("Well off. A programmer", "Poor. A cleaner")),
  attr_suffering = lab("suffering", c("Refugee", "Refugee. Had relatives killed by Russia")),
  attr_religion = lab("religion", c("Christian", "Muslim")),
  attr_skin = lab("skin", c("White skin, blond hair, blue eyes", "Dark skin, black hair, black eyes")),
  trial_refugee_origin = c("Syrian", "Ukrainian")[z$conjoint + 1L])
stopifnot(all(d$rating_willing %in% c(1:4, NA)), all(d$rating_food %in% c(1:5, NA)), all(d$rating_money %in% c(1:5, NA)))
tr <- as.matrix(z[, .(treat1, treat2, treat3, treat4, treat5)])
stopifnot(all(rowSums(tr) == 1))
d[, trial_treatment := c("Control", "Suffering Syrians", "Suffering Ukrainians", "Suffering Syrians + shared experience",
                         "Suffering Ukrainians + shared experience")[max.col(tr)]]
stopifnot(all(z$Q1_Female %in% 0:1))
d[, `:=`(cov_gender = c("male", "female")[z$Q1_Female + 1L], cov_age = as.integer(z$age_resp),
         cov_concern_russia = as.integer(ifelse(z$Q43_Concerned %in% 1:4, z$Q43_Concerned, NA)),
         cov_jobs_threat = as.integer(ifelse(z$Q51_Jobs %in% 0:1, z$Q51_Jobs, NA)),
         cov_survey_weight = as.numeric(z$Q0_Weights))]
oc <- grep("^(choice|rating)", names(d), value = TRUE)
d <- d[rowSums(!is.na(d[, ..oc])) > 0]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "charnysh_2026_refugee_assistance.csv"))
