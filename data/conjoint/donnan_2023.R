##Four cannabis discrete choice experiments (Canada, October 2021) from one survey, deposited as
##Donnan, J. (2024). Consumer preferences for attributes of cannabis products and retailers: A series
##of Discrete Choice Experiments [Data set]. Borealis. https://doi.org/10.5683/SP3/A55JZ8
##and reported in four articles, one per DCE:
##  dried flower: Donnan, J., Johnston, K., Najafizada, M., & Bishop, L. (2023). Drivers of purchase
##    decisions among consumers of dried flower cannabis products: A discrete choice experiment.
##    Journal of Studies on Alcohol and Drugs, 84(5). https://doi.org/10.15288/jsad.22-00269 (not read)
##  vape: Donnan, J., Johnston, K., Coombs, M., Najafizada, M., & Bishop, L. (2023). Exploring consumer
##    preferences for cannabis vaping products to support public health policy: A discrete choice
##    experiment. Applied Health Economics and Health Policy, 21(4), 651-659.
##    https://doi.org/10.1007/s40258-023-00804-w (PMC10232575)
##  edible: Donnan, J., Johnston, K., Coombs, M., Najafizada, M., & Bishop, L. (2024). Exploring
##    consumer preferences for cannabis edible products to support public health policy: A discrete
##    choice experiment. PLoS ONE. https://doi.org/10.1371/journal.pone.0292336 (PMC11098505)
##  retailer: Donnan, J., Downey, M., Johnston, K., Najafizada, M., & Bishop, L. (2024). Examining
##    attributes of retailers that influence where cannabis is purchased: A discrete choice
##    experiment. Journal of Cannabis Research. https://doi.org/10.1186/s42238-023-00204-w (PMC10851494)
##LICENCE: the Borealis record says CC0 1.0, but the deposit's Read Me states "Data cannot be used
##for commercial gain"; carried as CC BY-NC 4.0 (Ben's ruling 2026-10-09: the stricter README term
##governs).
##Files read: MergedData_analysis Dataverse.tab (datafile 711711, ?format=original = SPSS .sav with
##value labels), the four "CannabisChoice_<DCE>_DCE Design.tab" files (?format=original .csv:
##Version, Task, Concept, Att 1..k as level codes; attribute headers in French), and "Cannabis
##Choice Data Read Me File.docx" (level code -> English level text; covariate code lists).
##Usage: Rscript donnan_2023.R <raw dir> <output dir>; raw dir holds merged.sav, design_flower.csv,
##design_edible.csv, design_vape.csv, design_retailer.csv (the downloads renamed).
##
##Online Canadian panel sample (Angus Reid, email invitation; edible paper), 8-25 October 2021, adults 19+ who had bought cannabis in the
##last 12 months; respondents were routed by quotas (QuotaProductType) to the product DCEs they were
##eligible for, so each DCE has its own respondents. FOUR TABLES (different attribute sets, separate
##analyses and papers): donnan_2023_cannabis_flower, donnan_2024_cannabis_edible,
##donnan_2023_cannabis_vape, donnan_2024_cannabis_retailer.
##Design: Sawtooth Lighthouse CBC, D-efficient fractional factorial, 300 versions (blocks) of 8 tasks
##(retailer 6) of two unlabelled alternatives "Option A"/"Option B" (papers): a FIXED BLOCKED
##DESIGN. The respondent's version is sys_CBCVersion_<DCE>; task k = <DCE>_Random<k> = design Task k
##(Sawtooth's random-task order); profile = design Concept (1 = Option A). Forced choice, NO opt-out
##(papers: "No opt-out option was provided"). Attribute order fixed (design column order).
##Choice wording (papers): vape "You are purchasing a 0.5 g cannabis vape product with THC of your
##preferred variety (sativa, indica, hybrid). Which of the following products would you choose?
##While some options may not seem possible, assume both options are available as presented";
##retailer "You are going to make a cannabis purchase from a store either in person or online, which
##of the following locations would you choose? While some options may not seem possible, assume both
##options are available as presented."; flower and edible: a similar scenario, wording not available.
##Level text: the Read Me's English level labels (identical to the papers' Table 1 for vape, edible,
##retailer), with the Read Me's typo "Unknow" written "Unknown" as in the papers. The survey was
##bilingual (the design files carry the French attribute names); which respondents saw French is
##not recorded.
##Respondents: like the papers, only respondents with sys_RespStatus = 5 (qualified/complete) are
##kept; incomplete respondents' partial tasks are dropped (flower 79, edible 53, vape 25, retailer 35
##respondents). Papers: vape 384/385, edible 684, retailer 1,626 (flower paper not read).
##Covariates (Read Me code lists -> text; "Prefer not to say" -> NA): cov_age_group (Age),
##cov_province, cov_sex_at_birth (Sex, "What sex were you assigned at birth?"), cov_gender (Pronouns "What is your gender
##identity?": Man -> male, Woman -> female, Gender diverse / Other -> other, 5 Prefer not to say (.sav
##label) -> NA), cov_education, cov_income, cov_urban_rural, cov_cannabis_freq (CannabisFreq).
##cov_duration_sec = sys_ElapsedTime (whole survey, seconds). Dropped: system fields (times, browser,
##user agent, screen width), free-text "_other" fields, multi-select use/type/store/employment
##batteries, quota flags. No survey weight.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_sav(file.path(raw, "merged.sav")))
s <- s[sys_RespStatus == 5]
lv <- list(
  flower = list(price = c("$20", "$30", "$40", "$50"), packaging = c("Plastic", "Bag", "Can", "Pre-Roll", "Glass"),
                moisture = c("Low", "Medium"), potency = c("10 – 14.9% THC", "15 – 19.9% THC", "20 – 24.9% THC", "25%+ THC"),
                recommendation = c("Recommended by person selling", "Recommended by Family or Friend", "Recommended in online reviews", "Self-selected without input from others"),
                package_info = c("No info on the package", "Producer, Amount of THC/CBD, not strain specific",
                                 "Producer, Amount of THC/CBD, Strain, harvest/package dates, Growth and Supply Chain Info"),
                regulated_health_canada = c("Yes", "No", "Unknown")),
  edible = list(edible_type = c("A Candy (e.g. chocolate bar, gummy, mint)", "A Baked Product (e.g. brownie, cookie, granola bar)", "A Savory Product (e.g. pretzels, trail mix)"),
                price = c("$5", "$10", "$15"), thc_per_package = c("5 mg", "10 mg", "50 mg", "100 mg"),
                cannabis_taste = c("Strong cannabis taste", "Mild cannabis taste", "No cannabis taste"),
                package_info = c("No info on the package", "Producer, Amount of THC and/or CBD in milligrams, nutritional information",
                                 "Producer, Amount of THC and/or CBD in milligrams, nutritional information, strain, terpenes, growth and supply Chain Info"),
                thc_consistency = c("Unknown", "Exactly the same"),
                recommendation = c("Recommended by person selling", "Recommended by Family or Friend", "Recommended in online reviews", "Self-selected without input from others"),
                regulated_health_canada = c("Yes", "No", "Unknown")),
  vape = list(device_type = c("Pre-filled Cartridge", "Disposable pen"), price = c("$30", "$40", "$50", "$60"),
              thc_amount = c("70%", "80%", "90%"),
              contents = c("Full spectrum with cannabis taste and terpenes", "Distillate with no cannabis taste or terpenes", "Distillate with non-cannabis flavors (e.g. fruit)"),
              recommendation = c("Recommended by person selling", "Recommended by Family or Friend", "Recommended in online reviews", "Self-selected without input from others"),
              regulated_health_canada = c("Yes", "No", "Unknown")),
  retailer = list(prices = c("Product discounts available", "Products offered at regular prices"),
                  product_info = c("Only what is on the package", "Some additional information about the product",
                                   "Extensive information in each product such as terpene levels, grower and supply chain information"),
                  customer_service = c("I can get all of my questions answered and can receive help selecting my products",
                                       "No one is available to answer questions of help select a product"),
                  proximity = c("Within walking distance", "Store within a 15 minute drive", "Store within a 30 minute drive", "Online purchase with home delivery"),
                  product_variety = c("Limited product selection", "Wide product selection"),
                  provincially_regulated = c("Yes", "No", "Unknown")))
