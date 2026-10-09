##Military-intervention conjoint (US and Turkey, January-February 2020) from
##Kiratli, O. S. (2024). Policy objective of military intervention and public attitudes: A conjoint
##experiment from US and Turkey. Political Behavior, 46(2), 1257-1279.
##https://doi.org/10.1007/s11109-023-09871-0
##Replication data: Harvard Dataverse doi:10.7910/DVN/TGUADW, CC0 1.0, no restricted files.
##File read: warspobe-small.dta (Dataverse "original format" download of warspobe-small.tab).
##Read as text only: wars-do.do. Level text and wording from the open-access article (Table 1,
##Fig. 1 = US screen) and its online appendix (ESM1 docx: A-I = Turkish screen, A-II variables).
##Usage: Rscript kiratli_2024.R <dir holding warspobe-small.dta> <output dir>
##
##Two samples: US (1,490 MTurk workers via Qualtrics) and Turkey (1,002 Cint panelists); both
##counts match the article. The author analyses the countries separately (every model in the .do
##file is run `if country2==...`) and the Turkish sample saw Turkish text with a Turkish actor, so
##there are TWO tables: kiratli_2024_intervention_us and kiratli_2024_intervention_turkey.
##Each respondent saw 6 pairs of military-operation proposals (A = profile 1, B = profile 2) with
##6 attributes. Task and profile come from the source's `oper` code = task*10 + proposal (11..62;
##every respondent has all 12 codes and exactly one chosen proposal per task).
##Outcome: choice. US: "If you had to choose only one, which of these two military operations
##would you approve?" (Fig. 1). Turkey: "Sizce Türkiye hangi kriz için askeri birlik
##göndermelidir?" (A-I; "In your opinion, for which crisis should Turkey send troops?"). Forced
##choice: the article says no "neither" option was offered. No rating.
##Attributes (data value labels are abbreviations; text below is the displayed English text from
##Fig. 1 where it shows a level, else Table 1):
##  attr_objective: the clause that follows "Country A/B has deployed troops to a neighboring
##    country, which is an ally of the US/Turkey." (that common prefix is not stored):
##    1 IPC = "The operation aims to overthrow the government in the aggressor target country."
##    2 FPR = "The operation aims to expel the target country from the invaded territory."
##    3 Peace = "The operation aims to maintain peace between two sides."
##    4 HI = "The operation aims to protect civilians in the conflict zone, many of whom are women
##       and children."
##  attr_support ("Operation supported by"): US "US government only" / "US government plus UN" (Fig. 1),
##    "US government plus NATO allies" / "US government plus opposition party" (Table 1). Turkey's
##    screen reads "Hükümet artı ..." ("Government plus ...", A-I), so the Turkey table stores
##    "Government only" / "Government plus UN" / "Government plus NATO allies" / "Government plus
##    opposition parties" (Table 1: "opposition party (parties in Turkey)").
##  attr_regime ("Attacking country's regime"): Democracy / Partial democracy / Authoritarian
##  attr_religion ("Attacking country's religion"): Muslim / Christian / Buddhist
##  attr_military ("Attacking country's military power"): Strong / Weak
##  attr_mode ("Mode of operation"): Ground troops only / Air force only / Both ground troops and air force
##The Turkey table's level text is therefore English (the Turkish instrument is not deposited;
##A-I shows only some Turkish levels, e.g. "Yarı demokrasi", "Zayıf", "Hükümet artı Birleşmiş Milletler").
##Randomization: "fully randomized ... approximately uniformly distributed" (article p. 1268).
##Attribute order: the US screen lists objective, support, regime, religion, military, mode; the
##Turkish screen lists objective, regime, religion, military, support, mode; whether order was
##randomized is not stated and is not in the data.
##Covariates: cov_age (years); cov_gender from sex (value labels 0 Female, 1 Male; A-II agrees);
##cov_education_code keeps codes: the .dta labels (US: 1 Less than high school, 2 Incomplete high
##school, 3 Some college/university (no 4-year degree), 4 High school graduate, 5 College graduate,
##6 Post-graduate) conflict with A-II ("from 1=No formal education, to 6=Master's/PhD"), and Turkey's
##codes 1-9 have no labels (A-II: "1=No formal education, to 9=Master's/PhD"); cov_fp_* (Q18_*,
##1 Strongly Disagree .. 5 Strongly Agree): selfish = Q18_1 "This country would be better off if we
##just re[...]" (label truncated in source), own_interests Q18_2, cooperate Q18_3, influence Q18_5,
##military_strength Q18_6, strike_first Q18_7, learn_others Q18_8 (wording A-II, US/Turkey);
##cov_govt_fp_success (Q19_1, 1 Very unsuccessful .. 5 Very successful); cov_polint_code (1 Very
##interested, 2 Slightly, 3 Moderately, 4 Not at all; label order as in source); cov_ideology
##(1 = extreme left .. 10 = extreme right; 12 = Don't know per value labels); US only: cov_party_id7
##as value-label text (Strong Democrat .. Strong Republican, Don't know).
##Dropped: ResponseID (Qualtrics IDs; re-keyed to integers in source order), the author's derived
##rep/dem/party2/ideo2 dummies, country/country2 (one table per country) and `secim` (unlabelled,
##varies within respondent). No survey weight in the deposit. No repeated task.
##Spot check: the A-III unadjusted marginal means (e.g. US IPC 0.355, Humanitarian 0.620; Turkey
##Muslim 0.587) reproduce from these tables.
suppressMessages({library(haven); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "warspobe-small.dta"))
lab <- function(x) { l <- attr(x, "labels"); setNames(names(l), l)[as.character(zap_labels(x))] }
d <- data.table(rid = k$ResponseID, country = k$country, task = as.integer(k$oper) %/% 10L,
                profile = as.integer(k$oper) %% 10L, choice = as.integer(k$choice))
