##Primary-candidate electability conjoint from
##Hassell, H. J. G., & Visalvanich, N. (2023). Perceptions of electability: Candidate (and voter)
##ideology, race, and gender. Political Behavior. https://doi.org/10.1007/s11109-023-09909-3
##Replication data: Harvard Dataverse doi:10.7910/DVN/HUMCVU, CC0 1.0, no restricted files, no
##terms. Files read: ConjointAnalysisReady.dta (Dataverse "original format" download of
##ConjointAnalysisReady.tab) and "ConjointAnalysisReady Codebook.txt" (the deposit's codebook).
##AllPollsFinal (ABC/Roper polls, no conjoint) is not used. The article could not be read
##(publisher and repository copies blocked); everything below is from the deposit.
##Usage: Rscript hassell_2023.R <raw dir> <output dir>
##
##2,051 respondents in the file, each shown 8 pairs of hypothetical primary candidates (16 rows
##per respondent, `number` = "the nth candidate the respondent saw", `paircomparison` = pair
##1-8). task = paircomparison (verified = ceiling(number / 2)); profile = 1 for the odd, 2 for
##the even `number` (recorded order). Primary scenario (trial_primary): Democrats got a
##Democratic primary, Republicans a Republican one, independents either (codebook
##conjointd#/conjointr#); it is respondent-assigned, so kept as trial_, not attr_.
##Attributes, text as stored in the deposit's wide slot columns (race#, gender#, ... for
##candidate # = number; district# for pair #). The questionnaire is not deposited, so whether
##the screen showed exactly these strings is unknown:
##  attr_race Black/Latino/White; attr_gender Female/Male; attr_age 34/51/68;
##  attr_ideology Very Liberal/Liberal/Moderate (Democratic primary, ideology#dem) or
##    Moderate/Conservative/Very Conservative (Republican primary, ideology#rep); the slot of
##    the other party is ignored (checked against the authors' ConjIdeology 1-6);
##  attr_experience None/State Legislator; attr_personableness "... personable and engaging as
##    an individual" (Very/Somewhat/"Not ersonable", typo kept as in the source);
##  attr_speaking Dynamic speaker/Good speaker/Below average speaker;
##  attr_district_pct_white 55/95 ("racial makeup of the district", codebook) and
##  attr_district_incumbent_won 51/68 ("partisan safety of the district", codebook; presumably
##    the incumbent's vote share): set per PAIR, identical on both profiles of a task.
##Restrictions: ideology levels depend on the primary scenario (codebook); district attributes
##are task-level. Otherwise no rule documented.
##Outcomes (codebook wording only, paraphrase), forced choice between the two candidates:
##  choice_electable = which candidate the respondent "identified ... as most electable of pair"
##    (conjointd#/conjointr# = 1 or 2 = position; equals the authors' moreelectable)
##  choice_vote = which candidate the respondent "identified ... as preferred candidate"
##    (conjointd#vote/conjointr#vote; equals wouldvote)
##No opt-out is documented. A skipped question is NA here (the authors' moreelectable/wouldvote
##code it 0 on both profiles: 261 / 319 pairs); pairs with both questions skipped are dropped,
##as are the 48 respondents with no answers at all (no primary scenario assigned).
##Covariates (codes per the deposit codebook, kept as codes unless stated): cov_age (years);
##cov_gender_code (gender 1/2: no codebook mapping; it disagrees with the authors' derived
##rfemale for 38 respondents, so not mapped); cov_race (multi-select codes, e.g. "1,2": 1 white,
##2 black, 3 native american, 4 asian, 5 Hawaiian/Pacific Islander, 6 other);
##cov_education_code (educ 1-7; the codebook's list repeats code 5 and so does not map 7 codes);
##cov_income 1-7 (<$20,000 .. $120,000 or more); cov_urbanrural 1 urban 2 suburban 3 rural;
##cov_born_us 1 US 2 not; cov_attention_politics 0-10; cov_party_id (pid3 text: 1 Republican,
##2 Democrat, 3 Independent); cov_pid_lean 1 lean R 2 lean D 3 neither (independents);
##cov_pid_strength 1 strong 2 weak; cov_ideology 1 very liberal..7 very conservative (9 = not
##thought about it, absent); cov_polactivity_1..6 1 yes 2 no (meeting/rally, campaign work,
##office, contributed, contacted official, voted in primary); cov_midterm_vote (5 = voted);
##cov_pid5 1-5; cov_duration_sec = durationinseconds (whole survey).
##Dropped: Qualtrics ResponseId (responseid) and panel id (rid) -- respondents re-keyed from the
##authors' respondantID; free text (race_6_text, whereborn_2_text); the authors' derived
##dummies/recodes (Conj*, minority, black, rfemale, RIdeolExt, IDNumber). No weight, no
##attention check, no repeated task.
##N: 2,003 respondents with answers (paper's N not checked: article unreadable). Spot check:
##choice_electable/choice_vote agree with the authors' moreelectable/wouldvote on every
##answered row (stopifnot below).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "conj.dta")))
stopifnot(k[, .N, respondantID][, all(N == 16)], all(k$paircomparison == ceiling(k$number / 2)))
slot <- function(stem, idx) { m <- as.matrix(k[, paste0(stem, 1:max(idx)), with = FALSE]); as.vector(m[cbind(seq_len(nrow(k)), idx)]) }
pd <- k[number == 1, .(respondantID, prim = fifelse(!is.na(conjointd1) | !is.na(conjointd1vote), "Democratic",
                                               fifelse(!is.na(conjointr1) | !is.na(conjointr1vote), "Republican", NA_character_)))]
