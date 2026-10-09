##Faculty-hiring conjoints at two U.S. public universities (four samples) from
##Carey, J. M., Carman, K. R., Clayton, K. P., Horiuchi, Y., Htun, M., & Ortiz, B. (2020). Who
##wants to hire a more diverse faculty? A conjoint analysis of faculty and student preferences for
##gender and racial/ethnic diversity. Politics, Groups, and Identities, 8(3), 535-553.
##https://doi.org/10.1080/21565503.2018.1491866
##Replication data: Harvard Dataverse doi:10.7910/DVN/GD1UEI, CC0 1.0, no restricted files.
##Files read (from ReplicationPackage.tar.gz): data/Campus_Diversity_Project__UNM_Faculty_
##Recruitment_by_Faculty.csv, ..._UNM_Faculty_Recruitment_by_Students.csv, ..._UNR_Faculty_
##Recruitment_by_Faculty.csv, ..._UNR_Faculty_Recruitment.csv (UNR students); legacy Qualtrics
##exports (row 1 codes, row 2 question text). Read as text, not run: documents/*.pdf (the four
##questionnaires: wording, answer codes), documents/UNM_faculty.php and UNR_faculty.php (the
##profile randomizers: levels, weights, restriction, number of tasks), functions/read_qualtrics.R
##and scripts/unm.R, unr.R (the authors' sample filter and outcome coding).
##Usage: Rscript carey_2020.R <dir holding ReplicationPackage/> <output dir>
##
##Respondents saw pairs of hypothetical faculty candidates ("Candidate 1", "Candidate 2") and
##answered "If you had to choose between them, which of these two candidates should be given
##priority to be hired as a new faculty member at the University of New Mexico?" (UNR: "...at the
##University of Nevada, Reno?"); options Candidate 1 (1) / Candidate 2 (2): forced choice, no
##opt-out. The table on each screen was headed "Which candidate do you think should be given
##priority in faculty recruitment? Even if you are not entirely sure, please indicate which of the
##two you would be most likely to choose." (Q2.3 etc., display only).
##FOUR TABLES, one per survey (separate populations and fieldings, separate questionnaires; the
##authors estimate AMCEs per sample and compare them, never pool):
##  carey_2020_hiring_unm_faculty, carey_2020_hiring_unm_students: University of New Mexico, Oct
##    2016, 8 tasks, 8 attributes: gender, race/ethnicity, heritage (New Mexican / U.S. Citizen /
##    Non U.S. Citizen), research record, teaching record, PhD institution, spouse/partner is a
##    current or potential faculty member, community engagement/service record.
##  carey_2020_hiring_unr_faculty, carey_2020_hiring_unr_students: University of Nevada, Reno, 10
##    tasks, 9 attributes: department/program, position, race/ethnicity, gender, PhD institution,
##    undergraduate institution, spouse/partner, teaching record, research record.
##Task = screen (Q2.4, Q2.7, ... in order), profile = candidate number; attribute names, levels and
##row order are the Qualtrics embedded fields F-<task>-<attr> / F-<task>-<profile>-<attr>. Level
##text as recorded. The randomizers shuffle the attribute rows once per respondent (the same order
##on every screen: checked), kept as attrpos_* (1 = top row).
##Level weights from the PHP randomizers: gender Woman/Man/Non-binary 0.45/0.45/0.10 (both
##universities); UNM race/ethnicity White 0.35, Hispanic or Latino 0.35, Black or African
##American, Asian, American Indian or Alaska Native 0.10 each; everything else uniform. UNM
##restriction: Heritage "Non U.S. Citizen" never with race "American Indian or Alaska Native"
##(checked in all UNM data). UNR: no restriction. Only faculty randomizers are deposited; the
##student data show the same level set, shares and (UNM) missing pair, so the student tables are
##recorded as observed rather than documented.
##Sample: as the authors (read_qualtrics.R): consent given (Q1.2 = 1), survey finished (V5 = 1),
##and no blank conjoint field. Unanswered tasks of those respondents are omitted (rows with no
##outcome). Respondents who stopped part-way are not included, as in the paper.
##Covariates (answer text from each questionnaire PDF; blank -> NA): cov_gender (Man -> male, Woman
##-> female, Non-binary -> other), cov_race (race/ethnicity, the questionnaire's own categories);
##students also cov_parent_college ("Did either of your parents, or both, attend college?" Yes/No;
##note the codes are reversed between UNM and UNR, mapped from each PDF) and cov_parent_income
##(parents' total income band; UNM has "Don't know"); cov_duration_sec = EndDate - StartDate
##(minutes resolution in the export). Dropped: Qualtrics ResponseID (re-keyed), the display items
##(Q1.1, Q2.1, Q2.3, ...), consent.
##N: UNM faculty 870, UNM students 1,387, UNR faculty 203, UNR students 622 respondents; all
##tasks answered. The authors' saved estimates (figures/_csv/*All*.csv, nobs) have one fewer in
##each sample (869, 1,386, 202, 621): their reader loses the first data row of every export (with
##that respondent dropped, OLS reproduces their UNM-faculty AMCEs exactly: Woman 0.106, Non-binary
##0.056). That respondent is kept here. The article text was not read.
##Spot check: OLS of choice on all attributes, SEs clustered by id, UNM faculty: Woman 0.106 (SE
##0.008), American Indian or Alaska Native 0.213 (0.017) vs the authors' 0.106 (0.008), 0.213 (0.017).
library(data.table)
a <- commandArgs(TRUE); raw <- file.path(a[1], "ReplicationPackage", "data"); out <- a[2]
rd <- function(f) {
  x <- fread(file.path(raw, f), header = FALSE, colClasses = "character", encoding = "UTF-8")
  setnames(x, sub("^﻿", "", unlist(x[1]))); x[-(1:2)]
}
lab <- function(x, l) { x[x == ""] <- NA; stopifnot(all(is.na(x) | x %in% names(l))); unname(l[x]) }
gender <- c("1" = "male", "2" = "female", "3" = "other")
race_unm_fac <- c("1" = "American Indian or Alaska Native", "2" = "Asian", "3" = "Black or African American",
                  "4" = "Hispanic or Latino", "5" = "Native Hawaiian or Other Pacific Islander", "6" = "White", "7" = "Other")
