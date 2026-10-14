##Hypothetical bond-referendum ballots from
##Bechard, A., Lang, C., & Pearson-Merkowitz, S. (2024). Voter approval of bond referendums: The role of
##bond amount and ballot characteristics. State Politics & Policy Quarterly, 24(1), 53-76.
##https://doi.org/10.1017/spq.2023.26
##Replication data: doi:10.15139/S3/TDPLWQ, CC0 1.0 (the Dataverse terms field is empty beyond
##the stock "CC0 with additional/modified terms" sentence). Files read: ready.dta (Stata),
##codebook.pdf, replication.do (read as text, not run), readme.txt.
##Usage: Rscript bechard_2024_bond_referendums.R <dir holding ready.dta> <output dir>
##
##Rhode Island registered voters, one cross-section (ready.dta, 851 rows). Each respondent
##saw a hypothetical bond ballot of 1, 3 or 5 bonds (ballot size randomized; a 1-bond ballot
##is land conservation or affordable housing) and voted yes/no on each bond. Bond types:
##land conservation, affordable housing, K-12 schools, higher education, transportation.
##Each bond carries a randomized price: $20, 50, 100, 200, 300 or 500 million (price_* in
##millions per replication.do "now in units of $1 million"). Ballot position (order_*) was also randomized.
##Table design: one task per bond seen, one profile per task, attributes = bond type, price,
##ballot size. A bond was "seen" when its vote_* is non-missing (price_* is filled for all five
##bonds on a 3-bond ballot, so the vote, not the price, marks what was shown).
##  choice = vote_* (1 = voted yes on the bond, 0 = no). A single-profile vote, so opt_out = yes.
##Task index = fixed bond order (land, affordable housing, K-12, higher education, transportation),
##NOT display order (task_source inferred). The recorded ballot position is kept raw as trial_order_code: it
##is NOT used as an attribute because it is inconsistent in the source (110 of 851 rows repeat a
##position among the bonds seen, and order is filled for bonds not seen).
##Attribute text: price "$<n> million" (unit from replication.do), ballot size "<n> bond(s) on the
##ballot", bond type from the codebook variable descriptions ("land bond", "affordable housing bond",
##"k12 school bond", "higher education bond", "transportation bond", paraphrased into full names).
##Sample rule: replication.do drops time_survey < 60 and any row missing city, home_own, under_rep,
##age_cts, dem, ind, vote_frequency, educ_cts, inc_cts or sex_male; this script applies the same drops, so the
##sample is the authors' estimation sample.
##Covariates (codebook.pdf): cov_gender from sex_male/sex_female (1 male); cov_age_group from the
##age_18_29..age_65plus binaries (text of the band); cov_party_id from party_dem/rep/ind/other
##binaries ("Democrat","Republican","Independent","Other"); cov_duration_sec = time_survey (seconds);
##cov_education_years = educ_cts (coded years, midpoints); cov_home_own, cov_hispanic 0/1;
##cov_vote_frequency_code and cov_govt_trust_code keep source codes (codebook: vote_frequency 1-4 but data
##run 1-5; govt_trust 1-5 but data run 1-4). Dropped: city (small-town geography), age_cts and inc_cts
##(band midpoints), race and income dummies, all derived price/total/dummy variables.
##No survey weight. Randomization restrictions: not documented beyond ballot size determining which bonds
##appear. 
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_dta(file.path(raw, "ready.dta")))
keep <- d$time_survey >= 60 & !is.na(d$city) & !is.na(d$home_own) & !is.na(d$under_rep) & !is.na(d$age_cts) &
  !is.na(d$dem) & !is.na(d$ind) & !is.na(d$vote_frequency) & !is.na(d$educ_cts) & !is.na(d$inc_cts) & !is.na(d$sex_male)
d <- d[keep]
d[, id := .I]
bonds <- c(land = "land conservation bond", aff = "affordable housing bond", k12 = "K-12 school bond",
           higher_ed = "higher education bond", transportation = "transportation bond")
ordcol <- c(land = "order_land", aff = "order_aff", k12 = "order_k12", higher_ed = "order_higher_ed", transportation = "order_tran")
d[, cov_gender := fifelse(sex_male == 1, "male", fifelse(sex_female == 1, "female", NA_character_))]
ageb <- c(age_18_29 = "18-29", age_30_44 = "30-44", age_45_54 = "45-54", age_55_64 = "55-64", age_65plus = "65+")
d[, cov_age_group := NA_character_]
for (v in names(ageb)) d[get(v) == 1, cov_age_group := ageb[[v]]]
pt <- c(party_dem = "Democrat", party_rep = "Republican", party_ind = "Independent", party_other = "Other")
d[, cov_party_id := NA_character_]
for (v in names(pt)) d[get(v) == 1, cov_party_id := pt[[v]]]
d[, `:=`(cov_duration_sec = as.numeric(time_survey), cov_education_years = as.integer(educ_cts),
         cov_home_own = as.integer(home_own), cov_hispanic = as.integer(hispanic),
         cov_vote_frequency_code = as.integer(vote_frequency), cov_govt_trust_code = as.integer(govt_trust))]
cov <- c("cov_gender", "cov_age_group", "cov_party_id", "cov_duration_sec", "cov_education_years", "cov_home_own",
         "cov_hispanic", "cov_vote_frequency_code", "cov_govt_trust_code")
L <- list()
for (i in seq_along(bonds)) {
  b <- names(bonds)[i]
  s <- d[!is.na(get(paste0("vote_", b))) & !is.na(get(paste0("price_", b)))]
  L[[i]] <- cbind(s[, .(id)], task = i, profile = 1L, choice = as.integer(s[[paste0("vote_", b)]]),
    attr_bond_type = bonds[[b]], attr_price = paste0("$", as.integer(s[[paste0("price_", b)]]), " million"),
    attr_ballot_size = paste0(as.integer(s$ballot_size_cts), ifelse(s$ballot_size_cts == 1, " bond", " bonds"), " on the ballot"),
    trial_order_code = as.integer(s[[ordcol[[b]]]]), s[, ..cov])
}
r <- rbindlist(L)
r[, task := as.integer(factor(task)) , by = id]  # renumber tasks 1..k within respondent
stopifnot(!anyNA(r$choice), !anyNA(r$attr_price))
setorder(r, id, task, profile)
fwrite(r, file.path(out, "bechard_2024_bond_referendums.csv"))
