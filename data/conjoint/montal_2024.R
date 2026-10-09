##Journal-submission conjoint among Latin American IR scholars from
##Montal, F., Yamin, P., & Pauselli, G. (2024). A matter of journal choice: A conjoint experiment
##on submission choices of Latin American IR scholars. International Studies Perspectives, 25(3),
##407-424. https://doi.org/10.1093/isp/ekad025
##Replication data: Harvard Dataverse doi:10.7910/DVN/UJ5S1V, CC0 1.0, no restricted files.
##File read: data_ISP.rds (long, one row per respondent x task x profile). Read as text:
##"1. Functions.R", "2. Figures.R" (cregg analysis: select ~ attributes, id = ResponseId).
##No codebook or questionnaire in the deposit.
##Usage: Rscript montal_2024.R <raw dir> <output dir>
##
##446 IR scholars based in Latin America (paper: 446), 3 tasks of 2 hypothetical journals
##(question = task, choice = profile position 1/2), 8 attributes. Attribute text is the deposit's
##own level labels (English, short: e.g. Editorial Location = Country / Global North / Latin
##America; Language = English / Local language; Acceptance Rate 05% / 40% / 90%). The covariate
##answers are Spanish, so the questionnaire was at least partly in Spanish; the displayed
##attribute wording is not deposited, so these labels may be translations or shorthand.
##Leading spaces in the Scimago levels (" No", " Yes") are trimmed. "Peer Pressure" is the
##attribute the authors' figures call "Colleagues Published"; "Methods" = "Relevance of Methods".
##Outcome: choice = select (the journal the respondent would submit to); forced choice, wording
##not deposited. 4 of 1,338 tasks have neither profile selected (unanswered); they are dropped.
##Randomization restrictions and attribute order not documented.
##Covariates: the survey answers as text, named by question number (cov_q2_1 ...; question
##wording not deposited), except the reserved cov_gender (2.2: Femenino = female, Masculino =
##male, Otro = other), cov_age_group (2.3, band text), cov_education (2.4, answer text).
##2.6 is the country of PhD studies (the authors' Figures.R). The 3.1_k / 3.2_k multiple-choice
##options keep their text (NA = not ticked). The `check` flag (0 for all rows) is dropped.
##DROPPED: Qualtrics ResponseId (re-keyed to integers in file order); 3.2_14_TEXT (free text).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "data_ISP.rds")))
stopifnot(all(x$check == 0), all(x$choice %in% 1:2), all(x$question %in% 1:3))
at <- c(Methods = "methods", Audience = "audience", `Editorial Location` = "editorial_location",
        `Response Time` = "response_time", `Peer Pressure` = "peer_pressure", Scimago = "scimago",
        Language = "language", `Acceptance Rate` = "acceptance_rate")
ids <- unique(x$ResponseId)
d <- data.table(id = match(x$ResponseId, ids), task = x$question, profile = as.integer(x$choice),
                choice = as.integer(x$select))
for (v in names(at)) d[, paste0("attr_", at[[v]]) := trimws(as.character(x[[v]]))]
skip <- c("ResponseId", "choice", "select", "question", "check", "3.2_14_TEXT", names(at))
for (v in setdiff(names(x), skip)) d[, paste0("cov_q", gsub("\\.", "_", v)) := as.character(x[[v]])]
stopifnot(all(d$cov_q2_2 %in% c(NA, "Femenino", "Masculino", "Otro")))
d[, cov_gender := c(Femenino = "female", Masculino = "male", Otro = "other")[cov_q2_2]]
setnames(d, c("cov_q2_3", "cov_q2_4"), c("cov_age_group", "cov_education"))
d[, cov_q2_2 := NULL]
d[, n := sum(choice), .(id, task)]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], all(d$n %in% 0:1), d[n == 0, uniqueN(paste(id, task))] == 4)
d <- d[n == 1][, n := NULL]
setcolorder(d, c("id", "task", "profile", "choice", paste0("attr_", at)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "montal_2024_journal_choice.csv"))
