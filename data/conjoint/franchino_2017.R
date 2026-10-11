##Two conjoint experiments on Eurozone economic policy and fiscal union (Italy) from
##Franchino, F., & Segatti, P. (2019). Public opinion on the Eurozone fiscal union: evidence from survey
##experiments in Italy. Journal of European Public Policy, 26(1), 126-148 (online 2017).
##https://doi.org/10.1080/13501763.2017.1400087
##Replication data: Taylor & Francis figshare doi:10.6084/m9.figshare.5596942 (v1), CC BY 4.0. Files read: dataset2.dta
##(inside "Replication material.zip", Stata value labels; only the columns listed below are read; the file is a
##988-column Italian panel survey, the rest is dropped); text only: Figure_3.do, Figure_4.do, Table_1.do,
##"RJPP_1400087_online appendix.docx" (Tables S6-S8: attribute lists and example choice screens).
##Usage: Rscript franchino_2017.R <dir holding dataset2.dta> <output dir>
##
##3,488 Italian adults (a survey sample with a replacement sample, SOURCE 1/2; mode and dates not stated in the files read) each have 4 rows in
##dataset2.dta = 2 tasks x 2 profiles of EACH of two conjoint experiments. TWO TABLES (different attribute sets):
##  franchino_2017_economic_policy: choice between two economic policy programs, 6 attributes (unemployment rate,
##     inflation rate, national social services and taxation, euro, European oversight of government budget, European social
##     services and taxation); 3,026 respondents with data (462 respondents have these variables missing: not shown them or lost).
##  franchino_2017_fiscal_union: choice between two fiscal union schemes, 6 attributes (tax rate, tax type, spending
##     destination, spending type, spending institution, auditing institution); 3,118 respondents (370 missing).
##TASK / PROFILE ARE INFERRED. The rows of the file are in random order across respondents, but a respondent's 4 rows keep
##their relative file order, and in rows 1-2 and rows 3-4 of every respondent exactly one profile is chosen in each experiment
##(all 3,026 / 3,118 respondents), which fixes the pairing; task = 1 for the first pair of rows, 2 for the second, profile = 1
##for the first row of the pair. Which pair was shown first and which profile on the left cannot be verified (the chosen
##profile is first in 50% of pairs: 0-1 and 1-0 patterns are balanced), the same row pairs hold both experiments.
##Level text: Stata value labels, completed from the appendix (Table S6/S7) where the label is abbreviated. Economic policy:
##unemployment 13%/7%/3%/1% (the appendix lists the last as "1% (full employment)", the example screen shows bare percentages:
##stored "1%"); inflation 0.5%/2%/5%/8%; taxsoc Same tax-spend = "Social services and taxation are adequate", Less tax-spend =
##"Cut taxes, even at the cost of fewer social services", More tax-spend = "More social services, even at the cost of higher
##taxes"; euro Keep euro / Ditch euro = "Keep the euro as the national currency" / "Replace the euro with a national currency";
##eucontrol Adequate / Less / More control = "Oversight is adequate" / "Less oversight" / "More oversight"; eutaxsoc Against /
##Additional / Alternate = "Social services and taxation must remain national prerogatives" / "European social services and
##taxation, in addition to national ones" / "...replacing national ones". The matching rests on the label order and wording (the
##value labels are English abbreviations of the appendix options). Fiscal union: tax rate 1/3/5/10 per mille; tax type
##Additional / Alternate "to national taxation"; spending destination Health, Unemployment benefits, Education, Infrastructure,
##Not earmarked; spending type Additional / Alternate "to national expenditure"; spending institution European Commission /
##National Government; auditing institution European Court of Auditors / European Commission / Italian Court of Auditors.
##Outcomes (same tasks): choice = Y1 / FU1, "Between these two programs [schemes], which one do you prefer?" (forced choice,
##no opt-out); rating = Y2 / FU2, "Are you for or against these two programs [schemes]? Express your opinion on a scale ranging from
##'strongly against' to 'strongly for'", 1 = molto contrario (strongly against), 2 = abbastanza contrario, 3 = abbastanza
##favorevole, 4 = molto favorevole (strongly for); higher = more favourable. Rows with no outcome are dropped.
##Randomization: the appendix says nothing on restrictions or level probabilities ("random" choice tasks); observed.
##Covariates: cov_survey_weight = WEIGHT (constant within respondent, as in the deposit; the authors' regressions do not state
##using it in the conjoint code); cov_eu_membership_view = D022 value-label text (Italian: "Secondo lei il fatto che l'Italia
##appartenga all'Unione Europea e' un bene, un male, ...": Un bene / Un male / N un bene, n un male / Non saprei), the authors'
##moderator in Figure 3 (missing for respondents without the first experiment). Dropped: SERIE (interview id), the 970 other
##survey columns (Italian survey items, party/leader, media, demographics), BASKET/SOURCE/PRE_EU sample flags.
##Respondents ids are re-keyed to 1..n within each table.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cols <- c("ID", "WEIGHT", "D022", "Y1", "Y2", "unemployment", "inflation", "taxsoc", "euro", "eucontrol", "eutaxsoc",
          "FU1", "FU2", "taxrate", "taxtype", "spend", "spendtype", "spendinst", "contrinst")
