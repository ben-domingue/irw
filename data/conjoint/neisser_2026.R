##Hypothetical-MP rating conjoint (Germany) from
##Neisser, C., & Wehrhöfer, N. (2026). Outside income as a signal: Evidence from
##politicians and voters. The Review of Economics and Statistics.
##https://doi.org/10.1162/rest.a.1834
##Replication data: Harvard Dataverse doi:10.7910/DVN/5BPEXH, CC0 1.0, no restricted files.
##File read: "survey data/data/input/114945 Uni Köln Vignettenstudie - FD_4000.dta" from
##replication_package.zip (Stata value labels hold the German level text). Design facts
##from readme.pdf (section 1.3, Table 6) and "survey data/code/1_read_survey_data.do"
##(read as text).
##Usage: Rscript neisser_2026.R <dir holding the .dta> <output dir>
##
##4,028 German respondents (Bilendi online panel, 12 Dec 2023 - 5 Jan 2024), sampled only
##if they intended to vote for SPD, CDU/CSU, Greens, FDP or Die Linke. Each rated 3
##hypothetical members of the Bundestag, one at a time (task 1-3; profile = 1, a
##single-profile rating design: no choice between profiles). Attributes (German text as
##displayed): attr_gender Männlich/Weiblich; attr_marital_status Ledig/Verheiratet;
##attr_party SPD/CDU/CSU/Die Grünen/FDP/Die Linke; attr_terms "1 Legislaturperiode"/
##"2 Legislaturperioden"/"3 oder mehr Legislaturperioden"; attr_mandate "Über ein
##Direktmandat"/"Über ein Listenmandat" (the displayed text continued with an explanation
##whose pronoun followed the MP's gender, e.g. "..., d.h. er wurde direkt in seinem
##Wahlkreis gewählt"; only the lead is stored because the female wording is truncated in
##the value label); attr_outside_activity = the disclosed outside activity and income, one
##displayed line, e.g. "Anwalt, Einkünfte zwischen 1000€ und 3500€" (13 levels: none, or
##4 activities x 3 income bands; the authors split it into job and income).
##Level weights (observed, not documented; every pair of levels occurs, so no combination rule
##is visible): "Keine veröffentlichungspflichtigen
##Nebentätigkeiten und Nebeneinkünfte" is 25% of profiles vs about 6% for each of the 12
##other levels; parties are unequal (SPD 32%, CDU/CSU 30%, Greens 19%, FDP 14%, Linke 6%,
##the same shares as the authors' 2021 vote-share weights).
##Outcomes, each 1 = "stimme gar nicht zu" .. 7 = "stimme voll und ganz zu", wording from
##the truncated Stata variable labels and readme Table 6 (paraphrase):
##  rating_voter_interest = "Es handelt sich um einen Abgeordneten, der primär die
##     Interessen der Wähler ..." (MP primarily represents voters' interests)
##  rating_competent = "Es handelt sich um einen fachlich kompetenten Abgeordneten ..."
##  rating_own_interest = "Es handelt sich um einen Abgeordneten, der primär die eigenen
##     ..." (MP primarily represents own or third-party interests). NOTE: higher = LESS
##     favourable; kept as asked.
##  rating_hardworking = "Es handelt sich um einen hart arbeitenden Abgeordneten."
##The authors divide each outcome by its weighted SD; raw 1-7 kept here.
##Attention check: the authors keep respondents who ticked "sehr interessiert" and
##"überhaupt nicht interessiert" only; 3 respondents fail (cov_attention_pass = 0), kept.
##cov_survey_weight = the authors' raking-style weight (target shares for gender, East/West,
##age group and party from the 2021 federal election, computed in 1_read_survey_data.do on
##the 4,025 passing respondents; recomputed here the same way, NA for the 3 failing).
##Covariates: cov_age_group = the band text of the Stata value labels on age_participant ("18-29",
##"30-39", "40-49", "50-59", ">= 60"; "Wie alt sind Sie?"); cov_gender from gender_participant
##(value labels 1 "Männlich" -> "male", 2 "Weiblich" -> "female"; "Divers"/"Keine Angabe" do not
##occur); cov_west 1=West Germany 0=East Germany (incl. Berlin); cov_party_preference
##1=SPD 2=CDU/CSU 3=Greens 4=FDP 5=Die Linke (vote intention, "Welche Partei würden Sie wählen,
##wenn am kommenden Sonntag ...", so not party identification; codes kept); cov_informed_* 0/1 (has informed themself
##about MPs' outside activities via friends / Bundestag website / media / social media / no
##/ no answer).
##Dropped: the panel's captured ID (platform identifier), interview time. Respondent ids
##are the survey's record numbers re-keyed to integers.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- read_dta(file.path(raw, "114945 Uni Köln Vignettenstudie - FD_4000.dta"))
lab <- function(v) { l <- attr(v, "labels"); r <- names(l)[match(as.numeric(v), l)]; stopifnot(!anyNA(r)); r }
stopifnot(!anyDuplicated(x$record))
pass <- with(x, quality_check2r1 == 1 & quality_check2r2 == 0 & quality_check2r3 == 0 & quality_check2r4 == 0 & quality_check2r5 == 1)
stopifnot(identical(names(attr(x$age_participant, "labels"))[1:5], c("18-29", "30-39", "40-49", "50-59", ">= 60")),
          identical(names(attr(x$gender_participant, "labels"))[1:2], c("Männlich", "Weiblich")))
