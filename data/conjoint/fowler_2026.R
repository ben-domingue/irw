##Two sequential discrete choice experiments on plug-in electric vehicle (PEV) smart charging in Belgium, from
##the replication package of "From Purchase to Participation: Sequential Choice Experiments on PEV
##Smart-Charging" (Fowler, van Passel & Lizin; manuscript submitted to Utilities Policy; no article DOI).
##Deposit: Mendeley Data doi:10.17632/pgrgnctxjf (version 2), CC BY 4.0. Files read: merged_data.csv
##(Experiment 1, one row per respondent x task, the authors' own join of the Qualtrics export to the design),
##merged_data_with_class_probabilities.csv (Experiment 2, see below), "File for merginge_big_data_8choices.csv"
##and "File4merging_4 choices_ex2.csv" (design files), the Qualtrics .qsf (level wording) and the authors'
##cleaning/analysis scripts (read as text, never run).
##Usage: Rscript fowler_2026.R <dir holding the files above> <output dir>
##
##TABLE 1, fowler_2026_pev_charger_purchase (this script also writes fowler_2026_pev_charger_service, below).
##Experiment 1: "Suppose you recently bought an electric car and you have a basic charger that does not have
##advanced features. Please indicate your preference for a new electric car charger. You can choose between two
##hypothetical private residential chargers, or you can keep your current charger" (qsf, tasks "(j/8)").
##Belgian drivers (18+, licence holders; Flanders, Wallonia, Brussels), online panel, July 2024; questionnaire in
##Dutch, French or English. 8 tasks x 2 chargers (Charger 1 = profile 1, Charger 2 = profile 2), 6 attributes:
##smart charging (none / by a smart home management system / by the energy retailer / by yourself using your
##smartphone), solar charging (No/Yes), two-way charging (None / Vehicle to home / Vehicle to home and grid),
##peak electricity-use management (No/Yes), annual reward on the electric bill, price of charger (EUR, with
##installation). Third alternative "Use your current charger" (no advanced features, no new purchase, no reward) is
##a fixed outside option without levels: opt_out = yes, no profile row, choice = 0 on both profiles when chosen
##(choice_variable 3: 1,716 of 7,240 tasks before filtering).
##Level text: the design file stores one-hot dummies (shms, retailer, self, smartnone; solar/nosolar;
##v2h/v2hg/notwoway; peak/nopeak) and numeric reward/price. Displayed wording taken from the .qsf example cards
##(English); the .qsf example cards were compared with the design file for set 1,
##tasks 1 and 2 (match level for level), and the design columns of every respondent-task are checked in the
##script against "File for merginge_big_data_8choices.csv" (stopifnot). Reward is shown as "EUR n annually (EUR 10n total over ten years)" and the
##smart-home-management level carries its note "(would require existing or additional investment in the smart
##home system)" on the card; both are stored in the shortened form "By a smart home management system".
##Fixed blocked design: 5 versions of 8 tasks, each respondent one version (trial_version = the authors' `set`).
##Restrictions: none documented; task order = (j/8) number in the question text, the design `choice` index.
##Sample: the file holds 905 respondents; the authors' validity flag ex1_junk (age/bill/drive/meter implausible
##or straight-lining) leaves 769 = the "769 valid responses" of the deposit description; the table keeps
##ex1_junk == 0 as the authors do (136 dropped).
##Covariates: age (kept only if a whole number 16-110, else NA: the file has 0 and 3200), cov_woman (the authors'
##0/1 dummy; not a three-way gender question so not cov_gender), education (answer text, English), income (household
##band text, EUR), region, language, drives an EV, daily drive (km), duration in seconds. Dropped: Qualtrics
##response ids, reCAPTCHA / RelevantID fraud scores, timestamps, free text, all derived scales and dummies.
##No survey weight. Respondent ids are the file's respondent.id re-keyed to integers.

