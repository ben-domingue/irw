##Candidate-photo survey experiment on Generation Z political engagement (US) from
##Deckman, M., & McDonald, J. (2022). Uninspired by old white guys: The mobilizing factor of younger, more
##diverse candidates for Gen Z women. Politics & Gender, 19(1), 195-219.
##https://doi.org/10.1017/S1743923X21000477
##Replication data: Harvard Dataverse doi:10.7910/DVN/VVDIOD, CC0 1.0, no restricted files, no terms.
##File read: "Deckman McDonald final data.tab" in its Stata "original format" download (saved as data.dta;
##2,210 rows x 64 columns, the authors' recoded analysis file). "Deckman McDonald final script.do" was read
##as text only. There is no questionnaire, codebook or raw (pre-recode) export in the deposit.
##Usage: Rscript deckman_2022.R <raw dir> <output dir>   (raw dir holds data.dta)
##
##2,210 Generation Z US respondents (the paper: a survey experiment embedded in a nationally representative
##survey of Gen Z citizens; sample provider and field dates are not in the deposit). Each was shown ONE
##Democratic politician and answered questions about future political engagement: a 2 x 2 x 2 factorial,
##one candidate per respondent, between-subject (8 cells of 256-294, `condition`). The candidate is a
##picture/profile (presentation = image); the deposit holds only the authors' condition coding, not the
##stimulus: age 22 ("Gen Z candidate") or 68 ("older candidate"), woman or man, White or Black.
##  attr_candidate_age     22 / 68        (condition label, e.g. "22whiteman"; genzcand)
##  attr_candidate_gender  woman / man
##  attr_candidate_race    White / Black
##The gender level is stated by the authors' condition coding only (there is no stimulus text), so the
##crosswalk signal is "photo". The levels are the authors' codes, not displayed sentences.
##Outcomes (rating_*): eight items on how likely the respondent is to take part in a political activity in
##the future, stored in the deposit only as the authors' 0-1 normalisations of 5-point items
##("act1norm".."act8norm", RECODE of activity_unlikely<activity>; values 0, .25, .5, .75, 1). The raw answer
##options and the direction are not in the deposit: the authors average the eight items into "future political
##engagement" (higher = more mobilized) and all eight correlate positively (r 0.05-0.61), so higher is taken
##as more likely to engage, but that is an inference. Activity names are from the .do file's headings.
##  rating_volunteer_campaign (act1), rating_protest_rally (act2), rating_encourage_vote (act3),
##  rating_discuss_politics (act4), rating_follow_news (act5), rating_run_for_office (act6),
##  rating_attend_meeting (act7), rating_social_media_issue (act8).
##Dropped: the dummies and interactions (blackwoman22 ..., nonprivtreat, genzcand/blackcand/femalecand,
##highgenid and all products), futureactivity / futureactivity2 / factormobilization (derived indices),
##the authors' race, partisanship (pid7, ideology), education-goal, religion, family-income items
##(numeric codes with no labels in the deposit), williamsfav and gender-identity scores (derived).
##Covariates: cov_gender (male, labelled female/male by the authors; missing 64), cov_party_id (pidwleaners,
##the authors' recode of 7-point party ID with leaners: Democrat / Republican / Pure Indie; NA for
##others). No opt-out (ratings only). Respondent id = row number (no id in the file).
##Count check: 2,210 respondents; 5 have no outcome and are dropped.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(file.path(raw, "data.dta")))
stopifnot(nrow(x) == 2210)
cond <- as.character(as_factor(x$condition))
stopifnot(all(cond %in% c("22blackwoman", "22whitewoman", "22blackman", "22whiteman", "68blackwoman", "68whitewoman", "68blackman", "68whiteman")))
m <- regmatches(cond, regexec("^(22|68)(black|white)(woman|man)$", cond)); m <- do.call(rbind, m)
stopifnot(identical(as.character(as_factor(x$genzcand)) == "Gen Z Candidate", m[, 2] == "22"),
          identical(as.character(as_factor(x$blackcand)) == "Black Cand", m[, 3] == "black"))
items <- c(rating_volunteer_campaign = "act1norm", rating_protest_rally = "act2norm", rating_encourage_vote = "act3norm",
           rating_discuss_politics = "act4norm", rating_follow_news = "act5norm", rating_run_for_office = "act6norm",
           rating_attend_meeting = "act7norm", rating_social_media_issue = "act8norm")
d <- data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L)
for (k in names(items)) { v <- as.numeric(x[[items[k]]]); stopifnot(all(v %in% c(0, .25, .5, .75, 1, NA))); set(d, j = k, value = v) }
d[, `:=`(attr_candidate_age = m[, 2], attr_candidate_gender = m[, 4],
         attr_candidate_race = ifelse(m[, 3] == "white", "White", "Black"))]
pw <- as.character(as_factor(x$pidwleaners)); stopifnot(all(is.na(pw) | pw %in% c("Democrat", "Republican", "Pure Indie")))
g <- as.character(as_factor(x$male)); stopifnot(all(is.na(g) | g %in% c("female", "male")))
cv <- data.table(id = d$id, cov_gender = g, cov_party_id = pw)
d <- d[!Reduce(`&`, lapply(names(items), function(k) is.na(d[[k]])))]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "deckman_2022_genz_candidates.csv"))
