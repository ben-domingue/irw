##Candidate group-appeal conjoints in Britain and Norway from
##Finseraas, H., Heath, O., Langsæther, P. E., & Smets, K. (2026). How group appeals shape
##group-party linkages in two political systems. The Journal of Politics, 88(3), 1264-1269.
##https://doi.org/10.1086/735505
##Replication data: Harvard Dataverse doi:10.7910/DVN/EKM4B3, CC0 1.0. Files read: Data_Britain.tab
##and Data_Norway.tab (Dataverse "original format" .dta downloads). Attribute text from the
##online appendix in the deposit (group_appeals_dataverse.pdf, Tables A1 and A2); variable meanings
##from codebook.pdf. No code from the deposit was run.
##Usage: Rscript finseraas_2026.R <dir holding Data_Britain.dta and Data_Norway.dta> <output dir>
##
##Two tables, one per country: the attribute sets differ (Britain has a climate-vs-growth and an EU
##attribute, Norway a carbon-tax and an abortion attribute) and the paper analyses each country
##separately. Each respondent saw 2 tasks of 2 fictional candidates, 9 attributes, all levels
##fully randomized with equal probability (appendix); attribute order fixed (no attrpos_).
##  finseraas_2026_group_appeals_britain: YouGov UK Omnibus, May 2023, 2,001 respondents (as in
##    the paper).
##  finseraas_2026_group_appeals_norway: Kantar online panel, Jan-Feb 2022, 3,190 respondents in
##    the deposit; 19 answered no conjoint question and drop out, leaving 3,171 (3,137 made at
##    least one choice; 34 gave only ratings). The paper reports 2,931 analysed; the gap is not
##    explained in the deposit (not fixed here). Norwegian
##    respondents saw Norwegian text; attr_* hold the authors' English translation (Table A2).
##Attributes (text from Tables A1/A2; policy levels follow "Candidate wants to...", group appeals
##follow "Candidate states that..."): age (30 / 60), gender (Woman / Man), born and raised in (Big
##city / Countryside), economic left-right, immigration (asylum easier/harder), climate (Britain:
##combat climate change vs. growth; Norway: increase/reduce the carbon tax), Britain: EU
##cooperation vs. independence; Norway: abortion (expand to week 18 / keep at week 12; the appendix
##table says 18 while its text speaks of a 12-vs-16 debate), and group appeal (5 statements,
##mapped from class_appeal_full: Turnout = neutral statement, Attention and Powerful = the two
##conflict statements, Interests and Common = the two solidarity statements).
##OCCUPATION IS COLLAPSED in the deposit: respondents saw one of 6 job titles (Britain: factory
##worker, bus driver, care worker, lawyer, journalist, banker; Norway: factory worker, electrician,
##nurse, professor, engineer, CEO) but the data keep only working vs. middle class. attr_occupation
##holds the class with the three possible titles, e.g. "Working class (Factory worker, bus driver
##or care worker)"; the title actually shown is not recoverable.
##Outcomes (same tasks):
##  choice = selected: which of the two candidates they would prefer if they had to vote for one
##    of them. Forced, no opt-out. Norway: 228 of 6,380 tasks have no choice (choice NA, rows kept
##    when a rating is present).
##  rating_represent = represented: to what extent the candidate would represent "someone like
##    you", 1 (not at all) to 7 (to a very great extent); higher = more represented.
##  rating_leftright = rightrating: placement of the candidate from 1 (far left) to 7 (far right).
##    Checked 2026-10-07: codebook.pdf labels rightrating "Profile: Left-right rating" for Norway
##    and "Profile: Rating" for Britain, but the authors' code.do runs the same left-right
##    regressions on rightrating in both countries and combines them in one figure. Norway's
##    separately labelled `rating` (1 = Helt til venstre ... 7 = Helt til hoyre, 9996 = NA) equals
##    rightrating in all 12,437 non-missing cases, so it is a labelled duplicate and is not kept.
##    Not a favourability scale: higher = further right.
##Covariates: cov_male, cov_working_class (Britain: class identity; Norway: EGP class from
##occupation, many missing), cov_vote_conservative (Britain: votes Conservative vs Labour; Norway:
##votes Høyre), cov_age_scaled (Britain only: age rescaled 0-1 by the authors), cov_voted (Britain:
##turnout), cov_university (Norway), cov_leftright_scaled (Norway: self-placement rescaled 0-1).
##Dropped: the authors' dummies (appeal and level dummies, the X-interaction terms), older,
##id_round. RespondentSerial is a survey serial (kept as id).
##Spot check: the authors' Britain working-class choice AMCEs (jop_log.log, n = 4,156 rows,
##e.g. restrict immigration .1105, conflict appeal .0412) reproduce exactly from this table.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
appeal <- c("It is important that everyone votes on election day!",
            "Too much attention has been given to the upper middle class in recent political debates, it is time for politicians to prioritize people from the working class",
            "The rich are getting more powerful while working class voices are not being heard, now it's the workers' turn!",
            "All working class people have shared interests and need to unite in politics!",
            "All working class people need to turn out to vote to improve their common situation!")
