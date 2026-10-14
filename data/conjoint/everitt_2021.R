##Candidate sexual orientation and marital status survey experiment from
##Everitt, J., & Horvath, L. (2021). Public attitudes and private prejudices: Assessing voters' willingness
##to vote for out lesbian and gay candidates. Frontiers in Political Science, 3, 662095.
##https://doi.org/10.3389/fpos.2021.662095
##Replication data: figshare doi:10.6084/m9.figshare.14790915 (v1), CC BY 4.0. Files read: "Study master Oct 16.sav"
##(value labels read with haven), "Frontiers script release.R" (read as text, not run).
##Usage: Rscript everitt_2021.R <dir holding the .sav, saved as master.sav> <output dir>
##
##Canadian online panel (Quest Mindshare, quota sample, 25-27 Sept 2018), 1,014 submitted. Design (paper, Methods):
##within-subject, two screens. Screen 1: a 350-word news story about a local person seeking a nomination, with the
##candidate's GENDER manipulated (David Kenney "he" / Donna Kenney "she"); respondent rates willingness to vote.
##Screen 2: a biography adds the candidate's SEXUAL ORIENTATION (a partner named Denis/Denise, so a gay or lesbian
##candidate) and FAMILIAL STATUS (partner "wife/husband and partner of 18 years", with children, vs a former
##boyfriend/girlfriend, single, childless), then the respondent rates again. The 2 x 2 x 2 cell is the
##`study` code (1 f/s/m ... 8 m/g/s) = candidategender, candidateso, candidaterel (value labels in the .sav).
##Table: 2 tasks per respondent, 1 profile each. Task 1 = screen 1 (orientation and marital status "(not shown)"),
##task 2 = screen 2 (all three attributes). Gender is therefore shown in both tasks and constant within respondent.
##  rating = vote1 / vote2, "likelihood of voting" for the candidate, 1-10 (the paper: "ten-point ordinal scale";
##           exact wording and anchors are not in the deposit; direction taken as higher = more willing).
##A task with a missing rating is omitted (100 missing vote1, 105 missing vote2); 888 respondents have both,
##the paper's analysed N. No opt-out. Level text: gender from the paper (name + pronoun); orientation from the
##.sav labels ("lesbian or gay"/"straight"); marital status paraphrased from the paper.
##Dropped: knowledge quiz (Q8), feeling thermometers (Q9), trait batteries NS1Q/NS2Q (candidate ratings of
##traits, other outcomes not kept), opinion items, derived scales and differences, the filter variable, V96,
##Q22 (free-typed ethnicity), submit dates, language. Covariates: cov_gender (Q1: male/female; "other" kept as
##other), cov_birth_year (Q2), cov_education (Q4 .sav label text), cov_party_id (Q17, label text of the
##A1..A5 codes: Liberal, Conservative, N.D.P., Green, None of these), cov_sexual_orientation (Q23 label text,
##prefer-not-to-say = NA). Respondents are re-keyed to integers (the file's `id` is a survey-platform row id).
##No survey weight. Randomization: balanced 8-cell assignment (123-142 per cell); restrictions none stated.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_sav(file.path(raw, "master.sav")))
stopifnot(nrow(d) == 1014)
d[, rid := .I]
lab <- function(x) as.character(as_factor(x, levels = "labels"))
gen <- c("Donna Kenney (she)", "David Kenney (he)")[d$candidategender + 1L]
so  <- c("lesbian or gay", "straight")[d$candidateso + 1L]
mar <- c("single (a former boyfriend/girlfriend)", "married (wife/husband and partner of 18 years, with children)")[d$candidaterel + 1L]
stopifnot(!anyNA(gen), !anyNA(so), !anyNA(mar))
q1 <- lab(d$Q1); q1[q1 == "other"] <- "other"
party <- c(A1 = "Liberal", A2 = "Conservative", A3 = "N.D.P.", A4 = "Green", A5 = "None of these")[as.character(d$Q17)]
q23 <- lab(d$Q23); q23[q23 %in% c("prefer not to say")] <- NA
cov <- data.table(cov_gender = q1, cov_birth_year = as.integer(d$Q2), cov_education = lab(d$Q4),
  cov_party_id = unname(party), cov_sexual_orientation = q23)
cov[cov_gender == "", cov_gender := NA]
cov[cov_education == "", cov_education := NA]
cov[cov_sexual_orientation == "", cov_sexual_orientation := NA]
t1 <- data.table(id = d$rid, task = 1L, profile = 1L, rating = as.integer(d$vote1), attr_candidate_gender = gen,
                 attr_candidate_orientation = "(not shown)", attr_candidate_marital_status = "(not shown)")
t2 <- data.table(id = d$rid, task = 2L, profile = 1L, rating = as.integer(d$vote2), attr_candidate_gender = gen,
                 attr_candidate_orientation = so, attr_candidate_marital_status = mar)
r <- rbind(cbind(t1, cov), cbind(t2, cov))[!is.na(rating)]
setorder(r, id, task, profile)
fwrite(r, file.path(out, "everitt_2021_candidate_orientation.csv"))
