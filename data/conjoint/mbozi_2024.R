##Visual vote-tally-sheet conjoint (Kenya and Malawi) from
##Mbozi, F. (2024). When do voters see fraud? Evaluating the effects of poll supervision on
##perceptions of integrity. Journal of Experimental Political Science.
##https://doi.org/10.1017/xps.2024.5
##Replication data: Harvard Dataverse doi:10.7910/DVN/EZS44G, CC0 1.0, no restricted files.
##File read: rep_full_df.csv (the author's long file built from AP21_Kenya.csv and
##AP21_Malawi.csv by Mbozi_Data_Cleaning_Qualtrics_to_Clean_DF.ipynb, read as text; question
##wording checked against the raw exports' header rows). Design facts from the article.
##Usage: Rscript mbozi_2024.R <raw dir> <output dir>
##
##390 respondents from Qualtrics in-house online panels (Kenya 250, Malawi 140; late March
##to mid-April 2022). Each did 3 forced-choice tasks (the source's run r1-r3); each task
##showed two IMAGES of simplified polling-station vote tally sheets, "Form A" (profile 1)
##and "Form B" (profile 2), drawn at random by Qualtrics from a pool of generated images.
##ONE TABLE, pooled with cov_country, as in the article's main analysis.
##IMAGE CONJOINT: the profiles were pictures, not text. The attributes are the six features
##the author manipulated on the image; levels are the author's coding, decoded from the
##image file names via Qualtrics_Dictionary_KY/MW.csv (notebook key: 1 = presiding officer
##present, 2 = DPP / Jubilee present, 3 = MCP / opposition present, 4 = observer (NICE /
##ELOG) present, 5 = DPP / Jubilee crossed out, 6 = MCP / opposition crossed out). Level text
##here follows the article: a signature on the form signals the person was present at the
##count; an error is a crossed-out tally with a lower number written beside it.
##  attr_presiding_officer, attr_ruling_party_agent (DPP in Malawi, Jubilee in Kenya),
##  attr_opposition_agent (MCP in Malawi, ODM in Kenya), attr_observer:
##      "Signature present" / "Signature absent"
##  attr_ruling_party_tally, attr_opposition_tally: "Crossed out and corrected" / "No correction"
##The party named on the form differs by country; the attribute names here are the roles.
##Other things differed between images and are NOT stored: the vote numbers (the author
##codes a large/small vote difference from picture numbers, a coding she corrected once in
##the notebook) and the image id. Correction images (any 5/6) and clean images come from
##separate pools, so feature combinations are not uniform (restrictions observed). 21
##tasks (42 rows) show two forms with identical features (the author's main analysis drops
##them, N = 2,298 rows); kept here.
##Outcomes:
##  choice = "Between these two vote tally sheets, click on the one that you believe has
##           more reliable information about the vote outcomes at its polling station?"
##           Forced, no opt-out.
##  rating_misconduct = "In your opinion, what is the likelihood that electoral misconduct
##           occurred at this polling station?" 1 = very unlikely .. 5 = very likely, asked
##           for each form. NOTE direction: higher = LESS favourable (kept as asked).
##  "To what extent do you agree with the following statements" (Malawi: "Looking at the
##  form, ..."), 1 = strongly disagree .. 5 = strongly agree, each form (higher = more
##  suspicion, kept as asked):
##  rating_tally_changed = "The vote tallies may have been changed in favor of a specific candidate."
##  rating_interests_unprotected = "The interests of political parties were not protected at this station"
##  rating_party_influence = "It is very possible that a political party had too much influence at this polling station."
##  rating_officer_pressure = "The presiding officer may have been put under pressure from other groups in the polling station."
##Task/profile: task = run, profile = the author's form_proper (A/B); verified one chosen
##form per task.
##Covariates: cov_country kenya/malawi (text); cov_age years; cov_gender female / male (answer
##text in rep_full_df.csv gender: Female, Male; "Prefer not to say" = missing); cov_education
##(answer text in rep_full_df.csv educ, as worded: Some secondary school, Secondary school
##completed, Post-secondary training but not at a university, Some university, University
##completed); cov_trust_emb (trust in IEBC / MEC) 1=do not trust 2=somewhat 3=a lot 4=not sure
##5=rather not say. Dropped: ethnicity, party, knowledge and role-attribution items.
##Respondent ids (row numbers per country) re-keyed to integers, Malawi first.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "rep_full_df.csv"), colClasses = list(character = "id"))
code <- function(x, lv) { i <- match(x, lv); stopifnot(all(is.na(x) | !is.na(i))); i }
s[, key := paste(country, id)]
s[, id := match(key, unique(key))]
tr <- lapply(regmatches(s$treatment, gregexpr("[0-9]", s$treatment)), as.integer)
has <- function(k) vapply(tr, function(x) k %in% x, logical(1))
sig <- function(k) fifelse(has(k), "Signature present", "Signature absent")
cor <- function(k) fifelse(has(k), "Crossed out and corrected", "No correction")
d <- data.table(id = s$id, task = as.integer(sub("r", "", s$run)), profile = code(s$form_proper, c("A", "B")),
                choice = as.integer(s$chosen), rating_misconduct = as.integer(s$lik_fraud),
                rating_tally_changed = as.integer(s$tally_chg2), rating_interests_unprotected = as.integer(s$unprt_int2),
                rating_party_influence = as.integer(s$p_excess2), rating_officer_pressure = as.integer(s$po_prs2),
                attr_presiding_officer = sig(1), attr_ruling_party_agent = sig(2), attr_opposition_agent = sig(3),
                attr_observer = sig(4), attr_ruling_party_tally = cor(5), attr_opposition_tally = cor(6),
                cov_country = s$country, cov_age = as.integer(s$age),
                cov_gender = c("female", "male", NA)[code(s$gender, c("Female", "Male", "Prefer not to say"))],
                cov_education = c("Some secondary school", "Secondary school completed", "Post-secondary training but not at a university",
                                  "Some university", "University completed")[code(s$educ, c("Some secondary school", "Secondary school completed",
                                               "Post-secondary training but not at a university", "Some university", "University completed"))],
                cov_trust_emb = code(s$trust_EMB, c("I do not trust them", "I somewhat trust them", "I trust them a lot", "Not sure", "Rather not say")))
stopifnot(!anyDuplicated(d[, .(id, task, profile)]), d[, sum(choice), .(id, task)][, all(V1 == 1)],
          uniqueN(d$id) == 390, nrow(d) == 2340,
          all(unlist(d[, .(rating_misconduct, rating_tally_changed, rating_interests_unprotected, rating_party_influence, rating_officer_pressure)]) %in% 1:5))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mbozi_2024_tally_sheets.csv"))
