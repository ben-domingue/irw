##Campaign-message candidate conjoint from
##Dai, Y., & Kustov, A. (2024). The (in)effectiveness of populist rhetoric: A conjoint experiment
##of campaign messaging. Political Science Research and Methods, 12(4), 849-856.
##https://doi.org/10.1017/psrm.2023.55
##Replication data: Harvard Dataverse doi:10.7910/DVN/QFYZSR, CC0 1.0. Files read:
##Conjoint_clean.RData (object d_stack: one row per respondent x pair x candidate, with the
##displayed level text) and Survey_clean.tab (original format .csv; respondent covariates).
##Replication codes.Rmd read as text. Design facts from the online appendix (Table B1, Table A3,
##Appendix D-E; static.cambridge.org S2049847023000559sup001.pdf).
##Usage: Rscript dai_2024.R <raw dir> <output dir>
##
##1,004 US MTurk respondents (appendix Table A3: n = 1004/8032), 4 pairs of hypothetical House
##primary candidates in "your party's primary". Each candidate was shown as prose (Table B1):
##"Candidate [A/B] worked as a [job] before running for office. Candidate [A/B] has [office] and
##is likely [polls] in the polls now. Here are Candidate [A/B]'s campaign message highlights:"
##followed by four statements: pluralism/people-centrism (12 statements), moralism/anti-
##establishment (12), immigration (8), economy (8). Level text = the deposit's text columns,
##which match Table B1 up to contractions (e.g. "I'll" vs "I will"); the deposit's text is kept.
##The authors' derived codings (job2/job4, office2, ..., populist2, *congruent) are dropped.
##choice = Y: "If you had to choose between these two candidates in the upcoming primary, who
##would you vote for? If neither of the two candidates appeals to you, please still indicate who
##you would rather vote for." [Candidate A / Candidate B]; forced choice, no opt-out.
##task = choiceNum, profile = candNum (recorded). Randomization restrictions are not documented;
##level shares look uniform (each job ~10%, each statement 7-9% or 11-14%). Whether the same
##statement could appear for both candidates: yes, 8-13% of pairs share a statement.
##Covariates (Survey_clean): cov_age, cov_female, cov_white, cov_college (the authors' 0/1
##codings), cov_ideology3, cov_partyid3, cov_attention_pass (appendix fn 1: passed the end-of-
##survey attention check; ~70%). Dropped as derived: Republican2/Democrat2/partyid2,
##Populist2/populismatt/populismattstr (built from the six populism items, not deposited).
##No MTurk IDs are in the deposit (id is already 1..1004).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "Conjoint_clean.RData"), envir = e)
x <- as.data.table(e$d_stack)
s <- fread(file.path(raw, "Survey_clean.csv"))
d <- data.table(id = as.integer(as.character(x$id)), task = as.integer(x$choiceNum), profile = as.integer(x$candNum),
                choice = as.integer(x$Y), attr_job = x$job, attr_office = x$office, attr_polls = x$polls,
                attr_pluralism = x$pluralism, attr_moralism = x$moralism, attr_immigration = x$immigration,
                attr_economy = x$economy)
cv <- s[, .(id = as.integer(id), cov_age = age, cov_female = Female2, cov_white = White2, cov_college = College2,
            cov_ideology3 = ideology3, cov_partyid3 = partyid3, cov_attention_pass = attention.pass)]
d <- merge(d, cv, by = "id", all.x = TRUE)
stopifnot(d[, .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)], uniqueN(d$id) == 1004L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dai_2024_populist_rhetoric.csv"))
