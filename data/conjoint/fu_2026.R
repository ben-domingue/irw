##Perceived-victory conjoints (Taiwan) from
##Fu, R. T., Lee, E. I., & Kao, K. Y. (2026). Do you think David can win against Goliath?
##Evidence on factors affecting popular perceptions of victory in Taiwan against Chinese
##aggression. Research & Politics. https://doi.org/10.1177/20531680261467197
##Replication data: Harvard Dataverse doi:10.7910/DVN/FUILWY, CC0 1.0. Files read: cj_w1.rda
##(data.table dg1) and cj_w2.rda (dg2), each loaded into its own environment. ReadMe.txt,
##analysis.R, function.R and run.log were read as text. The article (Sage) could not be
##retrieved, so question wording and display language are not documented here.
##Usage: Rscript fu_2026.R <dir holding the two .rda> <output dir>
##
##Taiwanese adults compared 5 pairs of hypothetical scenarios of a Chinese attack and chose one
##(`chosen`; the outcome concerns perceived chances of Taiwan's victory, per the title and
##ReadMe; exact wording unknown). 7 attributes (names from function.R .relabel_attribute):
##international military support (att1), international economic sanctions (att2), economic
##strength against China (att3), military strength against China (att4), Taiwan's military
##readiness (att5), Taiwan's public morale (att6), parties' views on anti-aggression (att7).
##Two waves with different wording of att1 are analysed separately by the authors, so two tables:
##  fu_2026_victory_abstract (wave 1, "abstract condition": att1 = No/Limited/Full support from
##    US and Japan), 1,444 respondents, as in run.log.
##  fu_2026_victory_concrete (wave 2, "concrete condition": att1 = Do nothing/Providing
##    weapons/Sending troops), 1,011 respondents, as in run.log.
##att1 combines US and Japan in one attribute with 6 levels (Japan never does more than the US);
##the levels are stored as the authors' English factor labels. Randomization rules and
##attribute order are not documented in the deposit: restrictions unknown.
##task = `round`, profile = `profile` (recorded). Exactly one profile chosen per task.
##Covariates: cov_gender (Male/Female), cov_birth_year, cov_age_group, cov_region (6 regions),
##cov_identity (Taiwanese / Dual/Chinese; blank = neither). IDs are the authors' integers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(file, obj, n, name) {
  e <- new.env(); load(file.path(raw, file), envir = e)
  s <- as.data.table(e[[obj]])
  nm <- c(att1 = "military_support", att2 = "sanctions", att3 = "economic_strength", att4 = "military_strength",
          att5 = "readiness", att6 = "morale", att7 = "party_unity")
  d <- s[, .(id = as.integer(ID), task = as.integer(round), profile = as.integer(profile), choice = as.integer(chosen))]
  for (k in names(nm)) d[, paste0("attr_", nm[[k]]) := as.character(s[[k]])]
  d[, `:=`(cov_gender = as.character(s$gender), cov_birth_year = as.integer(s$year), cov_age_group = as.character(s$age),
           cov_region = as.character(s$loc), cov_identity = as.character(s$identity))]
  stopifnot(uniqueN(d$id) == n, d[, .N, id][, all(N == 10)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
            !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
}
build("cj_w1.rda", "dg1", 1444, "fu_2026_victory_abstract")
build("cj_w2.rda", "dg2", 1011, "fu_2026_victory_concrete")
