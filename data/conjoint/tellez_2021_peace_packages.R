##Peace-agreement package conjoint (Colombia, 2016) from
##Tellez, J. F. (2021). Peace without impunity: Worldview in the settlement of civil wars. The Journal of Politics, 83(4).
##https://doi.org/10.1086/711555 (initials/volume from Crossref; deposit author "Tellez, Juan").
##Replication data: Harvard Dataverse doi:10.7910/DVN/OKYC0B, CC0 1.0.
##Files read: conjoint-noDup.tab (the R original conjoint-noDup.rda, one data.table `conjoint_nodup`, saved as
##cj.rdata; loaded into its own environment), README-1, conjoint-models.R and marginal-means.R as text.
##Usage: Rscript tellez_2021_peace_packages.R <dir holding cj.rdata> <output dir>
##
##997 Colombian adults (survey, December 2016, mode not stated, after the October 2016 peace referendum), 5 tasks x 2 packages
##(Acuerdo de Paz A / B), 6 attributes with 3 levels each: land, FARC elections, reintegration, victims' justice,
##victims' reparation, drug policy. 9 respondents have 4 tasks (the authors' "noDup" file; 9,952 rows). Task =
##task_num, profile = A/B (recorded); exactly one package chosen per task (checked); forced choice, no opt-out.
##choice = package chosen (`chosen_dummy`; question wording not in the deposit: "Which peace agreement do you prefer",
##paraphrase from the variable `prof_chosen` = "Acuerdo de Paz A/B").
##LABELS: the deposit stores the authors' short level tags ("land-high", "justice-medium", ...). No appendix text was
##recoverable (the article is paywalled and was not read), so the levels use the authors' own plain-language labels from their
##marginal-means.R / conjoint-models.R code (var_replace, in the order of the factor levels), paraphrased:
##  land: no transfer / small transfer / large transfer; elections: no electoral participation / FARC competes /
##  FARC competes + seats; reintegration: no assistance / 90% min. wage for demobilized / 200% min. wage for
##  demobilized; justice: no jail / jail for HR violators / jail for all FARC; reparation: no reparations / FARC ask
##  forgiveness / FARC pay victims; drugs: aerial fumigation / manual eradication / substitution program.
##The low/medium/high tags map to the order of those labels (checked against the coefficient labels in the models).
##Randomization restrictions and attribute order are not documented; all levels are near-uniform (shares 31-34%).
##Covariates: cov_gender (`woman` 1/0 -> female/male, authors' dummy name), cov_age_group (Spanish band text),
##cov_stratum (socio-economic stratum, text), cov_referendum_vote (answer text; "No responde" -> NA).
##PII FOUND: lat/lon, startDate/endDate, Qualtrics record IDs, municipality (all dropped). Dropped: derived
##dummies/numeric codes, child-rearing score, feelings thermometers, voted/registered dummies.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "cj.rdata"), envir = e)
x <- as.data.table(e$conjoint_nodup)
stopifnot(nrow(x) == 9952, uniqueN(x$recordID) == 997)
m <- function(v, from, to) { r <- to[match(v, from)]; stopifnot(!anyNA(r)); r }
d <- x[, .(id = as.integer(factor(recordID)), task = as.integer(task_num), profile = match(profile, c("A", "B")),
  choice = as.integer(chosen_dummy),
  attr_land = m(Tierras, paste0("land-", c("low", "medium", "high")), c("No transfer", "Small transfer", "Large transfer")),
  attr_elections = m(FARC_Elecciones, paste0("elections-", c("low", "medium", "high")), c("No electoral participation", "FARC competes", "FARC competes + seats")),
  attr_reintegration = m(Reinsercion, paste0("reinter-", c("low", "medium", "high")), c("No assistance", "90% min. wage for demobilized", "200% min. wage for demobilized")),
  attr_justice = m(Victimas_Justicia, paste0("justice-", c("low", "medium", "high")), c("No jail", "Jail for HR violators", "Jail for all FARC")),
  attr_reparation = m(Victimas_Reparacion, paste0("repar-", c("low", "medium", "high")), c("No reparations", "FARC ask forgiveness", "FARC pay victims")),
  attr_drug_policy = m(Estupefacientes_Politica, c("drug-air", "drug-manual", "drug-sub"), c("Aerial fumigation", "Manual eradication", "Substitution program")),
  cov_gender = c("male", "female")[woman + 1L], cov_age_group = as.character(age_factor), cov_stratum = as.character(nse),
  cov_referendum_vote = fifelse(vote_choice == "No responde", NA_character_, vote_choice))]
stopifnot(!anyNA(d$profile), d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "tellez_2021_peace_packages.csv"))
