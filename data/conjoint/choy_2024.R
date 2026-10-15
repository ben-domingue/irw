##Shark fin soup choice in Singapore: online discrete choice experiment, from the Zenodo deposit "Data for:
##Understanding consumers to inform market interventions for Singapore's shark fin trade" (Choy, Booth & Verissimo).
##Article: Choy, C., Booth, H., & Verissimo, D. (2024). People and Nature, 6, 733-748, doi:10.1002/pan3.10590.
##Deposit: doi:10.5281/zenodo.10421161 (concept doi 10.5281/zenodo.10421160), CC BY 4.0 (Zenodo record licence cc-by-4.0).
##Files read: "Compiled data.xlsx", sheet "CE_20 Jun" (long: one row per option); "Chi-square goodness of fit tests.xlsx"
##(only to confirm the gender coding). Not read: "35433 Final CEOE Data (N=300) V2.xlsx" (password-protected; the open
##Compiled file is its twin).
##Usage: Rscript choy_2024.R <dir holding the xlsx files> <output dir>
##
##Sample: 300 Singapore residents (online panel, Rakuten Insight, March-April 2022) who had eaten shark fin in the past
##3 years; N = 300 equals the article's final sample after quality control. 15 choice sets per respondent from a
##D-efficient Bayesian design (Ngene); question ordering was randomized (article), so the set number (1-15, the number in
##the OPTION label "1a", "1b", ...) is the design's set index, NOT necessarily the order shown: task_source = inferred.
##Each set: three shark fin soup alternatives (a, b, c = profile 1, 2, 3) plus a fixed "No shark fin" alternative
##(OPTION "No shark fin", attribute codes -999). The none alternative has no attribute levels, so it is not a profile
##row; it is the opt-out (opt_out = yes). Exactly one of the four is chosen in every set (verified).
##Choice: which shark fin soup the respondent would purchase (article 2.2; exact on-screen wording not in the deposit).
##Attributes (5; Table 1 of the article; the data hold numeric codes, 0 = the article's reference level, which is the
##first level listed in Table 1; codes taken in Table 1 order; the MNL signs in the article were reproduced with this
##mapping in the check below: price negative, responsible and lab-cultured source positive):
##  PRICE 0-4 = SGD $10, SGD $50, SGD $100, SGD $150, SGD $200
##  SIZE 0/1 = Small, Large     QUALITY (texture and quality of fin) 0/1 = Loose shark fin filaments, Whole, intact shark fin
##  MENU 0/1/2 = As part of set package menu, A la carte menu (article spells "A la carte" with a grave accent), Chef's Specialty dish
##  SOURCE 0/1/2 = Wild caught, unmanaged fishery; Wild caught, responsible fishery; Lab cultured (no sharks killed)
##Level text is Table 1 of the article, mapped by code order; the deposit stores only codes (no codebook). Restrictions on
##combinations: none stated (Bayesian D-efficient design; no rule given). Level probabilities: not stated.
##Respondent id: RESP (1-300, re-used as id); the file's ID column (original panel serial numbers 12-479) is dropped.
##Covariates: gender (D3_GENDER 1 = male, 2 = female: 180/120 = 60% male as the article reports; the Chi-square workbook
##lists male 60%, female 40%); age, education and income band are kept as codes with _code suffix (no codebook:
##D2_AGE 1-9, D6_EDUCATION 1-6, D7_INCOME 1-11; the 9 age bands are finer than the article's 5, so they cannot be mapped).
##Dropped: Q1-Q9 attitude and consumption items, derived scale averages, dialect dummies, religion and race codes (no labels).
##No survey weight. No identifying columns (no IPs, names, platform ids).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_excel(file.path(raw, "compiled.xlsx"), sheet = "CE_20 Jun"))
stopifnot(nrow(d) == 300 * 15 * 4, uniqueN(d$RESP) == 300)
d[, set := suppressWarnings(as.integer(sub("[abc]$", "", OPTION)))]
d[, alt := ifelse(OPTION == "No shark fin", 0L, match(sub("^[0-9]+", "", OPTION), c("a", "b", "c")))]
d[OPTION == "No shark fin", set := NA]
d[, set := nafill(set, type = "locf"), by = RESP]   # none row follows 'c' of its set
stopifnot(!anyNA(d$alt), d[, .N, .(RESP, set)][, all(N == 4)], d[, sum(CHOICE), .(RESP, set)][, all(V1 == 1)])
d[, none_chosen := any(CHOICE == 1 & alt == 0L), .(RESP, set)]
p <- d[alt > 0]
stopifnot(nrow(p) == 300 * 15 * 3, all(p$PRICE %in% 0:4), all(p$SIZE %in% 0:1), all(p$QUALITY %in% 0:1),
          all(p$MENU %in% 0:2), all(p$SOURCE %in% 0:2))
tx <- function(x, labs) labs[x + 1L]
o <- p[, .(id = as.integer(RESP), task = set, profile = alt, choice = as.integer(CHOICE))]
o[, attr_price := tx(p$PRICE, c("SGD $10", "SGD $50", "SGD $100", "SGD $150", "SGD $200"))]
o[, attr_fin_size := tx(p$SIZE, c("Small", "Large"))]
o[, attr_texture_quality := tx(p$QUALITY, c("Loose shark fin filaments", "Whole, intact shark fin"))]
o[, attr_menu_type := tx(p$MENU, c("As part of set package menu", "A la carte menu", "Chef's Specialty dish"))]
o[, attr_fin_source := tx(p$SOURCE, c("Wild caught, unmanaged fishery", "Wild caught, responsible fishery", "Lab cultured (no sharks killed)"))]
o[, cov_gender := ifelse(p$D3_GENDER == 1, "male", ifelse(p$D3_GENDER == 2, "female", NA))]
o[, cov_age_code := as.integer(p$D2_AGE)]
o[, cov_education_code := as.integer(p$D6_EDUCATION)]
o[, cov_income_code := as.integer(p$D7_INCOME)]
o[, trial_none_chosen := as.integer(p$none_chosen)]
setorder(o, id, task, profile)
stopifnot(!anyNA(o[, .SD, .SDcols = patterns("^attr_")]), o[, uniqueN(cov_gender), id][, all(V1 == 1)],
          o[, .N, .(id, task)][, all(N == 3)], uniqueN(o$id) == 300, o[, mean(cov_gender == "male")] > 0.59)
##Spot check: conditional logit with a none constant (survival::clogit; price, size, quality, menu linear in code, source
##dummies as in the article's Table 2): price coefficient should be about -0.26, responsible-source about +0.53.
if (requireNamespace("survival", quietly = TRUE)) {
  library(survival)
  m <- copy(d)
  m[, ch := as.integer(CHOICE)]
  m[, `:=`(none = as.integer(alt == 0L), price = ifelse(alt == 0L, 0, PRICE), size = ifelse(alt == 0L, 0, SIZE),
            qual = ifelse(alt == 0L, 0, QUALITY), menu = ifelse(alt == 0L, 0, MENU),
            srcR = as.integer(alt > 0 & SOURCE == 1), srcL = as.integer(alt > 0 & SOURCE == 2), grp = paste(RESP, set))]
  f <- survival::clogit(ch ~ none + price + size + qual + menu + srcR + srcL + survival::strata(grp), data = m)
  message("MNL check (article: none -1.161, price -0.261, size 0.036, quality 0.006, menu -0.023, resp 0.531, lab 0.266):")
  print(round(coef(f), 3))
}
dir.create(out, showWarnings = FALSE, recursive = TRUE)
fwrite(o, file.path(out, "choy_2024_shark_fin.csv"))
