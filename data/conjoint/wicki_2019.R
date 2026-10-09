##Sustainable passenger transport policy-package conjoint (China, Germany, USA) from
##Wicki, M., Fesenfeld, L., & Bernauer, T. (2019). In search of politically feasible policy-packages for
##sustainable passenger transport: Insights from choice experiments in China, Germany, and the USA.
##Environmental Research Letters, 14(8), 084048. https://doi.org/10.1088/1748-9326/ab30a2
##Replication data: Harvard Dataverse doi:10.7910/DVN/N1NUST, CC0 1.0. File read: conjoint_design.RData
##(object df_conj, loaded into its own environment). mobility_conjoint_analysis_V4.R read as text, not
##run. Design facts from the article (open access, IOP HTML, read 2026-10-08).
##Usage: Rscript wicki_2019.R <dir holding conjoint_design.RData> <output dir>
##
##4,876 respondents (Ipsos internet panels, February 2018; CN 1,624, DE 1,626, US 1,626 = the article,
##after the authors dropped 79 who finished in six minutes or less), 4 tasks (round) x 2 policy packages
##(policy A/B), 7 attributes, all shown. One table with cov_country: the authors pool the three
##countries in their main models (and also estimate per country), and the stored attribute text is
##one English set.
##Outcomes:
##  choice = choice: binary forced choice between the two packages (exactly one per task, checked).
##           The article does not give the wording.
##  rating = rate: each package rated on a 7-point scale, 1 = strongly opposed, 7 = strongly support
##           (article); equals rate_A/rate_B (checked).
##Attribute text: the authors' English level labels (attrib*_lab) with their "1) " numbering prefix and
##trailing spaces removed. The surveys were presumably in Chinese, German and English; the displayed
##translations are not deposited. The car-requirement attribute is stored for all countries in US
##units ("At least 40/55 miles per gallon"); the article's attribute table gives l/100 km
##(maximum 5.9 / 4.3 l/100 km) and says only the US version used miles per gallon, so the German and
##Chinese respondents most likely saw l/100 km: the stored text is not what they saw.
##Attribute names (article): fuel_tax (new tax on fossil fuels), revenue_use (use of fuel-tax
##revenues), downtown_restriction (restricting fossil-fuelled cars in downtown areas),
##public_transport (financial support for public transportation), car_requirements (requirements for
##newly registered cars), campaigns (information campaigns), industry_subsidies (reducing subsidies
##for the fossil-fuel car industry).
##Restriction (article, checked): "No tax revenues" occurs exactly when the tax is "No new tax".
##Attribute order: randomized per respondent and kept across tasks (article); not recorded.
##Covariates: cov_country (DE/US/CN), cov_gender (male/female), cov_age (years), cov_age_group,
##cov_edu_group (educ: Low/Medium/High, the authors' harmonized groups, not answer text), cov_incgrp (income quintile group),
##cov_km (as stored; presumably km driven per year), cov_stopdriving and cov_caraccess (codes; no
##labels in the deposit), cov_duration (as stored; unit not documented). Dropped: start/end time,
##frame (constant "Mobility"), idround, the coded Attrib* and rate_A/rate_B duplicates.
##No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "conjoint_design.RData"), envir = e)
s <- as.data.table(e$df_conj)
stopifnot(nrow(s) == 39008, uniqueN(s$id) == 4876, s[, .N, .(id, round, policy)][, all(N == 1)])
cl <- function(x) trimws(sub("^[0-9]+\\) ", "", as.character(x)))
nm <- c(fuel_tax = 1, revenue_use = 2, downtown_restriction = 3, public_transport = 4, car_requirements = 5,
        campaigns = 6, industry_subsidies = 7)
d <- s[, .(id = as.integer(id), task = as.integer(round), profile = match(policy, c("A", "B")),
           choice = as.integer(choice), rating = as.integer(rate))]
for (k in names(nm)) d[, paste0("attr_", k) := cl(s[[sprintf("attrib%d_lab", nm[[k]])]])]
stopifnot(all(d$rating == as.integer(sub("_", "", fifelse(s$policy == "A", s$rate_A, s$rate_B)))))
stopifnot(identical(d$attr_fuel_tax == "No new tax", d$attr_revenue_use == "No tax revenues"))
d[, `:=`(cov_country = as.character(s$country), cov_gender = as.character(s$gender), cov_age = as.integer(s$age),
         cov_age_group = as.character(s$age_grp), cov_edu_group = s$educ, cov_incgrp = s$incgrp, cov_km = s$km,
         cov_stopdriving = as.integer(s$stopdriving), cov_caraccess = as.integer(s$caraccess), cov_duration = s$duration)]
stopifnot(!anyNA(d[, .(choice, rating)]), all(d$rating %in% 1:7), all(d$cov_gender %in% c("male", "female")),
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(cov_country), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wicki_2019_passenger_transport.csv"))
