##Local nonpartisan candidate conjoint (US, CES 2022) from
##Ornstein, J. T., Heideman, A. J., Moy, B. J., & Schiff, K. J. (2024). Hometown advantage: Voter
##preferences for community embeddedness in local contests. Journal of Experimental Political
##Science, 12(3), 267-281. https://doi.org/10.1017/XPS.2024.16
##Replication data: Harvard Dataverse doi:10.7910/DVN/PPMGWL, CC0 1.0, no restricted files.
##File read: CES2022_UGA.RData (one data frame `d`, loaded into its own environment). main.R
##(read as text) shows how the authors stack it. No codebook ships; level text is as stored
##(full sentences / names), design facts from the article (doi above).
##Usage: Rscript ornstein_2024.R <dir holding the .RData> <output dir>
##
##1,308 respondents to the University of Georgia team module of the 2022 Cooperative Election
##Study (post-election wave); each chose between two candidates in five hypothetical nonpartisan
##local elections. The file has one row per contest (A_* and B_* columns; conjoint_choice 1 = A,
##2 = B) and NO task column: it holds five consecutive blocks of 1,308 rows, each with the same
##respondent order (verified), so task = block (1-5) is INFERRED from row order; profile 1 = A,
##2 = B (recorded).
##choice: the candidate chosen; forced, no opt-out (no skipped answers in the file). Question
##wording is not in the deposit or the article text (Figure 1 is an image).
##Attributes (text as stored): attr_name (122 names; candidate race and gender were not listed
##but signalled by racially distinct names from Butler & Homola; the authors' coding of each name
##is in the source A_/B_Race (B/L/W) and A_/B_Gender columns, not kept as attributes: gender goes
##to crosswalk.csv), attr_age (30/45/60), attr_career, attr_community_ties (owned/rented x 2/10
##years, one sentence), attr_political, attr_endorsement, attr_family.
##Randomization: the article says levels were drawn uniformly with no restrictions on
##combinations, but names are not uniform: each White-coded name appears ~80-110 times, each
##Black- or Latino-coded name ~15-45 times (White 65% of profiles).
##Covariates (CES codes; 8/98 = skipped, 9/99 = not asked): cov_pid3 1=Democrat 2=Republican
##3=Independent 4=Other 5=Not sure; cov_race 1=White 2=Black 3=Hispanic 4=Asian 5=Native
##American 6=Two or more 7=Other 8=Middle Eastern; cov_residency (CC22_361) 1=<1 month 2=2-6
##months 3=7-11 months 4=1-2 years 5=3-4 years 6=5+ years; cov_urbancity 1=City 2=Suburb 3=Town
##4=Rural area 5=Other; cov_gender4 1=Man 2=Woman 3=Non-binary 4=Other; cov_ownhome 1=Own 2=Rent
##3=Other; cov_survey_weight = teamweight (blank for 308 respondents).
##Dropped: CES caseid (re-keyed to integers in file order).
##N: 1,308 = the article. Spot check (authors' formula, lm clustered by respondent, name gender/
##race codings merged back): previously elected 0.070 (SE 0.009), 10-year residency 0.077,
##homeowner 0.040; the article reports these only in a figure, so not compared numerically.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "CES2022_UGA.RData"), envir = e)
s <- as.data.table(zap_labels(e$d))
n <- uniqueN(s$caseid); stopifnot(n == 1308, nrow(s) == 5 * n)
for (k in 1:4) stopifnot(identical(s$caseid[seq_len(n) + k * n], s$caseid[seq_len(n)]))
s[, `:=`(task = rep(1:5, each = n), id = match(caseid, unique(caseid)))]
stopifnot(all(s$conjoint_choice %in% 1:2))
cov <- c(cov_pid3 = "pid3", cov_race = "race", cov_residency = "CC22_361", cov_urbancity = "urbancity",
         cov_gender4 = "gender4", cov_ownhome = "ownhome")
one <- function(p, k) {
  x <- s[, .(id = as.integer(id), task = as.integer(task), profile = k, choice = as.integer(conjoint_choice == k),
             attr_name = get(paste0(p, "_Name")), attr_age = as.character(get(paste0(p, "_Age"))),
             attr_career = get(paste0(p, "_CareerHistory")), attr_community_ties = get(paste0(p, "_CommunityTies")),
             attr_political = get(paste0(p, "_Political")), attr_endorsement = get(paste0(p, "_Endorsements")),
             attr_family = get(paste0(p, "_Family")))]
  for (c in names(cov)) x[, (c) := as.integer(s[[cov[[c]]]])]
  x[, cov_survey_weight := s$teamweight]
}
d <- rbind(one("A", 1L), one("B", 2L))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ornstein_2024_hometown_advantage.csv"))
