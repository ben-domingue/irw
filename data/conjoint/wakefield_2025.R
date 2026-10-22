##Latino voters' candidate conjoint (policy appeals) from
##Wakefield, D. (2025). It's the economy: The effect of economic policy appeals on Latino
##independents. Political Behavior, 47(4), 1571-1594. https://doi.org/10.1007/s11109-025-10004-y
##Replication data: Harvard Dataverse doi:10.7910/DVN/4UNMYC, CC0 1.0, no restricted files.
##Files read: njev_study3_clean.tab, downloaded in its original format (a Qualtrics export of
##study 3, one row per respondent, which carries the DISPLAYED policy text). Read as text:
##DW_ItsTheEconomy_ReplicationFiles-1.Rmd (the author's cleaning code: the candidate columns,
##the vote coding at lines 2634-2660 and the covariate items).
##Usage: Rscript wakefield_2025.R <dir holding njev_study3_clean.tab> <output dir>
##
##810 Latino US respondents (2023), 6 elections of two congressional candidates. 27 respondents
##have a recorded choice in election 6 but no attributes for its Republican profile; that task
##is dropped for them (the author's own long file drops the same 27 tasks), leaving 4,833 tasks
##and 9,666 rows, every task with exactly one chosen candidate.
##The deposit also ships njev_study3_conjointdata.tab, the author's long file. It is NOT used:
##its attribute columns hold his short codes ("Progressive", "Anti-Socialism", "No Policy")
##rather than the displayed text, and its two vote columns, built per party, are 0 on both
##profiles in 132 tasks and 1 on both in 135. Building from the wide export instead gives the
##displayed wording and a clean forced choice in all 4,860 tasks.
##
##Design. One Democratic and one Republican candidate per election, with party-specific policy
##option sets (hence restrictions = yes): the columns e<k>c1* are always the Democrat and
##e<k>c2* always the Republican, while `Cand1` (D or R, fixed for a respondent across all six
##elections) says which of the two was shown first. profile is that display position.
##  attr_party: Democrat / Republican.
##  attr_race: the candidate's race as displayed. The instrument varies the wording of the
##    Latino level itself ("Hispanic", "Latino", "Latinx"), kept as displayed rather than
##    collapsed as the author's recode does; the other level is "White".
##  attr_economics, attr_immigration, attr_abortion: the position as displayed, e.g. "Tax the
##    rich to make healthcare and education more affordable" (Democrat only), "Support free
##    markets instead of adopting socialist policies" (Republican only), "Invest in
##    infrastructure like roads and bridges" (both parties).
##A candidate with no position on an issue has the placeholder "_" in the export, which the
##author codes "No Policy"; it is stored as the reserved "(not shown)". Whether the row was
##displayed empty or omitted from the profile is not documented, so this is an inference, the
##only one in this table.
##Level shares are near-uniform within each party's option set, except that "(not shown)" is
##about a quarter of the economics attribute and a fifth of the other two.
##
##Outcome. choice: which of the two candidates the respondent would vote for
##(election<k>_choice = "Candidate 1" / "Candidate 2"; forced, no missing values).
##No question wording survives in the deposit (no instrument, no codebook).
##
##Covariates, all as answer text: cov_gender (Female / Male / "Non-binary / third gender" ->
##other, "Prefer not to say" -> NA), cov_age_group, cov_state, cov_registered_voter,
##cov_race (the panethnic item, multi-select, as stored), cov_national_origin,
##cov_english_skills, cov_spanish_skills, cov_party_id (the party question), cov_party_id_lean
##(the author's party_id, which folds in the strength and lean follow-ups: "Independent lean
##Dem" and so on), cov_linked_fate (how much what happens to other Latinos affects the
##respondent) and cov_duration_sec (the whole survey, Qualtrics "Duration (in seconds)").
##PII FOUND in njev_study3_clean.tab and dropped here: IPAddress, LocationLatitude,
##LocationLongitude, RecipientFirstName, RecipientLastName, RecipientEmail, ExternalReference,
##the free-text gender / race / national-origin "other" answers, and the Qualtrics timestamps.
##The Qualtrics ResponseId is re-keyed 1..n in file order. No survey weight ships with the
##deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "njev_study3_clean.tab"))
stopifnot(nrow(s) == 810L, uniqueN(s$ResponseId) == 810L, all(s$Cand1 %in% c("D", "R")))

