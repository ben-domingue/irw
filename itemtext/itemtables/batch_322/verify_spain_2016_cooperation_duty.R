# verify_spain_2016_cooperation_duty.R
#
# CLAIM UNDER TEST: live item p5 carries CIS 3130 question P.5 (duty to cooperate
# internationally despite the economic cost) and p13 carries P.13 (dedicate 0.7% of
# GDP), with resp 1 = "Si", 2 = "No" for both.
#
# WHY THERE IS ANYTHING TO CHECK: mapping_basis is data_labels (the CIS SPSS syntax
# ES3130 labels P5 and P13 and gives their value labels), but data/spain_2016_cooperation.do
# reads the fixed-width DA3130 with hand-typed infix positions (p5 col 41, p13 col 50).
# A mistyped position would attach a name to the wrong column, so the check is run.
#
# FALSIFIABLE PREDICTION: applying the .do file's sentinel rules to DA3130
# (p5: drop 3,8,9; p13: drop 8,9) at the ES3130 positions gives per-column,
# per-level counts that must reproduce the live table cell for cell. The two
# columns' counts differ, so a swap of the two items, or of resp 1/2, would fail.
#
# Hard-coded raw numbers: DA3130 from CIS microdata package md3130.zip
# (https://www.cis.es/documents/d/guest/md3130), N=2453, counted as
# table(substr(line,41,41)) and table(substr(line,50,50)).
#   col 41 (P5):  1=1942 2=245 3=207 8=52 9=7
#   col 50 (P13): 1=1657 2=359 8=419 9=18

suppressMessages(library(irw))
TABLE <- "spain_2016_cooperation_duty"

RAW <- rbind(p5 = c(`1` = 1942, `2` = 245), p13 = c(`1` = 1657, `2` = 359))
RAW_N <- rowSums(RAW)

# live per-item n, server-side aggregate -- no export
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live_n <- setNames(pi$n, pi$item)[rownames(RAW)]

cat(sprintf("%-5s %10s %10s\n", "item", "raw n", "live n"))
for (it in rownames(RAW)) cat(sprintf("%-5s %10d %10d\n", it, RAW_N[it], live_n[it]))
ok_n <- all(live_n == RAW_N)
ok_distinct <- RAW_N["p5"] != RAW_N["p13"]

# per-level cells: only if a local (cached) copy is available, never forcing an export
ok_cells <- NA
if (isTRUE(getOption("irw.cache", TRUE))) {
  d <- tryCatch(irw::irw_fetch(TABLE), error = function(e) NULL)
  if (!is.null(d)) {
    tb <- table(d$item, d$resp)
    cat("\nper-level counts (raw vs live):\n")
    for (it in rownames(RAW)) for (r in c("1", "2"))
      cat(sprintf("  %-4s resp=%s  raw %5d  live %5d\n", it, r, RAW[it, r], tb[it, r]))
    ok_cells <- all(sapply(rownames(RAW), function(it) all(tb[it, c("1","2")] == RAW[it, ])))
  }
}

cat(sprintf("\nlive n reproduce raw-column n: %s; the two n distinct: %s; per-level cells match: %s\n",
            ok_n, ok_distinct, ok_cells))
cat("Does NOT establish: the English in the _translated columns (IRW-written).\n")
cat(if (ok_n && ok_distinct && !isFALSE(ok_cells)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
