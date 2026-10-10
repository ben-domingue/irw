##Forest biodiversity contract DCE (private forest owners, Denmark and Finland) from
##Süring, C., & Lundhede, T. (2025). Private forest owner preferences for action- and
##result-based biodiversity restoration contracts - A discrete choice experiment in Denmark and
##Finland. Forest Policy and Economics. https://doi.org/10.1016/j.forpol.2025.103609
##Data: Zenodo record 18289556 (doi:10.5281/zenodo.18289556), "Forest biodiversity contract design
##survey dataset" (Süring, C.), CC BY 4.0. File read: Data_clean.csv (semicolon-separated).
##Also read: Codebook.docx (variable list with English labels + Danish reference questionnaire,
##via pandoc). The article (CC BY, KU repository) is behind a bot check and was not read.
##Usage: Rscript suring_2025.R <dir holding Data_clean.csv> <output dir>
##
##Labelled DCE: 9 choice sets per respondent, each "Kontrakt A", "Kontrakt B" and "Ingen af dem"
##(neither). The two contracts are the codebook's management-based (m_*) and results-based (r_*)
##alternatives: profile 1 = management-based, profile 2 = results-based (var95 codes 1 and 2).
##Whether the management-based contract was always "Kontrakt A" is not documented. The
##neither option has no attributes: OPT-OUT, choice = 0 on both profiles (12,840 of
##the 28,979 answered main-survey tasks).
##Choice question (Danish questionnaire): "Vi vil nu bede dig om at træffe 9 valg mellem to
##forskellige kontraktversioner A og B ... Hvis ingen af de to præsenterede kontraktversioner er
##attraktive for dig, kan du vælge 'Ingen af dem'", row "Dit valg".
##ONE TABLE with cov_country: the depositors pool both countries in one file with one codebook,
##the design is identical, and the level text is shared (English codebook labels); only the
##compensation currency differs (see below). Display languages Danish and Finnish.
##Kept: main surveys only (data_collec "Main survey (Danish)" / "(Finnish)"); the two Danish
##pilots (107 respondents, ids 1P*/2P*) are dropped as separate fieldings. Tasks with
##avail = 0 ("choice not available": no answer or more than one option ticked, codebook var96)
##are dropped (a few carry a choice code 1/2: more than one option ticked); respondents with no available task drop out: 1,716 Danish and 1,631 Finnish
##respondents remain. The Zenodo description gives 1,795 Danish and 1,631 Finnish owners: the
##Danish gap (79) is not explained by the pilots alone (flagged, not fixed).
##TASK is INFERRED from row order (every respondent has exactly 9 consecutive rows, matching the
##9 choice sets; no task column in the file). Not verifiable beyond the count.
##Attributes (levels = codebook English labels; Danish/Finnish display text only in the
##questionnaire template, "XX" placeholders):
##  attr_objective: contract objective, alternative-specific (management: deadwood / gaps / age
##    classes; results: beetles / ground vegetation / birds), stored as the codebook's full
##    objective wording (vars 61-66). RESTRICTION: objectives come in fixed pairs within a task
##    ("Vi benytter de følgende tre par af kontraktmål"): Deadwood with Beetles, Gaps with
##    Plants, Age classes with Birds (checked: no other pairing occurs).
##  attr_compensation: "Maksimal kompensation pr. ha (for 20-års perioden)". The file stores
##    DKK for both countries, Finnish EUR amounts converted at 7.45 (codebook var87-88). Stored
##    as the amount shown: Danish "15000 DKK" ... "65000 DKK"; Finnish amounts converted back to
##    EUR ("2000 EUR" ... "8500 EUR"; the six FI DKK values divide exactly by 7.45). The
##    "<number> <currency>" format is ours.
##  attr_threshold (No threshold / Stepped threshold / Single threshold), attr_payment_schedule
##    (Payment at contract start / Yearly installments / Payment at contract end),
##    attr_measuring_reporting (External examiner / Forest owner / Forest owner + consultant):
##    codebook code labels (vars 89-94), capitalised.
##Not kept as an outcome: ha_enroll (hectares the respondent would enrol under the chosen
##contract, asked after each choice; exists only for the chosen profile).
##Covariates: cov_country (DK/FI from the id prefix), cov_gender (gender: 0 male, 1 female, 2
##other; codebook var79), cov_age (age, years as entered; implausible values (<18 or >110) set
##NA), cov_education (educ, codebook var82 English labels), cov_region (region, codebook var10
##names, country-specific code lists), cov_income_code (income, CODES 0-10, country-specific
##bands in codebook var83), cov_duration_sec (duration, whole survey), and the remaining
##respondent variables under their source names as stored (forest size, shares, schemes, trust,
##perceived biodiversity base_*, likelihood full_*/half_*, pref_*, all_optout/all_optin,
##dif_*, child, f_inc, sessions, last_page). Dropped: RespID (re-keyed to integers in file
##order), start/end timestamps, data_collec, the three FREE-TEXT fields otheruse,
##other_scheme2, other_legis2 (some entries carry identifying detail), avail, ha_enroll,
##ha_avail. No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "Data_clean.csv"), sep = ";", na.strings = "NA", encoding = "UTF-8")
stopifnot(nrow(s) == 43488, s[, .N, RespID][, all(N == 9)], s[, uniqueN(data_collec), RespID][, all(V1 == 1)])
s[, task := seq_len(.N), RespID]
s <- s[data_collec %in% c("Main survey (Danish)", "Main survey (Finnish)")]
s[, cc := substr(RespID, 1, 2)]
stopifnot(all(s$cc %in% c("DK", "FI")), s[, all((cc == "DK") == (data_collec == "Main survey (Danish)"))])
stopifnot(all(s[avail == 1, choice] %in% 0:2))
s <- s[avail == 1]
obj <- c(Deadwood = "Leaving 10m^3 of deadwood per enrolled hectare every 4 years",
         Gaps = "Creating 4 new canopy cover gaps of minimum 150m^2 per enrolled hectare within the first 4 contract years",
         "Age classes" = "Introducing 2 new tree age classes in every enrolled hectare (one in the first 4 contract years and one in the last 4 contract years)",
         Beetles = "4 additional native species of saproxylic beetles (present in every enrolled hectare)",
         Plants = "4 additional native species of ground vegetation (herbs and woody plants) (present in every enrolled hectare)",
         Birds = "4 additional native species of birds (present in every enrolled hectare)")