lv <- function(x, l) { x <- as.integer(zap_labels(x)); stopifnot(all(x %in% seq_along(l))); l[x] }
d[, attr_objective := lv(k$xob, c("The operation aims to overthrow the government in the aggressor target country.",
                                  "The operation aims to expel the target country from the invaded territory.",
                                  "The operation aims to maintain peace between two sides.",
                                  "The operation aims to protect civilians in the conflict zone, many of whom are women and children."))]
stopifnot(identical(unname(attr(k$xob, "labels")), c(1, 2, 3, 4)), names(attr(k$xob, "labels")) == c("IPC", "FPR", "Peace", "HI"))
stopifnot(names(attr(k$xsup, "labels")) == c("Only gov", "Gov plus NATO allies", "Gov plus UN", "Gov plus opposition party"))
d[, attr_support := lv(k$xsup, c("government only", "government plus NATO allies", "government plus UN", "government plus opposition party"))]
d[country == "US", attr_support := paste("US", attr_support)]
d[country == "Turkey", attr_support := sub("^government", "Government", sub("opposition party$", "opposition parties", attr_support))]
stopifnot(names(attr(k$xreg, "labels")) == c("Authoritarian", "Democracy", "Partial democracy"),
          names(attr(k$xrel, "labels")) == c("Buddhist", "Christian", "Muslim"),
          names(attr(k$xmil, "labels")) == c("Strong", "Weak"),
          names(attr(k$xmod, "labels")) == c("Ground troops only", "Air force only", "Both ground and air"))
d[, attr_regime := lv(k$xreg, c("Authoritarian", "Democracy", "Partial democracy"))]
d[, attr_religion := lv(k$xrel, c("Buddhist", "Christian", "Muslim"))]
d[, attr_military := lv(k$xmil, c("Strong", "Weak"))]
d[, attr_mode := lv(k$xmod, c("Ground troops only", "Air force only", "Both ground troops and air force"))]
d[, cov_age := as.integer(k$age)]
stopifnot(all(k$sex %in% 0:1)); d[, cov_gender := c("female", "male")[as.integer(k$sex) + 1L]]
d[, cov_education_code := as.integer(k$education)]
q <- c(selfish = "Q18_1", own_interests = "Q18_2", cooperate = "Q18_3", influence = "Q18_5",
       military_strength = "Q18_6", strike_first = "Q18_7", learn_others = "Q18_8")
for (n in names(q)) d[, paste0("cov_fp_", n) := as.integer(k[[q[n]]])]
d[, cov_govt_fp_success := as.integer(k$Q19_1)]
d[, cov_polint_code := as.integer(k$polint)]
d[, cov_ideology := as.integer(k$ideo)]
d[, cov_party_id7 := lab(k$partisan)]
stopifnot(d[, uniqueN(country), rid][, all(V1 == 1)], d[, .N, rid][, all(N == 12)],
          d[, sum(choice), .(rid, task)][, all(V1 == 1)], !anyDuplicated(d[, .(rid, task, profile)]))
for (cc in c("US", "Turkey")) {
  x <- d[country == cc]
  x[, id := match(rid, unique(rid))]
  x[, c("rid", "country") := NULL]
  if (cc == "Turkey") { stopifnot(all(is.na(x$cov_party_id7))); x[, cov_party_id7 := NULL] }
  setcolorder(x, c("id", "task", "profile"))
  setorder(x, id, task, profile)
  fwrite(x, file.path(out, paste0("kiratli_2024_intervention_", tolower(cc), ".csv")))
}
