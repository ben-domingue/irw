##Candidate-sex conjoint (US, president and House) from
##Ono, Y., & Burden, B. C. (2019). The contingent effects of candidate sex on voter choice.
##Political Behavior, 41(3), 583-607. https://doi.org/10.1007/s11109-018-9464-6
##Replication data: Harvard Dataverse doi:10.7910/DVN/IZKZET, CC0 1.0, no restricted files.
##File read: POBE_R_data.csv (the full data; the other POBE_R_data_*.csv files are subsets of
##it for the authors' figures). Read as text, not run: R code for Figure 2_stage1.txt and other
##figure scripts. Design and wording: the authors' APSA 2017 working paper (Ono and Burden,
##https://www.bu.edu/polisci/files/2017/09/Ono-and-Burden.pdf), Table 1, Figure 1, appendix.
##Usage: Rscript ono_2019.R <dir holding POBE_R_data.csv> <output dir>
##
##1,583 US voting-eligible adults (SSI online panel, March 2016, quotas on region, sex, race,
##age), 10 tasks of 2 hypothetical candidates, 13 attributes. Five tasks were for President
##and five for the U.S. House: trial_office. The paper says the order of the two blocks was
##randomized across respondents, but in the file tasks 1-5 are President and 6-10 Congress for
##EVERY respondent, so `task` is the authors' numbering, not the display order (for about half
##the respondents the Congress block came first); the order within a block is not documented.
##Outcome: choice = selected. Congress wording (working paper Figure 1): "If you had to choose
##between them, which of these candidates would you vote to be a member of the U.S. House of
##Representatives?" (Candidate 1 / Candidate 2). The presidential wording is not shown in any
##source; presumably parallel. Forced choice, no opt-out (exactly one chosen in every task).
##Attribute text: the file stores short levels; the four issue positions are replaced by the
##displayed text of Table 1 / Figure 1 (e.g. "Cut military budget" -> "Wants to cut military
##budget and keep the U.S. out of war"); the rest is as stored (Figure 1 shows age as "52";
##the file's "52 years old" is kept). Attribute order was randomized per respondent (fixed
##across the 10 tasks) and is not recorded. All attributes randomized independently and
##uniformly (working paper p. 11, "complete randomization of all attributes").
##Dropped: the authors' derived pair flags (Party competition, Sex competition, Implausible
##pair) and R_Agegroup (derived from age); R_Ideology (7-point code, direction not
##documented). Covariates: cov_sex, cov_age, cov_region, cov_race, cov_partisanship,
##cov_hillary (feeling about Hillary Clinton: Like/Neutral/Dislike), cov_ba_degree (R_Education
##2 = BA degree, 1 = no BA; counts match appendix Table A1, 888/666), cov_class (R_Class
##1 lower, 2 middle, 3 upper; Table A1 counts match), cov_political_interest (R_Interest 1 =
##not at all .. 4 = very interested, appendix section 5).
##Spot check: lm(choice ~ all attributes), SEs clustered by id, gives the female AMCE -1.3
##points the paper reports.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "POBE_R_data.csv"), check.names = FALSE)
stopifnot(uniqueN(s$respondentIndex) == 1583, s[, .N, respondentIndex][, all(N == 20)],
          s[, sum(selected), .(respondentIndex, task)][, all(V1 == 1)])
rc <- function(x, map) { y <- unname(map[x]); stopifnot(!anyNA(y)); y }
d <- s[, .(id = as.integer(respondentIndex), task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected),
           attr_sex = Sex, attr_age = Age, attr_family = Family, attr_race = Race,
           attr_experience = `Experience in public office`, attr_characteristic = `Salient personal characteristics`,
           attr_party = `Party affiliation`, attr_expertise = `Policy area of expertise`,
           attr_national_security = rc(`Position on national security`, c(
             "Cut military budget" = "Wants to cut military budget and keep the U.S. out of war",
             "Maintain strong defense" = "Wants to maintain strong defense and increase U.S. influence")),
           attr_immigrants = rc(`Position on immigrants`, c(
             "Favors giving guest worker status" = "Favors giving citizenship or guest worker status to undocumented immigrants",
             "Opposes giving guest worker status" = "Opposes giving citizenship or guest worker status to undocumented immigrants")),
           attr_abortion = rc(`Position on abortion`, c(
             "Pro-choice" = "Abortion is a private matter (pro-choice)",
             "Pro-life" = "Abortion is not a private matter (pro-life)",
             "No opinion (neutral)" = "No opinion (neutral)")),
           attr_deficit = rc(`Position on government deficit`, c(
             "Reduce deficit through tax increase" = "Wants to reduce the deficit through tax increase",
             "Reduce deficit through spending cuts" = "Wants to reduce the deficit through spending cuts",
             "Don't reduce deficit now" = "Does not want to reduce the deficit now")),
           attr_favorability = `Favorability rating among the public`,
           trial_office = Office,
           cov_sex = R_Sex, cov_age = as.integer(R_Age), cov_region = R_Region, cov_race = R_Race,
           cov_partisanship = R_Partisanship, cov_hillary = R_Hillary,
           cov_ba_degree = as.integer(R_Education == 2), cov_class = as.integer(R_Class),
           cov_political_interest = as.integer(R_Interest))]
stopifnot(d[, uniqueN(trial_office), .(id, task)][, all(V1 == 1)], d[, uniqueN(cov_age), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ono_2019_candidate_sex.csv"))
