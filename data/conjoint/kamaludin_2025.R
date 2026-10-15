##Refrigerator energy-label choice experiment (Malaysia) from
##Kamaludin, M., Razali, M. A. S., Haron, N. F., Abd Aziz, A., & Samdin, Z. (2025). Household preferences towards
##energy labels in Malaysia: A pathway to sustainability. Journal of Sustainability Science and Management, 20(1), 1-22.
##https://doi.org/10.46754/jssm.2025.01.001
##Data: Mendeley Data doi:10.17632/5bhwp4t8xb.1, CC BY 4.0 (Mendeley public API, data_licence). File read:
##"Survey Data.xlsx" (one sheet; row 1 is blank, row 2 holds the headers; 9,588 data rows).
##Level text: the deposit stores codes 1-4 (price in RM); the displayed wording is from the article's Table 1 and
##Table 2 (an example choice set), mapped by level order: code k = k-th level listed in Table 1.
##Usage: Rscript kamaludin_2025.R <dir holding the xlsx, any name ending .xlsx> <output dir>
##
##799 heads of household, rural and urban Malaysia (face-to-face, written questionnaire read out by 5 enumerators,
##Nov 2021 - Feb 2022; article n = 799). Each of 4 choice sets (file column card): Option A, Option B and a
##"No-option" (file choset 3, all attributes at their lowest code 1 and price 950 = not an alternative with levels:
##opt_out = yes, its rows are dropped; chosen in 171 of 3,196 sets). Outcome: tick one option (article Table 2:
##"Please tick your choice"; the no-option is added "if the condition matches the respondent's actual decision").
##Design: orthogonal 4x4x4x3 (192 combinations), 16 choice sets in 4 blocks (article); the block of a respondent is
##not in the deposit. task = card 1-4 (assumed the order shown), profile = choset 1/2 (Option A / B).
##Attributes (Table 1): energy star rating (2-star, 3-star, 4-star, 5-star); energy consumption = average energy
##consumption cost per year (RM132.70, RM106.20, RM84.92, RM67.98); energy saving = total energy savings per year
##compared with the lowest 2-star rated products ("No possibility of saving", "Saved RM26.50 per year", "Saved RM47.78
##per year", "Saved RM64.72 per year"); price of the refrigerator (RM950, RM1,400, RM2,000). The mapping of codes to
##levels assumes the file's codes follow the Table 1 order (the file's code 1 on the no-option is the first level).
##Restrictions: none documented (orthogonal design). Level weights: the article says the design is balanced, but the
##shares among the 6,392 shown profiles are unequal (star levels 22-28%, price RM950 34%, RM1,400 31%, RM2,000 34%
##after the no-option rows are removed), so recorded as observed. Attribute order fixed (assumed).
##Covariates kept (codes, no codebook, hence _code): cov_age (years), cov_gender_code (0/1/2), cov_education_code (1-6),
##cov_income_resp_rm (file inc_res, a number of Ringgit; period not stated).
##Dropped: id_all/index counters, marital status, household composition, area of living, job, ethnicity.
##N vs paper: 799 respondents as in the article; the sheet's header row is read as an NA row and dropped.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fn <- list.files(raw, pattern = "[.]xlsx$", full.names = TRUE)[1]
x <- as.data.table(suppressMessages(read_excel(fn, sheet = 1, skip = 1, col_names = c("id_all","res_id","index","card","choset","cset",
  "choice","estar","econ","esave","price","gender","age","marital","hh_k","hh_r","hh_d","hh_j","Live_area","job","edu","ethnic","inc_res"),
  col_types = "numeric")))
x <- x[!is.na(res_id)]
stopifnot(nrow(x) == 9588, uniqueN(x$res_id) == 799, x[, .N, res_id][, all(N == 12)])
stopifnot(x[, sum(choice), .(res_id, card)][, all(V1 == 1)], x[choset == 3, all(estar == 1 & econ == 1 & esave == 1 & price == 950)])
x[, id := match(res_id, sort(unique(res_id)))]
ST <- c("2-star","3-star","4-star","5-star"); EC <- c("RM132.70","RM106.20","RM84.92","RM67.98")
SV <- c("No possibility of saving","Saved RM26.50 per year","Saved RM47.78 per year","Saved RM64.72 per year")
p <- x[choset < 3]
d <- p[, .(id, task = as.integer(card), profile = as.integer(choset), choice = as.integer(choice),
  attr_energy_star = ST[estar], attr_energy_consumption = EC[econ], attr_energy_saving = SV[esave],
  attr_price = paste0("RM", formatC(price, format = "d", big.mark = ",")),
  cov_age = ifelse(age >= 15 & age <= 100, as.integer(age), NA_integer_), cov_gender_code = as.integer(gender),
  cov_education_code = as.integer(edu), cov_income_resp_rm = as.integer(inc_res))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^task$|^profile$")]), d[, .N, .(id, task)][, all(N == 2)],
  d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kamaludin_2025_refrigerator_energy_label.csv"))
