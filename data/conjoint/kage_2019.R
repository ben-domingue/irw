##Politician-choice conjoints (Japan) from
##Kage, R., Rosenbluth, F. M., & Tanaka, S. (2019). What explains low female political
##representation? Evidence from survey experiments in Japan. Politics & Gender, 15(2), 285-309.
##https://doi.org/10.1017/S1743923X18000223
##Replication data: Harvard Dataverse doi:10.7910/DVN/9ZOYJN, CC0 1.0, no restricted files.
##File read: dataset1.csv (Dataverse "original format" of dataset1.tab). Also read as text:
##Replications.R (authors' cjoint code, level orders, constraint list) and the accepted manuscript
##(White Rose eprint 137075) for design and wording.
##Usage: Rscript kage_2019.R <raw dir> <output dir>
##
##Survey 1: 1,611 Japanese adults (Research Now opt-in online panel, sample tailored to census
##demographics; wave 2 of a two-wave survey, January-March 2015). Two conjoint scenarios, each
##3 pairs of hypothetical politicians, shown in the same order to everyone (module 1 first;
##sequence_id 1-6 then 7-12). Different attribute sets, so TWO TABLES:
##  kage_2019_elect_politician (module 1, "Electing a Politician"): 9 attributes gender, party
##    (LDP/DPJ/JCP/Komei/Restoration), consumption tax (Increase/Postponement/Decrease), policy
##    priority (Deregulation/"SMEs and Local"/Welfare), age, prior experience (None/City council/
##    Prefecture council), education, children, marital status. Choice: which of the two
##    candidates "you would personally prefer" to see elected to the House of Representatives
##    (instructions quoted in the manuscript, fn. 7).
##  kage_2019_promote_politician (module 2, "Promoting a Politician"): 6 attributes gender, age,
##    experience (Elected 5 times / Elected 5 times in a row / Elected 6 times in a row),
##    education, children, marital status. Choice: which of the two politicians the respondent
##    would personally prefer to see promoted as LDP leader (manuscript, paraphrase).
##Levels are the authors' English labels in the data (respondents saw Japanese; Tables B-C of
##the online appendix were not read). Forced choice, no opt-out: every pair has exactly one
##chosen profile. rating = the source's `evaluation`, 1-7, asked of each profile; the question
##and its anchors are not in the manuscript or the deposit (chosen profiles average 4.6, others
##3.4-3.8, so higher is more favourable; stored raw).
##Attribute order was randomized "in a given comparison" (manuscript), i.e. per task, but not
##recorded. Randomization: the authors' cjoint design has an empty constraint list and the
##manuscript speaks of independent randomization (restrictions none).
##task = contest_no (1-3), profile = candidate_id (1-2), both recorded.
##Covariates (text as stored; blanks -> NA): cov_age_group, cov_gender (Female/Male -> female/
##male), cov_marital, cov_education, cov_employment, cov_party_id (party_affiliat; "No
##affiliation" kept as text), cov_survey_weight (weight_uncapped; the authors weight their AMCEs
##with it).
##N: 1,611 respondents and 9,666 rows per scenario, as in the manuscript. Spot check below:
##weighted OLS of chosen on gender in module 1 gives the female effect the manuscript reports
##(+0.04).
##Not built from this deposit: Survey 2 (dataset2; 202 respondents each rate one memo, author
##gender x nationality; how the author was shown is undocumented), Study 3 (candidate survey
##with candidates' names) and Study 4 (single-factor encouragement experiment).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "dataset1.csv"), na.strings = "")
stopifnot(s[, .N, .(resid, module, contest_no)][, all(N == 2)], s[, sum(chosen), .(resid, module, contest_no)][, all(V1 == 1)],
          all(s$evaluation %in% 1:7), uniqueN(s$resid) == 1611, all(s$gender %in% c("Female", "Male")))
cov <- function(x) x[, .(cov_age_group = age, cov_gender = tolower(gender), cov_marital = marital, cov_education = education,
                         cov_employment = employment, cov_party_id = party_affiliat, cov_survey_weight = weight_uncapped)]
build <- function(m, attrs, name) {
  x <- s[module == m]
  d <- x[, .(id = as.integer(resid), task = as.integer(contest_no), profile = as.integer(candidate_id),
             choice = as.integer(chosen), rating = as.integer(evaluation))]
  for (k in names(attrs)) d[, paste0("attr_", k) := x[[attrs[[k]]]]]
  stopifnot(!anyNA(d))
  d <- cbind(d, cov(x))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
  d
}
d1 <- build(1, c(gender = "m1_gender", party = "m1_party", consumption_tax = "m1_consumption", policy_priority = "m1_manifesto",
                 age = "m1_age", experience = "m1_exper", education = "m1_edu", children = "m1_child", marital_status = "m1_marital"),
            "kage_2019_elect_politician")
d2 <- build(2, c(gender = "m2_gender", age = "m2_age", experience = "m2_exper", education = "m2_edu", children = "m2_child",
                 marital_status = "m2_marital"), "kage_2019_promote_politician")
message("female effect, module 1: ", round(coef(lm(choice ~ I(attr_gender == "Female"), d1, weights = cov_survey_weight))[2], 3))
