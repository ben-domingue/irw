##Malawi MP candidate conjoint after voter-education videos from
##Ofosu, G. K., Seeberg, M. B., & Wahman, M. (2026). Messages matter: How voter education
##campaigns affect citizens' willingness to vote for women. Journal of Politics, 88(1), 145-161.
##https://doi.org/10.1086/734252
##Replication data: Harvard Dataverse doi:10.7910/DVN/6FHV5B, CC0 1.0. Files read:
##mm_conjoint_data.csv and mm_respondent_data.csv (Dataverse "original format" downloads,
##saved as conj.csv and resp.csv). Read as text: readme,
##ofosu_seeberg_wahman_replicationfiles_codebook.pdf (value labels), ofosu_seeberg_wahman_codes.Rmd
##(paper text + analysis). Not downloaded: V-Dem-CY-Full+Others-v12.dta (986 MB, case selection only).
##Usage: Rscript ofosu_2026.R <dir holding conj.csv and resp.csv> <output dir>
##
##Face-to-face survey (IPOR, random walk, gender quota) in 12 rural constituencies of Malawi's
##Central and Southern regions, 2022. The respondent file has 2,239 non-pilot respondents
##(paper: 2,239; 872 control, 852 discrimination, 515 progress); 6 of them have no recorded
##conjoint answer at all, so the table has 2,233 (871 / 849 / 513). The 391 pilot interviews
##(validdata FALSE) and 2 rows with no validdata flag are dropped, as in the authors' code.
##Design: 6 pairs of hypothetical MP candidates, 5 attributes, read aloud while respondents saw
##visual symbols. Stored text = the codebook value labels (authors' English labels, not the
##spoken wording): gender Male/Female; party Independent/Minor/Major; policy focus
##Boreholes/Education/Roads; education Secondary/University; profession Teacher/Maize
##farmer/Major business owner. PARTY: the displayed label was the actual party name, customised
##per constituency: "Major" = the party whose presidential candidate won the constituency in
##2019, "Minor" = the runner-up (paper fn.); the names shown are not deposited.
##Levels uniform and independent (paper). Attribute order randomized once per respondent
##(paper); attrpos_* from the respondent file's *_order columns (1-5; missing for 13 respondents).
##Outcomes, asked in random order per task (trial_self_first = 1 if Q1 came first):
##  choice: "Which of these two candidates would you vote for as your MP?"
##  choice_others: "Which of these two candidates do you think others in your constituency would
##    vote for as their MP?"
##  Forced choice, no "don't know" (paper). Yet 118 tasks have neither candidate chosen on Q1 and
##  164 on Q2: the deposit has no answer for them, so that outcome is set missing (NA) on both
##  profiles of those tasks; no opt-out was offered. The 62 tasks with no answer to either
##  question are dropped (26,744 rows); after that 25 tasks lack Q1 and 56 lack Q2.
##trial_video = the video shown before the conjoint (randomized per respondent; source tr_video):
##  "Control" (product advert), "Low viability" (= the paper's discrimination campaign),
##  "High viability" (= the paper's progress campaign); mapping from the counts above and the
##  authors' code (tr_video_lv relevels to "Low viability").
##Covariates: cov_age (q5_age), cov_gender (q4: 1 Male, 2 Female, 3 Prefer not to say),
##cov_region (Central/Southern), cov_constituency (q2 label), cov_vote_man_more_likely_win (q19_v),
##cov_more_women_mps_2025 (q20_v), cov_woman_faces_discrimination (q21_v),
##cov_men_better_leaders (q22_v) (all 1 Strongly agree ... 4 Strongly disagree, -999 refused,
##999 don't know), cov_close_to_party (q27: 1 No, 2 Yes, -999, 999), cov_party_close (q28 codes,
##codebook), cov_voted_last_election (turnout_last_elect, 0/1).
##Dropped: respondent uuid (re-keyed), enumerator NAMES, interview date, free-text q23, the
##video recall item q24, the authors' derived dummies (female, primary_or_less, assets, ethnic_*,
##party_*, conservative, ...).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cj <- fread(file.path(raw, "conj.csv"))
rs <- fread(file.path(raw, "resp.csv"), encoding = "UTF-8")
rs <- rs[validdata %in% TRUE]
stopifnot(nrow(rs) == 2239, !anyDuplicated(rs$KEY))
rs[, id := as.integer(factor(KEY))]
lab <- list(rd_rand_a_party = c("Independent", "Minor", "Major"), rd_rand_a_promises = c("Boreholes", "Education", "Roads"),
            rd_rand_a_education = c("Secondary", "University"), rd_rand_a_gender = c("Male", "Female"),
            rd_rand_a_profession = c("Teacher", "Maize farmer", "Major business owner"))
cj <- cj[PARENT_KEY %in% rs$KEY]
d <- cj[, .(KEY = PARENT_KEY, task = as.integer(round_num), profile = as.integer(candidate),
            choice = as.integer(outcome_binary_resp), choice_others = as.integer(outcome_binary_other),
            trial_self_first = as.integer(resp_pref_first))]
for (v in names(lab)) d[, paste0("attr_", sub("rd_rand_a_", "", v)) := lab[[v]][cj[[v]] + 1L]]
setnames(d, "attr_promises", "attr_policy_focus")
d[, s := sum(choice), .(KEY, task)][s == 0, choice := NA_integer_]
d[, s := sum(choice_others), .(KEY, task)][s == 0, choice_others := NA_integer_][, s := NULL]
const <- c(`47` = "Nkhotakota South East", `44` = "Nkhotakota North East", `49` = "Ntchisi South", `50` = "Ntchisi North",
           `60` = "Salima Central", `59` = "Salima North", `143` = "Chiradzulu East", `140` = "Chiradzulu South",
           `193` = "Nsanje North", `191` = "Nsanje Central", `170` = "Phalombe Central", `169` = "Phalombe South")
cv <- rs[, .(KEY, id, attrpos_party = party_order, attrpos_policy_focus = promises_order, attrpos_education = education_order,
             attrpos_gender = gender_order, attrpos_profession = profession_order, trial_video = tr_video,
             cov_age = q5_age, cov_gender = q4, cov_region = c(`2` = "Central", `3` = "Southern")[as.character(region)],
             cov_constituency = const[as.character(q2)], cov_vote_man_more_likely_win = q19_v, cov_more_women_mps_2025 = q20_v,
             cov_woman_faces_discrimination = q21_v, cov_men_better_leaders = q22_v, cov_close_to_party = q27,
             cov_party_close = q28, cov_voted_last_election = turnout_last_elect)]
d <- merge(d, cv, by = "KEY")[, KEY := NULL]
d <- d[!(is.na(choice) & is.na(choice_others))]
stopifnot(uniqueN(d$id) == 2233, nrow(d) == 26744, d[, .N, .(id, task)][, all(N == 2)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          d[, sum(choice), .(id, task)][, all(V1 == 1, na.rm = TRUE)], d[, sum(choice_others), .(id, task)][, all(V1 == 1, na.rm = TRUE)],
          d[, uniqueN(trial_video), id][, all(V1 == 1)], d[, uniqueN(id), trial_video][order(trial_video), V1] == c(871, 513, 849))
setcolorder(d, c("id", "task", "profile", "choice", "choice_others"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ofosu_2026_malawi_women_candidates.csv"))