disp <- function(x) { x <- trimws(as.character(x)); fifelse(x == "_" | x == "", "(not shown)", x) }
PARTYCOL <- c(Democrat = "c1", Republican = "c2")

rows <- rbindlist(lapply(1:6, function(k) rbindlist(lapply(names(PARTYCOL), function(party) {
  cc <- PARTYCOL[[party]]
  pos <- fifelse(s$Cand1 == substr(party, 1, 1), 1L, 2L)   # Cand1 names the party shown first
  data.table(ResponseId = s$ResponseId, task = k, profile = pos,
             choice = as.integer(s[[paste0("election", k, "_choice")]] == paste("Candidate", pos)),
             attr_party = party,
             attr_race = disp(s[[paste0("e", k, cc, "Race")]]),
             attr_economics = disp(s[[paste0("e", k, cc, "Econ")]]),
             attr_immigration = disp(s[[paste0("e", k, cc, "Immig")]]),
             attr_abortion = disp(s[[paste0("e", k, cc, "Abortion")]]))
}))))
stopifnot(nrow(rows) == 9720L, !anyNA(rows$choice))
## 27 respondents have no attributes for election 6's Republican profile although a choice is
## recorded; that task is dropped for them (the author's long file drops the same 27 tasks)
rows[, complete := !anyNA(.SD), .(ResponseId, task), .SDcols = patterns("^attr_")]
stopifnot(rows[complete == FALSE, uniqueN(ResponseId)] == 27L,
          rows[complete == FALSE, all(task == 6L)])
rows <- rows[complete == TRUE][, complete := NULL]
stopifnot(nrow(rows) == 9666L)

gender <- as.character(s$gender)
cov <- data.table(
  ResponseId = s$ResponseId,
  cov_gender = fcase(gender == "Female", "female", gender == "Male", "male",
                     gender == "Non-binary / third gender", "other"),
  cov_age_group = as.character(s$age),
  cov_state = as.character(s$state),
  cov_registered_voter = as.character(s$reg.voter),
  cov_race = as.character(s$race),
  cov_national_origin = as.character(s$natl.origin),
  cov_english_skills = as.character(s$english.skills),
  cov_spanish_skills = as.character(s$spanish.skills),
  cov_party_id = as.character(s$`party.id...43`),
  cov_party_id_lean = as.character(s$party_id),
  cov_linked_fate = as.character(s$lat.linked.fate),
  cov_duration_sec = suppressWarnings(as.numeric(s$`Duration (in seconds)`)))
for (v in names(cov)) if (is.character(cov[[v]])) set(cov, i = which(cov[[v]] == ""), j = v, value = NA_character_)

d <- merge(rows, cov, by = "ResponseId", all.x = TRUE, sort = FALSE)
d[, id := as.integer(frank(ResponseId, ties.method = "dense"))][, ResponseId := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "attr_party", "attr_race",
                 "attr_economics", "attr_immigration", "attr_abortion"))
stopifnot(d[, .N, .(id, task)][, all(N == 2L)],
          d[, sum(choice), .(id, task)][, all(V1 == 1L)],
          d[, uniqueN(profile), .(id, task)][, all(V1 == 2L)],
          d[, uniqueN(attr_party), .(id, task)][, all(V1 == 2L)],
          !anyNA(d[, grep("^attr_", names(d)), with = FALSE]),
          d[, all(attr_race %in% c("Hispanic", "Latino", "Latinx", "White"))],
          d[attr_party == "Democrat", !any(grepl("socialist", attr_economics))],
          d[attr_party == "Republican", !any(grepl("Tax the rich", attr_economics))],
          d[, uniqueN(id)] == 810L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wakefield_2025_latino_appeals.csv"))
