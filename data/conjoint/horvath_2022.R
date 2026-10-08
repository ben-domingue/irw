##Contact-tracing app conjoint (UK, Study 1) from
##Horvath, L., Banducci, S., & James, O. (2022). Citizens' attitudes to contact tracing apps.
##Journal of Experimental Political Science, 9(1), 118-130. https://doi.org/10.1017/XPS.2020.30
##Replication data: Harvard Dataverse doi:10.7910/DVN/KVKGUB, CC0 1.0, no restricted files, no
##terms. File read: "May+2020+Public+Affairs+Survey+V2_May+24,+2020_10.36 - Copy.csv" (Qualtrics
##export, TAB-separated despite the name, triple header: names / question text / ImportId).
##Codebook May_2020_Public_Affairs_Survey_V2.docx and the authors' study1.R read as text only.
##Study 2 (Contact+tracing+conjoint_June...csv) is a single 7-point question with a one-factor
##prime, not a conjoint, and is not built.
##Usage: Rscript horvath_2022.R <dir holding the export, saved as study1.csv> <output dir>
##
##Dynata UK online sample, May 2020 omnibus ("Public Affairs Survey"); the conjoint is one block.
##Filters as the authors (study1.R): responses started after 20/05/2020 10:35 (earlier ones are
##previews/tests), screened-out respondents (no gender answer) dropped; tasks with blank attribute
##fields or no answer dropped. 5 respondent-tasks from an earlier attribute set ("Data used",
##"Location data shared", "Contact data shared") fall before the cutoff and are not included.
##Result: 1,504 respondents, matching the article (N = 1,504).
##5 tasks (Q23-Q27), 2 apps each: task and profile RECORDED (Qualtrics F-<task>-<profile>-<row>).
##choice: "Here, we are presenting two hypothetical versions of a contact tracing app. Please
##  choose the app which you would be more likely to install on your phone. ... Which app would
##  you be more likely to install on your phone?" Mobile App 1 / Mobile App 2, forced, no opt-out.
##Six attributes, level text as displayed (F-t-p-k fields): data storage, data stored until,
##contacts uploaded, location uploaded, purpose of app, what constitutes a contact. attrpos_* =
##the row (1-6) where the attribute was shown (F-t-k field); order randomized per respondent.
##RESTRICTIONS (observed; not documented in the deposit): a decentralised ("locally at device")
##app always has "Not stored", "Notify users directly of exposure to virus", and "None" for
##contacts and location uploaded; central-database apps never have those storage/purpose levels.
##So levels are far from uniform (e.g. contacts uploaded None 45%).
##trial_breach_prime: respondent-level arm shown before the conjoint, "control" (Q21, data
##security text) or "breach" (Q22, same text plus a paragraph on data breaches).
##Covariates (codebook codes): cov_gender (1 male, 2 female, 4 transgender, 5 none of these,
##6 rather not say), cov_birth_year, cov_region (1 East of England .. 12 Yorkshire & Humberside),
##cov_trust_nhs (0 = do not trust at all .. 10 = complete trust), cov_gov_handling (1 very badly
##.. 4 very well, 5 don't know), cov_education (1 no formal .. 4 university degree, 5 don't know,
##6 prefer not to say). Dropped: Qualtrics ResponseId (re-keyed), dates, durations, the
##(empty) recipient name/email columns, other survey experiments and items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "study1.csv")
nm <- names(fread(f, sep = "\t", nrows = 0, header = TRUE))
s <- fread(f, sep = "\t", skip = 3, header = FALSE, colClasses = "character", col.names = nm, encoding = "UTF-8")
s[, st := as.POSIXct(StartDate, format = "%d/%m/%Y %H:%M", tz = "Europe/London")]
s <- s[st > as.POSIXct("2020-05-20 10:35", tz = "Europe/London") & Q2 != ""]
s[, rid := .I]
key <- c("Data storage" = "storage", "Data stored until" = "stored_until", "Contacts uploaded" = "contacts_uploaded",
         "Location uploaded" = "location_uploaded", "Purpose of app" = "purpose", "What constitutes a contact" = "contact_definition")
d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(id = s$rid, task = t, profile = p, ans = s[[paste0("Q", 22 + t)]])
  for (k in 1:6) { an <- s[[sprintf("F-%d-%d", t, k)]]; lv <- s[[sprintf("F-%d-%d-%d", t, p, k)]]
    for (n in names(key)) { w <- an == n; x[w, paste0("attr_", key[[n]]) := lv[w]]; x[w, paste0("attrpos_", key[[n]]) := k] } }
  x
}))))
d <- d[ans %in% c("1", "2") & complete.cases(d[, paste0("attr_", key), with = FALSE])]
d <- d[d[, .N, .(id, task)][N == 2], on = .(id, task)][, N := NULL]
d[, choice := as.integer(ans == as.character(profile))][, ans := NULL]
d[, attr_storage := sub("\\.$", "", attr_storage)]
cv <- s[, .(id = rid, trial_breach_prime = fifelse(ctrace_pre_stimulus_DO == "Q22", "breach", "control"),
            cov_gender = as.integer(Q2), cov_birth_year = as.integer(Q3), cov_region = as.integer(Q4),
            cov_trust_nhs = as.integer(Q6_1), cov_gov_handling = as.integer(Q8), cov_education = as.integer(Q96))]
stopifnot(cv[id %in% d$id, all(s$ctrace_pre_stimulus_DO[id] %in% c("Q21", "Q22"))])
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", paste0("attr_", key), paste0("attrpos_", key)))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(d$id) == 1504,
          d[attr_storage %like% "Decentralised", all(attr_stored_until == "Not stored" & attr_contacts_uploaded == "None")])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "horvath_2022_contact_tracing_apps.csv"))
