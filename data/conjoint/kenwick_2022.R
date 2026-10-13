##Military-adviser vignette experiment from
##Kenwick, M. R., & Maxey, S. R. (2022). You and whose army? How civilian leaders leverage the
##military's prestige to shape public opinion. The Journal of Politics, 84(3).
##https://doi.org/10.1086/718355
##Replication data: Harvard Dataverse doi:10.7910/DVN/2LH0BZ, CC0 1.0, no restricted files.
##File read: "survey_results.csv" (experiment folder), the authors' cleaned analysis file, one row
##per respondent. Variable meanings from "codebook.tab" (the authors' codebook, original xlsx).
##Not read: pretest.dta (the pre-test asks only about the adviser, no outcome factor), the speech
##analysis files.
##Usage: Rscript kenwick_2022.R <raw dir> <output dir>
##
##2,394 US online respondents (October 2019; all consented). Each saw ONE vignette in which a
##president decides about a military intervention after consulting an adviser (named Wilson in
##the pre-test), randomized in a 2 x 4 between-subject design: attr_adviser = Military adviser /
##Civilian adviser (the adviser's affiliation) and attr_outcome = Stay out / Engage / Success /
##Failure (the president stays out of the conflict, engages, the engagement succeeds, the
##engagement fails). Cells hold 295-302 respondents each. THE VIGNETTE WORDING IS NOT IN THE
##DEPOSIT (no questionnaire): the level text is the authors' condition names from the codebook
##and replication code ("military-engage condition", "Advisor has Military Affiliation / Advisor
##is Civilian"), not the sentences respondents read. Each respondent is one task with one
##profile; id = row order of the source file.
##Outcomes (wording is the codebook's description, a paraphrase):
##  rating = approval of the president's decision, ordinal 1 strongly disapprove, 2 somewhat
##    disapprove, 3 somewhat approve, 4 strongly approve (source approve_o; higher = more
##    approval).
##  rating_trust_president = trusts the president to do the right thing, 0 no / 1 yes (pright).
##  rating_trust_adviser = trusts the adviser to do the right thing, 0 no / 1 yes (aright; 1 NA).
##  rating_credit = who gets credit for the success, -1 adviser / 0 both / 1 president; asked only
##    in the Success cells (NA elsewhere).
##  rating_blame = who is blamed for the failure, -1 adviser / 0 both / 1 president; asked only in
##    the Failure cells (NA elsewhere; one Failure respondent has none).
##Opt-out: none (no choice outcome). Randomization restrictions: none stated; the 2 x 4 cells are
##near-uniform (about 300 each), no combination missing.
##Checks: the codebook's treatment dummies (civtreat/miltreat, out/engage/success/fail) agree
##with true_out for all 2,394 rows. The manipulation checks (outcome_manip,
##consult) are dropped.
##Covariates (codebook codes mapped to the codebook's text): cov_gender from `male` (1 male /
##0 female; the codebook has no other category); cov_party_id from party_order (-2 Democrat,
##-1 independent leaning Democratic, 0 independent leaning neither, 1 independent leaning
##Republican, 2 Republican); cov_education (codebook 1-6; 7 NA rows); cov_age_group (codebook
##bands); cov_duration_sec = duration_in_seconds (survey duration). Dropped: start/end dates,
##derived dummies (cons, white, black, hisp_d, wealthy, college, ...).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "survey_results.csv"))
r[, V1 := NULL]
stopifnot(nrow(r) == 2394, all(r$consent == 1))
adv <- ifelse(r$miltreat == 1, "Military adviser", ifelse(r$civtreat == 1, "Civilian adviser", NA))
stopifnot(!anyDuplicated(r[, .I]), !anyNA(adv), all(r$miltreat + r$civtreat == 1))
outc <- c("Stay out", "Engage", "Success", "Failure")[r$true_out]
stopifnot(!anyNA(outc), all(r$out == (r$true_out == 1)), all(r$engage == (r$true_out == 2)),
          all(r$success == (r$true_out == 3)), all(r$fail == (r$true_out == 4)))
lab <- function(x, lv) { stopifnot(all(is.na(x) | x %in% seq_along(lv))); lv[x] }
d <- data.table(id = seq_len(nrow(r)), task = 1L, profile = 1L,
  rating = as.integer(r$approve_o),
  rating_trust_president = as.integer(r$pright), rating_trust_adviser = as.integer(r$aright),
  rating_credit = as.integer(r$credit), rating_blame = as.integer(r$blame),
  attr_adviser = adv, attr_outcome = outc,
  cov_gender = c("female", "male")[r$male + 1L],
  cov_party_id = c("Democrat", "Independent leaning Democratic", "Independent leaning neither",
                   "Independent leaning Republican", "Republican")[r$party_order + 3L],
  cov_education = lab(r$education, c("Did not finish high school", "High school",
     "Some college but no degree", "Community college or associate's", "Four year degree",
     "Graduate or professional degree")),
  cov_age_group = lab(r$age_cat, c("18-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+")),
  cov_duration_sec = as.integer(r$duration_in_seconds))
stopifnot(all(d$rating %in% 1:4), d[attr_outcome == "Success", !anyNA(rating_credit)],
          d[attr_outcome != "Success", all(is.na(rating_credit))])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kenwick_2022_military_advisers.csv"))
