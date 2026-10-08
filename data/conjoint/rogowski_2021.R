##Supreme Court nominee conjoint from
##Rogowski, J. C., & Stone, A. R. (2021). How political contestation over judicial nominations
##polarizes Americans' attitudes toward the Supreme Court. British Journal of Political Science,
##51(3), 1251-1269. https://doi.org/10.1017/S0007123419000383
##Replication data: Harvard Dataverse doi:10.7910/DVN/OXIOI9, CC0 1.0. File read: conjoint_data.RData
##(datafile 3424445, ?format=original; one data.frame `data`, loaded into its own environment).
##Read as text only: read-me.txt, replication-file.R, r-code-output.pdf; also the article's online
##Supplementary Appendix (Cambridge sup001.pdf; Tables A.1-A.2).
##Usage: Rscript rogowski_2021.R <dir holding conjoint_data.RData> <output dir>
##
##2,500 US adults (online survey fielded "in the first days of the Trump presidency" (article); the
##appendix gives N = 2,500 and 10,000 evaluations) each rated 4 hypothetical Supreme Court nominee
##profiles, one at a time (single-profile design: profile = 1). The file has no task column: each
##respondent has exactly 4 consecutive rows, and task is INFERRED from row order (the appendix
##analyses "the first nominee profile a respondent" saw, consistent with rows being in display order,
##but the deposit does not say so).
##Attributes (6), coded 1..k in the file; level text from the authors' cjoint design list
##(attribute_list in replication-file.R, makeDesign), which is in the same order as the plot labels:
##age 45/55/65; gender Male/Female; race White/Black/Hispanic or Latino/a; law school Elite/Ivy /
##Well-regarded public / Second-tier regional / Not top 100; current position Federal judge / Elected
##politician / Law professor / Think-tank / Corporate defense attorney; abortion view Roe is settled
##law / Cannot comment / Roe should be overturned. NOTE: level 4 of current position is "Think-tank"
##in the design list but "Chief counsel" in the authors' plot labels (and in every appendix figure);
##the displayed wording is not in the deposit, so the design-list text is used and the conflict flagged.
##The displayed profile wording is not in the deposit; these are the authors' labels.
##trial_rhetoric (No/Yes): respondent-level arm, whether the respondent received elite rhetoric
##statements (attributed to Trump and Senate Democrats) with the profiles; constant within respondent.
##Outcomes (single profile, so both are ratings):
##  rating = support: "On a scale from strongly oppose to strongly support, where would you place your
##    level of support for this potential nominee?" 1 = Strongly oppose ... 5 = Strongly support
##    (appendix Table A.2; 53 rows missing).
##  rating_trust = trust: "Evaluation of trust in nominee's impartiality" (read-me; wording and anchors
##    not in deposit or appendix), 1-5 (30 rows missing). Direction assumed higher = more trust (not stated).
##Dropped: legit.additive (an additive index of four 5-point legitimacy items asked after each profile;
##the items themselves are not deposited); 7 rows with neither support nor trust (rows with no
##outcome are omitted). caseid (panel case id) re-keyed to integers in source order.
##Covariates: cov_pid3 (the authors' 3-category party recode pid3a: Democrat/Independent/Republican;
##the appendix shows the source item also had Other and Not sure, so this is not the reserved
##cov_party_id), cov_survey_weight (post-stratification weight).
##No randomization restrictions are documented (makeDesign type "constraints" with none given); all
##current position x law school and abortion x position pairs occur; shares near-uniform.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "conjoint_data.RData"), envir = e)
s <- as.data.table(e$data)
stopifnot(nrow(s) == 10000, s[, .N, caseid][, all(N == 4)], uniqueN(s$caseid) == 2500)
s[, id := match(caseid, unique(caseid))][, task := seq_len(.N), id]
stopifnot(s[, uniqueN(politicized), id][, all(V1 == 1)])
L <- list(age = c("45", "55", "65"), gender = c("Male", "Female"), race = c("White", "Black", "Hispanic or Latino/a"),
          law = c("Elite/Ivy", "Well-regarded public", "Second-tier regional", "Not top 100"),
          pos = c("Federal judge", "Elected politician", "Law professor", "Think-tank", "Corporate defense attorney"),
          abort = c("Roe is settled law", "Cannot comment", "Roe should be overturned"))
d <- s[, .(id, task, profile = 1L, rating = as.integer(support), rating_trust = as.integer(trust),
           attr_age = L$age[treat_age], attr_gender = L$gender[treat_gender], attr_race = L$race[treat_race],
           attr_law_school = L$law[treat_lawS], attr_current_position = L$pos[treat_currentP],
           attr_abortion_view = L$abort[treat_pAbortion],
           cov_pid3 = as.character(pid3a), cov_survey_weight = weight,
           trial_rhetoric = c("No", "Yes")[politicized + 1])]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^trial_|^cov_")]))
d <- d[!(is.na(rating) & is.na(rating_trust))]
stopifnot(nrow(d) == 9993, all(d$rating %in% c(1:5, NA)), all(d$rating_trust %in% c(1:5, NA)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "rogowski_2021_court_nominees.csv"))
