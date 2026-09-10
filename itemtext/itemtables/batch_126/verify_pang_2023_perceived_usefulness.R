# verify_pang_2023_perceived_usefulness.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST. data/pang_2023_nev_adoption.py assigns the IRW item codes
# POSITIONALLY: item_cols <- columns 6..45 of the PLOS S1 workbook, and this
# table takes item_cols[0:5] (1-based columns 6..10), renamed item_01..item_05
# in column order. So the claim is
#     item_01 = S1 column  6 = "5. I think driving an NEV is more efficient ..."
#     item_02 = S1 column  7 = "6. ... offers better driving experience ..."
#     item_03 = S1 column  8 = "7. ... makes communication more convenient ..."
#     item_04 = S1 column  9 = "8. ... makes car life richer and exciting"
#     item_05 = S1 column 10 = "9. ... self-learning ability knows me better ..."
# and each shipped item_text is that column's own header (the S1 headers ARE the
# item wording; the S2 questionnaire prints the identical five sentences).
#
# Falsifiable prediction: per-item mean / n / max computed from those five raw
# columns must equal the live IRW per-item values EXACTLY (same rows, no
# transformation), and the five means must be pairwise distinct so that any
# permutation of the five codes would break the test for every permuted item.
# The max column carries an extra, independent signature: only ONE of the five
# source columns has max 4 rather than 5, and the live table's item_02 is the
# only item with resp_max 4.
#
# This verifies the item<->item_text axis ONLY. The option<->resp axis (which
# end of 1..5 is agreement) is NOT verified here -- see the caveat printed at
# the end and notes_pang_2023_perceived_usefulness.csv.

suppressMessages(library(irw))

TABLE <- "pang_2023_perceived_usefulness"
S1 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0285815.s001")

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(S1, tmp, quiet = TRUE, mode = "wb")
raw <- readxl::read_excel(tmp)
stopifnot(ncol(raw) == 45)

pu_cols <- 6:10   # 1-based: item_cols[1:5] of columns 6..45
cat("S1 columns used (positions 6-10):\n")
for (j in pu_cols) cat(sprintf("  col %2d  %s\n", j, substr(names(raw)[j], 1, 72)))

src <- lapply(pu_cols, function(j) suppressWarnings(as.numeric(raw[[j]])))
src <- lapply(src, function(v) v[!is.na(v)])
src_mean <- sapply(src, mean); src_n <- sapply(src, length); src_max <- sapply(src, max)

# The live table is 1,545 rows, so this fetch is a negligible export.
d <- irw::irw_fetch(TABLE)
items <- sprintf("item_%02d", 1:5)
live_mean <- sapply(items, function(i) mean(d$resp[d$item == i]))
live_n    <- sapply(items, function(i) sum(d$item == i))
live_max  <- sapply(items, function(i) max(d$resp[d$item == i]))

cat("\nper-item: source column vs live IRW table\n")
cat(sprintf("%-8s %12s %12s %12s %6s %6s %5s %5s\n",
            "item", "src_mean", "live_mean", "diff", "src_n", "live_n", "s_max", "l_max"))
for (i in 1:5)
  cat(sprintf("%-8s %12.6f %12.6f %12.2e %6d %6d %5d %5d\n",
              items[i], src_mean[i], live_mean[i], live_mean[i] - src_mean[i],
              src_n[i], live_n[i], src_max[i], live_max[i]))

gap <- min(dist(src_mean))
cat(sprintf("\nsmallest gap between any two of the five source means: %.4f\n", gap))
cat("(so the five items are mutually distinguishable by mean; swapping any pair\n",
    " would move both means by at least that much)\n", sep = "")
cat(sprintf("source columns with max < 5: %s ; live items with resp_max < 5: %s\n",
            paste(items[src_max < 5], collapse = ","),
            paste(items[live_max < 5], collapse = ",")))

ok_map <- max(abs(live_mean - src_mean)) < 1e-9 &&
          all(live_n == src_n) && all(live_max == src_max) && gap > 0.01

cat("\nWhat this does NOT establish: (a) the DIRECTION of the response scale --\n")
cat("the S2 questionnaire lists 'Definitely agree' first and the paper's Methods\n")
cat("says 1 = strongly disagree, and these contradict; the shipped anchors follow\n")
cat("the questionnaire's display order on the strength of the file's demographic\n")
cat("coding, which is corroborative only. (b) nothing about the WORDS themselves --\n")
cat("the administered Chinese is unpublished, so item_text is the study's own\n")
cat("English rendering (S1 headers == S2 questionnaire, verbatim).\n")

cat(if (ok_map) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
