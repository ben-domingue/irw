##Two naturalization conjoints (Qatar) from
##Shockley, B., & Gengler, J. J. (2024). Sharing citizenship: Economic competition, cultural
##threat, and immigration preferences in the rentier state. Political Science Research and
##Methods, 12(1), 59-75. https://doi.org/10.1017/psrm.2023.18 (open access, CC BY 4.0)
##Replication data: Harvard Dataverse doi:10.7910/DVN/HZE7FF, CC0 1.0, no restricted files.
##Files read: "PSRM conjoint replication.dta" and "PSRM replication priorities.dta" (Dataverse
##"original format" downloads). The .dta files carry NO value labels for the attributes; the
##level labels are the authors' factor labels in "PSRM Replication Code.R" (read as text, not
##run), checked against the article text. No codebook or questionnaire is deposited.
##Usage: Rscript shockley_2024.R <raw dir> <output dir>
##
##Sample: SESRI (Qatar University) face-to-face survey of Qatari citizens, May 2018, 733
##completes; both tasks were self-administered on a touch-screen laptop. Respondents saw
##Arabic text; the English labels below are the authors' analysis labels, NOT the displayed
##wording (which is not deposited). Two separate experiments with different attribute sets,
##so TWO tables (the authors also analyse them separately: Figure 2 vs Figure 3).
##
##1. shockley_2024_qatar_groups ("priorities" experiment; paper Figure 2, Table A.2).
##   Respondents chose between two "baskets" of non-citizen groups to prioritise for
##   citizenship; each basket named two of five groups; 3 contests. task = contest_no,
##   profile = basket_no. choice = selected (exactly one basket chosen in every task; forced).
##   Each group is an attribute with level "Mentioned"/"Not mentioned" (the authors' labels):
##   attr_children_of_qatari_mothers, attr_born_in_qatar, attr_non_qatari_tribe ("a tribe not
##   native to Qatar"), attr_special_skills ("important professional skills"),
##   attr_military_service. attrpos_<group> = 1 or 2, the group's position within the basket
##   (source e1p/e2p: codes 1-5 for the first and second group shown; the code -> group map
##   1 children, 2 born, 3 tribe, 4 skills, 5 service is inferred from the indicators, with
##   which it agrees on every row; blank when the group was not in the basket).
##   488 respondents, 1,425 tasks (10 respondents have 1 contest, 19 have 2). 488 matches the
##   authors' cjoint log ("Number of Respondents = 488"). Covariates: cov_gender (source
##   `female` 1 = Male, 2 = Female per "PSRM Replication Code.R" factor(..., levels = c(1,2),
##   labels = c("Male","Female")); agrees with the file's `gender` labels MALE = 3 / FEMALE = 5
##   and its `male` dummy on every row), cov_age (years), cov_survey_weight (wgt: this file has
##   no weight, so it is taken from "PSRM conjoint replication.dta" by caseid, the same SESRI
##   case number; one value per case there; NA for the 33 of 488 respondents who are not in
##   that file). Dropped: unlabelled education/income/region codes, the authors' factor
##   scores, attitude indices, quantile recodes and dummies.
##
##2. shockley_2024_qatar_residency (individual-candidate conjoint; paper Figure 3, Table A.3).
##   Three pairs of hypothetical candidates for permanent residency, 6 attributes:
##   attr_religion (signalled by the candidate's first name, three names per group; the names
##   themselves are not in the deposit, so the level is the cued identity: "Christian",
##   "Sunni", "Shia", or "Not mentioned" = no first name shown), attr_nationality (British,
##   Indian, Palestinian, Egyptian, Yemeni), attr_occupation (Doctor, Teacher, Engineer,
##   Military), attr_salary (20K, 40K, 60K; Qatari riyals per month, per the article's
##   "40,000 Qatari riyals ... per month"), attr_time_in_country (Less than 1 year, 10 years,
##   20 years, Born in Qatar), attr_language (Arabic, English, Arabic and English).
##   choice = selected. OPT-OUT: "Respondents were allowed to reject both candidates rather than
##   being forced to choose one", but could not select both: 35 of 1,722 tasks have choice = 0
##   on both profiles. task = contest_no (1-3; some respondents have fewer contests: 54 have
##   1, 141 have 2), profile = row order within id_contest (assumed left/right; not recorded).
##   The article says respondents also RATED the six profiles; those ratings are not deposited.
##   657 respondents (of 733 completes); the authors' Figure 3 model uses the 554 with a
##   non-missing income answer. Covariates: cov_survey_weight (wgt), cov_income_over_40k
##   (1 = monthly household income more than 40K, 0 = less; NA = not answered; the authors'
##   recode of qinco1). No attention check or duration is deposited for either experiment.
##Respondent ids are re-keyed to 1..n within each table (source caseid is a survey case
##number); the two tables share 455 respondents but ids are not linked across tables.
##Spot checks: lm(choice ~ attr_children_of_qatari_mothers), SE clustered by id, gives
##0.299 (SE 0.021), as in the authors' log (0.29889, 0.021). The weighted lm of choice on
##the six residency attributes for the 554 respondents with income reproduces all 17
##AMCEs of the authors' Figure 3 / Table A.3 model to 4 decimals (e.g. no name -0.0562,
##Military 0.0515, 60K -0.0368).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]

