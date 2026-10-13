##Conjoint on prohibiting AI systems, five countries, from
##Ehret, S. (2022). Public preferences for governing AI technology: Comparative evidence.
##Journal of European Public Policy, 29(11), 1779-1798.
##https://doi.org/10.1080/13501763.2022.2094988
##Replication data: figshare doi:10.6084/m9.figshare.20537781, CC BY 4.0.
##Files read: replication_conjoint_data_analysis_prdct.Rdata (object conjoint_data; loaded into a new
##environment), online_appendix_jepp_ehret_.pdf (Table 1 level text, Table 7 samples, figure captions),
##replication_material_01_main_analysis_jepp.R (text only, not run; covariate coding comments).
##Usage: Rscript ehret_2022.R <dir holding the .Rdata> <output dir>
##
##932 respondents in 5 samples pooled in one table (cov_country): Germany 298 (Clickworkers, 2020), UK 202
##(university panel, 2019), China 156 (Microworkers; Hong Kong and mainland), Chile 101, India 175 (university
##panels); quotas for gender and age. Counts equal appendix Table 7 (which lists the 48 respondents with
##missing choices as already removed). The authors pool the samples (cross-country AMCE differences) and
##share one attribute set, so one table.
##5 tasks x 2 algorithm profiles, 7 attributes (appendix Table 1): privacy protection, risk of unemployment,
##job creation, discrimination, transparency, decision area, choices made in dilemma. The deposit stores
##short codes; the level text stored here is the full level wording of appendix Table 1 (a one-to-one recode).
##Outcome: choice = the algorithm chosen in "Which of the algorithms should be prohibited?" (selected = 1 is
##the prohibited one; exactly one per task; no opt-out). The 1-7 approval rating the appendix describes
##(Figure 2) is not in the deposit.
##Profile = row order within respondent-task (the file has two rows per task; no column records position:
##inferred; the share of first rows chosen is 0.50). Task is the recorded `task` column.
##Covariates (codes mapped from the authors' coding comments in the analysis script): cov_country;
##cov_unemployment_insurance_reliance (Major source / Minor source / Not a source at all / Refuse to answer
##or don't know), cov_living_standard_confidence (Very confident ... Not confident; same DK category),
##cov_privacy_concern (Very concerned ... Not concerned; same DK category). "NR" (non-response) = NA. These
##three are kept as in the file. digitalliteracy is the
##authors' binned scale of questionnaire items: dropped. The Qualtrics Response.ID is dropped (ids re-keyed).
##No survey weight. Randomization restrictions and level probabilities are not documented.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "replication_conjoint_data_analysis_prdct.Rdata"), e)
k <- as.data.table(e$conjoint_data)
rc <- function(x, from, to) { x <- as.character(x); stopifnot(all(x %in% from)); to[match(x, from)] }
k[, rid := match(Response.ID, unique(Response.ID))]
k[, pos := seq_len(.N), .(rid, task)]
d <- data.table(id = k$rid, task = as.integer(k$task), profile = k$pos, choice = as.integer(k$selected))
d[, attr_privacy_protection := rc(k$Privacy, c("customize", "gather w/o consent", "with consent"),
  c("Can customize whether personal information collected or not", "Gathers personal information without consent", "Requires to reveal personal information with consent"))]
d[, attr_risk_of_unemployment := rc(k$Risk.of.unemployment, c("very low unempl risk", "somewhat low risk", "somewhat high risk", "very high risk"),
  paste(c("Very low", "Somewhat low", "Somewhat high", "Very high"), "risk of unemployment for you and others due to automation"))]
d[, attr_job_creation := rc(k$Job.creation, c("no jobs", "benefit college edu", "benefit manual labor", "jobs benefit all"),
  c("Does not create new jobs", "Creates new jobs that benefit college educated professionals only - for example diagnosis specialist",
    "Creates new jobs that benefit manual labour and non-college occupations - for example robotics operator", "Creates new jobs that benefit all professions and occupations"))]
d[, attr_discrimination := rc(k$Discrimination, c("neutral", "recreate bias"),
  c("Acts neutral without bias or discrimination", "Somewhat high risk to recreate human biases and discrimination"))]
d[, attr_transparency := rc(k$Transparency, c("easy to explain", "nobody can understand", "only experts can understand"),
  c("Algorithm can be explained to 5th grader", "Nobody can understand how decisions are made", "Only experts can understand algorithm"))]
d[, attr_decision_area := rc(k$Example.area.of.use, c("medicial", "advertising", "production", "finance", "surveillance/safety", "public service"),
  c("Medical decisions on health and well-being", "Advertising and consumer goods", "Manufacturing and production", "Financial services and banking", "Security and surveillance", "Public administration"))]
d[, attr_choices_in_dilemma := rc(k$Choices.made.in.dilemma, c("humans vs. money", "humans vs humans", "money vs. money", "no choices made"),
  c("Chooses between helping humans or saving money", "Chooses between helping humans or other humans",
    "Chooses between spending money on one thing or spending money on another thing", "Does not make choices/decisions"))]
d[, cov_country := sub("^[a-e]\\) ", "", k$Q_country)]
d[, cov_unemployment_insurance_reliance := rc(k$socinsuremajsourc, c("NR", "1", "2", "3", "4"),
  c(NA, "Major source", "Minor source", "Not a source at all", "Refuse to answer / don't know"))]
d[, cov_living_standard_confidence := rc(k$livingstandexp, c("NR2", "12", "22", "32", "42", "52"),
  c(NA, "Very confident", "Confident", "Somewhat confident", "Not confident", "Refuse to answer / don't know"))]
d[, cov_privacy_concern := rc(k$privacyconcern, c("NR3", "13", "23", "33", "43", "53"),
  c(NA, "Very concerned", "Concerned", "Somewhat concerned", "Not concerned", "Refuse to answer / don't know"))]
stopifnot(uniqueN(d$id) == 932, d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_|^choice")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ehret_2022_ai_governance.csv"))
