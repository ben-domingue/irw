# verify_mexico_2023_quality_generalcorruption.R -- batch_424
#
# Claim: live item p9_1 / p9_7 is INEGI ENCIG variable P9_1 / P9_7 (same names in the 2023 and
# 2021 files; both in ASKED_2021, absent from RENAME_2021 in data/mexico_2023_quality.py, which
# stacks the waves with cov_year, recodes 1 (Si) -> 0 and 2 (No) -> 1, leaves 3 (No aplica) as 3,
# and sets 9 (No sabe / no responde) missing), and those variables are questions 9.1 and 9.7 of
# Seccion IX (Corrupcion general) in the ENCIG 2023 and 2021 cuestionarios (explicit numbering).
#
# Route 9 (response-frequency matching), per wave: counts of 1/2/3/9 per variable, and the full
# P9_1 x P9_7 joint table, from INEGI's own public microdata, hard-coded below --
#   2023: encig23_base_datos_csv.zip (sha256 af733d86...) -> encig2023_01_sec1_A_3_4_5_8_9_10.csv (38966 rows)
#   2021: encig21_base_datos_csv.zip (sha256 4463e585...) -> encig2021_01_sec1_A_3_4_5_8_9_10.csv (39930 rows)
# Prediction for live cov_year==Y: item k resp 0/1/3/NA = source code 1/2/3/9 counts; and the
# per-person joint table of (p9_1, p9_7) equals the source P9_1 x P9_7 crosstab.
# A swap of the two codes breaks this (only P9_7 has code 3; the Si/No counts differ ~10x),
# as does a flipped Si/No direction or a mis-stacked 2021 wave.
# Structural check: 9.1 has no 'No aplica' option in the cuestionario, so live p9_1 must have no
# resp 3; 9.7 does, and it must be the modal answer among 9.1 = No respondents (nothing to report).
# NOT established by the numbers: the variable -> questionnaire-question tie itself, which rests on
# the cuestionario numbering (9.1, 9.7 = P9_1, P9_7).
suppressMessages(library(irw))
TABLE <- "mexico_2023_quality_generalcorruption"
# columns: code 1 (Si), 2 (No), 3 (No aplica), 9 (No sabe / no responde)
SRC <- list(
  "2023" = rbind(p9_1 = c(4044, 34672, 0, 250), p9_7 = c(348, 7252, 31092, 274)),
  "2021" = rbind(p9_1 = c(3366, 35765, 0, 799), p9_7 = c(321, 10189, 28724, 696)))
# joint P9_1 (rows 1,2,9) x P9_7 (cols 1,2,3,9)
JOINT <- list(
  "2023" = rbind(c(221, 3325, 496, 2), c(126, 3906, 30414, 226), c(1, 21, 182, 46)),
  "2021" = rbind(c(197, 2933, 232, 4), c(121, 7116, 27974, 554), c(3, 140, 518, 138)))
d <- irw::irw_fetch(TABLE)
fail <- FALSE
lv <- function(r) factor(ifelse(is.na(r), "NA", as.character(r)), levels = c("0", "1", "3", "NA"))
for (y in names(SRC)) {
  cat(sprintf("\n== cov_year %s ==\n%-6s %-26s %-26s %s\n", y, "item", "source 1/2/3/9", "live 0/1/3/NA", "abs diff"))
  dy <- d[as.character(d$cov_year) == y, ]
  for (it in rownames(SRC[[y]])) {
    live <- as.vector(table(lv(dy$resp[dy$item == it])))
    dd <- sum(abs(live - SRC[[y]][it, ]))
    if (dd != 0) fail <- TRUE
    cat(sprintf("%-6s %-26s %-26s %d\n", it, paste(SRC[[y]][it, ], collapse = "/"), paste(live, collapse = "/"), dd))
  }
  a <- dy[dy$item == "p9_1", c("id", "resp")]; b <- dy[dy$item == "p9_7", c("id", "resp")]
  m <- merge(a, b, by = "id", suffixes = c("_91", "_97"))
  jt <- table(factor(ifelse(is.na(m$resp_91), "NA", m$resp_91), levels = c("0", "1", "NA")), lv(m$resp_97))
  jd <- sum(abs(unclass(jt) - JOINT[[y]]))
  cat(sprintf("joint p9_1 x p9_7 (12 cells): source vs live abs diff = %d (persons merged: %d)\n", jd, nrow(m)))
  print(jt)
  if (jd != 0) fail <- TRUE
  if (SRC[[y]]["p9_1", 3] != 0 || sum(dy$resp[dy$item == "p9_1"] == 3, na.rm = TRUE) != 0) fail <- TRUE
  if (which.max(jt["1", 1:3]) != 3) fail <- TRUE   # among 9.1 = No, 'No aplica' is modal for 9.7
}
cat("\nNot established: the P9_1/P9_7 -> question 9.1/9.7 tie, which is the cuestionario's own numbering.\n")
cat(if (!fail) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
