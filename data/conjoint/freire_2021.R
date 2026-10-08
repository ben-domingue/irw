##Climate-treaty design conjoint with Latin American elites from
##Freire, D., Mignozzetti, U., & Skarbek, D. (2021). Institutional design and elite support
##for climate policies: Evidence from Latin American countries. Journal of Experimental
##Political Science, 8(2), 172-184. https://doi.org/10.1017/XPS.2020.19
##Replication data: Harvard Dataverse doi:10.7910/DVN/VTA5OA, CC0 1.0. File read:
##freire-mignozzetti-skarbek.RData (data frame `cj`, loaded into its own environment);
##README.md, paper.R and supplementary-material-climate-policy.pdf read as text.
##Usage: Rscript freire_2021.R <dir holding the .RData> <output dir>
##
##Elite survey (Qualtrics, online, 1 Oct - 5 Dec 2018) of executive, legislative,
##civil-society and academic elites in ten Latin American countries (supplement s.1, s.7);
##the authors pool countries in their main models (country and elite type are subgroup
##covariates) -> ONE table with cov_country and cov_elite_group. 651 respondents, up to 7
##pairs of hypothetical climate-mitigation treaties. task and profile are the source columns.
##Prompt (supplement p. 66-67, English translation of the Spanish/Portuguese text):
##"Imagine that your country would sign an international treaty to mitigate climate change.
##... Please select the treaty that has the characteristics that you believe are best for
##your country." choice = `selected`; forced choice, no opt-out.
##Attributes, six, in a fixed row order (the source's .rowpos columns are the same for every
##respondent: rules 1, conflicts 2, punishment 3, repeated violations 4, costs 5,
##renegotiation 6, so no attrpos_). Level text is the authors' English factor labels
##(respondents saw Spanish or Portuguese, not deposited); supplement Table 32 spells "NGOs"
##as "Non-governmental organizations". Randomization uniform within each attribute, with
##ONE restriction (supplement p. 66): Punishment = None never appears with repeated
##violations = Less penalty (verified: 0 rows).
##Duplicates: 3 respondents have some tasks recorded twice (same profiles and choice; the
##copies differ only in non-conjoint columns); one copy is kept: 32 rows dropped, 7,936 left.
##Covariates: cov_country (`countryOrigin`, the country sampled; blank for 778 rows as in
##the source), cov_elite_group (`groupOrigin`). DROPPED: Qualtrics Response.ID (re-keyed),
##LocationLatitude/LocationLongitude (respondent GPS from Qualtrics), `country` and
##`validCountry` (derived from that location), respondentIndex.
##Check: marginal means match the supplement's MM table to 2 decimals (Fines 0.55,
##Imprisonment 0.46, None 0.45; Five years 0.59, Never 0.40).
##Count check: the supplement reports 654 interviews in total, of which the conjoint was in
##the online part; the deposit has 651 respondents.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "freire-mignozzetti-skarbek.RData"), envir = e)
s <- as.data.table(e$cj)
cjcols <- c("respondent", "task", "profile", "selected", grep("\\?$", names(s), value = TRUE))
stopifnot(length(cjcols) == 10, s[, uniqueN(Response.ID), respondent][, all(V1 == 1)])
s <- unique(s, by = cjcols)
stopifnot(s[, .N, .(respondent, task, profile)][, all(N == 1)], s[, sum(selected), .(respondent, task)][, all(V1 == 1)])
rp <- grep("rowpos$", names(s), value = TRUE)
stopifnot(all(s[, lapply(.SD, uniqueN), .SDcols = rp] == 1))
stopifnot(s[`What punishments do they use?` == "None" & `How are repeated violations punished?` == "Less penalty", .N] == 0)
key <- sort(unique(s$respondent))
d <- s[, .(id = match(respondent, key), task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected),
           attr_rule_makers = as.character(`Who makes the rules?`), attr_conflict_resolution = as.character(`How are conflicts resolved?`),
           attr_punishment = as.character(`What punishments do they use?`),
           attr_repeated_violations = as.character(`How are repeated violations punished?`),
           attr_cost_distribution = as.character(`How are costs distributed?`),
           attr_renegotiation = as.character(`How often will the agreement be renegotiated?`),
           cov_country = countryOrigin, cov_elite_group = groupOrigin)]
stopifnot(uniqueN(d$id) == 651, nrow(d) == 7936)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "freire_2021_climate_treaty.csv"))
