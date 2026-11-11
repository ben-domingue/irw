##Oregon households' choice between two Willamette Basin wild salmon and steelhead recovery programmes (recovery status,
##time to recovery, annual household tax) or the status quo, from the data set
##Papenfus, M. (2025). Stated Preference Data for Salmon Recovery [Data set]. U.S. EPA Office of Research and
##Development (ScienceHub). https://doi.org/10.23719/1532042 -- licence: U.S. public domain (EPA data licence page
##https://pasteur.epa.gov/license/sciencehub-license.html, linked as the Access & Use License on catalog.data.gov;
##17 U.S.C. 105). Article: Papenfus, M., & Weber, M. A. (2025). Valuing wild salmon and steelhead recovery in Oregon's
##most urbanized watershed. Ecological Economics, 236, 108540. https://doi.org/10.1016/j.ecolecon.2025.108540
##(paywalled; not read).
##Files read: salmon_long_finalData2.csv (7,011 rows = 790 respondents x 1-3 questions x 3 options) and
##documents/variable_definitions.txt (codebook). Also read as text: the EPA OMB supporting statement for the survey
##(ICR 201410-2080-001, omb.report), which describes the planned design.
##Usage: Rscript papenfus_2025.R <dir holding the csv> <output dir>
##
##Design: mail survey of Oregon residents (Willamette Basin and rest of state strata). Each choice question offers
##recovery options A and B and the status quo ("Respondents are asked to choose the program that they would prefer, or
##to choose the status quo (i.e. choose neither of the policy options)", OMB statement). The status quo (alt_label sq,
##option 1) carries fixed values (status 20000, time 0, cost 0) and is treated as the opt-out: no profile row; choice = 0
##on both profiles when sq was chosen. Profiles 1 = A_recovery, 2 = B_recovery (recorded). task = the question number
##Q1-Q3 (recorded); 22 respondents answered fewer than 3 questions (as deposited). Exactly one of the three options is
##chosen in every question (checked).
##CODED ATTRIBUTES (#3474). The codebook gives each column's meaning and unit but not the displayed wording; the OMB
##statement gives the planned level names, but it is a pre-fielding draft whose cost levels ($40-$300 in six levels)
##differ from the fielded ones in the data (80/150/350/450), so it is not taken as the final wording. Kept as deposited:
##  attr_status_code: 40000 / 70000 = "fish status in population number for choice option" (codebook); the OMB draft
##    calls these "Basic recovery" (20,000 -> 40,000 wild fish returning) and "High recovery" (-> 70,000).
##  attr_time_code: 15 / 25 / 50 = "time to recovery for that option (years)" (codebook).
##  attr_cost_code: 80 / 150 / 350 / 450 = cost; a permanent increase in annual household taxes in US dollars per the OMB
##    statement (the codebook gives no unit).
##Outcome: choice among A, B and the status quo; verbatim wording not deposited (paraphrase from the OMB statement);
##opt_out = yes.
##Covariates (constant within respondent, checked): cov_age (years, as recorded), cov_gender_code (0/1/2, unlabelled in
##the codebook), cov_income (codebook labels 1-7 -> text), cov_education (codebook labels 1-6 -> text, spelling as in the
##codebook), cov_wbres (1 = Willamette Basin resident, codebook), cov_county_fips (county FIPS code).
##Dropped: id (re-keyed; sid survey number also dropped), the dummy codings (fish_low/high, time_short/medium/long,
##shortBasic ... longHigh, asc_*, cost100, retired, edu_college*, inc, incMidPt, *_asc, idx.*, choiceSID*), fishPop
##(0/8/14, undocumented and one-to-one with status), srecovery (codebook: "binary indicator for either recovery option",
##but it varies within respondent on 135 of 790 and is 1 on status-quo rows; meaning unclear). No exclusions applied.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "salmon_long_finalData2.csv"))
stopifnot(nrow(k) == 7011L, uniqueN(k$id) == 790L, k[, uniqueN(sid), id][, all(V1 == 1L)])
stopifnot(k[, .(n = .N, s = sum(choice), o = paste(sort(alt_label), collapse = ",")), .(id, question)][,
  all(n == 3L & s == 1L & o == "A_recovery,B_recovery,sq")])
stopifnot(k[alt_label == "sq", all(status == 20000L & time == 0L & cost == 0L)])
stopifnot(k[, .(fp = uniqueN(fishPop)), status][, all(fp == 1L)])
cv <- c("age", "gender", "income", "edu", "wbres", "county")
stopifnot(k[, lapply(.SD, function(x) uniqueN(x)), id, .SDcols = cv][, all(as.matrix(.SD) == 1L), .SDcols = cv])
inc_lab <- c("Under $25,000", "$25000-$49,999", "$50,000-$74,999", "$75,000-$99,999", "$100,000-$149,999",
         "$150,000-$199,999", "Above $200,000")
edu_lab <- c("Less than high school", "High school or GED", "Some college (1-4 years, no degree)", "Associaties'degree",
         "Bachelor's degree", "Graduate degree")
p <- k[alt_label != "sq"]
d <- p[, .(id = match(id, sort(unique(k$id))), task = as.integer(sub("^Q", "", question)),
  profile = match(alt_label, c("A_recovery", "B_recovery")), choice = as.integer(choice),
  attr_status_code = as.integer(status), attr_time_code = as.integer(time), attr_cost_code = as.integer(cost),
  cov_age = as.integer(age), cov_gender_code = as.integer(gender), cov_income = inc_lab[income], cov_education = edu_lab[edu],
  cov_wbres = as.integer(wbres), cov_county_fips = as.integer(county))]
stopifnot(!anyNA(d$profile), !anyNA(d$task), all(d$attr_status_code %in% c(40000L, 70000L)),
          all(d$attr_time_code %in% c(15L, 25L, 50L)), all(d$attr_cost_code %in% c(80L, 150L, 350L, 450L)),
          all(is.na(p$income) | p$income %in% 1:7), all(is.na(p$edu) | p$edu %in% 1:6),
          d[, .N, .(id, task)][, all(N == 2L)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "papenfus_2025_salmon_recovery.csv"))
cat(nrow(d), uniqueN(d$id), d[, sum(choice), .(id, task)][, mean(V1 == 0)], "\n")