##TABLE 2, fowler_2026_pev_charger_service. Experiment 2, asked of the same respondents after Experiment 1:
##"Suppose you own an electric car and your home is already equipped with a charger that has smart charging and
##two-way charging (vehicle to home and grid) capabilities. You will now decide whether to allow your energy
##retailer to control your charger by choosing a smart charging service agreement. You can also choose not to
##accept either service agreement, which means that you'll control the charger yourself" (qsf, tasks "(j/4)").
##4 tasks x 2 service agreements (Service agreement 1 = profile 1, 2 = profile 2), 5 attributes: minimum battery
##level (None (0%) / 10% / 30% / 50%, each with its range for a Nissan Leaf), portable power bank (Yes/No),
##emergency roadside charging assistance (Yes/No), charging data security (Yes/No), monthly fee (EUR 0/10/30/50,
##shown with the yearly amount). Third alternative "No service agreement" (no levels; no fee) = opt-out
##(choice_variable 3). Fixed blocked design: 5 versions x 4 tasks (trial_version = the first number of the
##authors' set_variable; it differs from Experiment 1's version for a respondent). Task = the (j/4) number.
##Source: merged_data_with_class_probabilities.csv, which repeats each respondent's 4 Experiment 2 rows 8 times
##(a join with the 8 Experiment 1 tasks): the duplicates are collapsed (identical in every kept column; checked)
##and the design columns are checked against "File4merging_4 choices_ex2.csv". The file holds the 769
##respondents with ex1_junk == 0 only; the 10 of them flagged ex2_junk (straight-lining in Experiment 2) are kept
##and flagged in cov_ex2_straightline_flag, as the authors' Experiment 2 scripts do not filter them.
##Same covariates as Table 1 (from merged_data.csv, same respondent ids).
##Level text from the .qsf example cards (English) as for Table 1. Displayed fee wording: "EUR 10 per month (EUR
##120 per year)"; minimum battery wording keeps the card's "(28 km range for a Nissan Leaf, for example)".
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
## the exports are Windows-1252 with some characters written as literal "<U+0092>" (apostrophe) / "<U+00A0>"
## (no-break space) by R: read as Latin-1, convert to UTF-8, repair those
fx <- function(x) gsub("<U+00A0>", " ", gsub("<U+0092>", "'", enc2utf8(x), fixed = TRUE), fixed = TRUE)
rd <- function(f) { z <- fread(file.path(raw, f), encoding = "Latin-1")
  cc <- names(z)[sapply(z, is.character)]; z[, (cc) := lapply(.SD, fx), .SDcols = cc]; z }

## ---- Experiment 1 ----
d <- rd("merged_data.csv")
d <- d[ex1_junk == 0]
des <- rd("File for merginge_big_data_8choices.csv"); setnames(des, tolower(names(des)))
ck <- merge(d[, .(set = set.x, choice, shms_a, retailer_a, self_a, smartnone_a, solar_b, v2h_b, v2hg_b, peak_a, reward_a, reward_b, price_a, price_b)],
            des[, .(set, choice, d_shms = shms_a, d_ret = retailer_a, d_self = self_a, d_none = smartnone_a, d_solb = solar_b, d_v2hb = v2h_b,
                    d_v2hgb = v2hg_b, d_peak = peak_a, d_ra = reward_a, d_rb = reward_b, d_pa = price_a, d_pb = price_b)], by = c("set", "choice"))
stopifnot(nrow(ck) == nrow(d), all(ck$shms_a == ck$d_shms), all(ck$retailer_a == ck$d_ret), all(ck$self_a == ck$d_self),
          all(ck$smartnone_a == ck$d_none), all(ck$solar_b == ck$d_solb), all(ck$v2h_b == ck$d_v2hb), all(ck$v2hg_b == ck$d_v2hgb),
          all(ck$peak_a == ck$d_peak), all(ck$reward_a == ck$d_ra), all(ck$reward_b == ck$d_rb), all(ck$price_a == ck$d_pa), all(ck$price_b == ck$d_pb))
stopifnot(d[, uniqueN(respondent.id) == 769], d[, .N, respondent.id][, all(N == 8)])
smart <- function(x) {
  s <- cbind(shms = x$shms, retailer = x$retailer, self = x$self, smartnone = x$smartnone)
  stopifnot(all(rowSums(s) == 1))
  c("By a smart home management system", "By your energy retailer", "By yourself using your smartphone",
    "None. The car will begin charging once plugged in.")[max.col(s, ties.method = "first")]
}
two <- function(x) { s <- cbind(x$notwoway, x$v2h, x$v2hg); stopifnot(all(rowSums(s) == 1))
  c("None", "Vehicle to home", "Vehicle to home and grid")[max.col(s, ties.method = "first")] }