race6 <- c("1" = "Native American", "2" = "Asian", "3" = "Black", "4" = "Hispanic", "5" = "White", "6" = "Other")
inc <- c("1" = "Less than $25,000", "2" = "$25,000 - $49,999", "3" = "$50,000 - $74,999", "4" = "$75,000 - $99,999",
         "5" = "$100,000 - $149,999", "6" = "$150,000 - $199,999", "7" = "$200,000 - $299,999",
         "8" = "$300,000 - $499,999", "9" = "$500,000 or higher")
inc_unm <- c(sub(" - \\$", " – ", inc), "10" = "Don't know")   # UNM PDF prints "$25,000 – 49,999"
anm <- c("Gender" = "gender", "Race/Ethnicity" = "race", "Heritage" = "heritage", "Research Record" = "research",
         "Teaching Record" = "teaching", "Received PhD From" = "phd", "Received Ph.D. From" = "phd",
         "Spouse/Partner is a Current or Potential Faculty Member" = "spouse_faculty",
         "Community Engagement/Service Record" = "service", "Department/Program" = "department",
         "Faculty Position Being Considered For" = "position", "Received Undergraduate Degree From" = "undergrad")
specs <- list(
  carey_2020_hiring_unm_faculty = list(f = "Campus_Diversity_Project__UNM_Faculty_Recruitment_by_Faculty.csv", K = 8,
    cov = list(cov_gender = c("Q3.9", "g"), cov_race = c("Q3.13", "race_unm_fac"))),
  carey_2020_hiring_unm_students = list(f = "Campus_Diversity_Project__UNM_Faculty_Recruitment_by_Students.csv", K = 8,
    cov = list(cov_gender = c("Q3.13", "g"), cov_race = c("Q3.15", "race6"), cov_parent_college = c("Q3.19", "pc_unm"),
               cov_parent_income = c("Q3.23", "inc_unm"))),
  carey_2020_hiring_unr_faculty = list(f = "Campus_Diversity_Project__UNR_Faculty_Recruitment_by_Faculty.csv", K = 10,
    cov = list(cov_gender = c("Q3.7", "g"), cov_race = c("Q3.9", "race6"))),
  carey_2020_hiring_unr_students = list(f = "Campus_Diversity_Project__UNR_Faculty_Recruitment.csv", K = 10,
    cov = list(cov_gender = c("Q3.13", "g"), cov_race = c("Q3.15", "race6"), cov_parent_college = c("Q3.19", "pc_unr"),
               cov_parent_income = c("Q3.23", "inc"))))
