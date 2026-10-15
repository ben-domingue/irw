##Enset variety choice experiment in Ethiopia, from the Mendeley Data deposit "ChoiceTE" (Etensa, Alemu & Yayo;
##published 2026-05; "household survey, discrete choice experiment, and contingent valuation data collected from
##enset-producing households in Oromia and Central Ethiopia to analyze farmers' preferences and willingness to
##pay for improved climate-resilient enset varieties"). No article found; no article DOI.
##Deposit: doi:10.17632/yy3s5fdrxc (version 1), CC BY 4.0. File read: Choice.dta (long file; the deposit's other
##files, ChoiceMachinelearningdata.dta and probitdata_online.dta, hold the contingent-valuation and
##machine-learning analysis data and were not used).
##Usage: Rscript etensa_2026.R <dir holding Choice.dta> <output dir>
##
##Sample: 520 enset-growing households (Oromia and Central Ethiopia), 6 choice sets x 3 alternatives, forced choice
##(exactly one chosen per set; no opt-out). Alternatives 1 and 2 are improved varieties (asc = 1); alternative 3
##(asc = 0) has the same levels in every set (ebw 45, maturity 6, recurrent 3, yield 35, sequestration 0,
##price 65), i.e. the current/status-quo variety shown with its own levels, so it is profile 3 (no opt-out).
##6 attributes: ebw, maturity, recurrent, yield, sequestration, price.
##LABELS: codes only. The deposit has no codebook and the Stata variable labels give only the attribute names
##("EBW", "Maturity", "Recurrent", "Yield", "Sequestration", "Price"); neither the units nor the displayed
##wording of the levels is documented and the article could not be found. attr_* therefore hold the numeric level
##as stored, as text (e.g. "70"). Likely readings (not documented, not used): EBW = enset bacterial wilt (resistance
##level), price in ETB. Choice sets are in the file's `set` order 1-6 (task = set, recorded; the file stacks
##the 6 sets of alternative 1, then of alternative 2, then of 3: re-sorted here); profile = `alternatives` 1-3.
##Covariates kept: family size, extension service received (0/1, "Have you received any extension services",
##RECODE label), market access (0/1, "Do you have access to a market where you can ..." RECODE label), kebele code
##(saq06 1-18, labelled KB_1..KB_18). Dropped: log age and log TLU (derived), household id columns (re-keyed
##to 1..520), the authors' case/panel identifiers. No survey weight.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "Choice.dta")))
stopifnot(nrow(k) == 520 * 18, k[, uniqueN(saq01_household_id)] == 520, k[, .N, .(saq01_household_id, set)][, all(N == 3)],
          k[, sum(choice), .(saq01_household_id, set)][, all(V1 == 1)], k[alternatives == 3, all(asc == 0)], k[alternatives < 3, all(asc == 1)])
k[, id := as.integer(factor(saq01_household_id, levels = sort(unique(saq01_household_id))))]
o <- k[, .(id, task = as.integer(set), profile = as.integer(alternatives), choice = as.integer(choice),
           attr_ebw = as.character(as.integer(ebw)), attr_maturity = as.character(as.integer(maturity)),
           attr_recurrent = as.character(as.integer(recurrent)), attr_yield = as.character(as.integer(yield)),
           attr_sequestration = as.character(as.integer(sequestration)), attr_price = as.character(as.integer(price)),
           cov_family_size = as.integer(familysize), cov_extension_service = as.integer(extension),
           cov_market_access = as.integer(marketaccess), cov_kebele_code = as.integer(saq06))]
stopifnot(!anyNA(o[, 5:10]), o[profile == 3, uniqueN(paste(attr_ebw, attr_maturity, attr_price))] == 1)
setorder(o, id, task, profile)
fwrite(o, file.path(out, "etensa_2026_enset_varieties.csv"))
