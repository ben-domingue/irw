##Factorial vignettes of House candidates shown to political donors (US) from
##Meisels, M., Clinton, J. D., & Huber, G. A. (2024). Giving to the Extreme? Experimental Evidence on Donor Response to Candidate
##and District Characteristics. British Journal of Political Science. https://doi.org/10.1017/S0007123423000650
##Replication data: Harvard Dataverse doi:10.7910/DVN/Q1X3RZ, CC0 1.0, no restricted files. Files read: GTTE_DonorData.tab
##(downloaded with format=original; the ReadMe calls it GTTE_DonorData.csv), GTTE_ReadMe.pdf (variable codebook), GTTE_FiguresTables.R
##(as text; figure labels). Usage: Rscript meisels_2024.R <dir holding GTTE_DonorData.tab> <output dir>
##
##7,010 verified donors (2018 midterm donors, Democrats and Republicans only; 6,822 distinct `privateinternalid` values: 62 ids
##occur on 4 rows and 2 on 2 rows with different vignettes, so the ids collide across donors) each rated 5 vignettes of a House
##candidate. Each row is a respondent; id = row number. Donors were randomly assigned to primary-election vignettes (3,476) or
##general-election vignettes (3,534), constant within respondent: trial_election. Attributes randomized per vignette (ReadMe):
##district lean (leans toward the donor's own party / the other party / neither = toss-up; two dummies, 0/0 = toss-up per the
##authors' figure "omit: tossup"), opponent extreme vs typical, opponent incumbent vs challenger, candidate ideology relative to the
##donor (somewhat more moderate / same / somewhat more extreme / much more extreme), and four viability cues (key endorsements, raised
##substantial funds, barely lost a close House election last time, believed to have an enthusiastic district), each 0/1.
##LABELS: paraphrased from the ReadMe and the figure labels (no instrument deposited; the Cambridge article page timed out):
##displayed wording is not available, so levels are the authors' descriptions. Viability cue = 0 is stored as "(not shown)" on the
##reading that a cue not randomly assigned is simply not mentioned (the authors' baseline is "newcomer"); this is inferred, not stated.
##Outcome: rating = whether the donor reported being very likely or almost certain to contribute to the vignette candidate
##(0/1; ReadMe: dichotomized by the authors from a likelihood scale whose raw wording and scale are not in the deposit), from
##v_primary_contribute[1-5] or v_general_contribute[1-5] by arm. Vignettes with NA outcome (451 of 35,050) are dropped.
##Covariates: cov_party_id (OwnPID), cov_gender (d_female), cov_education (ReadMe codes 1-6 as text; code 9 (32 donors) -> NA),
##cov_age_group (ts_agecat, ReadMe categories; 9 -> NA), cov_net_worth (text categories), cov_race_white, cov_survey_weight
##(PooledDonorInvPropWgt inverse propensity weight; NA for 1,320 donors, kept as NA). Dropped: PCA ideology scores, extreme flag,
##e_winissues (derived/other questions), privateinternalid.
##Count check: ~7,000 donors per the article summary = 7,010 here; paper N not otherwise read.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "GTTE_DonorData.tab"), na.strings = c("NA", ""))
stopifnot(nrow(d) == 7010, d[, all(tv_districtchar_leanother1 + tv_districtchar_leanyour1 <= 1)])
d[, id := .I]
edu <- c("1" = "Less than high school", "2" = "High school", "3" = "Some college", "4" = "Associate's degree", "5" = "Bachelor's degree", "6" = "Postgraduate")
age <- c("1" = "< 35", "2" = "35-48", "3" = "49-58", "4" = "59-68", "5" = "69-78", "6" = "79-99")
rid <- c(somewhatother = "Somewhat more moderate than the donor", same = "Same ideology as the donor", somewhatmore = "Somewhat more extreme than the donor", muchmore = "Much more extreme than the donor")
res <- rbindlist(lapply(1:5, function(t) {
  g <- function(x) d[[paste0(x, t)]]
  y <- ifelse(d$tv_primary == 1, g("v_primary_contribute"), g("v_general_contribute"))
  cue <- function(x, lab) ifelse(g(x) == 1, lab, "(not shown)")
  data.table(id = d$id, task = t, profile = 1L, rating = as.integer(y),
    attr_district = ifelse(g("tv_districtchar_leanyour") == 1, "Leans toward your party", ifelse(g("tv_districtchar_leanother") == 1, "Leans toward the other party", "Toss-up")),
    attr_opponent_extremity = ifelse(g("tv_opponentextreme") == 1, "Extreme opponent", "Typical opponent"),
    attr_opponent_incumbency = ifelse(g("tv_opponentincumbent") == 1, "Incumbent opponent", "Challenger opponent"),
    attr_ideology = unname(rid[g("tv_relideo")]),
    attr_endorsements = cue("tv_viab_endorse", "Has key endorsements"),
    attr_money = cue("tv_viab_money", "Has raised substantial funds from large and small donors"),
    attr_prior_loss = cue("tv_viab_primlost", "Barely lost a close House election last time"),
    attr_enthusiasm = cue("tv_viab_enthus", "Believes the district is enthusiastic about their campaign"),
    trial_election = ifelse(d$tv_primary == 1, "primary", "general"),
    cov_party_id = d$OwnPID, cov_gender = ifelse(d$d_female == 1, "female", ifelse(d$d_female == 0, "male", NA_character_)),
    cov_education = unname(edu[as.character(d$d_education)]), cov_age_group = unname(age[as.character(d$ts_agecat)]),
    cov_net_worth = d$d_networthcat, cov_race_white = d$r_race_white, cov_survey_weight = d$PooledDonorInvPropWgt)
}))
stopifnot(!anyNA(res[, .(attr_district, attr_ideology)]))
cat("vignettes without outcome:", res[is.na(rating), .N], "\n")
r <- res[!is.na(rating)]
setorder(r, id, task, profile)
fwrite(r, file.path(out, "meisels_2024_donor_candidates.csv")); cat("rows", nrow(r), "resp", uniqueN(r$id), "\n")
