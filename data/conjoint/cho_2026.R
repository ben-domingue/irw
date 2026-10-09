##Congressional-candidate paired conjoints with Asian American respondents (pan-ethnic and
##co-ethnic designs) from
##Cho, J. J., Costa, M., & Horiuchi, Y. (2026). Descriptive or partisan representation? Examining
##trade-offs for Asian Americans. British Journal of Political Science, 56, e8.
##https://doi.org/10.1017/S0007123425101324
##Replication data: Harvard Dataverse doi:10.7910/DVN/OSSXEC, CC0 1.0, no restricted files, no terms.
##Files read (from ReplicationPackage.tar): R/data/Asian+American+Tradeoffs+Survey+-+Main_April+16,+2022_10.33.csv
##(Qualtrics export, 3 header rows), R/documents/Asian_American_Tradeoffs_Survey_-_Main.docx
##(questionnaire), R/documents/pre-registration.pdf (OSF k4sp5); the authors' R scripts
##(01_read_data.R, functions/reshape_conjoint.R) read as text, not run. Article (open access) for
##level probabilities, fielding and sample.
##Usage: Rscript cho_2026.R <dir holding the csv> <output dir>
##
##Lucid Marketplace, 26 Feb - 21 Mar 2022, respondents identifying as Asian or Asian American,
##randomly assigned to one of two designs (Qualtrics embedded field Block), which the article
##analyses separately and which differ in the Race/Ethnicity levels -> two tables:
##  cho_2026_asian_panethnic  (Block "Asian American", Qualtrics fields B-*): Asian American /
##     White / Black / Hispanic
##  cho_2026_asian_coethnic   (Block "Ethnic American", fields D-*): Chinese / Indian / Filipino /
##     Vietnamese / Korean / Japanese American / White / Black / Hispanic
##Other attributes (both): Party (Democrat/Republican), Votes with their Party (Sometimes/Often),
##Sex (Female/Male), Was Born in the U.S. (Yes/No), Education (Bachelor's degree/Professional degree),
##Advances Favorable Legislation for District Constituents (Sometimes/Often/Always). Level text as
##stored in the Qualtrics fields <B|D>-<task>-<profile>-<row> (attribute name in <B|D>-<task>-<row>).
##Probabilities (article): race/ethnicity Asian levels 50% combined (co-ethnic: ~8% each), White 30%,
##Black 10%, Hispanic 10%; education 68% professional / 32% bachelor's; others equal. Independent
##otherwise (data: pair compositions match independence).
##Attribute order: "randomized across respondents but fixed for each respondent" (pre-registration,
##article); attrpos_* = row position. In the co-ethnic block it varies across respondents (1,251
##distinct orders); in the pan-ethnic block every respondent has the SAME order (Race/Ethnicity,
##Party, Votes with their Party, Sex, Was Born in the U.S., Education, Advances ...), so the
##randomization did not operate there.
##10 tasks of 2 candidates, then task 11 = task 1 shown again with the same profiles in the same
##positions (questionnaire Task 11/11 pipes B-1-*/D-1-*; not swapped): stored as task 11 with
##trial_repeat_of = 1 and task 1's levels.
##Outcomes (questionnaire wording):
##  choice = "Which candidate are you most likely to vote for?" (Candidate 1/Candidate 2), forced.
##  rating = "Looking at just Candidate <k>, how likely are you to vote for this candidate for
##           Congress?" Very likely .. Very unlikely, stored 1-5 with 5 = Very likely (the authors'
##           coding in reshape_conjoint.R; the Qualtrics option codes run the other way).
##Sample: every respondent with at least one conjoint answer (2,813), less 8 (3 pan, 5 co) whose
##attribute fields were not saved at all (levels missing in source -> dropped): 1,403 pan-ethnic +
##1,403 co-ethnic; 58 answered only some tasks. The article's sample (2,362) = cov_final_status
##"Complete" AND cov_recaptcha_score >= 0.5 AND cov_party_field != "Independent" (01_read_data.R);
##that filter gives 2,355 here (1,179 + 1,176): the 2,362 includes the 7 of those 8 respondents,
##whose profiles the authors' reshape also drops. Tasks with no answer at all are omitted.
##Covariates (answer text): cov_gender (Man -> male, Woman -> female, Non-binary -> other),
##cov_age_group, cov_education, cov_income ("Prefer Not to Answer" -> NA), cov_hispanic (race1),
##cov_race (race2, multi-select text), cov_heritage (countryorigin), cov_mother_us_born,
##cov_father_us_born, cov_us_born, cov_birth_country (immigrationr_country), cov_party_id (party:
##Democrat/Republican/Independent/Other/Not Sure), cov_party_strength_dem (partyD),
##cov_party_strength_rep (partyR), cov_party_lean (partyI), cov_ideology, cov_party_field and
##cov_ethnicity_field (the embedded fields Party/Ethnicity the survey piped into questions;
##Party = party with leaners), the 12 identity items (cov_partisan_id1..4, cov_coethnic_id1..4,
##cov_panethnic_id1..4, answer text), cov_attention_pass (screener2 == "Every day,Never", the
##instructed answer), cov_duration_sec (whole survey), cov_final_status (panel status; blank ->
##"Incomplete"), cov_recaptcha_score.
##Dropped: ResponseId, rid, pid, SUPPLIER_ID, SUPNAME, UserAgent (platform/panel IDs, device string),
##free text (gender_4_TEXT, race2_7_TEXT, countryorigin_15_TEXT, immigrationr_country_14_TEXT,
##feedback), dates, Qualtrics fraud scores, consent/screener1, and the Study 1 representation items
##(panE..outEcoP: a separate, non-conjoint question set). No IP or location columns in the export.
##No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "Asian+American+Tradeoffs+Survey+-+Main_April+16,+2022_10.33.csv")
hd <- names(fread(f, nrows = 0))
x <- fread(f, skip = 3, header = FALSE, col.names = hd, colClasses = "character", na.strings = NULL)
x <- x[Block != ""]
x[, rid0 := .I]
ratemap <- c("Very unlikely" = 1L, "Somewhat unlikely" = 2L, "Neither likely nor unlikely" = 3L,
             "Somewhat likely" = 4L, "Very likely" = 5L)
