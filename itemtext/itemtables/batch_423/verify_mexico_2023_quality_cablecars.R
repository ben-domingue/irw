# verify_mexico_2023_quality_cablecars.R -- batch_423
#
# Claim: live item code p5_11_K is ENCIG 2023 microdata column P5_11_K (lowercased,
# no rename -- data/mexico_2023_quality.py keeps INEGI's names), which the 2023
# Cuestionario general prints as option K of question 5.11 (Cablebus/Mexicable
# cable car); p5_11a is 5.11a. Si/No stored 1->0, 2->1; 9 -> missing.
#
# What would break if item_text for two codes were swapped: the live per-item
# count vectors would no longer land on their namesake raw column. All nine
# raw vectors are distinct, so an exact cell-for-cell match pins every code to
# exactly one source column (route 9 + explicit code labels).
#
# Also checks the batch_422 block is gone: #2415/#2417 rebuilt the table 2023-only
# (the old .do had pooled 2021 q5.11 = toll highways under these codes).
#
# Raw counts below: INEGI encig23_base_datos_csv.zip ->
# encig2023_01_sec1_A_3_4_5_8_9_10.csv (38966 rows; zip sha256
# af733d867a568cbb0dadef4a5a793b02488a71728d1157860f14501f3d4c393d), fetched 2026-09-25.

suppressMessages(library(irw))
TABLE <- "mexico_2023_quality_cablecars"
RAW23 <- list(   # Si/No items: c(Si=1, No=2); p5_11a: codes 1..6
  p5_11_1 = c(622, 49), p5_11_2 = c(633, 34), p5_11_3 = c(646, 27),
  p5_11_4 = c(551, 120), p5_11_5 = c(614, 58), p5_11_6 = c(654, 19),
  p5_11_7 = c(643, 28), p5_11_8 = c(621, 16),
  p5_11a  = c(281, 356, 30, 4, 0, 2))

d <- irw::irw_fetch(TABLE)
ok <- TRUE

cat("(0) rebuild check: waves and ids\n")
yrs <- unique(d$cov_year)
cat(sprintf("  cov_year values: %s ; id range %d..%d ; distinct ids %d\n",
            paste(yrs, collapse = ","), min(d$id), max(d$id), length(unique(d$id))))
b0 <- identical(as.character(yrs), "2023") && max(d$id) <= 38966
cat(sprintf("  table is 2023-only (no 2021 toll-highway rows): %s\n\n", b0))
ok <- ok && b0

d <- d[!is.na(d$resp), ]
live <- lapply(names(RAW23), function(it) {
  x <- d$resp[d$item == it]
  if (it == "p5_11a") sapply(1:6, function(k) sum(x == k)) else c(sum(x == 0), sum(x == 1))
})
names(live) <- names(RAW23)

cat("(1) live code vs raw 2023 column: cell-for-cell, plus which raw columns each live vector matches\n")
for (it in names(RAW23)) {
  hits <- names(RAW23)[sapply(RAW23, function(r) length(r) == length(live[[it]]) && all(r == live[[it]]))]
  m <- identical(hits, it)
  ok <- ok && m
  cat(sprintf("  %-8s live %-22s raw %-22s matches raw column(s): %-10s %s\n", it,
              paste(live[[it]], collapse = "/"), paste(RAW23[[it]], collapse = "/"),
              paste(hits, collapse = ","), if (m) "unique namesake" else "FAIL"))
}
dist <- length(unique(sapply(RAW23, paste, collapse = "/"))) == length(RAW23)
cat(sprintf("  all %d raw count vectors distinct (so a permutation of codes cannot pass): %s\n",
            length(RAW23), dist))
ok <- ok && dist

cat("\n(2) resp direction: resp 0 carries the raw Si (code 1) count on every Si/No item,\n",
    "    e.g. p5_11_4 Si=551 -> resp0=", live$p5_11_4[1], ", No=120 -> resp1=", live$p5_11_4[2], "\n", sep = "")

cat("\nCorroboration read from the raw file, not re-fetched here: all 673 persons with any\n",
    "P5_11 Si/No answer have P5_1_10=1 (5.1 option 10 = Cablebus/Mexicable user), and\n",
    "P5_1_10 was asked only in CVE_ENT 09 (5077) and 15 (1414) -- the '[CDMX y EDO. MEX.]'\n",
    "gate printed in the questionnaire -- so the P5_11 block is the cable-car question.\n",
    "Not established by data: the code->text link itself rests on INEGI numbering\n",
    "(column P5_11_K = option K of 5.11 in encig23_cuestionario.pdf p.11); this script\n",
    "pins live code -> source column, and resp -> Si/No.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