## 1. groups ("priorities")
p <- as.data.table(zap_labels(read_dta(file.path(raw, "PSRM replication priorities.dta"))))
grp <- c(children_of_qatari_mothers = "children_1", born_in_qatar = "born_1", non_qatari_tribe = "nonqatari_1",
         special_skills = "skills_1", military_service = "service_1")
stopifnot(p[, .N, .(caseid, contest_no)][, all(N == 2)], p[, sum(selected), .(caseid, contest_no)][, all(V1 == 1)])
g <- data.table(id = as.integer(factor(p$caseid)), task = as.integer(p$contest_no), profile = as.integer(p$basket_no),
                choice = as.integer(p$selected))
for (k in seq_along(grp)) {
  v <- p[[grp[k]]]; stopifnot(all(v %in% 1:2))
  g[, paste0("attr_", names(grp)[k]) := c("Not mentioned", "Mentioned")[v]]
  pos <- ifelse(p$e1p == k, 1L, ifelse(p$e2p == k, 2L, NA_integer_))
  stopifnot(identical(!is.na(pos), v == 2))
  g[, paste0("attrpos_", names(grp)[k]) := pos]
}
stopifnot(all(p$female %in% 1:2))
g[, cov_gender := c("male", "female")[p$female]][, cov_age := as.integer(p$age)]
w <- unique(as.data.table(zap_labels(read_dta(file.path(raw, "PSRM conjoint replication.dta"))))[, .(caseid, wgt)])
stopifnot(!anyDuplicated(w$caseid))
g[, cov_survey_weight := as.numeric(w$wgt[match(p$caseid, w$caseid)])]
stopifnot(uniqueN(g$id) == 488)
setorder(g, id, task, profile)
fwrite(g, file.path(out, "shockley_2024_qatar_groups.csv"))

## 2. residency candidates
c <- as.data.table(read_dta(file.path(raw, "PSRM conjoint replication.dta")))
stopifnot(c[, .N, id_contest][, all(N == 2)], c[, sum(selected), id_contest][, all(V1 <= 1)])
c[, profile := seq_len(.N), id_contest]
lab <- list(namecand = c("Christian", "Sunni", "Shia", "Not mentioned"),
            natcand = c("British", "Indian", "Palestinian", "Egyptian", "Yemeni"),
            jobcand = c("Doctor", "Teacher", "Engineer", "Military"),
            salarycand = c("20K", "40K", "60K"),
            timecand = c("Less than 1 year", "10 years", "20 years", "Born in Qatar"),
            langcand = c("Arabic", "English", "Arabic and English"))
nm <- c(namecand = "religion", natcand = "nationality", jobcand = "occupation", salarycand = "salary",
        timecand = "time_in_country", langcand = "language")
d <- data.table(id = as.integer(factor(c$caseid)), task = as.integer(c$contest_no), profile = as.integer(c$profile),
                choice = as.integer(c$selected))
for (v in names(lab)) { x <- as.integer(c[[v]]); stopifnot(all(x %in% seq_along(lab[[v]])))
  d[, paste0("attr_", nm[v]) := lab[[v]][x]] }
d[, cov_survey_weight := as.numeric(c$wgt)][, cov_income_over_40k := as.integer(c$income == 2)]
stopifnot(uniqueN(d$id) == 657, d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "shockley_2024_qatar_residency.csv"))
