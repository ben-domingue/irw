##Value-of-democracy societies conjoint (Brazil, France, US) from
##Adserà, A., Arenas, A., & Boix, C. (2023). Estimating the value of democracy relative to
##other institutional and economic outcomes among citizens in Brazil, France, and the United
##States. PNAS, 120(48), e2306168120. https://doi.org/10.1073/pnas.2306168120
##Replication data: Harvard Dataverse doi:10.7910/DVN/RTUFHH, CC0 1.0. File read:
##pnas_data_dataverse.dta (original Stata, read with encoding latin1). harvard_dataverse.do
##read as text only. Design from the article (Table 1, Materials and Methods) and SI
##Figs. S1-S2 (instructions and an example US screen).
##Usage: Rscript adsera_2023.R <dir holding pnas_data_dataverse.dta> <output dir>
##
##6,014 respondents (nicequest online panels; 2,001 Brazil, 2,003 France, 2,010 US), seven
##pairs of hypothetical societies each (`set` = task 1-7, `position` = profile 1/2, Society
##A left / B right; both recorded). The authors drop respondents with duration < 600
##(do-file L71); all are kept here with cov_duration (the deposit's `duration`, unit not
##documented, presumably seconds). After that filter the counts match the article's N
##exactly: Brazil 1,910 x 14 = 26,740, France 1,693 x 14 = 23,702, US 1,624 x 14 = 22,736.
##One table with cov_country: same six attributes, design and questions in all three
##countries, and the authors estimate pooled ("all") as well as by-country models.
##Outcomes (both asked of every pair; SI Fig. S2):
##  choice: "We ask you to choose which society you consider to be the best one for you;
##    that is, the society in which you will be most content." Forced choice, no opt-out
##    (exactly one chosen in every task).
##  rating: "We will also ask you to rate each society separately on a range from 0 (very
##    bad) to 10 (very good)". STORED RAW: the deposit's values run 1-10 (no 0, no 11);
##    the article and screen say 0-10, so whether 0 was merged into 1 or the scale was
##    recoded is not documented. Higher = better.
##Attribute text (English, as in the US screen of SI Fig. S2; respondents in Brazil and
##France saw Portuguese/French text that is not deposited, so the French and Brazilian
##rows carry the English wording with their own currency amounts). Amounts are rebuilt
##from the design: country average income R$3,000 (Brazil), EUR 3,000 (France), $6,000
##(US) (article); individual income = 1.25/1.1/1/0.9/0.8 x average, society income =
##1.5/1/0.8 x average (Table 1). The deposit codes atr1/atr2 1-5 / 1-3, but the code
##order is reversed in the US (its value labels show only the R$/EUR amounts); the
##script therefore ranks the deposit's PPP values (atr1_cont_ppp, atr2_cont_ppp) within
##country, which gives the multiplier unambiguously (5 and 3 distinct values per
##country). Inequality: equal_society = 1 -> max 2 x and min 0.5 x the society's average
##income, else 4 x and 0.25 x (article Table 1); displayed with the amounts, e.g. "The
##maximum income in the country is $19200 and the minimum $1200" (SI Fig. S2 format;
##R$/EUR formatting by analogy). The four binary attributes come as 0/1 dummies named in
##the do-file (democracy, public_health, effort, equal_society) and are mapped to the
##quoted texts of article Table 1 / SI Fig. S2. Restrictions: none documented; the 2x2
##democracy x equal_society table is mildly unbalanced (21,950 vs 20,148 rows), all
##combinations occur. The atr1 Stata label reads "Monthly income of [you / your
##grandchildren]": no grandchildren arm is identified in the deposit or the article.
##Covariates: cov_country, cov_age (years), cov_gender (`female` 1/0, authors' dummy),
##cov_right_wing (1-10), cov_pro_trade, cov_pro_immigration, cov_pro_tech (1-5),
##cov_wealth_parents, cov_wealth_household (0-10 ladders, value labels), cov_duration.
##Dropped: derived dummies (income_above, veryhigh_income, college, high_school, country
##dummies), standardized dark-triad indices and the `status` principal component, PPP
##income columns. No survey weight in the deposit. No PII (numericalid re-keyed).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "pnas_data_dataverse.dta"), encoding = "latin1")))
stopifnot(nrow(s) == 84196, uniqueN(s$numericalid) == 6014)
cur <- c(Brasil = "R$", Francia = "EUR ", USA = "$"); avg <- c(Brasil = 3000, Francia = 3000, USA = 6000)
s[, `:=`(m1 = c(0.8, 0.9, 1, 1.1, 1.25)[frank(atr1_cont_ppp, ties.method = "dense")],
         m2 = c(0.8, 1, 1.5)[frank(atr2_cont_ppp, ties.method = "dense")]), by = pais]
stopifnot(s[, .(uniqueN(atr1_cont_ppp), uniqueN(atr2_cont_ppp)), pais][, all(V1 == 5 & V2 == 3)])
s[, `:=`(c1 = cur[pais], A = avg[pais])]
money <- function(c, x) paste0(c, formatC(round(x), format = "d", big.mark = ","))
money0 <- function(c, x) paste0(c, round(x))
s[, inc := money(c1, m1 * A)][, ctry := money(c1, m2 * A)]
s[, ineq := fifelse(equal_society == 1,
      paste0("The maximum income in the country is ", money0(c1, 2 * m2 * A), " and the minimum ", money0(c1, 0.5 * m2 * A)),
      paste0("The maximum income in the country is ", money0(c1, 4 * m2 * A), " and the minimum ", money0(c1, 0.25 * m2 * A)))]
# check against the deposit's own labels (code 1 = 3.750 R$/EUR in Brazil and France)
stopifnot(s[pais != "USA" & atr1 == 1, all(m1 == 1.25)], s[pais != "USA" & atr2 == 1, all(m2 == 1.5)],
          s[pais == "USA" & atr1 == 1, all(m1 == 0.8)])
d <- s[, .(id = as.integer(frank(numericalid, ties.method = "dense")), task = as.integer(set), profile = as.integer(position),
           choice = as.integer(choice), rating = as.integer(rating),
           attr_income_you = inc, attr_income_society = ctry,
           attr_political_institutions = fifelse(democracy == 1, "People choose the national government through free elections",
                                                 "There are no free elections to choose the national government"),
           attr_health_system = fifelse(public_health == 1, "There is a public health system paid by an income tax",
                                        "Health is not covered by a public health system"),
           attr_getting_ahead = fifelse(effort == 1, "Effort is more important than personal connections to get ahead",
                                        "Personal connections matter more than effort to get ahead"),
           attr_inequality = ineq,
           cov_country = c(Brasil = "BR", Francia = "FR", USA = "US")[pais], cov_age = as.integer(age),
           cov_gender = fifelse(female == 1, "female", "male"),
           cov_right_wing = as.integer(pol_right_wing), cov_pro_trade = as.integer(pol_pro_trade),
           cov_pro_immigration = as.integer(pol_immig), cov_pro_tech = as.integer(pol_tech),
           cov_wealth_parents = as.integer(wealthy_parents), cov_wealth_household = as.integer(wealthy_hh),
           cov_duration = as.integer(duration))]
stopifnot(all(s$democracy %in% 0:1), all(s$public_health %in% 0:1), all(s$effort %in% 0:1), all(s$equal_society %in% 0:1),
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)], !anyNA(d$rating),
          d[, uniqueN(cov_country), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "adsera_2023_value_of_democracy.csv"))
