##Researchers' purchase probability for chemical compounds: rated stimulus cards, Korean Chemical Bank users
##Sung, B., Park, K.-M., Park, C. G., Kim, Y.-H., Lee, J., & Jin, T.-E. (2023). What drives researcher
##preferences for chemical compounds? Evidence from conjoint analysis. PLOS ONE, 18(11), e0294576.
##https://doi.org/10.1371/journal.pone.0294576
##Raw data: figshare doi:10.6084/m9.figshare.23122511, CC BY 4.0. Files read: final_total_data.csv (saved as
##d.csv), "Data for descriptive statistics.csv" (saved as desc.csv), Conjoint_code.ipynb (read as text: it shows
##which dummies the analysis uses; no level text). Level text comes from the paper's Table 1 (fetched from the
##PMC full text, europepmc PMC10681187), not from the deposit.
##Usage: Rscript sung_2023.R <dir holding d.csv, desc.csv> <output dir>
##
##130 Korean researchers who use compounds from the Korean Chemical Bank (the paper's usable N = 130 of 151
##responses), each rating 16 fixed stimulus cards (orthogonal plan of 18 profiles with 2 holdouts excluded;
##all respondents saw the same 16 cards in the same row order). Attributes and levels (paper Table 1):
##new functionality (Low, High); type (Deposited by researchers, Bought abroad); structure database (Not provided,
##Provided); drug action data (Not provided, Provided (only in literature), Provided (only by KCB)); screening
##service (Not provided, Provided); price per 96-well plate (40,000 KRW, 100,000 KRW, 300,000 KRW).
##The deposit stores one-hot dummies (POTNETIAL1/2, TYPE1/2, INFODB1/2, DATA1-3, SERVICE1/2) and PRICE in KRW;
##dummy 1/2/3 = level 1/2/3 of the paper's Table 1 (the notebook's part-worth code is consistent with this order:
##DATA1 = -(DATA2 + DATA3)). The dummy-to-level mapping rests on that numbering convention, not on a label in the deposit.
##Outcome: rating = y, the purchase probability of the compound with that profile, 0-10 (paper: "purchase
##probability (ranging between zero and 10)"; higher = more likely to purchase), stored raw. The exact question
##wording is not given (paraphrase). task = row order within respondent (inferred; display order not documented).
##Covariates (desc.csv): cov_gender, cov_age_group (bands as in the file), cov_institute_type, cov_main_use. desc.csv has
##130 rows with IDs up to 138, so it cannot be joined on ID; the authors' notebook attaches it to the per-respondent
##table by row position (des_data.join(cluster_map)), and this script does the same (inferred alignment).
##Dropped: nothing else (no identifiers). Ids are the deposit's Index (1-130).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "d.csv")); s <- fread(file.path(raw, "desc.csv"))
setorder(x, Index)
stopifnot(uniqueN(x$Index) == 130, nrow(s) == 130, nrow(x) == 130 * 16)
pick <- function(cols, labs) labs[max.col(as.matrix(x[, ..cols]), ties.method = "first")]
stopifnot(x[, all(POTNETIAL1 + POTNETIAL2 == 1 & TYPE1 + TYPE2 == 1 & INFODB1 + INFODB2 == 1 & DATA1 + DATA2 + DATA3 == 1 & SERVICE1 + SERVICE2 == 1)])
d <- data.table(id = x$Index, task = rowid(x$Index), profile = 1L, rating = as.integer(x$y),
  attr_new_functionality = pick(c("POTNETIAL1", "POTNETIAL2"), c("Low", "High")),
  attr_type = pick(c("TYPE1", "TYPE2"), c("Deposited by researchers", "Bought abroad")),
  attr_structure_database = pick(c("INFODB1", "INFODB2"), c("Not provided", "Provided")),
  attr_drug_action_data = pick(c("DATA1", "DATA2", "DATA3"), c("Not provided", "Provided (only in literature)", "Provided (only by KCB)")),
  attr_screening_service = pick(c("SERVICE1", "SERVICE2"), c("Not provided", "Provided")),
  attr_price = paste(formatC(x$PRICE, format = "d", big.mark = ","), "KRW"))
stopifnot(all(d$attr_price %in% c("40,000 KRW", "100,000 KRW", "300,000 KRW")), all(d$rating %in% 0:10))
ids <- sort(unique(x$Index))
cv <- data.table(id = ids, cov_gender = tolower(s$Gender), cov_age_group = s$Age, cov_institute_type = s$`Institute type`, cov_main_use = s$`Main use of chemical compounds`)
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "sung_2023_chemical_compounds.csv"))
