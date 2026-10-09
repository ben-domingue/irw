##Party-manifesto conjoint (Flanders, Belgium) from
##Luypaert, J. (2024). Replication data for: Balancing an ideological trade-off: Electoral appeal of
##consistent and responsive party positions [Data set]. Harvard Dataverse.
##https://doi.org/10.7910/DVN/RZE2BA (deposited 2024-12-09; the article was not found in Crossref, so
##the deposit is cited).
##Replication data: CC0 1.0, no restricted files, no terms.
##Files read: dataset_forced_PPSD_OF.csv and dataset_forced_PPLIB_OF.csv (Dataverse originals of the
##.tab files). Also read as text: ReplicationCode.txt (design list, party codes of Q2). Read but not
##used: dataset_ranked_PPSD_OF.xlsx / dataset_ranked_PPLIB_OF.xlsx (see "Dropped") and
##Bundles_*.xlsx (the authors' classification of manifestos into consistent/responsive programs).
##Usage: Rscript luypaert_2024.R <raw dir> <output dir>
##
##2,119 Flemish voters (deposit description: "a conjoint experiment with 2082 voters conducted in
##Flanders"; the authors' code keeps voters of four parties, Q2 2 = Vooruit, 3 = Groen, 5 = Open VLD,
##7 = Vlaams Belang, and all respondents in the files are from these four, but one with Q2 missing). Each chose between two
##party manifestos in 10 tasks: tasks 1-5 social democratic manifestos (PPSD file), tasks 6-10 liberal
##manifestos (PPLIB file), with the same four binary attributes; trial_manifesto = "social democratic" /
##"liberal" (from the file names and the deposit description). ONE TABLE: same respondents, same
##attributes and design; the authors analyse the two manifesto families separately (filter on
##trial_manifesto to do the same).
##Attributes (Dutch level text as displayed, the authors' design list): WelfareState (Afbouwen /
##Uitbreiden van de welvaartstaat), InheritanceTaxes (Verlaag / Verhoog de belastingen op erfenis),
##Immigration (Geen bovenlimiet op aantal immigranten / Sterk terugdringen van aantal immigranten),
##NatureConservation (Verhoog / Verlaag het aantal beschermde natuurgebieden). Levels uniform and
##unconstrained (the authors' cjoint design: marginal weights 1/2, empty constraint list). Attribute
##row order was randomized once per respondent (the *.rowpos columns are constant within respondent
##and vary between respondents): attrpos_* columns. An empty column "Beschermen.van.natuurgebieden"
##(all NA) is ignored.
##Outcome: choice = `selected`, one manifesto chosen in every task, no opt-out. Question wording not
##in the deposit (the authors label it "Vote Intention"). The deposit description says respondents
##also rated the manifestos; that rating is in the "ranked" files but is NOT included: its question,
##scale and direction are undocumented, it takes values 1-6 for liberal and 1-5 for social democratic
##manifestos, and the authors' code never analyses it (FOR BEN: could be added as rating if a
##questionnaire turns up).
##Dropped: the Qualtrics ResponseId (re-keyed; the source `respondent` number is not kept) and
##respondentIndex; the pre-treatment Q3_*, Q5_*, Q6_1, Q8_1-Q11_1, Q14_*-Q17_* items (numeric codes
##with no labels or wording in the deposit).
##Covariates: cov_vote_party = Q2 mapped with the authors' code (voter groups "Vooruit", "Groen",
##"Open VLD", "Vlaams Belang"; whether Q2 is vote choice or party identification is not stated; one
##respondent has Q2 missing).
##N: 2,119 respondents (2,116 in the social democratic and 2,024 in the liberal tasks; 2,021 in both)
##vs 2,082 in the deposit description. Flag, not fixed.
##Spot check: the authors' H3 model (Open VLD voters, liberal manifestos, selected ~ 4 attributes, SEs
##clustered by respondent) gives lower inheritance taxes +0.226 (SE 0.016), expanding the welfare
##state +0.127; no published numbers to compare.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f, lab) {
  x <- fread(file.path(raw, f))
  stopifnot(x[, .(n = .N, s = sum(selected)), .(ResponseId, task)][, all(n == 2 & s == 1)], all(is.na(x$Beschermen.van.natuurgebieden)),
            x[, uniqueN(Welvaartstaat.rowpos), ResponseId][, all(V1 == 1)])
  x[, trial_manifesto := lab]
}
x <- rbind(rd("forced_SD.orig", "social democratic"), rd("forced_LIB.orig", "liberal"))
stopifnot(x[trial_manifesto == "social democratic", all(task %in% 1:5)], x[trial_manifesto == "liberal", all(task %in% 6:10)],
          x[, uniqueN(Q2), ResponseId][, all(V1 == 1)], all(x$Q2 %in% c(2, 3, 5, 7, NA)))
ids <- sort(unique(x$ResponseId))
d <- data.table(id = match(x$ResponseId, ids), task = as.integer(x$task), profile = as.integer(x$profile),
                choice = as.integer(x$selected),
                attr_welfare_state = x$WelfareState, attr_inheritance_taxes = x$InheritanceTaxes,
                attr_immigration = x$Immigration, attr_nature_conservation = x$NatureConservation,
                attrpos_welfare_state = as.integer(x$Welvaartstaat.rowpos), attrpos_inheritance_taxes = as.integer(x$Erfbelastingen.rowpos),
                attrpos_immigration = as.integer(x$Immigratie.rowpos), attrpos_nature_conservation = as.integer(x$Natuurgebieden.rowpos),
                trial_manifesto = x$trial_manifesto,
                cov_vote_party = c(`2` = "Vooruit", `3` = "Groen", `5` = "Open VLD", `7` = "Vlaams Belang")[as.character(x$Q2)])
d[, cov_vote_party := unname(cov_vote_party)]
for (v in grep("^attr", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]))
stopifnot(d[, all(sort(c(attrpos_welfare_state[1], attrpos_inheritance_taxes[1], attrpos_immigration[1], attrpos_nature_conservation[1])) == 1:4), .(id, task, profile)]$V1)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "luypaert_2024_party_manifestos.csv"))
cat(nrow(d), uniqueN(d$id), d[trial_manifesto == "liberal", uniqueN(id)], d[trial_manifesto != "liberal", uniqueN(id)], "\n")
