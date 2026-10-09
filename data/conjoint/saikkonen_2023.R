##Prime-minister conjoint on elite transgressions of democratic norms (Finland) from
##Saikkonen, I. A.-L., & Christensen, H. S. (2023). Guardians of democracy or passive bystanders?
##A conjoint experiment on elite transgressions of democratic norms. Political Research Quarterly,
##76(1), 127-142. https://doi.org/10.1177/10659129211073592
##The same experiment is re-analysed in the authors' "Lure of populism" files (same OSF project).
##Replication data: OSF project "Elite transgressions", https://osf.io/3f49x/ (doi 10.17605/OSF.IO/3F49X),
##node licence CC BY 4.0, no other terms in the files.
##Files read: "Replication data Guardians of democracy.dta" (OSF dg7tz, saved as guardians.dta) and
##"Replication data Lure of populism.dta" (OSF skrnw, saved as populism.dta; same 12,360 rows,
##merged on respid x comp x profile, attributes/choice identical in both: checked); the two
##do-files read as text. Level text: the article's Table 1 (English; the Finnish text shown is not
##deposited), mapped from the .dta value labels (male/female, low/intermediate/high, left/centre/right,
##should/must not be respected, condemns/does not condemn/incites, ordinary citizens/compromise
##political elites/compromise social groups, reduce/status quo/increase).
##Usage: Rscript saikkonen_2023.R <dir holding guardians.dta and populism.dta> <output dir>
##
##1,030 Finnish adults (Qualtrics online panel, 27 May-1 Jun 2020, representative on age, gender,
##region), 6 tasks (comp) of 2 profiles (profile) presented as prospective prime ministers,
##7 attributes. Article: "no restrictions were added to the randomization". Attribute order and
##level probabilities not documented. The article reports n = 1,030 (matches).
##Outcomes (one experiment, one table):
##  choice: respondents "were asked to pick the profile they would prefer as prime minister of
##    Finland" (article p.5; paraphrase, Finnish wording not deposited); exactly one per task.
##  choice_vote: follow-up "whether people would also vote for the leader selected" (article p.5,
##    used as a robustness check; `wouldvote` = 1 only on the chosen profile when Yes; opt-out:
##    a respondent can decline to vote for the chosen leader).
##Covariates: cov_gender (gendr: Female -> female, Male -> male), cov_age_group (ageclass; blank ->
##NA), cov_region (region_4: S/W/Hel/NE as stored), cov_province (region_18), cov_satsfdem,
##cov_trustparl, cov_trustparty, cov_trustgov, cov_trustpolit (0-10 as stored), cov_leftright
##(leftrightideol, 0-10, 10 = right), cov_attitude_immiwork, cov_attitude_asylum (Finnish label text
##as stored, double-encoded UTF-8 repaired), cov_demideal_1..6 (q1_1..q1_6, the authors' English
##labels). Dropped: municipality (re-identification risk), the source row id, unlabelled
##`immigration` (0-10, wording unknown), educ3 (codes without labels), the authors' recodes
##(exteff1-3 recoded in the do-file, *_3cat, *congru, indices, generation, polint 2-cat, _est_*).
##No survey weight (article: no weighting; none in the deposit).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
g <- as.data.table(as_factor(read_dta(file.path(raw, "guardians.dta"))))
p <- as.data.table(as_factor(read_dta(file.path(raw, "populism.dta"))))
stopifnot(nrow(g) == 12360L, uniqueN(g$respid) == 1030L, g[, .N, respid][, all(N == 12)])
m <- merge(g, p[, .(respid, comp, profile, gendr, ageclass, region_4, region_18,
                    p_choice = choice, p_judic = attjudic, p_popul = attpopul, p_immi = attimmi)],
           by = c("respid", "comp", "profile"))
stopifnot(nrow(m) == 12360L, all(m$choice == m$p_choice), all(as.character(m$attjudic) == as.character(m$p_judic)),
          all(as.character(m$attpopul) == as.character(m$p_popul)), all(as.character(m$attimmi) == as.character(m$p_immi)))
lab <- list(
  attviol = c("condemns" = "Condemns physical attacks against opposition candidates",
              "does not condemn" = "Does not condemn physical attacks on opposition candidates",
              "incites" = "Incites physical attacks against opposition candidates"),
  attjudic = c("should be respected" = "Must be respected even if they may have a negative effect on policies advanced by his/her party",
               "must not be respected" = "Do not have to be respected if they may have a negative effect on policies advanced by his/her party"),
  attideol = c(left = "Leftist", centre = "Centrist", right = "Rightist"),
  attimmi = c(reduce = "Reduce number of immigrants", "status quo" = "Maintain number of immigrants at current level",
              increase = "Increase number of immigrants"),
  attgender = c(female = "Female", male = "Male"),
  atteduc = c(low = "Low", intermediate = "Intermediate", high = "High"),
  attpopul = c("ordinary citizens" = "Demands of ordinary citizens", "compromise political elites" = "Compromises between political elites",
               "compromise social groups" = "Compromises between relevant social groups"))
nm <- c(attviol = "violence", attjudic = "judicial_decisions", attideol = "ideology", attimmi = "immigration",
        attgender = "gender", atteduc = "education", attpopul = "decisions_reflect")
fixenc <- function(x) { x <- as.character(x); y <- iconv(x, "UTF-8", "latin1"); Encoding(y) <- "UTF-8"; ifelse(is.na(y), x, y) }
d <- m[, .(id = as.integer(respid), task = as.integer(comp), profile = as.integer(as.character(profile)),
           choice = as.integer(as.character(choice)), choice_vote = as.integer(as.character(wouldvote)))]
stopifnot(all(d$choice == as.integer(as.integer(as.character(m$conjointchoice)) == d$profile)))
for (v in names(lab)) { x <- lab[[v]][as.character(m[[v]])]; stopifnot(!anyNA(x)); d[, paste0("attr_", nm[[v]]) := unname(x)] }
d[, `:=`(cov_gender = c(Female = "female", Male = "male")[as.character(m$gendr)],
         cov_age_group = fifelse(m$ageclass == "", NA_character_, as.character(m$ageclass)),
         cov_region = as.character(m$region_4), cov_province = fixenc(m$region_18),
         cov_satsfdem = as.integer(m$satsfdem), cov_trustparl = as.integer(m$trustparl), cov_trustparty = as.integer(m$trustparty),
         cov_trustgov = as.integer(m$trustgov), cov_trustpolit = as.integer(m$trustpolit), cov_leftright = as.integer(m$leftrightideol),
         cov_attitude_immiwork = fixenc(m$attitude_immiwork), cov_attitude_asylum = fixenc(m$attitude_asylum))]
for (k in 1:6) d[, paste0("cov_demideal_", k) := as.character(m[[paste0("q1_", k)]])]
stopifnot(!anyNA(d$cov_gender), d[, .(sum(choice), sum(choice_vote), sum(choice_vote * (1 - choice)), .N), .(id, task)][, all(V1 == 1 & V2 <= 1 & V3 == 0 & N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "saikkonen_2023_elite_transgressions.csv"))
