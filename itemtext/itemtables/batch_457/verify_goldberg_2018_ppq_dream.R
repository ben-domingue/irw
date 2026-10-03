# verify_goldberg_2018_ppq_dream.R -- batch_457
#
# item<->item_text needs no check: the live codes dream1..dream6 ARE the PPQ .sav
# column names and item_text is each column's own SPSS variable label (data_labels).
# What carried inference is option_text<->resp: the .sav has NO value labels and the
# form (PPQ_FINAL.pdf p.7) prints unnumbered bubbles, so resp = k was assigned to the
# k-th printed option. Two things could be wrong and this script tests both:
#   (1) the option COUNT per item: dream1 prints 7 bubbles, dream5 prints 4, the rest 5.
#   (2) the ORDER, especially dream5, printed as a 2x2 grid:
#         No, they just morph...        Often they tell a coherent story.
#         Sometimes they tell a...      Almost always they tell a story.
#       We ship column-major order (No=1, Sometimes=2, Often=3, Almost always=4).
#       Row-major would make 2=Often, 3=Sometimes. If ours is right, dream-recall
#       frequency (dream2, dream3) and enjoyment (dream6) rise monotonically over
#       dream5 = 1..4; under row-major, level 2 would sit ABOVE level 3.
#   Direction of the 1-7 sleep-hours item: mode must be at 3/4 (Seven/Eight hours);
#   reversed it would sit at Nine/Ten-or-eleven, implausible in a community sample.
suppressMessages(library(irw))
TABLE <- "goldberg_2018_ppq_dream"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
ok <- TRUE

printed <- c(dream1 = 7, dream2 = 5, dream3 = 5, dream4 = 5, dream5 = 4, dream6 = 5)
cat("Per-item live max resp vs printed option count:\n")
for (it in names(printed)) {
  mx <- max(w[[it]], na.rm = TRUE)
  cat(sprintf("  %-7s live max %d  printed %d\n", it, mx, printed[[it]]))
  if (mx != printed[[it]]) ok <- FALSE
}

cat("\ndream5 level: 1 No/morph, 2 Sometimes, 3 Often, 4 Almost always (shipped order)\n")
for (y in c("dream2", "dream3", "dream6")) {
  m <- tapply(w[[y]], w$dream5, mean, na.rm = TRUE)
  cat(sprintf("  mean %s by dream5: %s  strictly increasing: %s\n", y,
              paste(sprintf("%.2f", m), collapse = " / "), all(diff(m) > 0)))
  if (!all(diff(m) > 0)) ok <- FALSE
}

tab1 <- table(w$dream1)
cat("\ndream1 (sleep hours) counts by resp:", paste(names(tab1), tab1, sep = "=", collapse = " "), "\n")
mode1 <- as.integer(names(tab1)[which.max(tab1)])
cat("  mode at resp", mode1, "(3=Seven, 4=Eight expected)\n")
if (!mode1 %in% 3:4) ok <- FALSE

r23 <- cor(w$dream2, w$dream3, use = "pair")
cat(sprintf("\ncor(dream2 dream-frequency, dream3 recall) = %.2f (same direction expected > 0)\n", r23))
if (r23 <= 0) ok <- FALSE

cat("\nNOT established: the scanner's own bubble->integer key (never published); the\n",
    "5-option frequency items are pinned only by printed left-to-right order and the\n",
    "positive inter-item correlations, which a whole-scale reversal of all of them\n",
    "together would also satisfy.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
