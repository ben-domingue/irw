##IMF-programme message vignette (Pakistan, Gallup Pakistan phone survey, June 2023) from
##Reinsberg, B., Abouharb, M. R., & Seiferling, M. (2026). Unlocking public support: How communication
##about program design affects public perception of IMF interventions. Foreign Policy Analysis, 22(2),
##orag003. https://doi.org/10.1093/fpa/orag003
##The same experiment is analysed in Abouharb, Reinsberg & Heinkelmann-Wild (2026), The scapegoating
##hypothesis revisited, Global Studies Quarterly 6(1), ksag010 (statements T4-T6, outcomes Q1-Q2).
##Replication data: Harvard Dataverse doi:10.7910/DVN/HJ9OPE, CC0 1.0, no restricted files. File read:
##Gallup data.tab as the original Stata file (?format=original). FPA replication.do/.smcl read as text,
##not run. Wording from the two articles (FPA accepted version, Glasgow eprint 375887, Experiment
##section; GSQ, Glasgow eprint 378321, Research Strategy section) and the .dta variable/value labels.
##Usage: Rscript reinsberg_2026.R <dir holding gallup.dta> <output dir>
##
##Factorial vignette, one per respondent (task = 1, profile = 1). Everyone read the base text "The
##government of Pakistan on 2 September 2022 agreed on a credit line to borrow $6 billion from the IMF.
##This money will help Pakistan to address the current economic crisis but will require that the
##government commits to economic reforms." (FPA; GSQ writes "International Monetary Fund"), followed by
##six statements, each shown independently with probability one-half (FPA: "Any given statement
##appeared independently of the other statements with probability one-half"; all 64 combinations occur,
##18-37 respondents each). Each attr_ holds the statement text when shown and "(not shown)" otherwise:
##  hurt, adjburden, socprog (T1-T3: FPA's treatments; text from FPA)
##  govblame, industryblame, ngoblame (T4-T6: GSQ's treatments; text from GSQ; the .dta labels are
##  the same text cut at 80 characters, checked).
##The order of the statements in the vignette is not documented. Survey translated by Gallup into local
##languages (GSQ); the stored text is the articles' English.
##Outcomes (all ratings of the single vignette; codes as in the source, labels from the .dta):
##  rating                 = q3 "To what extent do you approve or disapprove of this program?"
##                           1 Disapprove a lot ... 4 Approve a lot (FPA's main outcome, dichotomized there)
##  rating_gov_responsible = q1 "To what extent do you think the government of Pakistan under the
##                           leadership of Shehbaz Sharif (PML-N) is responsible for the program with the
##                           IMF?" 1 Not / 2 Somewhat / 3 Much responsible (wording GSQ)
##  rating_imf_responsible = q2 "To what extent do you think the IMF is responsible for this program?"
##                           (.dta label; GSQ prints "... for the government's program with the IMF?"),
##                           1-3 as q1
##  rating_imf_confidence  = q6, 0 "No confidence at all" - 10 "Complete confidence" (wording FPA)
##N: 1,691 respondents (FPA/GSQ say 1,600 sampled; the authors' models use the 1,514 who answered the
##IMF-knowledge item q9 correctly). cov_imf_knowledge keeps q9 as label text so that filter can be
##reproduced (its option text is cut at 80 characters in the .dta). cov_survey_weight = Weight (poststratification).
##Covariates (text from .dta value labels): cov_gender (d1 Male/Female), cov_age (d2, years),
##cov_education (d3; 99 Refused -> NA, 98 "Don't know" kept), cov_employment (d4; 99 -> NA), cov_sector
##(d4a; asked of workers only), cov_area (d5), cov_income (d7, PKR monthly bands), cov_mother_tongue (d8),
##cov_vote_intention (q4; vote choice, not party ID; 99 -> NA; one CP1252 apostrophe re-encoded), cov_record_statement (q5),
##cov_q7 / cov_q8 (q7/q8 agree-disagree items, full wording truncated in the .dta;
##99 -> NA). Dropped: q4a (authors' grouping of q4), interview Date. ID is Gallup's sequential 1..1691.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "gallup.dta"))
stopifnot(nrow(s) == 1691L, !anyDuplicated(s$ID))
st <- c(hurt = "Some of these reforms may hurt some people in Pakistan.",
        adjburden = "The reform program includes measures to reduce the budget deficit, including an increased general sales tax and expenditure cuts.",
        socprog = "Pakistan’s social protection system, the Benazir Income Support Program (BISP), will not be affected by the program.",
        govblame = "Members of the government criticized the IMF for insisting on cuts in electricity subsidies, increasing costs for consumers and industry.",
        industryblame = "The chairman of an important industry association criticized the IMF for insisting on cuts in electricity subsidies, increasing costs for consumers and industry.",
        ngoblame = "Civil society organizations criticized the IMF for insisting on cuts in electricity subsidies, increasing costs for consumers and industry.")
d <- data.table(id = as.integer(s$ID), task = 1L, profile = 1L, rating = as.integer(s$q3),
                rating_gov_responsible = as.integer(s$q1), rating_imf_responsible = as.integer(s$q2),
                rating_imf_confidence = as.integer(s$q6))
for (v in names(st)) {
  x <- as.integer(zap_labels(s[[v]])); stopifnot(all(x %in% 0:1))
  lab <- sub("^T[1-6]\\. ", "", attr(s[[v]], "label"))
  a7 <- function(z) substr(gsub("[^ -~]", "", z), 1, 50)
  stopifnot(a7(st[[v]]) == a7(lab))   # .dta label = same text, cut at 80 characters
  d[, paste0("attr_", v) := fifelse(x == 1L, st[[v]], "(not shown)")]
}
txt <- function(v, na = 99) { x <- zap_labels(s[[v]]); y <- as.character(as_factor(s[[v]], levels = "labels")); bad <- !validUTF8(y); y[bad] <- iconv(y[bad], "CP1252", "UTF-8"); y[x %in% na | is.na(x)] <- NA; y }
d[, cov_gender := c("male", "female")[as.integer(zap_labels(s$d1))]]
d[, cov_age := as.integer(zap_labels(s$d2))]
d[, cov_education := txt("d3")][, cov_employment := txt("d4")][, cov_sector := txt("d4a")]
d[, cov_area := txt("d5")][, cov_income := txt("d7")][, cov_mother_tongue := txt("d8")]
d[, cov_vote_intention := txt("q4")][, cov_record_statement := txt("q5")]
d[, cov_q7 := txt("q7")][, cov_q8 := txt("q8")][, cov_imf_knowledge := txt("q9")]
d[, cov_survey_weight := as.numeric(s$Weight)]
stopifnot(all(d$rating %in% 1:4), all(d$rating_gov_responsible %in% 1:3), all(d$rating_imf_responsible %in% 1:3),
          all(d$rating_imf_confidence %in% 0:10), all(zap_labels(s$d1) %in% 1:2), d[cov_age < 18 | cov_age > 100, .N] == 0)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "reinsberg_2026_imf_messages.csv"))
