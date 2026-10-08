##Populist-candidate conjoints (Germany 2017 and 2018) from
##Neuner, F. G., & Wratil, C. (2022). The populist marketplace: Unpacking the role of "thin"
##and "thick" ideology. Political Behavior, 44(2), 551-574.
##https://doi.org/10.1007/s11109-020-09629-y
##Replication data: Harvard Dataverse doi:10.7910/DVN/Z66XXP, CC0 1.0, no restricted files.
##Files read: data_conjoint_2017_R.dta and data_conjoint_2018_R.dta (Dataverse "original
##format" downloads). Level text = the German Stata value labels (as displayed); design facts
##from the article (author manuscript, UCL Discovery 10103131) and the authors' R scripts
##(read as text, not run).
##Usage: Rscript neuner_2022.R <raw dir> <output dir>
##
##Payback Online Panel samples of German voting-eligible adults. Each respondent saw 5 pairs
##of fictitious candidate profiles (no party labels) and chose "which candidate in each pair they
##would rather cast their vote for" (article paraphrase; the German wording is only in an
##appendix screenshot). Forced choice, no opt-out. THREE TABLES (separate fieldings / attribute
##sets, analysed separately by the authors):
##  neuner_2022_populist_candidates_2017: 2017 wave 3 (March-Sept 2017), n = 2,371. Attributes:
##     positions on refugees, EU, taxes on the rich, free trade; first and second priority
##     (13 priorities).
##  neuner_2022_populist_candidates_2018: 2018 "exact replication" arm (May/June 2018, half of
##     n = 3,427): same attributes and levels as 2017.
##  neuner_2022_populist_amended_2018: 2018 "amended" arm (the other half): positions on euro-
##     area economic cooperation, social housing investment, tariffs, referendums; first and
##     second priority (13 priorities: "Den Machtmissbrauch der Parteien beenden" replaces
##     "Direkte Demokratie stärken (z.B. Volksentscheide)", which became the referendums position).
##The 2018 arm is identified by which attribute columns are filled (each respondent is in one
##arm only; checked).
##Task and profile: the deposit has no task column. Rows come in respondent blocks of 10
##alternating kandidat A/B (A = left, profile 1); task t = rows 2t-1, 2t, as in the authors' own
##carryover analysis (choice_task). Verified: every pair has exactly one chosen profile. One
##2018 respondent with only 7 rows is dropped.
##Restrictions (article fn. 4 / p. 18): first and second priority are drawn from the same list
##and cannot be identical (never equal in the data). Attribute order not documented.
##One amended-arm euro level is truncated in the Stata label ("...der Euro-Lände"); completed
##to "Ist für eine viel schwächere wirtschaftspolitische Zusammenarbeit der Euro-Länder".
##Covariates: cov_survey_weight (weight_wave3 / weightB); cov_vote_intention (party label text);
##(2017 label "GrÃ¼ne" repaired to "Grüne"); cov_thin_pop_1..8 (eight thin-populism items, 1-4; item wording and direction are only in
##the online appendix, not deposited); cov_eu_membership, cov_eu_unification, cov_globalization,
##cov_refugees_war, cov_immigrants, cov_tax_rich (thick-populism items, 1 = stimme überhaupt
##nicht zu .. 4 = stimme voll und ganz zu).
##Dropped: panel ids (lfdn_W3 / lfdn, re-keyed per table), the authors' derived binary
##priority dummies.
##N: 2,371 (2017) matches the article; 2018 arms 1,712 (replication) + 1,714 (amended) + 1 dropped
##= the article's 3,427.
##Spot check (weighted choice shares, 2017): anti-elite priority "Die politische Elite entmachten"
##0.38 vs 0.46-0.55 for other priorities; "Austritt Deutschlands aus der EU" 0.38; "Aufnahme
##sehr vieler neuer Flüchtlinge" 0.37: the article's headline pattern (anti-elitism and EU exit
##penalised; anti-immigration positions not).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x) { l <- attr(x, "labels"); y <- names(l)[match(as.integer(x), l)]; y[is.na(x)] <- NA; y }
build <- function(s, idv, pos, wt, popv, nm) {
  s <- copy(s); setnames(s, idv, "rid")
  s[, r := seq_len(.N), rid]
  stopifnot(s[, all(kandidat == c("A", "B")[2 - r %% 2])])
  d <- data.table(rid = s$rid, task = (s$r + 1L) %/% 2L, profile = 2L - s$r %% 2L, choice = as.integer(s$praeferenz))
  for (v in names(pos)) { x <- lab(s[[pos[[v]]]]); stopifnot(!anyNA(x)); d[, paste0("attr_", v) := x] }
  d[, attr_priority_first := lab(s$schwerpunkt1)][, attr_priority_second := lab(s$schwerpunkt2)]
  stopifnot(!anyNA(d$attr_priority_first), !anyNA(d$attr_priority_second), d[, all(attr_priority_first != attr_priority_second)],
            d[, sum(choice), .(rid, task)][, all(V1 == 1)])
  d[, cov_survey_weight := s[[wt]]][, cov_vote_intention := lab(s$sonntagsfrage)]
  d[, cov_vote_intention := gsub("\u00c3\u00bc", "\u00fc", cov_vote_intention)]  # 2017 label "GrÃ¼ne" is double-encoded
  for (i in 1:8) d[, paste0("cov_thin_pop_", i) := as.integer(s[[popv[i]]])]
  thick <- c(eu_membership = "europ_union_mitgliedschaft", eu_unification = "europ_vereinigung", globalization = "globalisierung",
             refugees_war = "fluechtlinge_krieg", immigrants = "einwanderer", tax_rich = "reiche")
  for (v in names(thick)) d[, paste0("cov_", v) := as.integer(s[[thick[[v]]]])]
  d[, id := as.integer(factor(rid))][, rid := NULL]
  setcolorder(d, c("id", "task", "profile")); setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(nm, ".csv")))
}
p1 <- c(refugees = "fluechtlinge", eu = "EU", taxes = "steuern", trade = "freihandel")
s17 <- as.data.table(read_dta(file.path(raw, "data_conjoint_2017_R.dta")))
stopifnot(s17[, .N, lfdn_W3][, all(N == 10)])
pop17 <- c("pop1_volksabstimmungen", "pop2_buerger_vs_politiker", "pop3_einfacher_buerger", "pop4_parteien",
           "pop5_responsivitaet_bundestag", "pop6_einigkeit_buerger", "pop7_buerger_vs_politiker2", "pop8_kompromiss_verrat")
