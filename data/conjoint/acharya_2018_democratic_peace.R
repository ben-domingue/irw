##Democratic-peace vignette experiment (replication and extension of Tomz & Weeks 2013) from
##Acharya, A., Blackwell, M., & Sen, M. (2018). Analyzing causal mechanisms in survey experiments.
##Political Analysis, 26(4), 357-378. https://doi.org/10.1017/pan.2018.19 (Study #2)
##Replication data: Harvard Dataverse doi:10.7910/DVN/KHE44F, CC0 1.0, no restricted files, no terms.
##File read: tw-replication-dvn.tab (datafile 3123594, ?format=original = tw-replication-dvn.csv,
##Latin-1). tw-replication-dvn.R read as text, not run. Survey instrument: the article's online
##supplement (conjoint-supp.pdf, Appendix C "Democratic Peace Survey Instrument"). The deposit's
##other experiment is acharya_2018_scotus_nominees (acharya_2018.R).
##Usage: Rscript acharya_2018_democratic_peace.R <dir holding tw-replication-dvn.csv> <output dir>
##
##1,247 US adult MTurk workers via Qualtrics, 9 June 2016 (article p. 373). Each read ONE text
##vignette (task = 1, profile = 1): "A country is developing nuclear weapons and will have its first
##nuclear bomb within six months. ..." with four randomized bullets, each binary with probability
##0.5, independently (supplement: "For each binary choice in the treatment condition, each
##respondent was randomly assigned to either condition with probability 0.5"):
##  attr_alliance   "This country has / does not have a military alliance with the United States."
##  attr_democracy  "This country is a democracy and shows every sign that it will remain a democracy"
##                  / "... is not a democracy and shows no sign of becoming a democracy"
##  attr_trade      "This country has / does not have high level of trade with the United States."
##  attr_motives    "The country's motives remain unclear, but if it builds nuclear weapons, it will
##                  have the power to blackmail or destroy other countries" (Tomz-Weeks original) /
##                  "The country has stated that it is seeking nuclear weapons to aid in a conflict
##                  with another country in the region" (the authors' manipulated-mediator arm).
##Level text = the instrument's bullet with the deposit's *_text fragment inserted (the fragments
##are what the data store: "has"/"does not have", the democracy clause, the motives sentence; the
##motives sentence's mangled apostrophe is restored). Fixed bullets (nonnuclear forces half as
##strong as the US; refused all requests to stop) are not stored. Attribute order fixed (instrument).
##Outcome: rating = favor_attack, "Would you favor or oppose using the U.S. military to attack the
##country's nuclear development sites?" 1 Favor strongly, 2 Favor somewhat, 3 Neither favor nor
##oppose, 4 Oppose somewhat, 5 Oppose strongly (instrument option order; the authors' code counts
##1-2 as favor). Stored raw: HIGHER = MORE OPPOSED to the strike. One respondent with no answer
##omitted.
##Covariates: cov_age (Q2, years, after the age screen Q1). The deposit has no value labels; the
##instrument lists the answer options but the codes are not documented (employment codes run 1-10
##with gaps), so these keep their codes with a _code suffix: cov_gender_code (female, 1/2;
##instrument order Male, Female), cov_race_code, cov_employed_code, cov_education_code (educ),
##cov_follow_gov_code, cov_dem_place_code, cov_rep_place_code (ideological placement of the two
##parties, 1-7), cov_pid_code (pid_a: Republican, Democrat, Independent, Something else),
##cov_pid_strong_dem_code, cov_pid_strong_rep_code, cov_pid_lean_code. Dropped: dates, Status,
##Finished, the age screen, Q18_1-18 (an unlabelled 18-box check-all item, presumably the attention
##check; its pass rule is not documented). No survey weight.
##N: 1,247 in the article and file; 1,246 here (one blank outcome). Spot check (favor = 1-2, OLS):
##effect of democracy in the original-motives arm -0.056 and in the stated-threat arm -0.159, i.e.
##the ACDE "more than double in magnitude" the ATE, as the article reports (p. 373-374).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "tw-replication-dvn.csv"), encoding = "Latin-1")
stopifnot(nrow(s) == 1247, all(s$mil_text %in% c("has", "does not have")), all(s$trade_text %in% c("has", "does not have")))
stopifnot(all((s$mil_text == "has") == (s$mil_dummy == 1)), all((s$trade_text == "has") == (s$trade_dummy == 1)))
stopifnot(all(grepl("^is (not )?a democracy", s$dem_text)), all((s$dem_text == "is a democracy and shows every sign that it will remain a democracy") == (s$dem_dummy == 1)))
th <- fifelse(s$threat_dummy == 1,
  "The country has stated that it is seeking nuclear weapons to aid in a conflict with another country in the region",
  "The country’s motives remain unclear, but if it builds nuclear weapons, it will have the power to blackmail or destroy other countries")
stopifnot(all(substr(s$threat_text, 1, 11) == substr(th, 1, 11)), all(substr(s$threat_text, nchar(s$threat_text) - 30, nchar(s$threat_text)) == substr(th, nchar(th) - 30, nchar(th))))
d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L, rating = as.integer(s$favor_attack),
                attr_alliance = paste0("This country ", s$mil_text, " a military alliance with the United States."),
                attr_democracy = paste0("This country ", s$dem_text),
                attr_trade = paste0("This country ", s$trade_text, " high level of trade with the United States."),
                attr_motives = th,
                cov_age = as.integer(s$Q2), cov_gender_code = as.integer(s$female), cov_race_code = as.integer(s$race),
                cov_employed_code = as.integer(s$employed), cov_education_code = as.integer(s$educ),
                cov_follow_gov_code = as.integer(s$follow_gov), cov_dem_place_code = as.integer(s$dem_place),
                cov_rep_place_code = as.integer(s$rep_place), cov_pid_code = as.integer(s$pid_a),
                cov_pid_strong_dem_code = as.integer(s$pid_d_strong), cov_pid_strong_rep_code = as.integer(s$pid_r_strong),
                cov_pid_lean_code = as.integer(s$pid_lean))
d <- d[!is.na(rating)]
stopifnot(all(d$rating %in% 1:5), nrow(d) == 1246)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "acharya_2018_democratic_peace.csv"))
