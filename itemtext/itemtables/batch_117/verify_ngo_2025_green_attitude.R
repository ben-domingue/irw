# verify_ngo_2025_green_attitude.R
#
# Claim under test: the four unnumbered statements printed under the heading
# "Green attitude" in the S2 File questionnaire of Ngo & Nguyen (2025), PLOS ONE
# 20(5):e0323879, correspond IN PRESENTATION ORDER to the deposit columns
# G_ATT_1..G_ATT_4, which data/ngo_2025_green_purchasing.py melts unchanged into
# the IRW item codes.
#
# The questionnaire prints no item numbers and no codes, so the tie between text
# and code is an ORDER inference (mapping_basis = paper_order). What can be
# checked with numbers is (B) that the IRW code really is the deposit column
# name, (C) that those columns are the ones the paper's own measurement model
# describes, and (D) that the deposit's column order tracks the questionnaire's
# presentation order at every boundary where the two can be compared. What
# CANNOT be checked is the order WITHIN the four-item attitude block: no
# published per-item statistic separates them, so any permutation of the four
# statements would survive every test below. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "ngo_2025_green_attitude"
ITEMS <- paste0("G_ATT_", 1:4)

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
d$id   <- as.integer(as.character(d$id))

cat("=== A. Per-item descriptives from the live IRW table ===\n")
cat(sprintf("%-9s %5s %7s %7s %5s %5s\n", "item", "n", "mean", "sd", "min", "max"))
for (it in ITEMS) {
  z <- d$resp[d$item == it]
  cat(sprintf("%-9s %5d %7.3f %7.3f %5d %5d\n", it, sum(!is.na(z)),
              mean(z, na.rm = TRUE), sd(z, na.rm = TRUE),
              min(z, na.rm = TRUE), max(z, na.rm = TRUE)))
}

cat("\n=== B. Live table vs the deposit's own columns, cell for cell ===\n")
url <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0323879.s001")
f <- file.path(tempdir(), "pone.0323879.s001.csv")
if (!file.exists(f)) download.file(url, f, quiet = TRUE, mode = "wb")
raw <- read.csv(f, check.names = FALSE, fileEncoding = "UTF-8-BOM")

wide <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
                direction = "wide")
names(wide) <- sub("^resp\\.", "", names(wide))
wide <- wide[order(wide$id), ]
raw  <- raw[order(raw$No), ]
cat(sprintf("live ids %d, deposit rows %d, ids == deposit 'No': %s\n",
            nrow(wide), nrow(raw), identical(wide$id, as.integer(raw$No))))
mism <- sapply(ITEMS, function(it) {
  a <- as.numeric(wide[[it]]); b <- as.numeric(raw[[it]])
  sum(is.na(a) != is.na(b)) + sum(a != b, na.rm = TRUE)
})
for (it in ITEMS) cat(sprintf("  %-9s mismatching cells vs deposit column of the same name: %d\n",
                              it, mism[[it]]))
okB <- identical(wide$id, as.integer(raw$No)) && sum(mism) == 0
cat("B:", if (okB) "the IRW item code IS the deposit column name -- MATCH\n" else "MISMATCH\n")

cat("\n=== C. Paper Table 2 outer loadings vs item-construct correlations ===\n")
PUB <- c(G_ATT_1 = 0.871, G_ATT_2 = 0.836, G_ATT_3 = 0.845, G_ATT_4 = 0.845)
tot <- rowSums(sapply(ITEMS, function(it) as.numeric(wide[[it]])))
obs <- sapply(ITEMS, function(it) cor(as.numeric(wide[[it]]), tot))
cat(sprintf("%-9s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (it in ITEMS)
  cat(sprintf("%-9s %10.3f %10.3f %8.3f\n", it, PUB[[it]], obs[[it]], obs[[it]] - PUB[[it]]))
worst <- max(abs(obs - PUB))
cat(sprintf("largest deviation: %.3f (tolerance 0.03)\n", worst))
cat("  NOTE: published loadings tie at 0.845 for G_ATT_3 and G_ATT_4, so this\n",
    "  route could not separate those two even if it were about wording.\n", sep = "")
okC <- worst <= 0.03

cat("\n=== D. Questionnaire presentation order vs deposit column order ===\n")
# S2 File block order, read off the questionnaire (pone.0323879.s002.docx):
#   Green attitude, Green subjective norm, Green perceived behavioral control,
#   Green purchasing intention, Green purchasing behavior, then the demographic
#   questions gender, age, education, marital status.
S2_ORDER <- c("G_ATT", "G_SN", "G_PBC", "G_PI", "G_PB",
              "Gender", "Age", "Education", "Martial_status")
hdr <- names(raw)
first_pos <- sapply(S2_ORDER, function(p) {
  hits <- if (p %in% hdr) which(hdr == p) else grep(paste0("^", p, "_[0-9]+$"), hdr)
  if (length(hits)) min(hits) else NA_integer_
})
cat(sprintf("%-16s %s\n", "S2 block", "first column position in S1 header"))
for (p in S2_ORDER) cat(sprintf("%-16s %s\n", p, first_pos[[p]]))
okD <- !any(is.na(first_pos)) && !is.unsorted(first_pos, strictly = TRUE)
cat(sprintf("D: %d/%d blocks located, deposit order %s questionnaire order\n",
            sum(!is.na(first_pos)), length(S2_ORDER),
            if (okD) "== (strictly increasing) --  MATCH" else "!= -- MISMATCH"))

cat("\n=== E. Semantic reading of the item means (not a pass criterion) ===\n")
mns <- sapply(ITEMS, function(it) mean(d$resp[d$item == it], na.rm = TRUE))
cat(sprintf("  G_ATT_1 'satisfy my values'      %.2f\n", mns[["G_ATT_1"]]))
cat(sprintf("  G_ATT_2 'environment friendly'   %.2f\n", mns[["G_ATT_2"]]))
cat(sprintf("  G_ATT_3 'products are competitive' %.2f\n", mns[["G_ATT_3"]]))
cat(sprintf("  G_ATT_4 'exciting for me to buy'  %.2f\n", mns[["G_ATT_4"]]))
cat("  The means split into two flat pairs (1,3 ~2.7; 2,4 ~3.7), which is\n",
    "  consistent with the least-endorsed item being the market-belief statement\n",
    "  ('competitive') and the most-endorsed being 'environment friendly', but it\n",
    "  does not distinguish 1 from 3 or 2 from 4.\n", sep = "")

cat("\nWhat this does NOT establish: the order of the four statements within the\n",
    "attitude block. The questionnaire numbers nothing, the paper publishes no\n",
    "per-item mean/SD, and its two distinguishable loadings do not attach to any\n",
    "wording. Nothing here would break if the four item_text values were permuted.\n", sep = "")

cat(if (okB && okC && okD) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
