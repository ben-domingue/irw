##2x2 factorial vignette (one per respondent) on investment incentives and the governor's vote from
##Jensen, N. M., Malesky, E., Medina, M., & Ozdemir, U. (2014). Pass the bucks: Credit, blame, and the
##global competition for investment. International Studies Quarterly, 58(3), 433-447.
##https://doi.org/10.1111/isqu.12106
##Replication data: Harvard Dataverse doi:10.7910/DVN/AYRHDO, CC0 1.0 (no restricted files). Files read:
##pass_the_bucks_data_isq_replication.tab; wording and design from the article PDF in the deposit
##(Jensen_et_al-2014-International_Studies_Quarterly.pdf, "Research design" section) and the Stata do file (as text).
##Usage: Rscript jensen_2014.R <dir holding pass_the_bucks_data_isq_replication.tab> <output dir>
##
##Cooperative Congressional Election Survey module (YouGov/Polimetrix internet panel, October 2009), US adults, a nationwide
##subsample of 1,974 respondents. Each respondent had a 25% chance of each of four vignettes:
##"Your state competed with a number of other states over a new manufacturing plant that will create 1,000 jobs. With the
##support of the governor, your state offered a tax incentive (break/reduction) package that was [greater / equal or less]
##than that of the other states. If your state [receives / does not receive] this investment, how would this effect your
##evaluation of your governor's performance in office?"
##Attributes: tax incentive package (incentive_greater: 1 = greater, 0 = equal or less) and the investment outcome
##(FDI_receives: 1 = receives, 0 = does not receive); cells 517, 483, 504, 470 of the 1,974 answered (treatmentIF 1-4).
##Outcome: rating = likelihood_vote, "(1) I would be much more likely to vote for the governor in the next election ... (5) I would be much less likely".
##The authors invert the scale in the deposit: 5 = much more likely to vote for the governor, 1 = much less likely
##(article: "We invert this scale with a score of 5 representing 'much more likely'"); stored as in the file, raw.
##The middle answer "My vote choice would not be altered" is the neutral/opt-out category of the scale (3).
##One vignette per respondent, no respondent id kept (V100 is a panel id, dropped): id = row number of the kept rows.
##1,996 rows in the file; 22 have no answer (omitted, and one of them has no treatment): 1,974 rows kept = the paper's N = 1,974.
##Covariates: cov_state (stateabrev), cov_party_id_code (CC423 as coded; the do file uses 1, 2, 3 for Democrat, Republican, independent,
##codes 4-5 are not documented), cov_registered (registered, 1 = registered to vote). Dropped: derived interactions (i, F, i_f, i_appr ...),
##state-level covariates (unemployment, approval), pre-treatment governor approval, CC424 (undocumented), panel id.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "pass_the_bucks_data_isq_replication.tab"))
stopifnot(nrow(d) == 1996)
d <- d[!is.na(likelihood_vote) & !is.na(incentive_greater) & !is.na(FDI_receives)]
stopifnot(all(d$likelihood_vote %in% 1:5), all(d$incentive_greater %in% 0:1), all(d$FDI_receives %in% 0:1))
r <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L, rating = as.integer(d$likelihood_vote),
  attr_tax_incentive_package = c("equal or less than that of the other states", "greater than that of the other states")[d$incentive_greater + 1L],
  attr_investment = c("does not receive this investment", "receives this investment")[d$FDI_receives + 1L],
  cov_state = d$stateabrev, cov_party_id_code = as.integer(d$CC423), cov_registered = as.integer(d$registered))
print(r[, .N, .(attr_tax_incentive_package, attr_investment)])
print(r[, .(mean_rating = mean(rating)), attr_investment])
fwrite(r, file.path(out, "jensen_2014_incentive_credit.csv"))
cat("rows", nrow(r), "\n")
