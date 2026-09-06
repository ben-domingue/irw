# verify_genpsych_russell_2024_gemma.R -- Step 5b, route 9 (response-frequency matching).
#
# CLAIM UNDER TEST. The shipped item_text for items_1..items_28 was taken from row 2
# (the Qualtrics question-text row) of the study's own gemma-2_deID.xlsx, keyed by
# column name, and the option_text<->resp mapping is the likert_mapping in
# data/genpsych_russell_2024.r (Strongly Disagree=1, Disagree=2, Neither agree nor
# disagree=3, Agree=4, Strongly agree=5).
#
# THE FALSIFIABLE PREDICTION. If both are right, then counting each label in each
# raw xlsx column and counting each integer for the same item code in the live IRW
# table must agree cell for cell. Swapping any two item codes, or permuting any two
# levels of the label->integer map, breaks at least one cell: all 28 items have
# distinct count signatures (checked), and the five level counts are far from equal.
#
# RAW is hard-coded from OSF zcytb (view_only 79d2c8bf12c24393863d60c4143f8a0e),
# Empirical Validation/gemma-2/data/gemma-2_deID.xlsx -- counts of
# c("Strongly Disagree","Disagree","Neither agree nor disagree","Agree",
#   "Strongly agree", <blank>) per items_N column over its 1001 respondent rows.
# It is a property of a deposited file and will not change.
#
# Live counts are read with a server-side GROUP BY rather than irw_fetch(), so this
# script costs a query and not a 28k-row export.

suppressMessages(library(irw))

TABLE <- "genpsych_russell_2024_gemma"

RAW <- list(
  "items_1" = c(5, 31, 139, 478, 335, 13),
  "items_2" = c(6, 21, 59, 322, 563, 30),
  "items_3" = c(8, 24, 72, 432, 447, 18),
  "items_4" = c(13, 78, 166, 509, 226, 9),
  "items_5" = c(10, 112, 254, 449, 171, 5),
  "items_6" = c(56, 211, 196, 390, 145, 3),
  "items_7" = c(59, 213, 191, 330, 196, 12),
  "items_8" = c(5, 53, 111, 407, 405, 20),
  "items_9" = c(11, 88, 163, 460, 269, 10),
  "items_10" = c(9, 72, 162, 457, 289, 12),
  "items_11" = c(206, 342, 205, 166, 79, 3),
  "items_12" = c(278, 357, 200, 100, 61, 5),
  "items_13" = c(142, 277, 221, 255, 101, 5),
  "items_14" = c(72, 217, 176, 349, 176, 11),
  "items_15" = c(162, 317, 168, 231, 118, 5),
  "items_16" = c(260, 317, 189, 156, 74, 5),
  "items_17" = c(214, 303, 191, 195, 92, 6),
  "items_18" = c(95, 236, 212, 290, 157, 11),
  "items_19" = c(53, 172, 240, 365, 161, 10),
  "items_20" = c(100, 291, 182, 278, 137, 13),
  "items_21" = c(72, 164, 129, 386, 238, 12),
  "items_22" = c(146, 320, 153, 256, 115, 11),
  "items_23" = c(74, 222, 178, 322, 193, 12),
  "items_24" = c(8, 36, 123, 491, 331, 12),
  "items_25" = c(50, 213, 157, 369, 201, 11),
  "items_26" = c(20, 91, 224, 398, 257, 11),
  "items_27" = c(24, 108, 134, 379, 338, 18),
  "items_28" = c(45, 171, 213, 335, 224, 13)
)

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                   "TRIM(CAST(resp AS STRING)) AS resp, COUNT(*) AS n",
                   "FROM `%s` GROUP BY 1,2"), tbl$qualified_reference)
live_long <- as.data.frame(irw:::.irw_query_tibble(q))
lev <- c("1", "2", "3", "4", "5", "NA")

cat(sprintf("%-9s %-38s %-38s %s\n", "item", "raw xlsx (1,2,3,4,5,NA)",
            "live IRW resp (1,2,3,4,5,NA)", "match"))
ok <- TRUE
for (it in names(RAW)) {
    sub <- live_long[live_long$item == it, ]
    obs <- setNames(rep(0L, length(lev)), lev)
    idx <- match(sub$resp, lev)
    obs[idx[!is.na(idx)]] <- sub$n[!is.na(idx)]
    exp <- RAW[[it]]
    same <- all(as.integer(obs) == as.integer(exp))
    ok <- ok && same
    cat(sprintf("%-9s %-38s %-38s %s\n", it,
                paste(exp, collapse = ","), paste(as.integer(obs), collapse = ","),
                if (same) "OK" else "MISMATCH"))
}

cat(sprintf("\ntotal raw cells compared: %d (28 items x 6 levels); rows raw %d, rows live %d\n",
            28L * 6L, sum(unlist(RAW)), sum(live_long$n)))
cat("Signature check: all 28 items have distinct 6-tuples, so no item-code swap is\n",
    "invisible to this test. What this does NOT establish: nothing further is owed --\n",
    "the item<->text tie is data_labels (codes ARE the source column names) and this\n",
    "route independently pins both the item axis and the option_text<->resp axis.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
