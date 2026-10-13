##Partner-profile trust-game experiment among Bosnian politicians from
##Butler, D. M., & Tavits, M. (2019). Shared interests foster interethnic cooperation among
##politicians. Political Science Research and Methods. https://doi.org/10.1017/psrm.2019.60
##Replication data: Harvard Dataverse doi:10.7910/DVN/WMIMSW, CC0 1.0. File read:
##EliteCooperation.tab (tab-separated export of EliteCooperation.dta); "Cooperation Study.do" and
##"List of Replication File.docx" read as text. There is no questionnaire or codebook in the deposit.
##Usage: Rscript butler_2019.R <dir holding EliteCooperation.tab> <output dir>
##
##1,389 Bosnian politicians/officials (an elite survey; respondents are not platform workers), each
##playing 4 rounds (task 1-4) against a hypothetical partner described by two randomized
##attributes (the .do file builds rounds from whoQ10-13_ethn, whoq10-13_gen):
##  attr_partner_ethnicity : Serb (1) / Croat (2) / Bosniak (3) -- coding of the respondent's own
##                           ethnicity q1 in the authors' code (off_serb = q1==1, off_croat = 2,
##                           off_bosniak = 3), applied to the partner's code (the code compares
##                           q1 with the partner's ethnicity code to define "non-coethnic")
##  attr_partner_gender    : male (1) / female (2) -- coding of the respondent's own q2 (female =
##                           q2==2), applied to the partner's code the same way
##The partner descriptions come from numeric codes mapped by the authors' own recode code, not from
##displayed text; HOW the partner was presented (a name, a description) is not stated in the deposit
##(presentation = unknown), so no profile_gender crosswalk row is given.
##Outcome rating = q10..q13, one value 0-10 per round (dv_game in the authors' code, the "trust
##game" outcome of their experiment 2). The wording and the unit (e.g. an amount sent out of 10) are not
##in the deposit; stored raw, higher = presumably more trusting/cooperative.
##trial_eu_benefits_asked = 1 when the respondent was also asked the EU-benefits item q6a_1 before the
##game (the authors' tr_EU_benefits, a respondent-level randomized treatment; 767 of 1,389).
##Covariates: cov_ethnicity (q1 codes mapped by the authors' code: Serb, Croat, Bosniak; 95 = Other,
##47 respondents, dropped by the authors in their analyses but kept here), cov_gender (q2: 2 = female
##per the authors' code, 1 = male inferred), cov_years_in_office (q3; 0 = not elected), cov_entity_rs
##(RSentity = 1: Republika Srpska). Dropped: issue-priority ranks (q4_*), q6a_1 answers, the
##partner-choice experiment (q15_*: a separate respondent-level design without recoverable wording).
##Restrictions: none documented; partner combinations (3 x 2) all occur; ids = deposit `id`.
##One round (round 4 of one respondent) has no partner gender recorded: dropped (5,555 rows).
##N: 1,389 respondents (the paper's analysis sample drops the 47 "Other"-ethnicity respondents = 1,342;
##the paper itself was not compared further).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "EliteCooperation.tab"))
stopifnot(nrow(k) == 1389, uniqueN(k$id) == 1389)
eth <- c("1" = "Serb", "2" = "Croat", "3" = "Bosniak")
rs <- lapply(10:13, function(q) data.table(id = as.integer(k$id), task = q - 9L, profile = 1L, rating = as.integer(k[[paste0("q", q)]]),
  attr_partner_ethnicity = unname(eth[as.character(k[[paste0("whoQ", q, "_ethn")]])]),
  attr_partner_gender = c("male", "female")[k[[paste0("whoq", q, "_gen")]]],
  trial_eu_benefits_asked = as.integer(!is.na(k$q6a_1)),
  cov_ethnicity = ifelse(k$q1 == 95L, "Other", unname(eth[as.character(k$q1)])),
  cov_gender = c("male", "female")[k$q2], cov_years_in_office = as.integer(k$q3), cov_entity_rs = as.integer(k$RSentity)))
d <- rbindlist(rs)
stopifnot(!anyNA(d[, .(rating, attr_partner_ethnicity, cov_ethnicity, cov_gender)]), sum(is.na(d$attr_partner_gender)) == 1)
d <- d[!is.na(attr_partner_gender)]   # one round (id/round 4) has no partner gender: dropped
setorder(d, id, task, profile)
cat("coethnic partner share of rounds:", d[cov_ethnicity != "Other", mean(attr_partner_ethnicity == cov_ethnicity)], "\n")
fwrite(d, file.path(out, "butler_2019_elite_trust_game.csv"))
