##Polish dairy farmers' choice between contracts (DCE: action, PROW, time, rate), CONSOLE project WP3 Task 3.2 pan-EU farmer survey,
##Polish sample, from the data set
##Wąs, A., Majewski, E., & Malak-Rawlikowska, A. (2022). CONSOLE_WP3_Task3.2_Pan-EU survey of farmers and other rural
##landowners_PL_2022.10.20_v01 [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7228611 (CC BY 4.0, stated in the
##record and in the deposited .txt). No article or questionnaire is linked.
##Files read: CONSOLE_WP3_Task3.2_Pan-EU survey of farmers and other rural landowners_PL_2022.10.20_v01.RData (object
##input.data, 4,039 rows x 37 columns) and the .txt (metadata only).
##Usage: Rscript was_2022.R <dir holding the .RData> <output dir>
##
##Design: 302 farmers (personid) x 9 choice sets (cs, set number 1-36 of the design; 9 per farmer) x alternatives A and B
##plus an alternative C whose levels are all 0 in the deposit (no contract): C is treated as an opt-out (no profile row),
##choice = 0 on both profiles when value = "C" (2,642 of 4,039 rows; 1,321 of 2,718 sets). The deposit's long rows are a
##modelling format (one row for a set where A or B was chosen, two where C was); the script rebuilds each set from the
##wide *_A / *_B columns, which are constant within farmer x set (checked), with value = the chosen alternative.
##task = rank of cs within farmer (display order NOT recorded; trial_cs keeps the design set number); profile 1 = A,
##2 = B (recorded).
##CODED ATTRIBUTES (#3474). No codebook, questionnaire or article gives the displayed text or units. Every attribute is
##kept as deposited, named after the deposit's variable: attr_dzialanie_code (Dzialanie = "action": the authors'
##short Polish labels Szczepionka / Dodatki / Biofiltry, i.e. vaccine / feed additives / biofilters by the words'
##meaning; the displayed wording is unknown), attr_czy_prow_code (Czy_PROW = "whether PROW", 0/1; PROW is the Polish
##Rural Development Programme; 1 = yes by the variable name; displayed wording unknown), attr_czas_code (Czas = "time",
##1 / 5 / 10, unit not stated), attr_stawka_code (Stawka = "rate", 100-980, 17 values, unit/currency not stated).
##Outcome: choice among A, B and C; wording not deposited; opt_out = yes (C).
##Covariates (farm-level, as deposited; Polish variable names kept): cov_wojewodztwo_code (region code A2/A7/A10/A14,
##unlabelled), cov_krowy_mleczne (number of dairy cows), cov_przecietna_wydajnosc (average milk yield), cov_pozostale_bydlo
##(other cattle), cov_ur (agricultural land), cov_tuz (permanent grassland), cov_pracownicy (workers),
##cov_sytuacja_materialna_code (financial situation, unlabelled code), cov_nastepca (successor, as deposited),
##cov_metan_code (unlabelled). Dropped: X (row key), id.odpowiedzi, Stawka2, LKK (cow-count band, derived), rac,
##potrzeba / niepotrzeba, Udzial (modelling flags), the long-format attribute copies. No exclusions applied.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- list.files(raw, pattern = "\\.RData$", full.names = TRUE); stopifnot(length(f) == 1L)
e <- new.env(); stopifnot(load(f, envir = e) == "input.data"); k <- as.data.table(e$input.data)
stopifnot(nrow(k) == 4039L, uniqueN(k$personid) == 302L, all(k$value %in% c("A", "B", "C")))
w <- c("value", "Dzialanie_A", "Czy_PROW_A", "Czas_A", "Stawka_A", "Dzialanie_B", "Czy_PROW_B", "Czas_B", "Stawka_B")
stopifnot(k[, lapply(.SD, uniqueN), .(personid, cs), .SDcols = w][, all(as.matrix(.SD) == 1L), .SDcols = w])
stopifnot(all(k$Dzialanie_C == 0), all(k$Czy_PROW_C == 0), all(k$Czas_C == 0), all(k$Stawka_C == 0))
cv <- c("wojewodztwo", "krowy.mleczne", "przecietna.wydajnosc", "pozostale.bydlo", "UR", "TUZ", "pracownicy",
        "sytuacja.materialna", "nastepca", "metan")
stopifnot(k[, lapply(.SD, uniqueN), personid, .SDcols = cv][, all(as.matrix(.SD) == 1L), .SDcols = cv])
s <- unique(k[, c("personid", "cs", w, cv), with = FALSE])
stopifnot(nrow(s) == 2718L, s[, .N, personid][, all(N == 9L)])
s[, id := match(personid, sort(unique(personid)))]
s[, task := frank(cs, ties.method = "first"), id]
lv <- function(p) s[, .(id, task, profile = p, choice = as.integer(value == c("A", "B")[p]),
  attr_dzialanie_code = get(paste0("Dzialanie_", c("A", "B")[p])), attr_czy_prow_code = as.integer(get(paste0("Czy_PROW_", c("A", "B")[p]))),
  attr_czas_code = as.integer(get(paste0("Czas_", c("A", "B")[p]))), attr_stawka_code = as.integer(get(paste0("Stawka_", c("A", "B")[p]))),
  trial_cs = as.integer(cs), cov_wojewodztwo_code = wojewodztwo, cov_krowy_mleczne = krowy.mleczne,
  cov_przecietna_wydajnosc = przecietna.wydajnosc, cov_pozostale_bydlo = pozostale.bydlo, cov_ur = UR, cov_tuz = TUZ,
  cov_pracownicy = pracownicy, cov_sytuacja_materialna_code = as.integer(sytuacja.materialna), cov_nastepca = nastepca,
  cov_metan_code = as.integer(metan))]
d <- rbind(lv(1L), lv(2L))
stopifnot(all(d$attr_dzialanie_code %in% c("Szczepionka", "Dodatki", "Biofiltry")), all(d$attr_czy_prow_code %in% 0:1),
          all(d$attr_czas_code %in% c(1L, 5L, 10L)), d[, sum(choice), .(id, task)][, all(V1 <= 1L)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "was_2022_dairy_contracts_pl.csv"))
cat(nrow(d), uniqueN(d$id), d[, sum(choice), .(id, task)][, mean(V1 == 0)], "\n")
