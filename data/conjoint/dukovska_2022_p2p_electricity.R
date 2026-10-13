##Peer-to-peer (P2P) electricity bundle choice-based conjoint (Netherlands) from
##Dukovska, I. (2022). User preferences for local P2P electricity markets - Dataset. 4TU.ResearchData,
##doi:10.4121/20324832, CC BY 4.0 (record licence). No article is linked from the deposit.
##Files read (inside UserPreferencesForP2PElectricityTrading.zip, folder "4TU Survey data"):
##Survey_reports/Survey Responses_329_survey_results.csv (raw Qualtrics export; the two header rows below the names are dropped),
##Survey_design/Conjoint Design.csv, Survey_design/User Preferences Survey Translation NL-EN.csv
##(level text, English translation by the authors), ReadMe.txt. Usage:
##  Rscript dukovska_2022_p2p_electricity.R <dir holding "4TU Survey data"> <output dir>
##
##329 Dutch residential (12 did not finish the later background questions but all answered all 10 tasks and are kept) electricity users (online, May-June 2021; most in Zuid-Holland, one
##living abroad), 10 tasks, 3 electricity bundles per task, 4 attributes. Qualtrics CBC with
##180 versions (vers_CBCONJOINT = question_set of the design file, 57 versions occur): the design
##file lists, per version x question (1-10) x alternative (1-3), the level codes of the four
##attributes; respondent answers C1-C10 are the chosen alternative (1-3) of question 1-10. The
##README states the design file "can be used in combination with" the response file to find
##which respondent got which choice set; C1 = question 1 follows the survey order ("(1/10)").
##Task = question, profile = alternative position (both recorded). Forced choice among the
##three bundles, no none option (C values are only 1-3; the translation file lists no none text).
##Level text = the authors' English translation (Feature/Level entries of the translation csv;
##Dutch original in the survey): supplier 1 Conventional supplier / 2 Local (P2P) market;
##energy type 1 Green / 2 Mixed / 3 Gray energy; selling price 1 "10 cent/kWh" / 2 "6 cent/kWh"
##/ 3 "3 cent/kWh" / 4 Donate; monthly costs EUR 30, 40, 50, 60, 70. The code-to-level order is
##that of the Qualtrics level list; it is not stated that design-file codes follow the same order.
##(The English introduction instead describes selling at regular price / 33% / 66% discount /
##donate; the stored level labels, in cents/kWh, are used.)
##Question (English translation): "If you had to choose between the following electricity
##bundles, which on would you choose?"
##Randomization: individually generated Qualtrics CBC design (180 fixed versions); restrictions
##and level probabilities are not documented.
##Covariates: cov_gender (Man -> male, Vrouw -> female, blank NA), cov_birth_year, cov_education
##(Dutch answer text, as stored), cov_province. Dropped: ResponseId and timestamps (Qualtrics),
##UserLanguage, free text, attribute ranking, willingness and usage items, utilities files.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
p <- file.path(raw, "4TU Survey data")
f <- file.path(p, "Survey_reports", "Survey Responses_329_survey_results.csv")
r <- fread(f, encoding = "UTF-8")[grepl("^R_", ResponseId)]
stopifnot(nrow(r) == 329, all(grepl("^R_", r$ResponseId)))
dz <- fread(file.path(p, "Survey_design", "Conjoint Design.csv"), encoding = "UTF-8")
setnames(dz, c("question_set", "question", "choice", "supplier", "energy", "price", "cost"))
lv <- list(supplier = c("Conventional supplier", "Local (P2P) market"), energy = c("Green energy", "Mixed energy", "Gray energy"),
  price = c("10 cent/kWh", "6 cent/kWh", "3 cent/kWh", "Donate"), cost = c("EUR 30.00", "EUR 40.00", "EUR 50.00", "EUR 60.00", "EUR 70.00"))
for (n in names(lv)) dz[[n]] <- lv[[n]][dz[[n]]]
r[, id := .I][, vers := as.integer(vers_CBCONJOINT)]
stopifnot(all(r$vers %in% dz$question_set))
ch <- melt(r[, c("id", "vers", paste0("C", 1:10)), with = FALSE], id.vars = c("id", "vers"), variable.name = "q", value.name = "pick")
ch[, task := as.integer(sub("C", "", q))][, pick := as.integer(pick)]
stopifnot(ch[, all(pick %in% 1:3)])
d <- merge(ch[, .(id, vers, task, pick)], dz, by.x = c("vers", "task"), by.y = c("question_set", "question"), allow.cartesian = TRUE)
d[, `:=`(profile = as.integer(choice), choice = as.integer(pick == choice))]
d <- merge(d, r[, .(id, cov_gender = c(Man = "male", Vrouw = "female")[Gender], cov_birth_year = as.integer(Birth_year),
  cov_education = Education, cov_province = Province)], by = "id")
setnames(d, c("supplier", "energy", "price", "cost"), c("attr_supplier", "attr_energy_type", "attr_selling_price", "attr_monthly_cost"))
d <- d[, .(id, task, profile, choice, attr_supplier, attr_energy_type, attr_selling_price, attr_monthly_cost, cov_gender, cov_birth_year, cov_education, cov_province)]
stopifnot(nrow(d) == 9870, d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, 1:8]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dukovska_2022_p2p_electricity.csv"))
