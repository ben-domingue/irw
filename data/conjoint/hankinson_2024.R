##Single-profile housing-proposal experiment (Boston) from
##Hankinson, M., & de Benedictis-Kessner, J. (2024). How self-interest and symbolic politics shape the effectiveness of
##compensation for nearby housing development. Journal of Public Policy, 44. https://doi.org/10.1017/S0143814X24000199
##Replication data: Harvard Dataverse doi:10.7910/DVN/DZ0PR8, CC0 1.0 (no restricted files). File read: replication_data.rds (the
##authors' main long file, one row per respondent x proposal; the logitr file is a restructuring of it, not used) with codebook.pdf and
##replication_240717.R (as text). Usage: Rscript hankinson_2024.R <dir holding replication_data.rds> <output dir>
##
##Online survey of Boston residents (three waves; 578 respondents in the file, 531 kept after the drop below; the abstract says nearly 600). Each respondent
##evaluated up to five hypothetical housing developments rendered on images of their own neighbourhood, one proposal at a time
##(task = proposal_order dev_prop_1..5, profile 1). Randomized attributes (codebook): whether the development includes affordable housing
##units (proposal_aff 1) or is 100% market-rate (0); then, after the first support question, the compensation offered: its amount (12 levels,
##$50 to $10,000) and its form (private cash payment vs public park investment). The location, hence the distance from home, is NOT randomized
##(a property of the proposal) and is stored as trial_distance_km. The wording of the support questions and the dollar sign are not in the deposit
##(Boston survey; "$" assumed from the codebook's "amount of compensation"). Two outcomes on each proposal, asked in sequence:
##  rating_support_before_compensation = proposal_support, support for the proposal WITHOUT compensation (before the compensation was shown),
##    0 (strongly oppose) to 1 (strongly support) in steps of 0.25 as recoded by the authors;
##  choice = proposal_vote, support (1) or oppose (0) the proposal WITH the compensation; a single-profile accept/reject, so opt_out = yes.
##Rows (229, all wave 1) where proposal_aff is missing are dropped: it is not clear whether the affordable-housing factor was shown, and a blank
##attribute would mean "missing in source". The 5 rows with no wave are kept. 2,583 rows, 531 respondents remain.
##Covariates (authors' coding in the codebook): cov_gender (female 1/0, else NA), cov_age, cov_education (educ labels 0-5), cov_income (13 income
##labels), cov_homeowner (own: owner / renter), cov_race (the authors' non-Hispanic white / Black / Asian, Hispanic; 'Other' when none), cov_party_id (pid: -1 Republican or lean,
##0 Independent/neither, 1 Democrat or lean), cov_ideology (ideo: -1 conservative or lean, 0 moderate, 1 liberal or lean). trial_wave = survey wave (1-3).
##Dropped: derived distance versions, near, price_2sd, support_bi, dummy duplicates (democrat, liberal, college, white ...).
##Not in this table: open-ended text, locations (dropped as identifying), the demographics-only file.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(readRDS(file.path(raw, "replication_data.rds")))
stopifnot(nrow(d) == 2812, d[, uniqueN(wave), id][, all(V1 == 1)])
d <- d[!is.na(proposal_aff)]
d[, task := as.integer(sub("dev_prop_([0-9]).*", "\\1", proposal_order))]
stopifnot(!anyNA(d$task), all(d$proposal_vote %in% 0:1), all(d$proposal_aff %in% 0:1), all(d$proposal_public %in% 0:1))
educ <- c("Did not graduate from high school", "High school graduate", "Some college, but no degree", "2-year college degree", "4-year college degree",
          "Postgraduate degree (MA, MBA, MD, JD, PhD, etc.)")
inc <- c("None or less than $19,999", "$20,000 to $39,999", "$40,000 to $49,999", "$50,000 to $59,999", "$60,000 to $69,999", "$70,000 to $89,999",
         "$90,000 to $119,999", "$120,000 to $149,999", "$150,000 to $199,999", "$200,000 to $249,999", "$250,000 to $349,999", "$350,000 to $499,999", "$500,000 and over")
r <- data.table(id = as.integer(factor(d$id)), task = d$task, profile = 1L, choice = as.integer(d$proposal_vote),
  rating_support_before_compensation = d$proposal_support,
  attr_affordable_housing = c("100% market-rate housing", "including affordable housing units")[d$proposal_aff + 1L],
  attr_compensation_amount = paste0("$", format(d$proposal_comp, big.mark = ",", trim = TRUE)),
  attr_compensation_form = c("private cash payment", "public park investment")[d$proposal_public + 1L],
  trial_distance_km = d$dist_km, trial_wave = as.integer(d$wave),
  cov_gender = c("male", "female")[d$female + 1L], cov_age = as.integer(d$age), cov_education = educ[d$educ + 1L], cov_income = inc[d$income],
  cov_homeowner = c("renter", "owner")[d$own + 1L],
  cov_race = ifelse(is.na(d$white), NA, ifelse(d$latino == 1, "Hispanic", ifelse(d$white == 1, "White (non-Hispanic)", ifelse(d$black == 1, "Black (non-Hispanic)",
             ifelse(d$asian == 1, "Asian (non-Hispanic)", "Other"))))),
  cov_party_id = c("Republican or lean Republican", "Independent/neither", "Democrat or lean Democrat")[d$pid + 2L],
  cov_ideology = c("conservative or lean conservative", "moderate/neither", "liberal or lean liberal")[d$ideo + 2L])
setorder(r, id, task, profile)
stopifnot(!anyDuplicated(r[, .(id, task)]))
print(r[, .(n = .N, vote = mean(choice), support = mean(rating_support_before_compensation)), attr_affordable_housing])
cat("rows", nrow(r), "respondents", uniqueN(r$id), "\n")
fwrite(r, file.path(out, "hankinson_2024_housing_compensation.csv"))
