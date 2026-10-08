##Hong Kong protest-demand package conjoints (before and after the National Security Law) from
##Kobayashi, T., Song, J., & Chan, P. (2021). Does repression undermine opposition demands?
##The case of the Hong Kong National Security Law. Japanese Journal of Political Science,
##22(4), 268-286. https://doi.org/10.1017/S1468109921000256
##Replication data: Harvard Dataverse doi:10.7910/DVN/KJBRQG, CC0 1.0. Files read:
##JJPS_KSC_Wave1.csv, JJPS_KSC_Wave2.csv (Dataverse "original format" downloads).
##Attribute and level TEXT comes from the `Scale_Labels` vector in the authors'
##JJPS_KSC_Replication.R (read as text, not run); the data hold only codes A1, B2, ...
##Usage: Rscript kobayashi_2021.R <dir holding the two csv files> <output dir>
##
##Hong Kong respondents chose between two hypothetical packages of government responses
##to the 2019 protesters' demands (commission of inquiry, rioter classification, amnesty,
##universal suffrage, Chief Executive resignation) bundled with economic relief measures
##(cash handout, tax reduction, public-housing rent waiver, rates waiver). The wave 2
##experiment (after the NSL took effect, June 2020) adds four attributes describing NSL
##enforcement (target, term of imprisonment, trial by jury, authority in charge).
##TWO TABLES, one per wave: the attribute sets differ (9 vs 13 attributes) and the samples
##are separate (no respondent ID appears in both files). The authors compare waves on the
##9 shared attributes (difference in marginal means); a user can stack the two tables.
##  kobayashi_2021_hk_demands_wave1: 1,522 respondents x 5 tasks x 2 profiles.
##  kobayashi_2021_hk_demands_wave2: 1,541 respondents x 5 tasks x 2 profiles.
##Task and profile are recorded (columns Task, Profile).
##Outcome: choice = Choice, forced choice, exactly one profile chosen in every task
##(checked). The question wording, the survey firm, the fielding dates and the display
##language are not in the deposit and the article is paywalled (not read); the wording in
##the design record is a paraphrase. Attribute order and randomization restrictions are not
##documented; level shares look uniform.
##Attribute text is the authors' English labels (some are shortened or ungrammatical, e.g.
##"Waived one month's of rents"; kept as written). Respondents likely saw Chinese; not
##verifiable from the deposit.
##Covariate: cov_pid = the respondent's political camp as stored (Pro-establishment,
##Pan-democrats, Localist), the authors' subgroup variable.
##Dropped: the source ID (a Qualtrics ResponseId, R_...), re-keyed to integers 1..n per wave.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- c(
  A1 = "Denied",
  A2 = "Setting up an independent review committee with members appointed by the Hong Kong government",
  A3 = "Setting up an independent commission of inquiry",
  B1 = "Denied", B2 = "Fully accepted",
  C1 = "Denied", C2 = "Amnesty only for protestors arrested over minor offenses",
  C3 = "Amnesty only for juvenile protestors", C4 = "Fully accepted",
  D1 = "Status quo",
  D2 = "Voters may elect the CE from the candidates nominated by the Nominating Committee through 'one person, one vote'",
  D3 = "Voters may elect all members of the Legislative Council through 'one person, one vote'",
  D4 = "Voters may elect the CE and all members of the Legislative Council through 'one person, one vote'",
  E1 = "Denied", E2 = "Fully accepted",
  F1 = "HKD 10,000", F2 = "HKD 25,000",
  G1 = "75% of the first $20,000", G2 = "100% of the first $15,000",
  G3 = "75% of the first $40,000", G4 = "100% of the first $30,000",
  H1 = "Waived one month's of rents", H2 = "Waived two months' of rents", H3 = "Waived four months' of rents",
  I1 = "Waived up to a ceiling of $3,000 per annum", I2 = "Waived up to a ceiling of $6,000 per annum",
  I3 = "Waived up to a ceiling of $12,000 per annum",
  J1 = "Those who made public statements that call for toppling Central or HKSAR govts",
  J2 = "Those who made public statements that criticize or call for toppling Central or HKSAR govts",
  K1 = "Mostly 3-5 years", K2 = "Mostly 10 years to life sentence",
  L1 = "Mostly yes", L2 = "Mostly no",
  M1 = "Mostly Hong Kong Police Force", M2 = "Mostly National Security Agents")
nm <- c(A = "police_inquiry", B = "rioter_classification", C = "amnesty", D = "universal_suffrage",
        E = "ce_resignation", F = "cash_handout", G = "tax_reduction", H = "housing_rent_waiver",
        I = "rates_waiver", J = "nsl_target", K = "nsl_imprisonment", L = "nsl_jury_trial", M = "nsl_authority")
build <- function(f, n_attr, n_id, tab) {
  s <- fread(file.path(raw, f))
  d <- data.table(id = match(s$ID, unique(s$ID)), task = as.integer(s$Task), profile = as.integer(s$Profile),
                  choice = as.integer(s$Choice))
  for (k in names(nm)[seq_len(n_attr)]) {
    stopifnot(all(s[[k]] %in% names(lab)), all(substr(s[[k]], 1, 1) == k))
    d[, paste0("attr_", nm[[k]]) := unname(lab[s[[k]]])]
  }
  d[, cov_pid := s$PID]
  stopifnot(uniqueN(d$id) == n_id, d[, .N, id][, all(N == 10)], !anyDuplicated(d[, .(id, task, profile)]),
            d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(tab, ".csv")))
}
build("JJPS_KSC_Wave1.csv", 9, 1522, "kobayashi_2021_hk_demands_wave1")
build("JJPS_KSC_Wave2.csv", 13, 1541, "kobayashi_2021_hk_demands_wave2")
