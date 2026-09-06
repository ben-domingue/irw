# verify_gabriel_2026_media_use.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST (both mapping axes at once):
#   item axis  : media_1..media_6 correspond to the six media channels named in
#                the S2 Dataset codebook (Q24_SQ001..SQ006), i.e.
#                media_1 = Daily newspapers, media_2 = Weekly or trade magazines,
#                media_3 = Radio and television, media_4 = Online sources,
#                media_5 = Social media, media_6 = Producer/retailer websites.
#   resp axis  : resp 1..5 = Regelmaessig / Haeufig / Gelegentlich / Selten / Nie
#                (Regularly / Frequently / Occasionally / Rarely / Never).
#
# FALSIFIABLE PREDICTION: Gabriel & Bitsch (2026) PLOS ONE 10.1371/journal.pone.0341457
# Fig 6 publishes, for each NAMED channel, the % of respondents in each NAMED
# anchor. If either axis were permuted, the live per-item x resp percentage
# profile would land on the wrong published row (or the wrong column order).
# All six published profiles are mutually distinct, so a match pins every item
# against every other item AND fixes the anchor order.
#
# Published values are read off Fig 6 (rounded to whole %). Blank segments in the
# figure (bars too narrow to carry a label) are given as NA and skipped.

suppressMessages(library(irw))

TABLE <- "gabriel_2026_media_use"
TOL   <- 0.75   # figure is printed to whole percent

# Fig 6 rows, in the figure's own order, columns = Regularly, Frequently,
# Occasionally, Rarely, Never  (i.e. resp 1..5 under the claimed mapping).
PUB <- rbind(
  "Radio and television"                                   = c(18, 17, 28, 19, 18),
  "Daily newspaper"                                        = c(12,  8, 18, 21, 40),
  "Internet sources (e.g. blogs, forums, podcasts)"        = c(10, 16, 24, 20, 30),
  "Social media such as Facebook or X"                     = c( 9, 11, 18, 20, 43),
  "Websites/newsletters from producers and food retailers" = c(NA,  8, 22, 24, 42),
  "Weekly and trade journals"                              = c(NA,  6, 17, 24, 51)
)

# The mapping this table ships, figure row -> item code.
CLAIM <- c("Radio and television"                                   = "media_3",
           "Daily newspaper"                                        = "media_1",
           "Internet sources (e.g. blogs, forums, podcasts)"        = "media_4",
           "Social media such as Facebook or X"                     = "media_5",
           "Websites/newsletters from producers and food retailers" = "media_6",
           "Weekly and trade journals"                              = "media_2")

d <- irw::irw_fetch(TABLE)
tt  <- table(factor(d$item, levels = paste0("media_", 1:6)),
             factor(d$resp, levels = 1:5))
pct <- round(100 * prop.table(tt, 1), 1)

cat("Live per-item response distribution (% of that item's responses)\n")
cat(sprintf("%-8s %7s %7s %7s %7s %7s\n", "item", "r=1", "r=2", "r=3", "r=4", "r=5"))
for (it in rownames(pct))
  cat(sprintf("%-8s %7.1f %7.1f %7.1f %7.1f %7.1f\n", it, pct[it,1], pct[it,2],
              pct[it,3], pct[it,4], pct[it,5]))

cat("\nPublished (Fig 6) vs live, under the shipped mapping\n")
ok <- TRUE
for (fig in rownames(PUB)) {
  it <- CLAIM[[fig]]
  p <- PUB[fig, ]; o <- as.numeric(pct[it, ])
  dif <- abs(p - o)
  bad <- any(dif > TOL, na.rm = TRUE)
  if (bad) ok <- FALSE
  cat(sprintf("  %-55s -> %-8s pub[%s] live[%s] maxdiff=%.1f %s\n",
              substr(fig, 1, 55), it,
              paste(ifelse(is.na(p), " -", sprintf("%2d", p)), collapse = ","),
              paste(sprintf("%4.1f", o), collapse = ","),
              max(dif, na.rm = TRUE), if (bad) "MISMATCH" else "ok"))
}

# Discriminance: confirm no OTHER item would also fit each published row, so the
# match identifies each item uniquely rather than merely being consistent.
cat("\nUniqueness check -- best-fitting item for each published row\n")
uniq <- TRUE
for (fig in rownames(PUB)) {
  p <- PUB[fig, ]
  err <- sapply(rownames(pct), function(it) max(abs(p - as.numeric(pct[it, ])), na.rm = TRUE))
  best <- names(which.min(err))
  second <- sort(err)[2]
  cat(sprintf("  %-55s best=%s (err %.1f), runner-up err %.1f\n",
              substr(fig, 1, 55), best, min(err), second))
  if (best != CLAIM[[fig]] || second <= TOL) uniq <- FALSE
}

cat("\n")
cat("item axis matches published Fig 6 within", TOL, "pp:", ok, "\n")
cat("each published row identifies exactly one item:", uniq, "\n")
cat("resp axis: fixed independently by the S2 Dataset's own German value labels\n")
cat("  (Data_label vs Data_Code crosstab, 1=Regelmaessig 2=Haeufig 3=Gelegentlich\n")
cat("   4=Selten 5=Nie, exact cell-for-cell); the ascending Fig 6 column order\n")
cat("   Regularly..Never above is the same order and corroborates it.\n")

if (ok && uniq) cat("VERDICT: PASS\n") else cat("VERDICT: FAIL\n")
