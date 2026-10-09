##Party-choice conjoint in the MAPLE I panel survey, wave 1 (six EU countries, 2019), from
##Lobo, M. C., Pannico, R., Heyne, L., Silva, T., Kartalis, Y., & Nina, S. R. (2023). MAPLE I Study -
##Public Opinion Panel Survey on European Attitudes and Political Behaviour, 2019 [Data set].
##Harvard Dataverse. No article is linked to the deposit; none was located for the conjoint.
##Replication data: Harvard Dataverse doi:10.7910/DVN/AGFZFO, CC0 1.0, no restricted files.
##Files read: wave1_2_merged.dta (Stata original of wave1_2_merged.tab; 15,535 x 315) and
##Codebook_Wave1_2_merged.docx (section "Experiments", Appendix 9 "Conjoint characteristic wording",
##weights, covariates).
##Usage: Rscript lobo_2023.R <raw dir> <output dir>
##
##Qualtrics online panels with crossed quotas (age x education x gender) in Belgium, Germany, Greece,
##Ireland, Portugal and Spain, wave 1 fielded 15 Feb - 26 Apr 2019 (codebook). Within wave 1,
##respondents were split between experiments (Experiment_w1): the 6,393 with "Conjoint" saw 2 rounds
##(task 1-2) of 2 hypothetical parties (profile 1 = Party A, 2 = Party B) described by 6 attributes.
##ONE TABLE PER COUNTRY: the six national samples are separate populations with separate panels and
##languages, and no analysis pooling them was found, so the brief's rule (pool only when the
##researchers did) gives six tables with the same layout: lobo_2023_parties_<be|de|gr|ie|pt|es>.
##Attribute text: the codebook's ENGLISH wording (Appendix 9), mapped from the stored codes "Option 1"
##.. "Option k"; respondents saw their own language (UserLanguage_w1: NL/FR in Belgium, DE, EL,
##EN-GB in Ireland, PT, ES), which is not deposited, so label_language = en everywhere:
##  attr_leader (3: more than one / one / never held a ministerial post), attr_ideology (Left /
##  Center-Left / Center-Right / Right), attr_economy (economy performed better / stayed the same /
##  performed worse during the party's last term), attr_eu (deepening / keep current level /
##  reversal of EU integration), attr_immigration (more restrictive / more open), attr_corruption
##  (fighting corruption most important / other issues more important).
##  attrpos_*: row position 1-6 (Rd_1_Order_*); randomized per respondent, identical in both
##  rounds (checked), every ordering of pairs occurs.
##Outcomes (codebook wording; the Irish English version names Ireland, the others their own country):
##  choice: "Taking into account the characteristics of these two parties, if we had legislative
##    elections in Ireland, which party would you vote for?" Party A / Party B (Q57 round 1, Q61
##    round 2); forced, no opt-out, every task answered.
##  rating: "What is the probability that you would vote for each of these parties? ... where 0 means
##    that you definitely would not vote for this party and 10 means that you definitely would vote
##    for this party" (Q58_1/Q58_2, Q62_1/Q62_2), 0-10 raw, higher = more likely.
##Dropped: 10 conjoint respondents whose attribute values are blank in the deposit (Belgium 5,
##Ireland 2, Greece/Portugal/Spain 1 each): levels not saved, so their tasks are dropped.
##Covariates: cov_gender (Q3_w1: 1 Female, 2 Male; 3 "I would prefer not to answer" -> NA), cov_age
##(Q4_w1, years), cov_age_group (Q4A_w1 labels), cov_education (Q5_w1 via the codebook's generic list
##1 Early childhood education ... 9 Doctoral or equivalent; the .dta labels use Irish names such as
##"Junior cert. education" for code 3, the codebook's "Lower secondary education" is used),
##cov_language (UserLanguage_w1), cov_duration_sec (Duration_sec_w1, whole wave-1 survey),
##cov_survey_weight (WEIGHT_RIM_w1, the within-country rim post-stratification weight on age, gender
##and education). Not kept: WEIGHT_Cell_w1 (cell weight; the codebook advises the rim weight when
##Greece is included) and WEIGHT_SB_w1 (rim weight rescaled to equalise country sample sizes,
##meaningful only for pooled analyses).
##PII in the deposit, dropped: ResponseId_w1/_w2 (Qualtrics response IDs), LocationLatitude_w1/
##LocationLongitude_w1 (Qualtrics geolocation), RecordedDate. id = row number in the deposit file.
##N per table: BE 1,543, DE 1,308, GR 728, IE 764, PT 1,041, ES 999 (6,383 in all). No paper to compare.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(haven::zap_labels(haven::read_dta(file.path(raw, "wave1_2_merged.dta"))))
x[, rowid := .I]
x <- x[Experiment_w1 == "Conjoint"]
stopifnot(nrow(x) == 6393)
x <- x[Rd_1_LEADER_A_w1 != ""]
stopifnot(nrow(x) == 6383)
lv <- list(LEADER = c("The party leader has held more than one ministerial post.", "The party leader has held one ministerial post.",
                      "The party leader has never held a ministerial post."),
           IDEOLOGY = c("Left", "Center-Left", "Center-Right", "Right"),
           ECONOMIC_PERFORMANCE = c("During the party’s last term in office, the economy of the country performed better than it did before.",
                                    "During the party’s last term in office, the economy of the country stayed the same as it was before.",
                                    "During the party’s last term in office, the economy of the country performed worse than it did before."),
           EU_POSITION = c("The party supports a deepening of EU integration.",
                           "The party does not support either a deepening nor a reversal of EU integration. It wants to keep the current level of EU integration.",
                           "The party supports a reversal of EU integration."),
           IMMIGRATION_POSITION = c("The party supports a more restrictive immigration policy.", "The party supports a more open immigration policy."),
           CORRUPTION_POSITION = c("Fighting corruption is the most important issue for the party.", "Other issues are more important than fighting corruption for the party."))