stopifnot(s[, all(paste(m_objec, r_objec) %in% c("Deadwood Beetles", "Gaps Plants", "Age classes Birds"))])
thr <- c("No threshold", "Stepped threshold", "Single threshold")
sch <- c("Payment at contract start", "Yearly installments", "Payment at contract end")
mr <- c("External examiner", "Forest owner", "Forest owner + consultant")
comp <- function(x, cc) {
  dk <- c(15000, 25000, 35000, 45000, 55000, 65000)
  stopifnot(all(x[cc == "DK"] %in% dk), all((x[cc == "FI"] / 7.45) %in% c(2000, 3500, 4500, 6000, 7500, 8500)))
  fifelse(cc == "DK", paste(x, "DKK"), paste(round(x / 7.45), "EUR"))
}
s[, rid := match(RespID, unique(RespID))]
prof <- function(p, pre) {
  data.table(id = s$rid, task = s$task, profile = p, choice = as.integer(s$choice == p),
             attr_objective = unname(obj[s[[paste0(pre, "objec")]]]), attr_compensation = comp(s[[paste0(pre, "comp")]], s$cc),
             attr_threshold = thr[s[[paste0(pre, "thresh")]] + 1L], attr_payment_schedule = sch[s[[paste0(pre, "sched")]] + 1L],
             attr_measuring_reporting = mr[s[[paste0(pre, "mr")]] + 1L], row = seq_len(nrow(s)))
}
d <- rbind(prof(1L, "m_"), prof(2L, "r_"))
ctry <- c(DK = "Denmark", FI = "Finland")
cv <- s[, .(cov_country = unname(ctry[cc]), cov_gender = c("male", "female", "other")[gender + 1L],
            cov_age = fifelse(age >= 18 & age <= 110 & age == round(age), as.integer(age), NA_integer_),
            cov_education = c("Primary education", "Secondary or vocational education", "Bachelor degree or equivalent",
                              "Master degree or equivalent", "Doctoral degree")[educ + 1L],
            cov_region = fifelse(cc == "DK", c("Hovedstaden", "Midtjylland", "Nordjylland", "Sjælland", "Syddanmark")[region + 1L],
                                 c("Ahvenanmaa", "Etelä-Karjala", "Etelä-Pohjanmaa", "Etelä-Savo", "Kainuu", "Kanta-Häme", "Keski-Pohjanmaa",
                                   "Keski-Suomi", "Kymenlaakso", "Lappi", "Pirkanmaa", "Pohjanmaa", "Pohjois-Karjala", "Pohjois-Pohjanmaa",
                                   "Pohjois-Savo", "Päijät-Häme", "Satakunta", "Uusimaa", "Varsinais-Suomi")[region + 1L]),
            cov_income_code = as.integer(income), cov_duration_sec = as.numeric(duration))]
stopifnot(s[cc == "DK", all(region %in% c(0:4, NA))])
rest <- setdiff(names(s), c("RespID", "data_collec", "end", "start", "duration", "region", "otheruse", "other_scheme2", "other_legis2",
                            "gender", "age", "educ", "income", "m_objec", "r_objec", "m_comp", "r_comp", "m_thresh", "r_thresh",
                            "m_sched", "r_sched", "m_mr", "r_mr", "choice", "avail", "ha_enroll", "ha_avail", "task", "cc", "rid"))
for (v in rest) cv[, paste0("cov_", v) := s[[v]]]
d <- cbind(d, cv[d$row])[, row := NULL]
stopifnot(uniqueN(d[cov_country == "Denmark", id]) == 1716, uniqueN(d[cov_country == "Finland", id]) == 1631,
          !anyDuplicated(d[, .(id, task, profile)]), d[, sum(choice), .(id, task)][, all(V1 <= 1)],
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "suring_2025_forest_contracts.csv"))
