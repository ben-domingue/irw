##AI-enhanced military technology trust conjoint (US Army ROTC cadets) from the deposit of
##Lushenko, P. (2025). AI, trust, and the war room: Evidence from a conjoint experiment in the US
##military. Cambridge Forum on AI: Law and Governance. https://doi.org/10.1017/cfl.2025.10019
##(that article analyses the OFFICERS file only; the cadet sample is the one in Lushenko, P., &
##Sparrow, R. (2024). Artificial intelligence and U.S. military cadets' attitudes about future
##war. Armed Forces & Society, https://doi.org/10.1177/0095327X241284264, not open access and not
##read, so whether it reports this conjoint is unconfirmed).
##Replication data: Harvard Dataverse doi:10.7910/DVN/KDSDXC, CC0 1.0, no restricted files.
##File read: cadets.csv (Dataverse "original format" download of cadets.tab; a Qualtrics export
##with 3 header rows: names, question text, import IDs). officers.csv (95 responses) is NOT
##built: below the 100-respondent floor.
##Usage: Rscript lushenko_2025.R <raw dir> <output dir>
##
##474 completed responses (Qualtrics, 10 Nov - 4 Dec 2023, anonymous link). Each saw 9 single
##profiles of an AI-enabled military technology (Qualtrics conjoint fields F-<task>-<attr> =
##attribute name, F-<task>-1-<attr> = level), 9 attributes, all shown, in the same fixed order
##for every respondent and task (Platform, Purpose, Precision, Autonomy, Civilian, Friendly,
##Contribution, Regulation, Other; checked). Article (same instrument, officers): "Consider a
##large war involving the United States, in which US Army forces adopt a new AI-enabled military
##technology against a peer adversary. ... This new capability is used under the following
##circumstances and with the following outcomes."; levels drawn uniformly ("a uniform
##distribution of randomization"), no restrictions mentioned.
##  rating = conjoint_dv_<task>_1: "Do you trust partnering with this AI-enhanced military
##           technology when it is used under these conditions?" (export question-text row),
##           1-5, stored raw. The export holds codes only; the anchors are from the article
##           describing the same item for the officers: "one denotes 'strong distrust' and five
##           denotes 'strong trust'" (higher = more trust).
##The repeated fixed reliability scenario before and after the conjoint (reliability_dv_1/_2)
##is dropped: its attributes are not in the export. 3 respondents have ratings for all 9 tasks
##but no saved attribute levels (all F- fields blank): dropped (471 respondents kept).
##Level text kept as exported, trailing spaces trimmed ("20-22 US Army soldiers ").
##Covariates: the export holds numeric codes with no value labels and the instrument is not
##deposited, so they keep their codes with a _code suffix: cov_gender_code (Q1 "What is your
##sex?"), cov_age_group_code (Q2 "How old are you?", banded), cov_race_code (Q3),
##cov_education_code (Q4), cov_party_code (Q20 "Generally speaking, do you usually think of
##yourself as a...?"), cov_ideology_code (Q21), cov_military_role_code (Q28 "Are you a Cadet,
##Enlisted, or Commissioned?"); cov_duration_sec = Qualtrics "Duration (in seconds)" (whole
##survey). Dropped: Respondent Group (a between-subject scenario arm asked AFTER the conjoint,
##Q8/Q9, not a conjoint factor), post-conjoint attitude items, the free-text Q6, timers,
##Q_RecaptchaScore and the Qualtrics metadata. IP address, latitude/longitude, recipient name/
##email and external reference are present as columns but masked ("*******") in the deposit;
##ResponseId (Qualtrics) dropped, ids re-keyed 1..N in file order. No survey weight. No attention
##check item in the export besides the commitment questions Q5/Q7 (not kept).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read.csv(file.path(raw, "cadets.csv"), colClasses = "character", check.names = FALSE, fileEncoding = "UTF-8-BOM")
s <- as.data.table(s[-(1:2), ])  # drop the question-text and import-ID rows
stopifnot(nrow(s) == 474, all(s$Finished == "1"))
s[, id := seq_len(.N)]
nm <- c(Platform = "platform", Purpose = "purpose", Precision = "precision", Autonomy = "autonomy", Civilian = "civilian_casualties",
        Friendly = "friendly_forces_saved", Contribution = "mission_contribution", Regulation = "regulation", Other = "other_adopters")
L <- vector("list", 9)
for (t in 1:9) {
  x <- data.table(id = s$id, task = t, profile = 1L, rating = as.integer(s[[sprintf("conjoint_dv_%d_1", t)]]))
  for (j in 1:9) {
    an <- s[[sprintf("F-%d-%d", t, j)]]
    stopifnot(all(an %in% c(names(nm)[j], "")))
    x[, paste0("attr_", nm[[j]]) := trimws(s[[sprintf("F-%d-1-%d", t, j)]])]
  }
  L[[t]] <- x
}
d <- rbindlist(L)
miss <- d[, any(attr_platform == ""), id][V1 == TRUE, id]
stopifnot(length(miss) == 3, d[!id %in% miss, all(.SD != ""), .SDcols = patterns("^attr_")])
d <- d[!id %in% miss]
stopifnot(all(d$rating %in% 1:5))
cv <- c(Q1 = "gender_code", Q2 = "age_group_code", Q3 = "race_code", Q4 = "education_code", Q20 = "party_code",
        Q21 = "ideology_code", Q28 = "military_role_code", "Duration (in seconds)" = "duration_sec")
cvd <- s[, c("id", names(cv)), with = FALSE]
for (v in names(cv)) set(cvd, j = v, value = as.integer(fifelse(cvd[[v]] == "", NA_character_, cvd[[v]])))
setnames(cvd, names(cv), paste0("cov_", cv))
d <- merge(d, cvd, by = "id")
d[, id := match(id, sort(unique(id)))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lushenko_2025_ai_trust_cadets.csv"))
