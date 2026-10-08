##Anti-corruption candidate conjoint (Paraguay) from
##Vera, S. (2025). Cleaning up politics: Anti-corruption appeals in electoral campaigns.
##British Journal of Political Science, 55, e108. https://doi.org/10.1017/S0007123425100501
##Replication data: Harvard Dataverse doi:10.7910/DVN/66ANEK, CC0 1.0. File read:
##anticorr_replication_data.RData (one tibble `d`, loaded into its own environment).
##No codebook ships; the attribute table is the article's Supplementary Table A4 (not read).
##Usage: Rscript vera_2025.R <dir holding the .RData> <output dir>
##
##2,060 Paraguayan adults (Offerwise online panel, Aug-Sep 2021, quotas on gender, age,
##education), 5 pairs of hypothetical municipal candidates, 9 attributes. The file has NO
##task or profile column: each respondent has exactly 10 consecutive rows, and consecutive
##row pairs form a task (in every pair exactly one profile is chosen on the effectiveness
##question, and the vote is either one-of-two or none), so task and profile are INFERRED
##from row order. Two respondents (source ids 1540, 9785) have no attribute values (their
##raw attribute columns hold numbers and first names) and are dropped: 2,058 respondents.
##The article reports 2,060; the authors' cregg models also drop those 20 rows.
##The same tasks carried two choice questions; both are in one table (one experiment):
##  choice: "If the general municipal elections were held tomorrow, which of these
##    candidates would you vote for?" Candidate 1 / Candidate 2 / would not vote. OPT-OUT:
##    3,424 of 10,290 tasks are "would not vote" (choice = 0 on both profiles; the source
##    codes them NA).
##  choice_effective: "Which of these candidates do you believe will help reducing
##    corruption the most?" Forced choice, no opt-out.
##Attribute text. Only three attributes ship with the Spanish text shown to respondents
##(bullet and tab stripped): anti-corruption platform (atributo4), bribery record
##(atributo1) and candidate gender (atributo7). The other six ship only as the author's
##short English labels, which are used as is: ideology ("No Ideo.", "Close Ideo.",
##"Distant Ideo."; the article speaks of ideological closeness, so the displayed text was
##probably relative to the respondent's own position; not verifiable from the deposit),
##party (Established/New), embezzlement, competence (job-creation record), age (30/40/50
##years old), education (Primary/Secondary/College Ed.). Attribute order and any
##randomization restrictions are not documented in the deposit (no attribute combination is
##missing). Level weights OBSERVED: platform is unbalanced (no 7,600 rows, vague 4,746,
##concrete 8,234), and ideology, age and education each have one level at ~23% against
##~37-40% for the other two; bribery, gender, party, embezzlement, competence are 50/50.
##Covariates: cov_age (Q1, years), cov_gender (Q2 answer text: "Mujer" -> "female", "Hombre"
##-> "male"; the author's anticorr_representative_matching.R L27 codes Mujer as female),
##cov_education (a1, the answer text as stored, e.g. "12 años: 3er curso de la E. Media o 6to
##curso", "No sé/ No estoy seguro"; trailing no-break spaces trimmed; "Prefiero no decir" -> NA),
##cov_education_years (years of schooling taken from that answer text, 0-18, 18 = "18 or
##more"; "No sé" and "Prefiero no decir" set missing).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "anticorr_replication_data.RData"), envir = e)
s <- as.data.table(e$d)
stopifnot(s[, .N, id][, all(N == 10)])
s[, r := seq_len(.N), id][, task := (r + 1L) %/% 2L][, profile := 2L - r %% 2L]
s <- s[!is.na(anticorruption)]
stopifnot(s[, .N, id][, all(N == 10)], uniqueN(s$id) == 2058)
stopifnot(all(s$Q2 %in% c("Mujer", "Hombre")))
clean <- function(x) trimws(gsub("^•\\s*", "", x))
d <- s[, .(id = as.integer(id), task = as.integer(task), profile = as.integer(profile),
           attr_anticorruption = clean(atributo4), attr_bribery = clean(atributo1), attr_gender = clean(atributo7),
           attr_ideology = as.character(ideology), attr_party = as.character(party), attr_embezzlement = as.character(embezzlement),
           attr_competence = as.character(competence), attr_age = as.character(age), attr_education = as.character(education),
           cov_age = as.integer(Q1), cov_gender = c(Mujer = "female", Hombre = "male")[as.character(Q2)],
           cov_education = fifelse(a1 == "Prefiero no decir", NA_character_, trimws(as.character(a1), whitespace = "[\\h\\v]")),
           cov_education_years = suppressWarnings(as.integer(sub("^([0-9]+) a.*", "\\1", a1))))]
stopifnot(d[, uniqueN(attr_anticorruption)] == 3, d[, uniqueN(attr_bribery)] == 2, d[, uniqueN(attr_gender)] == 2)
vote <- as.integer(s$outcome_q1); vote[is.na(vote)] <- 0L
d[, choice := vote][, choice_effective := as.integer(s$outcome_q4)]
setcolorder(d, c("id", "task", "profile", "choice", "choice_effective"))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)], s[, uniqueN(is.na(outcome_q1)), .(id, task)][, all(V1 == 1)])
stopifnot(d[, sum(choice_effective), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "vera_2025_anticorruption.csv"))