build <- function(blk, L, q) {
  s <- x[Block == blk]
  rows <- list()
  for (t in 1:11) {
    ts <- if (t == 11) 1 else t
    for (p in 1:2) {
      d <- data.table(rid0 = s$rid0, task = t, profile = p,
                      vote = s[[paste0(q, t, "_vote")]], pref = s[[paste0(q, t, "_cand", p, "pref")]])
      for (k in 1:7) {
        an <- s[[sprintf("%s-%d-%d", L, ts, k)]]; lv <- s[[sprintf("%s-%d-%d-%d", L, ts, p, k)]]
        d[, (paste0("A", k)) := an][, (paste0("V", k)) := lv]
      }
      rows[[length(rows) + 1]] <- d
    }
  }
  d <- rbindlist(rows)
  d <- d[!(vote == "" & pref == "")]
  # tasks with any answer keep both profiles
  ans <- d[, .(any = any(vote != "" | pref != "")), .(rid0, task)]
  long <- melt(d, id.vars = c("rid0", "task", "profile", "vote", "pref"),
               measure.vars = patterns(A = "^A", V = "^V"), variable.name = "pos")
  miss <- long[A == "" | V == "", unique(rid0)]
  stopifnot(long[rid0 %in% miss, all(A == "" & V == "")])   # whole respondent unsaved, never partial
  message(blk, ": ", length(miss), " respondents answered but have no saved attribute levels; dropped")
  long <- long[!rid0 %in% miss]; ans <- ans[!rid0 %in% miss]
  long[, attr := c("Race/Ethnicity" = "race_ethnicity", "Party" = "party", "Votes with their Party" = "votes_with_party",
                   "Sex" = "sex", "Was Born in the U.S." = "born_in_us", "Education" = "education",
                   "Advances Favorable Legislation for District Constituents" = "advances_legislation")[A]]
  stopifnot(!anyNA(long$attr))
  w <- dcast(long, rid0 + task + profile + vote + pref ~ attr, value.var = "V")
  p <- dcast(long, rid0 + task + profile ~ attr, value.var = "pos")
  setnames(p, setdiff(names(p), c("rid0", "task", "profile")), paste0("attrpos_", setdiff(names(p), c("rid0", "task", "profile"))))
  for (v in grep("^attrpos_", names(p), value = TRUE)) p[, (v) := as.integer(get(v))]
  an <- setdiff(names(w), c("rid0", "task", "profile", "vote", "pref"))
  setnames(w, an, paste0("attr_", an))
  w <- merge(w, p, by = c("rid0", "task", "profile"))
  w <- w[rid0 %in% ans[any == TRUE, rid0]]
  w <- w[ans[any == TRUE], on = .(rid0, task), nomatch = 0][, any := NULL]
  w[, choice := fifelse(vote == "", NA_integer_, as.integer(vote == paste("Candidate", profile)))]
  stopifnot(all(w$pref %in% c(names(ratemap), "")), all(w$vote %in% c("Candidate 1", "Candidate 2", "")))
  w[, rating := ratemap[pref]]
  w[, trial_repeat_of := fifelse(task == 11L, 1L, NA_integer_)]
  stopifnot(w[!is.na(choice), sum(choice), .(rid0, task)][, all(V1 == 1)],
            w[, .N, .(rid0, task)][, all(N == 2)])
  # covariates
  cv <- s[, .(rid0,
              cov_gender = c(Man = "male", Woman = "female", "Non-binary" = "other", "Other (Please specify):" = "other")[gender],
              cov_age_group = age, cov_education = education, cov_income = fifelse(income == "Prefer Not to Answer", NA_character_, income),
              cov_hispanic = race1, cov_race = race2, cov_heritage = countryorigin,
              cov_mother_us_born = immigrationm, cov_father_us_born = immigrationf, cov_us_born = immigrationr,
              cov_birth_country = immigrationr_country, cov_party_id = party, cov_party_strength_dem = partyD,
              cov_party_strength_rep = partyR, cov_party_lean = partyI, cov_ideology = ideology,
              cov_party_field = Party, cov_ethnicity_field = Ethnicity,
              cov_partisan_id1 = partisanID1, cov_partisan_id2 = partisanID2, cov_partisan_id3 = partisanID3, cov_partisan_id4 = partisanID4,
              cov_coethnic_id1 = coethnicID1, cov_coethnic_id2 = coethnicID2, cov_coethnic_id3 = coethnicID3, cov_coethnic_id4 = coethnicID4,
              cov_panethnic_id1 = panethnicID1, cov_panethnic_id2 = panethnicID2, cov_panethnic_id3 = panethnicID3, cov_panethnic_id4 = panethnicID4,
              cov_attention_pass = fifelse(screener2 == "", NA_integer_, as.integer(screener2 == "Every day,Never")),
              cov_duration_sec = as.numeric(`Duration (in seconds)`),
              cov_final_status = fifelse(FinalStatus == "", "Incomplete", FinalStatus),
              cov_recaptcha_score = as.numeric(fifelse(Q_RecaptchaScore == "", NA_character_, Q_RecaptchaScore)))]
  for (v in names(cv)) if (is.character(cv[[v]])) cv[get(v) == "", (v) := NA_character_]
  w <- merge(w, cv, by = "rid0")
  ids <- sort(unique(w$rid0)); w[, id := match(rid0, ids)]
  w[, c("rid0", "vote", "pref") := NULL]
  setcolorder(w, c("id", "task", "profile", "choice", "rating", grep("^attr_", names(w), value = TRUE),
                   grep("^attrpos_", names(w), value = TRUE), "trial_repeat_of"))
  setorder(w, id, task, profile); w
}
pan <- build("Asian American", "B", "asianam")
co <- build("Ethnic American", "D", "ethnicam")
auth <- function(w) uniqueN(w[cov_final_status == "Complete" & cov_recaptcha_score >= 0.5 & cov_party_field != "Independent", id])
message("respondents: ", uniqueN(pan$id), " + ", uniqueN(co$id), "; authors' sample: ", auth(pan), " + ", auth(co))
stopifnot(uniqueN(pan$id) == 1403, uniqueN(co$id) == 1403, auth(pan) + auth(co) == 2355)
fwrite(pan, file.path(out, "cho_2026_asian_panethnic.csv"))
fwrite(co, file.path(out, "cho_2026_asian_coethnic.csv"))
