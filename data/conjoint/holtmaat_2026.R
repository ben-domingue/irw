##Overseas climate adaptation package (aid + climate migrants) paired conjoint, Netherlands, from
##Holtmaat, E. A., Dolšak, N., & Prakash, A. (2026). In situ or ex situ overseas climate adaptation?
##Public support for immigration and climate aid in the Netherlands. European Political Science
##Review, 18(2), 235-255. https://doi.org/10.1017/S1755773926100319 (OA, CC BY 4.0)
##Replication data: Harvard Dataverse doi:10.7910/DVN/OELHKG, CC0 1.0. File read: data_share.tab
##(the only file). Online appendix (S1755773926100319sup001.docx, Appendix 1 "Full survey") read for
##the attribute list and question wording.
##Usage: Rscript holtmaat_2026.R <dir holding data_share.tab> <output dir>
##
##1,199 Dutch online-panel respondents (paper n = 1199), 5 tasks of 2 policy packages, 6 attributes;
##11,990 rows exactly as the paper reports. Columns: BLOCK = ID = respondent, QES = task (1-5),
##ALT = profile (1-2), RES = chosen (exactly one per task, checked).
##Outcome choice: "We will present two policy packages side-by-side. Which policy would have your
##support?" (appendix 1; forced choice, policy 1 or policy 2, no opt-out).
##CODED ATTRIBUTES (#3474). The deposit stores each attribute only as a level index A1-A6 (plus the
##authors' A?L? dummies of the same, dropped as derived); no codebook, value labels or code map the
##indices to text. Every attribute is therefore attr_<name>_code, holding the deposited index.
##Attribute identity: appendix 1 lists the attributes as 1 Country (4 levels), 2 Accept climate
##migrants from this country per year (7), 3 Give climate aid to this country (EUR) per year (6),
##4 Extreme weather events experienced by the country (4), 5 Value of Dutch trade with this country
##(EUR) (4), 6 Year country seeks to achieve net zero emissions (4). The deposit's A1..A6 have
##exactly 4, 7, 6, 4, 4, 4 levels in that order, so A1..A6 are named after them (country, migrants,
##aid, weather, trade, net_zero_year). Levels as listed in the appendix: country
##Somalia/Pakistan/Colombia/Albania; migrants 0/100/300/600/1000/1500/2500; aid 0/3 million/
##10 million/50 million/100 million/200 million; weather Drought/Sea level rise/Floods/Wildfire;
##trade 0/500 million/1 billion/5 billion; year 2045/2050/2060/2070. NO source states which index is
##which level (the listing order is plausible but unverified), so the codes are kept as deposited.
##Randomization: "randomly assigned/unrestricted" (appendix 1); attribute order not documented.
##Benchmark arms: before the conjoint each respondent read one of three introductions (appendix 1
##Options 1-3: no benchmark / Dutch past-record benchmark / developed-countries benchmark); the
##deposit's Segment* dummies -> trial_benchmark ("none", "dutch", "developed_countries"), one per
##respondent (checked). The paper finds the arms do not change results and pools them.
##Covariates: cov_gender (Q14, Dutch text: Man = male, Vrouw = female, Non-binair = other, Zeg ik
##liever niet = NA), cov_birth_year (Q15), cov_education (Q33, Dutch answer text as deposited;
##"Zeg ik liever niet" = NA), cov_work_sector, cov_income (Dutch text; the euro sign arrived
##mis-encoded and is restored to EUR text), cov_religion (Dutch text), cov_children (Q38 number
##input as recorded; a few implausible values such as 788 and 4551 kept raw), cov_charity (Ja/Nee),
##cov_ideology (Q36, 1 = extreme left .. 10 = extreme right), cov_integration_<country> (1 = low ..
##7 = high difficulty integrating into Dutch society), cov_aid_effective (Q12, 1 = strongly disagree
##.. 7 = strongly agree that climate aid helps adaptation), cov_pride_dutch (Q13, same scale).
##Dropped: the respondent ID (panel number; re-keyed to 1..n), BLOCK/STR (copies of ID), the A?L?
##dummies, Q4 (attention check, constant: failers were screened out before the conjoint).
##No survey weight in the deposit. The postal code asked in the survey is not deposited.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "data_share.tab"), encoding = "UTF-8")
stopifnot(nrow(k) == 11990L, all(k$ID == k$BLOCK))
k[, idn := match(ID, sort(unique(ID)))]
d <- data.table(id = k$idn, task = as.integer(k$QES), profile = as.integer(k$ALT), choice = as.integer(k$RES))
an <- c(A1 = "country", A2 = "migrants", A3 = "aid", A4 = "weather", A5 = "trade", A6 = "net_zero_year")
nl <- c(A1 = 4L, A2 = 7L, A3 = 6L, A4 = 4L, A5 = 4L, A6 = 4L)
for (v in names(an)) {
  x <- as.integer(k[[v]]); stopifnot(all(x %in% seq_len(nl[[v]])), uniqueN(x) == nl[[v]])
  d[, paste0("attr_", an[[v]], "_code") := x]
}
seg <- k[, .(SegmentNobenchmark, SegmentDutchbenchmark, SegmentDevelopedcountriesben)]
stopifnot(all(rowSums(seg) == 1L))
d[, trial_benchmark := c("none", "dutch", "developed_countries")[max.col(as.matrix(seg))]]
stopifnot(d[, uniqueN(trial_benchmark), id][, all(V1 == 1L)])
g <- k$Q14_Gender; stopifnot(all(g %in% c("Man", "Vrouw", "Non-binair", "Zeg ik liever niet")))
d[, cov_gender := fcase(g == "Man", "male", g == "Vrouw", "female", g == "Non-binair", "other", default = NA_character_)]
d[, cov_birth_year := as.integer(k$Q15_Birthyear)]
d[, cov_education := fifelse(k$Q33_Educationlevel == "Zeg ik liever niet", NA_character_, k$Q33_Educationlevel)]
d[, cov_work_sector := k$Q34_Worksector]
inc <- k$Income; inc <- gsub("[^ -~]+", "EUR ", inc, perl = TRUE); inc <- gsub("EUR  ", "EUR ", inc, fixed = TRUE)
d[, cov_income := trimws(inc)]
d[, cov_religion := k$Q37_Religion]
d[, cov_children := as.integer(k$Q38_Numberofchildren)]
d[, cov_charity := k$Charity]
d[, cov_ideology := as.integer(k$Q36_PoliticalideologyOption)]
for (cn in c("Pakistan", "Albania", "Somalia", "Colombia")) d[, paste0("cov_integration_", tolower(cn)) := as.integer(k[[paste0("Integration_", cn)]])]
d[, cov_aid_effective := as.integer(k$Q12_Climateaidandadaptatio)]
d[, cov_pride_dutch := as.integer(k$Q13_PrideinDutchcultureOp)]
stopifnot(d[, .N, .(id, task)][, all(N == 2L)], d[, sum(choice), .(id, task)][, all(V1 == 1L)],
          d[, uniqueN(task), id][, all(V1 == 5L)], uniqueN(d$id) == 1199L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "holtmaat_2026_climate_adaptation.csv"))
