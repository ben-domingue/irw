##Constituency-candidate selection conjoint among German party members (November 2018) from
##Berz, J., & Jankowski, M. (2022). Local preferences in candidate selection: Evidence from a conjoint
##experiment among party leaders in Germany. Party Politics, 28(6), 1136-1149.
##https://doi.org/10.1177/13540688211041770
##Replication data: Harvard Dataverse doi:10.7910/DVN/E2QITV, CC0 1.0, no restricted files.
##Files read: cj_data_prepared.csv (Qualtrics export, ";"-separated, row 2 = question text) and
##df_survey.rds (the authors' cleaned respondent file, keyed by ResponseId: block-order flags
##LTFIRST/BTFIRST). Read as text only: berz_jankowski_analysis.R, read_qualtrics.R (the authors'
##copy of cjoint::read.qualtrics: F-<task>-<attribute> = attribute name, F-<task>-<profile>-<attribute>
##= level; response column k belongs to task k).
##Usage: Rscript berz_2022.R <raw dir> <output dir>
##
##310 respondents (304 finished; all 310 answered all 10 tasks), fielded by e-mail on 2018-11-19 and
##after; party members (Q35: AfD, Grüne, CDU/CSU, Linke, FDP, SPD); the article's title calls them
##party leaders. The analysis code's own count (nrow/20) is 310; the triage note said 309.
##Each respondent chose between two constituency candidates (Kandidat 1 = profile 1, 2 = profile 2)
##in 5 tasks for the Bundestag and 5 for the Landtag (a state parliament); the two blocks came in
##random order (df_survey LTFIRST = 1 for 152, BTFIRST = 1 for 158). Here `task` is the DISPLAY
##order: the first block's tasks are 1-5 (assuming the within-block order cj_*1..cj_*5 is the shown
##order); trial_parliament = "Bundestag" / "Landtag". The authors number Bundestag tasks 1-5 and
##Landtag 6-10 regardless of order.
##Outcome: choice. Bundestag tasks: "Welchen Kandidat bevorzugen Sie als Wahlkreiskandidaten für die
##Bundestagswahl?"; Landtag: "... für die Landtagswahl?" (Qualtrics question text); answers 1/2 only,
##forced choice, no missing.
##Attributes (German text as displayed; 7 attributes, all from the F- columns):
##  attr_local_bodies "Arbeitet regelmäßig in lokalen Parteigremien": Ja / Nein
##  attr_local_experience "Erfahrung in der Lokalpolitik": Keine / 1 Jahr / 4 Jahre / 7 Jahre
##  attr_lives_in_district "Wohnt im Wahlkreis seit": der Geburt / 15 Jahren / 8 Jahren / 2 Jahren
##  attr_dissent "Stellt eigene Überzeugung vor Position der Partei": nie / selten / gelegentlich / häufig
##  attr_gender "Geschlecht": Männlich / Weiblich
##  attr_education "Bildung": Hauptschule + Berufsausbildung / Mittlere Reife + Berufsausbildung /
##    Abitur + Berufsausbildung / Abitur + Studium
##  attr_age "Alter": 23 Jahre / 31 Jahre / 39 Jahre / 46 Jahre / 57 Jahre
##Attribute row order was randomized per respondent (identical across that respondent's 10 tasks,
##checked); attrpos_<name> gives each attribute's row (1-7).
##Covariates (answer text as in the export; refusals none): cov_gender (Q39 Männlich = male,
##Weiblich = female), cov_age (Q40, years), cov_party_member (Q35 "In welcher Partei sind Sie
##Mitglied?"), cov_membership_years (Q36, text e.g. "5 Jahre", "mehr als 10 Jahre"), cov_activity
##(Q51, participation outside campaigns), cov_mandate (Q33 Ja/Nein: holds an elected mandate),
##cov_left_right_self / cov_left_right_party (Q28_1 / Q29_1, 0 = ganz links .. 10 = ganz rechts; the
##export writes the end points as "links"/"rechts", mapped to 0/10),
##cov_satisfaction_federal / _state / _local (Q30_1-3 answer text), cov_bundesland (Q47).
##Dropped: Qualtrics metadata and ResponseId (re-keyed in source order), empty recipient-name/e-mail
##fields, free-text answers (Q34 other mandate, Q38 other party, Q43 cooperation list with typed
##parties), representation-share items Q27/Q53, issue items Q31, Q32 ("Aufstehen!" rating, mixed
##codes/text), the authors' derived variables. No weight.
##Checks: cov_left_right_self equals the authors' left_right_self (df_survey.rds) for all 310.
##Marginal means: candidates who often put their own convictions first ("häufig") are chosen 0.39,
##living in the district for only 2 years 0.46. Not compared to the article (not accessed).
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
df <- as.data.table(read.csv(file.path(raw, "cj_data_prepared.csv"), sep = ";", check.names = FALSE,
                             encoding = "UTF-8", colClasses = "character"))
