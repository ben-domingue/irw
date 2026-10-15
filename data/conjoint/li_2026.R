##Mobility-as-a-Service (MaaS) subscription choice in a stated-preference experiment, from the Zenodo deposit "Empirical
##Dataset for Latent Variable Choice Modeling" (Li, Feng, Rasouli & Wong, 2026), the data of "A Behaviorally-Informed Deep
##Neural Network for Latent Variable Choice Modeling" (Travel Behaviour and Society; article DOI not in the deposit, doi="").
##Deposit: doi:10.5281/zenodo.20192916 (concept doi 10.5281/zenodo.20192915), CC BY 4.0 (record licence cc-by-4.0).
##Files read: MaaS_data.csv, MaaS_Data_Dictionary.pdf (pdftotext; the codebook), README.md (anonymisation only).
##Usage: Rscript li_2026.R <dir holding MaaS_data.csv> <output dir>
##
##Sample: 1,299 individuals x 8 SP tasks = 10,392 rows ("Observations 10392" in the dictionary). Where the survey was fielded is
##not stated (euro prices; the dictionary mentions addresses per km2): country unknown. The file has NO respondent id.
##Respondent id reconstructed from the run structure: the file is 1,299 consecutive runs of exactly 8 rows with task =
##1..8 in order, and every covariate is constant within a run (verified); id = run number. task_source = recorded (task column),
##but the person grouping is inferred.
##Design: each task shows ONE MaaS subscription profile and the respondent answers yes/no (choice 1 = Yes, 0 = No, dictionary
##"MaaS subscription choice variable"; exact question wording not in the deposit). Rejecting is the outside option, so
##opt_out = yes (README rule: single-profile accept/reject). profile = 1.
##Attributes (6; codes mapped with the dictionary's value lists): monthly subscription price 150/180/210/240 EUR per month;
##time commitment 1/3/6/12 months; service reviews from the general public (Only positive reviews / Mainly positive reviews
##but also some criticisms / Mainly negative reviews but also some positive / Mainly negative reviews); share of the
##subscription among family members, friends and colleagues, each 0%/25%/50%/75%. Every level occurs exactly 2,598 times
##(balanced design); restrictions and level probabilities not stated; attribute order not stated.
##Covariates (dictionary): cov_gender_code (gender: 1 = female, 0 = otherwise per the dictionary, so kept as a code, not as cov_gender), cov_age (age_N, years),
##cov_marital_status (text), cov_income_band_eur_year (individual annual income, text; 7 = "Income unknown" kept as text),
##cov_urban_density (5-level text). Dropped: the six attitudinal indicator items (IND_MM1-3, IND_PT1-3). No survey weight.
##No identifying columns (anonymised by the depositors).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "MaaS_data.csv"))
stopifnot(nrow(d) == 10392, ncol(d) == 19)
d[, id := cumsum(task == 1L)]
stopifnot(uniqueN(d$id) == 1299, d[, .N, id][, all(N == 8)], d[, all(task == 1:8), id][, all(V1)],
          d[, uniqueN(.SD), id, .SDcols = c("age_N", "gender", "marital_status", "income", "urban_density")][, all(V1 == 1)],
          all(d$choice %in% 0:1))
tx <- function(x, labs) labs[x]
share <- c("0%", "25%", "50%", "75%")
o <- d[, .(id, task = as.integer(task), profile = 1L, choice = as.integer(choice))]
o[, attr_monthly_price := tx(d$prop_PR, c("150 EUR/month", "180 EUR/month", "210 EUR/month", "240 EUR/month"))]
o[, attr_time_commitment := tx(d$prop_TC, c("1 month", "3 months", "6 months", "12 months"))]
o[, attr_service_reviews := tx(d$prop_RW, c("Only positive reviews", "Mainly positive reviews but also some criticisms",
                                            "Mainly negative reviews but also some positive", "Mainly negative reviews"))]
o[, attr_share_family := tx(d$prop_RL, share)]
o[, attr_share_friends := tx(d$prop_FR, share)]
o[, attr_share_colleagues := tx(d$prop_CL, share)]
o[, cov_gender_code := as.integer(d$gender)]
o[, cov_age := as.integer(d$age_N)]
o[, cov_marital_status := tx(d$marital_status, c("Single", "Living together", "Married", "Separated", "Widow/Widower", "Other"))]
o[, cov_income_band_eur_year := tx(d$income, c("Less than 10,000 EUR", "10,000 to 20,000 EUR", "20,000 to 30,000 EUR", "30,000 to 40,000 EUR",
                                               "40,000 to 50,000 EUR", "More than 50,000 EUR", "Income unknown"))]
o[, cov_urban_density := tx(d$urban_density, c("Highest urban density (more than 2500 addresses per km2)", "High urban density (1500-2500 addresses per km2)",
                                               "Moderate urban density (1000-1500 addresses per km2)", "Low urban density (500-1000 addresses per km2)",
                                               "Lowest urban density (less than 500 addresses per km2)"))]
stopifnot(!anyNA(o[, .SD, .SDcols = patterns("^attr_|^cov_")]))
setorder(o, id, task, profile)
dir.create(out, showWarnings = FALSE, recursive = TRUE)
fwrite(o, file.path(out, "li_2026_maas_subscription.csv"))