mk <- function(suf) {
  g <- function(n) d[[paste0(n, "_", suf)]]
  x <- list(shms = g("shms"), retailer = g("retailer"), self = g("self"), smartnone = g("smartnone"),
            notwoway = g("notwoway"), v2h = g("v2h"), v2hg = g("v2hg"))
  stopifnot(all(g("solar") + g("nosolar") == 1), all(g("peak") + g("nopeak") == 1))
  data.table(id = as.integer(factor(d$respondent.id)), task = as.integer(d$choice),
             profile = if (suf == "a") 1L else 2L,
             choice = as.integer(d$choice_variable == if (suf == "a") 1L else 2L),
             attr_smart_charging = smart(x), attr_solar_charging = ifelse(g("solar") == 1, "Yes", "No"),
             attr_two_way_charging = two(x), attr_peak_management = ifelse(g("peak") == 1, "Yes", "No"),
             attr_reward = sprintf("EUR %d annually (EUR %d total over ten years)", as.integer(g("reward")), 10L * as.integer(g("reward"))),
             attr_price = sprintf("EUR %d", as.integer(g("price"))),
             trial_version = as.integer(d$set.x))
}
e1 <- rbind(mk("a"), mk("b"))
cv <- function(x) { x <- as.numeric(x); ifelse(x >= 16 & x <= 110 & x == round(x), x, NA) }
cov1 <- data.table(id = as.integer(factor(d$respondent.id)),
  cov_age = as.integer(cv(d$age)), cov_woman = as.integer(d$woman),
  cov_education = fx(d$education), cov_income_band = trimws(d$income), cov_region = d$region,
  cov_language = d[["choose your language | kies uw taal | choisissez votre langue"]],
  cov_drives_ev = d[["do you currently drive an electric car?"]],
  cov_daily_drive_km = as.numeric(d$daily_drive), cov_duration_sec = as.integer(d[["duration (in seconds)"]]))
cov1 <- unique(cov1, by = "id")
e1 <- merge(e1, cov1, by = "id")
stopifnot(e1[, sum(choice), .(id, task)][, all(V1 <= 1)], !anyNA(e1$attr_price))
setorder(e1, id, task, profile)
fwrite(e1, file.path(out, "fowler_2026_pev_charger_purchase.csv"))

## ---- Experiment 2 ----
x <- rd("merged_data_with_class_probabilities.csv")
des2 <- rd("File4merging_4 choices_ex2.csv"); setnames(des2, tolower(names(des2)))
cols <- c("respondent.id", "set_variable", "choice_variable", "minimum_a", "minimum_b", "portable_a", "portable_b",
          "no_portable_a", "no_portable_b", "emergency_a", "emergency_b", "no_emergency_a", "no_emergency_b",
          "privacy_a", "privacy_b", "no_privacy_a", "no_privacy_b", "fee_a", "fee_b")
u <- unique(x[, ..cols])
stopifnot(nrow(u) == 769 * 4, u[, .N, respondent.id][, all(N == 4)], setequal(u$respondent.id, d$respondent.id))
u[, c("ver", "task") := tstrsplit(set_variable, "_", type.convert = TRUE)]
chk <- merge(u, des2[, .(ver = set, task = choice, m_a = minimum_a, m_b = minimum_b, f_a = fee_a, f_b = fee_b, p_a = portable_a, p_b = portable_b)],
             by = c("ver", "task"))
stopifnot(nrow(chk) == nrow(u), all(chk$minimum_a == chk$m_a), all(chk$minimum_b == chk$m_b), all(chk$fee_a == chk$f_a),
          all(chk$fee_b == chk$f_b), all(chk$portable_a == chk$p_a), all(chk$portable_b == chk$p_b))
mn <- c("0" = "None (0%)", "10" = "10% (28 km range for a Nissan Leaf, for example)",
        "30" = "30% (83 km range for a Nissan Leaf, for example)", "50" = "50% (138 km range for a Nissan Leaf, for example)")
yn <- function(y, n) { stopifnot(all(y + n == 1)); ifelse(y == 1, "Yes", "No") }
mk2 <- function(suf) {
  g <- function(n) u[[paste0(n, "_", suf)]]
  fee <- as.integer(g("fee"))
  data.table(id = as.integer(factor(u$respondent.id, levels = sort(unique(d$respondent.id)))), task = as.integer(u$task),
             profile = if (suf == "a") 1L else 2L,
             choice = as.integer(u$choice_variable == if (suf == "a") 1L else 2L),
             attr_minimum_battery_level = unname(mn[as.character(g("minimum"))]),
             attr_portable_power_bank = yn(g("portable"), g("no_portable")),
             attr_emergency_roadside_assistance = yn(g("emergency"), g("no_emergency")),
             attr_charging_data_security = yn(g("privacy"), g("no_privacy")),
             attr_monthly_fee = sprintf("EUR %d per month (EUR %d per year)", fee, 12L * fee),
             trial_version = as.integer(u$ver))
}
e2 <- rbind(mk2("a"), mk2("b"))
stopifnot(!anyNA(e2$attr_minimum_battery_level), !anyNA(e2$attr_monthly_fee))
fl <- unique(d[, .(id = as.integer(factor(respondent.id)), cov_ex2_straightline_flag = as.integer(ex2_junk))], by = "id")
e2 <- merge(e2, cov1, by = "id"); e2 <- merge(e2, fl, by = "id")
stopifnot(e2[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(e2, id, task, profile)
fwrite(e2, file.path(out, "fowler_2026_pev_charger_service.csv"))
