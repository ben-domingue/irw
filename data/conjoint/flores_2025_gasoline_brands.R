##Gasoline station visits rated on brand, price and waiting time: rated hypothetical cards, Monterrey (Mexico)
##Flores, D., & Arteaga, J. C. (2025). Conjoint gasoline data [Data set]. Mendeley Data, v1.
##Deposit: doi:10.17632/vdrhxr25m5, CC BY 4.0 (Mendeley data_licence field). No paper DOI listed.
##File read: Database.xlsx (sheet "Data" for the data, sheet "Variables description" for the codebook; Data saved as
##db.xlsx). Usage: Rscript flores_2025_gasoline_brands.R <dir holding db.xlsx> <output dir>
##
##Online survey of 270 drivers in the Monterrey metropolitan area (the deposit text says 274). Each respondent rated 12
##hypothetical gas-station visits (Opcion 1-12) described by brand (Oxxo Gas, Petro 7, Pemex, Mobil, Fullok, BP; each
##brand appears in 2 of the 12 cards), waiting time (5 or 20 minutes) and price. Three questionnaire versions (Version 1-3),
##each a fixed set of 12 cards (verified: the card is identical for every respondent of a version and Opcion); respondents
##saw the cards of their version only. Fixed design, all respondents of a version saw the same 12 cards; brand x wait x
##price combinations are not independent (price is tied to the card). trial_version stores the version.
##Price: the deposit has price columns for 87-octane and for 91-octane gasoline (precio_87, precio_91; both pesos, per the
##description "price (for 87 and 91 octane gasoline, respectively)"). Both are stored as two attributes, attr_price_87 and
##attr_price_91; that both were displayed on every card is INFERRED from this description, the questionnaire is not in the
##deposit. The currency is not stated outright (weekly spend is in pesos).
##Outcome: rating = Valoracion, "Rate given to a hypothetical visit, scale of 1 to 10" (Variables description). Direction and
##anchors are not documented; stored raw. task = Opcion (card number in the version), profile = 1; the display order is not
##documented. 49 respondents answered only some cards (Completa = 0); their answered cards are kept, unrated cards (227 rows)
##are omitted. 270 respondents appear, 3,013 ratings.
##Covariates kept (all from Data): cov_gender (Sexo: Femenino -> female, Masculino -> male), cov_age_group (Edad text, Spanish),
##cov_municipality (Municipioderesidencia), cov_fuel_used (gas_usada text), cov_weekly_spend (gasto_semanal text),
##cov_hybrid_car (hibrido: Si/No).
##Dropped: dummy and interaction columns (oxxogas ... bp, inter_*, _est_*, log_p87/p91, baja/media/alta, R_*, nueva = a derived 1-3
##recode of the rating), brand-knowledge and usage dummies (cono_*, usa_*), free-text questions, the respondent timestamps
##(inicio, fin), the second ID column and the respondent id of the source (re-keyed to integers). No names, emails, IPs.
suppressMessages({library(readxl); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(suppressWarnings(suppressMessages(read_excel(file.path(raw, "db.xlsx"), sheet = "Data", guess_max = 10000))))
stopifnot(nrow(x) == 3240, uniqueN(x$identifica) == 270, x[, .N, by = identifica][, all(N == 12)])
x[, card := paste(Marca, Minutos, precio_87, precio_91)]
stopifnot(x[, uniqueN(card), by = .(Version, Opcion)][, all(V1 == 1)])
x <- x[!is.na(Valoracion)]
stopifnot(all(x$Valoracion %in% 1:10))
lab <- function(v) ifelse(v == "Femenino", "female", ifelse(v == "Masculino", "male", NA_character_))
d <- x[, .(id = match(identifica, sort(unique(identifica))), task = as.integer(Opcion), profile = 1L, rating = as.integer(Valoracion),
           attr_brand = Marca, attr_wait_minutes = as.character(Minutos),
           attr_price_87 = as.character(precio_87), attr_price_91 = as.character(precio_91),
           cov_gender = lab(Sexo), cov_age_group = Edad, cov_municipality = Municipioderesidencia,
           cov_fuel_used = gas_usada, cov_weekly_spend = gasto_semanal, cov_hybrid_car = hibrido,
           trial_version = as.integer(Version))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "flores_2025_gasoline_brands.csv"))
