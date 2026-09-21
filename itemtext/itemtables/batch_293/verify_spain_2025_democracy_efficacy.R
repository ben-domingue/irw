# verify_spain_2025_democracy_efficacy.R
#
# CLAIM UNDER TEST: the four live item codes p8de_1..p8de_4 carry the four
# P.8 statements in the order this batch shipped them, i.e.
#   p8de_1 = "La gente como yo no tiene ninguna influencia sobre lo que hace el Gobierno"
#   p8de_2 = "La gente como yo no tiene ninguna posibilidad de manifestar su opinion a los/as politicos/as"
#   p8de_3 = "Este quien este en el poder, siempre busca sus intereses personales"
#   p8de_4 = "Los/as politicos/as no se preocupan mucho de lo que piensa la gente como yo"
#
# WHY THERE IS ANYTHING TO CHECK: mapping_basis is data_labels (the CIS .sav
# labels each column P8DE_1..P8DE_4 with its statement) and data/spain_2025_democracy.do
# uses the source column name lowercased, so this table is exempt under Step 5b.
# The check below is run anyway because it is decisive and costs no export.
#
# THE FALSIFIABLE PREDICTION: the .do file drops resp in {3,8,9} for this block,
# so the number of surviving responses per column is fixed by the raw microdata
# and differs for all four columns. If two items' text were swapped, the shipped
# statement would sit against the wrong n.
#
# Hard-coded numbers come from CIS study 3497's own microdata file 3497_num.csv
# (md3497.zip, https://www.cis.es/documents/d/guest/md3497), counted as
# sum(!is.na(x) & !(x %in% c(3,8,9))) per column; and from the published
# marginals es3497mar (Pregunta 8, N=4.010), which print the four statements in
# the same order with their percentage distributions.

suppressMessages(library(irw))

TABLE <- "spain_2025_democracy_efficacy"

# n surviving the .do file's sentinel rule, per RAW COLUMN (3497_num.csv)
RAW_N <- c(P8DE_1 = 3979, P8DE_2 = 3983, P8DE_3 = 3967, P8DE_4 = 3956)

# published marginals, es3497mar Pregunta 8: % giving 1 / 2 / 3 / 4 / 5 / N.S. / N.C.
PUB <- rbind(
  P8DE_1 = c(35.8, 37.9, 0.2, 21.1, 4.4, 0.4, 0.2),
  P8DE_2 = c(26.0, 34.8, 0.1, 31.8, 6.4, 0.5, 0.4),
  P8DE_3 = c(37.4, 37.9, 0.6, 19.7, 4.0, 0.3, 0.1),
  P8DE_4 = c(36.0, 39.2, 0.7, 20.7, 2.7, 0.4, 0.3))
PUB_N <- round(4010 * rowSums(PUB[, c(1, 2, 4, 5)]) / 100)

# live per-item n, server-side aggregate -- no table export
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live <- setNames(pi$n, pi$item)
live <- live[c("p8de_1", "p8de_2", "p8de_3", "p8de_4")]

cat(sprintf("%-8s %10s %10s %8s %12s\n",
            "item", "raw col n", "live n", "diff", "pub-implied n"))
for (i in 1:4)
  cat(sprintf("%-8s %10d %10d %8d %12d\n",
              names(live)[i], RAW_N[i], live[i], live[i] - RAW_N[i], PUB_N[i]))

ok_counts <- all(live == RAW_N)
ok_unique <- length(unique(RAW_N)) == 4

cat(sprintf("\nall four raw-column n distinct: %s (%s)\n",
            ok_unique, paste(RAW_N, collapse = ", ")))
cat(sprintf("live n reproduce raw-column n exactly: %s\n", ok_counts))
cat("Published-marginal n are within 13 of the raw counts (rounding of one-decimal\n",
    "percentages against N=4010), so they corroborate rather than pin.\n", sep = "")
cat("What this does NOT establish: nothing about option_text/resp (the 1..5 anchors\n",
    "come from the same .sav value labels and are identical for all four items, so no\n",
    "per-item evidence exists or is needed), and nothing about the English in the\n",
    "_translated columns, which IRW produced.\n", sep = "")

cat(if (ok_counts && ok_unique) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
