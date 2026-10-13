##Clothing detergent profiles ranked by preference: ranking of 10 fixed product profiles, Durban (South Africa)
##Kamwendo, A. (2021). Clothing detergent category data [Data set]. Mendeley Data, v1. (Phase 2 questionnaire of a
##Durban University of Technology marketing study; no paper DOI listed.)
##Deposit: doi:10.17632/5bkgk7jzzs, CC BY 4.0 (Mendeley data_licence field). Files read: "Phase 2 Data Set.xlsx" (saved as
##data.xlsx; sheet Sheet1; the clothing-detergent columns only), "Clothing Detergents Poster.pdf" (the 10 profiles, an
##image: levels read by eye from a 200 dpi render, text labels are printed under each picture) and "Questionnaire 2.pdf"
##(pdftotext). Usage: Rscript kamwendo_2021.R <dir holding data.xlsx> <output dir>
##
##Respondents (sample not described in the deposit; the questionnaire's residence options include university residence) were shown a poster with 10 fixed
##clothing-detergent profiles and ranked them from most preferred (1st) to least preferred (10th). Fixed design: all
##respondents ranked the same 10 profiles, there is no randomization. Attributes (5, text printed on the poster):
##durability (2 weeks, 3 weeks: shown as a large numeral over "WEEKS"), strength (MODERATELY STRONG PRODUCT, VERY STRONG
##PRODUCT), price (MODERATELY PRICED, PRICED LOW; with a Rands & Cents picture), form and size (LIQUID 2l, LIQUID 1l, POWDER
##1 kg, POWDER 2 kg: size shown in the picture), scent (OCEANIC SCENT, FLORAL SCENT). Profile levels by poster number 1-10
##(durability weeks / strength / price / form-size / scent): 1: 2/mod/mod/L2l/oceanic; 2: 3/mod/mod/P1kg/floral;
##3: 3/mod/low/L1l/oceanic; 4: 2/very/low/P1kg/oceanic; 5: 3/very/low/L2l/floral; 6: 2/mod/low/P2kg/floral;
##7: 2/very/mod/L1l/floral; 8: 3/very/mod/P2kg/oceanic; 9: 3/very/low/L2l/oceanic; 10: 2/very/mod/P1kg/oceanic.
##Outcome: rating = the rank given to the profile, 1 = most preferred, 10 = least preferred (never inverted); each
##respondent's ten ranks are a permutation of 1-10. The sheet's columns "Profile 1" ... "Profile 10" are read as the rank
##given to each profile: INFERRED from the headers (the questionnaire itself collected the inverse form, "write the profile
##number in the box for 1st choice ... 10th choice"; the deposit does not say it was converted). task = 1, profile = poster
##number. No choice column.
##Rows kept: respondents whose ten values are a permutation of 1-10 (203 of 216 sheet rows; the others are empty or have missing or
##repeated ranks and are dropped). IDs re-keyed to integers in sheet order.
##Covariates: cov_gender_code (1/2 as in the sheet; by the questionnaire's option order 1 = male, 2 = female, not stated as codes
##in the deposit), cov_generation_code (2/3/4 = Generation X/Y/Z by the questionnaire's option order 1946-64, 1965-76, 1977-94,
##1995-97; code 1 does not occur). Dropped: occupation, residence, income and living-standards-measure columns
##(unlabelled codes/derived).
suppressMessages({library(readxl); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(suppressWarnings(suppressMessages(read_excel(file.path(raw, "data.xlsx"), col_names = FALSE))))
stopifnot(as.character(unlist(x[3, 8:17])) == paste("Profile", 1:10))
y <- x[4:nrow(x)]
r <- suppressWarnings(as.matrix(sapply(y[, 8:17], as.numeric)))
ok <- apply(r, 1, function(v) !anyNA(v) && all(sort(v) == 1:10))
stopifnot(sum(ok) == 203)
y <- y[ok]; r <- r[ok, , drop = FALSE]
prof <- data.table(profile = 1:10,
  attr_durability = c("2 weeks","3 weeks","3 weeks","2 weeks","3 weeks","2 weeks","2 weeks","3 weeks","3 weeks","2 weeks"),
  attr_strength = c("Moderately strong product","Moderately strong product","Moderately strong product","Very strong product","Very strong product","Moderately strong product","Very strong product","Very strong product","Very strong product","Very strong product"),
  attr_price = c("Moderately priced","Moderately priced","Priced low","Priced low","Priced low","Priced low","Moderately priced","Moderately priced","Priced low","Moderately priced"),
  attr_form_size = c("Liquid 2l","Powder 1 kg","Liquid 1l","Powder 1 kg","Liquid 2l","Powder 2 kg","Liquid 1l","Powder 2 kg","Liquid 2l","Powder 1 kg"),
  attr_scent = c("Oceanic scent","Floral scent","Oceanic scent","Oceanic scent","Floral scent","Floral scent","Floral scent","Oceanic scent","Oceanic scent","Oceanic scent"))
n <- nrow(y)
d <- data.table(id = rep(seq_len(n), each = 10), task = 1L, profile = rep(1:10, times = n), rating = as.integer(t(r)),
                cov_gender_code = rep(as.integer(y[[3]]), each = 10), cov_generation_code = rep(as.integer(y[[2]]), each = 10))
d <- merge(d, prof, by = "profile")
setcolorder(d, c("id", "task", "profile", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kamwendo_2021_detergent_ranking.csv"))
