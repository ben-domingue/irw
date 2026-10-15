##Mobile money factorial vignette experiment (Uganda) from
##Hamdan, J. S., Lehmann-Uschner, K., & Menkhoff, L. (2022). Mobile money, financial inclusion, and unmet
##opportunities: Evidence from Uganda. The Journal of Development Studies, 58(3), 671-691.
##https://doi.org/10.1080/00220388.2021.1988078
##Data: figshare doi:10.6084/m9.figshare.16912592 (v2, Taylor & Francis), CC BY 4.0 (figshare API). Files read:
##fjds-2020-nov-0075-File007.dta (31 MB; columns id, preference_1..12, cal_randnum1..4_1..12, q10_gender, q12_age,
##q170a_language only) and, as text, File006.do (vignette dimensions, value labels) and File008.pdf (Supplementary
##Materials: Table S2 gives example vignettes verbatim; Table S5 gives N).
##Usage: Rscript hamdan_2021.R <dir holding File007.dta> <output dir>
##
##2,223 microentrepreneurs (survey Feb-Apr 2019, trading centres in Uganda; interview language English or Rutooro). Each was
##to answer 12 vignettes ("Imagine you want to ... [amount] UGX ... You are charged a fee of [x%] of the ... amount.
##[This equals y UGX | (NO FURTHER INFO)] Would you make this transfer?"). Four independently randomized
##dimensions (File006.do: draw probabilities 1/6, 1/3, 1/6, 1/2; all 180 cells observed):
##  attr_transaction (6): transfer to a user on the same network / on a different network / cash withdrawal /
##     payment in a store / saving / loan  (wording condensed from the Table S2 vignettes and the .do value labels)
##  attr_amount (3): UGX 10,000 / UGX 50,000 / UGX 150,000
##  attr_fee (5 x type): 1% 5% 10% 15% 25%, written as in the vignette for each transaction type ("fee of 5% of the
##     transfer amount", "fee of 1% of the withdrawal amount", "fee of 25% of the payment amount", "interest rate of
##     10% of the saving amount per year", "fee of 15% of the loan amount per month"); for saving the percentage is
##     an interest rate, not a fee, so effects of attr_fee are not comparable across transaction types.
##  attr_fee_info (2): "Fees reported in % only" / "Fees reported in % and UGX" (.do value labels; the vignette adds
##     "[This equals y UGX]" in the second case).
##One vignette per task, k = 1..12 (the .do reshapes preference_k by k; k is taken as the order shown). Single-profile
##accept/reject question: choice = 1 "yes, would make it", 0 "no" (opt_out = yes: rejecting is the outside option).
##WHAT THE DEPOSIT HOLDS: an answer for only 8,896 of the 26,676 vignettes drawn (2,206 respondents; exactly the N of
##the authors' Table S5, whose note says vignettes on savings and loans and those with the fee reported in % only
##"have been excluded"). The stored answers are all transaction types 1-4 with the fee also shown in UGX. So the
##table has 3 varying attributes (transaction type with 4 levels, amount, fee) and attr_fee_info (always "Fees reported
##in % and UGX", i.e. the vignette ends "[This equals y UGX]") is dropped as constant; saving/loan levels never occur
##in the table. The dropped vignettes were not saved, not missing at random. Restrictions: none (independent draws,
##Table S3); level weights uniform within what is kept. Task indices have gaps; respondents with no stored answer (17)
##are absent. "preference" (a count of yes over 12) is derived and does not match the stored answers: dropped.
##Covariates: cov_gender (q10_gender value labels Male/Female -> male/female), cov_age (q12_age, years, as
##recorded; implausible < 15 or > 90 set NA), trial_interview_language (q170a_language: English / Rutooro).
##Respondent key id is the deposit's survey number (not an external identifier). Dropped: everything else (1,200
##survey variables, trading-centre names, assets, finance), derived dummies, the random draws randnum*_id.
##N vs paper: 2,206 respondents / 8,896 vignette answers match the Supplementary Table S5.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fn <- list.files(raw, pattern = "[.]dta$", full.names = TRUE)[1]
cols <- c("id", "q10_gender", "q12_age", "q170a_language", paste0("preference_", 1:12),
  paste0("cal_randnum", rep(1:4, each = 12), "_", 1:12))
x <- as.data.table(read_dta(fn, col_select = all_of(cols)))
stopifnot(nrow(x) == 2223, uniqueN(x$id) == 2223)
L <- rbindlist(lapply(1:12, function(k) data.table(id = x$id, task = k, y = as.numeric(x[[paste0("preference_", k)]]),
  t = as.integer(x[[paste0("cal_randnum1_", k)]]), m = as.integer(x[[paste0("cal_randnum2_", k)]]),
  f = as.integer(x[[paste0("cal_randnum3_", k)]]), i = as.integer(x[[paste0("cal_randnum4_", k)]]))))
stopifnot(!anyNA(L[, .(t, m, f, i)]), L[, all(t %in% 1:6 & m %in% 1:3 & f %in% 1:5 & i %in% 1:2)], L[!is.na(y), all(y %in% 0:1)])
stopifnot(L[, uniqueN(paste(t, m, f, i))] == 180, L[!is.na(y), .N] == 8896, L[!is.na(y), uniqueN(id)] == 2206)
L <- L[!is.na(y)]
stopifnot(L[, all(t %in% 1:4 & i == 2)], L[, uniqueN(paste(t, m, f))] == 60)
tr <- c("Transfer to a user on the same network", "Transfer to a user on a different network", "Cash withdrawal from the mobile money account",
  "Payment in a store", "Saving", "Loan")
pc <- c("1%", "5%", "10%", "15%", "25%")
feetext <- function(t, f) {
  p <- pc[f]
  ifelse(t %in% 1:2, paste0("Fee of ", p, " of the transfer amount"),
  ifelse(t == 3, paste0("Fee of ", p, " of the withdrawal amount"),
  ifelse(t == 4, paste0("Fee of ", p, " of the payment amount"),
  ifelse(t == 5, paste0("Interest rate of ", p, " of the saving amount per year"),
         paste0("Fee of ", p, " of the loan amount per month")))))
}
L[, `:=`(profile = 1L, choice = as.integer(y),
  attr_transaction = tr[t], attr_amount = c("UGX 10,000", "UGX 50,000", "UGX 150,000")[m], attr_fee = feetext(t, f),
  attr_fee_info = c("Fees reported in % only", "Fees reported in % and UGX")[i])]
g <- as.character(as_factor(x$q10_gender)); g <- ifelse(g == "Male", "male", ifelse(g == "Female", "female", NA))
cv <- data.table(id = x$id, cov_gender = g, cov_age = ifelse(x$q12_age >= 15 & x$q12_age <= 90, as.integer(x$q12_age), NA_integer_),
  trial_interview_language = as.character(as_factor(x$q170a_language)))
d <- merge(L[, .(id, task, profile, choice, attr_transaction, attr_amount, attr_fee)], cv, by = "id")
d[, id := match(id, sort(unique(id)))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|choice")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hamdan_2021_mobile_money.csv"))
