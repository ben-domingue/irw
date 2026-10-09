##West Bank policy-package conjoint (Israeli Jewish adults, wave 3) from
##Manekin, D. S., Grossman, G., & Mitts, T. (2019). Contested ground: Disentangling material and
##symbolic attachment to disputed territory. Political Science Research and Methods, 7(4), 679-697.
##https://doi.org/10.1017/psrm.2018.22 (closed access; not read beyond the abstract)
##Replication data: Harvard Dataverse doi:10.7910/DVN/INCWQN, CC0 1.0, one archive
##Replication_dataverse_final.tar.gz. Files read: conjoint_dataset_anon.rdata (2 rows per respondent),
##sumstats_phase3_anon.rdata (the same 1,345 respondents' background answers as Hebrew answer text,
##joined by ResponseID), 1.Main_results.R and 2.Supplementay_information_tables.R (read as text, not run).
##Usage: Rscript manekin_2019.R <dir holding the extracted .rdata files> <output dir>
##
##1,345 respondents, ONE task of 2 policy packages, 4 attributes (territory, security, economy, budgets).
##The level text is the authors' English (factor labels in the .rdata, identical to the attribute list
##in 1.Main_results.R); the survey was in Hebrew (Hebrew answer text in sumstats_phase3_anon) and the
##Hebrew attribute wording is not deposited.
##task = 1 for every row. profile is INFERRED from row order within ResponseID: in all 1,345 pairs the
##first row is chosen exactly when Q8_conjoint_choice = 1 and the second exactly when it is 2
##(stopifnot below), so row 1 = policy 1.
##  choice = chose.policy (Q8_conjoint_choice, "Conjoint policy choice (1-2)"): forced choice between
##           the two packages, no opt-out (exactly one chosen per respondent). Question wording is not
##           in the deposit.
##  rating = rank_policy, stored 1-7, one per profile; the authors call it "Conjoint rank policy (1-7)"
##           (SI summary table) and plot it as "Change in policy ranking". Wording, anchors and
##           direction are NOT documented in the deposit; stored raw.
##Randomization restrictions (1.Main_results.R constraint_list, cjoint makeDesign): no "attacks will
##decrease significantly" with "security budget will increase ...", no "attacks will increase
##significantly" with "security budget will decrease ...", no "attacks will increase significantly" with
##"economy will grow significantly". Level shares are unequal (security unchanged 1,240 of 2,690 rows).
##Covariates (Hebrew answer text from sumstats_phase3_anon, mappings per 2.Supplementay_information_
##tables.R L55-111): cov_gender (Q2: נקבה = female, זכר = male, blank = NA), cov_age_group (Q3),
##cov_region (Q4, area of residence), cov_religiosity (Q5), cov_education (Q20), cov_income (Q21,
##relative to average), cov_vote_2015 (Q17 text; the Qualtrics placeholder "Click to write Choice 6" is
##the authors' "Israel Beitenu" (L104) and is stored as "ישראל ביתנו"), cov_ethnicity (Q22). Blank
##answers are NA. Dropped: ResponseID (Qualtrics id; respondents re-keyed 1..1345 in ResponseID order),
##the numeric-coded copies of the same questions, Q13/Q14/Q29 (other experiments' items with codes and
##no labels), the authors' derived ideology/likud/extreme-right dummies.
##NOT built from this deposit: the phase-2 conjoint (conjoint_phase2_anon.rdata, 1,217 respondents, a
##two-level territory attribute): its levels are numeric codes whose only labels are the authors' plot
##axis names in 3.Supplementay_information_figures.R ("Withdraw from territory", "Security budget
##increase"), not the displayed text. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "conjoint_dataset_anon.rdata"), envir = e)
s <- as.data.table(e$conjoint_dataset_anon)
e2 <- new.env(); load(file.path(raw, "sumstats_phase3_anon.rdata"), envir = e2)
cv <- as.data.table(e2$sumstats_phase3_anon)
stopifnot(nrow(s) == 2690, s[, .N, ResponseID][, all(N == 2)], uniqueN(cv$ResponseID) == 1345,
          setequal(cv$ResponseID, s$ResponseID))
s[, profile := seq_len(.N), ResponseID]
stopifnot(s[, all(chose.policy == as.integer(as.integer(Q8_conjoint_choice) == profile))])
ids <- data.table(ResponseID = sort(unique(s$ResponseID)))[, id := .I]
s <- ids[s, on = "ResponseID"]
d <- s[, .(id, task = 1L, profile, choice = as.integer(chose.policy), rating = as.integer(rank_policy),
           attr_territory = as.character(territory), attr_security = as.character(security),
           attr_economy = as.character(economy), attr_budgets = as.character(budgets), ResponseID)]
stopifnot(d[, sum(choice), id][, all(V1 == 1)], all(d$rating %in% 1:7),
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
nz <- function(x) { x <- trimws(as.character(x)); x[x == ""] <- NA; x }
cv <- cv[, .(ResponseID, g = nz(Q2), cov_age_group = nz(Q3), cov_region = nz(Q4), cov_religiosity = nz(Q5),
             cov_education = nz(Q20), cov_income = nz(Q21), cov_vote_2015 = nz(Q17_vote_2015_text),
             cov_ethnicity = nz(Q22))]
stopifnot(all(cv$g %in% c("נקבה", "זכר", NA)))
cv[, cov_gender := c("נקבה" = "female", "זכר" = "male")[g]][, g := NULL]
cv[cov_vote_2015 == "Click to write Choice 6", cov_vote_2015 := "ישראל ביתנו"]
setcolorder(cv, c("ResponseID", "cov_gender"))
d <- cv[d, on = "ResponseID"][, ResponseID := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "manekin_2019_disputed_territory.csv"))
