##Beer eco-label choice experiment (US) from
##Staples, A. J., Reeling, C. J., Widmar, N. J. O., & Lusk, J. L. (2020). Consumer willingness to pay for
##sustainability attributes in beer: A choice experiment using eco-labels. Agribusiness, 36(4), 591-612.
##https://doi.org/10.1002/agr.21655
##Data: Mendeley Data doi:10.17632/4z748jnnjs.2 (version 2), CC BY 4.0 (Mendeley public API, data_licence).
##File read: Code.zip -> "Code/Model 1 - MNL with Full Dataset/Beer Data Full Dataset.dta" (long file, 30,984 rows =
##1,291 respondents x 8 choice occasions x 3 alternatives). Attribute meaning and level wording from the first
##author's open thesis (Purdue, figshare 8866010, Table 1 and chapter 3: "Consumer Willingness-to-Pay for
##Sustainability Attributes in Beer"), plus the authors' Stata do-file in the zip (read as text, not run).
##Usage: Rscript staples_2020.R <dir holding Code.zip's extracted dta, any name ending .dta> <output dir>
##
##US adults who buy beer (Qualtrics survey, spring 2019, nationally representative targeted sample via Kantar;
##1,291 completed, as in the thesis; the thesis' main models drop 245 "serial nonparticipants", the deposit's full file
##keeps them and so does this table). Each of 8 choice occasions: Beer A, Beer B and "No Purchase" (opt-out, no
##attributes: Alternative 3, opt_out = yes, rows dropped; chosen in 3,332 of 10,328 sets). Outcome: which of the
##alternatives would you choose (thesis wording: the respondent selects which alternative they would choose; cheap-talk
##arm: "If you would not purchase either beer, then you should choose the option to not buy either product").
##D-efficient Ngene design, 16 choice sets in two blocks of 8 (trial_block, randomly assigned); the sets were
##randomly ordered per respondent (task = Respondentchoiceoccasion, assumed the order shown).
##Attributes (thesis Table 1): primary packaging of a six-pack of 12-oz containers (Can / Bottle), water-conserving
##practices label (Yes/No), energy-conserving practices label (Yes/No; the file calls it Carbon), waste-reduction /
##landfill-diversion label (Yes/No), locally produced label (Yes/No), price per six-pack ($6.99, $8.49, $9.99, $11.49).
##The sustainability attributes are shown as eco-label icons on the beer, so "Yes" = label present, "No" = absent.
##Restrictions: none documented. Level weights: D-efficient design, probabilities not stated (unknown).
##Attribute order fixed (a fixed label figure; not stated otherwise).
##trial_cheap_talk: 1 = instructions with a cheap-talk script, 0 = without (randomized, independent of block).
##Covariates kept: cov_gender (the file's label "1 = male, 0 = female"), cov_age_group, cov_education,
##cov_income_usd, cov_region (text from the file's dummy-variable labels; 1 respondent has no income band -> NA).
##Dropped: all other dummies and purchase-behaviour variables, derived effects-coded columns (EC_*), ASC, BudLight.
##N vs paper: 1,291 respondents as in the thesis.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(list.files(raw, pattern = "[.]dta$", full.names = TRUE, recursive = TRUE)[1]))
stopifnot(nrow(x) == 30984, uniqueN(x$RespondentID) == 1291, x[, .N, RespondentID][, all(N == 24)])
stopifnot(x[, sum(Choice), .(RespondentID, Respondentchoiceoccasion)][, all(V1 == 1)], x[Alternative == 3, all(Price == 0 & ASC == 1)])
x[, id := match(RespondentID, sort(unique(RespondentID)))]
pickdum <- function(cols, labs) { m <- as.matrix(x[, ..cols]); r <- apply(m, 1, function(z) if (isTRUE(sum(z) == 1)) labs[which(z == 1)] else NA_character_); r }
x[, cov_age_group := pickdum(c("Age_sub21","Age_21to24","Age_25to34","Age_35to44","Age_45to54","Age_55to64","Age_65plus"),
  c("<21","21-24","25-34","35-44","45-54","55-64","65+"))]
x[, cov_education := pickdum(c("Educ_NoHSdip","Educ_HSdip","Educ_College_NoDegree","Educ_AAorBA","Educ_GradDegree"),
  c("No high school diploma","High school, no college","Attended college, no degree","AA or BA","Graduate degree"))]
x[, cov_income_usd := pickdum(c("Income_0to24999","Income_25to49999","Income_50to74999","Income_75to99999","Income_100plus"),
  c("0-24,999","25,000-49,999","50,000-74,999","75,000-99,999","100,000+"))]
x[, cov_region := pickdum(c("Region_NE","Region_S","Region_MW","Region_W"), c("Northeast","South","Midwest","West"))]
x[, cov_gender := ifelse(Gender == 1, "male", "female")]
p <- x[Alternative < 3]
yn <- function(v) ifelse(v == 1, "Yes", "No")
d <- p[, .(id, task = as.integer(Respondentchoiceoccasion), profile = as.integer(Alternative), choice = as.integer(Choice),
  attr_packaging = ifelse(Package == 1, "Bottle", "Can"), attr_water_conserving = yn(Water), attr_energy_conserving = yn(Carbon),
  attr_waste_reduction = yn(Landfill), attr_local = yn(Localness), attr_price = sprintf("$%.2f", Price),
  cov_gender, cov_age_group, cov_education, cov_income_usd, cov_region,
  trial_block = as.integer(Block), trial_cheap_talk = as.integer(Cheaptalk))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^task$|^profile$")]), d[, .N, .(id, task)][, all(N == 2)],
  d[, sum(choice), .(id, task)][, all(V1 <= 1)], all(d$attr_price %in% c("$6.99","$8.49","$9.99","$11.49")))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "staples_2020_beer_eco_labels.csv"))
