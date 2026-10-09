##Two tariff conjoints (Germany: coalition agreements; UK: candidates) from
##Grahn, M., Lawall, K., Mainz, S., Nordbrandt, M., & Turnbull-Dugarte, S. J. (2025). A game of tariffs:
##is there demand for tariffs in Europe? Journal of European Public Policy.
##https://doi.org/10.1080/13501763.2025.2571062 (open access, CC BY; read from the Reading CentAUR copy;
##the appendix with Tables A.2/A.3 and question wording was not available)
##Replication data: Harvard Dataverse doi:10.7910/DVN/H9DPSX, CC0 1.0. File read:
##Grahn_etal_replication_material.zip -> df_UK_JEPP.rds, df_DE_JEPP.rds (long cregg frames that also
##carry the respondent's wide Qualtrics export, including the displayed level text of every task and
##profile in choice<task>_<attribute><profile>), tariffs_replication_JEPP.R (as text).
##Usage: Rscript grahn_2025.R <dir holding df_UK_JEPP.rds and df_DE_JEPP.rds> <output dir>
##
##Two experiments with different attribute sets, samples and languages: two tables (the authors
##analyse them separately as Study 1 and Study 2).
##Level text = the displayed text from the wide export columns (emoji included as shown), checked to
##map to the authors' coded long columns (each displayed text has one code; the DE migration code
##"Generic" covers two displayed texts). Task and profile are recorded in the long frame.
##Attribute order and randomization restrictions are not documented in the deposit.
##
##grahn_2025_tariffs_uk (Study 2): 1,500 Prolific respondents (UK, May 2025; article 1,500, matches),
##5 tasks x 2 candidates "each running under the respondent's self-identified most preferred political
##party" (article); that party is the same for both candidates and stored as trial_candidate_party
##(candidateGroup). Attributes: attr_name, attr_age, attr_job, attr_photo (the Qualtrics graphic id of
##the candidate photo, e.g. "IM_4yZ6PLpcLdRbo4H"; image not deposited; photos/names vary by the
##authors' undocumented candidate category cat A-D, which is not stored), attr_immigration,
##attr_immigration_motivation (a bare emoji shown when no motivation was given: authors' "No
##motivation"), attr_social_media, attr_economy (incl. the two tariff levels), attr_gender_ruling
##(position on the UK Supreme Court ruling on gender).
##  choice: "Which candidate do you prefer?" (Qualtrics label of <t>_outcome1), forced choice.
##  rating: "How likely is it that you would ever support each of the candidates?" 1 = Not at all
##    likely ... 5 = Very likely (PTV; asked for both candidates).
##  Covariates: cov_age, cov_gender (Woman female, Man male, Non-binary/ third gender other, Prefer not
##  to say NA), cov_trans, cov_ethnicity, cov_education, cov_migrant_background, cov_religion,
##  cov_party_id (partyID; "No - None" kept as text), cov_party_id_strength, cov_leftright (lr_self_1,
##  as text "1 Left" ... "10 Right"), cov_gender_attitude, cov_social_media_regulation,
##  cov_ruling_aware, cov_affect_* (0-10 feeling thermometers). Dropped: prolificID, PROLIFIC_PID,
##  ResponseId (re-keyed), free text (conjoint_reflect, *_TEXT), timings, the constant attention
##  checks ac1_1/ac2 (all respondents 9 and 3: the deposit holds passers only), post-conjoint
##  photo-perception items, authors' recodes.
##
##grahn_2025_tariffs_de (Study 1): 3,864 Bilendi respondents (Germany, April 2025). The ARTICLE
##REPORTS 3,994; the deposit has 3,864 (flagged, not resolved). 3 tasks x 2 hypothetical coalition
##agreements (Koalitionsvertrag 1/2), attributes (German text as displayed): attr_coalition (parties),
##attr_economy, attr_protectionism (the tariff attribute: tariffs, green tariffs, two EU-contribution
##cuts), attr_migration, attr_womens_rights (women's quotas in companies), attr_lgbt, attr_social_media.
##  choice: preferred coalition agreement (paraphrase; question text not in the export labels).
##  rating: likelihood item asked for each agreement, 1 = "Gar nicht wahrscheinlich" ... 5 = "Sehr
##    wahrscheinlich" (<t>_outcome2_1/2; wording not deposited; the article calls it the ranked
##    outcome).
##  The German survey also contained a video experiment (video_remember, mc_treatment); the
##  assignment is not in the deposit and whether it preceded the conjoint is not documented.
##  Covariates: cov_age, cov_gender (Frau female, Mann male, Nicht-binär/drittes Geschlecht and
##  Andere Selbstbeschreibung other, Möchte ich lieber nicht sagen NA), cov_region (arealiving,
##  Bundesland), cov_education, cov_migrant_family, cov_employed, cov_party_id (partyID; refusal NA,
##  "Ich weiß nicht" and "Nein, keine dieser Parteien." kept), cov_party_id_strength, cov_leftright,
##  cov_dem_sat, cov_trust_*, cov_party_thermometer_*, cov_affect_*. Dropped: PROLIFIC_PID (present
##  though the panel is Bilendi), ResponseId (re-keyed), free text (*_TEXT, video_remember),
##  sexual orientation and trans identity (sensitive), video-experiment items, timings, recodes.
##No survey weights in either file.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
wide_attr <- function(m, stem) {
  v <- rep(NA_character_, nrow(m))
  for (t in sort(unique(m$task))) for (p in 1:2) {
    i <- which(m$task == t & m$profile == p)
    v[i] <- as.character(m[[sprintf("choice%d_%s%d", t, stem, p)]][i])
  }
  trimws(gsub("\\s+", " ", v))
}
chk <- function(text, code) stopifnot(!anyNA(text), all(text != ""), uniqueN(data.table(text, code)) == uniqueN(text))
num <- function(x) as.integer(sub("^\\D*(\\d+).*$", "\\1", as.character(x)))
## ---- UK ----
u <- as.data.table(readRDS(file.path(raw, "df_UK_JEPP.rds")))
stopifnot(nrow(u) == 15000L, uniqueN(u$ResponseId) == 1500L, u[, .(sum(selected), .N), .(ResponseId, task)][, all(V1 == 1 & N == 2)])
d <- u[, .(id = match(ResponseId, sort(unique(ResponseId))), task = as.integer(task), profile = as.integer(profile),
           choice = as.integer(selected), rating = as.integer(PTV))]
