##Factorial vignette: a Chinese immigrant's skill level x extra information (Japan), from
##Igarashi, A., Miwa, H., & Ono, Y. (2022). Why do citizens prefer high-skilled immigrants to low-skilled
##immigrants? Identifying causal mechanisms of immigration preferences with a survey experiment.
##Research & Politics, 9(2). https://doi.org/10.1177/20531680221091439
##Replication data: Harvard Dataverse doi:10.7910/DVN/LG1LY9, CC0 1.0. Files read: replication_data.tab (read as
##CSV original, replication_data.csv), explanatory_memo.pdf (codebook), replication_code.R (text).
##Not built: additional_data.csv (Online Appendix experiment: one factor, skill, with six outcomes: single-factor).
##Usage: Rscript igarashi_2022.R <dir holding data.csv> <output dir>   (raw file saved as data.csv)
##
##3,000 Japanese adults (opt-in panel, March 2020, quotas on gender, age, prefecture), ONE vignette each, 8 cells =
##skill (2) x added information (4: none, convenience-store job wish, asthma + health insurance, teen shoplifting).
##No respondent id: id = row number; task = profile = 1. Cell sizes match the paper's Table A1 (3,000).
##Outcome: choice = Y (1 approve, 0 do not approve) "If you were an immigration officer, would you grant this man
##a 3-5 year visa? 1 Approve his visa / 2 Do not approve his visa" (English translation in the online appendix B.2 of
##the RIETI discussion paper 21048, same authors). Single-profile accept/reject: opt_out = yes.
##Attribute level text taken from the English translation of the vignettes in Online Appendix B.2 (RIETI DP 21048);
##the deposit stores only group codes 1-8 (memo: skill x arm). Wording is the authors' English rendering of the
##Japanese text, so levels are paraphrased from it (the vignette also names Chen Long, 32, Shanghai: constant).
##Skill is manipulated jointly by education and former job; levels combine both. Level shares are the cell sizes
##(not equal: 784/755/714/747 per arm), assignment probabilities not stated.
##Covariates: cov_gender (memo: 0 male, 1 female), cov_age (years), cov_education (3-level text from the memo's
##dummies: high school or lower / college of technology, junior college or vocational school / college or higher),
##cov_income (memo's 17 before-tax family income bands, text; 487 NA kept NA), cov_ideology (memo 1-5 text).
##Dropped: dummies for arm/skill, manipulation check (MC), political knowledge, partisanship dummies.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "data.csv"))
stopifnot(nrow(x) == 3000)
skill <- c(`1` = "Master's degree in computer science; has worked as a systems engineer", `0` = "Completed technical high school; has worked as a plumber")
info <- c(`1` = "(not shown)", `2` = "Wants to work as a convenience store clerk after coming to Japan",
          `3` = "Has chronic asthma and plans to receive treatment using the Japanese health insurance system",
          `4` = "Was arrested for shoplifting comic books in a bookstore at age 16")
inc <- c("Less than 1M yen", "1-2M yen", "2-3M yen", "3-4M yen", "4-5M yen", "5-6M yen", "6-7M yen", "7-8M yen",
         "8-9M yen", "9-10M yen", "10-12M yen", "12-15M yen", "15-20M yen", "20-25M yen", "25-35M yen", "35-50M yen", "50M yen or more")
ide <- c("Very progressive/left", "Somewhat progressive/left", "Middle of the road", "Somewhat conservative/right", "Very conservative/right")
edu <- fifelse(x$high.edu == 1, "College or higher", fifelse(x$middle.edu == 1, "College of technology, junior college, or vocational school", "High school or lower"))
stopifnot(x[, all(low.edu + middle.edu + high.edu == 1)])
d <- x[, .(id = .I, task = 1L, profile = 1L, choice = as.integer(Y),
           attr_skill = skill[as.character(W)], attr_added_info = info[as.character(Z)],
           cov_gender = c("male", "female")[gender + 1L], cov_age = as.integer(age), cov_education = edu,
           cov_income = inc[income], cov_ideology = ide[ideology])]
stopifnot(!anyNA(d$attr_skill), !anyNA(d$attr_added_info), d[, .N, .(attr_skill, attr_added_info)][, .N] == 8)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "igarashi_2022_skilled_immigrant.csv"))
