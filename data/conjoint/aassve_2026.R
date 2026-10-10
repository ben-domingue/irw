##Fertility-intention conjoint (four countries) from
##Aassve, A., et al. (2026). Parenthood decisions in uncertain times: Experimental evidence
##from four countries. Proceedings of the National Academy of Sciences, 123.
##https://doi.org/10.1073/pnas.2601690123
##Replication data: Harvard Dataverse doi:10.7910/DVN/WTKEE6, CC0 1.0, no restricted files,
##no terms. File read: replication_data_min.dta (Dataverse "original format" download of
##replication_data_min.tab). Level text = the .dta value labels (the authors' short labels;
##the wording respondents saw is not deposited). parenthoodinuncertaintimes_replication.do
##read as text for the design (run = task, conjoint = side).
##Usage: Rscript aassve_2026.R <raw dir> <output dir>
##
##8,330 adults aged 20-44 (online, May 2025 per the Bocconi press release; the release says
##8,334) in Argentina 2,096, Germany 2,090, Italy 2,069 and the United States 2,075. Each saw
##5 pairs (task = `run`, "order of the conjoint table (1-5)") of hypothetical couple scenarios
##(profile = `conjoint`, "side of the conjoint table (1 or 2)"), 10 attributes:
##attr_woman_age (26/32/38 years old), attr_children (No children / 1 child), attr_home
##(Owner / Renting), attr_work_housework (Egalitarian / Double-burden / Traditional),
##attr_childcare (No Public Childcare / Part-time Childcare / Full-time Childcare),
##attr_income (household monthly income "as shown in conjoint table", local currency, five
##levels per country: AR 500/800/1200/1700/2300, DE 1700/2300/3100/4200/5500, IT 1200/1600/
##2200/3000/4000, US 1770/3400/5600/8500/11000 = the authors' Much lower .. Much higher),
##attr_climate, attr_economy, attr_politics, attr_war (macro outlook Optimistic / Pessimistic).
##ONE TABLE with cov_country: the authors pool the four countries (country fixed effects)
##and the attribute labels are common; income amounts are in each country's currency.
##Outcomes (wording not deposited; paraphrase from the .dta labels and the press release):
##  choice = conjointchoice, "Outcome: forced choice" (which scenario would make the
##    respondent more inclined to have a child), one per task, no opt-out; 399 tasks have no choice (NA on
##    both profiles) but a rating.
##  rating = "Outcome: rating (1-10)", intention to have a child in the next three years
##    (the respondent's own) under each scenario, 1-10 (direction assumed: higher = more likely; the authors read
##    positive coefficients as higher intention). Profiles with neither outcome are omitted.
##Levels are balanced (each ~1/2 or 1/3; all Parity x Age and Work x Policy cells occur).
##Covariates: cov_country; cov_gender (female 1/0, "Respondent characteristics: if female");
##cov_age (years); cov_tertiary_self, cov_married, cov_single, cov_cohabiting, cov_withfplann
##(intends a child within 3 years) 0/1; cov_fertilitydesire (desired number of children);
##cov_fert_ideal_trad_life (ideal number of children; 5 = More than 4); cov_hhincome_ppp,
##cov_pincome_ppp (monthly, PPP intl $). Dropped: Qualtrics ResponseId (re-keyed),
##COUNTRY (duplicate code), the authors' derived dim_Income category, dim_pppincome,
##country median incomes. No survey weight in the deposit.
##N = 8,330 respondents (press release 8,334). Spot check: see return; the paper's AMCE
##tables were not accessible.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "replication_data_min.dta")))
lab <- function(x) { y <- as.character(as_factor(x, levels = "labels")); stopifnot(!is.na(y)); y }
d <- data.table(rid = match(paste(k$country, k$ResponseId), unique(paste(k$country, k$ResponseId))),
                task = as.integer(k$run), profile = as.integer(k$conjoint),
                choice = as.integer(k$conjointchoice), rating = as.integer(k$rating))
d[, `:=`(attr_woman_age = lab(k$dim_Age), attr_children = lab(k$dim_Parity), attr_home = lab(k$dim_Ownership),
         attr_work_housework = lab(k$dim_Work), attr_childcare = lab(k$dim_Policy),
         attr_income = as.character(as.integer(k$dim_cincome)),
         attr_climate = lab(k$dim_climate), attr_economy = lab(k$dim_econ), attr_politics = lab(k$dim_Political),
         attr_war = lab(k$dim_War))]
stopifnot(!is.na(d$attr_income), k[, uniqueN(dim_cincome), .(country, dim_Income)][, all(V1 == 1)])
cc <- c(argentina = "Argentina", germany = "Germany", italy = "Italy", usa = "United States")
stopifnot(all(k$country %in% names(cc)))
d[, cov_country := cc[k$country]]
stopifnot(all(k$female %in% 0:1))
d[, cov_gender := fifelse(k$female == 1, "female", "male")][, cov_age := as.integer(k$age)]
for (v in c("tertiary_self", "married", "single", "cohabiting", "withfplann", "fertilitydesire")) d[, paste0("cov_", v) := k[[v]]]
d[, cov_fert_ideal_trad_life := as.integer(zap_labels(k$fert_ideal_trad_life))]
d[, cov_hhincome_ppp := k$hhincome_ppp][, cov_pincome_ppp := k$pincome_ppp]
stopifnot(d[, .N, .(rid, task)][, all(N == 2)], all(d$rating %in% c(1:10, NA)),
          d[, .(s = sum(choice), n = sum(is.na(choice))), .(rid, task)][, all((n == 0 & s == 1) | n == 2)])
d <- d[!(is.na(choice) & is.na(rating))]
d[, id := rid][, rid := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "aassve_2026_parenthood.csv"))
