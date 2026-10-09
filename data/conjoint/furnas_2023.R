##Congressional-staff factorial vignette (2017 Congressional Capacity Survey) from
##Furnas, A. C., LaPira, T. M., Hertel-Fernandez, A., Drutman, L., & Kosar, K. R. (2023). More
##than mere access: An experiment on moneyed interests, information provision, and legislative
##action in Congress. Political Research Quarterly, 76(1), 348-364 (online 2022-05-13).
##https://doi.org/10.1177/10659129221098743
##Replication data: Harvard Dataverse doi:10.7910/DVN/R693MD, CC0 1.0, no restricted files.
##File read: MoreThanMereAccessData.csv (Dataverse "original format"; the only file in the
##deposit; no codebook or code).
##Usage: Rscript furnas_2023.R <raw dir> <output dir>
##
##437 congressional staffers (anonymized 2017 Congressional Capacity Survey, deposit description)
##each read ONE vignette (task 1, profile 1) about a request for a meeting. Three slots were
##randomized; their text is stored in the data as the sentence fragments shown (kept verbatim,
##trailing full stops included):
##  attr_ident  "constituent." / "donor to your Member's election campaign." / "lobbyist
##              representing a large, national business." / "lobbyist representing a national
##              consumer group."  (who asks)
##  attr_action "propose a new bill." / "stop a bill currently under consideration."
##  attr_info   "evidence of how their proposal would help jobs and employment in your
##              constituency from a center-left think-tank." / "... from a center-right
##              think-tank." / "... from an analysis they conducted." / "polling from your
##              constituency that shows support for their position."
##The rest of the vignette prose is not in the deposit and the article was not reachable, so
##the frame around the slots and the question wording are unknown. All 32 cells occur (20-35
##respondents per ident x info cell).
##Outcomes (wording paraphrased from the variable names and the article abstract): four 5-point
##likelihood ratings of the request, stored in the source as answer text and coded here
##1 Very unlikely, 2 Somewhat unlikely, 3 Neither, 4 Somewhat likely, 5 Very likely
##(higher = more likely; the option order is the answer text's own):
##  rating                    takemeeting        (take the meeting)
##  rating_use_info           useinfo            (use the information offered)
##  rating_recommend          recommendtoboss    (recommend the requested position to the Member)
##  rating_representative     representativeness (the request reflects constituents' views)
##3 respondents with a missing outcome keep their other answers (NA there); none has all four
##missing.
##Covariates: cov_survey_weight = psweight; codes with no label source keep the _code suffix:
##cov_chamber_code (chamber_ls2, 0/1), cov_office_type_code (officetype2, 1-3), cov_partyid_code
##(partyid, 0-6). Dropped: ccsid (survey ID; re-keyed to integers in file order), q19_1..q19_5
##(an agree-disagree battery with no wording in the deposit), know_sub_st (a derived 0-1
##knowledge score).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "MoreThanMereAccessData.csv"), na.strings = c("NA", ""))
stopifnot(!anyDuplicated(r$ccsid))
lk <- c("Very unlikely", "Somewhat unlikely", "Neither", "Somewhat likely", "Very likely")
cd <- function(x) { i <- match(x, lk); stopifnot(all(is.na(x) | !is.na(i))); i }
d <- r[, .(id = seq_len(.N), task = 1L, profile = 1L,
  rating = cd(takemeeting), rating_use_info = cd(useinfo), rating_recommend = cd(recommendtoboss),
  rating_representative = cd(representativeness),
  attr_ident = ident, attr_action = action, attr_info = info,
  cov_survey_weight = psweight, cov_chamber_code = chamber_ls2, cov_office_type_code = officetype2,
  cov_partyid_code = partyid)]
stopifnot(!anyNA(d[, .(attr_ident, attr_action, attr_info)]), uniqueN(d$attr_ident) == 4,
          uniqueN(d$attr_action) == 2, uniqueN(d$attr_info) == 4)
d <- d[!(is.na(rating) & is.na(rating_use_info) & is.na(rating_recommend) & is.na(rating_representative))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "furnas_2023_staff_access.csv"))
