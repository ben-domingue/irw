##European Defense Union conjoint (France, Germany, Italy, Netherlands, Spain) from
##Nicoli, F., Burgoon, B., & van der Duin, D. (2025). Citizen support for a European Defense
##Union: An international conjoint experiment on security cooperation in Europe.
##International Studies Quarterly, 69(3), sqaf044. https://doi.org/10.1093/isq/sqaf044
##Replication data: Harvard Dataverse doi:10.7910/DVN/HTAPIS, CC0 1.0. File read:
##replication dataset APPENDIX final.dta (Dataverse "original format" download). Also
##inspected: replication dataset.dta. Read as text: replication dofile.do, appendix dofile.do.
##Attribute text, scales and design from the article (OUP HTML, read via a summarising fetch).
##Usage: Rscript nicoli_2025.R <dir holding appendix.dta> <output dir>
##(the script expects the APPENDIX .dta saved as appendix.dta)
##
##IPSOS opt-in panels, November 2022, five countries. Respondents were split 50/50 between
##this military-security experiment (Conjoint_2_framing = 1 "Military" in the main file) and
##an "energy security experiment". The APPENDIX file holds the military half only: 3,839
##respondents x 3 pairs x 2 packages = 23,034 rows; the article reports 750 per country
##(3,750). 2,893 passed the attention check (cov_attention_pass), the authors' main sample.
##The energy-security arm (3,839 respondents, main file only, same numeric codes d1-d6) is NOT
##built: its displayed attribute text is not in the deposit or the article, and the main file
##keeps only a collapsed version of its rating.
##One table pooling the five countries (cov_country), as the authors pool them (Figure 1,
##pooled models) and the attributes are the same in every country.
##Attributes (6): the article's Table 1 English text, mapped from the authors' Stata labels
##(d1 programme level national/European; d2 flat tax / progressive tax / Eurobonds /
##repurposing; d3 intergovernmental / confederal / federal governance; d4 no opt-outs / opt-outs;
##d5 joint EU / national procurement; d6 small / large size). Respondents saw national-language
##versions (the article says the framing text is "in different languages"; not deposited), so
##the stored text is the English master. "50.000" in the article is written 50,000.
##Attribute order was randomized per respondent and held across pairs (article); not recorded.
##task = pair (1-3); profile = package order within the pair (odd package = 1, firstpack = 1).
##Outcomes (wording paraphrased in the article, not quoted):
##  choice = binary_dv, which of the two packages on the screen the respondent preferred;
##    forced choice (exactly one chosen per pair, checked).
##  rating = conjointcat2, each package on a 5-point scale: 1 strongly against, 2 somewhat
##    against, 3 neutral, 4 somewhat in favor, 5 strongly in favor (the authors' support_type
##    collapses 1-2 / 3 / 4-5 to -1/0/1, which fixes the direction). Higher = more favourable.
##Covariates: cov_country (text), cov_survey_weight (Weight_Country), cov_age (age_year),
##cov_education3 (Education_R2: 1 Low, 2 Middle, 3 High; the authors' recode, the only
##education measure deposited; codes kept, not the reserved cov_education), cov_attention_pass
##(AttentionCheck, .dta label "Recode attention check: pass or fail", 0 = Fail, 1 = Pass).
##Dropped: income_class (no labels), support_type, supportB1, supportB3, firstpack,
##total_opposition, d*_pairval (the other package's levels), the _est_* estimation flags.
##Randomization: independent uniform draws per dimension (article); level shares uniform.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "appendix.dta")))
stopifnot(nrow(s) == 23034, uniqueN(s$Serial) == 3839, s[, .N, Serial][, all(N == 6)])
lv <- list(
  d1 = c("Jointly finance the improvement of the national armed forces of the member states, each separately",
         "Put together some parts of national armed forces, into a novel European army"),
  d2 = c("By increasing taxes by 0.5 percent, for everyone in the EU", "By increasing taxes by 1 percent, only for the rich in the EU",
         "By increasing EU public debt, to be repaid in the future", "By reallocating national spending on national armed forces"),
  d3 = c("All countries must agree, i.e., one country can block any decision on its own",
         "A majority of countries must agree: no country can block a decision on its own",
         "Both the majority of countries and a majority of members of the European Parliament must agree"),
  d4 = c("No: all countries must participate if this is the common decision", "Yes: a country can always refuse to participate if it so wishes"),
  d5 = c("Yes: the EU countries procure and jointly purchase common military equipment",
         "No: every country procures and purchases military equipment on its own"),
  d6 = c("Enough to support a small unit: about 5,000 servicemen and their equipment",
         "Enough to support a large force: about 50,000 servicemen and their equipment"))
stopifnot(identical(names(attr(s$d2, "labels")), c("flat tax increase", "progressive tax increase", "Eurobonds", "repurposing")),
          identical(names(attr(s$d3, "labels")), c("intergovernmental governance", "confederal governance", "federal governance")),
          identical(names(attr(s$d4, "labels"))[1], "no optouts allowed"), identical(names(attr(s$d5, "labels"))[1], "joint EU procurement"),
          identical(names(attr(s$d6, "labels"))[1], "small size"), identical(names(attr(s$d1, "labels"))[1], "programme level: national"))
nm <- c(d1 = "programme", d2 = "financing", d3 = "governance", d4 = "opt_outs", d5 = "joint_purchases", d6 = "size")
d <- s[, .(id = as.integer(Serial), task = as.integer(pair), profile = 2L - as.integer(package) %% 2L,
           choice = as.integer(binary_dv), rating = as.integer(conjointcat2))]
for (v in names(nm)) d[, paste0("attr_", nm[[v]]) := lv[[v]][as.integer(zap_labels(s[[v]]))]]
d[, `:=`(cov_country = as.character(as_factor(s$Country)), cov_survey_weight = as.numeric(s$Weight_Country),
         cov_age = as.integer(s$age_year), cov_education3 = as.integer(zap_labels(s$Education_R2)),
         cov_attention_pass = as.integer(zap_labels(s$AttentionCheck)))]
stopifnot(identical(as.integer(s$firstpack), as.integer(d$profile == 1L)), d[, .N, .(id, task)][, all(N == 2)],
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, all(rating %in% 1:5)],
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          all(sign(d$rating - 3L) == s$support_type))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "nicoli_2025_defense_union.csv"))
