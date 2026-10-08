##Supreme Court nominee conjoint (judicial philosophies) from
##Krewson, C. N., & Owens, R. J. (2021). Public support for judicial philosophies: Evidence
##from a conjoint experiment. Journal of Law and Courts, 9(1), 89-110.
##https://doi.org/10.1086/712649
##Replication data: Harvard Dataverse doi:10.7910/DVN/RLVSNF, CC0 1.0, no restricted files.
##Files read: conjoint.RData (data.frame `dat`, forced choice), conjoint2.RData (`dat2`, the
##ratings of the same profiles, row for row), cjoint_design.RData (cjoint design object
##`design_adj`, read for its dependence rule). conjoint_analysis.R read as text. No codebook or
##questionnaire ships; the article is paywalled. Sample facts (YouGov, 1,000 matched
##respondents, fielded 2018-04-26 to 2018-05-04) are from the appendix of the authors'
##companion paper (Krewson & Owens 2022, JLC 10(2), doi:10.1086/715547), which uses a design
##with the same attributes and N; that the two papers share the fielding is INFERRED.
##Usage: Rscript krewson_2021.R <raw dir> <output dir>
##
##1,000 US adults, 5 pairs of hypothetical nominees, 10 attributes. The files have NO task or
##profile column. Rows come in 10 blocks of 1,000, each block holding every respondent once in
##the same order; blocks 2k-1 and 2k form task k (profile 1 = odd block): in every task exactly
##one profile is preferred (24 tasks are unanswered on both rows). So task and profile are
##INFERRED from row order; which block was shown left is assumed.
##Outcomes (one experiment, one table):
##  choice: Preferred, forced choice between the two nominees, no opt-out. 24 tasks
##    (48 rows) have no choice: choice blank there. Wording not in the deposit (unknown).
##  rating: Score, 1-5 rating of each nominee. Wording and anchors not in the deposit; that 5
##    is the favourable end is INFERRED (chosen profiles average 3.7, unchosen 2.6). 2 rows
##    have no rating. Rows with neither outcome are omitted.
##Attribute text: the authors' short labels, used as is (Age 40-65; Sex; Race; Religion;
##Legal_Education (15 law schools); Position; Philosophy (8 levels; the companion appendix
##describes each, e.g. "Original Intent: Looks to the intent of the drafters and ratifiers of
##the Constitution..."; whether respondents saw the label or the description is not
##documented); ABA Rating; Held_Office; Ideology; Party of the appointing president). Display
##order not documented.
##Randomization RESTRICTED (design_adj$dependence: Party <-> Ideology): a Democratic nominee
##is Liberal or Moderate, a Republican Conservative or Moderate. Level weights are NOT uniform
##(observed: race White 38%, Black 25%, others 12-13%; law school Yale 19.5%, Stanford 17%,
##Harvard 13%, Chicago 10%, others 3-7%); the design object carries the joint probabilities
##(its marginals give race .38/.25/.12/.12/.12 and law school .200/.167/.133/.100/.067/.033...,
##matching the data, but ABA rating .50/.33/.17 and a 7-level Philosophy, which the data do not
##show: ABA rating is about 1/3 each and Philosophy has 8 levels).
##Covariates: cov_survey_weight (YouGov weight), cov_party_id (pid3, factor labels as stored:
##Democrat / Republican / Independent / Other / Not Sure), cov_party_id7_code (pid7, kept as
##codes 1-8: the deposit gives only the ends, "Partisanship (Strong Democrat to Strong
##Republican)" in the authors' plot label, and 8 = not sure from their recode to NA; no source
##names codes 2-6), cov_ideo5 (1 = very liberal .. 5 = very conservative, 6 = not sure, same
##source). No attention check, duration or repeated task in the deposit.
##Dropped: YouGov respondent ids (re-keyed 1..1,000 in file order), the authors' derived
##Philosophy2 (computed in their code, not stored).
##N: 1,000 = the companion paper's N; the article was not checked (paywalled).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env()
for (f in c("conjoint.RData", "conjoint2.RData", "cjoint_design.RData")) load(file.path(raw, f), envir = e)
s <- as.data.table(e$dat); s2 <- as.data.table(e$dat2)
stopifnot(nrow(s) == 10000, nrow(s2) == 10000, all(s$id == s2$id),
          all(sapply(c("Age", "Sex", "Race", "Religion", "Legal_Education", "Position", "Philosophy", "Rating", "Held_Office", "Ideology", "Party"),
                     function(v) all(as.character(s[[v]]) == as.character(s2[[v]])))))
stopifnot(identical(e$design_adj$dependence, list(Party = "Ideology", Ideology = "Party")))
blk <- (seq_len(nrow(s)) - 1L) %/% 1000L
stopifnot(all(s$id == rep(s$id[1:1000], 10)), uniqueN(s$id[1:1000]) == 1000)
ids <- match(s$id, s$id[1:1000])
d <- data.table(id = ids, task = blk %/% 2L + 1L, profile = blk %% 2L + 1L,
                choice = as.integer(s$Preferred), rating = as.integer(s2$Score),
                attr_age = as.character(s$Age), attr_sex = as.character(s$Sex), attr_race = as.character(s$Race),
                attr_religion = as.character(s$Religion), attr_legal_education = as.character(s$Legal_Education),
                attr_position = as.character(s$Position), attr_philosophy = as.character(s$Philosophy),
                attr_aba_rating = as.character(s$Rating), attr_held_office = as.character(s$Held_Office),
                attr_ideology = as.character(s$Ideology), attr_party = as.character(s$Party),
                cov_survey_weight = s$weight, cov_party_id = as.character(s$pid3),
                cov_party_id7_code = as.integer(as.character(s$pid7)), cov_ideo5 = as.integer(as.character(s$ideo5)))
stopifnot(d[, .(s = sum(choice), n = sum(is.na(choice))), .(id, task)][, all((n == 0 & s == 1) | n == 2)])
stopifnot(d[, !any((attr_party == "Democratic" & attr_ideology == "Conservative") | (attr_party == "Republican" & attr_ideology == "Liberal"))])
d <- d[!(is.na(choice) & is.na(rating))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "krewson_2021_judicial_philosophy.csv"))