spec <- list(flower = c("DriedFlower", "donnan_2023_cannabis_flower", 8), edible = c("Edible", "donnan_2024_cannabis_edible", 8),
             vape = c("VapePen", "donnan_2023_cannabis_vape", 8), retailer = c("Experience", "donnan_2024_cannabis_retailer", 6))
txt <- function(x, labs) { x <- as.integer(x); labs[x] }
age <- c("18 or younger", "19-29", "30-39", "40-49", "50-59", "60 or above")
prov <- c("British Columbia", "Alberta", "Saskatchewan", "Manitoba", "Ontario", "Quebec", "New Brunswick", "Nova Scotia",
          "Prince Edward", "Newfoundland and Labrador Island", "Yukon", "Northwest Territories", "Nunavut", "I do not live in Canada")
edu <- c("Did not complete high school", "High school diploma", "Some post-secondary", "College/trade/technical/vocational training completed",
         "Undergraduate degree", "Graduate degree")
inc <- c("Less than $25,000", "$25,000 to $49,999", "$50,000 to $74,999", "$75,000 to $99,999", "$100,000 or more", NA)
urb <- c("Rural area (less than 1,000 people)", "Small population centre (between 1,000 and 29,999 people)",
         "Medium population centre (between 30,000 and 99,999 people)", "Large urban population centre (between 100,000 and 999,999 people)",
         "Very large urban centre (1 million or more people)")
