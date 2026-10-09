##Internet-voting (i-voting) reform conjoint (UK) from
##Turnbull-Dugarte, S. J., & Devine, D. (2023). Support for digitising the ballot box: A
##systematic review of i-voting pilots and a conjoint experiment. Electoral Studies, 86,
##102679. https://doi.org/10.1016/j.electstud.2023.102679
##Replication data: Harvard Dataverse doi:10.7910/DVN/RJTVG8, CC0 1.0, no restricted files.
##File read: evoting_replicationfile.dta (Dataverse "original format" download). The authors'
##replication_electoralstudies.R and appendix.R were read as text only. The article itself
##could not be retrieved (publisher and repository returned 403), so question wording below
##is a paraphrase from the variable names and the authors' figure labels.
##Usage: Rscript turnbulldugarte_2023.R <raw dir> <output dir>
##
##1,200 UK respondents (education coded with Prolific's "DATA EXPIRED" value, so presumably a
##Prolific sample; not confirmed), 5 tasks x 2 i-voting reform proposals, long file with
##recorded task, profile, selected (one chosen per task, verified) and choice (1/2, agrees).
##Outcomes, ONE table (all three are asked about the same profiles):
##  choice           = selected: which of the two proposals the respondent supports
##                     (paraphrase; forced choice, no opt-out).
##  rating_support   = probselected, 0-6 per proposal; the authors rescale it to 0-1
##                     (probnormal), so higher = more likely to support (direction inferred
##                     from the rescaling and the authors' use; anchors not in the deposit).
##  rating_trust     = trustworthy, 0-6 per proposal; the authors' figure label is
##                     "Trustworthiness vis-a-vis in-person voting", rescaled 0-1 as
##                     trustnormal (higher = more trustworthy, inferred). 2 profiles have NA.
##Attribute level text = the .dta value labels on the authors' *_num variables (the
##Qualtrics labels; typos such as "smarphone" and "IT form" kept as stored). The authors'
##recode code uses slightly different wording for the same codes (e.g. "Decreases risk of
##fraud"); the .dta labels are used. Codes of the *_num variables and the authors' 0-based
##codes agree one-to-one (checked). "Administered by" is ONE source variable with 6 levels
##(platform_num: council / central government / both, each with or without "private sector
##IT firm"); the authors split it into platform and private for analysis. It is stored as
##the single displayed attribute attr_administered_by. Attribute names follow the authors'
##figure labels. Attribute order and randomization restrictions are not documented.
##Covariates: cov_gender (sex, authors' recode 0 = "Man" -> male, 1 = "Woman" -> female);
##cov_education (education .dta value labels; "DATA EXPIRED" = missing -> NA, "Don't know /
##not applicable" kept); cov_ethnicity (ethnic labels White/Asian/Black/Mixed/Other);
##cov_degree (0 No degree / 1 Degree), cov_noncis (0 Cisgender / 1 Not cisgender),
##cov_lgb (queer: 0 Hetero / 1 LGB), cov_votemethod (0 In-person voter / 1 Convenience voter),
##cov_ideo (0 Left / 1 Centre / 2 Right), cov_vote_main (votemain 0 Labour / 1 Conservative /
##2 Other / 3 Abstain; a vote, not party ID), all labels from the authors' recode code;
##cov_duration_sec = Qualtrics "Duration (in seconds)" for the whole survey.
##Dropped: IDvar's value labels (Qualtrics ResponseIds; IDvar itself is already 1..1200),
##Start/EndDate, consent, unlabelled survey items (onlineactivity_*, perceive_*,
##internetsat, turnout, income, voteleave, vote2019, child), the authors' derived dummies and
##means (trustbin, satisfied_*, viewsfraud, nonwhite, edmean, incomemean, income2, votetory,
##*normal) and the 0-based attribute codes. No survey weight in the deposit. No repeated task.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "evoting_replicationfile.dta"))
s <- as.data.table(zap_labels(k))
d <- data.table(id = as.integer(s$IDvar), task = as.integer(s$task), profile = as.integer(s$profile),
                choice = as.integer(s$selected), rating_support = as.integer(s$probselected),
                rating_trust = as.integer(s$trustworthy))
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
          all((s$choice == s$profile) == (s$selected == 1)), all(d$rating_support %in% 0:6), all(d$rating_trust %in% c(0:6, NA)))
lab <- function(v) { x <- as.character(as_factor(k[[v]], levels = "labels")); stopifnot(!anyNA(x)); x }
attrs <- c(prereg = "prereg_num", method = "method_num", voting_window = "vwindow_num", successful_trials_in = "trials_num",
           result_of_pilot = "pilot_num", effect_on_fraud = "fraud_num", costs = "cost_num", administered_by = "platform_num",
           proposing_party = "party_num", endorsed_by = "endorse_num")
for (n in names(attrs)) d[, paste0("attr_", n) := lab(attrs[[n]])]
setnames(d, "attr_prereg", "attr_pre_registration")
# the labelled codes agree one-to-one with the authors' 0-based codes
for (v in c("prereg", "fraud", "method", "vwindow", "trials", "pilot", "cost", "party", "endorse"))
  stopifnot(s[, uniqueN(get(paste0(v, "_num"))), by = v][, all(V1 == 1)])
stopifnot(s[, uniqueN(platform_num), .(platform, private)][, all(V1 == 1)])
stopifnot(all(s$sex %in% 0:1))
d[, cov_gender := fifelse(s$sex == 1, "female", "male")]
ed <- as.character(as_factor(k$education, levels = "labels")); ed[ed == "DATA EXPIRED"] <- NA
d[, cov_education := ed]
d[, cov_ethnicity := as.character(as_factor(k$ethnic, levels = "labels"))]
rc <- function(x, l) { stopifnot(all(x %in% c(seq_along(l) - 1, NA))); l[x + 1] }
d[, `:=`(cov_degree = rc(s$degree, c("No degree", "Degree")), cov_noncis = rc(s$noncis, c("Cisgender", "Not cisgender")),
         cov_lgb = rc(s$queer, c("Hetero", "LGB")), cov_votemethod = rc(s$votemethod, c("In-person voter", "Convenience voter")),
         cov_ideo = rc(s$ideo, c("Left", "Centre", "Right")), cov_vote_main = rc(s$votemain, c("Labour", "Conservative", "Other", "Abstain")),
         cov_duration_sec = as.integer(s$Durationinseconds))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "turnbulldugarte_2023_ivoting.csv"))
