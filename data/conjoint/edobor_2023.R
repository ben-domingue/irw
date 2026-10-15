##Cyclone insurance choice experiment with small coastal US business owners, from
##Edobor, E. W., Marshall, M. I., Katare, B., & Valdivia, C. (2024). Insuring for cyclone events: What matters to
##small business owners? Journal of the Agricultural and Applied Economics Association. https://doi.org/10.1002/jaa2.146
##Data: Purdue University Research Repository doi:10.4231/SF2E-WK20 (v1.0, 2023), CC0 1.0 Universal (landing page).
##Files read: Data_for_Choice Experiment.xls (inside the public bundle; Data_for_WTPAnalysis.xls not read) and, as
##text, the supporting docs "2022 Coastal Small Business Insurance Survey Codebook.pdf" (attribute definitions and
##the displayed choice cards CE1_1..) and "Description of Study Variables.pdf".
##Usage: Rscript edobor_2023.R <dir holding "Data_for_Choice Experiment.xls"> <output dir>
##
##598 small-business owners in 21 US coastal states (Qualtrics online survey, May-Jul 2022; 631 valid responses, 598
##kept by the authors' cleaning, as the deposit states). 6 choice tasks each (blocks 1-6 of a fixed blocked design,
##one block per respondent; the survey also showed a 7th, consistency-check task that is not in the data file).
##Each task: two cyclone insurance packages (Option 1, Option 2) plus a fixed "None of them" option WITHOUT
##attributes: an opt-out (opt_out = yes, 'None' rows dropped; choice = 0 on both profiles when it was chosen).
##Outcome (choice): "Among the following cyclone insurance options, which one do you prefer?" (cards CE1_1..).
##Long file: one row per respondent x set x alternative; Alternatives 1/2 are the packages, 3 is "None" (verified:
##'None'=1 on exactly the Alternatives = 3 rows and one chosen row per task). Profile = Alternatives (row order in the
##file is 1, 3, 2, so the code, not the row, gives the position; INFERRED to equal the on-screen Option number).
##The respondent key PID is the authors' pre-cleaning number: re-keyed to 1..598 in PID order. No other identifier.
##Attributes (displayed text from the codebook's choice cards): policy (Flood and Business Interruption Insurance /
##Windstorm and Business Interruption Insurance / Flood, Windstorm and Business Interruption Insurance), provider
##(Private / Government / Government and Private; the data say "Government-Private Corporation" etc.), coverage
##("60|75|90% of building, building contents, expenses and income"), premium ("20|50|80% above what you currently
##pay in total for all your business-related insurance"), waiting period ("24|48|72 hours After"), deductible
##("5|7.5|10% of Total Damage"). The file stores numbers for the last four; wording as on the cards.
##Restrictions: none documented. Level weights: no probabilities documented; shares near equal.
##trial_block = block number 1-6. Covariates: none in this file (respondent covariates are in the other xls, not read).
##Dropped: derived choice dummies (Floodbiz..None), Consistent, droplist, CE1-CE6 columns, _caseid.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_excel(file.path(raw, "Data_for_Choice Experiment.xls")))
stopifnot(nrow(x) == 10764, uniqueN(x$PID) == 598, x[, .N, PID][, all(N == 18)])
stopifnot(x[Alternatives == 3, all(None == 1)], x[Alternatives != 3, all(None == 0)], x[, sum(Choice), .(PID, Set)][, all(V1 == 1)])
x[, id := match(PID, sort(unique(PID)))]
p <- x[Alternatives != 3]
pv <- c("Private Corporation" = "Private", "Government Corporation" = "Government", "Government-Private Corporation" = "Government and Private")
d <- p[, .(id, task = as.integer(Set), profile = as.integer(Alternatives), choice = as.integer(Choice),
  attr_policy = policy, attr_provider = unname(pv[provider]),
  attr_coverage = paste0(coverage, "% of building, building contents, expenses and income"),
  attr_premium = paste0(premium, "% above what you currently pay in total for all your business-related insurance"),
  attr_waiting_period = paste0(period, " hours After"), attr_deductible = paste0(deductible, "% of Total Damage"),
  trial_block = as.integer(Block))]
stopifnot(!anyNA(d), d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 <= 1)], d[, uniqueN(trial_block), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "edobor_2023_cyclone_insurance.csv"))
