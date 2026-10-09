##Farm support-payment factorial survey (Scotland) from
##Glenk, K., Liebe, U., Burns, J., & Thomson, S. (2024). Perceived legitimacy of agricultural
##support schemes: An investigation using factorial survey experiments. Q Open, 4(2), qoae016.
##https://doi.org/10.1093/qopen/qoae016
##Data: Zenodo record 11035265 (doi 10.5281/zenodo.11035265), CC BY 4.0. File read:
##Glenk_vignette_agric_acceptance_data.xlsx, sheet A1 (data) and sheet Datamap (the survey
##program's question wording and value labels). Glenk_vignette_agric_acceptance_code.do read
##as text (attribute-level summary, outcome anchors, reshape). Article (OUP HTML) for the
##design, Table 2 (outcomes) and Table A1 (levels, payment amounts).
##Usage: Rscript glenk_2024.R <dir holding the xlsx> <output dir>
##
##2,011 Scottish adults (online access panel, quotas on age and gender, Jan-Feb 2022), each
##randomly allocated to one farm type (dConjoint: beef 504, dairy 503, sheep 501, cropping
##503; the product named in the questions follows it: beef, dairy products, lamb,
##potatoes) and shown 6 text vignettes of a farmer drawn without replacement from 72
##(orthogonal fold-over design, article). One table: the authors pool the four farm types
##(treatment dummies in their models); farm type is trial_farm_type.
##Task/profile: one vignette per task, profile = 1. The deposit stores the 6 vignettes in
##72 situation slots (dAttribute*_k, B3*_k, k = design row) with no display order, so
##task = rank of k within respondent (INFERRED, not the display order); trial_design_row
##= k (1-72).
##Attribute text = the Datamap value labels piped into the vignette text (template not
##deposited; article Fig. 2 is an image): gender "Mr."/"Ms." (the .do comment says
##"Mrs."), started farming "5/10/20 years ago", qualification, size, production type,
##production level, animal welfare (beef/dairy/sheep: standard/good/exceptional) or product
##quality (cropping: the .do's level summary, e.g. "poor and is mainly used for livestock
##feed"; the Datamap carries only the welfare labels) -> two columns, the other one
##"(not shown)" by design; biodiversity "poor/average/good" (Datamap; the article's
##Table A1 says "poor/moderate/good" and the .do "less land/moderate/good": CONFLICT, the
##program labels are used), carbon footprint of farm and per unit of output, financial
##situation, payment change (attr 12, e.g. "decrease of 50%") and the payment amount
##sentence piped from pipe_A13row<1-18> for the farm type (attr 13, e.g. "decrease from
##currently £10k to £5k per year"; Datamap labels read by the script; row = (size - 1) x 6 +
##change, checked; amounts agree with article Table A1).
##Outcomes (1-11, stored raw; Datamap wording; anchors from Datamap / article Table 2):
##  rating_accept   "How acceptable are the described changes in payments to this farmer
##    for you?" 1 Fully unacceptable, 6 neither, 11 Fully acceptable (B3A)
##  rating_fair     "The farmer described, [Mr./Ms. X], will obtain [£Y] per year in support
##    payments. Do you think this amount is an unfairly low level of income support, a fair
##    level of income support, or an unfairly high level of income support?" 1 Unfairly low,
##    6 fair, 11 Unfairly high (B3B; NOT reversed here; the authors reverse it)
##  rating_supply   "How happy would you be for [Mr./Ms. X] to supply you (through a shop or
##    market) with [product]?" 1 Very unhappy, 11 Very happy (B3C); NA when the respondent
##    ticked "I do not buy or eat [product]" (1,140 vignettes)
##  rating_petition "Imagine that a government income support scheme for farmers similar to
##    [Mr./Ms. X] would be discontinued. How willing would you be to write to your local MSP
##    to lobby on behalf of this farmer for the continuation of their support payments?"
##    1 Not willing at all, 11 Very willing (B3D)
##N: all 2,011 kept; the article's models use 1,951 (60 missing perceived financial
##situation or environmental activism) and 1,767 for supply.
##Covariates (Datamap labels): cov_age (A1), cov_gender (A2; 99 prefer not to say -> NA),
##cov_education (DEducation, the program's grouped levels, e.g. "Level 4 and above";
##prefer not to answer -> NA), cov_settlement (A3), cov_party_id (E9; "Don't know" kept).
##Dropped: uuid (panel respondent identifier; ids re-keyed from `record`), the warm-up
##vignette B2_* (fixed "Mr. P"), program helpers (pipe_*, FinalConcept, B3_Version,
##dChoice_situation), all other survey items. No weights in the deposit.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(suppressMessages(read_excel(file.path(raw, "Glenk_vignette_agric_acceptance_data.xlsx"), "A1", na = c("", "NA"))))
stopifnot(nrow(s) == 2011, uniqueN(s$record) == 2011)
L <- rbindlist(lapply(1:72, function(k) {
  x <- s[, c("record", "dConjoint", paste0("dAttribute", 1:13, "_", k), paste0("B3", LETTERS[1:4], "_", k), paste0("noanswerB3C_", k, "_r99")), with = FALSE]
  setnames(x, c("record", "farm", paste0("a", 1:13), "acc", "fair", "sup", "pet", "na_sup"))
  x[, (names(x)) := lapply(.SD, as.numeric)][, k := k][!is.na(a1)]
}))
stopifnot(L[, .N, record][, all(N == 6)], L[, all(a13 == (a4 - 1) * 6 + a12)], L[na_sup == 1, all(is.na(sup))])
# payment amount sentences: Datamap labels of pipe_A13row1-18, codes 1-4 = farm type (beef, dairy, sheep, cropping)
dm <- as.data.table(suppressMessages(read_excel(file.path(raw, "Glenk_vignette_agric_acceptance_data.xlsx"), "Datamap", col_names = FALSE)))
setnames(dm, c("v1", "v2", "v3"))
A13 <- t(sapply(1:18, function(r) {
  i <- which(dm$v1 == sprintf("[pipe_A13row%d]: Pipe A13row%d", r, r)); stopifnot(length(i) == 1)
  blk <- dm[(i + 2):(i + 5)]; stopifnot(all(blk$v2 == as.character(1:4))); blk$v3 }))