maps <- list(g = gender, race_unm_fac = race_unm_fac, race6 = race6, inc = inc, inc_unm = inc_unm,
             pc_unm = c("1" = "Yes", "2" = "No"), pc_unr = c("1" = "No", "2" = "Yes"))
expect_n <- c(carey_2020_hiring_unm_faculty = 870, carey_2020_hiring_unm_students = 1387,
              carey_2020_hiring_unr_faculty = 203, carey_2020_hiring_unr_students = 622)
for (nm in names(specs)) {
  sp <- specs[[nm]]; s <- rd(sp$f); K <- sp$K
  fcols <- grep("^F-", names(s), value = TRUE)
  nA <- length(fcols) / K / 3
  stopifnot(nA == round(nA))
  s <- s[V5 == "1" & Q1.2 == "1"]
  s <- s[s[, rowSums(.SD == "") == 0, .SDcols = fcols]]
  s[, id := seq_len(.N)]
  resp <- paste0("Q2.", seq(4, by = 3, length.out = K))
  stopifnot(all(resp %in% names(s)))
  L <- rbindlist(lapply(1:K, function(t) rbindlist(lapply(1:2, function(p) rbindlist(lapply(1:nA, function(k)
    data.table(id = s$id, task = t, profile = p, pos = k, attr = anm[s[[paste0("F-", t, "-", k)]]],
               lev = s[[paste0("F-", t, "-", p, "-", k)]])))))))
  stopifnot(!anyNA(L$attr), all(L$lev != ""), L[, uniqueN(attr), .(id, task, profile)][, all(V1 == nA)])
  ord <- L[profile == 1][order(id, task, pos)][, .(o = paste(attr, collapse = "|")), .(id, task)]
  stopifnot(ord[, uniqueN(o), id][, all(V1 == 1)])
  d <- dcast(L, id + task + profile ~ attr, value.var = "lev")
  setnames(d, setdiff(names(d), c("id", "task", "profile")), paste0("attr_", setdiff(names(d), c("id", "task", "profile"))))
  P <- dcast(L[profile == 1], id + task ~ attr, value.var = "pos")
  setnames(P, setdiff(names(P), c("id", "task")), paste0("attrpos_", setdiff(names(P), c("id", "task"))))
  d <- merge(d, P, by = c("id", "task"))
  ch <- rbindlist(lapply(1:K, function(t) data.table(id = s$id, task = t, v = s[[resp[t]]])))
  stopifnot(all(ch$v %in% c("1", "2", "")))
  d <- merge(d, ch[v != ""], by = c("id", "task"))
  d[, choice := as.integer(profile == as.integer(v))][, v := NULL]
  if (grepl("unm", nm)) stopifnot(d[attr_heritage == "Non U.S. Citizen" & attr_race == "American Indian or Alaska Native", .N] == 0)
  for (cv in names(sp$cov)) d[, (cv) := lab(s[[sp$cov[[cv]][1]]], maps[[sp$cov[[cv]][2]]])[match(id, s$id)]]
  tm <- function(x) as.POSIXct(x, format = "%m/%d/%y %H:%M", tz = "UTC")
  d[, cov_duration_sec := as.integer(difftime(tm(s$V4), tm(s$V3), units = "secs"))[match(id, s$id)]]
  setcolorder(d, c("id", "task", "profile", "choice"))
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(d$id) == expect_n[[nm]], max(d$id) == uniqueN(d$id))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(nm, ".csv")))
  cat(nm, uniqueN(d$id), "respondents", nrow(d), "rows\n")
}
