##Ethiopian decentralisation conjoint from
##Davis, B., Dow, D. A., Springman, J., & Tellez, J. F. (2026). Two dilemmas in the politics of
##ethnic federalism: Experimental evidence from Ethiopia. Journal of Conflict Resolution, 70(9),
##1642-1669. https://doi.org/10.1177/00220027261427753
##Replication data: Harvard Dataverse doi:10.7910/DVN/XBZV21, CC0 1.0, no restricted files.
##Files read: clean-decent-conjoint.rds; level text checked against codebook.tab (deposit's
##codebook.csv) and replication.qmd (read as text; Table 1 and the cregg calls).
##Usage: Rscript davis_2026.R <raw dir> <output dir>
##
##Ethiopian university students (endline survey of the authors' panel; abstract). The baseline
##file clean_baseline.rds (vignette experiment) has no respondent id and cannot be linked; not used.
##Each respondent saw 2 pairs (task 1-2) of hypothetical federal arrangements (profile A = 1,
##B = 2) with 4 two-level attributes, and chose one. The deposit has no task column: the rows of
##each r_id are A,B,A,B and task is INFERRED from row order (rows 1-2 = task 1, rows 3-4 = task 2;
##verified: every complete pair has exactly one chosen profile).
##Outcome: choice = `outcome` ("Whether the conjoint profile was chosen by the respondent",
##codebook); the question wording is not in the deposit (recorded as a paraphrase). Forced
##choice, no opt-out.
##Attributes (level text as in the data = the codebook): hiring ("Who decides public hiring?"),
##police ("One national police or state police forces?"), culture ("Who decides official
##language, teaching of history?"), borders ("How are state borders drawn?"); feature labels
##from replication.qmd. The qmd's Figure A11 checks the levels are uniformly distributed; the
##paper's randomization details (restrictions, attribute order) were not seen.
##Dropped tasks: 70 pairs with no attributes and no outcome, 30 pairs with attributes but no
##outcome, and 2 pairs with an outcome but no attributes (2,108 -> 2,006 tasks).
##Covariates: cov_ethnicity3 (three_ethn: Oromo/Amhara/Other), cov_multiethnic (identifies
##with several ethnic groups, 1/0), cov_career_plans (q26 post-graduation plans, answer text),
##cov_ethnic_violence_any (ev_dichotomous: the authors' binary "any support for ethnic
##violence"; a derived indicator kept because its source items are not deposited). Dropped:
##derived public_plans and multiethnic_bin. r_id is "Endline_<n>" (825 respondents) or
##"Expansion_<n>" (229; a second recruitment wave, pooled by the authors' cregg calls); the prefix is
##kept as cov_sample and ids are re-keyed to integers 1..N in r_id sort order. No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "clean-decent-conjoint.rds")))
x[, r := seq_len(.N), r_id]
stopifnot(x[, .N, r_id][, all(N == 4)], all(x$profile == c("A", "B")[2L - x$r %% 2L]))
x[, task := (r + 1L) %/% 2L]
x[, keep := all(!is.na(outcome)) & all(!is.na(hiring) & !is.na(police) & !is.na(culture) & !is.na(borders)), .(r_id, task)]
x <- x[keep == TRUE]
stopifnot(x[, sum(outcome), .(r_id, task)][, all(V1 == 1)])
stopifnot(all(grepl("^(Endline|Expansion)_[0-9]+$", x$r_id)))
d <- data.table(id = frank(x$r_id, ties.method = "dense"), task = x$task, profile = match(x$profile, c("A", "B")),
                choice = as.integer(x$outcome),
                attr_hiring = as.character(x$hiring), attr_police = as.character(x$police),
                attr_culture = as.character(x$culture), attr_borders = as.character(x$borders),
                cov_sample = sub("_[0-9]+$", "", x$r_id), cov_ethnicity3 = x$three_ethn, cov_multiethnic = as.integer(x$multiethnic),
                cov_career_plans = x$q26, cov_ethnic_violence_any = as.integer(x$ev_dichotomous))
stopifnot(!anyNA(d$id))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "davis_2026_ethnic_federalism.csv"))