stopifnot(A13[1, 1] == "decrease from currently £10k to £5k per year", A13[3, 2] == "stay unchanged at £20k",
          A13[7, 4] == "decrease from currently £30k to £15k per year")
lab <- list(
  a1 = c("Mr.", "Ms."), a2 = c("5 years ago", "10 years ago", "20 years ago"),
  a3 = c("an agricultural qualification", "a business degree", "no relevant qualification"),
  a4 = c("small", "moderately sized", "large"),
  a5 = c("conventional (rather than organic)", "organic (rather than conventional)"),
  a6 = c("lower than average", "average", "above average"),
  aw = c("standard", "good", "exceptional"),
  pq = c("poor and is mainly used for livestock feed", "decent with some used for livestock feed and some for human consumption",
         "exceptional and is mainly used for human consumption"),
  a8 = c("poor", "average", "good"), a9 = c("amongst the lowest", "average", "amongst the highest"),
  a10 = c("low", "average", "high"), a11 = c("not profitable (makes a loss)", "coping (making neither profit nor loss)", "making a profit"),
  a12 = c("decrease of 50%", "decrease of 25%", "no change", "increase of 10%", "increase of 25%", "increase of 50%"))
farmlab <- c("beef", "dairy", "sheep", "cropping")
setorder(L, record, k)
d <- L[, .(id = as.integer(frank(record, ties.method = "dense")), task = as.integer(rowid(record)), profile = 1L,
           rating_accept = as.integer(acc), rating_fair = as.integer(fair), rating_supply = as.integer(sup), rating_petition = as.integer(pet),
           attr_gender = lab$a1[a1], attr_started_farming = lab$a2[a2], attr_qualification = lab$a3[a3], attr_size = lab$a4[a4],
           attr_production_type = lab$a5[a5], attr_production_level = lab$a6[a6],
           attr_animal_welfare = fifelse(farm == 4, "(not shown)", lab$aw[a7]),
           attr_product_quality = fifelse(farm == 4, lab$pq[a7], "(not shown)"),
           attr_biodiversity = lab$a8[a8], attr_carbon_farm = lab$a9[a9], attr_carbon_output = lab$a10[a10],
           attr_financial_situation = lab$a11[a11], attr_payment_change = lab$a12[a12],
           attr_payment_amount = A13[cbind(a13, farm)],
           trial_farm_type = farmlab[farm], trial_design_row = as.integer(k), record)]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, all(task %in% 1:6)])
cv <- s[, .(record, cov_age = as.integer(A1),
            cov_gender = c("female", "male", "other")[match(as.integer(A2), 1:3)],
            cov_education = c("No qualification", "Level 1", "Level 2", "Level 3", "Level 4 and above")[match(as.integer(DEducation), 1:5)],
            cov_settlement = c("Settlement of 125,000 people and over.", "Settlement of 10,000 to 124,999 people.",
              "Settlement of 3,000 to 9,999 people, and within a 30 minute drive time of a Settlement of 10,000 or more.",
              "Settlement of 3,000 to 9,999 people, and with a drive time of over 30 minutes to a Settlement of 10,000 or more.",
              "Area with a population of less than 3,000 people, and within a 30 minute drive time of a Settlement of 10,000 or more.",
              "Area with a population of less than 3,000 people, and with a drive time of over 30 minutes to a Settlement of 10,000 or more.")[match(as.integer(A3), 1:6)],
            cov_party_id = c("Scottish National Party (SNP)", "Conservative", "Liberal Democrat", "Labour", "Green Party", "Other",
              "No - I do not think of myself as a little closer to one party", "Don't know")[match(as.integer(E9), c(1:7, 99))])]
d <- merge(d, cv, by = "record")[, record := NULL]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "glenk_2024_farm_support.csv"))
