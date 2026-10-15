##Result-based carbon-compensation contracts, Finland, choice experiments (CONSOLE project) from
##Haltia, E. (2022). CONSOLE_WP3_Task3.2_ Pan-EU survey of farmers and other rural landowners_FI_2022.11.03_v01 [Data set]. Zenodo.
##Natural Resources Institute Finland (contributors Tarvainen, Leppanen). No article DOI in the record.
##Deposit: Zenodo doi:10.5281/zenodo.7276709 (version record; concept DOI 10.5281/zenodo.7276708), CC BY 4.0 (record licence cc-by-4.0).
##Files read: the .xlsx (sheets "CE data farmers", "CE data forest owners", "Data farmers", "Data forest owners"). Level text and attribute units come
##from the twin README record doi:10.5281/zenodo.7505626 (CC BY 4.0), file CodesQuestionsAndVariableCoding_2022.11.03.xlsx (English sheets "CE data ...",
##Finnish question text and codes in the "Data ..." sheets).
##Usage: Rscript haltia_2022.R <dir holding the .xlsx, named fi.xlsx> <output dir>
##
##Two surveys, two tables (different level sets: contract length, carbon payment unit): 409 Finnish farmers (haltia_2022_carbon_farm_contracts,
##carbon farming) and 386 forest owners (haltia_2022_carbon_forest_contracts, forest carbon). Each respondent made 6 choices (tasks) among two contract
##alternatives and a third alternative stored with Duration 0, Additional 0, Payment 0 and no service level: that is "no contract" and is treated as the
##opt-out (no profile row, choice = 0 on both profiles); no questionnaire is deposited, so that reading is inferred from the zeros (exactly one of
##3 chosen in every task). Fixed or randomised design not stated; level weights: the data show unequal shares
##(additional payment EUR 50 appears less often than EUR 10 or 100); no restrictions documented.
##Attributes (codebook, translated English): attr_plan = "Plan for carbon farming by an expert" (farmers) / "Carbon forest plan by an expert" (forest owners) with
##levels No plan; Free plan at the beginning of the contract period; Free plan that is updated in every five years (farmers: "Free carbon farming plan ...").
##attr_contract_length = 5/10/15 years (farmers), 20/30/40 years (forest owners). attr_payment_start = "Payment at the begin of the contract period",
##EUR 10/50/100 per ha. attr_carbon_payment = "Carbon payment", EUR 5/12/25/37/50 per t (farmers), EUR 2/5/10/15/20 per m3 (forest owners). The unit of the
##tonne (of CO2?) is not stated.
##Outcome: choice = choice among the contract alternatives (question wording not deposited; paraphrase).
##Covariates from the "Data" sheets: cov_gender (1 Mies = male, 2 Nainen = female, 3 Muu = other), cov_education (Finnish answer text from the codebook: 1 Peruskoulu tai kansakoulu,
##2 Toinen aste (ammattikoulu, lukio), 3 Alempi korkeakouluaste (kandidaatti, AMK), 4 Ylempi korkeakouluaste (maisteri, YAMK), 5 Tutkijakoulutus, 6 Muu).
##Birth year is empty in the deposit. ID = the deposit's respondent number (not a platform id). Dropped: all other survey variables, free text. No weight.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "fi.xlsx")
edu <- c("Peruskoulu tai kansakoulu", "Toinen aste (ammattikoulu, lukio)", "Alempi korkeakouluaste (kandidaatti, AMK)",
         "Ylempi korkeakouluaste (maisteri, YAMK)", "Tutkijakoulutus", "Muu")
build <- function(ce, dat, gcol, ecol, plan, lens, paytxt, name, n_exp) {
  d <- as.data.table(read_excel(f, sheet = ce)); setnames(d, sub("Servive", "Service", names(d)))
  p <- as.data.table(read_excel(f, sheet = dat))
  stopifnot(uniqueN(d$ID) == n_exp, d[, .N, ID][, all(N == 18)], d[, sum(Choice), .(ID, ChoiceTask)][, all(V1 == 1)])
  stopifnot(d[Alternative == 3, all(Duration == 0 & Additional == 0 & Payment == 0)], d[Alternative < 3, all(Service0 + Service1 + Service2 == 1)])
  d[, svc := fifelse(Service0 == 1, "No plan", fifelse(Service1 == 1, paste("Free", plan, "at the beginning of the contract period"),
                      paste("Free", plan, "that is updated in every five years")))]
  r <- d[Alternative < 3, .(id = as.integer(ID), task = as.integer(ChoiceTask), profile = as.integer(Alternative),
         choice = as.integer(Choice), attr_plan = svc, attr_contract_length = paste(Duration, "years"),
         attr_payment_start = sprintf("EUR %d per ha", as.integer(Additional)), attr_carbon_payment = sprintf(paste0("EUR %d per ", paytxt), as.integer(Payment)))]
  cv <- p[, .(id = as.integer(ID), cov_gender = c("male", "female", "other")[get(gcol)], cov_education = edu[get(ecol)])]
  stopifnot(!anyNA(cv$cov_gender), !anyNA(cv$cov_education), cv[, .N, id][, all(N == 1)])
  r <- merge(r, cv, by = "id")
  setorder(r, id, task, profile)
  fwrite(r, file.path(out, paste0(name, ".csv")))
}
build("CE data farmers", "Data farmers", "VI101", "VI103", "carbon farming plan", "", "t", "haltia_2022_carbon_farm_contracts", 409)
build("CE data forest owners", "Data forest owners", "MO101", "MO103", "carbon forest plan", "", "m3", "haltia_2022_carbon_forest_contracts", 386)
