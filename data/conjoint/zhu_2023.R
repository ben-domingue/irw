##Corruption-competence vignette experiment across government levels (China) from
##Zhu, L., & Yang, F. (2023). Trading integrity for competence? The public's varying preferences for bureaucratic types across
##government levels in China. Political Science Research and Methods, 11(4), 877-892. https://doi.org/10.1017/psrm.2023.7
##Replication data: Harvard Dataverse doi:10.7910/DVN/GQFQJJ, CC0 1.0. Files read: tradeoff_data.tab, tradeoff_analysis.do (as text; defines the
##eight vignette types QK 1-8), README File.docx, and the Cambridge Online Appendix PDF (Tables A, C, D, E: group sizes and cell proportions).
##Usage: Rscript zhu_2023.R <dir holding tradeoff_data.tab saved as data.tab> <output dir>
##
##Nationwide Chinese survey, 5,527 respondents; each read ONE vignette about a local official (2 x 2 x 2, between subjects, one cell per respondent;
##QK = the randomly assigned cell, n = 699/687/675/707/721/681/677/680 for QK 1..8 as in Appendix Table A):
##  attr_integrity         corrupt / honest   (stored column corrupt = 1 for QK 1-4, 0 for QK 5-8; the do file's comment says 0 = corrupt, but its
##                         QK key, Table 3/C/D and the demotion rates show corrupt = 1 is the corrupt official; the QK key is used)
##  attr_competence        incompetent (bad performance) / competent (good performance)  (Appendix Tables C and D label the columns "Bad performance
##                         (Incompetent)" / "Good performance (Competent)")
##  attr_government_level  township leader / municipal mayor
##QK key from the do file: 1 corrupt+incompetent township, 2 corrupt+competent township, 3 corrupt+incompetent municipal, 4 corrupt+competent
##municipal, 5 honest+incompetent township, 6 honest+competent township, 7 honest+incompetent municipal, 8 honest+competent municipal. Verified
##against the data columns (corrupt, competent, rank are constant within QK and agree) and Appendix Table C (promotion proportions .056 .227 .087 .222
##.178 .736 .248 .750 reproduced).
##LABELS: paraphrased. The vignette wording is not in the deposit or the Online Appendix (the article is not open access); the level text is the
##authors' own descriptive labels from the do file and appendix tables, not the displayed sentences.
##Outcomes (each respondent answered three yes/no questions about the official; wording not in the deposit, paraphrased from the appendix table
##titles): choice_demotion  supports demoting the official (1 yes); choice_promotion  supports promoting him/her (1 yes);
##choice_report  supports reporting his/her corruption (1 yes). Single-profile accept/reject questions: opt_out = yes.
##No respondent id: id = row number of the file (5,527 rows). task = profile = 1.
##Covariates: cov_gender (male 0/1; 68% male as Appendix Table A), cov_age_code (age band 1-6, bands not documented).
##Dropped: income band (1-7, unlabelled), education, Han, party member, urban, hukou, hometown, public employee, government-perception items,
##contact frequency, manipulation checks (check_corrupt, check_competent), derived town_/municipal_ dummies.
##Count check: N = 5,527 as in the paper abstract and Appendix Table A.
##PII FOUND: none.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "data.tab"), showProgress = FALSE)
stopifnot(nrow(x) == 5527, all(x$QK %in% 1:8))
q <- x$QK
integ <- ifelse(q %in% 1:4, "corrupt", "honest")
comp <- ifelse(q %in% c(2, 4, 6, 8), "competent (good performance)", "incompetent (bad performance)")
lev <- ifelse(q %in% c(3, 4, 7, 8), "municipal mayor", "township leader")
stopifnot(all(x$corrupt == (q <= 4)), all(x$competent == (q %in% c(2, 4, 6, 8))), all(x$rank == (q %in% c(3, 4, 7, 8))))
d <- data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L, choice_demotion = as.integer(x$demotion), choice_promotion = as.integer(x$promotion),
  choice_report = as.integer(x$report), attr_integrity = integ, attr_competence = comp, attr_government_level = lev,
  cov_gender = c("female", "male")[x$male + 1L], cov_age_code = as.integer(x$age))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "zhu_2023_corruption_competence.csv"))
cat(nrow(d), "rows\n")
