##Research-ethics conjoint among political scientists (APSA members) from
##Costa, M., Crabtree, C., Holbein, J. B., & Landgrave, M. (2023). Is that ethical? An exploration
##of political scientists' views on research ethics. Research & Politics, 10(4).
##https://doi.org/10.1177/20531680231209553 (article found via Crossref by title; not read).
##Replication files: OSF https://doi.org/10.17605/OSF.IO/KYPWD, licence CC BY 4.0 (OSF node
##licence). The readme titles the paper "What do political scientists believe about research ethics?".
##Files read: ethics_apsa_survey.csv (Qualtrics export with a question-text second header row),
##ethics_apsa_codebook.pdf, analysis_conjoint.R (read as text, not run).
##Usage: Rscript costa_2023.R <dir holding ethics_apsa_survey.csv> <output dir>
##
##362 consenting APSA members (node description: "a survey conducted with the American Political
##Science Association ... 362 political scientists"); Conjoint Survey Design Tool layout (codebook):
##F-t-k = name of the attribute in row k of task t, F-t-p-k = level of profile p in that row.
##5 tasks x 2 hypothetical published studies, 7 attributes: author affiliation, author rank,
##publication outlet, conclusions, study type (methodology), location of study, sample size.
##Attribute order is randomized per respondent: the row order differs between respondents and is
##identical across that respondent's 5 tasks (checked below); attrpos_<attr> = row (1-7). The rows
##move in blocks (author rank always directly follows author affiliation; study type, location and
##sample size always appear as one consecutive block), so not every order occurs.
##Outcome (question-text row of the export): choice = taskXchoice, "If you had to choose, which of
##the two studies would you say is more ethical?" 1 / 2; forced (no neither option). Tasks with no
##answer are dropped (respondents who skipped all 5 tasks drop out entirely): 247 respondents and
##1,165 tasks remain of 353 respondents shown the conjoint. The node description's 362 is all
##consenting respondents.
##353 of the 362 have conjoint data (9 have no attribute rows at all); every profile shows all 7
##attributes. Levels are stored as displayed (e.g. "Amherst College", "Political Science Review");
##the authors' groupings in analysis_conjoint.R (Top 20 Research Univ., SLAC, "Political Science
##Review (fake)", ...) are not applied.
##Restrictions, level probabilities: not documented (unknown).
##Covariates (export answer text): cov_position (position1), cov_rank (position2), cov_gender
##(Man = male, Woman = female, Transgender / Genderqueer / Other = other; blank = NA), cov_subfield.
##The ranking and harm batteries are not kept. No platform IDs; respondent is a 1..n serial.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "ethics_apsa_survey.csv"), header = TRUE, encoding = "UTF-8", colClasses = "character")
setnames(x, gsub("\\.", "-", names(x)))
stopifnot(x$`F-1-1`[1] == "F-1-1", grepl("more ethical", x$task1choice[1]))
x <- x[-1][ethics_consent == "Yes"]
stopifnot(nrow(x) == 362)
L <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) rbindlist(lapply(1:7, function(k)
  x[, .(id = as.integer(respondent), task = t, profile = p, pos = k, attr = get(sprintf("F-%d-%d", t, k)),
        level = get(sprintf("F-%d-%d-%d", t, p, k)), ch = get(sprintf("task%dchoice", t)))]))))))
L <- L[attr != ""]
# order is per respondent: same attribute in the same row in every task
stopifnot(L[, uniqueN(pos), .(id, attr)][, all(V1 == 1)])
print(L[, .(n_attr = uniqueN(attr)), id][, table(n_attr)])
L <- L[ch %in% c("1", "2")]
L[, attr := paste0("attr_", gsub(" ", "_", tolower(attr)))]
L[, attrpos := sub("^attr_", "attrpos_", attr)]
w <- dcast(L, id + task + profile + ch ~ attr, value.var = "level")
wp <- dcast(unique(L[, .(id, attrpos, pos)]), id ~ attrpos, value.var = "pos")
d <- merge(w, wp, by = "id")
d[, choice := as.integer(as.integer(ch) == profile)][, ch := NULL]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
ac <- grep("^attr_", names(d), value = TRUE)
stopifnot(length(ac) == 7, !anyNA(d[, ..ac]), all(unlist(d[, ..ac]) != ""))
cv <- x[, .(id = as.integer(respondent), cov_position = fifelse(position1 == "", NA_character_, position1),
            cov_rank = fifelse(position2 == "", NA_character_, position2),
            cov_gender = c(Man = "male", Woman = "female", Transgender = "other", Genderqueer = "other")[gender],
            cov_subfield = fifelse(subfield == "", NA_character_, subfield))]
cv[x$gender %like% "^Other", cov_gender := "other"]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", sort(ac)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "costa_2023_research_ethics.csv"))
