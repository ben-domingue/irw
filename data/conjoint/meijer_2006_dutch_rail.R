##Dutch rail stated-preference experiment (Hague Consulting Group for NS, 1987), from
##Meijer, E. & Rouwendal, J. (2006). Measuring welfare effects in models with random coefficients. Journal of Applied
##Econometrics, 21(2), 227-244. doi:10.1002/jae.841. The data were first analysed in Ben-Akiva, M., Bolduc, D. & Bradley, M.
##(1993), Estimation of travel choice models with randomly distributed values of time (Laval, Recherche en Energie 9303).
##Replication data: JAE Data Archive at ZBW, doi:10.15456/jae.2022319.0711039686, CC BY 4.0 (the licence printed on the
##archive's resource page; the dataset's CKAN record leaves license_id empty). Ben 2026-11-15: the deposit's licence is
##taken as given, although the data were collected for NS. Files read: mr-data.txt (2,929 rows, whitespace-separated, no
##header) and readme.mr.txt (column definitions). The same data ship in the R package mlogit as `Train`; this table is
##built from the deposit, which mlogit matches row for row.
##Usage: Rscript meijer_2006_dutch_rail.R <dir holding mr-data.txt> <output dir>
##
##Design: 235 respondents, each making 5 to 19 paired choices (2,929 tasks, mean 12.5) between two train journeys that differ
##in some or all of fare, journey time, number of rail-to-rail transfers (interchanges) and comfort level. A designed choice
##experiment with fixed levels, not independently randomized attributes; the design itself is not documented in the deposit.
##No opt-out: every task records option 1 or option 2.
##Layout: id = the deposit's respondent index (column 1, already 1..235); task = the respondent-specific choice index
##(column 2, 1..n within respondent, recorded); profile = option 1 or option 2 (columns 4-7 and 8-11, recorded); choice = 1 for
##the chosen option (column 3: 3 = option 1 chosen, 4 = option 2 chosen).
##Attributes. The deposit gives values and units but not the text respondents saw, so the values are stored with the readme's
##units: attr_fare = fare in cents of a Dutch guilder ("2400 cents"; 1 guilder = 100 cents), attr_journey_time = minutes
##("150 minutes"), attr_interchanges = number of rail-to-rail transfers ("0 interchanges"). Comfort is a code with no text in
##any source read: attr_comfort_code = 0, 1 or 2 as deposited. The readme says only "comfort level"; the mlogit help page
##says 0, 1, 2 run in decreasing comfort (0 = most comfortable), which is not confirmed by the deposit.
##Dropped: columns 12-15, which the readme says "have not been used in the analysis" and does not define (they vary within
##respondent). No respondent covariates in the deposit; no weights. Question wording not in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "mr-data.txt"), header = FALSE)
stopifnot(nrow(d) == 2929, ncol(d) == 15, uniqueN(d$V1) == 235, all(d$V3 %in% c(3, 4)),
          d[, all(V2 == seq_len(.N)), by = V1][, all(V1)], !anyNA(d[, 1:11]),
          all(c(d$V7, d$V11) %in% 0:2))
prof <- function(k, fare, time, chg, comf)
  d[, .(id = V1, task = V2, profile = k, choice = as.integer(V3 == k + 2),
        attr_fare = paste(get(fare), "cents"), attr_journey_time = paste(get(time), "minutes"),
        attr_interchanges = paste(get(chg), "interchanges"), attr_comfort_code = get(comf))]
long <- rbind(prof(1L, "V4", "V5", "V6", "V7"), prof(2L, "V8", "V9", "V10", "V11"))
setorder(long, id, task, profile)
stopifnot(nrow(long) == 2 * 2929, long[, sum(choice), by = .(id, task)][, all(V1 == 1)])
fwrite(long, file.path(out, "meijer_2006_dutch_rail.csv"))
