##Surveillance-policy factorial vignette from
##Ziller, C., & Helbling, M. (2021). Public support for state surveillance. European Journal of
##Political Research, 60(4), 994-1006. https://doi.org/10.1111/1475-6765.12424
##Replication data: Harvard Dataverse doi:10.7910/DVN/OLVRK0, CC0 1.0, no restricted files.
##File read: "ZH_surveillance_data.tab" (Stata original, saved as d.dta); labels for the factor
##levels from the authors' ZH_surveillance_do.do (read as text, coefplot coeflabels).
##Usage: Rscript ziller_2021.R <raw dir> <output dir>
##
##6,169 online respondents in Germany (2,780, August 2019), the UK (1,119), France (1,120) and Spain
##(1,150) (December 2019); each read ONE vignette about a government surveillance programme, randomly
##assigned to one of 18 cells (3 x 3 x 2, 329-396 per cell): attr_policy_scope (not mentioned /
##dragnet scope / targeted scope), attr_data_security (not mentioned / data security debated /
##data not secure), attr_terror_salience (not mentioned / number of terror victims salient). The
##authors' "not mentioned" level means the vignette left that element out, stored as "(not shown)".
##The other level texts are the authors' short labels from the do-file, not the vignette sentences
##(no questionnaire in the deposit; the threat level cites country-specific attack and victim counts
##of the last three years per the article abstract). The authors report a pooled all-country model
##and four country models; the vignette text is the same design, so one table with cov_country.
##Outcomes: rating = `agree` (support for the surveillance measure) and rating_trust_gov = `trust_gov`
##(trust in government), both 11 points coded 1-11 in the file; wording, direction and anchors are not
##in the deposit (the authors treat higher as more support / trust in their coefplots, not verified).
##10 and 20 missing answers are NA; rows with both missing are omitted. No choice, no opt-out.
##One vignette per respondent: id = row order, task = profile = 1.
##Covariates: cov_country (Land value labels, German names mapped to English), cov_gender (sex labels
##Maennlich/Weiblich), cov_age. Dropped: trust in other institutions, need-for-security scale (sec),
##education/income/settlement codes with no labels, derived dummies.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_dta(file.path(raw, "d.dta")))
stopifnot(nrow(d) == 6169, all(d$policy %in% 0:2), all(d$datasec %in% 0:2), all(d$terror %in% 0:1))
ns <- "(not shown)"
o <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L,
  rating = as.integer(d$agree), rating_trust_gov = as.integer(d$trust_gov),
  attr_policy_scope = c(ns, "Dragnet scope", "Targeted scope")[d$policy + 1L],
  attr_data_security = c(ns, "Data security debated", "Data not secure")[d$datasec + 1L],
  attr_terror_salience = c(ns, "No. of terror victims salient")[d$terror + 1L],
  cov_country = c("Germany", "United Kingdom", "France", "Spain")[as.integer(d$Land)],
  cov_gender = c("male", "female")[as.integer(d$sex)], cov_age = as.integer(d$age))
stopifnot(o[!is.na(rating), all(rating %in% 1:11)], o[!is.na(rating_trust_gov), all(rating_trust_gov %in% 1:11)])
o <- o[!(is.na(rating) & is.na(rating_trust_gov))]
setorder(o, id, task, profile); fwrite(o, file.path(out, "ziller_2021_state_surveillance.csv"))
