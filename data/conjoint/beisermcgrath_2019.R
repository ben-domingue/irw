##International climate-agreement (coal tax) conjoints, USA and China, from
##Beiser-McGrath, L. F., & Bernauer, T. (2019). Commitment failures are unlikely to undermine
##public support for the Paris agreement. Nature Climate Change, 9, 248-252.
##https://doi.org/10.1038/s41558-019-0414-z
##Replication data: Harvard Dataverse doi:10.7910/DVN/D1QMP5, CC0 1.0, no restricted files, no terms.
##Files read: replication_materials/data/usa_uncond_data.csv and chn_uncond_data.csv (inside
##replication_materials.zip); _readme.txt and code/*.R read as text, not run. Attribute wording,
##question, treatments: the article's Supplementary Information (41558_2019_414_MOESM1_ESM.pdf),
##Supplementary Table 1 (worded for the USA sample), Table 23 (China/USA wording), Figure 1.
##Usage: Rscript beisermcgrath_2019.R <dir holding the two csv files> <output dir>
##
##Two samples, two tables: USA (3,007 respondents) and China (3,000), as in the abstract. The
##authors model each country separately (main_analysis.R) and the attribute text differs (own
##country, currency), so the samples are not pooled. Each respondent saw 5 pairs (task = source
##`round`; profile 1 = Policy A on the left, 2 = Policy B, source `policy`) of a new tax on coal,
##6 attributes. Outcome `choice`: "Which of the two policies do you prefer?" (SI Table 1); the
##intro asks which one "the US government should choose". Forced choice: exactly one chosen per
##task in every task (checked). No rating.
##Before the conjoint each respondent was randomized to one of 6 information treatments on coal
##consumption (SI Figure 1), kept as trial_info_treatment (constant within respondent).
##Attribute text (USA): SI Table 1 verbatim, codes Attrib1-6 = the table's level numbers (the
##deposit's attrib*_lab columns, authors' short labels, agree one-to-one with the codes).
##Attribute text (China): the survey was fielded in Chinese and the Chinese grid is not deposited.
##Levels are the English wording of SI Table 1 with <COUNTRY> = China and RMB amounts, following
##SI Table 23 (which prints China levels such as "30RMB per year", "40RMB billion over ten years",
##"Decided by <COUNTRY> in consultation with other countries", "India (7.0% of total world carbon
##dioxide emissions)"); RMB amounts from the authors' labels ("$10/40RMB billion", "30 Dollar/RMB").
##In the China version, "China" in the partner attribute is replaced by the USA (authors' label
##"China/USA"); the share of world emissions printed with the USA levels is NOT documented, so the
##three USA levels are stored WITHOUT the percentage ("the USA, the European Union, and India",
##"the USA and India", "the USA"). The China table is therefore a translated reconstruction.
##Attribute order: numbered 1-6 in the SI table; whether the order was randomized is not stated
##(unknown). Restrictions: none documented. Level shares are visibly unequal (e.g. USA cost $200
##14% vs $100 18%; partner India 19% vs China 15%): level_weights observed for the USA table; China
##shares are near-equal (15.6-17.5%), unknown.
##Spot check: USA choice shares fall with cost ($30 0.69 ... $300 0.34) and favour the sanctioned
##agreement (0.55), matching SI Table 23 (US most popular: $30, sanctions, joint decision, China+EU+India).
##China: the most popular profile in SI Table 23 (informal agreement, India) is NOT the top level by
##marginal choice share (sanctions 0.57, informal 0.44; that table comes from an interaction model,
##number1.R); not resolvable from the deposit.
##Covariates: cov_gender (resp_gender text), cov_age (resp_age, years), and codes with no labels in
##the deposit: cov_education_code (Q43), cov_income_code (Q40; 17 USA / 14 China = no income given,
##balance.R), cov_party_id_code (Q44, USA only; 8 = not sure, balance.R), cov_climate_serious_code
##(Q23, "climate change is serious", SI Table 9). Employment indicators ftime/ptime/unem/retir are
##kept (cov_emp_fulltime, cov_emp_parttime, cov_emp_unemployed, cov_emp_retired: the only
##employment data). Comprehension checks: cov_comprehension_own / cov_comprehension_other (pass_own,
##pass_oth; pass = both is dropped as derived). The authors' treat1-5/control dummies are dropped.
##No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]

