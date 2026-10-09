##German party-candidate conjoint (AfD / CDU / SPD / Die Linke candidates) from
##Chou, W., Dancygier, R., Egami, N., & Jamal, A. A. (2021). Competing for loyalists? How party
##positioning affects populist radical right voting. Comparative Political Studies, 54(12),
##2226-2260. https://doi.org/10.1177/0010414021997166
##Replication data: Harvard Dataverse doi:10.7910/DVN/BQDMAD, CC0 1.0, no restricted files.
##Files read (inside cps-replication.zip): data/conjoint-data.csv, data/fourthwave.dta,
##data/weights_wave4.csv, Codebook.txt; replication/Figure-4-5-6-9.R and Appendix-C-1.R read as
##text. Usage: Rscript chou_2021.R <dir holding the unzipped cps-replication/> <output dir>
##
##3,019 German respondents of the authors' 4-wave online panel (wave 4; the conjoint file holds
##only those who passed the attention check v_253 == 3, as in the authors' scripts). Each saw 5
##screens (task = screen 1-5, recorded), each with FOUR candidates, one per party: Die Linke, SPD,
##CDU, AfD (profile 1-4 in the codebook order of v_602 "Candidate chosen on screen": 1 Die Linke,
##2 SPD, 3 CDU, 4 AfD; whether the columns were shown in this order is not documented). The party
##label is fixed by column, not randomized; it is kept as attr_party.
##Outcomes (Codebook.txt):
##  choice = choice.[party] "R chose candidate of [party] on conjoint screen"; one of four, no
##           opt-out (verified: exactly one chosen per screen, matching `choices`).
##  rating = rating.[party] "How R rated candidate of [party]", 1 (least favorable) to 7 (most
##           favorable). Wording paraphrased (the questionnaire is not deposited).
##Attributes (English text as in the data = Codebook.txt; respondents saw German): experience
##(v1), reason (v2), chance_winning (v3), refugee_policy (v4), border_policy (v5), pension_policy
##(v6), tax_policy (v7). Text kept as stored, including the deposit's "notbe" typo and the
##inconsistent final periods of v2.
##Restrictions (observed, not documented; the article was not accessible): level sets differ by
##party: the AfD candidate never has "Previously served for several terms" and only the two
##most restrictive refugee policies (complete stop / upper limit of 200,000); and every screen has
##exactly one or two candidates "expected to win the support of many voters".
##Covariates (fourthwave.dta, merged on pseudonym = id; codebook/value labels): cov_gender (v_8:
##1 Male, 2 Female), cov_birth_year (v_5), cov_state (v_354), cov_education_years (v_366; 0 "please
##select" -> NA), cov_income (v_129 label text; "No answer" -> NA), cov_occupation (v_95 label
##text), cov_vote_2017_second (v_141, party second vote in the 2017 election, label text; "No
##answer" -> NA), cov_vote_intention (v_143, "if election is next Sunday", label text; "No
##answer" -> NA), cov_survey_weight (weights_wave4.csv, used in appendix C.1).
##The panel pseudonym is re-keyed to integers (sorted pseudonym order). No repeated task.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
dd <- file.path(raw, "cps-replication", "data")
x <- fread(file.path(dd, "conjoint-data.csv"), encoding = "UTF-8")
w <- as.data.table(read_dta(file.path(dd, "fourthwave.dta"), encoding = "CP1252"))
wt <- fread(file.path(dd, "weights_wave4.csv"))
pa <- c(lnk = "Die Linke", spd = "SPD", cdu = "CDU", afd = "AfD")
av <- c(v1 = "experience", v2 = "reason", v3 = "chance_winning", v4 = "refugee_policy", v5 = "border_policy",
        v6 = "pension_policy", v7 = "tax_policy")
stopifnot(x[, .N, id][, all(N == 5)], x[, all((choice.lnk + choice.spd + choice.cdu + choice.afd) == 1 &
                                            choices == choice.lnk + 2 * choice.spd + 3 * choice.cdu + 4 * choice.afd)])
L <- lapply(seq_along(pa), function(p) {
  s <- names(pa)[p]
  r <- data.table(pid = x$id, task = as.integer(x$screen), profile = p, choice = as.integer(x[[paste0("choice.", s)]]),
                  rating = as.integer(x[[paste0("rating.", s)]]), attr_party = pa[[p]])
  for (v in names(av)) r[, paste0("attr_", av[[v]]) := x[[paste0(s, ".", v)]]]
  r
})
d <- rbindlist(L)
stopifnot(all(d$rating %in% 1:7), !anyNA(d), !any(d[, unlist(.SD), .SDcols = patterns("^attr_")] == ""))
lab <- function(v, na = character()) { r <- as.character(as_factor(v, levels = "labels")); r[r %in% na] <- NA; r }
w <- w[pseudonym %in% d$pid]
stopifnot(nrow(w) == uniqueN(d$pid), all(w$v_8 %in% 1:2), all(d$pid %in% wt$pseudonym))
cv <- data.table(pid = w$pseudonym, cov_gender = c("male", "female")[as.integer(w$v_8)], cov_birth_year = as.integer(w$v_5),
                 cov_state = w$v_354, cov_education_years = as.integer(zap_labels(w$v_366)),
                 cov_income = lab(w$v_129, "No answer"), cov_occupation = lab(w$v_95),
                 cov_vote_2017_second = lab(w$v_141, "No answer"), cov_vote_intention = lab(w$v_143, "No answer"))
cv[cov_education_years == 0, cov_education_years := NA]
cv <- merge(cv, wt[, .(pid = pseudonym, cov_survey_weight = weights)], by = "pid")
d <- merge(d, cv, by = "pid")
d[, id := frank(pid, ties.method = "dense")][, pid := NULL]
setcolorder(d, "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "chou_2021_party_candidates.csv"))
