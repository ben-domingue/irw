##Brexit-deal conjoint experiments (Germany and Spain) from
##Jurado, I., León, S., & Walter, S. (2022). Brexit dilemmas: Shaping postwithdrawal
##relations with a leaving state. International Organization, 76(2), 273-304.
##https://doi.org/10.1017/S0020818321000412
##Replication data: Harvard Dataverse doi:10.7910/DVN/3DNBNQ, CC0 1.0, no restricted files.
##Files read: "Brexit dilemmas_Conjoint.dta" and "Brexit_dilemmas_Survey.dta" (Dataverse
##"original format" downloads, saved as conjoint.dta and survey.dta), which keep the Stata
##value labels. The conjoint screens are reproduced in the article's online appendix
##(Appendix 2, Cambridge supplementary .docx).
##Usage: Rscript jurado_2022.R <raw dir> <output dir>
##
##Online panel samples in Germany (2,388 respondents) and Spain (2,408), each fielded in two
##cross-sectional waves (no respondent is in both; trial_wave = the source's wave code 1/2;
##Germany 1,550 + 838, Spain 1,550 + 858). The paper pools waves and adds a wave dummy (the
##appendix calls one of them "the March 2019 wave"); they are kept together here because the
##attribute set and question are identical. One table per country.
##Each respondent saw 6 tasks of two Brexit agreements ("Brexit-Vereinbarung A/B", "Acuerdo
##para el Brexit A/B") with 7 attributes, and answered "Welche Brexit-Vereinbarung würden Sie
##wählen, wenn die Entscheidung bei Ihnen läge?" / "¿Qué acuerdo para el Brexit elegiría si la
##decisión la tomara usted?" (Which Brexit agreement would you choose if the decision were
##yours?). Forced choice, no opt-out; every task has exactly one chosen profile. The
##attribute ROW ORDER was randomized across respondents (visible in the two appendix screens)
##but row positions are not in the data, so no attrpos_ columns. Every pair of levels
##co-occurs (no sign of restrictions), but level frequencies are not uniform (e.g. brexit
##bill "None" 24% vs "Small" 21%; free movement "Some restrictions" 29% vs "No
##restrictions" 37%), so randomization weights were apparently unequal; not documented.
##profile = source `ab` + 1. The deposit does not document `ab`; ab = 0 is taken to be
##agreement A (left column). This is an assumption.
##LEVEL TEXT: respondents saw German or Spanish text; the data carry the authors' English
##value labels, used here, except trade level 1 ("None"), written out as "No trade barriers
##(UK stays in the single market)" to match the screen ("verbleibt im europäischen
##Binnenmarkt: Keine Handelsbeschränkungen"). "Programmes" levels "+ crime" = including
##cooperation against terrorism and organised crime.
##Covariates (from the survey file, joined on respondent_id; numeric codes):
##  cov_agegroup 1=18-25 2=26-35 3=36-45 4=46-55 5=56-65 6=over 65; cov_gender 1=female
##  2=male; cov_education 1=low 2=medium 3=high; cov_ideology 0=extreme left..10=extreme
##  right; cov_vote party vote intention (1 CDU/CSU 2 SPD 3 FDP 4 Linke 5 Grüne 6 AfD 101 PP
##  102 PSOE 103 Podemos 104 Cs 105 PNV 106 PDeCat 107 ERC 997 other); cov_eu_opinion
##  1=very negative..5=very positive (source survey file coding); cov_eu_referendum
##  1=definitely leave..4=definitely remain (survey file; "don't know" already missing);
##  cov_friends_uk 1=yes 2=no; cov_business_ties 0/1; cov_risk 1=extremely uncomfortable
##  ..7=extremely comfortable taking risks; cov_economic_harm 1=much better off..5=much
##  worse off as a result of Brexit; cov_soft_hard preferred EU negotiation line 1=very
##  soft..5=very hard; cov_country_handling "country handling Brexit well" 1=strongly
##  disagree..5=strongly agree; cov_goal_* importance of five negotiation goals 1=not
##  important at all..5=very important; cov_unemployed/cov_employed/cov_retired 0/1.
##Dropped: the authors' derived dummies (education dummies, party dummies, vote_incumbent,
##satis_brexitgov, informed index), regional GDP exposure and tourism-nights measures
##(region-level), and the conjoint file's duplicate EU-opinion/referendum codings (reverse-
##coded copies of the survey file's; eu_opinion there 1 = very positive).
##No survey weight is deposited. The article full text could not be retrieved (2026-10-07),
##so the respondent count was not checked against it; the appendix's covariate models use
##1,862 (Germany) and 1,808 (Spain) respondents with complete covariates.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x) { l <- attr(x, "labels"); names(l)[match(x, l)] }
k <- read_dta(file.path(raw, "conjoint.dta"))
s <- as.data.table(zap_labels(read_dta(file.path(raw, "survey.dta"))))
d <- data.table(id = as.integer(k$respondent_id), task = as.integer(k$task), profile = as.integer(k$ab) + 1L,
                choice = as.integer(k$choice), country = as.integer(zap_labels(k$country)), trial_wave = as.integer(k$wave))
amap <- c(brexitbill = "brexit_bill", rights = "rights_eu_citizens_in_uk", circulation = "freedom_of_movement",
          eulaw = "eu_law_applicability", trade = "trade", business = "business_freedom", programmes = "eu_programmes")
for (v in names(amap)) d[, paste0("attr_", amap[[v]]) := lab(k[[v]])]
d[attr_trade == "None", attr_trade := "No trade barriers (UK stays in the single market)"]
cmap <- c(agegroup = "agegroup", gender = "gender", education_tri = "education", ideology = "ideology", vote = "vote",
          eu_opinion = "eu_opinion", eu_referendum = "eu_referendum", friends_uk = "friends_uk", ties = "business_ties",
          risk_personality = "risk", economicharm = "economic_harm", softhard = "soft_hard", country_handling = "country_handling",
          goal_avoidleave = "goal_avoid_more_exits", goal_avoidcontribution = "goal_avoid_more_contributions",
          goal_punish = "goal_punish_uk", goal_mutualagreement = "goal_mutual_agreement",
          goal_protectecointerests = "goal_protect_economic_interests", unemployed = "unemployed", worker = "employed", retired = "retired")
cv <- s[, c("respondent_id", names(cmap)), with = FALSE]
setnames(cv, c("id", paste0("cov_", cmap)))
cv[, id := as.integer(id)]
stopifnot(!anyDuplicated(cv$id), all(d$id %in% cv$id))
d <- merge(d, cv, by = "id", all.x = TRUE)
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
for (cn in list(c(1L, "germany"), c(2L, "spain"))) {
  x <- d[country == as.integer(cn[1])][, country := NULL]
  setorder(x, id, task, profile)
  fwrite(x, file.path(out, paste0("jurado_2022_brexit_deal_", cn[2], ".csv")))
}
