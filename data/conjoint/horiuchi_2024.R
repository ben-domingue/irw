##Two military-deployment conjoints (Japan) from
##Horiuchi, Y., & Tago, A. (2024). U.S. military should not be in my backyard: Conjoint
##experiments in Japan. Journal of Conflict Resolution, 68(9), 1798-1824.
##https://doi.org/10.1177/00220027231203607
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZIRSC1, CC0 1.0, no restricted files.
##Files read (from ReplicationPackage.tar.gz, horiuchi-tago/data/surveys/): Osprey.csv,
##Osprey_Okinawa.csv (Study 1), F35.csv, F35_Okinawa.csv (Study 2): Qualtrics exports with
##two header rows, answers as Japanese text. Wording from documents/surveys/Osprey.docx,
##F35.docx, F35_Okinawa.docx; the authors' scripts (step01, step04, functions/) read as text.
##Usage: Rscript horiuchi_2024.R <raw dir holding the four CSVs> <output dir>
##
##Two experiments with different attribute sets = two tables. In each, a national online
##sample and an Okinawa oversample answered the same conjoint and the authors pool them
##(okinawa indicator), so each table pools both, with cov_sample (national / okinawa).
##Profiles "計画案A" (profile 1) and "計画案B" (profile 2) in a grid; attribute rows in an
##order randomized once per respondent (the A-t-k names are identical over a respondent's
##tasks), recorded as attrpos_<attr>. Level text is Japanese as displayed, with the HTML
##line break "<br>" replaced by a space (e.g. "沖縄県那覇市 （陸上自衛隊・那覇駐屯地）").
##Outcome (both): choice, "あなたはどちらの計画案をより支持しますか。もし、どちらを支持するか
##はっきりとは言えない場合でも、どちらか一方、あえていえば支持する方を選んでください。" then
##"どちらを支持しますか。" 計画案A / 計画案B; forced, no opt-out.
##
##horiuchi_2024_osprey (Study 1, MV-22 Osprey): 10 tasks ("同じような表が１０回提示されます"),
##6 attributes: 施設の場所 (location: 4 Ground SDF camps), 運用する主体 (operated by: アメリカ軍 /
##自衛隊), 地域振興策 (regional incentives over 20 years), 部隊の規模 (force size), 夜間訓練の有無
##(night training), 訓練の範囲 (training radius). The authors' reshape keeps tasks 1-7
##(filter(task < 8)); all 10 answered tasks are kept here. 1,002 national + 387 Okinawa rows.
##horiuchi_2024_f35 (Study 2, F-35 fighters): 8 tasks ("８回"), 5 attributes: 基地の場所 (8 air
##bases), 運用する主体, 防音対策 (soundproofing subsidy per household), 地域振興策, 夜間訓練の有無.
##Task 8 re-displays task 1's profiles (the questionnaire pipes A-1-* into ケース８), in the
##same left/right order: trial_repeat_of = 1 on task 8. The authors use tasks 1-7.
##F35.csv also carries `frame` (control / covid19 / historical_statement) and `opinion`, arms
##of an experiment for another project; neither appears in the deposited questionnaire, so
##where they were shown is unknown: kept as cov_frame (opinion dropped: it is only the text of
##that arm). F35_Okinawa: 196 did not consent and 55 did not finish; rows with no conjoint
##answer are omitted, partly answered respondents keep their answered tasks.
##Sample filters used by the authors and NOT applied here (columns kept to apply them):
##reCAPTCHA score >= 0.5 (cov_recaptcha_score); Study 1 Okinawa-sample respondents not living
##in Okinawa and Study 2 national respondents living abroad ("海外") are dropped by the authors
##(cov_prefecture); Study 2 requires Finished.
##Covariates, export answer text checked against the questionnaires: cov_gender (男 = male,
##女 = female), cov_age (typed years: Osprey Q2.3 - the docx shows age bands but the export
##has years - and F35 Q12.3), cov_education, cov_prefecture, cov_income (household income
##band), cov_party_id (ふだん何党を支持; "どの政党も支持していない" = supports no party, kept as
##text), cov_turnout, cov_ideology (Osprey Q7.1_1, 1 = 最も「左」 .. 7 = 最も「右」, stored as
##coded; F35 Q10.1 as answer text), cov_duration_sec. F35 only: cov_us_presence (Q5.1, US
##forces in Japan) and cov_us_presence_local (Q5.2, effect on your area), cov_frame;
##F35_Okinawa only: cov_attention_check (answer text as exported; the correct answer is not
##documented). Dropped: panel IDs rid/pid/nid/eqtid/SUPPLIER_ID/SUPNAME (re-keyed: id runs
##over the national then the Okinawa file in row order), the free-text debrief comment
##(Q25.1 / Q24.1), municipality and postal code (F35_Okinawa), dates, other attitude items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) fread(file.path(raw, f), colClasses = "character", na.strings = "", encoding = "UTF-8")[-(1:2)]
build <- function(r, T, K, outq, an, repeat_task = NA) {
  rb <- function(x) gsub("<br>", " ", x, fixed = TRUE)
  d <- rbindlist(lapply(1:T, function(t) rbindlist(lapply(1:2, function(p) {
    ans <- r[[outq[t]]]; stopifnot(all(ans %in% c("計画案A", "計画案B", NA)))
    src <- if (!is.na(repeat_task) && t == T) repeat_task else t
    x <- data.table(id = r$id, task = t, profile = p, choice = as.integer(match(ans, c("計画案A", "計画案B")) == p))
    for (k in names(an)) { x[, paste0("attr_", an[k]) := NA_character_]; x[, paste0("attrpos_", an[k]) := NA_integer_] }
    for (j in seq_len(K)) {
      nm <- rb(r[[sprintf("A-%d-%d", src, j)]]); lv <- rb(r[[sprintf("A-%d-%d-%d", src, p, j)]])
      stopifnot(all(nm %in% names(an) | is.na(nm)))
      for (k in names(an)) { w <- !is.na(nm) & nm == k
        x[w, paste0("attr_", an[k]) := lv[w]]; x[w, paste0("attrpos_", an[k]) := j] }
    }
    x }))))
  d <- d[!is.na(choice)]
  if (!is.na(repeat_task)) d[, trial_repeat_of := ifelse(task == T, as.integer(repeat_task), NA_integer_)]
  stopifnot(d[, !anyNA(.SD), .SDcols = patterns("^attr")], d[, .(sum(choice), .N), .(id, task)][, all(V1 == 1 & N == 2)])
  d
}
gen <- function(x) { stopifnot(all(x %in% c("男", "女", NA))); c("男" = "male", "女" = "female")[x] }
## Study 1: Osprey
s1 <- rbind(cbind(rd("Osprey.csv"), cov_sample = "national"), cbind(rd("Osprey_Okinawa.csv"), cov_sample = "okinawa"), fill = TRUE)
s1[, id := .I]
an1 <- c("施設の場所" = "location", "運用する主体" = "operated_by", "地域振興策" = "regional_incentives",
         "部隊の規模" = "force_size", "夜間訓練の有無" = "night_training", "訓練の範囲" = "training_range")
