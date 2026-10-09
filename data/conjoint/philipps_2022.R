##Factorial vignette survey of German state-level MPs from
##Philipps, G. (2024). Compromise-building in the spotlight of the media? Individual and
##situational influences on the self-mediatization of parliamentary negotiations. The
##International Journal of Press/Politics, 29(2), 570-590 (online first 2022).
##https://doi.org/10.1177/19401612221132719
##Replication data: Harvard Dataverse doi:10.7910/DVN/SD9M5A, CC0 1.0, no restricted files.
##Files read: "dataset_self-mediatization of parliamentary negotiations_factorial MP
##survey.sav" (Dataverse "original format" download of the .tab; read here as data.sav) and
##the deposit's "variable overview ... .pdf" (German wording + English translation of every
##item; the vignette text itself is not deposited and the article is closed access).
##Usage: Rscript philipps_2022.R <raw dir holding data.sav> <output dir>
##
##258 German state-parliament (Landtag) MPs, one vignette each (task = 1, profile = 1): a
##coalition negotiation over a draft law, in a 2 x 2 factorial design randomly assigned
##(VI06, "randomly distributed vignette variant"): pressure to reach a decision (high/low) x
##election campaign (imminent/still far away). Cell sizes 70/68/61/59. The level text is the
##variable overview's English description of each VI06 value (respondents read German prose;
##label_language en). No respondent id ships: one row per respondent, id = row number.
##Outcomes (all 1-5; the PDF's English translation, so "(translated)" in design_outcomes):
##  "In the period until the next round of negotiations, ..." 1 = not likely at all .. 5 = very likely
##   rating_info_social (DV01_01) ... I would publish information about the negotiation of the
##     draft law on social media platforms, such as Twitter or Facebook.
##   rating_info_website (DV01_02), rating_position_social (DV01_03; "advertise my faction's
##     position regarding the draft law"), rating_position_website (DV01_04),
##   rating_info_press_release (DV01_05), rating_info_interview (DV01_06),
##   rating_info_journalists (DV01_07; "by providing certain journalists with corresponding
##     information"), rating_position_press_release (DV01_08), rating_position_interview
##     (DV01_09), rating_position_journalists (DV01_10)
##  "How likely would the following actions be in the period until the next round of
##   negotiations?" 1 = not likely at all .. 5 = very likely
##   rating_initiate_nondisclosure (DV02_01), rating_agree_nondisclosure (DV02_02),
##   rating_keep_confidential (DV02_03)
##  "How likely would it be that you, as a negotiator, would do the following in the next round
##   of negotiations?" 1 = not likely at all .. 5 = very likely
##   rating_compromise (DV03_01), rating_stick_to_position (DV03_02),
##   rating_end_without_agreement (DV03_03), rating_reach_agreement (DV03_04)
##  "If you compare the situation described with your experience in parliament, how much do you
##   agree with the following statements?" 1 = do not agree at all .. 5 = agree completely
##   rating_realism_imagine (CH01_01), rating_realism_experienced (CH01_02),
##   rating_realism_can_occur (CH01_03), rating_realism_others_experienced (CH01_04; 2 missing)
##  Manipulation checks, "In the situation description, it was stated, ..." (2 missing each):
##   rating_check_pressure (CH02_01) 1 = "... that there is no high pressure to reach a decision,
##     as the draft law is aimed at a problem of little relevance" .. 5 = "... a high pressure
##     ... problem of great relevance"
##   rating_check_campaign (CH02_02) 1 = "... that the election campaign is imminent, and
##     therefore public attention is increased" .. 5 = "... still far away, and therefore the
##     public attention is average"
##All ratings are stored raw (no reversal). Not a choice task: no opt-out.
##Covariates (codes -> text from the .sav value labels / variable overview): cov_gender (SD01:
##1 female, 2 male, 3 diverse -> other, missing 1), cov_age (SD02, years, 6 missing),
##cov_faction (FA01, parliamentary group the MP belongs to, label text; a membership, not
##party identification), cov_governing_faction (FA02, 1 yes / 2 no), cov_comm_<channel>
##(CF01-CF05 "How often do you use the following mediums or ways to publish information about
##your political work?", 1 = never .. 5 = very often: press_release, interview,
##background_talks, website, social_media).
##Dropped: the authors' recodes and indices (IV01, IV02, *_pos, *_MEAN, CF_OLD, CF_NEW).
##No survey weight in the deposit. N = 258 matches the deposit description (n = 258).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_sav(file.path(raw, "data.sav"))
stopifnot(nrow(s) == 258, all(s$VI06 %in% 1:4))
z <- function(x) { x <- as.integer(zap_labels(x)); x[x < 0] <- NA_integer_; x }
pres <- c("high pressure to reach a decision", "high pressure to reach a decision",
          "low pressure to reach a decision", "low pressure to reach a decision")
camp <- c("election campaign still far away", "election campaign imminent",
          "election campaign imminent", "election campaign still far away")
v <- z(s$VI06)
d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L,
                attr_decision_pressure = pres[v], attr_election_campaign = camp[v])
outc <- c(DV01_01 = "info_social", DV01_02 = "info_website", DV01_03 = "position_social",
          DV01_04 = "position_website", DV01_05 = "info_press_release", DV01_06 = "info_interview",
          DV01_07 = "info_journalists", DV01_08 = "position_press_release", DV01_09 = "position_interview",
          DV01_10 = "position_journalists", DV02_01 = "initiate_nondisclosure", DV02_02 = "agree_nondisclosure",
          DV02_03 = "keep_confidential", DV03_01 = "compromise", DV03_02 = "stick_to_position",
          DV03_03 = "end_without_agreement", DV03_04 = "reach_agreement", CH01_01 = "realism_imagine",
          CH01_02 = "realism_experienced", CH01_03 = "realism_can_occur", CH01_04 = "realism_others_experienced",
          CH02_01 = "check_pressure", CH02_02 = "check_campaign")
for (k in names(outc)) { x <- z(s[[k]]); stopifnot(all(x %in% c(1:5, NA))); d[, paste0("rating_", outc[[k]]) := x] }
g <- z(s$SD01); stopifnot(all(g %in% c(1:3, NA)))
d[, cov_gender := c("female", "male", "other")[g]]
d[, cov_age := z(s$SD02)]
f <- z(s$FA01); d[, cov_faction := as.character(as_factor(s$FA01, levels = "labels"))]
d[is.na(f), cov_faction := NA_character_]
d[, cov_governing_faction := z(s$FA02)]
cf <- c(CF01 = "press_release", CF02 = "interview", CF03 = "background_talks", CF04 = "website", CF05 = "social_media")
for (k in names(cf)) d[, paste0("cov_comm_", cf[[k]]) := z(s[[k]])]
stopifnot(d[, uniqueN(paste(attr_decision_pressure, attr_election_campaign))] == 4)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "philipps_2022_self_mediatization.csv"))
