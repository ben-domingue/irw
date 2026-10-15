##Biofortified / genetically engineered gari (cassava) choice experiment, Nigeria, from
##Akinwehinmi, T. O., Gassler, B., & Teuber, R. (2026). Consumer preferences for genetically engineered
##foods in Nigeria: does process information matter? Q Open. https://doi.org/10.1093/qopen/qoag007
##(authors: Akinwehinmi is the dataset author, Gassler and Teuber are listed as contributors).
##Deposit: JLUpub doi:10.22029/jlupub-20740, CC BY-NC 4.0 (dc.rights.uri creativecommons.org/licenses/by-nc/4.0/).
##Files read: biofortification_data.csv (a section-header row precedes the variable names: skip = 1) and
##README-file .xlsx (codebook, sharedStrings read as text); authors' Apollo code read as text for the
##design (4_code_full_attendance_mixl_nutrition.R: alt 3 = status quo with its own price/dummies).
##Usage: Rscript akinwehinmi_2026.R <dir holding biofortification_data.csv> <output dir>
##
##235 households (face to face, Ondo and Oyo States, Apr-Jun 2022; article N 235 = 116 + 119), 8 choice
##tasks each (16 tasks in 2 blocks of 8, D-efficient idefix design), three alternatives per task:
##two biofortified gari options and a status-quo gari. The status quo is a profile: the data record its
##levels (0% vitamin A, 0% iron, high starch, conventional breeding, 300 Naira) and the article calls it
##"non-biofortified gari available in the market constrained to 0 percent VA and iron"; the article does
##not give its on-screen text, so its levels are INFERRED from the all-zero dummies and Price3 = 300.
##No opt-out. choice: which of the three alternatives was chosen (the question wording is not given in the
##article or deposit). Task order and profile order: the data hold no task index; task = row order within
##respondent (inferred; each respondent has 8 rows) and profile = option 1/2/3.
##Source ids: data row 825 (the first row of the id-104 block) carries id 278 but has the same location, gender, age, block and
##information arm as the 7 rows of id 104; id 278 occurs nowhere else, so it is read as respondent 104's
##first task (one 8-row respondent; 235 respondents as in the article). INFERRED.
##Attributes (level text from Table 1 of the article, paraphrased where the displayed wording is not given):
##  vitamin A: 60% or 100% of the estimated average requirement (EAR) (status quo 0%): "60% of EAR".
##  iron: 0%, 25% or 50% of EAR. starch: Low / High. breeding method: Conventional / Genetic Modification /
##  Gene Editing. price: 300 / 500 / 700 Naira per 1 kg of gari (status quo 300). The deposit stores dummies
##  (VAA/VAB, IRA/IRB, GM/GE, LowStarch) and the numeric price; text is rebuilt from the codebook definitions.
##Restrictions (article): at least 60% VA in the biofortified options and conventionally bred options have 0%
##iron; observed in the data. Level weights: unequal (price 300 in 50% of rows, as the status quo is always 300).
##Trial: trial_info_arm = information group (between respondents): Nutrition information (video on VA and iron
##deficiency; 116 respondents) vs Nutrition + scientific-method information (119). The README says
##consumer 1/2 but the data hold 2/3 with info_risk = 1 for 2 and info_risk_method = 1 for 3; mapped by the
##info dummies. trial_block = DCE block 1/2. The authors fit models by arm; one table, as the same design.
##Covariates (codebook): cov_gender (1 Male, 2 Female), cov_age (years), cov_education (1 None, 2 Primary,
##3 Secondary, 4 OND/NCE, 5 HND/BSC, 6 Msc/PhD), cov_location (1 Akure, 2 Ondo Rural, 4 Ibadan, 5 Oyo Rural).
##Dropped: all interaction/derived columns, stated non-attendance dummies, awareness/knowledge items,
##income, purchase habits.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "biofortification_data.csv"), skip = 1)
stopifnot(nrow(x) == 1880)
stopifnot(sum(x$id == 278) == 1); x[id == 278, id := 104L]
x[, task := seq_len(.N), id]
stopifnot(uniqueN(x$id) == 235, x[, .N, id][, all(N == 8)])
stopifnot(x[, uniqueN(Location), id][, all(V1 == 1)], all(x$Choice %in% 1:3))
long <- rbindlist(lapply(1:3, function(k) {
  g <- function(n) x[[paste0(n, k)]]
  data.table(id = x$id, task = x$task, profile = k, choice = as.integer(x$Choice == k),
    attr_vitamin_a = fifelse(g("VAB") == 1, "100% of EAR", fifelse(g("VAA") == 1, "60% of EAR", "0% of EAR")),
    attr_iron = fifelse(g("IRB") == 1, "50% of EAR", fifelse(g("IRA") == 1, "25% of EAR", "0% of EAR")),
    attr_starch = fifelse(g("LowStarch") == 1, "Low", "High"),
    attr_breeding_method = fifelse(g("GM") == 1, "Genetic Modification", fifelse(g("GE") == 1, "Gene Editing", "Conventional")),
    attr_price = paste(g("Price"), "Naira per 1 kg"),
    trial_info_arm = fifelse(x$info_risk_method == 1, "Nutrition + scientific method information", "Nutrition information"),
    trial_block = x$block,
    cov_gender = c("male", "female")[x$gender], cov_age = as.integer(x$age),
    cov_education = c("None", "Primary", "Secondary", "OND/NCE", "HND/BSC", "Msc/PhD")[x$education_level],
    cov_location = c("Akure", "Ondo Rural", NA, "Ibadan", "Oyo Rural")[x$Location])
}))
stopifnot(x[, all(info_risk + info_risk_method == 1)], !anyNA(long[, .(attr_vitamin_a, attr_price, cov_gender)]))
setorder(long, id, task, profile)
fwrite(long, file.path(out, "akinwehinmi_2026_gari_biofortified.csv"))
