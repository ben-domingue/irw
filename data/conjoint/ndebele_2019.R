##Consumer switching in the New Zealand retail electricity market, choice experiment from
##Ndebele, T., Marsh, D., & Scarpa, R. (2019). Consumer switching in retail electricity markets: Is price all
##that matters? Energy Economics, 83, 88-103. https://doi.org/10.1016/j.eneco.2019.06.012
##Deposit: Mendeley Data doi:10.17632/t58vfsrv5w (version 1), CC BY-NC 3.0. Files read: "Ndebele et.al., 2019.
##Data.csv" and "Column Headings.docx" (variable list; read as text). Level wording, units and the choice card
##come from the first author's open PhD thesis (University of Waikato, 2016, hdl.handle.net/10289/10238;
##Table 2-4 attribute table and Figure 4-5 choice card), not from the deposit; "Commands.docx" holds NLOGIT code
##(not used).
##Usage: Rscript ndebele_2019.R <dir holding the data csv> <output dir>   (file name "data.csv" or the original)
##
##Sample: 224 adults from an online panel in New Zealand, 2014 (quota-sampled on gender, age, income; the thesis
##and the paper report 224). 12 choice tasks x 3 alternatives, all respondents the same 12 tasks (fixed
##design, not blocked: the thesis states every respondent saw the same choice tasks).
##Outcome: choice = "In the scenarios that follow please only consider the information provided in deciding
##whether to switch supplier or not. Assume that any information not provided is the same for the three
##suppliers. Which supplier would you prefer?" among Your Current Supplier, Supplier A, Supplier B. Exactly one
##chosen per task; no opt-out. The status quo is shown with its own levels, so it is a profile (profile 1;
##ASC_SQ = 1); the same status-quo card for every respondent (homogeneous pivot design, absolute levels
##stored, so not a pivot problem): call wait 5 minutes, fixed rate 0 months, discount 10%, loyalty rewards Yes,
##renewable 50%, NZ ownership 50%, well-known electricity company, bill $250.
##Attributes (8; thesis Table 2-4): average time for telephone calls to be answered by a customer service
##representative (0, 5, 10, 15 minutes); fixed rate guarantee, i.e. length of time prices are guaranteed (0, 12,
##24, 36 months); prompt payment discount (0, 10, 20, 30%); loyalty rewards (No/Yes); electricity supplied from
##renewable sources (25, 50, 75, 100%); NZ ownership (25, 50, 75, 100%); supplier type; average monthly bill
##before GST, levy and discounts ($150, 200, 250, 300). The card also shows the bill after discount in
##brackets when the discount is above 0 ("$250 ($225 after discount)"; "$250" for no discount). Only the bill
##before discount is stored (attr_monthly_bill, "NZ$250"): the deposit's NET_BILL equals bill x (1 - discount)
##on every row except one task, where bill 200 with discount 30% has NET_BILL 160 instead of 140 (224 rows, all
##respondents; the authors' SAVINGS uses 160), and which figure the card showed cannot be established, so
##the after-discount amount is left to be derived from attr_monthly_bill and attr_prompt_payment_discount.
##Currency is NZ$ (the codebook's income is "2014 NZ$").
##attr_alternative holds the card's column label (Your current supplier / Supplier A / Supplier B).
##Supplier-type coding: the codebook lists TYPE2 = well-known electricity supplier and TYPE3 = well-known
##non-electricity company, but every status-quo row (which the thesis defines as a well-known electricity company,
##and the thesis' model reference category) has TYPE3 = 1 and TYPE0-2 = 0, and the thesis' design codes are 0 = well-known
##electricity, 1 = new electricity, 2 = new non-electricity, 3 = well-known non-electricity. So TYPE0 = new
##electricity company, TYPE1 = new non-electricity company, TYPE2 = well-known non-electricity company, TYPE3 =
##well-known electricity company; the codebook's TYPE2/TYPE3 descriptions are swapped. (Exactly one dummy is 1
##per alternative; checked.)
##Covariates (codebook): GENDER (1 = male, 0 = female), AGE (years), INCOME (personal annual income before tax,
##2014 NZ$), the five ethnic-group dummies (as given, not forced exclusive), LANDLORD (owns residence), CHILDREN
##(under 18 in household), ADULTS, HHSIZE, SWITCHED (switched supplier in past 24 months). Dropped: derived
##dummies and scales (education dummies, BI scores, the NEP environmental-attitude total, SAVINGS and its
##interactions, SAV/Switch indicators, attribute non-attendance copies *_A, BILL_A, NETBIL_A, RP_BILL).
##No survey weight. No identifying columns. Respondent ids are the file's id (1..224).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- list.files(raw, pattern = "csv$", full.names = TRUE); stopifnot(length(f) == 1)
d <- fread(f)
stopifnot(nrow(d) == 224 * 12 * 3, d[, uniqueN(id)] == 224, d[NET_BILL != round(BILL * (1 - DISC / 100)), .N] == 224)
ty <- as.matrix(d[, .(TYPE0, TYPE1, TYPE2, TYPE3)]); stopifnot(all(rowSums(ty) == 1))
stype <- c("New electricity company", "New non-electricity company", "Well-known non-electricity company",
           "Well-known electricity company")[max.col(ty, ties.method = "first")]
stopifnot(d[ALTI == 1, all(ASC_SQ == 1)], d[ALTI != 1, all(ASC_SQ == 0)], d[ALTI == 1, all(TYPE3 == 1)])
bill <- sprintf("NZ$%d", d$BILL)
o <- data.table(id = as.integer(d$id), task = as.integer(d$TASK), profile = as.integer(d$ALTI), choice = as.integer(d$CHOICE),
  attr_alternative = c("Your current supplier", "Supplier A", "Supplier B")[d$ALTI],
  attr_call_waiting_time = sprintf("%d minutes", d$TIME), attr_fixed_rate_guarantee = sprintf("%d months", d$FIXED),
  attr_prompt_payment_discount = sprintf("%d%%", d$DISC), attr_loyalty_rewards = ifelse(d$REWARD == 1, "Yes", "No"),
  attr_renewable_share = sprintf("%d%%", d$RENEW), attr_nz_ownership = sprintf("%d%%", d$OWN),
  attr_supplier_type = stype, attr_monthly_bill = bill,
  cov_gender = ifelse(d$GENDER == 1, "male", "female"), cov_age = as.integer(d$AGE), cov_income_nzd = as.integer(d$INCOME),
  cov_nz_european = as.integer(d$NZ_EURO), cov_maori = as.integer(d$MAORI), cov_asian = as.integer(d$ASIAN),
  cov_pacific = as.integer(d$PACIFIC), cov_other_ethnic = as.integer(d$OTHER), cov_owns_residence = as.integer(d$LANDLORD),
  cov_children_under18 = as.integer(d$CHILDREN), cov_adults = as.integer(d$ADULTS), cov_household_size = as.integer(d$HHSIZE),
  cov_switched_24m = as.integer(d$SWITCHED))
stopifnot(o[, sum(choice), .(id, task)][, all(V1 == 1)], o[, .N, .(id, task)][, all(N == 3)], !anyNA(o$attr_monthly_bill))
setorder(o, id, task, profile)
fwrite(o, file.path(out, "ndebele_2019_electricity_switching.csv"))
