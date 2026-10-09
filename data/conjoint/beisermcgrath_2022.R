##Vehicle-pollution policy-bundle conjoint (New Delhi, November-December 2017) from
##Beiser-McGrath, L. F., Bernauer, T., & Prakash, A. (2022). Command and control or market-based
##instruments? Public support for policies to address vehicular pollution in Beijing and New Delhi.
##Environmental Politics, 32(4), 586-618. https://doi.org/10.1080/09644016.2022.2113608
##Replication data: Harvard Dataverse doi:10.7910/DVN/JVDNTD, CC0 1.0, no restricted files. File read:
##replication_data/data/df_conj_comb.csv (inside replication_data.zip); code/analysis.R read as text,
##not run. Wording, level text and design from the accepted version of the article (LSE Research
##Online eprint 116936): Data collection section, Table 1 ("wording for experiment in Delhi") and
##Appendix A1 (conjoint text).
##Usage: Rscript beisermcgrath_2022.R <dir holding df_conj_comb.csv> <output dir>
##
##Ipsos online quota samples, two waves (16-26 Nov and 4-10 Dec 2017), 750 respondents per wave per
##city by the article. The deposit has 1,501 New Delhi respondents (751 in wave 1, 750 in wave 2;
##the extra one is not explained) and 1,500 in Beijing. ONLY New Delhi is built here: the authors
##analyse the two cities separately (analysis.R fits every model per city), and the article gives
##the displayed text for Delhi only. Beijing's screen text (Chinese, with yuan amounts in place of
##"30 Rs." and "200,000Rs") is not deposited or published; the data hold only the authors' short
##labels ("2) 30R Tax") for both cities, so Beijing is held (labels).
##5 tasks x 2 policy bundles ("Policy A/B"), 4 attributes, all shown in every task. Outcomes:
##  choice = choice, "Which of the two policies should the government adopt and implement?" (forced
##           choice, no opt-out; exactly one per task, checked).
##  rating = rating, "Please rate the two policy measures on a scale from 1 to 7, where 1 indicates
##           that you "strongly oppose" and 7 indicates that you "strongly support" the policy
##           measure." Stored 1-7 as in the source, 7 = strongly support.
##task = round (recorded). profile is NOT recorded: it is the row order within each task (2 rows per
##respondent x round, rows never sorted by outcome: the first row is chosen in 56% of Delhi tasks),
##so profile 1 = Policy A is an inference.
##Attribute text: the deposit stores the authors' short labels "1) No Tax", "2) 30R Tax", ...; their
##leading number is the level number of Table 1 / Appendix A1, and each is written out with that
##level's text (e.g. "4) VOP for scotters" = level (4) "Permit costing 50,000Rs for motorcycles/
##scooters required, but no permit required for cars"). Text kept as printed in the article,
##including its "200,00Rs" (VOP level 3) and "cycles/scooters" (prohibition level 3) typos; the
##screen may differ. Attribute order: "SECTION ORDER [RANDOMIZED ONCE BETWEEN RESPONDENTS AND KEEP IT
##FIXED 5 TIMES]" (A1), not recorded. Levels: "each instrument is randomly assigned a specific level
##of stringency"; no restriction is stated; level shares run 23-27%.
##Covariates: trial_wave (survey, Wave 1/2: fielded two weeks apart, pooled by the authors),
##cov_gender from female (1 = female, 0 = male; the authors' variable name), cov_age (years),
##cov_owncar (1 = "Car Owner", per owncar_lab), cov_gov_perf (1-5, government performance in dealing
##with the city's challenges; the scale's end labels are not deposited), cov_educ_code and
##cov_income_code (codes 1-8 / 1-12; no codebook maps them). Dropped: date, city/city_f, survey,
##owncar_lab and gov_perf3 (derived). Ipsos IDs (C + 10 digits) are re-keyed to integers.
##No survey weight in the deposit.
##From this table the article's Table A1 Delhi choice AMCEs (lm, clustered SEs) reproduce.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "df_conj_comb.csv"))
stopifnot(nrow(s) == 30010L, uniqueN(s$ID) == 3001L)
s <- s[city == "Delhi"]
stopifnot(nrow(s) == 15010L, uniqueN(s$ID) == 1501L, s[, .N, .(ID, round)][, all(N == 2L)])
lv <- list(
  fuel_tax = c("No additional tax", "30 Rs. additional tax per litre",
               "30 Rs. additional tax per litre, tax income used to make metro and bus services cheaper",
               "30 Rs. additional tax per litre, tax income used to make hybrid and electric vehicles cheaper"),
  odd_even = c("No such restrictions/no odd-even rule", "Restrictions (odd-even rule) applied permanently (all year)",
               "Restrictions (odd-even rule) applied from November to February",
               "Restrictions (odd-even rule) applied whenever the local forecast predicts at least three consecutive days of high air pollution"),
  vehicle_ban = c("No such prohibition/motor vehicles older than 10 years allowed",
                  "Prohibition of cars and motorcycles/scooters older than 10 years",
                  "Prohibition of cars older than 10 years, but no such prohibition of cycles/scooters",
                  "Prohibition of motorcycles/scooters older than 10 years, but no such prohibition of cars"),
  vop = c("No permit required", "Permit required, costing 200,000Rs for cars and 50,000Rs motorcycles/scooters",
          "Permit costing 200,00Rs for cars required, but no permit required for motorcycles/scooters",
          "Permit costing 50,000Rs for motorcycles/scooters required, but no permit required for cars"))
short <- list(fuel_tax = c("No Tax", "30R Tax", "30R Tax + Pub Trans Subsidy", "30R Tax + Elec Cars Subsidy"),
              odd_even = c("No Odd-Even", "Permanent Odd-Even", "From Nov to Feb", "When Severe Air Pollution"),
              vehicle_ban = c("No Ban", "Vehicles > 10 Years", "Cars > 10 Years", "Scooters > 10 Years"),
              vop = c("No VOP", "VOP for vehicles", "VOP for cars", "VOP for scotters"))
s[, key := as.integer(factor(ID, levels = unique(ID)))]
s[, profile := seq_len(.N), .(ID, round)]
d <- s[, .(id = key, task = as.integer(round), profile, choice = as.integer(choice), rating = as.integer(rating))]
for (v in names(lv)) {
  code <- as.integer(sub("\\).*", "", s[[v]]))
  stopifnot(all(s[[v]] == paste0(code, ") ", short[[v]][code])))   # authors' label <-> level number
  d[, paste0("attr_", v) := lv[[v]][code]]
}
d[, trial_wave := s$survey]
d[, cov_gender := fifelse(s$female == 1L, "female", fifelse(s$female == 0L, "male", NA_character_))]
d[, cov_age := as.integer(s$age)][, cov_owncar := as.integer(s$owncar)][, cov_gov_perf := as.integer(s$gov_perf)]
d[, cov_educ_code := as.integer(s$educ)][, cov_income_code := as.integer(s$income)]
stopifnot(all((s$owncar_lab == "Car Owner") == (s$owncar == 1L)))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^trial_")]), d[, sum(choice), .(id, task)][, all(V1 == 1)],
          all(d$rating %in% 1:7), d[, uniqueN(cov_age), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "beisermcgrath_2022_vehicle_delhi.csv"))
