##Foreign-policy partner conjoints (US public), two studies, from the replication data of
##Kennedy, R. (2023). Do Americans care about human rights? International Journal of Human Rights (the deposit's
##own description; year = deposit release 2023; no article DOI found, the paper could not be located).
##Replication data: Harvard Dataverse doi:10.7910/DVN/OY8EZY, CC0 1.0. Files read: conjointData.tab (study 1) and
##conjointData2.tab (study 2), saved as c1.csv and c2.csv. scenarioData*.tab (a separate scenario experiment, no
##respondent id linking it to the conjoints, no scenario text) are NOT built.
##Usage: Rscript kennedy_2023.R <dir holding c1.csv c2.csv> <output dir>
##
##Two tables (different attribute sets and samples): kennedy_2023_hr_partner_s1 (1,181 respondents) and
##kennedy_2023_hr_partner_s2 (1,218 respondents). Each respondent: 5 tasks (cjnum) x 2 profiles; per task one
##profile `chosen` (exactly one per task, checked; forced choice, no opt-out) and per profile an `acceptable`
##judgement (0/1, stored as rating_acceptable: a 0/1 judgement of each profile, not a pick among profiles).
##Tasks where the choice is missing (NA in the source) are dropped (311 tasks study 1, 1,004 study 2); a missing
##`acceptable` alone stays NA. Profile 1/2 = row order within a task (choiceNum c<task>c<k>: k = profile) - the deposit
##marks the position by that suffix.
##LABELS: tags only. The deposit stores dummy-coded levels with short tags and ships no codebook; the paper could not
##be located, so neither the displayed attribute wording nor the question wording is recoverable. The profile is a
##hypothetical country (ally/adversary, human-rights record, regime type, press freedom, economic effect, ...); the
##stems cannot be expanded with certainty, so attributes keep the stems (m, a, dc, ms, hr, ec, gov, med / study 2: a,
##dc, ms, hr, ec, gov, nuc, tr) and levels keep the dummy tags (e.g. hrViolates, govDictator, medRepress, aAlly). Ben
##to decide whether to publish with tags only. Each family of dummies sums to exactly 1 in every profile (checked).
##Randomization restrictions, attribute order and level probabilities are not documented.
##Study 1 families: m (mNoChange, m3x, m2x), a (aAdversary, aAlly), dc (dcALot, dcALittle, dcSame), ms (msThird,
##msQuarter, msHalf), hr (hrViolates, hrUpholds), ec (ecHelpsLot, ecHelpsLittle, ecHurtsLittle, ecNeutral), gov (govDem,
##govDictator), med (medRepress, medFree). Study 2: a, dc, ms, hr, gov as above; ec (ecHurtsLot, ecHelpsLittle,
##ecHurtsLittle, ecNeutral); nuc (nucDev, nucHas, nucNot); tr (trSpon, trNot).
##No respondent covariates in the conjoint files. PII FOUND: Qualtrics ResponseId in study 2 and ResponseID in study 1
##(re-keyed to integers, dropped). Dropped: nothing else (all columns are dummies of attributes or outcomes).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fam1 <- list(m = c("mNoChange", "m3x", "m2x"), a = c("aAdversary", "aAlly"), dc = c("dcALot", "dcALittle", "dcSame"),
             ms = c("msThird", "msQuarter", "msHalf"), hr = c("hrViolates", "hrUpholds"),
             ec = c("ecHelpsLot", "ecHelpsLittle", "ecHurtsLittle", "ecNeutral"), gov = c("govDem", "govDictator"), med = c("medRepress", "medFree"))
fam2 <- list(a = c("aAdversary", "aAlly"), dc = c("dcALot", "dcALittle", "dcSame"), ms = c("msThird", "msQuarter", "msHalf"),
             hr = c("hrViolates", "hrUpholds"), ec = c("ecHurtsLot", "ecHelpsLittle", "ecHurtsLittle", "ecNeutral"),
             gov = c("govDem", "govDictator"), nuc = c("nucDev", "nucHas", "nucNot"), tr = c("trSpon", "trNot"))
one <- function(f, idcol, fam, name) {
  x <- fread(file.path(raw, f), na.strings = "NA")
  setnames(x, idcol, "rid")
  d <- data.table(id = as.integer(factor(x$rid, levels = unique(x$rid))), task = as.integer(x$cjnum),
                  profile = as.integer(sub("^c[0-9]+c", "", x$choiceNum)), choice = as.integer(x$chosen), rating_acceptable = as.integer(x$acceptable))
  stopifnot(!anyNA(d$profile), d[, .N, .(id, task, profile)][, all(N == 1)])
  for (k in names(fam)) {
    M <- sapply(fam[[k]], function(v) as.numeric(x[[v]])); ok <- !is.na(d$choice); stopifnot(all(rowSums(M[ok, , drop = FALSE]) == 1))
    d[[paste0("attr_", k)]] <- fam[[k]][max.col(M, ties.method = "first")]; d[[paste0("attr_", k)]][rowSums(is.na(M)) > 0] <- NA
  }
  d <- d[, if (!anyNA(choice)) .SD, .(id, task)]
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
  setcolorder(d, c("id", "task", "profile", "choice", "rating_acceptable"))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, name))
  cat(name, d[, uniqueN(id)], nrow(d), "\n")
}
one("c1.csv", "ResponseID", fam1, "kennedy_2023_hr_partner_s1.csv")
one("c2.csv", "ResponseId", fam2, "kennedy_2023_hr_partner_s2.csv")
