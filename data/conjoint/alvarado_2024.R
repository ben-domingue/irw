##Tax-fairness conjoints in four countries from
##Alvarado, M. (2024). Compensation and tax fairness: Evidence from four countries. British
##Journal of Political Science, 54(4), 1023-1042. https://doi.org/10.1017/S0007123423000698
##Replication data: Harvard Dataverse doi:10.7910/DVN/A6115X, CC0 1.0, no restricted files.
##Files read: Conjoint_Argentina.csv, Conjoint_Australia.csv, Conjoint_Chile.csv,
##Conjoint_USA.csv (raw Qualtrics exports, text answers coded numerically, three header
##rows; the randomizer's F-<task>-<profile>-<row> fields hold the level text). Sample rules
##from wrangling.R (read as text); design facts from the article (open access, CC BY 4.0).
##Usage: Rscript alvarado_2024.R <raw dir> <output dir>
##
##FOUR TABLES, one per country: the level text differs by country (currency amounts, sales
##tax shares, one source-of-income wording, and Spanish in Argentina and Chile), and the
##article reports each country separately.
##  alvarado_2024_tax_fairness_us (MTurk, October 2017)
##  alvarado_2024_tax_fairness_australia, _chile, _argentina (Respondi quota samples,
##  February 2020)
##Each respondent saw 5 pairs of hypothetical individuals (profile 1 = left, 2 = right) with 3
##attributes, levels as displayed: attr_income (Annual income / Ingreso mensual, e.g.
##"$40,000"/"$90,000"/"$160,000" in Australia), attr_sales_tax (Percentage of income paid in
##sales taxes / Porcentaje del ingreso pagado en impuestos al consumo (IVA), e.g.
##"1%"/"5%"/"10%"), attr_income_source (Source of income / Fuente de ingresos: effort, e.g.
##"Started own small business"; social background, e.g. "Appointed by parent in company they
##direct"; state benefit "Owns business that was bailed out by government"; luck "Receives
##annuity from lottery prize"; Spanish equivalents). The article says the attributes were
##fully randomized and varied independently. Attribute row order was randomized once per
##respondent (verified fixed across tasks): attrpos_* (1 = top).
##Outcome: choice = "Which of the two individuals would you personally prefer to charge a
##higher tax rate to?" (Spanish: "¿Cuál de las dos personas preferiría usted que pague una
##tasa de impuestos más alta?"). choice = 1 for the person chosen to pay MORE tax (being
##chosen is unfavourable; kept as asked). Forced choice between the two; -99 (skipped) and
##blank answers have no outcome and those tasks are omitted.
##Sample: every response with at least one answered task. cov_in_authors_sample = 1 for the
##authors' analysis sample: finished, consented and reached the conjoint (non-US; the US
##export has no separate consent variable), not the one duplicate Australian respondent
##(R_1LLjoVOtuK1Jh9Y, dropped by the authors as a repeat), and not a speeder (duration below
##half the median of those respondents). Counts compared with the article in the return.
##The authors' US entropy-balancing weights (weights.do, built from a file not deposited)
##are not available.
##Dropped (PII and free text): IP address, latitude/longitude, postcode/ZIP, the open
##"why did you choose ..." justification, US mTurkCode; also all other survey items (their
##numeric codes carry no value labels in the export). Ids: ResponseIds re-keyed to integers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cfg <- list(argentina = list(f = "Conjoint_Argentina.csv", q = paste0("ch", 1:5)),
            australia = list(f = "Conjoint_Australia.csv", q = paste0("ch", 1:5)),
            chile = list(f = "Conjoint_Chile.csv", q = paste0("ch", 1:5)),
            us = list(f = "Conjoint_USA.csv", q = c("Q26", "Q65", "Q67", "Q69", "Q71")))
an <- c("Annual income" = "income", "Ingreso mensual" = "income",
        "Percentage of income paid in sales taxes" = "sales_tax", "Porcentaje del ingreso pagado en impuestos al consumo (IVA)" = "sales_tax",
        "Source of income" = "income_source", "Fuente de ingresos" = "income_source")
for (nm in names(cfg)) {
  x <- fread(file.path(raw, cfg[[nm]]$f), colClasses = "character", na.strings = NULL, encoding = "UTF-8")[-(1:2)]
  stopifnot(!anyDuplicated(x$ResponseId))
  rn <- sapply(1:3, function(k) x[[sprintf("F-1-%d", k)]])
  ok <- rowSums(rn != "") == 3
  for (t in 2:5) stopifnot(all((sapply(1:3, function(k) x[[sprintf("F-%d-%d", t, k)]]) == rn)[ok, ]))
  short <- matrix(an[rn], nrow(x))
  base <- x$Finished == "1"
  if (nm != "us") base <- base & x$consent == "1" & x$`t_t1_First Click` != ""
  if (nm == "australia") base <- base & x$ResponseId != "R_1LLjoVOtuK1Jh9Y"
  dur <- as.numeric(x$`Duration (in seconds)`)
  auth <- base & dur >= median(dur[base]) / 2
  d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
    ans <- x[[cfg[[nm]]$q[t]]]
    stopifnot(all(ans %in% c("", "-99", "1", "2")))
    y <- data.table(r = seq_len(nrow(x)), task = t, profile = p,
                    choice = fifelse(ans %in% c("1", "2"), as.integer(ans == as.character(p)), NA_integer_))
    lv <- sapply(1:3, function(k) x[[sprintf("F-%d-%d-%d", t, p, k)]])
    for (v in c("income", "sales_tax", "income_source")) {
      j <- max.col(short == v & !is.na(short), ties.method = "first")
      y[, paste0("attr_", v) := lv[cbind(seq_len(nrow(x)), j)]]
      y[, paste0("attrpos_", v) := j]
    }
    y
  }))))
  d <- d[!is.na(choice)]
  stopifnot(d[, .N, .(r, task)][, all(N == 2)], d[, sum(choice), .(r, task)][, all(V1 == 1)],
            !anyNA(short[unique(d$r), ]), all(d$attr_income != ""), all(d$attr_sales_tax != ""), all(d$attr_income_source != ""))
  d[, cov_in_authors_sample := as.integer(auth[r])]
  setorder(d, r, task, profile)
  d[, id := match(r, unique(r))][, r := NULL]
  setcolorder(d, c("id", "task", "profile", "choice"))
  fwrite(d, file.path(out, paste0("alvarado_2024_tax_fairness_", nm, ".csv")))
}
