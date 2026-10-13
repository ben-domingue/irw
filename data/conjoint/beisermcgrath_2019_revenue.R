##Carbon-tax conjoint with randomized revenue-recycling information, USA and Germany, from
##Beiser-McGrath, L. F., & Bernauer, T. (2019). Could revenue recycling make effective carbon
##taxation politically feasible? Science Advances, 5(9), eaax3323.
##https://doi.org/10.1126/sciadv.aax3323
##Replication data: Zenodo doi:10.5281/zenodo.18144631 (concept DOI; also listed as
##10.5281/zenodo.18144632), CC BY 4.0. Files read: df_usa.csv, df_deu.csv; _readme.txt and
##main_analysis.R read as text, not run. The location files (state, place size) are not used.
##Wording and attribute definitions: the published article (Table 1, Materials and Methods).
##This is a different experiment from beisermcgrath_2019_paris_us/_cn (Nature Climate Change,
##Harvard doi:10.7910/DVN/D1QMP5): different attributes (cost, import/export exemptions,
##other countries, revenue use) and different samples.
##Usage: Rscript beisermcgrath_2019_revenue.R <dir holding the two csv files> <output dir>
##
##Two tables, one per country, because the authors estimated every model separately by country
##and the "other countries" attribute differs in text (the Germany file has the level
##"USA/Germany", the US file has no such level; it is stored as in the file).
##Ipsos online quota panels (age, sex, income, region), Feb 2018: US 3,640 and Germany 3,620
##respondents, as in the paper (n = 3640 / 3620; 36,400 / 36,200 hypothetical taxes).
##Each respondent: 5 tasks (round) x 2 proposals (policy A/B), ID is already an Ipsos-independent
##code of the form U1001161066 / C1676223048; it is re-keyed to integers.
##Outcomes:
##  choice = the proposal the respondent preferred (forced choice, exactly one per task, no opt-out)
##  rating = support for each proposed carbon tax on a 1-7 Likert scale (paper: "noted their level
##           of support for each proposed carbon tax on a Likert scale of 1 to 7"; 5-7 = supportive,
##           1-3 = oppositional). Exact wording and anchors are not in the deposit or article:
##           paraphrase; 7 = most supportive is inferred from that coding.
##Attributes (paper Table 1): tax ($10..$70 per metric ton, in 7 steps), foreign_firm (energy-
##intensive imports: fully exempt / half / full tax), domestic_firm (exporters: same three),
##oth_countries (similar tax introduced by other countries), revenue (use of revenue: 8 levels).
##The revenue attribute was randomly shown to half of the respondents (rev_treat = 1); for the
##others it is coded "(not shown)". rev_treat is kept as trial_revenue_shown (constant per respondent).
##Dropped: nothing else (the files contain only these variables). No survey weight. No PII.
##Randomization restrictions: none documented. Levels: tax and others near-uniform in the data.
##Attribute order: not documented.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
one <- function(f, name) {
  k <- fread(file.path(raw, f), na.strings = "NULL_NEVER")
  d <- data.table(id = match(k$ID, unique(k$ID)), task = as.integer(k$round),
                  profile = match(k$policy, c("A", "B")), choice = as.integer(k$choice), rating = as.integer(k$rate))
  d[, attr_tax := k$tax]
  d[, attr_foreign_firm := k$foreign_firm]
  d[, attr_domestic_firm := k$domestic_firm]
  d[, attr_oth_countries := k$oth_countries]
  d[, attr_revenue := ifelse(k$revenue == "NA" | is.na(k$revenue), "(not shown)", k$revenue)]
  d[, trial_revenue_shown := as.integer(k$rev_treat)]
  stopifnot(!anyNA(d), d[, uniqueN(trial_revenue_shown), id][, all(V1 == 1)],
            d[, sum(choice), .(id, task)][, all(V1 == 1)],
            d[trial_revenue_shown == 1, !any(attr_revenue == "(not shown)")],
            d[trial_revenue_shown == 0, all(attr_revenue == "(not shown)")])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, name))
  cat(name, nrow(d), uniqueN(d$id), "\n")
}
one("df_usa.csv", "beisermcgrath_2019_revenue_us.csv")
one("df_deu.csv", "beisermcgrath_2019_revenue_de.csv")