d <- as.data.table(read_dta(file.path(raw, "dataset2.dta"), col_select = all_of(cols)))
stopifnot(nrow(d) == 13952, d[, .N, ID][, all(N == 4)])
d[, k := seq_len(.N), ID]
d[, `:=`(task = (k + 1L) %/% 2L, profile = (k - 1L) %% 2L + 1L)]
lab <- function(x, map = NULL) { v <- as.character(as_factor(x, levels = "labels")); if (!is.null(map)) { stopifnot(all(v[!is.na(v)] %in% names(map))); v <- unname(map[v]) }; v }
d[, eu := lab(D022)]
mk <- function(tab, chc, rt, attrs) {
  x <- d[!is.na(get(chc)) & !is.na(get(rt))]
  stopifnot(x[, sum(get(chc)), .(ID, task)][, all(V1 == 1)], x[, .N, ID][, all(N == 4)])
  o <- x[, .(id = match(ID, sort(unique(ID))), task, profile, choice = as.integer(get(chc)), rating = as.integer(get(rt)),
             cov_survey_weight = WEIGHT, cov_eu_membership_view = eu)]
  for (n in names(attrs)) o[[paste0("attr_", n)]] <- attrs[[n]](x)
  setorder(o, id, task, profile)
  stopifnot(!anyNA(o[, .SD, .SDcols = patterns("^attr_|^rating$|^choice$")]))
  fwrite(o, file.path(out, paste0("franchino_2017_", tab, ".csv")))
  cat(tab, nrow(o), uniqueN(o$id), "\n")
}
mk("economic_policy", "Y1", "Y2", list(
  unemployment = function(x) lab(x$unemployment),
  inflation = function(x) lab(x$inflation),
  taxsoc = function(x) lab(x$taxsoc, c("Same tax-spend" = "Social services and taxation are adequate",
      "Less tax-spend" = "Cut taxes, even at the cost of fewer social services", "More tax-spend" = "More social services, even at the cost of higher taxes")),
  euro = function(x) lab(x$euro, c("Keep euro" = "Keep the euro as the national currency", "Ditch euro" = "Replace the euro with a national currency")),
  eucontrol = function(x) lab(x$eucontrol, c("Adeguate control" = "Oversight is adequate", "Less control" = "Less oversight", "More control" = "More oversight")),
  eutaxsoc = function(x) lab(x$eutaxsoc, c("Against" = "Social services and taxation must remain national prerogatives",
      "Additional" = "European social services and taxation, in addition to national ones", "Alternate" = "European social services and taxation, replacing national ones"))))
sp <- attr(d$spend, "labels"); stopifnot(length(sp) == 5)
mk("fiscal_union", "FU1", "FU2", list(
  taxrate = function(x) { v <- lab(x$taxrate); stopifnot(all(v %in% c("1‰", "3‰", "5‰", "10‰"))); v },
  taxtype = function(x) lab(x$taxtype, c("Additional" = "Additional to national taxation", "Alternate" = "Alternate to national taxation")),
  spend = function(x) c("Health", "Unemployment benefits", "Education", "Infrastructure", "Not earmarked")[as.integer(x$spend)],
  spendtype = function(x) lab(x$spendtype, c("Additional" = "Additional to national expenditure", "Alternate" = "Alternate to national expenditure")),
  spendinst = function(x) lab(x$spendinst),
  contrinst = function(x) lab(x$contrinst)))
