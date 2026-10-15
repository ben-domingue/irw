##Parking choice in 27 Ecuadorian cities, Ecuador: stated-preference experiment, from the Zenodo deposit "Data and R Script for: Parking Choice Behavior in Ecuadorian Cities - A National Stated Preference Analysis ..." (Garcia-Ramirez).
##Deposit: doi:10.5281/zenodo.20272342 (concept doi 10.5281/zenodo.20272341), CC BY 4.0 (record licence cc-by-4.0).
##No article DOI in the deposit (no article DOI; the title is "Parking Choice Behavior in Ecuadorian Cities: A National Stated Preference Analysis with Revealed Preference Validation, Technology Adoption, and Inter-City Heterogeneity"). Files read: Data_parking_survey_EC.xlsx (sheet "Original", one row per respondent) and the R script
##in the docx (Script R_parking_survey_EC.docx; read as text via pandoc, never run) for the design matrix, the eligibility filter and the coding.
##Usage: Rscript garciaramirez_2026_national.R <dir holding the xlsx> <output dir>
##
##Sample: 2150 licensed drivers (online survey across 27 cities); the authors' eligibility filter (drop "No poseo licencia", "Menor de 18")
##keeps all 2150. Respondent id = row number (no id column in the file); six SP scenarios each (columns 12-17 in order
##= scenario 1-6; the script maps choice_sc1..6 to columns 12..17; task_source inferred from column order), no blank
##choice cell. Independent of the Loja deposit (zenodo 18982400): only 3 of its 227 rows also appear here although this file has 398 Loja respondents.
##Design: FIXED design, every respondent saw the same six scenarios ("attribute values per option per scenario, extracted
##from the survey", the script's sp_design matrix, read as text). Task = scenario; the four labelled options are the profiles:
##A regulated on-street parking, B private parking, C irregular parking (unauthorised place), D leave the vehicle at home and use
##another mode (profile 1-4). Choice: "Imagine that you need to park your vehicle for 2 hours in a congested commercial
##area on a Tuesday at 10 AM. Which option would you choose?" ("OPCION A/B/C/D: ..." answers). No opt-out (D, leaving the car
##at home, is a labelled alternative with its own attributes, so it is a profile).
##Attributes (8, from the design matrix; level text is composed from the stored values with units, the Spanish wording shown to
##respondents is not in the deposit): walking distance to destination (m), parking cost for 2 h (USD), probability of finding
##a space (%), search time (minutes), probability of a fine (%), fine amount (USD), security level (Low/Medium/High),
##surveillance (Cameras/Guard/None). For option D the design leaves probability of a space, search time and surveillance NA:
##stored "(not shown)". Options A, B and D have fine probability 0 and amount 0 in the matrix; these are stored as "0%" and
##"USD 0" (whether they were displayed is unknown).
##Dropped: the revealed-preference block (last parking choice, price paid, search time), per-option perception batteries
##(8 items x 4 options, not per scenario), attitudes, parking behaviour, willingness to pay, free text, derived expected-fine
##variables. Covariates (source text, Spanish): cov_age_group, cov_gender (Hombre -> male, Mujer -> female, "Prefiero no decirlo"
##-> NA), cov_education, cov_household_income, cov_household_vehicle, cov_city (typed city, 'Ciudad'), cov_province ('Provincia'). No survey weight. No identifying columns.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_excel(file.path(raw, "Data.xlsx"), sheet = "Original"))
stopifnot(nrow(d) == 2150, ncol(d) == 74)
d <- d[!grepl("No poseo licencia|No tengo licencia", d[[2]], ignore.case = TRUE) & !grepl("Menor de 18", d[[1]], ignore.case = TRUE)]
stopifnot(nrow(d) == 2150)
d[, id := .I]
sp <- data.table(
 scenario = rep(1:6, each = 4), alt = rep(c("A", "B", "C", "D"), 6),
 distance = c(100,300,50,100, 300,600,100,200, 600,300,50,150, 100,600,100,300, 300,100,50,200, 600,300,100,150),
 cost = c(1.5,2.0,0.0,1.0, 0.5,1.5,0.0,2.0, 0.0,2.0,0.0,1.5, 2.0,0.5,0.0,0.5, 1.5,2.0,0.0,1.0, 0.5,1.5,0.0,2.0),
 pspace = c(60,90,80,NA, 30,60,60,NA, 90,60,30,NA, 60,30,90,NA, 60,90,60,NA, 30,60,80,NA),
 stime = c(15,5,10,NA, 30,15,15,NA, 5,15,30,NA, 15,30,5,NA, 15,5,15,NA, 30,15,10,NA),
 pfine = c(0,0,40,0, 0,0,10,0, 0,0,70,0, 0,0,70,0, 0,0,40,0, 0,0,10,0),
 fine = c(0,0,50,0, 0,0,100,0, 0,0,100,0, 0,0,50,0, 0,0,100,0, 0,0,30,0),
 sec = c("Medium","High","Low","Medium", "High","Medium","Medium","High", "Medium","High","Low","High", "High","Medium","Low","Medium", "Medium","High","Medium","High", "Medium","High","Medium","High"),
 surv = c("Cameras","Guard","None",NA, "Cameras","None","None",NA, "Cameras","Guard","None",NA, "Cameras","None","None",NA, "Cameras","Guard","None",NA, "Cameras","Guard","None",NA))
stopifnot(nrow(sp) == 24)
opt <- c(A = "Regulated on-street parking", B = "Private parking", C = "Irregular parking", D = "Leave the vehicle at home and use another mode")
letter <- function(x) { l <- sub("^.*OPCI[OÓ]N ([ABCD]).*$", "\\1", toupper(iconv(x, to = "UTF-8")), perl = TRUE); ifelse(grepl("^[ABCD]$", l), l, NA_character_) }
ch <- sapply(12:17, function(j) letter(d[[j]]))
stopifnot(!anyNA(ch))
nz <- function(x, f) ifelse(is.na(x), "(not shown)", f(x))
rows <- rbindlist(lapply(1:6, function(s) rbindlist(lapply(1:4, function(k) {
  r <- sp[scenario == s & alt == c("A", "B", "C", "D")[k]]
  data.table(id = d$id, task = s, profile = k, choice = as.integer(ch[, s] == r$alt),
    attr_parking_option = opt[[r$alt]], attr_walking_distance = paste(r$distance, "m"),
    attr_parking_cost_2h = sprintf("USD %.2f", r$cost), attr_prob_finding_space = nz(r$pspace, function(x) paste0(x, "%")),
    attr_search_time = nz(r$stime, function(x) paste(x, "minutes")), attr_prob_fine = paste0(r$pfine, "%"),
    attr_fine_amount = paste("USD", r$fine), attr_security = r$sec, attr_surveillance = nz(r$surv, identity))
}))))
cv <- d[, .(id, cov_age_group = d[[1]], cov_gender = ifelse(d[[3]] == "Hombre", "male", ifelse(d[[3]] == "Mujer", "female", NA)),
            cov_education = d[[5]], cov_household_income = ifelse(d[[6]] == "Prefiero no responder", NA, d[[6]]),
            cov_household_vehicle = d[[8]], cov_city = d[[71]], cov_province = d[[74]])]
rows <- merge(rows, cv, by = "id")
setorder(rows, id, task, profile)
stopifnot(rows[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(rows$id) == 2150, !anyNA(rows[, .SD, .SDcols = patterns("^attr_")]))
dir.create(out, showWarnings = FALSE, recursive = TRUE)
fwrite(rows, file.path(out, "garciaramirez_2026_parking_national.csv"))
