##Two-stage candidate (de)selection and list-ranking conjoint with Austrian party elites, from
##Jankowski, M., & Rehmert, J. (2024). Selecting and ranking female candidates under PR: Evidence
##from a two-stage conjoint experiment with party elites. European Journal of Political Research.
##https://doi.org/10.1111/1475-6765.12726
##Replication data: Harvard Dataverse doi:10.7910/DVN/O1ILRD, CC0 1.0, no restricted files, no terms.
##File read: long_data_prep.rds (one row per respondent x aspirant profile, with the respondent's
##survey answers and SPSS-style labels). Read as text only: replication_Jankowski_Rehmert.qmd.
##Design facts, English attribute table (Table A2) and the task screenshots (Figure A3, p. D5) from
##the preprint (OSF doi:10.31219/osf.io/mkauz, CC BY 4.0). respondents.tab (ResponseID + party) and
##vorstaende_austria.csv (party-executive roster) are not read.
##Usage: Rscript jankowski_2024.R <raw dir> <output dir>
##
##324 members of Austrian party executives (Greens, NEOS, SPOe, OeVP, FPOe), Qualtrics web survey
##sent 4 October 2021 (reminders November/December). ONE task with NINE aspirant profiles ("Person
##1".."Person 9", profile = source `profile`, recorded) and 8 attributes per respondent, in German.
##Two outcomes on the same profiles, one table:
##  rating_deselected: stage 1, "Wen wuerden Sie nicht nominieren?" ("Whom would you not nominate?"),
##    a checkbox under each profile; respondents had to tick exactly three (1 = deselected, 0 = kept).
##    Not a `choice`: three of nine are picked, so it is stored as a 0/1 judgement.
##  rating_list_position: stage 2, the six kept profiles are shown again and each is nominated to a
##    list position ("Nominierung auf Listenplatz...", buttons "Auf Listenplatz 1 nominieren." ..);
##    1-6, 1 = top of the list (lower = better); NA for the three deselected profiles.
##  Every respondent deselects exactly 3 and ranks the other 6 to positions 1-6 once each (checked).
##Attributes (the German text in the data, which matches the screenshot; "<br>" line breaks
##removed: "National-<br>rat" -> "Nationalrat", "Kandidatur<br>geplant" -> "Kandidatur geplant"):
##  gender (Geschlecht: Frau/Mann), age (Alter: in den 30ern..70ern), policy_expertise (Thematische
##  Kompetenz, 9 levels), intraparty_position (Politische Position innerhalb der Partei),
##  personal_votes (Potential fuer viele Vorzugsstimmen: gering/moderat/hoch), parliament_experience
##  (Parlamentserfahrung: Keine/Nationalrat), party_deviation (Abweichung von Parteibeschluessen:
##  selten/ab und zu/haeufig), and ONE dual-candidacy attribute per respondent: regional_list
##  ("Kandidatur auf Regionalliste": Ja, nominiert/Nicht nominiert; 180 respondents) or
##  state_federal_list ("Kandidatur auf Landes-/Bundesliste": Kandidatur geplant/Plant keine
##  Kandidatur; 144). The one a respondent did not see is "(not shown)" (the authors pool both as
##  fct_otherlist). Which version a respondent got presumably followed the list tier(s) they select
##  for, but the rule is not documented and does not map one-to-one onto ebene1-4.
##  "The order of the attributes was randomized between respondents and the attribute levels were
##  fully randomized" (preprint sec. 5): attrpos_* = the source *rowpos columns (1-8, constant within
##  respondent; NA for the attribute not shown).
##Respondents are re-keyed to the source `respondent` integer (the Qualtrics ResponseID/ResponseId
##is dropped). Covariates: cov_gender (respondent_gender Female/Male -> female/male), cov_party
##(respondent_party: Gruene, NEOS, SPO, OVP, FPO; the party whose executive the respondent sits on),
##cov_birth_decade (qyob, "In welchem Jahr wurden Sie geboren?", coarsened to decade: a small named elite population), cov_duration_sec (whole survey),
##cov_strategy (qstrategy answer text: individual traits vs list composition), cov_lr_party and
##cov_lr_self (qleftright1/2, 1 = ganz links .. 11 = ganz rechts), cov_influence_federal/state/
##regional (qefficacy1-3, own influence on the Bundeswahlvorschlag/Landes-/Regionalparteiliste,
##1 = sehr schwachen .. 7 = sehr starken Einfluss), cov_board_district/state/federal (bezirk-/land-/
##bundjanein answer text Ja/Nein), cov_selects_regional/state/federal/none (ebene1-4: 1 if the
##respondent takes part in candidate selection at that tier, else 0).
##DROPPED: Qualtrics metadata (Start/End/RecordedDate, Status, Progress, ResponseId,
##ExternalReference, DistributionChannel, UserLanguage), qpartyentry and the bezirk-/land-/bundwann
##years (year joined the party / each executive: with party, gender and birth year they would narrow
##a roster of named office-holders), personalexperience (free text), the reason-for-deselection
##placeholders (all 99), the experiment-programming columns (candidate*, selected*, deselected*,
##ndeselected, ballotposition1-6, currwidth*, currfontsize*), and derived columns (pospar,
##list_composition, lr_diff, lr_cat, fct_*, AndereKandidatur, id). No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "long_data_prep.rds")))
stopifnot(nrow(s) == 2916L, uniqueN(s$respondent) == 324L, all(s$task == 1L), s[, .N, respondent][, all(N == 9)],
          s[, uniqueN(ResponseID), respondent][, all(V1 == 1)], all(as.numeric(s$Progress) == 100))
