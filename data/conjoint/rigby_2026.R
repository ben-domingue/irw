##Australian university students' choice among three essays offered for purchase (contract cheating) or buying none,
##from the data set
##Rigby, D. (2026). Data for the paper "Responsive Regulation and Heterogeneity in Students' Willingness to Contract
##Cheat" [Data set]. University of Manchester (figshare). https://doi.org/10.48420/33834790 (CC BY 4.0, figshare record
##licence). The article is not yet locatable; the related UK study (Rigby et al. 2015, J. Econ. Behav. Organ.) used a
##similar essay DCE but other levels, so it is not used as a source for this deposit's levels.
##Files read: ausccprotno26forjournal.csv (13,600 rows = 340 respondents x 10 sets x 4 alternatives, 158 columns).
##Usage: Rscript rigby_2026.R <dir holding the csv> <output dir>
##
##Design (record description: "survey data from 340 Australian university students. Includes a discrete choice
##experiment on essay buying"): 10 sets per respondent (set 1-10; display order of sets not documented, task = set),
##alternatives 1-3 are essays (profiles 1-3, recorded) and alternative 4 (none = 1) has price, risk and penalty 0: the
##"buy none" option, treated as the opt-out (no profile row). The deposit codes alternative 4's grade as the
##respondent's own predicted grade (gr on alt 4 = owngrade, a modelling device), so it is not a shown level. choice
##(1-4, the chosen alternative, constant within set) and choi (= alt == choice, checked) agree; exactly one
##alternative per set. Essay levels vary across respondents within set x alternative (randomized or many blocks;
##undocumented).
##CODED ATTRIBUTES (#3474). No codebook, questionnaire or article gives the displayed text. Kept as deposited, named
##after the deposit's variables:
##  attr_price_code: 50 / 100 / 150 / 250 / 500 / 1000 (price; currency not stated, presumably AUD).
##  attr_gr_code: 1-4 (grade of the essay). The authors' dummy names map gr 2 = graM, 3 = graD, 4 = graHD (gra3/gra4/
##    gra5), i.e. probably Merit / Distinction / High Distinction, gr 1 = gra2; the displayed wording is not deposited.
##  attr_risk_code: 1-3 (detection risk). NOTE the authors' own dummies do not follow the code order: risk 1 = xrisk1,
##    risk 2 = xrisk3, risk 3 = xrisk2, and the combined code rp uses 0/2/1 for risk 1/2/3 -- so the code numbers need
##    not rank the risk; each code is still one level.
##  attr_pen_code: 1 / 2 (penalty if detected; pen1/pen2 dummies; meaning not deposited).
##Outcome: choice among three essays and none; wording not deposited; opt_out = yes.
##Covariates (constant within respondent): cov_age (years, as recorded), cov_ausgen_code (1-4, unlabelled),
##cov_englang_code (1/2), cov_student_code (1/2), cov_year_code (1-8, year of study?), cov_owngrade_code (0-4) and
##cov_predgrade_code (1-5) (unlabelled). Dropped: free text (year_8_other, protnopay_7_other, protallpay_3_other,
##defensadd), the attitude/risk-attitude item batteries (attitudes1/2_r*, risk_r*, att1q*/att2q*, unlabelled), the
##derived Dark Triad scales (psych, narc, mach) and risk scores, every dummy and derived design column (gra*, gr*,
##xrisk*, pen0-2, rp*, risk1000/100, p1000, pr, hr, cheap, sqall, buy*, allnone, none, choi), idn/n/myrand/draw
##(undocumented), consent/semester (constant), ethnicity/ctrystudy (all NA). No exclusions applied.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "ausccprotno26forjournal.csv"))
stopifnot(nrow(k) == 13600L, uniqueN(k$id) == 340L, k[, .N, .(id, set)][, all(N == 4L)], uniqueN(k$set) == 10L)
stopifnot(all(k$choi == (k$alt == k$choice)), k[, .(s = sum(choi), u = uniqueN(choice)), .(id, set)][, all(s == 1L & u == 1L)])
stopifnot(k[alt == 4L, all(price == 0L & risk == 0L & pen == 0L & none == 1L)], k[alt < 4L, all(none == 0L)])
stopifnot(k[alt == 4L, all(gr == owngrade)])
cv <- c("age", "ausgen", "englang", "student", "year", "owngrade", "predgrade")
stopifnot(k[, lapply(.SD, uniqueN), id, .SDcols = cv][, all(as.matrix(.SD) == 1L), .SDcols = cv])
p <- k[alt < 4L]
stopifnot(all(p$price %in% c(50L, 100L, 150L, 250L, 500L, 1000L)), all(p$gr %in% 1:4), all(p$risk %in% 1:3),
          all(p$pen %in% 1:2))
d <- p[, .(id = match(id, sort(unique(k$id))), task = as.integer(set), profile = as.integer(alt), choice = as.integer(choi),
  attr_price_code = as.integer(price), attr_gr_code = as.integer(gr), attr_risk_code = as.integer(risk),
  attr_pen_code = as.integer(pen), cov_age = as.integer(age), cov_ausgen_code = as.integer(ausgen),
  cov_englang_code = as.integer(englang), cov_student_code = as.integer(student), cov_year_code = as.integer(year),
  cov_owngrade_code = as.integer(owngrade), cov_predgrade_code = as.integer(predgrade))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "rigby_2026_contract_cheating.csv"))
cat(nrow(d), uniqueN(d$id), d[, sum(choice), .(id, task)][, mean(V1 == 0)], "\n")
