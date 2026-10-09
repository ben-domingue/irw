##Coyote (migrant smuggler) choice conjoint (Guatemala) from
##Romero, D., Villamizar-Chaparro, M., & Wibbels, E. (2026). The market in smugglers: Survey
##experimental evidence on the choice of coyotes in Guatemala. Comparative Political Studies.
##https://doi.org/10.1177/00104140261466974
##Replication data: Harvard Dataverse doi:10.7910/DVN/H38CWS, CC0 1.0. File read: CoyoteConjoint.csv
##(Dataverse "original format" download of CoyoteConjoint.tab, datafile 14008468). Read as text only:
##Codebook.md (section 5), README.txt, "Reproduction Files for the Market in Smugglers.Rmd".
##The household, deportee and coyote-use survey files are not conjoint data and are not read.
##Usage: Rscript romero_2026.R <dir holding CoyoteConjoint.csv> <output dir>
##
##Conjoint embedded in a Guatemalan household survey (Codebook.md: "Conjoint experiment embedded in the
##household survey"; fielding dates and mode not in the deposit). 1,534 respondent ids x 3 tasks x 2
##hypothetical coyotes, 6 attributes: price ($3,000 / $7,000 / $10,000), how the coyote was found
##(method), extra charges, safety reputation, record of success, accompaniment (company).
##Attribute text = the authors' English short labels as stored (Codebook.md lists them; the
##"recommeded" misspelling is kept). The text respondents saw (presumably Spanish) is not deposited.
##Outcome: choice = "1 = this profile was chosen" (codebook); the question wording is not deposited.
##Forced choice as stored: every answered task has exactly one chosen profile.
##Task and profile: the file is the authors' reshape in 6 blocks of 1,534 rows (block = task x profile).
##Task is RECORDED (which of coyote_conj1-3 is non-missing on the row; that column holds the answer,
##profile 1 or 2, on both rows of the task). Profile is INFERRED from row order within the task
##(first row = 1) and verified: in all 4,053 answered tasks the row with choice = 1 is the profile number
##stored in coyote_conj<k>. 1,098 rows (549 tasks) have no answer (all coyote_conj NA, choice NA) and are
##dropped; their task number is not recoverable. 119 ids answered no task, so the table holds 1,415
##respondents (the authors' figures print N = 1,534 unique ids, cregg dropping the NA rows).
##The authors analyse with cjoint design = "uniform"; no restriction is documented.
##Covariates (codebook section 5 and section 1 meanings): cov_gender (female: 1 -> female, 0 -> male),
##cov_employed, cov_bad_econ_sit, cov_worsethan_past12, cov_worse_fut12, cov_expense_trouble (1-5,
##difficulty covering expenses), cov_gang, cov_shootings, cov_extorsion, cov_plan2mig, cov_migrated_inal,
##cov_used_coyote, cov_num_coyote, cov_mig_inal_alone / _family / _group, all as stored (0/1 unless noted).
##Dropped: expense_trouble_bin (derived), is_lead and ag_job (undocumented).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "CoyoteConjoint.csv"))
stopifnot(nrow(s) == 9204, uniqueN(s$id) == 1534)
s[, row := .I]
s[, task := fifelse(!is.na(coyote_conj1), 1L, fifelse(!is.na(coyote_conj2), 2L, fifelse(!is.na(coyote_conj3), 3L, NA_integer_)))]
s[, ans := fcoalesce(coyote_conj1, coyote_conj2, coyote_conj3)]
stopifnot(s[is.na(task), all(is.na(choice))], s[!is.na(task), !anyNA(choice)])
s <- s[!is.na(task)]
stopifnot(s[, .N, .(id, task)][, all(N == 2)])
s[, profile := as.integer(rank(row)), .(id, task)]
stopifnot(s[, all(choice == as.integer(profile == ans))])
stopifnot(all(s$female %in% 0:1))
d <- s[, .(id = as.integer(id), task, profile, choice = as.integer(choice),
           attr_price = price, attr_method = method, attr_extra_charges = extra_charges, attr_safety = safety,
           attr_success = success, attr_company = company,
           cov_gender = c("male", "female")[female + 1L], cov_employed = employed, cov_bad_econ_sit = bad_econ_sit,
           cov_worsethan_past12 = worsethan_past12, cov_worse_fut12 = worse_fut12, cov_expense_trouble = expense_trouble,
           cov_gang = gang, cov_shootings = shootings, cov_extorsion = extorsion, cov_plan2mig = plan2mig,
           cov_migrated_inal = migrated_inal, cov_used_coyote = used_coyote, cov_num_coyote = num_coyote,
           cov_mig_inal_alone = mig_inal_alone, cov_mig_inal_family = mig_inal_family, cov_mig_inal_group = mig_inal_group)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
stopifnot(uniqueN(d$id) == 1415)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "romero_2026_coyote_choice.csv"))
