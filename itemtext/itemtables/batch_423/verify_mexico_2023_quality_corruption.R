# verify_mexico_2023_quality_corruption.R -- batch_423
#
# Claim: live item p8_1 / p8_2 / p8_3_1..3 is INEGI ENCIG variable P8_1 / P8_2 / P8_3_1..3
# (same names in the 2023 and 2021 files; data/mexico_2023_quality.py stacks them with
# cov_year, recodes 1 (Si) -> 0 and 2 (No) -> 1, sets 9 (No sabe / no responde) missing),
# and those variables are questions 8.1, 8.2 and options 1-3 of question 8.3 in the
# ENCIG 2023 and 2021 cuestionarios (explicit numbering).
#
# Route 9 (response-frequency matching), per wave: counts of 1/2/9 per variable from
# INEGI's own public microdata, hard-coded below --
#   2023: encig23_base_datos_csv.zip (sha256 af733d86...) -> encig2023_01_sec1_A_3_4_5_8_9_10.csv (38966 rows)
#   2021: encig21_base_datos_csv.zip (sha256 4463e585...) -> encig2021_01_sec1_A_3_4_5_8_9_10.csv (39930 rows)
# Prediction for live cov_year==Y, item k: resp0 = Si count, resp1 = No count, NA = code-9 count.
# Any swap of two items' codes breaks this because all five per-wave count vectors differ.
# Semantic check (route 8): Si share must fall 8.1 (belief/hearsay) > 8.2 (an acquaintance's
# experience) > each 8.3 option (own direct experience) in both waves.
# NOT established by the numbers: the variable -> questionnaire-question tie itself, which rests
# on the cuestionario numbering (8.1, 8.2, 8.3 options 1..3 = P8_1, P8_2, P8_3_1..3); nor order
# within the three 8.3 options beyond their distinct counts (their text tie is the numbering).
suppressMessages(library(irw))
TABLE <- "mexico_2023_quality_corruption"
ITEMS <- c("p8_1", "p8_2", "p8_3_1", "p8_3_2", "p8_3_3")
# columns: Si (1), No (2), No sabe/no responde (9)
SRC <- list(
  "2023" = rbind(p8_1 = c(21796, 16156, 1014), p8_2 = c(15685, 22777, 504),
                 p8_3_1 = c(2872, 35966, 128), p8_3_2 = c(1227, 37613, 126), p8_3_3 = c(1746, 37093, 127)),
  "2021" = rbind(p8_1 = c(22263, 16473, 1194), p8_2 = c(15067, 24136, 727),
                 p8_3_1 = c(2595, 37168, 167), p8_3_2 = c(1005, 38764, 161), p8_3_3 = c(1485, 38292, 153)))
d <- irw::irw_fetch(TABLE)
fail <- FALSE
for (y in names(SRC)) {
  cat(sprintf("\n== cov_year %s ==\n%-8s %-24s %-24s %s\n", y, "item", "source Si/No/NS", "live 0/1/NA", "abs diff"))
  dy <- d[as.character(d$cov_year) == y, ]
  for (it in ITEMS) {
    r <- dy$resp[dy$item == it]
    live <- c(sum(r == 0, na.rm = TRUE), sum(r == 1, na.rm = TRUE), sum(is.na(r)))
    dd <- sum(abs(live - SRC[[y]][it, ]))
    if (dd != 0) fail <- TRUE
    cat(sprintf("%-8s %-24s %-24s %d\n", it, paste(SRC[[y]][it, ], collapse = "/"), paste(live, collapse = "/"), dd))
  }
  nd <- nrow(unique(SRC[[y]])); cat(sprintf("distinct source count vectors: %d of 5\n", nd))
  if (nd != 5) fail <- TRUE
  si <- SRC[[y]][, 1] / (SRC[[y]][, 1] + SRC[[y]][, 2])
  cat("Si share:", paste(sprintf("%s=%.3f", ITEMS, si), collapse = "  "), "\n")
  if (!(si["p8_1"] > si["p8_2"] && si["p8_2"] > max(si[3:5]))) fail <- TRUE
}
cat("\nNot established: the P8_* -> question 8.1/8.2/8.3.k tie, which is the cuestionario's own numbering.\n")
cat(if (!fail) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
