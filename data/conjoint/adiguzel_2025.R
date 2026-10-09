##Checks-and-balances candidate conjoint (Turkey) from
##Adiguzel, F. S. (2025). Checks and balances and institutional gridlock: Implications for
##authoritarianism. Governance, 38(2). https://doi.org/10.1111/gove.70017
##Replication data: Harvard Dataverse doi:10.7910/DVN/WABIY5, CC0 1.0. Files read:
##experimentdata_pairlevel.rda (data.frame `alldata`, one row per respondent x task x candidate)
##and experimentdata_indlevel.rda (data.frame `ist`, one row per respondent; covariates).
##The authors' experimental_analysis.R was read as text (not run). No codebook or questionnaire
##ships and the article (Wiley) could not be read, so the outcome wording below is a PARAPHRASE
##from the variable names and the authors' table labels.
##Usage: Rscript adiguzel_2025.R <dir holding the .rda files> <output dir>
##
##515 respondents in the file (variable names `ist`, `Anketor` = interviewer suggest an interviewer-administered
##survey, presumably in Istanbul; not documented), 5 pairs of hypothetical candidates (A/B),
##2 attributes, both Turkish text as stored in the data (CP1254 -> UTF-8):
##  attr_judiciary_law: the candidate's proposed law on the judiciary (5 texts: reduce courts'
##    workload [neutral]; judiciary checks the government less / more; and, in the treatment
##    version only, the same two with a justification: "to speed up public services" /
##    "to reduce corruption"),
##  attr_social_policy: the candidate's social-policy plan (4 plans or "Bu konuda herhangi bir
##    öneri yapmamıştır" = made no proposal on this issue).
##trial_version: the between-respondent arm (source `signal`): 1 = the less/more-oversight laws
##carry the gridlock / corruption justification, 0 = no justification (stopifnot checks that the
##justified texts appear only in arm 1). Both arms in one table, as the authors analyse them jointly.
##task = last digit of the source `profile_code` (1-5), profile = candidate A (1) / B (2): RECORDED.
##Outcomes (paraphrase; anchors not deposited):
##  choice: which of the two candidates the respondent would select (source `selection`; exactly one
##    per answered task, no opt-out).
##  rating_democrat: how democratic the candidate is, 0-10 (authors: "Democracy Rating"; higher =
##    more democratic assumed from the authors' table, not stated).
##  rating_like: support / liking of the candidate, 1-5 (authors: "Support"; direction not stated).
##231 of 2,575 tasks have no selection (choice NA on both profiles); rows with no outcome at all are
##dropped (273 rows; 5 respondents answered nothing): 510 respondents, 4,877 rows. The authors drop 5 respondents with time_min < 14 (speeders); kept here, with
##cov_time_min so they can be filtered. Covariates kept: cov_gender (female 1 -> "female", 0 -> "male"),
##cov_age, cov_ideology (0-10 as stored, labels unknown), cov_erdogan_voter (0/1), cov_time_min
##(survey duration, minutes). Education/income codes have no labels and are left out, as are the
##interviewer code, the gridlock items and the authors' recodes (law_policyRecoded, social_policies).
##Restrictions/weights not documented; the two attributes are crossed in the data.
##Spot-check: Table A21 Selection, Authoritarian Characteristic -0.148 (N 4,642) reproduced below.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "experimentdata_pairlevel.rda"), envir = e)
load(file.path(raw, "experimentdata_indlevel.rda"), envir = e)
s <- as.data.table(e$alldata); p <- as.data.table(e$ist)
u <- function(x) iconv(as.character(x), "CP1254", "UTF-8")
s[, law := u(law_policy)][, soc := u(social_policy)]
stopifnot(s[, .N, id][, all(N == 10)], uniqueN(s$id) == 515, all(s$candidate %in% c("A", "B")))
s[, task := as.integer(substring(profile_code, nchar(profile_code)))][, profile := match(candidate, c("A", "B"))]
stopifnot(s[, .N, .(id, task)][, all(N == 2)], s[, uniqueN(task), id][, all(V1 == 5)])
just <- grepl("için", s$law)
stopifnot(all(s$signal[just] == 1), s[, uniqueN(law)] == 5, s[, uniqueN(soc)] == 5)
stopifnot(s[!is.na(selection), sum(selection), .(id, task)][, all(V1 == 1)],
          s[, uniqueN(is.na(selection)), .(id, task)][, all(V1 == 1)])
p <- p[, .(id, cov_gender = c("male", "female")[female + 1L], cov_age = as.integer(age),
           cov_ideology = ideology, cov_erdogan_voter = ErdoganVoters, cov_time_min = time_min)]
d <- s[, .(id = as.integer(id), task, profile, choice = as.integer(selection),
           rating_democrat = democrat, rating_like = like,
           attr_judiciary_law = law, attr_social_policy = soc, trial_version = as.integer(signal))]
d <- merge(d, p[, id := as.integer(id)], by = "id", all.x = TRUE)
d <- d[!(is.na(choice) & is.na(rating_democrat) & is.na(rating_like))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "adiguzel_2025_checks_balances.csv"))
x <- d[!is.na(choice) & cov_time_min > 13]
x[, law := relevel(factor(fifelse(grepl("daha az", attr_judiciary_law), "auth", fifelse(grepl("daha çok", attr_judiciary_law), "dem", "neutral"))), "neutral")]
cat("rows", nrow(d), "resp", uniqueN(d$id), "A21 N", nrow(x), "\n")
print(format(coef(lm(choice ~ law * trial_version + attr_social_policy * trial_version, x))[2:3], digits = 4))  # A21: -0.148, 0.156
