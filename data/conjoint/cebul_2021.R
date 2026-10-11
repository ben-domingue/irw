##US-China crisis vignette experiment (credibility of threats and assurances) from
##Cebul, M. D., Dafoe, A., & Monteiro, N. P. (2021). Coercion and the credibility of assurances. The Journal of
##Politics, 83(3), 975-991. https://doi.org/10.1086/711132
##Replication data: Harvard Dataverse doi:10.7910/DVN/PEHPBY, CC0 1.0, no restricted files. Files read:
##Assurances_JOP_Clean.tab (the authors' cleaned analysis file, n = 1,028), Assurances_JOP_Codebook.pdf,
##Assurances_SSI_Survey.pdf (Qualtrics export of the instrument; vignette and question text), Assurances_JOP_Cleaning.R
##(as text). Usage: Rscript cebul_2021.R <dir holding clean.tab> <output dir>
##
##1,028 US adults (SSI panel, fielded 2018) advised a hypothetical US president in a Diaoyu/Senkaku crisis with China.
##Each read ONE vignette (3 independently randomized binary factors = 8 cells; one task, one profile):
##  party: US president Sutter is Democratic / Republican (GOPPresident 0 / 1)
##  power: balance of power in the region: US / China military superiority (Power 0 / 1)
##  reputation: China's record with Vietnam (Paracel Islands): abided by / tried to alter the 2020 agreement
##    (Reputation 1 / 0)
##Level text is the "In summary" bullet shown to respondents (survey PDF pages 7-9). The authors dropped respondents
##who finished in < 4 minutes or read the Reputation page in < 5 seconds (1,453 finished -> 1,028); the deposit's clean
##file is used as is. The raw file (Assurances_JOP_Raw.tab) is not read: it holds ResponseIds, timings and free text.
##Outcomes (ratings on the same vignette, stored as in the clean file; direction in the codebook):
##  rating_cred_threat: "Suppose that the United States rejects China's demand ... Do you think that China will follow
##    through on its threat to contest U.S. military presence in the region?" 0 Very Unlikely .. 4 Very Likely.
##  rating_cred_assurance: "Suppose that the United States recognizes Chinese sovereignty ... Do you think that China
##    will still attempt to contest U.S. military presence in the region at a later date?" The survey codes Very Unlikely
##    = 4 .. Very Likely = 0, so HIGHER = MORE credible assurance (China less likely to contest later), as the codebook says.
##  rating_resolve: "How should the United States respond to China's demand ...?" 0 Accept the demand (ask Japan to
##    renounce its claim); 1 Reject, but ask Japan to renounce if conflict arises; 2 Reject, but ask Japan to renounce
##    only if conflict costs > 100 American fatalities; 3 Reject even if conflict costs > 100 American fatalities.
##    HIGHER = more resolve to resist. An ordinal choice among four options, stored as a rating (not a choice among profiles).
##Covariates: cov_gender (Gender: 1 Male, 2 Female, 3 Other; survey PDF), cov_age (Age in years), cov_education_code
##(Edu = survey Education option - 1, 0 Less than high school .. 7 Professional degree; cleaning R), cov_party_id (RParty:
##0 Democrat, 1 Independent, 2 Republican, 8 = "Haven't thought much about this" kept as that text; -99 = prefer not to
##answer -> NA), cov_pol_knowledge_code (PolKnow, 0 < 5 times a year .. 4 every day), cov_military_service (MilExp 1/0).
##Dropped: ResponseId and survey_code (platform ids), race, income, derived dummies (Male, Dem, Rep, Ind).
##Count check: n = 1,028 as in the cleaning code comment.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "clean.tab"))
stopifnot(nrow(s) == 1028, !anyDuplicated(s$ResponseId), all(s$GOPPresident %in% 0:1), all(s$Power %in% 0:1), all(s$Reputation %in% 0:1))
edu <- c("Less than high school", "High school or GED", "Some college", "2-year college degree", "4-year college degree",
         "Masters degree", "Doctoral degree", "Professional degree (e.g., JD or MD)")
d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L,
  rating_cred_threat = as.integer(s$CredThreat), rating_cred_assurance = as.integer(s$CredAssurance),
  rating_resolve = as.integer(s$Resolve),
  attr_president_party = c("Democratic", "Republican")[s$GOPPresident + 1L],
  attr_military_balance = c("The U.S. enjoys military superiority over China in the region",
                            "China enjoys military superiority over the U.S. in the region")[s$Power + 1L],
  attr_china_record = c("China has tried to alter a past territorial agreement with Vietnam over the Paracel Islands",
                        "China has abided by a past territorial agreement with Vietnam over the Paracel Islands")[s$Reputation + 1L],
  cov_gender = c("male", "female", "other")[s$Gender], cov_age = as.integer(s$Age),
  cov_education = unname(edu[s$Edu + 1L]),
  cov_party_id = fcase(s$RParty == 0, "Democrat", s$RParty == 1, "Independent", s$RParty == 2, "Republican",
                       s$RParty == 8, "Haven't thought much about this", default = NA_character_),
  cov_pol_knowledge_code = as.integer(s$PolKnow), cov_military_service = as.integer(s$MilExp))
stopifnot(!anyNA(d[, .(rating_cred_threat, rating_cred_assurance, rating_resolve)]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "cebul_2021_assurances.csv"))