nm <- c(LEADER = "leader", IDEOLOGY = "ideology", ECONOMIC_PERFORMANCE = "economy", EU_POSITION = "eu",
        IMMIGRATION_POSITION = "immigration", CORRUPTION_POSITION = "corruption")
col <- function(stem) { v <- grep(paste0("^", stem), names(x), value = TRUE); stopifnot(length(v) == 1); x[[v]] }
opt <- function(v, levels) { k <- as.integer(sub("^Option ", "", v)); stopifnot(!anyNA(k), all(k %in% seq_along(levels))); levels[k] }
for (f in names(nm)) stopifnot(all(col(paste0("Rd_1_Order_", f)) == col(paste0("Rd_2_Order_", f))))
ch <- list(x$Q57_w1, x$Q61_w1); rt <- list(list(x$Q58_1_w1, x$Q58_2_w1), list(x$Q62_1_w1, x$Q62_2_w1))
rows <- list()
for (t in 1:2) for (p in 1:2) {
  stopifnot(all(ch[[t]] %in% 1:2), all(rt[[t]][[p]] %in% 0:10))
  d <- data.table(rowid = x$rowid, task = t, profile = p, choice = as.integer(ch[[t]] == p), rating = as.integer(rt[[t]][[p]]))
  for (f in names(nm)) {
    d[, paste0("attr_", nm[[f]]) := opt(col(paste0("Rd_", t, "_", f, "_", c("A", "B")[p])), lv[[f]])]
  }
  for (f in names(nm)) d[, paste0("attrpos_", nm[[f]]) := as.integer(col(paste0("Rd_1_Order_", f)))]
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows)
stopifnot(d[, sum(choice), .(rowid, task)][, all(V1 == 1)])
edu <- c("Early childhood education", "Primary education", "Lower secondary education", "Upper secondary education",
         "Post-secondary non tertiary education", "Short-cycle tertiary education", "Bachelor or equivalent",
         "Master or equivalent", "Doctoral or equivalent")
stopifnot(all(x$Q3_w1 %in% 1:3), all(x$Q5_w1 %in% 1:9), all(x$Q4A_w1 %in% 1:3))
cv <- x[, .(rowid, country = Country, cov_gender = c("female", "male", NA)[Q3_w1], cov_age = as.integer(Q4_w1),
            cov_age_group = c("18-34", "35-54", "55+")[Q4A_w1], cov_education = edu[Q5_w1], cov_language = UserLanguage_w1,
            cov_duration_sec = as.integer(Duration_sec_w1), cov_survey_weight = WEIGHT_RIM_w1)]
stopifnot(!anyNA(cv$cov_survey_weight))
d <- merge(d, cv, by = "rowid")
d[, id := rowid][, rowid := NULL]
cc <- c(Belgium = "be", Germany = "de", Greece = "gr", Ireland = "ie", Portugal = "pt", Spain = "es")
stopifnot(all(d$country %in% names(cc)))
for (k in names(cc)) {
  o <- d[country == k][, country := NULL]
  setcolorder(o, c("id", "task", "profile", "choice", "rating"))
  setorder(o, id, task, profile)
  fwrite(o, file.path(out, paste0("lobo_2023_parties_", cc[[k]], ".csv")))
}