# respondents never have both scenarios
stopifnot(k[number == 1, !any(!is.na(conjointd1) & !is.na(conjointr1))])
k <- merge(k, pd, by = "respondantID")
k <- k[!is.na(prim)]
el <- fifelse(k$prim == "Democratic", slot("conjointd", k$paircomparison), slot("conjointr", k$paircomparison))
vt <- {m1 <- as.matrix(k[, paste0("conjointd", 1:8, "vote"), with = FALSE]); m2 <- as.matrix(k[, paste0("conjointr", 1:8, "vote"), with = FALSE])
       ix <- cbind(seq_len(nrow(k)), k$paircomparison); fifelse(k$prim == "Democratic", m1[ix], m2[ix])}
pos <- 2L - as.integer(k$number) %% 2L
d <- data.table(rid0 = k$respondantID, task = as.integer(k$paircomparison), profile = pos,
                choice_electable = as.integer(el == pos), choice_vote = as.integer(vt == pos))
stopifnot(all(el %in% c(1, 2, NA)), all(vt %in% c(1, 2, NA)),
          all(d$choice_electable == k$moreelectable, na.rm = TRUE), all(d$choice_vote == k$wouldvote, na.rm = TRUE))
ideod <- as.matrix(k[, paste0("ideology", 1:16, "dem"), with = FALSE]); ideor <- as.matrix(k[, paste0("ideology", 1:16, "rep"), with = FALSE])
ix <- cbind(seq_len(nrow(k)), as.integer(k$number))
d[, `:=`(attr_race = slot("race", k$number), attr_gender = slot("gender", k$number), attr_age = as.character(slot("age", k$number)),
         attr_ideology = fifelse(k$prim == "Democratic", ideod[ix], ideor[ix]),
         attr_experience = slot("experience", k$number), attr_personableness = slot("charisma", k$number),
         attr_speaking = slot("speaking", k$number),
         attr_district_pct_white = as.character(slot("districtwhite", k$paircomparison)),
         attr_district_incumbent_won = as.character(slot("incumbentwon", k$paircomparison)),
         trial_primary = k$prim)]
# attributes agree with the authors' recodes
stopifnot(all((d$attr_race == "White") == (k$ConjCandRace == 1)), all((d$attr_race == "Black") == (k$ConjCandRace == 2)),
          all(d[!is.na(k$ConjIdeology), attr_ideology] == c("Very Liberal", "Liberal", "Moderate", "Moderate", "Conservative",
                                                             "Very Conservative")[k$ConjIdeology[!is.na(k$ConjIdeology)]]),
          all(d$attr_ideology[d$trial_primary == "Democratic"] %in% c("Very Liberal", "Liberal", "Moderate")),
          all(d$attr_ideology[d$trial_primary == "Republican"] %in% c("Moderate", "Conservative", "Very Conservative")))
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
cv <- c(age = "age", gender = "gender_code", race = "race", educ = "education_code", income = "income", urbanrural = "urbanrural",
        whereborn = "born_us", attpol_1 = "attention_politics", pidlean = "pid_lean", pidstrength = "pid_strength",
        RIdeology = "ideology", midtermvote = "midterm_vote", pid5 = "pid5", durationinseconds = "duration_sec")
for (v in names(cv)) d[, paste0("cov_", cv[[v]]) := k[[v]]]
for (j in 1:6) d[, paste0("cov_polactivity_", j) := k[[paste0("polactivity_", j)]]]
stopifnot(all(k$pid3 %in% c(1:3, NA)))
d[, cov_party_id := c("Republican", "Democrat", "Independent")[k$pid3]]
d[cov_race == "", cov_race := NA]
d <- d[!(is.na(choice_electable) & is.na(choice_vote))]
d[, id := as.integer(factor(rid0))][, rid0 := NULL]
setcolorder(d, c("id", "task", "profile"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hassell_2023_electability.csv"))
