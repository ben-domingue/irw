##Court-curbing candidate conjoint (US, MTurk) from
##Driscoll, A., & Nelson, M. J. (2023). The costs of court curbing: Evidence from the
##United States. The Journal of Politics, 85(2), 609-624. https://doi.org/10.1086/723021
##Replication data: Harvard Dataverse doi:10.7910/DVN/JGST70, CC0 1.0. Files read:
##Study2.csv (the conjoint, "Study 2"); Study2Codebook.rtf and Study2.R read as text for
##the codes. Study 1 (Study1YouGov.dta) is a one-factor vignette (curb/defend/control) and
##is not a conjoint: not built.
##Usage: Rscript driscoll_2023.R <dir holding Study2.csv> <output dir>
##
##962 MTurk respondents (November 2019; the article says "a survey of 1,000 respondents"),
##15 pairs of hypothetical candidates each. task = source `trial`, profile = `c_number`
##(both recorded). Trials 1-10 were general-election pairs (one Democrat, one Republican);
##trials 11-15 were primary-election pairs in which both candidates shared the respondent's
##party (independents got Democrats) -> trial_election = general / primary.
##Attributes (all binary): party, and positions on college tuition, tariffs on China,
##background checks for guns, LGBT discrimination protection and court curbing. The
##displayed wording is in the article's Appendix B, which is NOT in the deposit; the level
##text stored here is the authors' factor labels from Study2.R (code 1 = the "Gov't
##Should ..." / "Supports ..." / Democratic label, 2 = the other). The court-curbing
##proposal changed with the trial (Study2.R: trials 1,6,11 judicial review; 2,7,12 electing
##justices; 3,8,13 term limits; 4,9,14 expanding the Court; 5,10,15 jurisdiction stripping),
##so attr_court holds the authors' proposal-specific label and trial_court_proposal names
##the proposal. RESTRICTION: the two candidates in a pair always took opposite positions on
##every issue and on court curbing, and opposite parties in general-election trials (the
##article says so; verified in the data below).
##DROPPED: candidate name (`c_name`, 12 numeric codes with no labels anywhere in the
##deposit; the same code appears on both profiles in 8.6% of pairs), the Qualtrics
##responseId (a platform ID), rowNo, and `legit` (the authors' factor score of the
##legitimacy battery, a derived scale).
##Outcomes (exact wording not in the deposit):
##  choice = c_choose, which of the two candidates the respondent would be more likely to
##    support (article). 1 = chosen. No opt-out is described; 2,430 of 14,430 tasks have
##    no answer (choice blank on both profiles; their ratings are kept). 5 tasks with no
##    answer to any outcome are omitted: 14,425 tasks, 28,850 rows.
##Check: choice ~ attributes by OLS, SEs clustered by id, on the authors' complete-case
##rows: court-curbing AMCE -0.066 in primary trials (article fig. 4: "a 6% reduction");
##copartisan profiles chosen 62% vs 38% (article: 61.75% vs 38.27%).
##  rating = c_rate, "Candidate Rating Outcome" (codebook), 5 points, stored as recoded by
##    Study2.R (raw 4->1, 3->2, 5->3, 2->4, 1->5; higher = more favourable per the authors).
##    Caution: the share of profiles chosen is not monotone in this recode (3 = raw 5 is
##    chosen 33%, 2 = raw 3 is chosen 48%), so the raw midpoint code may not mean what the
##    recode assumes. 86 rows blank.
##  rating_mobilize = c_mobil, "Mobilization Outcome", same 5-point recode; 53 rows blank.
##Covariates: cov_pid (7-point party ID, 1 = strong Democrat to 7 = strong Republican,
##per Study2.R's 1:3 = Democrat, 5:7 = Republican), cov_ideology (7-point, 1 = liberal,
##per Study2.R's 1:3 = Liberal).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "Study2.csv"), na.strings = "NA")
stopifnot(nrow(s) == 28860, uniqueN(s$respondent) == 962, s[, .N, .(respondent, trial)][, all(N == 2)])
for (v in c("c_pid", "c_educ", "c_china", "c_court", "c_lgbt", "c_gun")) stopifnot(all(s[[v]] %in% 1:2))
# opposite positions within every pair; opposite parties in trials 1-10, same party in 11-15
for (v in c("c_educ", "c_china", "c_court", "c_lgbt", "c_gun")) stopifnot(s[, uniqueN(get(v)), .(respondent, trial)][, all(V1 == 2)])
stopifnot(s[, uniqueN(c_pid), .(respondent, trial)][, all(V1 == ifelse(trial <= 10, 2, 1))])
lab <- function(x, yes, no) ifelse(x == 1, yes, no)
ctype <- (s$trial - 1L) %% 5L + 1L
court_yes <- c("Supports Eliminating Judicial Review", "Supports Electing Justices", "Supports Term Limits",
               "Supports Expanding the Court", "Supports Jurisdiction Stripping")
court_no <- c("Do Not Eliminate Judicial Review", "Do Not Elect Justices", "Opposes Term Limits",
              "Keep Court at 9 Justices", "Do Not Strip Jurisdiction")
court_prop <- c("judicial review", "electing justices", "term limits", "expanding the Court", "jurisdiction stripping")
rec <- function(x) c(5L, 4L, 2L, 1L, 3L)[x]   # Study2.R: 4=1;3=2;5=3;2=4;1=5
d <- s[, .(id = as.integer(respondent), task = as.integer(trial), profile = as.integer(c_number),
           choice = as.integer(c_choose == 1), rating = rec(c_rate), rating_mobilize = rec(c_mobil),
           attr_party = lab(c_pid, "Democratic Candidate", "Republican Candidate"),
           attr_education = lab(c_educ, "Gov't Should Help Pay for College", "Do Not Help Pay"),
           attr_china = lab(c_china, "Gov't Should Place Tariff on China", "Do Not Place Tariff"),
           attr_guns = lab(c_gun, "Gov't Should Require Background Check", "No Required Background Check"),
           attr_lgbt = lab(c_lgbt, "Gov't Should Protect LGBT from Discrimination", "No LGBT Discrimination Laws Needed"),
           attr_court = ifelse(c_court == 1, court_yes[ctype], court_no[ctype]),
           trial_court_proposal = court_prop[ctype],
           trial_election = ifelse(trial <= 10, "general", "primary"),
           cov_pid = as.integer(pid), cov_ideology = as.integer(ideo))]
stopifnot(d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)],
          d[, uniqueN(is.na(choice)), .(id, task)][, all(V1 == 1)])
d <- d[!(is.na(choice) & is.na(rating) & is.na(rating_mobilize))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "driscoll_2023_court_curbing.csv"))
