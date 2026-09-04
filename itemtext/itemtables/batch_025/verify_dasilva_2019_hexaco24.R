# verify_dasilva_2019_hexaco24.R
#
# Claim under test: IRW item code HEXACO24_n is column n of the HEXACO block
# (columns 9-32) of the figshare source workbook's "Base de dados" sheet, whose
# HEADER IS the administered Portuguese item text (data_labels), and the same n
# is the BHI item number the paper's numbered English list and the workbook's
# "Dimensoes" sheet use.
#
# Falsifiable prediction: the source columns are not interchangeable. Three of
# the 24 columns have a truncated observed range -- column 7 and column 15 were
# never answered "Concordo muito" (5) by any of the 240 complete respondents,
# and column 19 was never answered "Discordo muito" (1). If the positional
# assignment were shifted or permuted, those three restrictions would land on
# different item codes in the live table.
#
# Live side is fetched with irw_table_sets(per_item = TRUE) -- server-side
# aggregates, no whole-table export.

suppressMessages(library(irw))
TABLE <- "dasilva_2019_hexaco24"

# Raw source: per-column min/max/level-count over the 240 respondents with a
# complete HEXACO block, computed from figshare 10.6084/m9.figshare.7582019.v1,
# sheet "Base de dados", columns 9-32, under the labels-to-1..5 map in
# data/dasilva_2019_hexaco24.py. Hard-coded so the check runs offline.
RAW <- data.frame(
  n   = 1:24,
  min = c(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1),
  max = c(5,5,5,5,5,5,4,5,5,5,5,5,5,5,4,5,5,5,5,5,5,5,5,5),
  lev = c(5,5,5,5,5,5,4,5,5,5,5,5,5,5,4,5,5,5,4,5,5,5,5,5),
  nn  = rep(240, 24)
)

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
rownames(pi) <- pi$item

cat(sprintf("%-12s %14s %14s %8s\n", "item", "source(min-max/lev/n)", "live(min-max/lev/n)", "match"))
ok <- TRUE
for (i in 1:24) {
  code <- paste0("HEXACO24_", i)
  L <- pi[code, ]
  m <- (L$resp_min == RAW$min[i] && L$resp_max == RAW$max[i] &&
        L$n_resp_levels == RAW$lev[i] && L$n == RAW$nn[i])
  ok <- ok && isTRUE(m)
  cat(sprintf("%-12s %5d-%d/%d/%-4d %10d-%d/%d/%-4d %8s\n", code,
              RAW$min[i], RAW$max[i], RAW$lev[i], RAW$nn[i],
              L$resp_min, L$resp_max, L$n_resp_levels, L$n,
              if (isTRUE(m)) "yes" else "NO"))
}

cat("\nRestricted-range signature: source columns 7, 15 (max 4) and 19 (min 2);",
    "\nlive items", paste(pi$item[pi$n_resp_levels < 5], collapse = ", "), "\n")

cat("Note: this route pins the three restricted-range positions outright and shows\n",
    "no shift of the whole block; it does not by itself separate the 21 full-range\n",
    "items from one another. Those are tied by the source column headers being the\n",
    "item text (data_labels) and by the Dimensoes sheet / paper Table 1 assigning a\n",
    "distinct facet to each item number.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