lab <- function(x) as.character(as_factor(x))
common <- function(k, jobs) {
  stopifnot(identical(unname(attr(k$class_appeal_full, "labels")), 0:4 + 0),
            identical(names(attr(k$class_appeal_full, "labels")), c("Turnout appeal", "Attention", "Powerful", "Interests", "Common")))
  d <- data.table(id = as.integer(k$RespondentSerial), task = as.integer(k$round), profile = NA_integer_,
                  choice = as.integer(k$selected), rating_represent = as.integer(zap_labels(k$represented)),
                  rating_leftright = as.integer(zap_labels(k$rightrating)),
                  attr_age = lab(k$age_candidate), attr_gender = c(Female = "Woman", Male = "Man")[lab(k$gender_candidate)],
                  attr_occupation = c("Working class" = paste0("Working class (", jobs[1], ")"),
                                      "Middle class" = paste0("Middle class (", jobs[2], ")"))[lab(k$class_candidate)],
                  attr_born_raised = c(Urban = "Big city", Rural = "Countryside")[lab(k$rural_candidate)],
                  attr_economic = c("Expand welfare state" = "expand the welfare state, even if it means increasing taxes",
                                    "Reduce taxes" = "reduce taxes, even if means making welfare cuts to reduce taxes")[lab(k$policy_welfare)])
  d[, attr_group_appeal := appeal[as.integer(zap_labels(k$class_appeal_full)) + 1L]]
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
  d
}
## Britain
b <- read_dta(file.path(raw, "Data_Britain.dta"))
db <- common(b, c("Factory worker, bus driver or care worker", "Lawyer, journalist or banker"))
db[, profile := as.integer(b$pair)]
db[, attr_immigration := c("Liberal immigration" = "make it easier for people to get asylum in Britain",
                           "Restrict immigration" = "make it harder for people to get asylum in Britain")[lab(b$policy_immigration)]]
db[, attr_climate := c("Prioritize climate" = "combat climate change, even if it causes slower economic growth",
                       "Prioritize growth" = "increase economic growth, even if causes climate change")[lab(b$policy_environment)]]
db[, attr_eu := c("EU cooperation" = "ensure closer cooperation with EU",
                  "EU independence" = "ensure greater independence from the EU")[lab(b$policy_eu)]]
db[, `:=`(cov_male = as.integer(b$male), cov_working_class = as.integer(zap_labels(b$workingclass)),
          cov_vote_conservative = as.integer(b$vote_consvlab), cov_voted = as.integer(b$voted), cov_age_scaled = round(as.numeric(b$aged), 4))]
stopifnot(!anyNA(db[, .(attr_immigration, attr_climate, attr_eu, choice)]), db[, sum(choice), .(id, task)][, all(V1 == 1)],
          uniqueN(db$id) == 2001, db[, .N, .(id, task, profile)][, all(N == 1)])
setorder(db, id, task, profile)
fwrite(db, file.path(out, "finseraas_2026_group_appeals_britain.csv"))
## Norway
n <- read_dta(file.path(raw, "Data_Norway.dta"))
dn <- common(n, c("Factory worker, electrician or nurse", "Professor, engineer or CEO"))
dn[, profile := as.integer(n$profile)]
dn[, attr_immigration := c("Liberal immigration" = "make it easier for people to get asylum in Norway",
                           "Restrict immigration" = "make it harder for people to get asylum in Norway")[lab(n$policy_immigration)]]
dn[, attr_climate := c("Increase CO2 tax" = "increase the carbon tax", "Decrease CO2 tax" = "reduce the carbon tax")[lab(n$policy_environment)]]
dn[, attr_abortion := c("More liberal abortion" = "expand the right to abortion to week 18",
                        "No change in abortion" = "keep the right to abortion at week 12")[lab(n$policy_abort)]]
wc <- lab(n$workingclass)
dn[, `:=`(cov_male = as.integer(n$male), cov_working_class = as.integer(c("working class" = 1L, "middle class" = 0L)[wc]),
          cov_vote_conservative = as.integer(n$hvoter), cov_university = as.integer(zap_labels(n$uniedu)),
          cov_leftright_scaled = round(as.numeric(n$rightscale), 4))]
stopifnot(!anyNA(dn[, .(attr_immigration, attr_climate, attr_abortion)]), dn[, .N, .(id, task, profile)][, all(N == 1)])
dn <- dn[!(is.na(choice) & is.na(rating_represent) & is.na(rating_leftright))]
stopifnot(dn[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(dn$id) == 3171)
setorder(dn, id, task, profile)
fwrite(dn, file.path(out, "finseraas_2026_group_appeals_norway.csv"))
