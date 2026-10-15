##Marine user rights policy bundles, discrete choice experiment in Chile's Los Lagos region, from
##Albers, H. J., Chavez, C., Dissanayake, S., Dresdner, J., & Rakshit, A. (2026). Supporting and augmenting
##marine user rights: What do resource users want? Evidence from Chile (manuscript; replication package, no
##article DOI found).
##Deposit: Mendeley Data doi:10.17632/w2x33kmwhc (version 1), CC BY 4.0. Files read: "Base choice
##experiments.xlsx" (sheets "Survey data" = choices, "Elections" = design with Spanish level text),
##"Data_instituion_survey.xlsx" (sheet Hoja1, column C only: folio numbers of institutional respondents), README.docx
##and 01_build_sample_table2.do / 02_main_estimation_table3_A2_A3.do (read as text, never run).
##Usage: Rscript albers_2026.R <dir with the two xlsx files, named as in the deposit> <output dir>
##
##Sample: resource users (fishers, aquaculture and shellfish households and some institutional respondents such
##as cooperatives and agencies) in Los Lagos, Chile, 2018. 6 comparisons x 2 policy bundles per respondent,
##forced choice between "Alternativa 1" and "Alternativa 2" (the choice code is 1 or 2 = the bundle chosen);
##no opt-out. 36 bundle pairs in 6 blocks of 6 (fixed blocked design; each respondent saw one block of 6 design
##rows, in comparison order 1-6; trial_block = the block of the design row, (set-1) div 6 + 1). The survey sheet's
##own "Set N" column disagrees with the design row for 11 respondents (folios 226, 89, 94, 95, 134, 135, 166, 176,
##177, 189, 200: typed block number, apparent entry errors); the design row (column N, which the authors merge on)
##is used throughout.
##Attributes (design sheet, Spanish): AMERB (the management-area/TURF regime: no limits / keep current level
##of 40% / raise to 60%), surveillance, distance (400 m / 800 m), transferability of the right, and production
##restrictions. Level text is the Spanish text of the design sheet. Column names: attr_amerb, attr_surveillance,
##attr_distance, attr_transferability, attr_production_limits (the sheet's AMERB, Vigilancia, Distancia,
##Transferencia, Restringir).
##Respondents: following the authors' scripts, folios with exactly 6 records are kept (78 folios have 12 or 18
##records because the survey link was opened more than once and are excluded as the authors do), and folio 345
##is dropped (choice code 3, invalid). That leaves 222 respondents. The authors' estimation tables further
##drop institutional respondents (folios in Data_instituion_survey.xlsx): here they are kept and flagged
##(cov_institutional = 1 for 41 of the 222), so the 181 individual respondents can be selected. The question
##wording is not in the deposit (README: Table 1 / A1 reproduce the design only).
##No respondent covariates (the household survey sheets in the deposit hold interviewer and supervisor names, GPS
##and addresses and were not used). The enumerator-name column of the survey sheet is dropped.
##Folio numbers are re-keyed to integers. No survey weight.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(suppressMessages(read_excel(file.path(raw, "Base choice experiments.xlsx"), sheet = "Survey data")))
setnames(s, c("folio", "numerator", "block", "comparison", "set", "choice"))
s[, numerator := NULL]
s[, (names(s)) := lapply(.SD, as.integer)]
n <- s[, .N, folio]
s <- s[folio %in% n[N == 6, folio] & folio != 345]
stopifnot(s[, uniqueN(folio)] == 222, s[, .N, folio][, all(N == 6)], all(s$choice %in% 1:2),
          s[, uniqueN(comparison), folio][, all(V1 == 6)])
s[, block := (set - 1L) %/% 6L + 1L]
stopifnot(s[, uniqueN(block), folio][, all(V1 == 1)], s[, all(set == (block - 1L) * 6L + comparison)])
inst <- suppressMessages(read_excel(file.path(raw, "Data_instituion_survey.xlsx"), sheet = "Hoja1", range = "C2:C128"))
inst <- unique(na.omit(suppressWarnings(as.integer(inst[[1]]))))
e <- as.data.table(suppressMessages(read_excel(file.path(raw, "Base choice experiments.xlsx"), sheet = "Elections")))
nm <- names(e)
b1 <- e[, 2:6]; b2 <- e[, 9:13]
setnames(b1, c("amerb", "surveillance", "distance", "transferability", "production_limits"))
setnames(b2, c("amerb", "surveillance", "distance", "transferability", "production_limits"))
b1[, `:=`(set = as.integer(e[[1]]), profile = 1L)]; b2[, `:=`(set = as.integer(e[[8]]), profile = 2L)]
stopifnot(identical(as.integer(e[[1]]), 1:36), identical(as.integer(e[[15]]), 1:36), all(e[[7]] == 1), all(e[[14]] == 2))
des <- rbind(b1, b2)
o <- merge(s[, .(folio, block, task = comparison, set, choice)], des, by = "set", allow.cartesian = TRUE)
o[, id := as.integer(factor(folio, levels = sort(unique(folio))))]
o[, choice := as.integer(choice == profile)]
o <- o[, .(id, task, profile, choice, attr_amerb = amerb, attr_surveillance = surveillance, attr_distance = distance,
           attr_transferability = transferability, attr_production_limits = production_limits,
           trial_block = block, cov_institutional = as.integer(folio %in% inst))]
stopifnot(!anyNA(o), o[, sum(choice), .(id, task)][, all(V1 == 1)], o[, .N, .(id, task)][, all(N == 2)])
setorder(o, id, task, profile)
fwrite(o, file.path(out, "albers_2026_marine_user_rights.csv"))
