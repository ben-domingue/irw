##Performance-information issue-prioritization DCE (Belgian local politicians and managers) from
##van der Voet, J., & Lerusse, A. V. (2024). Performance information and issue prioritization by
##political and managerial decision-makers: A discrete choice experiment. Journal of Public
##Administration Research and Theory, 34(4), 582-597. https://doi.org/10.1093/jopart/muae011
##Replication data: DANS Data Station SSH doi:10.17026/SS/RHXP6Q, CC BY-NC 4.0, no restricted
##files. File read: JPARTDataset (Dataverse file 234220, named .xlsx but a tab-separated text
##file; long format, one row per respondent x choice set x alternative, features coded
##"Included" / "Not Included"). JPARTAnalysis.do read as text only.
##Level text: the deposit has no questionnaire, so the displayed wording is taken from the
##article's Table 2 (English; the article's appendix gives the Dutch and French versions that
##respondents saw), with the bracketed domain words filled in for each domain (roads / schools):
##  attr_source      external Included -> "The performance evaluation has been conducted by
##                   experts from a consultancy organization."; internal Included -> "... by
##                   experts from your own municipality."
##  attr_nature      subjective Included -> "The performance evaluation report measures [road
##                   quality / school performance] in a subjective way as [citizens' satisfaction
##                   / parents' satisfaction]."; objective Included -> "... in an objective way
##                   as [International Roughness Index / pupils' standardized test results]."
##  attr_aspiration  historical / social / coercive Included -> "The conclusion of the report is
##                   that the quality of this [road / school] is lower than it was 2 years ago." /
##                   "... lower than in neighboring municipalities." / "... lower than the target
##                   that was set."
##  attr_time        10 / 25 -> "Addressing this issue will require 10 [25] percent of your
##                   time per working week."
##The external/internal and subjective/objective codings are complementary in every row and
##exactly one aspiration type is Included (stopifnot). The domain-filled wording is the
##article's template, not a copy of the screen; check against the article's appendix if needed.
##Usage: Rscript vandervoet_2024.R <raw dir> <output dir>
##
##2,313 respondents (1,292 politicians, 1,021 public managers in 562 Belgian municipalities;
##Qualtrics, June-September 2022; article). Fixed blocked design: each respondent saw one domain
##(trial_service Roads / Schools) and one of 3 blocks of 4 choice sets (12 sets per domain;
##every respondent's 4 sets in the data are one block, in the same order). task = choice-set
##order in the data (obsid within respondent; the article does not say whether set order was
##randomized), profile = issue 1 / 2 (asc = 1 is always the first row of a set = issue 1).
##Outcome: choice = RES, the issue the respondent "would choose to prioritize" (article
##paraphrase; verbatim wording only in the article's appendix); exactly one chosen per set; no
##opt-out.
##Covariates as stored: cov_gender (gendersurvey Females/Males/Others -> female/male/other),
##cov_region (Brussels/Flanders/Wallonia), cov_function (Politicians / Public Managers),
##cov_position (Advisor, Alderman, Mayors, Other, Other PM, Public Managers), cov_education
##(educationuniversity, stored text incl. the typo "Univesity degree"). DROPPED for
##re-identification risk: age and tenure (with region, position and gender they can single out
##e.g. a mayor). id = respondent id as stored (integers 1-2313).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "JPARTDataset.xlsx"), sep = "\t", na.strings = c("", "NA"))
stopifnot(nrow(r) == 18504, all(r$external != r$internal), all(r$subjective != r$objective),
          all((r$historical == "Included") + (r$social == "Included") + (r$coercive == "Included") == 1),
          all(r$time %in% c(10, 25)), all(r$publicservice %in% c("Roads", "Schools")))
r[, profile := seq_len(.N), obsid]
stopifnot(r[, all(asc == as.integer(profile == 1))], r[, .N, obsid][, all(N == 2)],
          r[, uniqueN(id), obsid][, all(V1 == 1)], r[, all(diff(obsid) >= 0), id][, all(V1)])
r[, task := match(obsid, unique(obsid)), id]
rd <- r$publicservice == "Roads"
d <- r[, .(id = as.integer(id), task, profile, choice = as.integer(RES),
  attr_source = fifelse(external == "Included",
    "The performance evaluation has been conducted by experts from a consultancy organization.",
    "The performance evaluation has been conducted by experts from your own municipality."),
  attr_nature = fifelse(subjective == "Included",
    sprintf("The performance evaluation report measures %s in a subjective way as %s.",
            fifelse(rd, "road quality", "school performance"), fifelse(rd, "citizens' satisfaction", "parents' satisfaction")),
    sprintf("The performance evaluation report measures %s in an objective way as %s.",
            fifelse(rd, "road quality", "school performance"), fifelse(rd, "International Roughness Index", "pupils' standardized test results"))),
  attr_aspiration = sprintf("The conclusion of the report is that the quality of this %s is lower %s.", fifelse(rd, "road", "school"),
    fifelse(historical == "Included", "than it was 2 years ago",
            fifelse(social == "Included", "than in neighboring municipalities", "than the target that was set"))),
  attr_time = sprintf("Addressing this issue will require %d percent of your time per working week.", as.integer(time)),
  trial_service = publicservice,
  cov_gender = c(Females = "female", Males = "male", Others = "other")[gendersurvey],
  cov_region = region, cov_function = function1, cov_position = position, cov_education = educationuniversity)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(trial_service), id][, all(V1 == 1)],
          d[, max(task), id][, all(V1 == 4)], !anyNA(d))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "vandervoet_2024_performance_info.csv"))
