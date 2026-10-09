##Fully factorial "James" vignette (US, MTurk) from
##Ahler, D. J., & Sood, G. (2022). Typecast: A routine mental shortcut causes party
##stereotyping. Political Behavior. https://doi.org/10.1007/s11109-022-09780-8
##Replication data: Harvard Dataverse doi:10.7910/DVN/KBX2SL, CC0 1.0, no restricted files.
##File read: james_ff_clean.csv (Dataverse "original format" of james_ff_clean.tab). Also read
##as text: readme.md, 03_james_full_factorial_fig_3_si_3.R (authors' coding of the outcome and
##conditions) and the authors' manuscript (gsood.com/research/papers/typecast.pdf, 13 Jan 2022;
##section 2.2: vignette wording, sample, filter).
##Usage: Rscript ahler_2022.R <raw dir> <output dir>
##
##MTurk, August 2018, 1,991 respondents (2,000 rows; 9 rows have no condition and no answer and
##are dropped). One vignette per respondent (task = 1, profile = 1), four factors "randomly and
##independently" assigned (manuscript), as text inserted into:
##  "James is a 37-year-old (white | Black) man. He attended the University of Michigan, where he
##  double-majored in economics and political science and was president of a business and
##  marketing club. He also participated in (anti-tax demonstrations | living-wage demonstrations |
##  student government). James's co-workers describe him as highly driven, outspoken, and
##  confident. He is married to (Karen | Keith), whom he met in college, and they have one son.
##  In James's free time, he (...)."
##attr_race / attr_spouse / attr_activity / attr_demonstrations = the source's cf_race,
##cf_spouse, cf_relig, cf_policy: the inserted text as stored (race stored lower case "black"/
##"white"; the secular scouting text reads "...organized through the Secular Families
##Foundation" in the data, where the manuscript quotes an earlier wording).
##Outcome: rating = the source's james_cf, the answer to "Which of the following is most
##likely?" 1 = "James works in sales", 2 = "James works in sales and is an active supporter of
##the Democratic Party", 3 = "James works in sales and is an active supporter of the Republican
##Party" (codes per the authors' script: 2 = Democratic conjunction fallacy, 3 = Republican).
##NOMINAL codes, not an ordered scale; stored raw. The deposit's james_gpa (beliefs about James's
##GPA, 5 codes) has no labels and is left out.
##The authors analyse the 1,507 respondents that pass their pre-treatment filter (foreign or
##blacklisted IPs, duplicates, insincere respondents; Ahler, Roush & Sood): cov_untrustworthy
##(1 = filtered out by the authors, 0 = kept); the IP-derived flags themselves are dropped.
##Covariates: cov_party_id (authors' pid3 text: democrat/independent/republican; blank -> NA),
##cov_ideo3 (authors' ideo3 text), cov_party_id7_code, cov_gender_code, cov_age_group_code,
##cov_education_code, cov_state_code (codes; no labels deposited). Dropped: free text (other-party
##text, comments), race (multi-select codes), knowledge items, the other studies' variables
##(Kara, pcomp/visual conditions), the IP/VPN/duplicate flags.
##N: 1,991 respondents, 1,507 after the authors' filter, both as in the manuscript. Spot check
##below: among kept respondents, a Black James raises the raw Democratic conjunction-fallacy rate
##by 11.3 points and lowers the Republican one by 12.6 (authors' ordered-logit effects, SI table
##3.2: +15.0 and -9.7; same direction and size, the ordered logit constrains the two).
##No respondent id in the deposit: id = row number.
##Not built: the Linda and maximal-contrast James studies, the base-rate ("Bayesian cues"),
##timing and avatar experiments (single manipulated factor each).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "james_ff_clean.csv"), na.strings = c("", "NA"))
s[, id := .I]
s <- s[!is.na(james_cf)]
stopifnot(nrow(s) == 1991, !anyNA(s[, .(cf_race, cf_spouse, cf_relig, cf_policy)]), all(s$james_cf %in% 1:3))
d <- s[, .(id, task = 1L, profile = 1L, rating = as.integer(james_cf), attr_race = cf_race, attr_spouse = cf_spouse,
           attr_activity = cf_relig, attr_demonstrations = cf_policy,
           cov_party_id = pid3, cov_ideo3 = ideo3, cov_party_id7_code = as.integer(pid7), cov_gender_code = as.integer(gender),
           cov_age_group_code = as.integer(age), cov_education_code = as.integer(education), cov_state_code = as.integer(state),
           cov_untrustworthy = as.integer(untrustworthy))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ahler_2022_james_vignette.csv"))
k <- d[cov_untrustworthy == 0]
message("kept: ", nrow(k), "; Dem-CF rate Black - white: ",
        round(k[attr_race == "black", mean(rating == 2)] - k[attr_race == "white", mean(rating == 2)], 3))
