##Election-outcome conjoint (Canada, 2025) from
##Sevi, S., Blais, A., & Mekik, C. (2026). What do voters want out of elections? Electoral
##Studies, 102, 103091. https://doi.org/10.1016/j.electstud.2026.103091
##Replication data: Harvard Dataverse doi:10.7910/DVN/DBNDNP, CC0 1.0. File read:
##"Cdn Elxn-Outcomes_June 22, 2025_08.06.csv" (Dataverse original of the .tab: a raw Qualtrics
##export, row 1 names, row 2 question text, row 3 import ids). analysis.R read as text only.
##Usage: Rscript sevi_2026.R <dir holding the .csv> <output dir>
##
##Canadian online-panel respondents, April 2025 (during the federal campaign), English or
##French (Qualtrics UserLanguage EN / FR-CA -> cov_language). 6 paired tasks: two hypothetical
##election outcomes ("Outcome 1"/"Outcome 2") with 6 attributes: number of parties in the House
##of Commons, performance of the winning party (votes/seats), turnout, representation of women,
##ballot type, representation of visible minorities. Task and profile are recorded in the
##Qualtrics F-<task>-<profile>-<k> columns; F-<task>-<k> names the attribute in row k, so
##attribute order is recorded (attrpos_*, 1-6). The order differs between respondents and is
##the same in all 6 tasks of a respondent (checked in the script).
##Attribute text is as displayed: English for EN respondents, French for FR-CA respondents
##(e.g. "Le taux de participation à l’élection est de 70", missing % sign as displayed); trailing
##spaces trimmed. The authors' analysis.R translates French to English (fr2en) and recodes to
##short labels; neither is applied here.
##Outcomes:
##  choice: "If you had to choose one of these two scenarios, which would you pick as better for
##    Canada?" Outcome 1 / Outcome 2; forced (no opt-out).
##  rating: "How would you rate each on a scale from 0, which means very bad, and 10, which means
##    very good." 0-10, higher = better.
##Kept: every respondent who answered the conjoint (Finished = True with all 6 choices; 2,487).
##Respondents with Finished = True but no conjoint answers (screened out: non-citizens, minors,
##no consent) have no outcome and are omitted. The authors analyse "good cases" only: they drop
##speeders (< 240 s), time-outs (> 1,200 s) and non-citizens (analysis.R L205-208); the variables
##for that are kept (cov_duration_sec, cov_citizenship), as are the panel's own quality flags
##(cov_panel_goodcase, cov_panel_removedcase). No survey weight is deposited; analysis.R
##assigns education weights (1.16/0.98/0.90) but passes the misspelled `weigths`, so its models
##are unweighted; not kept.
##Covariates (answer text as exported, in English for both languages): cov_age (Q4, years),
##cov_gender (Q5: A man -> male, A woman -> female, Non-binary -> other, Prefer not to say -> NA),
##cov_education (Q6), cov_citizenship (Q3), cov_race (Q7, multi-select, comma-joined as
##exported), cov_province (Q8), cov_follow_politics (Q33), cov_party_id (Q34), cov_party_strength
##(Q35-Q39, the one asked), leader (Q40) and party (Q41) thermometers 0-100, vote 2021/2025 and
##Ontario 2025 (Q42-Q47), and the likelihood/liking of four outcomes (CPCMAJ, CPCMIN, LIBMAJ,
##LINMIN = Liberal minority; Q30 likely 0-10, Q31 like 0-10).
##Dropped (PII / platform): IPAddress, LocationLatitude/Longitude, ResponseId, PID (panel id),
##Recipient* and ExternalReference (empty), timestamps, consent Q1.
##N: 2,487 respondents (EN 2,018, FR-CA 469). The authors' good-case rule leaves 2,015, the same
##count as the panel's goodcase = yes; the article was not read, so its reported N is unchecked.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "Cdn Elxn-Outcomes_June 22, 2025_08.06.csv"), header = FALSE, encoding = "UTF-8", colClasses = "character")
h <- trimws(gsub(" ", "", unlist(r[1]))); r <- r[-(1:3)]
stopifnot(!anyDuplicated(h)); setnames(r, h)
ch <- c("Q11", "Q14", "Q17", "Q20", "Q23", "Q26"); rt <- c("Q12", "Q15", "Q18", "Q21", "Q24", "Q27")
r <- r[Finished == "True" & Reduce(`&`, lapply(ch, function(v) r[[v]] %in% c("Outcome 1", "Outcome 2")))]
r[, id := seq_len(.N)]
en <- c("Number of Parties in the House of Commons" = "parties", "Performance of winning party" = "performance",
        "Turnout" = "turnout", "Representation of Women" = "women", "Ballot" = "ballot",
        "Representation of Visible Minorities" = "minorities",
        "Nombre de partis à la Chambre des communes" = "parties", "Performance du parti gagnant" = "performance",
        "Taux de participation" = "turnout", "Représentation des femmes" = "women", "Bulletin de vote" = "ballot",
        "Représentation des minorités visibles" = "minorities")
