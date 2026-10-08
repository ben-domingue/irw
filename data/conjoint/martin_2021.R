##Corruption-severity conjoint from
##Martin, L. (2021). All sins are not created equal: The factors that drive perceptions
##of corruption severity. Journal of Experimental Political Science, 8(1), 15-25.
##https://doi.org/10.1017/xps.2019.33 (online 2019)
##Replication data: Harvard Dataverse doi:10.7910/DVN/ID1KJG, CC0 1.0. File read:
##profile_level_clean.dta (Dataverse "original format" download; built by the author's
##JEPS_Replication.do from the raw survey, which was read as text but not run). Wording
##from Martin_JEPS_Protocols.pdf and Readme.txt in the deposit.
##Usage: Rscript martin_2021.R <dir holding profile_level_clean.dta> <output dir>
##
##martin_2021_corruption: 778 market vendors, boda-boda (motorcycle taxi) drivers and
##  shopkeepers interviewed face to face in 18 towns in Uganda (in Lusoga or Luganda), 4
##  pairs of hypothetical officials accused of embezzlement, 5 attributes, shown as picture
##  icons that the enumerator placed and explained. attr_* hold the icon captions as
##  printed in the protocol figure: role ("Elected", "Appointed"), level ("Central
##  Government", "Local Government"), source of the funds ("Donor Funds", "Citizens' Taxes",
##  "Transfers from Central Gov't"), use of the stolen money ("Himself", "Help Kin /
##  village", "Buy election support for his party"; the author's labels are "On Himself",
##  "Patronage", "Clientelism"), and intended purpose of the funds ("Water", "Health
##  Care", "Government Salaries", "Roads / Infrastructure", "Education"). Levels were drawn
##  independently with equal probability; attribute order was fixed.
##  Outcomes: choice = chosen, "Which of these two officials would you personally rather
##  see prosecuted and punished for what they have done?" (forced; respondents had to pick
##  one, no opt-out). rating = rank, "on a scale of 1 to 5, how serious was the corruption
##  that Official 1/2 is accused of?" 1 = not at all serious ... 5 = extremely serious.
##  Direction: higher = MORE SEVERE corruption (i.e. less favourable to the official);
##  kept as in the source, not reversed. task = profile (pair 1-4), profile = profileab
##  (1 = first official).
##  Covariates: cov_age (years, "What is your age?"), cov_gender (male/female, from `male`,
##  .dta variable label "1 if male, 0 if female"), cov_urban (1 = lives in a town,
##  0 = village), cov_education_years (0-14; 14 = trade school or any post-secondary),
##  cov_occupation (1 market vendor, 2 boda-boda driver, 3 shopkeeper/small vendor),
##  cov_steal_upset (1-5, how upset at rumours a local official is corrupt), and four 1-4
##  likelihoods of acting on such rumours (cov_goprotest, cov_contact_official,
##  cov_campaign_against, cov_talkneighb; 4 = very likely).
##  Dropped: GPS coordinates, enumerator and interview identifiers, town, income and tax
##  modules, and all derived dummies. The respondent id is the author's pid
##  (enumerator-day-interview number) re-keyed to 1..778.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
p <- read_dta(file.path(raw, "profile_level_clean.dta"))
num <- function(x) as.numeric(zap_labels(x))
d <- data.table(id = match(p$pid, sort(unique(p$pid))), task = as.integer(p$profile), profile = as.integer(p$profileab),
                choice = as.integer(p$chosen), rating = as.integer(p$rank))
pick <- function(dums, labs) { m <- sapply(dums, function(v) num(p[[v]]) == 1); stopifnot(all(rowSums(m) == 1)); labs[max.col(m)] }
d[, attr_role := pick(c("elect", "appt"), c("Elected", "Appointed"))]
d[, attr_government := pick(c("central", "local"), c("Central Government", "Local Government"))]
d[, attr_funds_source := pick(c("donor", "tax", "transfer"), c("Donor Funds", "Citizens' Taxes", "Transfers from Central Gov't"))]
d[, attr_money_spent_on := pick(c("self", "kinvill", "buyel"), c("Himself", "Help Kin / village", "Buy election support for his party"))]
d[, attr_funds_purpose := pick(c("water", "health", "sal", "infra", "educ"),
                               c("Water", "Health Care", "Government Salaries", "Roads / Infrastructure", "Education"))]
d[, cov_age := num(p$age)][, cov_gender := c("female", "male")[num(p$male) + 1]][, cov_urban := num(p$urban_dum)]
d[, cov_education_years := num(p$education_years)][, cov_occupation := num(p$primaryoccupate)]
for (v in c("steal_upset", "goprotest", "contact_official", "campaign_against", "talkneighb")) d[, paste0("cov_", v) := num(p[[v]])]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "martin_2021_corruption.csv"))
