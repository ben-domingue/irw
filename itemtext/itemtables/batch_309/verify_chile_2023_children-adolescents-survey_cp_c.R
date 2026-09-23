# verify_chile_2023_children-adolescents-survey_cp_c.R
#
# WHAT IS BEING VERIFIED
# ----------------------
# Every shipped item_text / option_text in
# chile_2023_children-adolescents-survey_cp_c__items.csv is keyed to a Stata
# variable name (cp2_1 ... cp9_4) of the EANNA 2023 deposit, and
# data/chile_2023_children-adolescents-survey.do carries that name straight
# through (`gen item = "`var'"`), so `item` IS the source column name.
# The codebook -- "Libro de codigos base de datos EANNA 2023", sheet
# "2. Cuidador(a) Principal" -- ties each variable name to its label and prints
# a frequency for every value. That makes the tie falsifiable (route 9): if the
# text of cp5_5 and cp5_6 had been swapped, the shipped text would sit against
# the wrong frequency profile.
#
# Three checks, all against numbers published in (or derived from) the deposit:
#  A. 94 categorical item x value cells (cp2_*, cp3, cp4, cp5_*, cp6_*, cp8_*):
#     codebook frequency vs live count. Negative codes (-88/-99/-98) excluded:
#     the do-file mvdecodes them, so they cannot be in the live table.
#  B. cp9_*: the codebook's "88:88 = No sabe" frequencies (52/64/85/101) vs
#     the live count of resp == 89.5 (88:88 -> 88 + 88/60 = 89.47 -> 89.5 by the
#     do-file's hh:mm conversion). Also confirms the shipped option_text for
#     89.5 is "No sabe".
#  C. cp7_*/cp9_*: per-item mean of the live table vs the mean obtained by
#     applying the do-file's hh:mm -> decimal-hours conversion to the deposit's
#     own .dta (Base de datos EANNA 2023.dta, rp2 == 1), computed 2026-09-23.
#     This is what separates cp7_1 from cp7_2, whose codebook ranges are both
#     00:00-45:00.
# Live counts come from a server-side GROUP BY (redivis query), not irw_fetch():
# the table is 741,678 rows.

suppressMessages(library(irw))
TABLE <- "chile_2023_children-adolescents-survey_cp_c"

CB <- data.frame(matrix(c(
  "cp2_1", 1, 3525,
  "cp2_1", 0, 5268,
  "cp2_2", 1, 3502,
  "cp2_2", 0, 5291,
  "cp2_3", 1, 3508,
  "cp2_3", 0, 5285,
  "cp2_4", 1, 3506,
  "cp2_4", 0, 5287,
  "cp2_5", 1, 3573,
  "cp2_5", 0, 5220,
  "cp2_6", 1, 3498,
  "cp2_6", 0, 5295,
  "cp2_7", 1, 3493,
  "cp2_7", 0, 5300,
  "cp2_8", 1, 3521,
  "cp2_8", 0, 5272,
  "cp2_9", 1, 3504,
  "cp2_9", 0, 5289,
  "cp2_10", 1, 191,
  "cp2_10", 0, 8602,
  "cp2_77", 1, 131,
  "cp2_77", 0, 8662,
  "cp3", 1, 8108,
  "cp3", 2, 673,
  "cp4", 1, 8286,
  "cp4", 2, 9157,
  "cp5_1", 1, 409,
  "cp5_1", 2, 4585,
  "cp5_1", 3, 11277,
  "cp5_1", 4, 939,
  "cp5_2", 1, 205,
  "cp5_2", 2, 2661,
  "cp5_2", 3, 12386,
  "cp5_2", 4, 2076,
  "cp5_3", 1, 185,
  "cp5_3", 2, 2313,
  "cp5_3", 3, 12454,
  "cp5_3", 4, 2373,
  "cp5_4", 1, 206,
  "cp5_4", 2, 2670,
  "cp5_4", 3, 12761,
  "cp5_4", 4, 1659,
  "cp5_5", 1, 942,
  "cp5_5", 2, 8917,
  "cp5_5", 3, 6506,
  "cp5_5", 4, 496,
  "cp5_6", 1, 602,
  "cp5_6", 2, 8279,
  "cp5_6", 3, 7772,
  "cp5_6", 4, 393,
  "cp5_7", 1, 465,
  "cp5_7", 2, 7403,
  "cp5_7", 3, 8084,
  "cp5_7", 4, 333,
  "cp6_1", 1, 12509,
  "cp6_1", 2, 4993,
  "cp6_2", 1, 13470,
  "cp6_2", 2, 4032,
  "cp6_3", 1, 13812,
  "cp6_3", 2, 3690,
  "cp6_4", 1, 14247,
  "cp6_4", 2, 3255,
  "cp6_5", 1, 10911,
  "cp6_5", 2, 6591,
  "cp6_6", 1, 13356,
  "cp6_6", 2, 4146,
  "cp6_7", 1, 14859,
  "cp6_7", 2, 2643,
  "cp6_8", 1, 14048,
  "cp6_8", 2, 3454,
  "cp8_1", 1, 1187,
  "cp8_1", 2, 6895,
  "cp8_1", 3, 8751,
  "cp8_1", 4, 351,
  "cp8_2", 1, 655,
  "cp8_2", 2, 4900,
  "cp8_2", 3, 11270,
  "cp8_2", 4, 551,
  "cp8_3", 1, 523,
  "cp8_3", 2, 4279,
  "cp8_3", 3, 12181,
  "cp8_3", 4, 388,
  "cp8_4", 1, 832,
  "cp8_4", 2, 6272,
  "cp8_4", 3, 9859,
  "cp8_4", 4, 310,
  "cp8_5", 1, 3024,
  "cp8_5", 2, 11341,
  "cp8_5", 3, 2934,
  "cp8_5", 4, 59,
  "cp8_6", 1, 3539,
  "cp8_6", 2, 12097,
  "cp8_6", 3, 1712,
  "cp8_6", 4, 57
), ncol = 3, byrow = TRUE), stringsAsFactors = FALSE)
names(CB) <- c("item", "resp", "cb_n")
CB$resp <- as.numeric(CB$resp); CB$cb_n <- as.integer(CB$cb_n)

