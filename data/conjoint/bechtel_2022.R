##Disaster-relief divide-the-dollar conjoint (US, December 2016) from
##Bechtel, M. M., & Mannino, M. (2022). Retrospection, fairness, and economic shocks: How do
##voters judge policy responses to natural disasters? Political Science Research and Methods,
##10(2), 260-278 (online 2020). https://doi.org/10.1017/psrm.2020.39
##Replication data: Harvard Dataverse doi:10.7910/DVN/JRLYVN, CC0 1.0, no restricted files.
##File read: conjoint_scenariolevel.dta (Dataverse "original format" of conjoint_scenariolevel.tab;
##the authors' respondent x task x county file, 20,944 rows, 511 columns; only the columns used
##here are read). Read as text: Readme.docx, "2_main results.do", "3_appendix results.do",
##empirical_results.txt and the article PDF in the deposit (Bechtel-Mannino-Disasterrelief.pdf,
##pp. 6-10, Figure 1, Table 1).
##Usage: Rscript bechtel_2022.R <raw dir> <output dir>
##
##2,618 US citizens (Respondi online quota panel, December 2016; article p. 7). Each respondent
##split a total of $10 million in relief aid between two counties hit by a natural disaster, 4
##times (task = conjointno 1-4, profile = scenario 1-2 = county A/B; recorded).
##Outcome: rating = relief_, the amount given to this county in $ million (0-10; the two counties
##of a task always sum to 10, verified). The Qualtrics item labels are "contribution to region
##A/B"; the instruction text is a screenshot (Figure 1), so the question is a paraphrase.
##No choice column (an allocation, not a pick).
##Attributes (level text as displayed, from the Qualtrics conjoint fields G-<task>-<profile>-<row>
##with the attribute name in G<task><row>): economic_damage ($100,000 / $1 million / $4 million /
##$24 million), fatalities (0 / 5), household_income ("Average household income": $10,000 ..
##$100,000), unemployment (3% / 5% / 7% / 9%), presvote_2012 ("Presidential vote in 2012", five
##"xx% Democrat, yy% Republican" splits). The sixth dimension, presidential partisanship
##(president<task>: Democratic / Republican), is the same for both counties of a task (article
##Figure 1 note) and is stored on both profiles as attr_president. The text fields agree with the
##authors' coded variables (damagevalue, FeatPresident_; checked in the script).
##Attribute row order (5 county rows) was randomized across respondents (article Figure 1 note)
##and recorded: attrpos_* = row 1-5; it is the same in all 4 tasks of a respondent (verified).
##Randomization: all county values fully randomized; president randomized per task (article p. 9).
##Covariates: cov_survey_weight (`weight`, the authors' entropy-balancing weight to Census age/
##sex/education margins, used in the article's main results), cov_gender (sex: 0 Female, 1 Male;
##value labels), cov_age, cov_education (value-label text, 10 categories), cov_race (value-label
##text), cov_party_id (partyID value-label text: Republican / Democrats / No affiliation/other),
##cov_left_right (0 Left .. 10 Right), cov_attention_pass (color_correct, the attention question
##used in appendix Figure A6). The `state` column holds undocumented numeric codes and is dropped.
##PII: the file holds respondents' IP addresses and GPS latitude/longitude (and county of
##residence); none of these columns is read. ResponseID not read (uniqueID is the authors'
##running number). No repeated task. Dropped: the other survey experiments in the file
##(fin_cost, framing, rel_aid, prep) and all derived dummies.
##Spot check: weighted lm(rating ~ county attributes) on the Democratic-president tasks, clustered
##by id, reproduces the deposited log's model (log line 668: damage $24 million +1.169, SE .068;
##income $10,000 +.481) to 3 decimals.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
gcols <- c(outer(1:4, 1:5, function(t, k) paste0("G", t, k)), outer(outer(1:4, 1:2, paste0), 1:5, function(tp, k) paste0("G", tp, k)))
k <- as.data.table(read_dta(file.path(raw, "conjoint_scenariolevel.dta"),
                            col_select = c("uniqueID", "conjointno", "scenario", "relief_", "damagevalue", "FeatPresident_", "weight",
                                           "sex", "age", "education", "race", "partyID", "leftright", "color_correct",
                                           paste0("president", 1:4), all_of(unique(gcols)))))
lab <- function(v) as.character(as_factor(v, levels = "labels"))
for (v in names(k)[sapply(k, is.character)]) set(k, j = v, value = trimws(k[[v]]))
an <- c("Economic damage" = "economic_damage", "Fatalities" = "fatalities", "Average household income" = "household_income",
        "Unemployment rate" = "unemployment", "Presidential vote in 2012" = "presvote_2012")
d <- data.table(id = as.integer(k$uniqueID), task = as.integer(k$conjointno), profile = as.integer(k$scenario), rating = as.integer(k$relief_))
for (t in 1:4) for (r in 1:5) {
  w <- which(d$task == t); nm <- an[k[[paste0("G", t, r)]][w]]
  stopifnot(!anyNA(nm), all(k[[paste0("G", t, r)]] == k[[paste0("G1", r)]]))
  for (v in unique(nm)) {
    ww <- w[nm == v]
    set(d, ww, paste0("attr_", v), ifelse(d$profile[ww] == 1L, k[[paste0("G", t, 1, r)]][ww], k[[paste0("G", t, 2, r)]][ww]))
    set(d, ww, paste0("attrpos_", v), r)
  }
}
pr <- character(nrow(d)); for (t in 1:4) pr[d$task == t] <- k[[paste0("president", t)]][d$task == t]
d[, attr_president := pr]
stopifnot(!anyNA(d), d[, all(attr_president == c("Republican", "Democratic")[k$FeatPresident_ + 1L])],
          all(d$attr_economic_damage == c("$100,000", "$1 million", "$4 million", "$24 million")[match(round(k$damagevalue, 1), c(0.1, 1, 4, 24))]),
          d[, sum(rating), .(id, task)][, all(V1 == 10)], all(d$rating %in% 0:10), d[, .N, id][, all(N == 8)])
stopifnot(all(zap_labels(k$sex) %in% 0:1))
d[, `:=`(cov_survey_weight = k$weight, cov_gender = c("female", "male")[as.integer(zap_labels(k$sex)) + 1L], cov_age = as.integer(k$age),
         cov_education = lab(k$education), cov_race = lab(k$race), cov_party_id = lab(k$partyID),
         cov_left_right = as.integer(zap_labels(k$leftright)), cov_attention_pass = as.integer(k$color_correct))]
d[cov_left_right < 0, cov_left_right := NA]
d[!is.na(cov_age) & (cov_age < 18 | cov_age > 100), cov_age := NA]
setcolorder(d, c("id", "task", "profile", "rating", paste0("attr_", c(an, "president")), paste0("attrpos_", an)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bechtel_2022_disaster_relief.csv"))
