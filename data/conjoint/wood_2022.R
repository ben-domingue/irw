##Campaign-finance transparency candidate conjoint (Study 2) from
##Wood, A. K. (2022). Voters use campaign finance transparency and compliance information.
##Political Behavior. https://doi.org/10.1007/s11109-022-09776-4
##Replication data: Harvard Dataverse doi:10.7910/DVN/TA4DUW, CC0 1.0. File read:
##finalcleanconjointdata.RData (data frame `data`, one row per respondent x contest x candidate).
##Labels: "codebook for study 2 data.pdf" (deposit) and the article's Table 3 ("Conjoint attributes
##and levels, Study 2", an image on the article page). Study 1 (a two-candidate vignette with a
##transparency grade) is a different experiment and is not built.
##Usage: Rscript wood_2022.R <dir holding the .RData> <output dir>
##
##Bovitz opt-in panel, spring 2019, wave 2 of a two-wave survey: 1,490 respondents, each voting
##in a [PARTY] primary for an open state-senate seat ("Suppose you were voting in a [PARTY]
##primary for an open seat for state senate in your state. Please view the following two
##candidate profiles and answer the questions below."), 6 contests of 2 candidates (A/B), 9
##attributes. Party primary = the respondent's party (true independents randomly assigned):
##trial_primary.
##Outcomes:
##  choice = chosen ("If you had to choose between them, which of these candidates would you
##           vote for?", Candidate A or B; pre-analysis plan, appendix p. 11). No opt-out.
##  rating = trustrating, trustworthiness of each candidate, 1 = "Not at all", 3 = "Moderately",
##           5 = "Extremely" (codebook; the drop-down text in `trust` agrees one-to-one). Higher =
##           more trustworthy. The pre-analysis plan planned a 1-7 item; the deposit holds 1-5.
##Attribute text: two attributes are stored in the data as coding short-hand, mapped here to the
##displayed text of article Table 3 (codebook: "respondents did not see mention of dark money"):
##  cf_compliance: missed_deadlines = "Out of compliance (has missed filing deadlines)",
##    reporting_gaps = "Out of compliance (has not reported some contributions)",
##    in_compliance = "In compliance", donors_on_site = "In compliance, and website gives extra
##    information (number of small donors)", map_on_site = "In compliance, and website gives
##    extra information (map with number of donors from each zip code)".
##  relationship_dmgroups: discouraged_dark_money = "Requested that groups with anonymous
##    donors not support candidacy.", dark_money_support = "Supported by groups with anonymous
##    donors.", raised_dark_money = "Prior to announcing candidacy, raised money for a group with
##    anonymous donors that now supports campaign".
##  The other 7 attributes keep the text stored in the data (trailing spaces trimmed). Two
##  differ from Table 3: total raised is $250,000/$500,000/$750,000 in the data ($1,000,000 in
##  Table 3), grasp is "Good grasp" (Table 3 "Decent"); the data are kept. Persuasiveness reads
##  "Extremely Persuasive" in the Democratic-primary version and "Extremely persuasive" in the
##  Republican one (as stored; kept).
##Restrictions (appendix pre-analysis plan p. 13; article): Democratic-primary candidates never
##"Strongly opposes" and Republican-primary candidates never "Strongly Supports" the immigration
##or sex-education policy (confirmed in the data). Row order randomized across respondents,
##fixed within respondent (appendix p. 11); the order was not saved, so no attrpos_ columns.
##Cleaning: ParticipantID (panel ID) re-keyed to integers in source order. The deposit holds
##irregular contests: 21 with only one candidate row, 18 with 4 rows (3 respondents appear
##with 24 rows, i.e. twice), and 6 with no chosen candidate. Only contests with exactly one
##Candidate A row, one Candidate B row and one chosen candidate are kept (8,870 contests, 1,485 respondents;
##the article reports 8,931).
##Covariates: cov_gender from Gender (codebook: 1 = Male, 2 = Female); cov_age = Age (years);
##cov_education from education codes via codebook text; cov_party_id = PID1 (answer text);
##cov_pid_rep, cov_pid_dem, cov_pid_lean (strength / lean follow-ups), cov_ideo7, cov_newsint,
##cov_housemaj, cov_senatemaj, cov_sup_immig_policy, cov_sup_sex_ed as answer text (empty = NA);
##cov_income (codes 1-11, 99 = decline; codebook), cov_ethnicity (codes, ";"-joined; codebook),
##cov_hispanic (1 yes, 2 no) keep codes. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "finalcleanconjointdata.RData"), envir = e)
s <- as.data.table(e$data)
s[, rid := match(ParticipantID, unique(ParticipantID))]
s[, task := as.integer(contest_no)]
chk <- s[, .(n = .N, nA = sum(Candidate == "Candidate A"), nB = sum(Candidate == "Candidate B"), ch = sum(chosen)), .(rid, task)]
keep <- chk[n == 2 & nA == 1 & nB == 1 & ch == 1, .(rid, task)]
s <- s[keep, on = .(rid, task)]
cf <- c(missed_deadlines = "Out of compliance (has missed filing deadlines)",
        reporting_gaps = "Out of compliance (has not reported some contributions)",
        in_compliance = "In compliance",
        donors_on_site = "In compliance, and website gives extra information (number of small donors)",
        map_on_site = "In compliance, and website gives extra information (map with number of donors from each zip code)")
