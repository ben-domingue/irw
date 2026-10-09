##Ward-leader candidate conjoint (slums in Bangalore, Jaipur and Patna, India) from
##Rains, E., & Wibbels, E. (2023). Informal work, risk, and clientelism: Evidence from 223 slums
##across India. British Journal of Political Science, 53(1), 1-24. https://doi.org/10.1017/S0007123422000011
##Replication data: Harvard Dataverse doi:10.7910/DVN/ADZECE, CC0 1.0. Files read: r_conjoint.dta
##(Dataverse "original format" download of r_conjoint.tab); level text from Codebook.xlsx (rows for
##r_conjoint.dta) and conjoint_figures.R (the authors' factor labels, same mapping).
##Usage: Rscript rains_2023.R <dir holding r_conjoint.dta> <output dir>
##
##Household survey in slums of three Indian cities. r_conjoint.dta has one row per respondent x
##candidate, 6 rows per respondent, no task or profile column. Codebook: lcandidate_random_a =
##"Randomly selected trait for ward leader candidate (0=Congress party, 1=BJP party, 2=Co-ethnic,
##3=Educated)", lcandidate_random_b = "(0=Provides private benefits, 1=Provides better services,
##2=Provides co-ethnic benefits, 3=Provides pro-poor schemes, 4=Has the support of the neighborhood
##leader)", choice2 = "Indicator for whether respondent prefers this hypothetical candidate (1) over
##another candidate (0)". So each candidate shows one trait from each list (2 attributes), and the
##respondent picked one of two candidates.
##INFERRED: task = consecutive row pairs within respondent (rows 1-2, 3-4, 5-6; rows are contiguous
##per respondent in file order). Verified: every pair with both candidates' traits recorded has
##exactly one chosen (stopifnot); the odd/even row position is unrelated to choice (50.5% vs 49.4%
##chosen). Screen position (left/right, first/second read out) is not recorded: profile = row
##order within the pair, which does not depend on the outcome (profile_source unknown).
##Level text is the codebook's English description; the survey language, mode and the wording read
##to respondents are not in the deposit (the article full text was not available here), so the
##question in the design record is the codebook's paraphrase.
##Dropped: 1,704 of 7,878 respondents whose 6 rows have no traits recorded (choice2 is 0/1 on most
##of them, so the traits were not saved): their tasks cannot be described. No task with recorded
##traits lacks a choice. Kept: cov_occlow (codebook: 1 = less formal occupation, types 1-2; 0 = more
##formal, types 3-5; NA as in source). r_id re-keyed to integers. No weight, no other covariates in
##this file (per the codebook, the household files carry no r_id to link on).
##Restrictions/level weights: not documented. Count vs paper: not checked against the article text
##(not accessible); 6,174 respondents, 37,044 rows kept. Spot check (cregg-style AMCE, lm clustered
##by id, baselines as in conjoint_figures.R): better services +0.210 (SE 0.008), pro-poor schemes
##+0.176 vs support of neighborhood leader; trait A effects within +-0.03. Not compared with the paper.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(zap_labels(read_dta(file.path(raw, "r_conjoint.dta"))))
x[, row := .I]
stopifnot(x[, .N, r_id][, all(N == 6)], x[, all(diff(row) == 1), r_id][, all(V1)])
x[, k := seq_len(.N), r_id][, task := (k + 1L) %/% 2L][, profile := 2L - (k %% 2L)]
x[, miss := any(is.na(lcandidate_random_a) | is.na(lcandidate_random_b)), .(r_id, task)]
cat("respondents with any untraited task:", uniqueN(x[miss == TRUE]$r_id), "\n")
x <- x[miss == FALSE]
stopifnot(x[, sum(choice2), .(r_id, task)][, all(V1 == 1)])
la <- c("Congress party", "BJP party", "Co-ethnic", "Educated")
lb <- c("Provides private benefits", "Provides better services", "Provides co-ethnic benefits",
        "Provides pro-poor schemes", "Has the support of the neighborhood leader")
stopifnot(all(x$lcandidate_random_a %in% 0:3), all(x$lcandidate_random_b %in% 0:4))
ids <- unique(x$r_id)
d <- x[, .(id = match(r_id, ids), task = as.integer(task), profile = as.integer(profile),
           choice = as.integer(choice2), attr_trait_a = la[lcandidate_random_a + 1],
           attr_trait_b = lb[lcandidate_random_b + 1], cov_occlow = as.integer(occlow))]
setorder(d, id, task, profile)
cat("respondents:", uniqueN(d$id), " rows:", nrow(d), "\n")
fwrite(d, file.path(out, "rains_2023_ward_candidate.csv"))
