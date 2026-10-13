##Sustainable-product choice experiment (Swiss Environmental Panel, wave 14) from
##Gomm et al. (2026). Comparing and
##combining theory of planned behavior and dragons of inaction to explain pro-environmental
##consumption behavior. Sustainable Production and Consumption.
##https://doi.org/10.1016/j.spc.2026.04.008   (full author list not read; the Zenodo record lists
##Blumer, Czellar, Haasova, Kuhne, Schubert, Bernauer as depositors)
##Replication data: Zenodo doi:10.5281/zenodo.20008483 (concept DOI; version record 20008484),
##CC BY 4.0, no restricted files. Files read: w14_conjoint.RData (object dfconj) and, as text,
##Dragons_ReplicationCode_Gomm.R (the authors' English recodes, the price mapping used for
##willingness to pay). SEP_w14_reduced.RData was not used (no conjoint variables, no weight).
##Usage: Rscript gomm_2026.R <dir holding w14_conjoint.RData> <output dir>
##
##Different experiment from brugge_2024_circular_products (wave 8, other products and
##attributes): this is wave 14 (2024-25), price x environmental impact for six products.
##6,535 of the 6,833 panel members in the file have conjoint rows (298 have none and are absent
##here); 6 tasks x 2 profiles. Each respondent was randomly assigned one product category
##(w14_treat_product: Food products / Electronic devices / Clothes) and in each round (task) a
##product within it (w14_treat_c<round>_product; checked to equal `product` on every row):
##Tomatoes (1kg), Chocolate (100g); Laptop, Smartphone; Jacket, Shirt. The product is the same
##on both profiles of a task, so it is a task-level detail (trial_product, trial_product_category),
##not a profile attribute. Two randomized profile attributes: price (5 levels) and environmental
##impact (5 levels), a full 5x5 cross (all 25 pairs occur, ~3,100 each) - no restrictions found.
##Level text is the authors' English factor labels ("Very low price" ... "Very high price";
##"Very low" ... "Very high" impact); the authors map the price labels to product-specific CHF
##amounts for willingness to pay (e.g. smartphone 450/475/500/525/550; the amounts shown to
##respondents are not documented in the deposit, so the labels are stored).
##Outcomes: choice = dfconj$choice (1 = this profile chosen; exactly one per task, checked;
##question wording not deposited, paraphrase "which of the two products would you buy"; no
##opt-out); rating = dfconj$rating_num, the 1-7 likelihood item w14_c<k>_p<j>_q31x2 (variable
##label "conjoint_c<k>_prob_<j>"; value labels 1 Very unlikely ... 4 Neither likely, nor
##unlikely ... 7 Very likely; verified identical to the source item on every row). The authors'
##`rating` (0/1 = rating_num >= 5) is a derived dummy and is dropped.
##Attribute order: not recorded. Profile order = source `measure` (1/2). Task = `round`.
##Covariates (authors' English factor labels): cov_gender (Male/Female -> male/female),
##cov_age (age_num, 18-93; NA for 310 respondents), cov_age_group, cov_education (educ text),
##cov_household_income (inc text), cov_agglomeration (agglo). id = PubId, the panel's public
##respondent number (not a platform id). Dropped: all derived scales/indices (TPB, DIPB, *_fs,
##*_rescaled, *_f terciles, lr tercile), attitude item batteries without wording, ev_* items.
##No survey weight in the deposit. N vs paper: not checked against the article (not retrieved).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "w14_conjoint.RData"), envir = e); x <- as.data.table(e$dfconj)
x <- x[!is.na(measure)]
pl <- c("Tomatoes (1kg)", "Chocolate (100g)", "Jacket", "Shirt", "Laptop", "Smartphone")
tp <- function(v) as.integer(unclass(v))
prod_chk <- mapply(function(r, i) pl[tp(x[[paste0("w14_treat_c", r, "_product")]][i])], x$round, seq_len(nrow(x)))
stopifnot(all(prod_chk == as.character(x$product)))
cat_lab <- c("Food products", "Electronic devices", "Clothes")
d <- data.table(id = as.integer(x$PubId), task = as.integer(x$round), profile = as.integer(x$measure),
                choice = as.integer(x$choice), rating = as.integer(x$rating_num),
                attr_price = as.character(x$price), attr_impact = as.character(x$impact),
                trial_product = as.character(x$product),
                trial_product_category = cat_lab[tp(x$w14_treat_product)],
                cov_gender = c("Male" = "male", "Female" = "female")[as.character(x$gender)],
                cov_age = as.integer(x$age_num), cov_age_group = as.character(x$age),
                cov_education = as.character(x$educ), cov_household_income = as.character(x$inc),
                cov_agglomeration = as.character(x$agglo))
stopifnot(!anyNA(d$choice), !anyNA(d$attr_price), !anyNA(d$attr_impact), d[, .N, .(id, task)][, all(N == 2)])
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gomm_2026_sustainable_products.csv"))
