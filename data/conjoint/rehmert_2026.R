##Paired conjoint of German party delegates choosing between nomination candidates, from
##Rehmert, J. (2026). Intra-party competition, geographic responsiveness and incumbent deselection in closed-list PR.
##The Journal of Politics, 88(2), 572-585. https://doi.org/10.1086/734244
##Replication data: Harvard Dataverse doi:10.7910/DVN/VELXO1, CC0 1.0. Files read: cj_1.RDS, data_description_cj_1.txt (codebook),
##rep_figure2_3_6_7_8_9.R (text, not run; the authors' model formula).
##Usage: Rscript rehmert_2026.R <dir holding cj_1.RDS> <output dir>
##
##The deposit has 648 delegates of five German parties (Greens, CDU, FDP, Linke, SPD; 35 have no party recorded), 5 tasks x 2
##profiles each. In 349 tasks (both profiles) the choice is NA (unanswered); those tasks are omitted (rows with no outcome), leaving
##591 respondents with at least one answered task. Forced choice (exactly one chosen in every kept task, verified), so no opt-out. Task and profile are recorded (TaskID, Profile).
##Eight attributes (level text as stored; the deposit stores readable text, which the authors' figure code uses as plot labels):
##  age (in his/her 30s/50s/70s), sex (Man/Woman), district nomination (Has / Does not have a district nomination),
##  ideology (Centrist/Left-wing/Right-wing), place of birth (in Respondent's PR District / in the area of the Respondent's
##  Local Chapter / Outside Respondent's PR District), interests represented (Respondent's Local Party Chapter / Other Local
##  Chapters in Respondent's PR District / Local Chapters outside Respondent's PR District), tenure (1st/2nd/3rd Term),
##  loyalty = deviation from the party line (Often/Rarely/Sometimes).
##Some levels are relative to the respondent (district, chapter), so the text is the template, not a place name.
##Randomization restrictions: none documented; the cross-tabulations of nomination x birth and ideology x interest are balanced.
##Level shares are near-equal (about 1/3 or 1/2).  Attribute order: not documented (the column order is the stored order).
##Choice question wording: NOT in the deposit and the article text was not retrievable (publisher page returned 403);
##recorded as unknown, not paraphrased.
##Covariates: cov_party (party of the delegate: B90/Grüne, CDU, FDP, LINKE, SPD; not necessarily party identification),
##cov_ideology_own (left-right self-placement 0-10, "Left-right self-placement by Delegate"; scale direction not stated in
##the codebook), cov_ideology_party (left-right placement of own party by the delegate, same scale).
##Dropped: ResponseId (Qualtrics id; respondents re-keyed to integers), ideol_leaning, ideol_cat(_f), cj_same_ideology
##(derived by the authors from the above). cj_2.RDS (attitude items for the delegates, no profiles) is not used.
##Respondent count 648 in the deposit (591 kept) vs the paper: not checked (full text unavailable).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(readRDS(file.path(raw, "cj_1.RDS")))
stopifnot(nrow(d) == 6480, uniqueN(d$ResponseId) == 648)
d <- d[!is.na(choice)]; stopifnot(nrow(d) == 5782, uniqueN(d$ResponseId) == 591)
d[, id := match(ResponseId, unique(ResponseId))]
d[, `:=`(task = as.integer(as.character(TaskID)), profile = as.integer(as.character(Profile)))]
stopifnot(all(d[, .(s = sum(choice), n = .N), by = .(id, task)][, s == 1 & n == 2]))
ch <- function(x) enc2utf8(iconv(as.character(x), "latin1", "UTF-8"))  # party labels are stored latin1 (Grüne)
r <- d[, .(id, task, profile, choice = as.integer(choice),
  attr_age = ch(cj_age), attr_sex = ch(cj_sex), attr_district_nomination = ch(cj_wk), attr_ideology = ch(cj_ideo),
  attr_birthplace = ch(cj_born), attr_interests = ch(cj_interest), attr_tenure = ch(cj_tenure), attr_loyalty = ch(cj_loyalty),
  cov_party = ch(party), cov_ideology_own = as.integer(ideology_own), cov_ideology_party = as.integer(ideology_pty))]
stopifnot(!anyNA(r[, 1:12]))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "rehmert_2026_geographic_responsiveness.csv"))
