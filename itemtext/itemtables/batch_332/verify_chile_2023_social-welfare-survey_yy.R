# Verification for chile_2023_social-welfare-survey_yy (batch_332, irw#2381 slice 02).
# Self-contained: does not source batch_204's verify_chile_common.R or any shared helper.
#
# SOURCE. Encuesta de Bienestar Social 2023 (EBS 2023), Subsecretaría de Evaluación Social /
# INE, Chile. The official codebook 'libro_de_codigos_ebs_2023.xlsx' (bidat.gob.cl resource
# e1756ef1-3581-4611-b3bb-19ad3550bda8; sha256 11947ccf16a7286f7e93f3c00d832ae3a7f53fc53650664097c32e7b0cab1e28),
# sheet 'Y' ("Módulo YY: Ingresos"), lists each variable Name, its Label, every value, its value
# label and the observed FREQUENCY of that value. The frequencies are hard-coded below, copied
# from that sheet, so this script needs only the live IRW table.
#
# WHAT IT ESTABLISHES. Reproducing every (item, value) frequency from the live table is a joint
# test of the item mapping and the value coding: a swap of yy1/yy5_a (both 3-level), a reversed
# scale, or a different sample would each break it, because every item's count vector is
# distinct. yy3 is an open numeric amount with no value labels, so it is pinned instead by its
# non-missing n: 11234 respondents minus the codebook's -99 (47) and -88 (390) = 10797.
# The live table also holds NA-resp rows; their per-item counts are compared against the
# codebook's missing codes plus the yy5_a skip (yy5 != 1), which checks that they are exactly
# the sentinel/skip cells (a response-table defect, not a mapping one).
suppressMessages(library(irw))
TABLE <- "chile_2023_social-welfare-survey_yy"

CB <- list(                       # codebook sheet 'Y', Frecuencia column, valid codes only
  yy1   = c(`1` = 1878, `2` = 5702, `3` = 3583),
  yy2   = c(`1` = 2144, `2` = 3922, `3` = 3155, `4` = 1809, `5` = 191),
  yy4   = c(`1` = 5601, `2` = 2906, `3` = 1643, `4` = 730, `5` = 314),
  yy5   = c(`1` = 4553, `2` = 6675),
  yy5_a = c(`1` = 2258, `2` = 1509, `3` = 770))
CB_MISSING <- c(yy1 = 7 + 64, yy2 = 3 + 10, yy3 = 47 + 390, yy4 = 3 + 26 + 11, yy5 = 3 + 3,
                yy5_a = 7 + 9 + (6675 + 3 + 3))   # yy5_a also skipped unless yy5 == 1
N_RESP <- 11234

d <- as.data.frame(irw::irw_fetch(TABLE))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
v <- d[!is.na(d$resp), ]

ok <- TRUE
cat("=== 1. codebook frequencies vs live counts (categorical items) ===\n")
cat(sprintf("%-6s %4s %9s %9s\n", "item", "val", "codebook", "live"))
tot <- hit <- 0
for (it in names(CB)) for (k in names(CB[[it]])) {
  live <- sum(v$item == it & v$resp == as.numeric(k)); tot <- tot + 1
  if (live == CB[[it]][[k]]) hit <- hit + 1 else ok <- FALSE
  cat(sprintf("%-6s %4s %9d %9d%s\n", it, k, CB[[it]][[k]], live, if (live == CB[[it]][[k]]) "" else "  <-- MISMATCH"))
}
cat(sprintf("  %d of %d match exactly\n", hit, tot))
extra <- v[v$item %in% names(CB) & !mapply(function(i, r) as.character(r) %in% names(CB[[i]]), v$item, v$resp), ]
cat(sprintf("  live categorical values outside the codebook's valid codes: %d\n", nrow(extra)))
if (nrow(extra)) ok <- FALSE

cat("\n=== 2. yy3 (open monetary amount, CLP) ===\n")
y3 <- v$resp[v$item == "yy3"]
cat(sprintf("  non-missing n: live %d vs codebook %d - 47 - 390 = %d\n", length(y3), N_RESP, N_RESP - 437))
cat(sprintf("  distinct values %d, min %s, median %s, max %s; all multiples of 1000: %s\n",
            length(unique(y3)), format(min(y3), big.mark = ","), format(median(y3), big.mark = ","),
            format(max(y3), big.mark = ","), all(y3 %% 1000 == 0)))
if (length(y3) != N_RESP - 437) ok <- FALSE

cat("\n=== 3. NA-resp rows vs codebook missing codes + skip (response-table defect check) ===\n")
na <- tapply(is.na(d$resp), d$item, sum)
for (it in names(CB_MISSING)) {
  cat(sprintf("  %-6s live NA %5d  codebook missing/skip %5d%s\n", it, na[[it]], CB_MISSING[[it]],
              if (na[[it]] == CB_MISSING[[it]]) "" else "  <-- differs"))
}
cat(sprintf("  distinct ids %d (codebook sample %d)\n", length(unique(d$id)), N_RESP))
cat("  (informational only: NA rows are a known response-side defect; the .do drops them since #2326)\n")

cat("\nVERDICT:", if (ok) "PASS" else "FAIL", "\n")