dm <- c(discouraged_dark_money = "Requested that groups with anonymous donors not support candidacy.",
        dark_money_support = "Supported by groups with anonymous donors.",
        raised_dark_money = "Prior to announcing candidacy, raised money for a group with anonymous donors that now supports campaign")
stopifnot(all(s$cf_compliance %in% names(cf)), all(s$relationship_dmgroups %in% names(dm)))
txt <- function(x) { x <- trimws(as.character(x)); x[x == ""] <- NA; x }
d <- data.table(id = s$rid, task = s$task, profile = match(s$Candidate, c("Candidate A", "Candidate B")),
                choice = as.integer(s$chosen), rating = as.integer(s$trustrating),
                attr_immigration_policy = txt(s$police_immigrant), attr_sex_ed_policy = txt(s$sex_ed),
                attr_cf_compliance = unname(cf[s$cf_compliance]), attr_anonymous_donor_groups = unname(dm[s$relationship_dmgroups]),
                attr_total_raised = txt(s$`Total amount raised`), attr_small_donor_share = txt(s$small_donors),
                attr_profession = txt(s$`Professional Background`), attr_persuasiveness = txt(s$persuasiveness),
                attr_grasp = txt(s$grasp),
                trial_primary = c(D = "Democratic", R = "Republican")[s$party_assigned])
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^trial_|^profile$|^choice$|^rating$")]))
edu <- c("Less than high school graduate", "High school graduate, diploma or the equivalent (for example= GED)",
         "Some college credit, no degree", "Trade/technical/vocational training", "Associate degree",
         "Bachelor's degree", "Master's degree", "Professional degree", "Doctorate degree")
stopifnot(all(s$Gender %in% c("1", "2")), all(s$education %in% 1:9))
d[, cov_gender := c("male", "female")[as.integer(s$Gender)]]
ag <- suppressWarnings(as.integer(s$Age)); d[, cov_age := ag]
d[, cov_education := edu[s$education]]
d[, cov_party_id := txt(s$PID1)]
d[, `:=`(cov_pid_rep = txt(s$PIDrep), cov_pid_dem = txt(s$PIDdem), cov_pid_lean = txt(s$PIDlean),
         cov_ideo7 = txt(s$ideo7), cov_newsint = txt(s$newsint), cov_housemaj = txt(s$housemaj),
         cov_senatemaj = txt(s$senatemaj), cov_sup_immig_policy = txt(s$SupImmigPolicy), cov_sup_sex_ed = txt(s$SupSexEd),
         cov_income = suppressWarnings(as.integer(s$Income)), cov_ethnicity = txt(s$Ethnicity),
         cov_hispanic = suppressWarnings(as.integer(s$Hispanic)))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wood_2022_campaign_finance.csv"))
