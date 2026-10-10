##Crisis news-report conjoint (UK) from
##Berz, J. (2026). Crises and electoral accountability: How do individual characteristics of
##crises affect performance and responsibility evaluations among voters? Government and
##Opposition, 61, e19. https://doi.org/10.1017/gov.2026.10043
##Replication data: Harvard Dataverse doi:10.7910/DVN/IXPGSG, CC0 1.0. File read:
##Crisis_conjoint_final_raw.csv (a tab-separated Qualtrics export: row 1 names, row 2 question
##text, row 3 ImportIds, then 836 respondents). prepare_conjoint_data.R, read_qualtrics.R and
##analyze_conjoint_data.R were read as text (not run).
##Usage: Rscript berz_2026.R <dir holding Crisis_conjoint_final_raw.csv> <output dir>
##
##Adult UK nationals on Prolific (2023, English), 5 tasks, each a pair of short news reports
##about a crisis hitting the UK under two governments ("Crisis 1" / "Crisis 2"), with 9
##attributes (article: levels "fully randomised"): crisis type, damage to the economy, households
##affected, expert prediction, prevention spending, opposition behaviour, prime-minister
##behaviour, speed of government response, amount of disaster relief. Levels are the text
##fragments Qualtrics inserted into the report (F-<task>-<profile>-<k>), as displayed; the
##authors' shortened plot labels are NOT applied. Attribute order is fixed (F-<task>-<k> names
##are identical for every respondent and task). Profile 1 = Crisis 1, 2 = Crisis 2.
##Three forced choices per task (export question text; options "The government in Crisis 1/2"):
##  choice             <t>_Q7 "Which government do you prefer to re-elect?"
##  choice_handled     <t>_Q5 "Which government has handled their crisis better?"
##  choice_responsible <t>_Q6 "Which government is more responsible for the severity of their crisis?"
##No opt-out. Within a task the three answers are all present or all blank; blank tasks
##(break-offs) are omitted. Respondents: 824 with at least one answered task (12 answered none); the article and
##prepare_conjoint_data.R use the 812 who answered task 5 (12 partial respondents kept here,
##with their answered tasks).
##Covariates: cov_duration_sec (whole survey), cov_finished (Qualtrics Finished, 1/0),
##cov_knowledge_1..3 (Q9-Q11, True/False answers to "No-one may stand for parliament unless
##they pay a deposit." / "The UK uses proportional representation for general elections." /
##"The number of members of parliament is about 100."; blank = not answered -> NA),
##cov_party_identifier (Q12 Yes/No), cov_party_id (Q12b "Which political party do you identify
##with?", asked only if Q12 = Yes; else NA), cov_education (Q14 answer text as stored, "Prefer
##not to say" -> NA), cov_flooded (Q15), cov_covid_hospital (Q16), cov_job_loss (Q17).
##Dropped: PROLIFIC_PID (Prolific worker id), ResponseId (re-keyed 1..N in file order), consent.
##No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "Crisis_conjoint_final_raw.csv")
h <- names(fread(f, sep = "\t", nrows = 0))
s <- fread(f, sep = "\t", header = FALSE, skip = 3, colClasses = "character", encoding = "UTF-8")
setnames(s, h)
stopifnot(nrow(s) == 836, uniqueN(s$ResponseId) == 836)
s[, rid := seq_len(.N)]
anames <- c("type" = "crisis_type", "damage economy" = "damage_economy", "damage households" = "damage_households",
            "expert prediction" = "expert_prediction", "prevention spending" = "prevention_spending",
            "opposition behaviour" = "opposition_behaviour", "prime minister behaviour" = "pm_behaviour",
            "Speed gov. response" = "response_speed", "Amount disaster relief" = "relief_amount")
for (t in 1:5) for (k in 1:9) stopifnot(all(s[[sprintf("F-%d-%d", t, k)]] == names(anames)[k]))
pick <- function(x, p) { x <- trimws(x); stopifnot(all(x %in% c("", "The government in Crisis 1", "The government in Crisis 2")))
  fifelse(x == "", NA_integer_, as.integer(x == paste0("The government in Crisis ", p))) }
rows <- list()
for (t in 1:5) for (p in 1:2) {
  x <- data.table(id = s$rid, task = t, profile = p,
                  choice = pick(s[[paste0(t, "_Q7")]], p), choice_handled = pick(s[[paste0(t, "_Q5")]], p),
                  choice_responsible = pick(s[[paste0(t, "_Q6")]], p))
  for (k in 1:9) x[, paste0("attr_", anames[k]) := trimws(s[[sprintf("F-%d-%d-%d", t, p, k)]])]
  rows[[length(rows) + 1]] <- x
}
d <- rbindlist(rows)
stopifnot(d[, uniqueN(is.na(choice) + is.na(choice_handled) + is.na(choice_responsible)), .(id, task)][, all(V1 == 1)])
d <- d[!is.na(choice)]
stopifnot(!anyNA(d), all(as.matrix(d[, .SD, .SDcols = patterns("^attr_")]) != ""))
for (v in c("choice", "choice_handled", "choice_responsible")) stopifnot(d[, sum(get(v)), .(id, task)][, all(V1 == 1)])
bl <- function(x) fifelse(trimws(x) == "", NA_character_, trimws(x))
cv <- s[, .(id = rid, cov_duration_sec = as.integer(`Duration (in seconds)`), cov_finished = as.integer(Finished == "True"),
            cov_knowledge_1 = bl(Q9), cov_knowledge_2 = bl(Q10), cov_knowledge_3 = bl(Q11),
            cov_party_identifier = bl(Q12), cov_party_id = fifelse(Q12 == "Yes", bl(Q12b), NA_character_),
            cov_education = bl(Q14), cov_flooded = bl(Q15), cov_covid_hospital = bl(Q16), cov_job_loss = bl(Q17))]
cv[cov_education == "Prefer not to say", cov_education := NA]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "berz_2026_crisis_accountability.csv"))
