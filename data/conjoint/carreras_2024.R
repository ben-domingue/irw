##Corrupt-bureaucrat conjoint (Paraguay) from
##Carreras, M., Vera, S., & Visconti, G. (2024). Gender stereotypes and petty corruption among
##street-level bureaucrats: Evidence from a conjoint experiment. Research & Politics, 11(3).
##https://doi.org/10.1177/20531680241277405
##Replication data: Harvard Dataverse doi:10.7910/DVN/MGAQDT, CC0 1.0, no restricted files.
##Files read: replication_data.Rdata (object d: the conjoint, one row per profile; object d_match,
##the authors' matched subsample, not used) and 00_read_me.txt. The authors' 01-05 .R files were
##read as text (not run). The article (CC BY-NC, SAGE) could not be retrieved here, so outcome
##wording, display and randomization facts are not in this header.
##Usage: Rscript carreras_2024.R <dir holding replication_data.Rdata> <output dir>
##
##3,107 respondents, 10 rows each = 5 paired tasks (31,070 rows). The deposit has NO task or
##profile column: task = ceiling(row within respondent / 2), profile = 1/2 by row order within the
##pair (INFERRED from row order; verified: each respondent's rows are contiguous, every respondent
##has exactly 10 rows, and in every inferred pair exactly one profile is chosen on each of the
##three outcomes).
##Outcomes: three forced choices on the same pairs, outcome_q1, outcome_q2, outcome_q3 (0/1). The
##deposit gives no wording. outcome_q3 is the authors' main outcome (01_main_results.R, Figure 1)
##and is stored as `choice`; outcome_q1 and outcome_q2 ("alternative outcomes", 05_alternative_
##outcomes.R, saved as figureA3.pdf and figureA4.pdf; the read_me says Figures A2 and A3) are choice_q1 and choice_q2. No opt-out (exactly one
##chosen per pair on each).
##6 attributes, level text as stored: the deposit's *_eng columns are the authors' English
##translations (the display language is not documented in the deposit): speed (petty bribe-taking: "Has received bribes"/"Has NOT
##received bribes"), theft ("Has diverted public funds"/"Has NOT ..."), gender (Man/Woman),
##partyid (No party affiliation / Liberal Radical Autentico party / Colorado party), age (30/40/50
##years old), education (Primary/Secondary/College education).
##Covariates: cov_gender (female_resp: 1 -> "female", 0 -> "male"; the authors' dummy, used as
##`female_resp` in 02_main_results_by_respondents_gender.R), cov_education_code (education_resp,
##0-18, no labels; possibly years of schooling, not documented, so kept as codes; 03_conjoint_
##diagnostic.R regresses it on the attributes under the title "Balance test: Age").
##No platform IDs; idnum (survey numbers) re-keyed to 1..N in source order.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "replication_data.Rdata"), envir = e)
k <- as.data.table(e$d)
stopifnot(nrow(k) == 31070, all(rle(k$idnum)$lengths == 10), !anyDuplicated(rle(k$idnum)$values))
k[, pos := seq_len(.N), by = idnum]
d <- k[, .(id = match(idnum, unique(idnum)), task = as.integer((pos + 1) %/% 2), profile = as.integer(2 - pos %% 2),
           choice = as.integer(outcome_q3), choice_q1 = as.integer(outcome_q1), choice_q2 = as.integer(outcome_q2))]
for (v in c("speed", "theft", "gender", "partyid", "age", "education"))
  set(d, j = paste0("attr_", v), value = as.character(k[[paste0(v, "_eng")]]))
stopifnot(d[, .(sum(choice), sum(choice_q1), sum(choice_q2), .N), by = .(id, task)][, all(V1 == 1 & V2 == 1 & V3 == 1 & N == 2)])
stopifnot(all(k$female_resp %in% 0:1), d[, !anyNA(.SD)])
d[, `:=`(cov_gender = c("male", "female")[k$female_resp + 1], cov_education_code = as.integer(k$education_resp))]
stopifnot(d[, uniqueN(cov_education_code), by = id][, all(V1 == 1)], uniqueN(d$id) == 3107)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "carreras_2024_corrupt_bureaucrats.csv"))
