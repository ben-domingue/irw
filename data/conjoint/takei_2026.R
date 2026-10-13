##Audience-cost vignette experiment with American respondents evaluating an adversary leader's threat, from
##Takei, M., Moon, C., & Imada, H. (2026). Audience costs in the eyes of an adversary. Research & Politics.
##https://doi.org/10.1177/20531680261428603
##Replication data: Harvard Dataverse doi:10.7910/DVN/OUFHWL, CC0 1.0. Files read: RAP_Main_US.tab (the US experiment) and, only to
##decide on it, RAP_Pilot_Korea.tab; RAP_Main_US.do, RAP_Pilot_Korea.do and RAP_readme-1.txt as text.
##Usage: Rscript takei_2026.R <dir holding RAP_Main_US.tab saved as us.tab> <output dir>
##
##1,404 US respondents (online sample, October 2025), one vignette each (id = a running number; task = profile = 1). A scenario
##about 'Country A' threatening U.S. military bases in 'Country B'. Six two-level vignette fragments are stored in the export as
##text columns, each about 50/50 (697-735 per level), and all are attributes here:
##  attr_regime    democracy / dictatorship   (the authors' main factor)
##  attr_threat    'that Country A would not take any military action regarding the U.S. bases' / 'that if the U.S. did not withdraw
##                 its military bases in Country B, Country A would bomb and capture them. If the attack is conducted, there is a
##                 possibility that hundreds of U.S. soldiers will be killed' (the authors' second main factor: no threat / empty threat)
##  attr_military_strength  militarily strong / militarily weak
##  attr_motive    because of a longstanding historical feud / to get more power and resources
##  attr_interest  hurt / not affect (what the base withdrawal would do to Country A's interests, the wording of the fragment)
##  attr_region    Europe / the Middle East
##The do file calls the four regime x threat cells 1 No Threat (Dem.), 2 Empty Threat (Dem.), 3 No Threat (Dic.), 4 Empty Threat (Dic.);
##military, motive, interest and region are 'other covariates randomized in the scenario' (do file, section before 'Mechanisms').
##The fragments' place in the vignette sentence is not shown in the deposit (the text of the full scenario is in the article).
##Outcomes (ratings; the question wording is not in the deposit or the do file, only the authors' labels, so each question below is
##recorded as 'wording not in deposit' with the authors' label):
##  rating_threat_credibility  S1_Credibility 'Threat Credibility (Continuous)': 1 Very unlikely, 2 Unlikely, 3 Likely, 4 Very likely (stage 1)
##  rating_situational_s1, rating_general_s1, rating_situational_s2, rating_general_s2: 'Situational' and 'General' approval (SA, GA) at
##     stage 1 and after stage 2, each a 7-point composite the authors build in RAP_Main_US.do (SA_Cont / GA_Cont):
##     7 approve very strongly, 6 approve somewhat, 5 neither + lean toward approving, 4 neither + don't lean, 3 neither + lean toward
##     disapproving, 2 disapprove somewhat, 1 disapprove very strongly. Higher = more approval. (S1 columns coded the same way; the
##     do file only recodes S2.)
##Not kept: the four yes/no mechanism items (Credibility, Competency, Reputation, Morality: wording not in the deposit), Plausibility,
##ExCons, Specific_*, free-text feedback, Race, Income, Ideology, military experience, registration, empathy items, timers.
##Korean pilot (RAP_Pilot_Korea): HELD, not a conjoint: its only manipulated factor is the stage-2 outcome (Stay Out vs Back Down;
##treatment = which question block was shown), a single factor.
##Covariates: cov_gender (Male = male, Female = female, Others = other, Prefer not to answer = NA), cov_age (years), cov_party_id
##(Partisanship: Democrat / Republican / Independent / Other Party / Don't know; 'Prefer not to answer' = NA), cov_education (the
##source's categories: Less than high school, High school, Some college, Bachelor's degree or higher; refusal = NA),
##cov_duration_sec (survey duration, 'Duration (in seconds)').
##Dropped: start/end/recorded dates, distribution channel, consent item, response-id-like fields (none present). No IP or location is in the file.
##Two respondents have no threat-credibility answer (blank in the source): that cell is NA, their other answers are kept.
##Count check: the paper's N is not retrievable here (article page blocked); 1,404 = the number of rows in RAP_Main_US.tab, all with
##a condition. The authors' extra exclusions (inattentive, manipulation-check) are not applied.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "us.tab"), encoding = "UTF-8", showProgress = FALSE)
stopifnot(nrow(k) == 1404)
cred <- c("Very unlikely" = 1L, "Unlikely" = 2L, "Likely" = 3L, "Very likely" = 4L)
sev <- function(main, ap, di, ne) {
  r <- rep(NA_integer_, length(main))
  r[main == "Approve" & ap == "Very strongly"] <- 7L; r[main == "Approve" & ap == "Somewhat"] <- 6L
  r[main == "Neither approve nor disapprove" & ne == "Lean toward approving"] <- 5L
  r[main == "Neither approve nor disapprove" & ne == "Don't lean either way"] <- 4L
  r[main == "Neither approve nor disapprove" & ne == "Lean toward disapproving"] <- 3L
  r[main == "Disapprove" & di == "Somewhat"] <- 2L; r[main == "Disapprove" & di == "Very strongly"] <- 1L
  r
}
o <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L,
  rating_threat_credibility = unname(cred[k$S1_Credibility]),
  rating_situational_s1 = sev(k$S1_SA, k$S1_SA_Approve, k$S1_SA_Disapprove, k$S1_SA_Neither),
  rating_general_s1 = sev(k$S1_GA, k$S1_GA_Approve, k$S1_GA_Disapprove, k$S1_GA_Neither),
  rating_situational_s2 = sev(k$S2_SA, k$S2_SA_Approve, k$S2_SA_Disapprove, k$S2_SA_Neither),
  rating_general_s2 = sev(k$S2_GA, k$S2_GA_Approve, k$S2_GA_Disapprove, k$S2_GA_Neither),
  attr_regime = k$regime, attr_threat = k$threat, attr_military_strength = k$military, attr_motive = k$motive,
  attr_interest = k$interest, attr_region = k$region)
stopifnot(sum(is.na(o$rating_threat_credibility)) == 2, !anyNA(o[, .(rating_situational_s1, rating_general_s1, rating_situational_s2, rating_general_s2)]))
o[, cov_gender := ifelse(k$Gender == "Male", "male", ifelse(k$Gender == "Female", "female", ifelse(k$Gender == "Others", "other", NA)))]
o[, cov_age := as.integer(k$Age)]
o[, cov_party_id := ifelse(k$Partisanship == "Prefer not to answer", NA, k$Partisanship)]
o[, cov_education := ifelse(k$Education == "Prefer not to answer", NA, k$Education)]
o[, cov_duration_sec := as.integer(k[["Duration (in seconds)"]])]
setorder(o, id, task, profile)
fwrite(o, file.path(out, "takei_2026_audience_costs.csv"))