d[, attr_name := wide_attr(u, "name")][, attr_age := wide_attr(u, "age")][, attr_job := wide_attr(u, "job")]
d[, attr_photo := sub(".*IM=", "", wide_attr(u, "image"))]
d[, attr_immigration := wide_attr(u, "immigration")][, attr_immigration_motivation := wide_attr(u, "motivation")]
d[, attr_social_media := wide_attr(u, "socialmedia")][, attr_economy := wide_attr(u, "economy")]
d[, attr_gender_ruling := wide_attr(u, "gender")]
chk(d$attr_economy, u$economy_clean); chk(d$attr_job, u$job_clean); chk(d$attr_immigration, u$immigration_clean)
chk(d$attr_immigration_motivation, u$motivation_clean); chk(d$attr_social_media, u$socialmedia_clean); chk(d$attr_gender_ruling, u$gender_clean)
stopifnot(!anyNA(d$attr_name), !anyNA(d$attr_age), !anyNA(d$attr_photo), all(grepl("^IM_", d$attr_photo)), all(d$rating %in% 1:5))
o2 <- rep(NA_integer_, nrow(u)); for (t in 1:5) for (p in 1:2) { i <- which(u$task == t & u$profile == p); o2[i] <- num(u[[sprintf("%d_out2candidate%d", t, p)]][i]) }
stopifnot(all(o2 == d$rating))
d[, trial_candidate_party := as.character(u$candidateGroup)]
d[, `:=`(cov_age = as.integer(u$age),
         cov_gender = c(Woman = "female", Man = "male", "Non-binary/ third gender" = "other")[u$gender],
         cov_trans = fifelse(u$trans == "Prefer not to say", NA_character_, u$trans),
         cov_ethnicity = fifelse(u$ethnic == "Prefer not to say", NA_character_, u$ethnic),
         cov_education = u$educ, cov_migrant_background = fifelse(u$migrant == "Prefer not to say", NA_character_, u$migrant),
         cov_religion = u$religion, cov_party_id = u$partyID, cov_party_id_strength = u$partyID_strength,
         cov_leftright = u$lr_self_1, cov_gender_attitude = u$gender_attitude, cov_social_media_regulation = u$socialmediareg,
         cov_ruling_aware = u$rulingaware)]