qtext <- unlist(df[1]); df <- df[-1]
s <- as.data.table(readRDS(file.path(raw, "df_survey.rds")))
stopifnot(identical(df$ResponseId, s$qtx_id), all(xor(s$LTFIRST == "1", s$BTFIRST == "1")),
          all(qtext[paste0("cj_bt", 1:5)] == "Welchen Kandidat bevorzugen Sie als Wahlkreiskandidaten für die Bundestagswahl?"),
          all(qtext[paste0("cj_lt", 1:5)] == "Welchen Kandidat bevorzugen Sie als Wahlkreiskandidaten für die Landtagswahl?"))
anames <- c("Arbeitet regelmäßig in lokalen Parteigremien" = "local_bodies", "Erfahrung in der Lokalpolitik" = "local_experience",
            "Wohnt im Wahlkreis seit" = "lives_in_district", "Stellt eigene Überzeugung vor Position der Partei" = "dissent",
            "Geschlecht" = "gender", "Bildung" = "education", "Alter" = "age")
resp <- c(paste0("cj_bt", 1:5), paste0("cj_lt", 1:5))
lt_first <- s$LTFIRST == "1"
rows <- list()
for (k in 1:10) for (p in 1:2) {
  r <- data.table(rid = seq_len(nrow(df)), src_task = k, profile = p)
  ans <- as.integer(df[[resp[k]]]); stopifnot(all(ans %in% 1:2))
  r[, choice := as.integer(ans == p)]
  for (j in 1:7) {
    nm <- anames[df[[sprintf("F-%d-%d", k, j)]]]; stopifnot(!anyNA(nm))
    lv <- df[[sprintf("F-%d-%d-%d", k, p, j)]]; stopifnot(all(lv != ""))
    for (u in unique(nm)) { w <- nm == u; r[w, paste0("attr_", u) := lv[w]]; r[w, paste0("attrpos_", u) := j] }
  }
  rows[[length(rows) + 1]] <- r
}
d <- rbindlist(rows, fill = TRUE)
stopifnot(!anyNA(d))
d[, trial_parliament := ifelse(src_task <= 5, "Bundestag", "Landtag")]
d[, task := ifelse(lt_first[rid], ifelse(src_task <= 5, src_task + 5L, src_task - 5L), src_task)]
d[, src_task := NULL]
## attribute order constant within respondent
stopifnot(d[, uniqueN(paste(attrpos_local_bodies, attrpos_local_experience, attrpos_lives_in_district, attrpos_dissent,
                            attrpos_gender, attrpos_education, attrpos_age)), rid][, all(V1 == 1)])
stopifnot(d[, sum(choice), .(rid, task)][, all(V1 == 1)])
nz <- function(x) ifelse(x == "", NA, x)
## the export writes the scale end points as text: "links" = 0 (ganz links), "rechts" = 10 (ganz rechts)
lr <- function(x) { stopifnot(all(x %in% c("links", "rechts", as.character(1:9)))); as.integer(ifelse(x == "links", "0", ifelse(x == "rechts", "10", x))) }
cv <- data.table(rid = seq_len(nrow(df)),
  cov_gender = c("Männlich" = "male", "Weiblich" = "female")[df$Q39],
  cov_age = as.integer(df$Q40), cov_party_member = nz(df$Q35), cov_membership_years = nz(df$Q36),
  cov_activity = nz(df$Q51), cov_mandate = nz(df$Q33),
  cov_left_right_self = lr(df$Q28_1), cov_left_right_party = lr(df$Q29_1),
  cov_satisfaction_federal = nz(df$Q30_1), cov_satisfaction_state = nz(df$Q30_2), cov_satisfaction_local = nz(df$Q30_3),
  cov_bundesland = nz(df$Q47))
stopifnot(!anyNA(cv$cov_gender))
d <- cv[d, on = "rid"]
setnames(d, "rid", "id")
setcolorder(d, c("id", "task", "profile", "choice", sort(grep("^attr_", names(d), value = TRUE)),
                 sort(grep("^attrpos_", names(d), value = TRUE)), "trial_parliament"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "berz_2022_candidate_selection.csv"))
