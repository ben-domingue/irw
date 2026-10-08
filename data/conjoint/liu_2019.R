##Entry-level cadre selection conjoint (China) from
##Liu, H. (2019). The logic of authoritarian political selection: Evidence from a conjoint
##experiment in China. Political Science Research and Methods, 7(4), 853-870.
##https://doi.org/10.1017/psrm.2018.24
##Replication data: Harvard Dataverse doi:10.7910/DVN/SLZ2OA, CC0 1.0, no restricted files.
##File read: conjoint_ncse.dta. Attribute levels from its Stata value labels (English; the
##authors' plot script uses the same labels); outcome meanings from its variable labels. The
##article is paywalled and was not read beyond its abstract ("over 300 government officials in
##China"); the deposit's ReadMe and do-file give no question wording.
##Usage: Rscript liu_2019.R <raw dir> <output dir>
##
##332 Chinese government officials in the deposit (cov_online = 1 for the online respondent pool, 0 for the
##other pool, as coded by the author), 5 tasks x 2 candidate profiles for an entry-level post;
##task and profile recorded (source `task`, `profile`). Outcomes (wording NOT deposited):
##  choice = source `win` ("outcome: being selected"); exactly one selected per answered pair
##     (checked); 181 pairs unanswered. Treated as forced choice (no opt-out level in the data).
##  rating_qualified = `match` ("rating on being qualified and suitable"), 1-5.
##  rating_leadership = `leader` ("rating on leadership quality"), 1-5.
##  rating_implementation = `implement` ("rating on task implementation"), 1-5.
##  Ratings stored raw; anchors not deposited. They correlate positively with being selected
##  (match r = 0.39), consistent with 5 = most favourable, but no source states it.
##Attributes (value-label text; display language not documented): gender female/male; political
##affiliation none/ccp; college general college/elite university; education bachelor/master
##degree; award won in college (no award, artistic talent, community outreach, academic
##excellence, student leadership); prior work experience (no experience, company job,
##government job); father's occupation (private sector worker, SOE worker (CCP member), private
##entrepreneur, government official). Randomization restrictions and attribute order: not
##documented in the deposit (level shares look uniform). No survey weight. One respondent's task 4
##happens to repeat an earlier pair; no repeat task is documented.
##Covariates: cov_gender (res_gender 1 = male, 2 = female, missing = NA; res_gender has no value
##labels, the direction comes from res_male, variable label "respondent characteristic: male",
##which is 1 exactly where res_gender = 1), cov_age (res_age, years), cov_ccp,
##cov_rank (1-6, codes not labelled in the deposit), cov_leader, cov_interviewer (has
##interviewer experience), cov_workunit (label text), cov_online.
##Dropped: PairID, match_win (derived), res_male (duplicate of res_gender, codes missing
##gender as 0). Rows with no outcome at all omitted.
##N: 332 respondents in the deposit, consistent with the abstract's "over 300"; 33 answered
##nothing, so the table has 299 (ids re-keyed 1..299 after that drop).
##Spot check: LPM of choice on father's occupation, SE clustered by respondent: government
##official vs private sector worker +0.22 (abstract: kinship ties to government raise a
##candidate's chance by over 20 points).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "conjoint_ncse.dta")))
stopifnot(all(zap_labels(s$res_gender) %in% c(1, 2, NA)), s[!is.na(res_gender), all((zap_labels(res_gender) == 1) == (zap_labels(res_male) == 1))])
lab <- function(x) { l <- attr(x, "labels"); y <- names(l)[match(as.integer(x), l)]; stopifnot(!anyNA(y)); y }
d <- data.table(id = s$ObsID, task = as.integer(s$task), profile = as.integer(s$profile),
                choice = as.integer(s$win), rating_qualified = as.integer(s$match),
                rating_leadership = as.integer(s$leader), rating_implementation = as.integer(s$implement),
                attr_gender = lab(s$male), attr_political_affiliation = lab(s$ccp), attr_college = lab(s$eliteuniv),
                attr_education = lab(s$postgrad), attr_award = lab(s$prize), attr_work_experience = lab(s$workexp),
                attr_father_occupation = lab(s$fatherjob),
                cov_gender = c("male", "female")[as.integer(zap_labels(s$res_gender))], cov_age = as.integer(s$res_age),
                cov_ccp = as.integer(s$res_ccp), cov_rank = as.integer(s$res_rank), cov_leader = as.integer(s$res_leader),
                cov_interviewer = as.integer(s$res_interviewer),
                cov_workunit = { l <- attr(s$res_workunit, "labels"); names(l)[match(as.integer(s$res_workunit), l)] },
                cov_online = as.integer(s$online))
stopifnot(d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
d <- d[!(is.na(choice) & is.na(rating_qualified) & is.na(rating_leadership) & is.na(rating_implementation))]
d[, id := as.integer(factor(id))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "liu_2019_cadre_selection.csv"))
