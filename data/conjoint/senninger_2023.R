##MP re-election vote-choice conjoint (Germany) from
##Senninger, R., & Bischof, D. (2023). Do voters want domestic politicians to scrutinize the
##European Union? Political Science Research and Methods, 11(2), 410-418.
##https://doi.org/10.1017/psrm.2021.54 (design facts from the CC BY preprint,
##https://doi.org/10.31235/osf.io/5my7j).
##Replication data: Harvard Dataverse doi:10.7910/DVN/DXEZAM, CC0 1.0, no restricted files.
##Files read: dataframe13.RData (object `cjointdata`, 9,930 rows: the full conjoint data with
##respondent covariates; the same rows and attributes as dataframe2.RData, used for the main
##Figure 2), dataframe12.RData (object `cjointrandomdata`, read only for the per-respondent
##survey block order V2) and dataframe4.RData (object `cjointdata`, the same 9,930 rows, read
##only for the survey weights weights1/weights2). Each loaded into its own environment. The replication Rmd was read as
##text (not run).
##Usage: Rscript senninger_2023.R <dir holding dataframe4/12/13.RData> <output dir>
##
##993 German Clickworker respondents (6 March 2019). Five tasks, each a contest between two
##current MPs running for re-election (task, profile recorded by the authors' cjoint reshape),
##7 attributes, German text as displayed: most knowledge of problems (constituency / national /
##European politics), reason for most absent days in the Bundestag, effort to reform the
##Eurozone, gender, motivation for candidacy, years in parliament, party. attrpos_<name> = the
##source .rowpos (attribute row 1-7, randomized once per respondent: constant within id in the
##data); profiles shown as a table of attribute rows (the .rowpos fields; screenshot in the
##preprint's Figure S15, not inspected). Outcome: choice = which candidate the
##respondent would vote for ("state which candidate they would vote for", preprint;
##paraphrase, the German item is in the Supplementary Materials, not read); forced choice,
##exactly one per task (checked), no opt-out.
##RESTRICTION (preprint fn 3, and the authors' cjoint design object): AfD candidates always have
##"zwei Jahren" in parliament. Level weights OBSERVED (not documented): AfD is 4.6% of profiles
##against 18.5-19.6% for each other party, close to the 1/6 x 1/4 that redrawing every
##disallowed AfD profile would give; "zwei Jahren" 28.8% vs 23-24% for the other years follows.
##The other attributes are within 1.04x of uniform.
##trial_block_order: half of respondents answered the survey questions before the conjoint
##("Controls|conjoints") and half after ("conjoints|Controls"), source V2 (authors' posttreat).
##Covariates, the respondents' German answer text: cov_birth_year (yrbrn), cov_gender
##(geschlecht: "männlich" -> "male", "weiblich" -> "female", "keine Angabe" -> NA),
##cov_education (schule, school-leaving qualification as answered, e.g. "Abitur", "noch
##Schüler"; "keine Angabe" -> NA; the preprint's "level of school education"),
##cov_vote_intention (sonntagsfrage), cov_party_id (parteinah, the party the respondent leans
##towards, e.g. "SPD (Sozialdemokratische Partei Deutschlands)", "Nein, ich neige keiner
##Partei zu", "Ich weiß es nicht"; "keine Angabe" -> NA), cov_flag (flagge2), cov_euid1, cov_euid2, cov_democracy1, cov_democracy2,
##cov_influence (Einfluss2), cov_orientation (ausrichtung), cov_manipulation_answer
##(manipultest: the factual manipulation check answer; the authors score Ausbildung,
##Familienstand, Nationalitaet and -99 as passed). Item wordings are not in the deposit.
##cov_survey_weight = weights1 from dataframe4: the authors' post-hoc re-weighting to the 2016
##ESS on age group, gender and school education, trimmed at 3 (preprint Supplementary Figure
##S1; robustness only, the main results are unweighted). The same weights trimmed at 5
##(weights2, Figure S2) and the weights that add EU attitudes (Figures S3-S4, other files) are
##not built.
##Dropped: the authors' English recodes (mp_*, gender, schoolqual, EUsupport, impact, ...),
##derived pass flag manipulcheck, age groups. dataframe12 also carries Qualtrics ResponseIds (in
##a column named IPAddress) and Qualtrics randomization strings: not used. id = the authors'
##respondent number (1-993).
##Spot check: AMCE of Eurozone reform effort vs "gar nicht" (lm on all attributes, with
##party x years for the restriction, SEs clustered by id): "wenig" +3.5 pp, "viel" +12.0 pp; the
##preprint reports 3.6 (CI 1.1-6.0) and CI 9.6-14.5 (midpoint 12.05).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "dataframe13.RData"), envir = e); s <- as.data.table(e$cjointdata)
e2 <- new.env(); load(file.path(raw, "dataframe12.RData"), envir = e2)
bo <- unique(as.data.table(e2$cjointrandomdata)[, .(id = as.integer(respondent), trial_block_order = as.character(V2))])
stopifnot(!anyDuplicated(bo$id))
an <- c(knowledge = "Am.meisten.Kenntnis.von.Problemen.und.Herausforderungen", eurozone_reform = "Engagement.in.der.Reform.der.Eurozone",
        absent_days_reason = "Fehltage.im.Bundestag.meistens.aufgrund.von", gender = "Geschlecht",
        motivation = "Motivation.für.Kandidatur", years_in_parliament = "Parlamentsmitglied.seit", party = "Partei")
d <- s[, .(id = as.integer(respondent), task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected))]
for (n in names(an)) {
  d[, paste0("attr_", n) := as.character(s[[an[[n]]]])]
  d[, paste0("attrpos_", n) := as.integer(s[[paste0(an[[n]], ".rowpos")]])]
}
cv <- c(birth_year = "yrbrn", gender = "geschlecht", education = "schule", vote_intention = "sonntagsfrage", party_id = "parteinah",
        flag = "flagge2", euid1 = "EUID1", euid2 = "EUID2", democracy1 = "Demokratie1", democracy2 = "Demokratie2",
        influence = "Einfluss2", orientation = "ausrichtung", manipulation_answer = "manipultest")
for (n in names(cv)) d[, paste0("cov_", n) := if (n == "birth_year") as.integer(s[[cv[[n]]]]) else as.character(s[[cv[[n]]]])]
stopifnot(all(d$cov_gender %in% c("männlich", "weiblich", "keine Angabe")))
d[, cov_gender := c("männlich" = "male", "weiblich" = "female")[cov_gender]]
for (v in c("cov_education", "cov_party_id")) d[get(v) == "keine Angabe", (v) := NA_character_]
e4 <- new.env(); load(file.path(raw, "dataframe4.RData"), envir = e4)
wt <- unique(as.data.table(e4$cjointdata)[, .(id = as.integer(respondent), cov_survey_weight = as.numeric(weights1))])
stopifnot(!anyDuplicated(wt$id), nrow(wt) == 993)
d <- merge(d, bo, by = "id")
d <- merge(d, wt, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "trial_block_order"))
stopifnot(nrow(d) == 9930, uniqueN(d$id) == 993, d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
          d[attr_party == "AfD", all(attr_years_in_parliament == "zwei Jahren")], !anyNA(d$trial_block_order))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "senninger_2023_mp_eu_oversight.csv"))