for (v in grep("^affect_", names(u), value = TRUE)) d[, paste0("cov_", v) := as.integer(u[[v]])]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "grahn_2025_tariffs_uk.csv"))
## ---- DE ----
g <- as.data.table(readRDS(file.path(raw, "df_DE_JEPP.rds")))
stopifnot(nrow(g) == 23184L, uniqueN(g$ResponseId) == 3864L, g[, .(sum(selected), .N), .(ResponseId, task)][, all(V1 == 1 & N == 2)])
stopifnot(all((g$outcome1 == paste("Koalitionsvertrag", g$profile)) == (g$selected == 1)))
e <- g[, .(id = match(ResponseId, sort(unique(ResponseId))), task = as.integer(task), profile = as.integer(profile),
           choice = as.integer(selected), rating = as.integer(PTV))]
e[, attr_coalition := wide_attr(g, "parties")][, attr_economy := wide_attr(g, "economy")]
e[, attr_protectionism := wide_attr(g, "environment")][, attr_migration := wide_attr(g, "immigration")]
e[, attr_womens_rights := wide_attr(g, "abortion")][, attr_lgbt := wide_attr(g, "lgbt")][, attr_social_media := wide_attr(g, "socialmedia")]
chk(e$attr_coalition, g$parties_clean_simple); chk(e$attr_economy, g$economy_clean); chk(e$attr_protectionism, g$environment_clean)
chk(e$attr_migration, g$immigration_clean); chk(e$attr_womens_rights, g$abortion_clean); chk(e$attr_lgbt, g$lgbt_clean)
chk(e$attr_social_media, g$socialmedia_clean)
# the PTV in the long frame equals the wide outcome2 item of the same task/profile
o2 <- rep(NA_integer_, nrow(g)); for (t in 1:3) for (p in 1:2) { i <- which(g$task == t & g$profile == p); o2[i] <- num(g[[sprintf("%d_outcome2_%d", t, p)]][i]) }
stopifnot(all(o2 == e$rating), all(e$rating %in% 1:5))
pid <- g$partyID; pid[pid == "Möchte ich lieber nicht sagen"] <- NA
e[, `:=`(cov_age = as.integer(g$age),
         cov_gender = c(Frau = "female", Mann = "male", "Nicht-binär/drittes Geschlecht" = "other", "Andere Selbstbeschreibung" = "other")[g$gender],
         cov_region = g$arealiving, cov_education = g$educ, cov_migrant_family = g$dem_migfam, cov_employed = g$employed,
         cov_party_id = pid, cov_party_id_strength = g$partyIDstrength, cov_leftright = as.character(g$lr_self),
         cov_dem_sat = as.character(g$dem_sat))]
for (v in c(grep("^trust_|^party_feeling_therm_", names(g), value = TRUE), grep("^affect_", names(g), value = TRUE)))
  e[, paste0("cov_", sub("party_feeling_therm_", "party_thermometer_", v)) := as.character(g[[v]])]
setorder(e, id, task, profile)
fwrite(e, file.path(out, "grahn_2025_tariffs_de.csv"))
