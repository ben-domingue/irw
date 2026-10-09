##Local-versus-imported staple food discrete choice experiments (Kinshasa, DR Congo, 2019) from
##Thontwa, S. K., De Weerdt, J., & Van Passel, S. (2024). What do urban consumers want? Findings from a
##discrete choice experiment on the preference for locally produced food in the Democratic Republic of
##Congo. Agrekon, 63(4), 223-239. https://doi.org/10.1080/03031853.2024.2392582
##Replication data: Harvard Dataverse doi:10.7910/DVN/KPPMFF, CC0 1.0. Files read: Final.dta (the authors'
##analysis file built by Clean.do; Dataverse "original format") and, for the level text, the
##"Coding_<product> Choice_Cards" sheets of Survey1.xlsx (identical in Survey2/3.xlsx). Clean.do read as text,
##not run. The article is paywalled and was not seen.
##Usage: Rscript thontwa_2024.R <dir holding Final.dta and Survey1.xlsx> <output dir>
##
##Five tables, one per product, as the authors estimate one model per product (Clean.do Tables 3-5):
##  thontwa_2024_food_rice (RIZ), _maize (MAIS), _cassava (MANIOC), _sugar (SUCRE), _oil (HUILE).
##The same respondents answered all five. Each product is its own fixed blocked design: 8 versions
##(trial_version = Survey) x 8 cards (task = cno, the card number within the version), 2 options per card
##(profile = Option), no opt-out (Option_chosen is 1 or 2 on every answered card). Versions vary across
##products for the same respondent.
##Respondents: three survey groups, Survey1/2/3.xlsx, which Clean.do names CG, IT and LT (trial_arm). Their
##meaning is not documented in the deposit (the authors' Table 4/5 models interact Local origin with IT and
##LT, so they are probably treatment arms against a control group; not stated). Person_ID restarts within
##each group and matches different people, so id is re-keyed over (group, Person_ID): 601 respondents
##(CG 230, IT 186, LT 185; a few skipped a product). The Dataverse triage noted "236"; that is the largest
##Person_ID. Paper N not checked.
##Outcome:
##  choice = Choice (Option_chosen): which of the two options the respondent would buy. Wording not seen:
##           paraphrase. Exactly one per card (checked).
##Attributes (French text of the choice-card coding sheets; cards may also have had pictures):
##  attr_price (Cout, "Prix A/B/C: <n> FC", Congolese francs; levels differ by product),
##  attr_packaging (Emballage: Aucun / Minimum / Moyen / Standard Industriel; rice never shows Minimum and oil
##  never shows Moyen), attr_distance (Distance; text as in that product's sheet, which differs slightly between
##  products), attr_origin (Origine: Locale / Import Regionale / Import Est / Import Occident / Import ALatine).
##  Final.dta stores codes; the code order is Clean.do's egen group() order (alphabetical) and its labels
##  (Origin 1 Latin America, 2 Eastern, 3 Western, 4 Regional, 5 Local; Distance 1 walking, 2 nearby, 3 far),
##  matched to the sheet text; price is the numeric FC amount, matched to the sheet's "Prix" text.
##Covariates (Final.dta value labels, the authors' recodes in Clean.do): cov_age_group (French bands),
##cov_gender (Female/Male), cov_marital, cov_education_group (the authors' 4 groups from IDENT_05; not the
##original categories), cov_study_area, cov_has_children, cov_children (ChildNum), cov_children_under6,
##cov_income_group (Salary, the authors' 3 USD bands), cov_employed, cov_district (Kinshasa commune),
##cov_shopping_place, cov_meals_per_day ("No answer" = NA).
##PII: LocationLatitude/LocationLongitude are in Final.dta (dropped); the Survey*.xlsx sheets also hold
##IP addresses, GPS and Qualtrics ResponseIds (not read beyond the coding sheets). Derived dummies and
##interaction groupings (Aucun..Local, CG/IT/LT, *_Gender, SL_*, SalaryC) are dropped. No survey weight.
library(haven); library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x0 <- read_dta(file.path(raw, "Final.dta"))
lab <- function(v) as.character(as_factor(v, levels = "labels"))
x <- as.data.table(zap_labels(x0))
for (v in c("Age", "Gender", "Marital", "Education", "StudyArea", "Child", "Salary", "Employment", "District", "ShopingLocation", "Meals"))
  x[, paste0(v, "_t") := lab(x0[[v]])]
x[Meals_t == "No answer", Meals_t := NA]
x[, uid := .GRP, .(SurveyID, Person_ID)]
setorder(x, uid)
x[, id := match(uid, unique(uid))]
prods <- c(RIZ = "rice", MAIS = "maize", MANIOC = "cassava", SUCRE = "sugar", HUILE = "oil")
for (p in names(prods)) {
  sh <- as.data.frame(suppressMessages(read_excel(file.path(raw, "Survey1.xlsx"), sheet = paste0("Coding_", p, " Choice_Cards"), col_names = FALSE)))
  hdr <- unlist(sh[2, ]); sh <- sh[-(1:2), ]
  col <- function(n) trimws(sh[[which(hdr == n)[1]]])
  dist <- unique(col("Distance")); dist <- dist[!is.na(dist)]
  dmap <- c(dist[grepl("^Pres", dist)][1], dist[grepl("^Commune", dist)][1], dist[grepl("^Au dela", dist)][1])
  cout <- unique(col("Cout")); cout <- cout[!is.na(cout)]
  cnum <- as.numeric(sub(".*: *([0-9]+) *FC.*", "\\1", cout))
  pmap <- setNames(sub(": *", ": ", sub("^Prix ([abc])", "Prix \\U\\1", cout, perl = TRUE)), cnum); pmap <- pmap[!duplicated(names(pmap))]
  stopifnot(length(dmap) == 3, !anyNA(dmap), length(pmap) == 3)
  d <- x[Product == p]
  stopifnot(d[, .N, .(id, cno)][, all(N == 2)], d[, sum(Choice), .(id, cno)][, all(V1 == 1)],
            d[, all(Choice == (Option == Option_chosen))], d[, uniqueN(Survey), id][, all(V1 == 1)],
            all(as.character(d$Price) %in% names(pmap)))
  o <- d[, .(id, task = as.integer(cno), profile = as.integer(Option), choice = as.integer(Choice),
    attr_price = unname(pmap[as.character(Price)]),
    attr_packaging = c("Aucun", "Minimum", "Moyen", "Standard Industriel")[Packaging],
    attr_distance = dmap[Distance],
    attr_origin = c("Import ALatine", "Import Est", "Import Occident", "Import Regionale", "Locale")[Origin],
    trial_arm = SurveyID, trial_version = as.integer(Survey),
    cov_age_group = Age_t, cov_gender = c(Female = "female", Male = "male")[Gender_t], cov_marital = trimws(Marital_t),
    cov_education_group = Education_t, cov_study_area = StudyArea_t, cov_has_children = Child_t,
    cov_children = ChildNum, cov_children_under6 = Child6, cov_income_group = Salary_t, cov_employed = Employment_t,
    cov_district = District_t, cov_shopping_place = ShopingLocation_t, cov_meals_per_day = Meals_t)]
  stopifnot(!anyNA(o[, .(attr_price, attr_packaging, attr_distance, attr_origin)]))
  setorder(o, id, task, profile)
  fwrite(o, file.path(out, paste0("thontwa_2024_food_", prods[[p]], ".csv")))
  cat(prods[[p]], nrow(o), "rows,", uniqueN(o$id), "respondents\n")
}
