##MLA-candidate conjoint (Bihar, India) from
##Hankla, C. R., Banerjee, S., Thomas, A., & Banerjee, A. (2022). Electing women in ethnically
##divided societies: Candidates, campaigns, and intersectionality in Bihar, India. Comparative
##Political Studies, 56(9), 1433-1469. https://doi.org/10.1177/00104140221141838
##Replication data: Harvard Dataverse doi:10.7910/DVN/RSCG2F, CC0 1.0, no restricted files.
##File read: Hankla et al CPS data.dta (Dataverse "original format" download). Design and
##candidate texts from "Intersectionality Paper - Appendices.pdf" (pre-analysis plan, survey
##instrument pp. 9-14, design pp. 41, 50); the Stata log (read as text) shows the authors'
##models: conjoint CandidateChosen on the candidate dummies, clustered on RespondNumber.
##Usage: Rscript hankla_2022.R <dir holding hankla.dta (the .dta renamed)> <output dir>
##
##2,000 Bihar voters (door-to-door, random draws from voting rolls in 8 MLA constituencies),
##4 pairs of hypothetical MLA candidates each. Enumerators show a drawing of each candidate and
##read: "This is Shrimati/Shri <surname>, who is a candidate for MLA. She/He makes the
##following appeal to voters: <appeal>". Randomized: gender (drawing + Shrimati/Shri), caste or
##religion signalled by surname (Ansari = Muslim, Pandey = forward caste, Sahu = OBC, Paswan =
##SC; the 16 candidate scripts in the instrument), appeal (security vs public goods). In two of
##the pairs the candidates also carry a party, one BJP and one RJD. Attributes stored:
##  attr_gender  "Female"/"Male" (shown by drawing and title; not said as a word)
##  attr_surname the surname read out (the authors' caste coding is above)
##  attr_appeal  the appeal text read out (instrument p. 10)
##  attr_party   "BJP"/"RJD" in the partisan pairs, "(not shown)" in the others
##The .dta holds only the authors' dummies (CandidateFemale, CandidateMuslim/Forward/OBC/SC,
##CandidateProtect, CandidateBJP/RJD); the text above is mapped from those dummies via the
##instrument. Party wording as displayed is not documented beyond "representing the BJP/RJD".
##Task and profile are INFERRED: the file has no task/profile column and is stored as 8 blocks
##of 2,000 rows (one row per respondent per block). Blocks k and k+4 form a pair (k = 1..4):
##in every complete pair exactly one profile is chosen, blocks 1-2 carry no party and blocks
##3-4 carry one BJP and one RJD candidate. task = k (block order; whether it is the order shown
##is not documented, and the documents disagree on whether 1 or 2 partisan pairs were asked),
##profile = 1 for blocks 1-4, 2 for blocks 5-8 (which side was "first" is not verifiable).
##Outcome: choice = CandidateChosen. "If these two candidates were running against each other
##for MLA, and the election were held today, which would you vote for?" No opt-out.
##Dropped: the authors' StrongPref (a 0/1 recode of a 5-point strength-of-preference question
##whose raw answers are not deposited; constant within task), tasks with a missing choice or
##missing candidate attributes (one respondent has no data at all), and 4 rows where party
##deviates from the block pattern (a party in block 2 or none in block 4): their tasks are
##dropped. Respondent covariates: cov_gender (Female, label "Female Respondent": 1 female,
##0 male), cov_age (Age, years as recorded, 18-99), cov_education_code (Education, codes 0-9,
##no labels in the deposit), cov_muslim, cov_sc, cov_obc, cov_forward_caste (0/1 respondent
##dummies, .dta variable labels), cov_caste_discrimination (CastePersonalDiscrim, label "Caste
##Dscrimination", 0/1), cov_constituency (from the 7 constituency dummies; the 8th, reference
##constituency is unnamed in the deposit: "unnamed (reference)"). AgeCatagories and
##EdCatagories (derived) are dropped. No survey weight.
##N: the article reports about 2,000 respondents; 1,999 respondents remain here.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "hankla.dta"))))
stopifnot(nrow(s) == 16000L)
s[, blk := rep(1:8, each = 2000L)]
stopifnot(s[, .N, RespondNumber][, all(N == 8)], s[, uniqueN(RespondNumber), blk][, all(V1 == 2000)])
s[, task := (blk - 1L) %% 4L + 1L][, profile := (blk - 1L) %/% 4L + 1L]
caste <- s[, fifelse(CandidateMuslim == 1, "Ansari", fifelse(CandidateForward == 1, "Pandey",
                     fifelse(CandidateOBC == 1, "Sahu", fifelse(CandidateSC == 1, "Paswan", NA_character_))))]
stopifnot(s[!is.na(CandidateMuslim), all(CandidateMuslim + CandidateForward + CandidateOBC + CandidateSC == 1)])
sec <- "People like you too often have to live in fear of persecution and even violence from other groups. If elected, I will ensure that you and people like you can feel safe in your communities again."
pg  <- "People like you too often have to suffer from a lack of basic amenities within your communities. If elected, I will ensure that you and your community experience more development."
s[, attr_gender := c("Male", "Female")[CandidateFemale + 1L]]
s[, attr_surname := caste]
s[, attr_appeal := c(pg, sec)[CandidateProtect + 1L]]
s[, attr_party := fifelse(CandidateBJP == 1, "BJP", fifelse(CandidateRJD == 1, "RJD", "(not shown)"))]
stopifnot(s[, all(CandidateBJP + CandidateRJD <= 1)])
s[, bad := is.na(CandidateChosen) | is.na(attr_gender) | is.na(attr_surname) | is.na(attr_appeal) |
       (task <= 2 & attr_party != "(not shown)") | (task >= 3 & attr_party == "(not shown)")]
s[, badtask := any(bad), .(RespondNumber, task)]
cat("tasks dropped:", s[badtask == TRUE, uniqueN(paste(RespondNumber, task))], "\n")
s <- s[badtask == FALSE]
stopifnot(s[, .(sum(CandidateChosen), .N), .(RespondNumber, task)][, all(V1 == 1 & N == 2)])
stopifnot(s[task >= 3, uniqueN(attr_party) == 2, .(RespondNumber, task)]$V1)
cn <- c("Rajnagar", "Phulparas", "Pipra", "Tribeniganj", "Sherghati", "Barachatti", "Sikandra")
m <- as.matrix(s[, ..cn]); stopifnot(all(rowSums(m) <= 1, na.rm = TRUE))
const <- apply(m, 1, function(r) if (anyNA(r)) NA_character_ else if (sum(r) == 0) "unnamed (reference)" else cn[which(r == 1)])
d <- s[, .(id = as.integer(RespondNumber), task = as.integer(task), profile = as.integer(profile),
           choice = as.integer(CandidateChosen), attr_gender, attr_surname, attr_appeal, attr_party,
           cov_gender = c("male", "female")[Female + 1L], cov_age = as.integer(Age),
           cov_education_code = as.integer(Education), cov_muslim = as.integer(Muslim), cov_sc = as.integer(SC),
           cov_obc = as.integer(OBC), cov_forward_caste = as.integer(GeneralCaste),
           cov_caste_discrimination = as.integer(CastePersonalDiscrim), cov_constituency = const)]
stopifnot(d[, uniqueN(cov_age), id][, all(V1 == 1)], all(d$cov_age >= 18 | is.na(d$cov_age)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hankla_2022_bihar_candidates.csv"))
