##Taiwan bilingual/multilingual ballot paired comparison (Study 1) from
##Liu, A. H., Selsky, S., Xu, M., & Yew, J. (2026). When bilingual ballot designs promote or undermine
##inclusivity: Evidence from three studies. Public Opinion Quarterly. https://doi.org/10.1093/poq/nfag048
##Replication data: Harvard Dataverse doi:10.7910/DVN/YULUZ1, CC0 1.0, no restricted files.
##File read: "POQ _Study 1 _Taiwan.tab". Design and attribute coding from the authors'
##"Script _Study 1, Study 2 (SM3 3) .Rmd" (read as text, not run). The article (closed access) and
##the questionnaire were not available; there is no codebook in the deposit.
##Usage: Rscript liu_2026.R <raw dir> <output dir>
##
##Only Study 1 is built. Study 2 (Texas students) shows every respondent the same three ballots and
##asks for the best and worst (no randomized profiles); Study 3 (Georgia) assigns one of five ballot
##versions between subjects (one manipulated factor). Neither is a conjoint.
##Study 1: 2,088 Taiwanese respondents (column record), 5 rounds each (task = round). In each round two
##different ballots, drawn from 7 ballot designs (all 42 ordered pairs occur, 222-275 times each), were
##shown as ballot_A (profile 1) and ballot_B (profile 2). The 7 designs (Rmd table) cross two
##attributes:
##  language: "Chinese only" (A); "Chinese and Paiwan" (B, E); "Chinese and Vietnamese" (C, F);
##     "Chinese, Paiwan and Vietnamese" (D, G)
##  arrangement: "Stacked" (B, C, D; languages collated within each race, one column);
##     "Separated" (E, F, G; one column per language); design A is monolingual and has no arrangement,
##     coded "(not shown)" (the Rmd table gives "N/A"; its analysis code calls it "stacked").
##The level texts are the authors' descriptions of ballot images (presentation = image), in English;
##respondents saw ballots in Chinese (Mandarin) with Paiwan and/or Vietnamese. Restriction: arrangement
##exists only for multilingual ballots (7 of the 8 language x arrangement cells).
##Outcomes, one pick per pair each (fair = 1 -> ballot_A chosen, 2 -> ballot_B; verified that
##fair_yes is the chosen ballot letter in every answered round; same for the other two):
##  choice_fair, choice_democratic, choice_efficient. Wording not deposited: by the variable names,
##  "Which of the two ballots is more fair / more democratic / more efficient?" (paraphrase).
##  Unanswered picks (552 fair, 619 democratic, 429 efficient rounds) are NA on both profiles; rounds
##  with none of the three answered are dropped. No opt-out offered as far as the data show (NA =
##  item nonresponse).
##Covariates: cov_gender (column female 1/0), cov_region (the region_* dummy that is 1: central/
##east/north/south). Other demographics (D1-D4, Q59-Q66, age, education, party, income, ancestry,
##language proficiency, travel) are numeric codes with no codebook in the deposit (the Rmd recodes
##party from text in an undeposited xlsx), so they are dropped, as are the authors' derived
##variables (monolingual_yes, fair_A, pref, ...). `unique` is a row number (record*10+round) and is
##not used. No survey weight in the file.
##The Rmd drops every row with any NA (na.omit over all columns); this table keeps all answered rounds.
##Respondent count vs the article not checked (article closed access).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "POQ _Study 1 _Taiwan.tab"))
stopifnot(s[, .N, record][, all(N == 5)], !anyDuplicated(s[, .(record, round)]), all(s$ballot_A != s$ballot_B))
lang <- c(A = "Chinese only", B = "Chinese and Paiwan", C = "Chinese and Vietnamese", D = "Chinese, Paiwan and Vietnamese",
          E = "Chinese and Paiwan", F = "Chinese and Vietnamese", G = "Chinese, Paiwan and Vietnamese")
arr <- c(A = "(not shown)", B = "Stacked", C = "Stacked", D = "Stacked", E = "Separated", F = "Separated", G = "Separated")
outs <- c("fair", "democratic", "efficient")
for (o in outs) {
  x <- s[[o]]; stopifnot(all(x %in% c(1L, 2L, NA)))
  chosen <- ifelse(x == 1L, s$ballot_A, s$ballot_B)
  stopifnot(all(chosen[!is.na(x)] == s[[paste0(o, "_yes")]][!is.na(x)]))
}
s <- s[!(is.na(fair) & is.na(democratic) & is.na(efficient))]
reg <- as.matrix(s[, .(region_central, region_east, region_north, region_south)])
stopifnot(all(rowSums(reg) == 1), all(s$female %in% 0:1))
d <- rbindlist(lapply(1:2, function(p) {
  b <- if (p == 1) s$ballot_A else s$ballot_B
  x <- data.table(id = as.integer(s$record), task = as.integer(s$round), profile = p)
  for (o in outs) x[, paste0("choice_", o) := as.integer(s[[o]] == p)]
  x[, `:=`(attr_language = unname(lang[b]), attr_arrangement = unname(arr[b]))]
  x[, cov_gender := ifelse(s$female == 1, "female", "male")]
  x[, cov_region := c("central", "east", "north", "south")[max.col(reg)]]
  x }))
stopifnot(!anyNA(d$attr_language))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "liu_2026_taiwan_ballots.csv"))
