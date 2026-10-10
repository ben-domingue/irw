##Tax-compliance factorial vignette experiment (Kenya) from
##Ahsan Jansson, C., Lust, E., & Oguso, A. (2026). Community donations, public goods provision and
##taxpayer attitudes: Lessons from a survey experiment in Kenya. Political Science Research and
##Methods. https://doi.org/10.1017/psrm.2026.10098
##Replication data: Harvard Dataverse doi:10.7910/DVN/POT08T, CC0 1.0. File read: ReplicationData.dta
##(Dataverse "original format" download, datafile 13325311; Stata value labels used). Read as text
##only: README.txt, ReplicationCode.do, ReplicationLog.log. Vignette and question wording from the
##article (Cambridge Core HTML).
##Usage: Rscript ahsanjansson_2026.R <dir holding ReplicationData.dta> <output dir>
##
##Kenyan adults, telephone survey by TIFA, June-July 2021 (article: nationally representative, N 2,000;
##the deposit has 2,080 respondents). Each respondent heard ONE vignette (task = 1, profile = 1):
##  "Imagine {Gender}, who has a job and earns {Earnings} each month. He/She lives in an area with
##  {Service Provision} access to public services such as electricity, water, and security. Every year,
##  he/she donates a {Community Donations} share of his/her income to schools, churches, and other local
##  development initiatives in his/her community. John/Mary is also required to report his/her monthly
##  earnings and pay government tax accordingly. In his/her county, government resources are {Fairness}
##  distributed across wards, tax authorities provide {Transparency} information about the use of tax
##  funds. If he/she would decide to evade paying taxes, it is {Detection} that he/she would be caught,
##  and if he/she was caught, he/she would have to pay a {Fine} fine."
##Eight binary factors; article: "Factor levels are randomly selected with equal probability".
##Attribute text = the Stata VALUE LABELS (authors' short labels): gender Male/Female (the vignette
##apparently named the person John or Mary; the deposit stores only Male/Female), earnings
##30 000 KSH / 120 000 KSH, service provision Poor Access / Good Access, community donations Small
##Donation / Large Donation, fairness Unequally / Equally, transparency Very Little / A Lot Of,
##detection Unlikely / Likely, fine Small Fine / Large Fine. Exact displayed fragments (e.g. "good" vs
##"Good Access") are in the article's Table 1 image, not read.
##Outcomes (three yes/no questions about the vignette person; not a pick among profiles -> rating_):
##  rating_pay_tax      "Should the person pay income tax to the government?"
##  rating_justifiable  "Would it be justified if the person did not report all their income to pay less tax?"
##  rating_trust_gov    "Would you trust the government to spend the tax money wisely?"
##Stored as the deposit's analysis variables PayTax / Justifiable / TrustGov: 1 = Yes, 0 = No (the raw
##answers PayTaxRaw etc. are 1 Yes, 2 No, -888 Don't know, -998 Refuse; the script checks the mapping).
##Don't know and Refuse are NA, as in the authors' analysis. Respondents with all three NA are dropped.
##Check: the paper's Table 2 col. 1 (PayTax on the 8 factors, N = 2,026) reproduces from this table
##(e.g. earnings 120,000 KSH +0.106, detection likely -0.059).
##Covariates (variable labels in the .dta): cov_gender (Female 1 -> female, 0 -> male), cov_age (years),
##cov_education (value-label text: No Formal Schooling, Primary Schooling, Secondary Schooling, Mid-Level
##Collage [sic], University), cov_rural, cov_works, cov_ever_employed, cov_enough_income (income large
##enough to be eligible for PAYE), cov_resp_detection, cov_resp_tax_benefit, cov_resp_community_goods,
##cov_resp_contributed (respondent perceptions/behaviour, 0/1 as stored). Dropped: SecondaryEducation
##(derived from Education). No survey weight in the deposit.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "ReplicationData.dta"))
stopifnot(nrow(k) == 2080)
chk <- function(r, b) all((zap_labels(r) == 1 & b == 1) | (zap_labels(r) == 2 & b == 0) | (zap_labels(r) < 0 & is.na(b)), na.rm = FALSE)
stopifnot(chk(k$PayTaxRaw, k$PayTax), chk(k$JustifiableRaw, k$Justifiable), chk(k$TrustRaw, k$TrustGov))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L,
  rating_pay_tax = as.integer(k$PayTax), rating_justifiable = as.integer(k$Justifiable), rating_trust_gov = as.integer(k$TrustGov),
  attr_gender = lab(k$GenderAttribute), attr_earnings = lab(k$EarningsAttribute),
  attr_service_provision = lab(k$ServiceProvisionAttribute), attr_community_donations = lab(k$LocalContributionsAttribute),
  attr_fairness = lab(k$FairnessAttribute), attr_transparency = lab(k$TransparencyAttribute),
  attr_detection = lab(k$DetectionAttribute), attr_fine = lab(k$FineAttribute),
  cov_gender = c("male", "female")[as.integer(k$Female) + 1L], cov_age = as.integer(k$Age),
  cov_education = lab(k$Education), cov_rural = as.integer(k$Rural), cov_works = as.integer(k$Works),
  cov_ever_employed = as.integer(k$EverEmployed), cov_enough_income = as.integer(k$EnoughIncome),
  cov_resp_detection = as.integer(k$RespDetection), cov_resp_tax_benefit = as.integer(k$RespTaxBenefit),
  cov_resp_community_goods = as.integer(k$RespCommunityGoods), cov_resp_contributed = as.integer(k$RespContributed))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), all(d$cov_gender %in% c("male", "female")))
d <- d[!(is.na(rating_pay_tax) & is.na(rating_justifiable) & is.na(rating_trust_gov))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ahsanjansson_2026_tax_compliance.csv"))
