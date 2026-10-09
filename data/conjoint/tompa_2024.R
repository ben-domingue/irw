##Protein-source sustainability choice-based conjoint (Hungary) from
##Tompa, O., Kiss, A., Lakner, Z., Unger-Plasek, B., & Temesi, Á. (2024). Differences in
##perspectives on sustainability attributes of dietary protein sources between reduced
##animal-based dieters and nondieters.
##Humanities and Social Sciences Communications, 11, 1401.
##https://doi.org/10.1057/s41599-024-03932-3
##Replication data: Harvard Dataverse doi:10.7910/DVN/R2WHHT, CC0 1.0, no restricted files.
##File read: questionnaire_translated_processed_tompa_et_al_2024_HSSC-1.xlsx, sheets
##"Questionnaire_translated" (one row per respondent; CBC_1..CBC_16 = chosen card code, 0 = no
##choice) and "conjoint_cards_data" (the 16 fixed card pairs: card code, nutriscore, ecoscore,
##price, product category for card 1 and card 2). Design and wording from the article (open
##access, CC BY), "Design of the choice-based conjoint analysis" and Fig. 2.
##Usage: Rscript tompa_2024.R <raw dir> <output dir>
##
##639 adults (online Jotform survey in Hungary, 7 April - 9 May 2022, recruited via Facebook),
##16 choice tasks of 2 protein-product cards plus a "no choice" option. FIXED design: an
##orthogonal fraction of the 8 x 2 x 2 x 2 factorial (Doe.base / AlgDesign), the same 16 pairs
##for every respondent. task = choice-set number k of CBC_k / card row k; the display order of
##the 16 questions is not documented (the spreadsheet's CBC columns run 13, 4, 14, 3, ...).
##profile 1 = "conjoint card 1", 2 = "conjoint card 2". Every CBC value is 0 or one of that
##set's two card codes (checked).
##Question: "Please choose the protein source that you think is more sustainable on the basis
##of the information at your disposal" (article; English translation of the Hungarian survey).
##choice = 1 for the chosen card; "no choice" = 0 on both cards (opt-out).
##Attributes: attr_product (tofu, cheese, eggs, milk, pork, poultry, fish, almond; the
##spreadsheet's English names), attr_nutriscore (nutritional score class A-E shown on the card),
##attr_ecoscore (ecological score class A-E), attr_price (price in HUF for the portion, as a
##number). The article: nutritional score, ecological score and price each had 2 levels, shown
##on the card or not; the spreadsheet codes "not on the card" as "no label", stored here as
##"(not shown)". When shown, the letter or price is the product's own value (article Table 1),
##so these attributes are not independent of attr_product.
##Covariates (English answer text from the translated sheet): cov_age_group ("age (y)"; "60"
##as in source), cov_education (education_level), cov_income (income_cat), cov_family_status,
##cov_residence (type_residence), cov_food_responsibility (food_resposibility: yes /
##occasionally / no), cov_diet, cov_diet_type (diet_type_closed: no / special diet due to other
##reasons / dietotherapy due to disease), cov_occupation_type; cov_<food>_health (1-5,
##1 = unhealthy, 5 = very healthy), cov_<food>_ffq (food frequency, text categories, e.g.
##"5- 1-2 o/w" = 1-2 occasions/week per the abbrev. sheet), cov_<food>_sustainability (1-5,
##1 = not environmentally friendly at all .. 5 = very), kept as source text. No respondent
##gender in the deposit. Dropped: number (row id, re-keyed), date_code (submission time).
##N: 639 = all respondents; the article analyses 541 after excluding under-18s and diets due to
##disease (cov_diet_type "dietotherapy due to disease" = 118 rows; the under-18 rule cannot be
##checked, age bands start at 18-29). The table keeps all 639. No survey weight.
##Spot check: a conditional logit with the no-choice option as baseline, on cov_diet =
##"no_special" (247 nondieters), reproduces article Table 3 (almond 1.60, cheese -1.07, tofu
##1.36, nutritional score 0.32, ecological score -0.41).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "questionnaire_translated_processed_tompa_et_al_2024_HSSC-1.xlsx")
q <- as.data.table(read_excel(f, "Questionnaire_translated"))
cd <- as.data.table(read_excel(f, "conjoint_cards_data", skip = 2, col_names = FALSE))
setnames(cd, c("set", paste0(rep(c("code", "nutri", "eco", "price", "product"), 2), rep(1:2, each = 5))))
stopifnot(nrow(cd) == 16L, all(cd$set == 1:16))
ns <- function(x) fifelse(x == "no label", "(not shown)", as.character(x))
cards <- rbindlist(lapply(1:2, function(p) cd[, .(task = as.integer(set), profile = p, code = as.integer(get(paste0("code", p))),
  attr_product = get(paste0("product", p)), attr_nutriscore = ns(get(paste0("nutri", p))),
  attr_ecoscore = ns(get(paste0("eco", p))), attr_price = ns(get(paste0("price", p))))]))
stopifnot(!anyNA(cards))
q[, id := as.integer(number)]
stopifnot(!anyDuplicated(q$id))
ch <- melt(q[, c("id", paste0("CBC_", 1:16)), with = FALSE], id.vars = "id", variable.name = "task", value.name = "pick")
ch[, task := as.integer(sub("CBC_", "", task))][, pick := as.integer(pick)]
d <- merge(ch, cards, by = "task", allow.cartesian = TRUE)
stopifnot(d[, all(pick == 0L | pick %in% code), .(id, task)]$V1)
d[, choice := as.integer(pick == code)][, c("pick", "code") := NULL]
cv <- q[, .(id, cov_age_group = `age (y)`, cov_education = education_level, cov_income = income_cat, cov_family_status = family_status,
            cov_residence = type_residence, cov_food_responsibility = food_resposibility, cov_diet = diet,
            cov_diet_type = diet_type_closed, cov_occupation_type = `occupation type`)]
for (v in grep("_(health|ffq|sustainability)$", names(q), value = TRUE)) cv[, paste0("cov_", v) := q[[v]]]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice"))
stopifnot(nrow(d) == 639L * 32L, d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "tompa_2024_protein_sustainability.csv"))
