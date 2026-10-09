##Alternative-meat burger discrete choice experiment (UK; supermarket vs restaurant) from
##Gan, Y. S. (2026). Who chooses alternative meat and where? Understanding how foodscapes and
##individual variation shape plant-based meat and cell-cultured meat choices using a Discrete
##Choice Experiment [Data set]. OSF. https://doi.org/10.17605/OSF.IO/PNRHT (University of Bath PhD
##project), CC BY 4.0 (node licence). No article found.
##Files read: Data/Data v1.csv (raw wide file, one row per respondent) and Data/idefix output MAIN.csv
##(the idefix design: 20 choice sets x 2 alternatives). Read as text, not run: R codes/0.3 idefix
##generator MAIN.R (level decoding), 1.1 DCE descriptive MAIN.R (codings), 1.2 DCE mixed logit MAIN.R.
##Viewed: Study Material/Main Study - Images S01, S02, S06, R01 (the choice cards).
##Usage: Rscript gan_2026.R <dir holding "Data v1.csv" and "idefix output MAIN.csv"> <output dir>
##
##300 UK adults; each made 20 choices (task = design set 1-20 = ROp/SOp column; whether sets were shown
##in this order is not documented) between
##two burgers, Option A (profile 1, left) and Option B (profile 2), shown as an image card with a
##burger photo and four rows: Type, Price, Healthiness, Customer rating. Fixed Bayesian-efficient
##idefix design (one version, 20 sets; priors from a pilot), constraint: plant-based and
##cell-cultured never together (they are one "Type" attribute). Respondents were randomized to a
##supermarket (Condition 1, SOp1-20, n = 149) or restaurant (Condition 2, ROp1-20, n = 151) frame:
##trial_setting. Restaurant prices are the design price + £10 (the authors' model code; card R01
##shows £12/£20 where S01 shows £2/£10).
##Level text as printed on the cards (checked on S01, S02, S06, R01, which match design sets 1, 2, 6):
##  attr_type: "Plant-based" (plantC = 1), "Cell-cultured" (cellC = 1), "Normal" (neither)
##  attr_price: "£2", "£5", "£7", "£10" (supermarket); "£12", "£15", "£17", "£20" (restaurant)
##  attr_healthiness: "Unhealthy. Low protein. High fat." / "Healthy. High protein. Low fat." (the card
##    prints the second sentence in small type under the word)
##  attr_rating: customer rating "0 star", "1 star", "2 stars", "3 stars" (stars plus this caption)
##Outcome choice: Option A / Option B, forced (no opt-out); the column value 1 = left = Option A,
##2 = Option B (the authors' code: "Left (1) and Right (0)" after recoding 2 to 0). The question
##wording is not in the deposit (unknown). Two respondents answered 18 of 20 sets; their 2 missing
##sets are omitted.
##Covariates: cov_age (years), cov_gender (1 female, 2 male; the authors' descriptive code),
##cov_ethnicity (codes mapped by the authors' comment list: 1 Hispanic, 2 American Indian, 3 Asian,
##4 Black, 5 Native Hawaiian, 6 Caucasian/White, 7 Multiracial, 8 Other, 9 Prefer not to say -> NA),
##cov_diet_code, cov_income_code, cov_education_code, cov_redmeat_code, cov_whitemeat_code,
##cov_seafood_code (no labels in the deposit), cov_duration_min (Time, minutes as stored).
##Spot check: a conditional logit by setting gives the expected signs (supermarket: price -0.145 per
##pound, healthy +0.63, per star +0.06, plant-based -0.95, cell-cultured -1.27 vs Normal), confirming
##the A/B coding. Marginal choice shares by level are misleading here (fixed efficient design: e.g.
##3-star cards are often the £10 cell-cultured option), so use models that condition on all attributes.
##Dropped: consent items, attitude scale items (Attach, Health, Envi, Welfare, Plant, Cell), the
##free-text nationality and "Reason" answers.
##The authors' descriptive script reports n = 285 (it does not say which 15 are excluded; Diet = 2
##for exactly 15 respondents); all 300 are kept.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "Data v1.csv"))
des <- fread(file.path(raw, "idefix output MAIN.csv")); setnames(des, 1, "key")
des[, c("set", "alt") := tstrsplit(sub("^set", "", key), ".alt", fixed = TRUE)][, `:=`(set = as.integer(set), alt = as.integer(alt))]
stopifnot(nrow(des) == 40, all(x$Condition %in% 1:2), uniqueN(x$Count) == 300, !any(des$design.plantC == 1 & des$design.cellC == 1))
L <- melt(x[, c("Count", "Condition", paste0("ROp", 1:20), paste0("SOp", 1:20)), with = FALSE], id.vars = c("Count", "Condition"))
L[, room := substr(variable, 1, 1)][, set := as.integer(sub("^[RS]Op", "", variable))]
L <- L[(room == "S" & Condition == 1) | (room == "R" & Condition == 2)]
stopifnot(all(L$value %in% c(0, 1, 2)))
L <- L[value %in% 1:2]
d <- L[rep(seq_len(.N), each = 2)][, profile := rep(1:2, .N / 2)]
d <- merge(d, des, by.x = c("set", "profile"), by.y = c("set", "alt"))
d[, `:=`(id = as.integer(Count), task = set, choice = as.integer(value == profile),
         attr_type = fifelse(design.plantC == 1, "Plant-based", fifelse(design.cellC == 1, "Cell-cultured", "Normal")),
         attr_price = paste0("£", design.price + fifelse(Condition == 2, 10L, 0L)),
         attr_healthiness = fifelse(design.healthy == 1, "Healthy. High protein. Low fat.", "Unhealthy. Low protein. High fat."),
         attr_rating = c("0 star", "1 star", "2 stars", "3 stars")[design.social + 1],
         trial_setting = fifelse(Condition == 1, "supermarket", "restaurant"))]
cv <- x[, .(id = as.integer(Count), cov_age = as.integer(Age), cov_gender = c("female", "male")[Gender],
            cov_ethnicity = c("Hispanic", "American Indian", "Asian", "Black", "Native Hawaiian", "Caucasian/White", "Multiracial", "Other", NA)[Ethnicity],
            cov_diet_code = Diet, cov_income_code = Income, cov_education_code = Education, cov_redmeat_code = Redmeat,
            cov_whitemeat_code = Whitemeat, cov_seafood_code = Seafood, cov_duration_min = Time)]
stopifnot(all(x$Gender %in% 1:2), all(x$Ethnicity %in% 1:9), all(cv$cov_age %in% 18:99))
d <- merge(d[, .(id, task, profile, choice, attr_type, attr_price, attr_healthiness, attr_rating, trial_setting)], cv, by = "id")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, id][, all(N %in% c(36, 40))])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gan_2026_alternative_meat.csv"))