frq <- c("Less than once per month", "At least once per month, but less than once per week", "At least once per week",
         "Once per day", "Multiple times per day", NA)
stopifnot(identical(unname(attr(s$Pronouns, "labels")), c(1, 2, 3, 4, 5)), names(attr(s$Pronouns, "labels"))[5] == "Prefer not to say")
cv <- s[, .(rid = as.integer(sys_RespNum), cov_age_group = txt(Age, age), cov_province = txt(Province, prov),
            cov_sex_at_birth = txt(Sex, c("Male", "Female", NA)), cov_gender = txt(Pronouns, c("male", "female", "other", "other", NA)),
            cov_education = txt(Education, edu), cov_income = txt(Income, inc), cov_urban_rural = txt(UrbanRural, urb),
            cov_cannabis_freq = txt(CannabisFreq, frq), cov_duration_sec = as.numeric(sys_ElapsedTime))]
stopifnot(!anyDuplicated(cv$rid))
for (k in names(spec)) {
  p <- spec[[k]][1]; tab <- spec[[k]][2]; nt <- as.integer(spec[[k]][3])
  des <- fread(file.path(raw, paste0("design_", k, ".csv")))
  an <- names(lv[[k]]); stopifnot(ncol(des) == 3 + length(an))
  setnames(des, c("version", "task", "profile", an))
  for (j in an) { stopifnot(all(des[[j]] %in% seq_along(lv[[k]][[j]]))); des[, (j) := lv[[k]][[j]][get(j)]] }
  setnames(des, an, paste0("attr_", an))
  ch <- s[, c("sys_RespNum", paste0("sys_CBCVersion_", p), paste0(p, "_Random", 1:nt)), with = FALSE]
  setnames(ch, c("rid", "version", paste0("t", 1:nt)))
  ch <- melt(ch[!is.na(version)], id.vars = c("rid", "version"), variable.name = "task", value.name = "pick")
  ch <- ch[!is.na(pick)][, task := as.integer(sub("t", "", task))]
  stopifnot(all(ch$pick %in% 1:2), ch[, .N, rid][, all(N == nt)])
  d <- merge(ch, des, by = c("version", "task"), allow.cartesian = TRUE)
  stopifnot(nrow(d) == 2 * nrow(ch))
  d[, choice := as.integer(profile == pick)][, rid := as.integer(rid)]
  d <- merge(d, cv, by = "rid")
  ids <- sort(unique(d$rid)); d[, id := match(rid, ids)]
  d[, c("rid", "pick", "version") := NULL]
  d[, task := as.integer(task)][, profile := as.integer(profile)]
  setcolorder(d, c("id", "task", "profile", "choice", paste0("attr_", an)))
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  cat(tab, uniqueN(d$id), "respondents,", nrow(d), "rows\n")
  fwrite(d, file.path(out, paste0(tab, ".csv")))
}
