##Black vs white Democratic primary candidate conjoints (US, Lucid) from
##Mikkelborg, A. C. (2025). White Democrats' growing support for Black politicians in the era of
##the "Great Awokening." American Political Science Review. https://doi.org/10.1017/S0003055425000097
##Replication data: Harvard Dataverse doi:10.7910/DVN/LMBY8P, CC0 1.0, no restricted files.
##Files read: study1.csv, study2.csv, study3.csv, study4.csv ("anonymized data for original Lucid
##study 1-4", ReadMe.txt) and their study<k>_codebook.xlsx; appendix.pdf (deposited) gives the
##design and question wording; 1_clean.R was read as text (study 2 age codes).
##Usage: Rscript mikkelborg_2025.R <raw dir> <output dir>
##
##FOUR TABLES, one per original Lucid study (different attribute sets, separate fieldings):
##  mikkelborg_2025_primary_lucid1 (2022), _lucid2 (2023), _lucid3 (2023), _lucid4 (2023).
##Each respondent saw ONE pair of hypothetical Democratic congressional primary candidates (task =
##1). The deposits hold WHITE respondents only (appendix Table B1 reports Black respondents too).
##choice: "Which candidate for Congress would you support in this Democratic Primary election?"
##(Candidate A, Candidate B), forced, no opt-out (appendix Table C1).
##Restrictions (appendix "Additional information on conjoint study design"): candidate race was
##always assigned so that one candidate was Black and the other white; the two candidates could not
##have the same endorsement; other attributes equal-probability. Level text is as stored; the
##policy levels in studies 1-2 ("Ban fossil fuels", "All Americans") are shorter than the full
##sentences stored for study 4 ("Ban the use of fossil fuels after 2040, reducing economic growth
##by 5%"), so the stored text for studies 1-2 may abbreviate what respondents saw.
##Profile: study 1 records Candidate A/B (`candidate`). Studies 2-4 have two rows per respondent
##and no A/B column: profile = row order within respondent (INFERRED, unverifiable).
##Study 1 (469 white Democrats = Table B1): attributes race, job, experience, endorsement,
##  healthcare ("Publicly funded healthcare for ..."), climate (fossil fuels), reparations, age.
##  Ratings of each candidate, stored 0-1 in steps of 0.25 as deposited:
##  rating_favor "Do you have a favorable or unfavorable opinion of [CANDIDATE]?" 0 = Very
##    unfavorable .. 1 = Very favorable;
##  rating_ideology "how would you describe [CANDIDATE]'s political views in general?" 0 = Very
##    liberal .. 1 = Strongly conservative (direction is not favourability);
##  rating_goodjob / goodchance / repsme / repsgroups / demvotes / swingvotes: "Please indicate how
##    well you feel each phrase describes [CANDIDATE]: Would do a good job if elected / Has a good
##    chance of winning the general election / Represents people like me / Represents historically
##    underrepresented groups / Would perform well with loyal Democratic voters / Would perform well
##    with swing voters", 0 = Not well at all .. 1 = Extremely well.
##Study 2 (2,000 white respondents of all parties; the paper's analyses use Democrats, pid
##  5-7): two between-subject versions (trial_version): "Policy" shows healthcare, climate and
##  reparations positions; "Self-placement" shows the candidate's self-described ideology instead
##  (the other attributes are "(not shown)"). Age is stored as codes 1-5 = 44/47/50/55/58 (authors'
##  1_clean.R). Same six "describes" ratings as study 1 (0-1). One respondent has no answers and
##  is dropped: 1,999 (1,852 Democrats, pid 5-7 = Table B1's white Democrats).
##Study 3 (273 respondents who did the conjoint first; the deposit holds only those, codebook):
##  race, job, experience, endorsement, ideology (self-described), age. One respondent has
##  neither profile chosen and is dropped: 272.
##Study 4 (153 respondents in the control form = Table B1): race, gender, job, experience, age,
##  endorsement, fossil-fuel, healthcare, reparations positions (full sentences).
##Covariates (codebooks study<k>_codebook.xlsx): cov_age01 = age rescaled 0-1 (0 = 18, 1 = oldest
##in the sample: 83, 97, 93 in studies 1-3); cov_age (years, study 4); cov_gender (female, "Respondent
##gender (from Lucid)", codebook "0 = Male; 1 = Female" in all four studies); cov_region (study 3
##codes 1=Midwest 2=Northeast 3=South 4=West, text elsewhere); cov_education (educ, "Respondent
##education", as the codebook's text for the authors' 5-step coding: 0 "Less than high school",
##0.25 "High school", 0.5 "Some college, vocational school, or Associate's degree", 0.75
##"Bachelor's degree", 1 "Post-secondary degree"; the raw Lucid categories are not deposited);
##cov_hhinc 0 = $25k or less .. 1 = $150k or more (5 steps); cov_strength_dem (study 1: 0 = lean,
##.5 = mostly, 1 = strong Democrat; a strength follow-up, kept); cov_party_id7 (studies 2-4: pid,
##X1_pid in study 3, "How would you describe your political party identification?", as each
##study's codebook text: 1 "Strong Republican", 2 "Mostly Republican", 3 "Lean Republican",
##4 "Independent/other political affiliation" (study 4: "Independent/other affiliation/refused"),
##5 "Lean Democrat", 6 "Mostly Democrat", 7 "Strong Democrat"); cov_ideo (study 2) 1 = Very
##conservative .. 7 = Very liberal. The instruments have an instructed-response attention check
##("please select 'I have a question'"), but no deposited file records it; no survey weight is
##deposited per respondent (the appendix's weights are computed in the authors' code from
##genderageregionweights.csv targets, not stored). One task, so no repeated task.
##Dropped: post-treatment attitude batteries (racial resentment, self-monitoring, discrimination,
##thermometers, white identity/guilt/shame, policy views), the authors' indices and derived
##distances (canddistance, realdirdiff, candselfplacement_numfull, won is used as choice in
##study 1), respondent row ids (re-keyed). NOT BUILT: study5.csv (Lucid 5: one row per profile with
##no respondent or pair key, pairs not recoverable from row order) and ca_omnibus.csv (California
##voter study: candidate job missing for every second profile; Qualtrics ResponseIds).
##N vs appendix Table B1 (white respondents): Lucid 1 469 = 469; Lucid 2 1,999 kept, of whom
##1,852 Democrats = Table B1; Lucid 3 272 kept, 253 of them Democrats (pid 5-7) vs 254 in
##Table B1; Lucid 4 153 = 153 (136 Democrats, 17 with no pid). Table B1 counts are Democrats.
##Spot check: share of Black profiles chosen (Lucid 2 Democrats) 0.56, cf. the pooled Black
##marginal mean 0.56 in appendix Table B2 (pooled, so only indicative).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) fread(file.path(raw, f), na.strings = c("", "NA"))
fin <- function(d, name) {
  stopifnot(d[, .N, .(id, task, profile)][, all(N == 1)], d[, .N, id][, all(N == 2)],
            d[!is.na(choice), sum(choice), id][, all(V1 == 1)], d[, uniqueN(attr_race), id][, all(V1 == 2)],
            !anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
  setorder(d, id, task, profile); fwrite(d, file.path(out, paste0(name, ".csv")))
}
pr <- function(x) { stopifnot(x[, .N, X][, all(N == 2)]); x[, profile := seq_len(.N), X][, id := match(X, unique(X))] }
edu <- function(x) { stopifnot(all(x %in% c(0, .25, .5, .75, 1, NA)))
  c("Less than high school", "High school", "Some college, vocational school, or Associate's degree",
    "Bachelor's degree", "Post-secondary degree")[match(x, c(0, .25, .5, .75, 1))] }
sex <- function(x) { stopifnot(all(x %in% c(0, 1, NA))); c("male", "female")[x + 1] }
pid7 <- function(x, four = "Independent/other political affiliation") { stopifnot(all(x %in% c(1:7, NA)))
  c("Strong Republican", "Mostly Republican", "Lean Republican", four, "Lean Democrat", "Mostly Democrat", "Strong Democrat")[x] }
rt <- c("goodjob", "goodchance", "repsme", "repsgroups", "demvotes", "swingvotes")
## study 1
s <- rd("study1.csv")
stopifnot(s[, .N, respondent][, all(N == 2)], all(s$candidate %in% c("A", "B")), all(s$won %in% c("TRUE", "FALSE", TRUE, FALSE)))
d <- s[, .(id = as.integer(respondent), task = 1L, profile = match(candidate, c("A", "B")),
           choice = as.integer(as.logical(won)), rating_favor = favor, rating_ideology = placement)]
for (v in rt) d[, paste0("rating_", v) := s[[v]]]
d[, `:=`(attr_race = s$race, attr_age = as.character(s$candage), attr_job = s$job, attr_experience = s$exp,
         attr_endorsement = s$endorse, attr_healthcare = s$health, attr_climate = s$climate, attr_reparations = s$reparations,
         cov_age01 = s$age, cov_gender = sex(s$female), cov_region = s$region, cov_education = edu(s$educ), cov_hhinc = s$hhinc,
         cov_strength_dem = s$strength_dem)]
fin(d, "mikkelborg_2025_primary_lucid1")
## study 2
s <- pr(rd("study2.csv"))
stopifnot(all(s$candage %in% 1:5), all(s$treat %in% c("Policy", "Self-placement")),
          s[treat == "Policy", !anyNA(healthcare) & all(is.na(candselfplacement))],
          s[treat == "Self-placement", all(is.na(healthcare)) & !anyNA(candselfplacement)])
d <- s[, .(id = as.integer(id), task = 1L, profile = as.integer(profile), choice = as.integer(chosen_candidate))]
for (v in rt) d[, paste0("rating_", v) := s[[v]]]
d[, `:=`(attr_race = s$race, attr_age = c("44", "47", "50", "55", "58")[s$candage], attr_job = s$job,
         attr_experience = s$experience, attr_endorsement = s$endorsement, attr_healthcare = s$healthcare,
         attr_climate = s$climate, attr_reparations = s$reparations, attr_ideology = s$candselfplacement,
         trial_version = s$treat, cov_age01 = s$age, cov_gender = sex(s$female), cov_region = s$region, cov_education = edu(s$educ),
         cov_hhinc = s$hhinc, cov_party_id7 = pid7(s$pid), cov_ideo = s$ideo)]
pol <- c("attr_healthcare", "attr_climate", "attr_reparations")
stopifnot(d[trial_version == "Policy", !anyNA(.SD) & all(is.na(attr_ideology)), .SDcols = pol],
          d[trial_version == "Self-placement", all(is.na(unlist(.SD))) & !anyNA(attr_ideology), .SDcols = pol])
for (v in pol) d[trial_version == "Self-placement", (v) := "(not shown)"]
d[trial_version == "Policy", attr_ideology := "(not shown)"]
oc <- grep("^(choice|rating_)", names(d), value = TRUE)
d <- d[rowSums(!is.na(d[, ..oc])) > 0]
stopifnot(uniqueN(d$id) == 1999)
fin(d, "mikkelborg_2025_primary_lucid2")
## study 3
s <- pr(rd("study3.csv"))
s <- s[s[, .(ok = sum(chosen_candidate) == 1), X], on = "X"][ok == TRUE]
stopifnot(uniqueN(s$X) == 272)
s[, id := match(X, unique(X))]
d <- s[, .(id = as.integer(id), task = 1L, profile = as.integer(profile), choice = as.integer(chosen_candidate),
           attr_race = race, attr_age = as.character(candage), attr_job = job, attr_experience = exp, attr_endorsement = group,
           attr_ideology = ideo, cov_age01 = age, cov_gender = sex(female), cov_region = region, cov_education = edu(educ), cov_hhinc = hhinc,
           cov_party_id7 = pid7(X1_pid))]
fin(d, "mikkelborg_2025_primary_lucid3")
## study 4
s <- pr(rd("study4.csv"))
stopifnot(all(s$form == "Control"))
d <- s[, .(id = as.integer(id), task = 1L, profile = as.integer(profile), choice = as.integer(chosen_candidate),
           attr_race = race, attr_gender = gender, attr_age = as.character(candidate_age), attr_job = job,
           attr_experience = experience, attr_endorsement = endorsement, attr_climate = fossil, attr_healthcare = healthcare,
           attr_reparations = reparations, cov_age = age, cov_gender = sex(female), cov_region = region, cov_education = edu(educ),
           cov_hhinc = hhinc, cov_party_id7 = pid7(pid, "Independent/other affiliation/refused"))]
fin(d, "mikkelborg_2025_primary_lucid4")
