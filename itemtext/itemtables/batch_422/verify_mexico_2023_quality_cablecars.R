# verify_mexico_2023_quality_cablecars.R -- batch_422
#
# NO ITEM TEXT SHIPS FOR THIS TABLE (blocked). This script re-runs the evidence
# for the block: the item codes p5_11_1..p5_11_5 and p5_11a denote TWO different
# questions, because data/mexico_2023_quality.do appends ENCIG 2021 under
# ENCIG 2023 with no wave column and ENCIG renumbered section V between waves:
#   ENCIG 2023 q5.11 = "transporte publico por teleferico Cablebus o Mexicable"
#                      (8 Si/No items + 5.11a satisfaction)
#   ENCIG 2021 q5.11 = "autopistas con casetas de cuota" (toll highways)
#                      (5 Si/No items + 5.11a satisfaction)
# The .do file builds id = _n after `use 2023; append using 2021`, so ids
# 1..38966 are the 2023 wave (encig2023_01_sec1_A_3_4_5_8_9_10.csv has 38966
# rows, all matched in residentes) and ids > 38966 are the 2021 wave.
#
# The claim tested, and what would break it:
#   (a) the id<=38966 block reproduces the 2023 raw p5_11_* counts cell for cell
#       (raw 1=Si -> 0, 2=No -> 1 per the .do recode; 9 -> missing), so the 2023
#       reading of each code is the cable-car question with that option number;
#   (b) ids > 38966 carry responses on p5_11_1..5 and p5_11a only (never 6..8),
#       i.e. the 5-item 2021 block, and they are the large majority of rows.
# If (a) and (b) hold, the table pools cable-car and toll-highway answers under
# the same codes and no single item_text can be attached.
# PASS here means "the block's evidence reproduces", NOT "the mapping is clean".

suppressMessages(library(irw))
TABLE <- "mexico_2023_quality_cablecars"
N2023 <- 38966

# Raw counts from INEGI encig23_base_datos_csv.zip ->
# encig2023_01_sec1_A_3_4_5_8_9_10.csv (sha256 of the zip
# af733d867a568cbb0dadef4a5a793b02488a71728d1157860f14501f3d4c393d), fetched 2026-09-25.
# Si/No items: c(Si, No) ; p5_11a: c(1,2,3,4,5,6)
RAW23 <- list(
  p5_11_1 = c(622, 49), p5_11_2 = c(633, 34), p5_11_3 = c(646, 27),
  p5_11_4 = c(551, 120), p5_11_5 = c(614, 58), p5_11_6 = c(654, 19),
  p5_11_7 = c(643, 28), p5_11_8 = c(621, 16),
  p5_11a  = c(281, 356, 30, 4, 0, 2))

d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]
d$wave <- ifelse(d$id <= N2023, "2023", "2021")

ok <- TRUE
cat("(a) 2023 block (id <= 38966): live vs raw ENCIG 2023\n")
for (it in names(RAW23)) {
  x <- d$resp[d$item == it & d$wave == "2023"]
  obs <- if (it == "p5_11a") sapply(1:6, function(k) sum(x == k)) else c(sum(x == 0), sum(x == 1))
  m <- all(obs == RAW23[[it]])
  ok <- ok && m
  cat(sprintf("  %-8s live %-28s raw %-28s %s\n", it, paste(obs, collapse = "/"),
              paste(RAW23[[it]], collapse = "/"), if (m) "match" else "MISMATCH"))
}

cat("\n(b) 2021 block (id > 38966): responses per item\n")
# Raw ENCIG 2021 encig2021_01_sec1_A_3_4_5_8_9_10.csv (39930 rows; zip sha256
# 4463e585062961fa1bb200ec830a30d84f1d915f7a3fe4c8454d8198b516b62c), q5.11 = autopistas
RAW21 <- list(p5_11_1 = c(8970, 4996), p5_11_2 = c(8116, 5735), p5_11_3 = c(11540, 2283),
  p5_11_4 = c(12164, 1828), p5_11_5 = c(10649, 3229), p5_11a = c(1613, 8028, 2915, 736, 509, 223))
for (it in names(RAW21)) {
  x <- d$resp[d$item == it & d$wave == "2021"]
  obs <- if (it == "p5_11a") sapply(1:6, function(k) sum(x == k)) else c(sum(x == 0), sum(x == 1))
  m <- all(obs == RAW21[[it]]); ok <- ok && m
  cat(sprintf("  %-8s live %-28s raw2021 %-28s %s\n", it, paste(obs, collapse = "/"),
              paste(RAW21[[it]], collapse = "/"), if (m) "match" else "MISMATCH"))
}
n21 <- table(factor(d$item[d$wave == "2021"], levels = names(RAW23)))
n23 <- table(factor(d$item[d$wave == "2023"], levels = names(RAW23)))
for (it in names(RAW23))
  cat(sprintf("  %-8s 2021-wave n = %6d   2023-wave n = %4d   share from 2021 = %5.1f%%\n",
              it, n21[[it]], n23[[it]], 100 * n21[[it]] / (n21[[it]] + n23[[it]])))
b1 <- all(n21[paste0("p5_11_", 6:8)] == 0)
b2 <- all(n21[c(paste0("p5_11_", 1:5), "p5_11a")] > 10 * n23[c(paste0("p5_11_", 1:5), "p5_11a")])
cat(sprintf("\n  2021 wave absent from p5_11_6..8 (2021 q5.11 has 5 items): %s\n", b1))
cat(sprintf("  2021 wave > 10x the 2023 wave on p5_11_1..5 and p5_11a: %s\n", b2))
ok <- ok && b1 && b2

cat("\nNot established by this script: the question WORDING (that 2021 q5.11 is the\n",
    "toll-highway block and 2023 q5.11 the cable-car block) is read from the two INEGI\n",
    "questionnaires (encig21_cuestionario.pdf, encig23_cuestionario.pdf), not from data.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
