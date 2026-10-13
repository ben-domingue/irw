##India coal-exit / energy policy paired conjoint
##Pooja Ramamurthi (2022). Data for Policy conjoint [dataset]; no article is linked from the deposit.
##Data: figshare "Data for Policy conjoint", doi:10.6084/m9.figshare.20596998, CC BY 4.0.
##File read: policy_data.csv (14,670 rows). The deposit description says only that the data
##are an extract from larger experiments and survey; no codebook, no question wording.
##Usage: Rscript ramamurthi_2022_india_coal_policy.R <dir holding policy_data.csv> <output dir>
##
##1,467 respondents (PID), 5 tasks each ("question" 1-5), 2 profiles per task ("choice" 1/2 is
##the profile index; "binary" is the 0/1 chosen flag: exactly one chosen per task, verified).
##The file rows are in shuffled order; task = `question`. Whether question number equals the
##order shown is not documented. Forced choice, no opt-out. Question wording is NOT in the
##deposit (design_outcomes says unknown).
##Six attributes, levels as text in the source: end date for coal power plants, electricity
##generation, India's global role, technology investments, policy actors, annual share of
##income tax. Attribute order, restrictions and level probabilities are not documented;
##level shares are near-equal for end date (2030 is ~21% vs ~26% for others: observed unequal).
##Covariates: no codebook, so codes are kept with a _code suffix: cov_gender_code (1/2),
##cov_age_code (1-5, an age band code), cov_region_code (1-5). cov_language = UserLanguage (EN/HI).
##Dropped: PID (re-keyed), all survey items, timing, attention and derived columns (attention
##coding direction is undocumented).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "policy_data.csv"))
stopifnot(nrow(s) == 14670, s[, .N, .(PID, question)][, all(N == 2)])
s[, id := as.integer(factor(PID))]
d <- s[, .(id, task = as.integer(question), profile = as.integer(choice), choice = as.integer(binary),
  attr_coal_end_date = `End.date.for.coal.power.plants`, attr_electricity_generation = `Electricity.generation`,
  attr_global_role = `India.s.global.role`, attr_technology_investments = `Technology.Investments`,
  attr_policy_actors = `Policy.actors`, attr_income_tax_share = `Annual.share.of.income.tax`,
  cov_gender_code = as.integer(gender), cov_age_code = as.integer(age), cov_region_code = as.integer(region),
  cov_language = `UserLanguage.x`)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ramamurthi_2022_india_coal_policy.csv"))