build(s17, "lfdn_W3", p1, "weight_wave3", pop17, "neuner_2022_populist_candidates_2017")
s18 <- as.data.table(read_dta(file.path(raw, "data_conjoint_2018_R.dta")))
s18 <- s18[lfdn %in% s18[, .N, lfdn][N == 10]$lfdn]
s18[, arm := fifelse(is.na(fluechtlinge), "amended", "replication")]
stopifnot(s18[, uniqueN(arm), lfdn][, all(V1 == 1)],
          s18[arm == "replication", !anyNA(EU) & all(is.na(euro) & is.na(wohnung) & is.na(zoelle) & is.na(dirdem))],
          s18[arm == "amended", all(is.na(EU) & is.na(steuern) & is.na(freihandel)) & !anyNA(euro)])
el <- attr(s18$euro, "labels"); names(el)[names(el) == "Ist für eine viel schwächere wirtschaftspolitische Zusammenarbeit der Euro-Lände"] <-
  "Ist für eine viel schwächere wirtschaftspolitische Zusammenarbeit der Euro-Länder"; attr(s18$euro, "labels") <- el
pop18 <- paste0("pop", 1:8)
build(s18[arm == "replication"], "lfdn", p1, "weightB", pop18, "neuner_2022_populist_candidates_2018")
build(s18[arm == "amended"], "lfdn", c(euro = "euro", housing = "wohnung", tariffs = "zoelle", referendums = "dirdem"),
      "weightB", pop18, "neuner_2022_populist_amended_2018")