d1 <- build(s1, 10, 6, paste0("Q24.", seq(6, 24, 2)), an1)
c1 <- s1[, .(id, cov_sample, cov_gender = unname(gen(Q2.2)), cov_age = as.integer(Q2.3), cov_education = Q2.4,
             cov_prefecture = Q2.5, cov_income = Q2.6, cov_party_id = Q5.1, cov_turnout = Q6.1,
             cov_ideology = as.integer(Q7.1_1), cov_recaptcha_score = as.numeric(Q_RecaptchaScore),
             cov_duration_sec = as.integer(`Duration (in seconds)`))]
d1 <- merge(d1, c1, by = "id"); setorder(d1, id, task, profile)
fwrite(d1, file.path(out, "horiuchi_2024_osprey.csv"))
## Study 2: F-35
s2 <- rbind(cbind(rd("F35.csv"), cov_sample = "national"), cbind(rd("F35_Okinawa.csv"), cov_sample = "okinawa"), fill = TRUE)
s2[, id := .I]
an2 <- c("基地の場所" = "location", "運用する主体" = "operated_by", "防音対策 （対象地域の住民一戸あたり）" = "soundproofing",
         "地域振興策" = "regional_incentives", "夜間訓練の有無" = "night_training")
d2 <- build(s2, 8, 5, paste0("Q13.", seq(7, 21, 2)), an2, repeat_task = 1)
c2 <- s2[, .(id, cov_sample, cov_gender = unname(gen(Q12.2)), cov_age = as.integer(Q12.3), cov_education = Q12.4,
             cov_prefecture = Q12.5, cov_income = Q12.6, cov_party_id = Q9.1, cov_turnout = Q11.1, cov_ideology = Q10.1,
             cov_us_presence = Q5.1, cov_us_presence_local = Q5.2, cov_frame = frame, cov_attention_check = attention_check,
             cov_recaptcha_score = as.numeric(Q_RecaptchaScore), cov_duration_sec = as.integer(`Duration (in seconds)`))]
d2 <- merge(d2, c2, by = "id"); setorder(d2, id, task, profile)
fwrite(d2, file.path(out, "horiuchi_2024_f35.csv"))