br <- function(x) gsub("<br>", " ", gsub("-<br>", "", x))
att <- c(gender = "Geschlecht", age = "Alter", policy_expertise = "ThematischeKompetenz",
         intraparty_position = "PolitischePositioninnerhalbderPartei", regional_list = "KandidaturaufRegionalliste",
         state_federal_list = "KandidaturaufLandesBundesliste", personal_votes = "PotentialfürvieleVorzugsstimmen",
         parliament_experience = "Parlamentserfahrung", party_deviation = "AbweichungvonParteibeschlüssen")
d <- s[, .(id = as.integer(respondent), task = 1L, profile = as.integer(profile),
           rating_deselected = as.integer(deselected), rating_list_position = as.integer(ballotposition))]
for (k in names(att)) {
  v <- br(s[[att[[k]]]]); p <- suppressWarnings(as.integer(s[[paste0(att[[k]], "rowpos")]]))
  stopifnot(all((v == "") == is.na(p)))
  d[, paste0("attr_", k) := fifelse(v == "", "(not shown)", v)]
  d[, paste0("attrpos_", k) := p]
}
stopifnot(d[, all((attr_regional_list == "(not shown)") != (attr_state_federal_list == "(not shown)"))],
          d[, uniqueN(attrpos_gender), id][, all(V1 == 1)])
stopifnot(d[, sum(rating_deselected), id][, all(V1 == 3)], d[rating_deselected == 1, all(is.na(rating_list_position))],
          d[rating_deselected == 0, .(ok = setequal(rating_list_position, 1:6)), id][, all(ok)])
z <- function(x) as.integer(haven::zap_labels(x))
lab <- function(x) as.character(haven::as_factor(x, levels = "labels"))
d[, `:=`(cov_gender = c(Female = "female", Male = "male")[as.character(s$respondent_gender)],
         cov_party = as.character(s$respondent_party), cov_birth_decade = floor(z(s$qyob) / 10) * 10,
         cov_duration_sec = as.numeric(s$Durationinseconds), cov_strategy = lab(s$qstrategy),
         cov_lr_party = z(s$qleftright1), cov_lr_self = z(s$qleftright2),
         cov_influence_federal = z(s$qefficacy1), cov_influence_state = z(s$qefficacy2), cov_influence_regional = z(s$qefficacy3),
         cov_board_district = lab(s$bezirkjanein), cov_board_state = lab(s$landjanein), cov_board_federal = lab(s$bundjanein),
         cov_selects_regional = as.integer(!is.na(z(s$ebene1))), cov_selects_state = as.integer(!is.na(z(s$ebene2))),
         cov_selects_federal = as.integer(!is.na(z(s$ebene3))), cov_selects_none = as.integer(!is.na(z(s$ebene4))))]
d[, cov_gender := unname(cov_gender)]
stopifnot(!anyNA(d$cov_gender), all(d$cov_party %in% c("Gruene", "NEOS", "SPO", "OVP", "FPO")))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "jankowski_2024_list_ranking_austria.csv"))