rows <- list()
for (t in 1:6) for (p in 1:2) {
  x <- data.table(id = r$id, task = t, profile = p,
                  choice = as.integer(r[[ch[t]]] == paste("Outcome", p)), rating = as.integer(r[[paste0(rt[t], "_", p)]]))
  for (k in 1:6) {
    nm <- unname(en[trimws(r[[sprintf("F-%d-%d", t, k)]])]); stopifnot(!anyNA(nm))
    lv <- trimws(r[[sprintf("F-%d-%d-%d", t, p, k)]])
    for (a1 in unique(nm)) { i <- nm == a1; x[i, (paste0("attr_", a1)) := lv[i]]; x[i, (paste0("attrpos_", a1)) := k] }
  }
  rows[[length(rows) + 1]] <- x
}
d <- rbindlist(rows, use.names = TRUE)
an <- c("parties", "performance", "turnout", "women", "ballot", "minorities")
setcolorder(d, c("id", "task", "profile", "choice", "rating", paste0("attr_", an), paste0("attrpos_", an)))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr")]), d[, all(.SD != ""), .SDcols = patterns("^attr_")],
          d[, sum(choice), .(id, task)][, all(V1 == 1)],
          d[, uniqueN(paste(attrpos_parties, attrpos_performance, attrpos_turnout, attrpos_women, attrpos_ballot)), id][, all(V1 == 1)])
stopifnot(all(d$rating %in% c(0:10, NA)))
nul <- function(x) { x <- trimws(x); x[x == ""] <- NA; x }
stopifnot(all(r$Q5 %in% c("A man", "A woman", "Non-binary", "Prefer not to say")))
cv <- data.table(id = r$id, cov_language = r$UserLanguage, cov_age = as.integer(r$Q4),
  cov_gender = c("A man" = "male", "A woman" = "female", "Non-binary" = "other")[r$Q5],
  cov_education = nul(r$Q6), cov_citizenship = nul(r$Q3), cov_race = nul(r$Q7), cov_province = nul(r$Q8),
  cov_follow_politics = nul(r$Q33), cov_party_id = nul(r$Q34),
  cov_party_strength = nul(paste0(r$Q35, r$Q36, r$Q37, r$Q38, r$Q39)),
  cov_duration_sec = as.integer(r[["Duration (in seconds)"]]),
  cov_panel_goodcase = nul(r$goodcase), cov_panel_removedcase = nul(r$removedcase))
th <- c(Q40_1 = "therm_carney", Q40_2 = "therm_poilievre", Q40_3 = "therm_singh", Q40_4 = "therm_blanchet", Q40_5 = "therm_may",
        Q40_7 = "therm_trudeau", Q41_1 = "therm_liberal", Q41_2 = "therm_conservative", Q41_3 = "therm_ndp", Q41_4 = "therm_bq",
        Q41_5 = "therm_green", CPCMAJ_Q30_1 = "likely_cpc_majority", CPCMAJ_Q31_1 = "like_cpc_majority",
        CPCMIN_Q30_1 = "likely_cpc_minority", CPCMIN_Q31_1 = "like_cpc_minority", LIBMAJ_Q30_1 = "likely_lib_majority",
        LIBMAJ_Q31_1 = "like_lib_majority", LINMIN_Q30_1 = "likely_lib_minority", LINMIN_Q31_1 = "like_lib_minority")
for (v in names(th)) cv[, (paste0("cov_", th[[v]])) := as.integer(nul(r[[v]]))]
vt <- c(Q42 = "turnout_2021", Q43 = "vote_2021", Q44 = "turnout_2025", Q45 = "vote_2025", Q46 = "turnout_ontario_2025", Q47 = "vote_ontario_2025")
for (v in names(vt)) cv[, (paste0("cov_", vt[[v]])) := nul(r[[v]])]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "sevi_2026_election_outcomes.csv"))
