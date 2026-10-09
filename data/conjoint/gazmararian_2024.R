##Just-transition assistance conjoint (US): county-fair and national samples, from
##Gazmararian, A. F. (2024). Fossil fuel communities support climate policy coupled with just
##transition assistance. Energy Policy, 184, 113880. https://doi.org/10.1016/j.enpol.2023.113880
##Replication data: Harvard Dataverse doi:10.7910/DVN/FC9X6H, CC0 1.0. Files read:
##national_conjoint.rds, fair_conjoint.rds (data.frames, one row per respondent x task x profile),
##si_gazmararian_jepo.pdf (SI: samples, weights, survey instrument sec. 7), and as text the
##authors' conjoint_analysis.R and sample_comparison.R (fair `sex` coding, L133).
##Usage: Rscript gazmararian_2024.R <dir holding the two .rds files> <output dir>
##
##Two tables, one per sample: the same 7-attribute design was fielded on two different populations
##in different years and modes, and the article estimates them separately (conjoint_analysis.R fits
##m.nat and m.fair, then a sample interaction).
##  gazmararian_2024_transition_fair: 248 adults recruited at two county fairs in Southwest
##    Pennsylvania (July and August 2021; tablet, a few paper surveys), 6 tasks of 2 proposals.
##    One task of one respondent has no answer and is dropped (2 rows; the authors drop it too).
##  gazmararian_2024_transition_national: 1,001 US adults (Lucid, Feb-Mar 2023, census quotas;
##    the attention check was a screener), 5 tasks of 2 proposals.
##Outcome (SI sec. 7, Q7-13): choice, "If you had to choose, which proposal would you prefer the
##government to pursue?" Proposal A / Proposal B; forced, no opt-out. choice = the authors'
##`selected`; profile 1 = A, 2 = B.
##Attributes (level text as stored, which is the text of the conjoint table): Free Retraining
##Program, Retrained Worker Salary, Worker Retraining Time, Income Support During Retraining,
##Benefit Support, Relocation Support, Community Investment. Randomization restrictions, level
##probabilities and attribute order are not documented (SI shows a screenshot only).
##trial_intro: the introduction randomized per respondent (SI Q6, footnote 12): "control" = "We are
##interested in your views on how the government should help fossil fuel workers and communities.";
##"diversify" = the same preceded by "Because of cheap natural gas and renewables, a move away from
##coal may be inevitable." (column `group`).
##Weights (SI sec. 3): raking calibration weights trimmed to 0.3-3. Fair: cov_survey_weight =
##weights (range 0.3-3; with it the AMCEs of SI Table 8.1 column (1) reproduce exactly, e.g. relocation
##voucher 0.043, health-care benefit 0.127 vs none), cov_weight_untrimmed = weights2 (0.03-6.4; the
##deposited conjoint_analysis.R sets fair$weights <- fair$weights2, which does NOT reproduce the SI
##table). Note SI Table 8.1 column (2), labelled "Sample Weights: Yes", equals the UNWEIGHTED fit
##exactly (the column labels look swapped). National: cov_survey_weight = weights,
##cov_weight_trimmed = weights_trim (authors' columns; not checked against a table).
##Covariates. Fair: cov_age_group (age band text), cov_gender (sex 1 = female, 0 = male;
##sample_comparison.R L133), cov_education (edu text; two spellings of the bachelor's option kept as
##stored), cov_party_id (pid text), cov_attention_pass (pass_attn, Q10 "Which category was NOT
##included...?"), cov_fair (fair1 July / fair2 August). National: cov_gender (sex text), cov_age
##(years, authors' age), cov_education (HighestEd text), cov_party_id (PolParty, trailing tab
##removed), cov_state.
##PII in the deposit: national_conjoint.rds holds respondent ZIP codes (Zipcode), Lucid respondent
##ids (rid) and Qualtrics ResponseIds; fair_conjoint.rds holds Qualtrics ResponseIds, paper-survey
##ids, interview dates and free text. All dropped; ids re-keyed to integers (order of ResponseId).
##Other derived variables (dummies, binaries) are dropped.
##Counts: fair 248 respondents (SI "248 took the survey"); national 1,001 (SI Table 4.1). Match.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
an <- c("Free Retraining Program", "Retrained Worker Salary", "Worker Retraining Time", "Income Support During Retraining",
        "Benefit Support", "Relocation Support", "Community Investment")
cn <- paste0("attr_", tolower(gsub(" ", "_", an)))
## fair
f <- as.data.table(readRDS(file.path(raw, "fair_conjoint.rds")))
stopifnot(uniqueN(f$ResponseId) == 248, nrow(f) == 2976)
f <- f[!is.na(selected)]
f[, id := as.integer(factor(ResponseId))]
fd <- f[, c(list(id = id, task = as.integer(task), profile = match(profile, c("A", "B")), choice = as.integer(selected)),
            lapply(.SD, as.character)), .SDcols = an]
setnames(fd, an, cn)
fd[, `:=`(trial_intro = as.character(f$group), cov_age_group = as.character(f$age),
          cov_gender = c("male", "female")[as.integer(f$sex) + 1L], cov_education = as.character(f$edu),
          cov_party_id = as.character(f$pid), cov_attention_pass = as.integer(f$pass_attn), cov_fair = as.character(f$fair),
          cov_survey_weight = f$weights, cov_weight_untrimmed = f$weights2)]
stopifnot(fd[, .N, .(id, task)][, all(N == 2)], fd[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(fd$id) == 248,
          !anyNA(fd[, ..cn]), all(f$sex %in% 0:1))
setorder(fd, id, task, profile)
fwrite(fd, file.path(out, "gazmararian_2024_transition_fair.csv"))
## national
n <- as.data.table(readRDS(file.path(raw, "national_conjoint.rds")))
stopifnot(uniqueN(n$ResponseId) == 1001, nrow(n) == 10010)
n[, id := as.integer(factor(ResponseId))]
nan <- gsub(" ", ".", an)
nd <- n[, c(list(id = id, task = as.integer(task), profile = match(profile, c("A", "B")), choice = as.integer(selected)),
            lapply(.SD, as.character)), .SDcols = nan]
setnames(nd, nan, cn)
nd[, `:=`(trial_intro = as.character(n$group), cov_gender = c(Female = "female", Male = "male")[n$sex], cov_age = as.integer(n$age),
          cov_education = n$HighestEd, cov_party_id = trimws(n$PolParty), cov_state = n$State,
          cov_survey_weight = n$weights, cov_weight_trimmed = n$weights_trim)]
stopifnot(nd[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(nd[, ..cn]), !anyNA(nd$cov_gender))
setorder(nd, id, task, profile)
fwrite(nd, file.path(out, "gazmararian_2024_transition_national.csv"))
