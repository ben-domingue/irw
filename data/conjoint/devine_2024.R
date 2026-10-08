##Climate-policy proposal conjoint (Germany) from
##Devine, D., Stoker, G., & Jennings, W. (2024). Political trust and climate policy choice:
##Evidence from a conjoint experiment. Journal of Public Policy, 44(2), 327-343.
##https://doi.org/10.1017/S0143814X23000430
##Replication data: Harvard Dataverse doi:10.7910/DVN/NC5FMP, CC0 1.0, no restricted files.
##File read: data/replication_dat.dta (inside replication.zip). Design from the article (CC BY),
##pp. 333-334 and Table 1; the appendix with the full survey wording could not be retrieved.
##Usage: Rscript devine_2024.R <raw dir> <output dir>
##
##1,558 YouGov respondents in Germany (two waves, 14-20 Oct and 19-23 Nov 2021; no wave
##variable is deposited), 4 tasks (the source's screens 1-4, outcome QC2b_a..d) of two
##government climate proposals ("Proposal A" = profile 1, "Proposal B" = profile 2), 7
##attributes. Respondents saw German; the deposit carries only the English master-instrument
##value labels, so attr_ text is English (label_language en):
##  full English instrument text (value labels): attr_policy (level 4 is cut at 80 characters in
##    the .dta and completed from article Table 1: "...like electricity and plastic"),
##    attr_timing ("Acting now instead of later will avoid higher costs in 10/20/30 years' time"),
##    attr_complexity ("Experts agree that implementing the proposals would be very / fairly /
##    not very complicated"), attr_public_support ("60% support, 40% oppose", ...);
##  article Table 1 labels (the .dta labels are cut at 80 characters and cannot be completed):
##    attr_pricing ("Tax for the environment" / "Tax for the environment, other taxes reduced" /
##    "Tax on things that pollute, like petrol or electricity"), attr_gdp ("1% of GDP", "2% of
##    GDP", "1% of GDP, but reduce public health costs", "1% of GDP, but costs would be higher
##    for future generations", "GDP would increase by 1%"), attr_recommended_by ("Made by
##    government, backed by opposition", "Made by government, opposition in parliament", "Made
##    by expert panel", "Made by random members of public"); code-to-label mapping from the
##    authors' rep_code.R, checked against the .dta labels' first 80 characters.
##choice: "Which proposal would you prefer to be implemented?" (Proposal A / Proposal B; "There was
##  no Don't Know option or equivalent").
##Attribute order was randomized between respondents and held constant over tasks (article);
##  C2b_attr_order lists the attribute numbers in display order (policy always first), stored as
##  attrpos_<attr> (row position 1-7; the reading of the list as display order is inferred from
##  the variable label "Attribute order"). Randomization restrictions are not documented.
##Covariates (value-label text as deposited, English or German): cov_trust (SQG1, how often one
##  can trust the government, German), cov_climate_importance (SQ11_1, "Tackling climate
##  change", 0-10), cov_trust_climate (SQ12_1, trust on tackling climate change, 0-10),
##  cov_climate_myth (SQ16_2), cov_scientists_panic (SQ16_3), cov_worried_effects (SQ7_4, "The
##  effects of climate change"), cov_left_right (SQ30x_1, 1-10; code 997, unlabelled, set to NA),
##  cov_vote_2021 (DE_q_BTW21_Quote). Respondent IDs re-keyed to integers. No survey weight.
##N = 1,558 and 6,232 tasks match the article; the authors' Table A4 level counts reproduce.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- read_dta(file.path(raw, "replication_dat.dta"))
lab <- function(v) { l <- attr(v, "labels"); names(l)[match(as.numeric(v), l)] }
tbl1 <- list(attribut3 = c("Tax for the environment", "Tax for the environment, other taxes reduced",
                           "Tax on things that pollute, like petrol or electricity"),
             attribut5 = c("1% of GDP", "2% of GDP", "1% of GDP, but reduce public health costs",
                           "1% of GDP, but costs would be higher for future generations", "GDP would increase by 1%"),
             attribut6 = c("Made by government, backed by opposition", "Made by government, opposition in parliament",
                           "Made by expert panel", "Made by random members of public"))
an <- c(attribut1 = "policy", attribut2 = "timing", attribut3 = "pricing", attribut4 = "complexity", attribut5 = "gdp",
        attribut6 = "recommended_by", attribut7 = "public_support")
ord <- do.call(rbind, strsplit(gsub("\\[|\\]| ", "", x$C2b_attr_order), ","))
stopifnot(ncol(ord) == 7, apply(ord, 1, function(r) setequal(r, as.character(1:7))))
rows <- list()
for (t in 1:4) for (p in 1:2) {
  q <- as.numeric(x[[paste0("QC2b_", letters[t])]]); stopifnot(all(q %in% 1:2))
  d <- data.table(id = seq_len(nrow(x)), task = t, profile = p, choice = as.integer(q == p))
  for (k in names(an)) {
    v <- x[[sprintf("C2b_src_%d_%s_%d", t, k, p)]]; stopifnot(all(as.numeric(v) %in% 1:5))
    d[, paste0("attr_", an[[k]]) := if (k %in% names(tbl1)) tbl1[[k]][as.numeric(v)] else lab(v)]
  }
  for (j in 1:7) d[, paste0("attrpos_", an[[j]]) := apply(ord, 1, function(r) match(as.character(j), r))]
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows)
d[attr_policy == "Increasing the price of things that produce carbon to make, like electricity and",
  attr_policy := "Increasing the price of things that produce carbon to make, like electricity and plastic"]
# no level left unmapped
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr")]))
cv <- c(trust = "SQG1", climate_importance = "SQ11_1", trust_climate = "SQ12_1", climate_myth = "SQ16_2",
        scientists_panic = "SQ16_3", worried_effects = "SQ7_4", vote_2021 = "DE_q_BTW21_Quote")
cvd <- data.table(id = seq_len(nrow(x)))
for (v in names(cv)) cvd[, paste0("cov_", v) := lab(x[[cv[[v]]]])]
lr <- as.integer(x$SQ30x_1); cvd[, cov_left_right := fifelse(lr %in% 1:10, lr, NA_integer_)]
d <- merge(d, cvd, by = "id")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], nrow(d) == 12464L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "devine_2024_climate_policy.csv"))