cv <- data.table(id = seq_len(nrow(x)), age_code = as.integer(x$age_participant), gender_code = as.integer(x$gender_participant),
                 cov_west = as.integer(x$state_participant == 1), cov_party_preference = as.integer(x$party_preference),
                 cov_attention_pass = as.integer(pass))
for (k in 1:6) cv[, paste0("cov_informed_", c("friends", "bundestag_site", "media", "social_media", "no", "no_answer")[k]) := as.integer(x[[paste0("info_participantr", k)]])]
stopifnot(all(cv$age_code %in% 1:5), all(cv$gender_code %in% 1:2), all(cv$cov_party_preference %in% 1:5))
# authors' weight (1_read_survey_data.do), on the passing respondents
w <- cv[cov_attention_pass == 1]
w[, tgt := c(0.48, 0.52)[gender_code] * fifelse(cov_west == 1, 0.80, 0.20) * c(0.13, 0.14, 0.14, 0.20, 0.39)[age_code] *
            c(0.32, 0.30, 0.18, 0.14, 0.06)[cov_party_preference]]
w[, act := .N / nrow(w), by = .(gender_code, cov_west, age_code, cov_party_preference)]
cv[w, on = "id", cov_survey_weight := i.tgt / i.act]
cv[, `:=`(age_code = c("18-29", "30-39", "40-49", "50-59", ">= 60")[age_code], gender_code = c("male", "female")[gender_code])]
setnames(cv, c("age_code", "gender_code"), c("cov_age_group", "cov_gender"))
blk <- c("A", "B", "C")
d <- rbindlist(lapply(1:3, function(t) {
  r <- function(k) as.integer(x[[sprintf("F5%sMP_conjoint%s%d", blk[t], blk[t], k)]])
  data.table(id = seq_len(nrow(x)), task = t, profile = 1L,
             rating_voter_interest = r(1), rating_competent = r(2), rating_own_interest = r(3), rating_hardworking = r(4),
             attr_gender = lab(x[[sprintf("REC_ATTR1_%d", t)]]), attr_marital_status = lab(x[[sprintf("REC_ATTR2_%d", t)]]),
             attr_party = lab(x[[sprintf("REC_ATTR3_%d", t)]]), attr_terms = lab(x[[sprintf("REC_ATTR4_%d", t)]]),
             attr_mandate = c("Über ein Direktmandat", "Über ein Listenmandat")[as.integer(x[[sprintf("REC_ATTR5_%d", t)]])],
             attr_outside_activity = lab(x[[sprintf("REC_ATTR6_%d", t)]]))
}))
rc <- grep("^rating_", names(d), value = TRUE)
stopifnot(all(unlist(d[, ..rc]) %in% 1:7), !anyNA(d$attr_mandate))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "neisser_2026_mp_outside_income.csv"))
