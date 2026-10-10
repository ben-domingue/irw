##Tax-reform conjoint among business elites and nonelites (China) from
##Kao, J. C., Lü, X., & Queralt, D. (2024). Do gains in political representation sweeten tax
##reform in China? It depends on who you ask. Political Science Research and Methods, 12(1),
##146-165. https://doi.org/10.1017/psrm.2022.58
##Replication data: Harvard Dataverse doi:10.7910/DVN/TKEWPJ, CC0 1.0, no restricted files.
##File read: china_ntwr.dta (Dataverse "original format" download of china_ntwr.tab). Level text
##is the .dta value labels; design facts from the article (SSI online surveys, fall 2017; six
##paired comparisons; attribute values and order randomized; level translations in its Appendix
##D, not read) and replication_master.do / log_file.txt (read as text, not run).
##Usage: Rscript kao_2024.R <raw dir> <output dir>
##
##Online respondents in China recruited through SSI (fall 2017): 349 business elites and 755
##nonelites in the file (source elite_1, "Elite definition by source of survey"). Each compared
##six pairs (task 1-6, profile 1-2, both recorded) of tax-reform proposals and chose the one
##they preferred (choice = selected_2; exactly one chosen per task; the article describes no
##neither option; exact wording not in the deposit or article text: "requested to choose which
##is most preferred", paraphrase).
##Attributes (value labels): attr_tax_type (Income Tax / VAT), attr_tax_rate (1% / 5% / 10% / 15%
##/ 20%), attr_government_services ("Fiscal contract through increase spending": No Change /
##Defense / Edu., Health, & Pension / Environment / Infrastructure), attr_political_influence
##("NTWR through providing": No Change / Citizen Input / Fiscal Transparency / Election /
##Property Rights). These are the authors' short English labels; respondents saw Chinese text
##(the article refers to a translation of the attribute values). Attribute order was randomized
##(article) and is not recorded.
##Sample: 57 respondents with no recorded choice (selected_2 missing on every task) are omitted,
##leaving 1,047. The article's analyses use the 536 respondents (272 elites, 264 nonelites) who
##pass its screening, i.e. those with cov_elite_t10 non-missing (1 = business elite at a top-10%
##firm, 0 = nonelite); 532 of them have choices here (as in log_file.txt: 270 elite clusters).
##Respondents outside the screened sample are kept with cov_elite_t10 = NA.
##Covariates (value labels -> text where labelled): cov_age (years), cov_gender (male 1/0 ->
##male/female), cov_education (No School .. PhD), cov_ccp_member (0/1), cov_married (0/1),
##cov_household_income (monthly, bracket label), cov_sector (employment sector label),
##cov_money_today ("Do you prefer receiving $100 now or $200 one year from today?": label text),
##cov_vat_burden (label text), cov_tax_bargain (label text: "Does not matter as long as high
##quality public spending" / "Some says in policy making"), cov_years_paying_tax (label text),
##cov_elite_source (elite_1), cov_elite_t10 / cov_elite_t5 / cov_elite_t1 (business elites at
##the top 10% / 5% / 1% of firm size), cov_trust_gov (0/1, "Trust in government"). Dropped: the
##hashed panel id psid (re-keyed to integers), the authors' derived dummies (satisfaction and
##awareness dummies, low_discount). No survey weight.
##NOT BUILT: taiwan_ntwr.dta (the article's "shadow case", 824 respondents) has no task or profile
##columns and its row order does not pair profiles (consecutive rows within a respondent give
##exactly one choice no more often than random pairing does), so tasks cannot be rebuilt.
##Restrictions: none documented; all 250 level combinations occur.
##Spot check: OLS of choice on the attribute dummies among elites (cov_elite_t10 = 1) gives
##Citizen Input 0.155, Edu., Health, & Pension 0.289, 20% -0.231 on 3,240 rows, as in
##log_file.txt (Figure 2).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "china_ntwr.dta")))
stopifnot(k[, .N, psid][, all(N == 12)], !anyDuplicated(k[, .(psid, task, profile)]))
k <- k[k[, .(ok = !all(is.na(selected_2))), psid], on = "psid"][ok == TRUE]
stopifnot(!anyNA(k$selected_2), k[, sum(selected_2), .(psid, task)][, all(V1 == 1)])
lab <- function(x) as.character(as_factor(x, levels = "labels"))
d <- data.table(id = as.integer(factor(k$psid, levels = unique(k$psid))), task = as.integer(k$task),
                profile = as.integer(k$profile), choice = as.integer(k$selected_2),
                attr_tax_type = lab(k$tax), attr_tax_rate = lab(k$rate),
                attr_government_services = lab(k$pub_goods_services), attr_political_influence = lab(k$representation))
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), !any(grepl("^[0-9]+$", d[[v]])))
stopifnot(all(k$male %in% c(0, 1, NA)))
d[, `:=`(cov_age = as.integer(k$age), cov_gender = fifelse(k$male == 1, "male", "female"),
         cov_education = lab(k$edu), cov_ccp_member = as.integer(k$ccp), cov_married = as.integer(k$married),
         cov_household_income = lab(k$income_cat), cov_sector = lab(k$sector), cov_money_today = lab(k$money_today),
         cov_vat_burden = lab(k$vat_burden), cov_tax_bargain = lab(k$tax_bargain), cov_years_paying_tax = lab(k$year_paying_tax),
         cov_elite_source = as.integer(k$elite_1), cov_elite_t10 = as.integer(k$elite_t10), cov_elite_t5 = as.integer(k$elite_t5),
         cov_elite_t1 = as.integer(k$elite_t1), cov_trust_gov = as.integer(k$trust_gov))]
stopifnot(d[, .N, .(attr_tax_type, attr_tax_rate, attr_government_services, attr_political_influence)][, .N] == 250)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kao_2024_tax_reform.csv"))
