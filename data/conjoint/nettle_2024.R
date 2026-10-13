##Welfare scheme conjoint, UK, from
##Nettle, D., Chrisp, J., Johnson, E., & Johnson, M. (preprint). What do people want from a welfare system?
##Conjoint survey evidence from UK adults. (SP2.1 conjoint experiment on welfare scheme preferences.)
##Preprint: https://doi.org/10.31235/osf.io/zfnuh
##Replication data: OSF doi:10.17605/osf.io/htsqc, CC BY-NC 4.0 (node licence). Files read:
##"Data and R code/conjointdata.csv", the protocol PDF ("NIHR154451 SP2.1 Conjoint Analysis Protocol FINAL.pdf",
##attribute definitions and the Qualtrics survey), paper_Rmd_v4.Rmd (text only, not run; design description).
##Usage: Rscript nettle_2024.R <dir holding conjointdata.csv> <output dir>
##
##800 UK adults recruited on Prolific (April 2023), 15 tasks x 2 policies, 10 attributes. The file has 801
##Prolific ids; one has no choice data and all attributes NA in 30 rows (the Rmd removes the non-matching
##person from the individual file): dropped, leaving 800 as in the paper ("800 UK residents").
##Task and profile are recorded in `stratum` = <Prolific id> + "c<task 2 digits><profile 2 digits>"
##(e.g. c0701 = task 7, profile 1); the task also equals `choice.numeric` (checked). Exactly one chosen per task.
##Outcome: choice = "Choose your preferred option below" (their preferred welfare policy of two; forced; no
##opt-out; the authors did not ask for ratings). Level text is stored as in the file (the authors' short
##labels for the Qualtrics levels; the protocol lists the long form). payment level = weekly payment in the
##order child/adult/pensioner; income tax = basic/higher/additional rate. One label is stored as in the file
##although it lacks its percent sign: "Poverty -10" (= decreased by 10%).
##Restrictions (paper Rmd): designs ruled out a priori: payments are 9 fixed child/adult/pensioner bundles
##(child payment not above adult, adult not above pensioner) and income tax is 7 fixed three-rate bundles
##(the file shows the same bundles); other attributes are drawn independently.
##Dropped: Prolific PID and the stratum string (ids re-keyed to integers), free-text columns (vote.last.other,
##vote.intend.other, benefits.text), `benefits` (a multi-select list of benefits received), choice.numeric.
##Covariates: cov_age (Prolific, years), cov_gender (Prolific "sex as recorded on official documents"; Male/Female),
##cov_ethnicity (Prolific simplified; DATA_EXPIRED = NA), cov_managing_financially (text, numbering removed),
##cov_voting_attitude, cov_vote_last (2019 General Election vote or non-vote, text), cov_vote_intend (text).
##"Prefer not to say" = NA. Prolific demographics are missing for 104 respondents (expired): NA. No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "conjointdata.csv"), encoding = "UTF-8")
k <- k[!is.na(chosen)]
n <- nchar(k$stratum)
d <- data.table(id = match(k$pid, unique(k$pid)), task = as.integer(substr(k$stratum, n - 3, n - 2)),
                profile = as.integer(substr(k$stratum, n - 1, n)), choice = as.integer(k$chosen))
stopifnot(all(substr(k$stratum, 1, n - 5) == k$pid), all(d$task == k$choice.numeric))
for (p in list(c("payment", "Payment level"), c("income_tax", "Income tax"), c("other_funding", "Other funding"), c("poverty", "Poverty"),
               c("inequality", "Inequality"), c("life_expectancy", "Life expectancy"), c("anxiety_depression", "Anxiety and depression"),
               c("conditionality", "Conditionality"), c("means_testing", "Means testing"), c("universality", "Universality")))
  d[, paste0("attr_", p[1]) := k[[p[2]]]]
cl <- function(x) { x <- trimws(x); x[x %in% c("", "NA", "Prefer not to say", "DATA_EXPIRED")] <- NA; x }
d[, cov_age := as.integer(k$Age)]
d[, cov_gender := tolower(cl(k$Sex))]
d[, cov_ethnicity := cl(k[["Ethnicity simplified"]])]
d[, cov_managing_financially := cl(sub("^[0-9]\\.\\s*", "", k$managing.financially))]
d[, cov_voting_attitude := cl(k$voting.attitude)]
d[, cov_vote_last := cl(k$vote.last)]
d[, cov_vote_intend := cl(k$vote.intend)]
stopifnot(uniqueN(d$id) == 800, d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d$cov_gender %in% c("female", "male", NA))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "nettle_2024_welfare_schemes.csv"))