NOSABE <- c(cp9_1 = 52L, cp9_2 = 64L, cp9_3 = 85L, cp9_4 = 101L)
DTA_MEAN <- c(cp7_1 = 11.7493, cp7_2 = 1.9054, cp7_3 = 0.1387, cp7_4 = 0.0224,
              cp9_1 = 1.9228,  cp9_2 = 1.5586, cp9_3 = 1.0442, cp9_4 = 0.7551)
MEAN_TOL <- 0.005   # Stata float rounding moves a handful of values by 0.1

here <- tryCatch({
    a <- commandArgs(trailingOnly = FALSE)
    f <- sub("^--file=", "", a[grep("^--file=", a)])
    if (length(f)) dirname(normalizePath(f[1])) else "."
}, error = function(e) ".")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
shipped <- if (file.exists(items_csv)) read.csv(items_csv, stringsAsFactors = FALSE) else NULL

ref <- irw::irw_table_sets(TABLE, source = "core")$table
q <- function(sql) as.data.frame(redivis::query(sql)$to_data_frame())
live <- q(sprintf("SELECT item, resp, COUNT(*) AS n FROM `%s` WHERE resp IS NOT NULL GROUP BY item, resp", ref))
live$resp <- as.numeric(live$resp); live$n <- as.integer(live$n)
means <- q(sprintf("SELECT item, AVG(resp) AS m, COUNT(resp) AS n FROM `%s` WHERE item LIKE 'cp7_%%' OR item LIKE 'cp9_%%' GROUP BY item", ref))

ok <- TRUE
cat("== A. categorical cells: codebook frequency vs live count ==\n")
m <- merge(CB, live[!grepl("^cp[79]_", live$item), ], by = c("item", "resp"), all = TRUE)
m <- m[order(m$item, m$resp), ]
m$diff <- m$n - m$cb_n
cat(sprintf("%-7s %4s %8s %8s %5s  %s\n", "item", "resp", "codebk", "live", "diff", "shipped option_text / item_text"))
for (i in seq_len(nrow(m))) {
    lab <- ""
    if (!is.null(shipped)) {
        k <- which(shipped$item == m$item[i] & shipped$resp == m$resp[i])
        if (length(k)) lab <- paste(shipped$option_text[k[1]], "/", substr(shipped$item_text[k[1]], 1, 45))
    }
    cat(sprintf("%-7s %4g %8s %8s %5s  %s\n", m$item[i], m$resp[i],
        ifelse(is.na(m$cb_n[i]), "-", m$cb_n[i]), ifelse(is.na(m$n[i]), "-", m$n[i]),
        ifelse(is.na(m$diff[i]), "?", m$diff[i]), lab))
}
exact <- sum(!is.na(m$diff) & m$diff == 0)
cat(sprintf("cells: %d | exact: %d\n", nrow(m), exact))
if (exact != nrow(m) || nrow(m) != 94) ok <- FALSE
prof <- tapply(seq_len(nrow(m)), m$item, function(ix) paste(m$resp[ix], m$n[ix], collapse = ";"))
cat(sprintf("distinct frequency profiles: %d of %d items\n", length(unique(prof)), length(prof)))
if (length(unique(prof)) != length(prof)) ok <- FALSE

cat("\n== B. cp9_*: codebook '88:88 No sabe' vs live resp == 89.5 ==\n")
for (it in names(NOSABE)) {
    n <- live$n[live$item == it & abs(live$resp - 89.5) < 1e-6]; n <- if (length(n)) n else 0L
    lab <- if (!is.null(shipped)) shipped$option_text[shipped$item == it & abs(shipped$resp - 89.5) < 1e-6][1] else NA
    cat(sprintf("%-6s codebook %4d  live %4d  shipped option_text '%s'\n", it, NOSABE[it], n, lab))
    if (n != NOSABE[it]) ok <- FALSE
    if (!is.null(shipped) && !identical(lab, "No sabe")) ok <- FALSE
}

cat("\n== C. cp7_*/cp9_*: mean from deposit .dta (do-file conversion) vs live ==\n")
for (it in names(DTA_MEAN)) {
    lm <- means$m[means$item == it]
    txt <- if (!is.null(shipped)) shipped$item_text[shipped$item == it][1] else ""
    cat(sprintf("%-6s dta %8.4f  live %8.4f  diff %7.4f  n %s  %s\n", it, DTA_MEAN[it], lm, lm - DTA_MEAN[it],
                means$n[means$item == it], txt))
    if (!length(lm) || abs(lm - DTA_MEAN[it]) > MEAN_TOL) ok <- FALSE
}
cat("Note: C reproduces means, it does not check wording; the item_text for cp7_k / cp9_k is the\n",
    "questionnaire's age-group label, tied to the name by the .dta variable label.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
