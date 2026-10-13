##Online-abuse comments directed at (fictitious) politicians, Danish public, from
##Petersen, N. B. G., Pedersen, R. T., & Thau, M. (2025). Citizens' perceptions of online abuse directed at
##politicians: Evidence from a survey experiment. European Journal of Political Research, 64(2), 790-809.
##https://doi.org/10.1111/1475-6765.12724
##Replication data: Harvard Dataverse doi:10.7910/DVN/LIXDR1, CC0 1.0. Files read:
##"citizen_perceptions_of_online_abuse_replication.tab" downloaded in original format (= the Stata .dta
##with value labels, saved here as data.dta), the authors' replication .do file and the README PDF (read as
##text, not run). Usage: Rscript petersen_2025.R <dir holding data.dta> <output dir>
##
##2,050 rows (Danish citizens, online panel); 2,031 have comments (4 each); the 19 rows without comments are
##omitted. Comment-rows where all three outcomes are missing (287 of 8,124: unanswered or don't know) are omitted
##too ("Rows with no outcome"), which leaves 1,985 respondents and 7,837 rows. The paper reports about 2,000
##respondents; N not checked further.
##Each respondent read FOUR fictitious social-media comments about a fictitious politician, one per task:
##task k = comment type: 1 criticism (messages 1-5), 2 insult (6-10), 3 threat (11-15), 4 sexism (16-20); the
##message type is therefore tied to task position (checked: every row of task k holds only that type's
##comments), and the comment WITHIN the type is random. Attributes:
##  attr_name: first name of the politician, 40 names (20 female 1-20, 20 male 21-40), drawn with
##    replacement across the four tasks (some respondents see a name twice);
##  attr_message: the comment text (20 comments, Danish original not in the deposit; English labels from the
##    value labels). Messages 19 and 20 contain the template "[woman/man]" in the labels; stored as labelled,
##    not resolved;
##  attr_channel: Twitter / Facebook;
##  attr_party: the fictitious politician's party (12 parties occur: Social Democrats, Social Liberals,
##    Conservative Peoples' party, New Right, Socialist Peoples' Party, Liberal Alliance, Moderates, Danish
##    Peoples' Party, Liberals, Unity List, Denmark Democrats, The Alternative).
##The politician's gender (gender_post, pronoun) is determined by the name (checked: names 1-20 female,
##21-40 male in all rows) and is dropped as an attribute; it enters the crosswalk through attr_name
##(signal = name, the authors' gender_post coding). Derived (messagetype, ownparty*, fic_pol_sym*, *_std) not read.
##Outcomes (variable labels; scale from the do-file, which rescales (x-1)/6, so 1-7; 99 = don't know -> NA):
##  rating_abusive "The comment is abusive" (label: "The comments is abusive"), rating_tolerate "Politicians should
##  be able to tolerate comments like this", rating_report "I would report this message" (to Twitter/Facebook per
##  the authors' figure label). Scale anchors are not stated in the deposit. No choice, no opt-out.
##Covariates: cov_gender (woman: 0 Man, 1 Woman), cov_age (age, truncated at 81 by the authors for GDPR: 81 means
##81-93), cov_party_id (party_id_or_closer value labels; "Don't know" kept as text, NA when blank),
##cov_left_right (0 very left - 10 very right, 99 -> NA), cov_political_interest (0-10, 99 -> NA),
##trial_split_exposure_neg ("Exposed"/"Not exposed": the authors' randomized split; the willingness-to-run
##question wtr_pre_exposure was asked before exposure in one group only; not read further).
##Dropped: remaining pre-treatment items (vote, trust, social-media use, party sympathies), interview status.
##Respondent id = row number of the file (no platform id in the deposit).
##Restrictions: yes (comments tied to task position; the four messages of a respondent are distinct).
##Spot check: mean rating_abusive by comment type rises criticism < insult < threat.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- as.data.table(read_dta(file.path(raw, "data.dta")))
stopifnot(nrow(r) == 2050)
r[, id := .I]
lab <- function(v) { l <- attr(r[[v]], "labels"); setNames(names(l), as.character(l)) }
unlab <- function(x, l) unname(l[as.character(as.integer(x))])
lnm <- lab("name1"); lms <- lab("message1"); lch <- lab("channel_post1"); lpa <- lab("party1")
stopifnot(length(lnm) == 40, length(lms) == 20, length(lch) == 2)
for (k in 2:4) stopifnot(identical(lab(paste0("name", k)), lnm), identical(lab(paste0("message", k)), lms))
d <- rbindlist(lapply(1:4, function(k) {
  g <- as.integer(r[[paste0("gender_post", k)]]); nm <- as.integer(r[[paste0("name", k)]])
  x <- data.table(id = r$id, task = k, profile = 1L, nm = nm, g = g,
                  attr_name = unlab(nm, lnm), attr_message = unlab(r[[paste0("message", k)]], lms),
                  attr_channel = unlab(r[[paste0("channel_post", k)]], lch), attr_party = unlab(r[[paste0("party", k)]], lpa),
                  rating_abusive = as.integer(r[[paste0("abusive_", k)]]), rating_tolerate = as.integer(r[[paste0("legit_", k)]]),
                  rating_report = as.integer(r[[paste0("report_", k)]]))
  x[!is.na(nm)]
}))
stopifnot(all((d$nm > 20) == (d$g == 0)), uniqueN(d$id) == 2031, nrow(d) == 8124)
for (v in c("rating_abusive", "rating_tolerate", "rating_report")) {
  stopifnot(all(d[[v]] %in% c(1:7, 99L, NA)))
  set(d, which(d[[v]] == 99L), v, NA_integer_)
}
stopifnot(!anyNA(d$attr_name), !anyNA(d$attr_message), !anyNA(d$attr_channel), !anyNA(d$attr_party),
          d[, .N, .(id, task)][, all(N == 1)], d[, uniqueN(attr_message), id][, all(V1 == 4)])
d[, c("nm", "g") := NULL]
d <- d[!(is.na(rating_abusive) & is.na(rating_tolerate) & is.na(rating_report))]
lpi <- lab("party_id_or_closer"); lx <- lab("split_exposure_neg")
cv <- data.table(id = r$id, cov_gender = c("0" = "male", "1" = "female")[as.character(as.integer(r$woman))],
                 cov_age = as.integer(r$age), cov_party_id = unlab(r$party_id_or_closer, lpi),
                 cov_left_right = ifelse(as.integer(r$left_right) == 99L, NA, as.integer(r$left_right)),
                 cov_political_interest = ifelse(as.integer(r$interest) == 99L, NA, as.integer(r$interest)),
                 trial_split_exposure_neg = unlab(r$split_exposure_neg, lx))
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "petersen_2025_online_abuse.csv"))
