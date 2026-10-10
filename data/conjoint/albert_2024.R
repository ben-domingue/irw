##Primary-election candidate conjoint (Study 1) from
##Albert, Z., & Costa, M. (2024). Winning at all costs? How negative partisanship affects
##voter decision-making. Political Behavior, 47(3), 963-989.
##https://doi.org/10.1007/s11109-024-09974-2
##Replication data: Harvard Dataverse doi:10.7910/DVN/1TYGV6, CC0 1.0, no restricted files.
##Files read: study1_data.csv (Dataverse "original format" download, saved as study1.csv) and
##butler_homola_names_coded.csv (saved as names.csv; read only to check that every displayed
##name is in the authors' coding list). study1_results.R (authors' code) read as text for the
##outcome meanings and level recodes. The deposit has no questionnaire or codebook and the
##article is not open access, so outcome wording below is a paraphrase of the authors' code.
##Usage: Rscript albert_2024.R <raw dir> <output dir>
##
##6,548 rows in the Qualtrics export; 2,913 respondents answered at least one conjoint
##question (1,690 in the Democratic block, 1,223 in the Republican block). Respondents
##(partisans and leaners) chose between two hypothetical candidates of their own party
##("Candidate A" = profile 1, "Candidate B" = profile 2) in up to 6 tasks. Independents
##(573 rows with conjoint profiles generated but no answers) and respondents who failed
##attentioncheck1 (the survey ended for them) have no outcomes and are omitted.
##Attributes, as stored in the export (Qualtrics piped text, the fragment inserted into the
##profile sentence; the surrounding sentence is not in the deposit):
##  attr_name      candidate name (72 names from Butler & Homola 2017, coded by the authors for
##                 sex and race in butler_homola_names_coded.csv: these carry candidate gender
##                 and race; crosswalk signal = name)
##  attr_win       "has" / "does NOT have" (the authors recode these to Win / Lose: chance of
##                 winning the general election)
##  attr_ideology  "Rated 1 (very liberal)" ... "Rated 5 (somewhat conservative)" for
##                 Democratic-block respondents (ideology_demA/B_t), "Rated 1 (very
##                 conservative)" ... "Rated 5 (somewhat liberal)" for Republican-block
##                 respondents (ideology_repubA/B_t). The export fills both sets for everyone;
##                 the set kept is the one for the block the respondent answered, as in the
##                 authors' code (which uses pid3; for all answering respondents the block and
##                 pid3 agree).
##  attr_age       35-75, as text
##trial_primary = Democratic / Republican: which party's candidates the task showed (from
##which of vote_dem<t> / vote_repub<t> holds the answer).
##Outcomes (both forced choice between A and B, no opt-out; source codes 1 = A, 2 = B):
##  choice           vote_<party><t>: which candidate the respondent would vote for (the
##                   authors' "strategic choice", plot title "Vote for")
##  choice_represent sincere_<party><t>: which candidate the respondent thinks would best
##                   represent their interests (authors' "sincere choice", plot title "Thinks
##                   represents best")
##Randomization restrictions: none documented; within a task the two names always differ.
##Covariates keep the source's numeric codes, since the deposit has no codebook:
##cov_gender_code, cov_race_code, cov_edu_code, cov_pid_code (authors' code: 1 = Democrat,
##2 = Republican, 3-5 non-partisan options), cov_pid_ind_code (leaner follow-up: 1 =
##Democrat, 2 = Republican, 3 = neither, per authors' code), cov_partywin_dems_code /
##cov_partywin_repubs_code (importance of the party winning; the authors recode 5=1, 6=2, 3=3,
##2=4 with 4 = most important), cov_ideo7 (1 = very liberal ... 7 = very conservative,
##authors' code), feeling thermometers 0-100 (Democrats, Republicans, Trump, Biden), and
##cov_attentioncheck2_1..5 (the five boxes of a check-all attention item, 1 = ticked).
##Dropped: Qualtrics ResponseId (re-keyed to integers in file order), consent, attentioncheck1
##(constant 3 = pass among answering respondents), the 3,635 rows without conjoint answers.
##Study 2 (study2_data.csv, 7,627 rows) is not built: the export records only Candidate A's
##issue positions and win prospects, and with no questionnaire Candidate B's description is
##unknown.
##N vs paper: not checked against the article text (paywalled).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "study1.csv"), na.strings = "")
nm <- fread(file.path(raw, "names.csv"))
stopifnot(!anyDuplicated(r$ResponseId))
r[, id := seq_len(.N)]
d <- rbindlist(lapply(1:6, function(t) rbindlist(lapply(c("dem", "repub"), function(pt) {
  v <- r[[sprintf("vote_%s%d", pt, t)]]; s <- r[[sprintf("sincere_%s%d", pt, t)]]
  k <- which(!is.na(v) | !is.na(s))
  rbindlist(lapply(1:2, function(p) {
    ab <- c("A", "B")[p]
    data.table(id = r$id[k], task = t, profile = p,
               choice = as.integer(v[k] == p), choice_represent = as.integer(s[k] == p),
               trial_primary = c(dem = "Democratic", repub = "Republican")[[pt]],
               attr_name = r[[sprintf("name%s_%d", ab, t)]][k],
               attr_win = r[[sprintf("win%s_%d", ab, t)]][k],
               attr_ideology = r[[sprintf("ideology_%s%s_%d", pt, ab, t)]][k],
               attr_age = as.character(r[[sprintf("age%s_%d", ab, t)]][k]))
  }))
}))))
stopifnot(!anyNA(d[, .(attr_name, attr_win, attr_ideology, attr_age)]),
          all(d$attr_name %in% nm$Name), all(d$attr_win %in% c("has", "does NOT have")),
          d[, uniqueN(trial_primary), id][, all(V1 == 1)],
          d[, .N, .(id, task)][, all(N == 2)],
          d[, sum(choice), .(id, task)][, all(is.na(V1) | V1 == 1)],
          d[, sum(choice_represent), .(id, task)][, all(is.na(V1) | V1 == 1)],
          d[, uniqueN(attr_name), .(id, task)][, all(V1 == 2)])
cv <- r[, .(id, cov_gender_code = gender, cov_race_code = race, cov_edu_code = edu, cov_pid_code = pid,
            cov_pid_ind_code = pid_ind, cov_partywin_dems_code = partywin_dems, cov_partywin_repubs_code = partywin_repubs,
            cov_ideo7 = ideo7, cov_feelingtherm_dems = feelingtherm_dems, cov_feelingtherm_repubs = feelingtherm_repubs,
            cov_feelingtherm_trump = feelingtherm_trump, cov_feelingtherm_biden = feelingtherm_biden,
            cov_attentioncheck2_1 = attentioncheck2_1, cov_attentioncheck2_2 = attentioncheck2_2,
            cov_attentioncheck2_3 = attentioncheck2_3, cov_attentioncheck2_4 = attentioncheck2_4,
            cov_attentioncheck2_5 = attentioncheck2_5)]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "albert_2024_negative_partisanship.csv"))
