##Corrupt-mayor conjoint (Spain) from
##Breitenstein, S. (2019). Choosing the crook: A conjoint experiment on voting for corrupt
##politicians. Research & Politics, 6(1). https://doi.org/10.1177/2053168019832230
##Replication data: Harvard Dataverse doi:10.7910/DVN/HOSWS7, CC0 1.0, no restricted files.
##File read: Choosing_crook.dta (Dataverse "original format" download). Level text and Spanish
##question text from the .dta (string attributes, variable and value labels); design facts from
##the article (open-access copy, ddd.uab.cat record 221014) and the authors' recode/analysis
##do-files (read as text, not run).
##Usage: Rscript breitenstein_2019.R <raw dir> <output dir>
##
##Online survey with population quotas, Spain, June 2016 (article: n = 2,275). Each respondent
##saw 3 pairs (task = source `round`) of candidates for mayor; profile = source `candidate`
##(1 = "García", 2 = "Martínez", the answer options of the choice question). Outcomes:
##  rating = source voteprobability, the article's main outcome: probability of voting for
##     each candidate if they ran in the respondent's town, 0 ("would never vote for") to 10
##     ("would definitely vote for"); source codes 1-11 stored as 0-10 (the authors rescale to
##     0-1).
##  choice = source selectr1/select2/selectrd3 (one per task): "Imagina que hay elecciones en tu
##     municipio. ¿Qué alcalde o alcaldesa preferir..." (variable label, truncated in the .dta),
##     options García / Martínez; forced choice, no opt-out.
##Attributes (Spanish level text as displayed, from the .dta; English in the article's
##Table 1): sex (Mujer/Hombre), party (PP, PSOE, Podemos, Ciudadanos), qualities, economic
##outcomes, corruption (honest / accused by the other parties / accused by a judge). The
##article: "completely randomized, so no combination of attributes was restricted"; attribute
##order randomized per respondent and fixed over the 3 tasks (order not in the data).
##trial_page_seconds = Qualtrics page-submit time of that task (timer1_3/timer2_3/timer3_3).
##The authors drop speeders' tasks (do-file: drop if timer1_3 < 15 | timer2_3 < 10 | timer3_3 < 9,
##row-wise, so a fast task is dropped, not the whole respondent); all tasks are kept here, and
##the rule can be applied with trial_page_seconds (< 15 / 10 / 9 for tasks 1 / 2 / 3).
##Covariates: cov_female (Mujer = 1), cov_age, cov_education, cov_party_id, cov_party_closeness,
##cov_employment, cov_income (Spanish label text); cov_ideology 0 (left) .. 10 (right), source
##1-11 minus 1, "No lo sé" (12) -> NA; cov_turnout_municipal 0 (Seguro que no votaría) .. 10
##(Seguro que votaría), source codes 1-10 -> 0-9 and 13 -> 10 per the value labels;
##cov_ptv_pp/psoe/podemos/ciudadanos (0-10 propensity to vote for each party in the municipal
##election); cov_satisfaction_democracy 0 (Nada) .. 10 (Completamente), source minus 1;
##cov_knowledge_1..3 (answer text of three political-knowledge items: who is pictured
##(Juncker correct), the acting employment minister (Fátima Báñez correct), what EU elections
##elect (MEPs correct)) and cov_knowledge_unemployment (estimated unemployment rate, %).
##Dropped: survey respondent id gid (re-keyed 1..2,248), the duplicate `gender`/`sex` codings
##kept once (cov_female from `gender`; `sex` is the candidate attribute), the authors' derived
##variables. 1 respondent has only 2 tasks; 1 pair has no choice; 2 profiles no rating.
##N: 2,248 respondents / 6,742 pairs in the deposit vs the article's 2,275 surveyed. Applying the
##speeder rule leaves 12,284 rated profiles, exactly the article's count (it says 6,142 pairs;
##6,143 here).
##Spot check (speeder rule applied, rating/10 on the five attributes, SEs clustered by id):
##accused by parties -0.23, accused by a judge -0.27 (article: -0.22, -0.27; its model codes
##party as co-partisanship); mean for honest candidates 0.49 (article 0.49).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "Choosing_crook.dta")))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
stopifnot(s[, .N, .(gid, round)][, all(N == 2)], all(s$candidate %in% 1:2))
sel <- with(s, fcoalesce(as.integer(selectr1), as.integer(select2), as.integer(selectrd3)))
d <- data.table(gid = s$gid, task = as.integer(s$round), profile = as.integer(s$candidate),
                choice = as.integer(sel == s$candidate), rating = as.integer(zap_labels(s$voteprobability)) - 1L,
                attr_sex = s$sex, attr_party = s$party, attr_qualities = s$qualities, attr_economic_performance = s$outcomes,
                attr_corruption = s$corruption,
                trial_page_seconds = fcase(s$round == 1, s$timer1_3, s$round == 2, s$timer2_3, s$round == 3, s$timer3_3))
stopifnot(d[!is.na(choice), sum(choice), .(gid, task)][, all(V1 == 1)], all(d$rating %in% c(0:10, NA)))
ideo <- as.integer(zap_labels(s$ideol)); ideo <- ifelse(ideo == 12L, NA_integer_, ideo - 1L)
tv <- as.integer(zap_labels(s$voteprob)); stopifnot(all(tv %in% c(1:10, 13L)))
d[, `:=`(cov_female = as.integer(zap_labels(s$gender) == 2), cov_age = as.integer(s$age), cov_education = lab(s$studies),
         cov_ideology = ideo, cov_party_id = lab(s$partyid), cov_party_closeness = lab(s$partyclose),
         cov_turnout_municipal = ifelse(tv == 13L, 10L, tv - 1L),
         cov_ptv_pp = as.integer(s$voteprob4_1), cov_ptv_psoe = as.integer(s$voteprob4_2),
         cov_ptv_podemos = as.integer(s$voteprob4_4), cov_ptv_ciudadanos = as.integer(s$voteprob4_5),
         cov_satisfaction_democracy = as.integer(zap_labels(s$satisfdemo)) - 1L,
         cov_knowledge_1 = lab(s$polsoph1), cov_knowledge_2 = lab(s$polsoph2), cov_knowledge_3 = lab(s$polsoph3),
         cov_knowledge_unemployment = as.numeric(s$polsoph4), cov_employment = lab(s$sitlab), cov_income = lab(s$income))]
d <- d[!(is.na(choice) & is.na(rating))]
d[, id := as.integer(factor(gid))][, gid := NULL]
setcolorder(d, c("id", "task", "profile"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "breitenstein_2019_corrupt_mayors.csv"))