partners_us <- c("China, the European Union, and India (42.6% of total world carbon dioxide emissions)",
                 "China and India (32.4% of total world carbon dioxide emissions)",
                 "China (25.4% of total world carbon dioxide emissions)",
                 "European Union (10.2% of total world carbon dioxide emissions)",
                 "India (7.0% of total world carbon dioxide emissions)",
                 "No other countries with large carbon dioxide emissions")
partners_cn <- c("the USA, the European Union, and India", "the USA and India", "the USA",
                 partners_us[4:6])
lev <- function(cn) {
  C <- if (cn) "China" else "the U.S."; cur <- function(x) if (cn) paste0(x, "RMB") else paste0("$", x)
  list(cost = paste(cur(c(30, 100, 150, 200, 250, 300)), "per year"),
       agreement = c("A legally binding international agreement with sanctions on countries that don't comply",
                     "A legally binding international agreement, without sanctions on countries that don't comply",
                     "An informal, that is, legally non-binding international agreement",
                     paste("An effort undertaken by", C, "on its own")),
       tax_decision = c(paste("Decided by", C, "on its own"), paste("Decided by", C, "in consultation with other countries"),
                        "Decided jointly by the world's large coal consumption countries"),
       partners = if (cn) partners_cn else partners_us,
       n_countries = c("20", "80", "150", "190"),
       compensation = c(paste(cur(if (cn) c(120, 80, 40) else c(30, 20, 10)), "billion over ten years"), "No support"))
}
treat_us <- c("No information", "USA decreased coal use, China increased", "USA decreased coal use, UK increased",
              "USA decreased coal use, other countries increased", "USA decreased coal use, other countries decreased",
              "USA decreased coal use (USA only)")
treat_cn <- c("No information", "China increased coal use, USA decreased", "China increased coal use, UK increased",
              "China increased coal use, other countries increased", "China increased coal use, other countries decreased",
              "China increased coal use (China only)")
build <- function(f, cn, name) {
  s <- fread(file.path(raw, f))
  stopifnot(s[, .N, respid][, all(N == 10)], all(s$policy %in% c("A", "B")))
  L <- lev(cn); nm <- names(L)
  ## authors' labels must agree with the codes (label number order differs from code order for some attributes)
  labchk <- list(c(1:6), c(4, 3, 2, 1), c(1:3), c(6, 5, 4, 3, 2, 1), c(1:4), c(4, 3, 2, 1))
  for (i in 1:6) stopifnot(s[, all(as.integer(sub("\\).*", "", get(paste0("attrib", i, "_lab")))) == labchk[[i]][get(paste0("Attrib", i))])])
  d <- s[, .(id = as.integer(respid), task = as.integer(round), profile = fifelse(policy == "A", 1L, 2L), choice = as.integer(choice))]
  for (i in 1:6) d[, paste0("attr_", nm[i]) := L[[i]][s[[paste0("Attrib", i)]]]]
  d[, trial_info_treatment := (if (cn) treat_cn else treat_us)[s$treatment + 1L]]
  stopifnot(all(s$resp_gender %in% c("female", "male")))
  d[, `:=`(cov_gender = s$resp_gender, cov_age = as.integer(s$resp_age), cov_education_code = as.integer(s$Q43),
           cov_income_code = as.integer(s$Q40))]
  if (!cn) d[, cov_party_id_code := as.integer(s$Q44)]
  d[, `:=`(cov_climate_serious_code = as.integer(s$Q23), cov_emp_fulltime = as.integer(s$ftime), cov_emp_parttime = as.integer(s$ptime),
           cov_emp_unemployed = as.integer(s$unem), cov_emp_retired = as.integer(s$retir),
           cov_comprehension_own = as.integer(s$pass_own), cov_comprehension_other = as.integer(s$pass_oth))]
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
}
build("usa_uncond_data.csv", FALSE, "beisermcgrath_2019_paris_us")
build("chn_uncond_data.csv", TRUE, "beisermcgrath_2019_paris_cn")
