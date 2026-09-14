# verify_pang_2023_perceived_ease_use.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST. data/pang_2023_nev_adoption.py assigns the IRW item codes
# POSITIONALLY: item_cols <- columns 6..45 of the PLOS S1 workbook, and this
# table takes item_cols[6:10] (0-indexed [5:10]), renamed item_01..item_05 in
# column order. So the claim is
#     item_01 = S1 column 11 = "10. I think it's easier to drive an NEV ..."
#     item_02 = S1 column 12 = "11. ... the operation in an NEV is more convenient"
#     item_03 = S1 column 13 = "12. ... the operation interface ... friendly"
#     item_04 = S1 column 14 = "13. ... all the intelligent functions ..."
#     item_05 = S1 column 15 = "14. ... remote software update ..."
# and each shipped item_text is that column's own header (the S1 headers ARE the
# item wording). The falsifiable prediction: per-item mean/n/max computed from
# those five raw columns must equal the live IRW per-item values EXACTLY (same
# rows, no transformation), and the five means must be pairwise distinct so that
# any permutation of the five codes would break the test for every permuted item.
#
# Also printed: the option_text<->resp direction evidence. The S1 file's
# demographic columns are coded in the questionnaire's own option display order
# (S2 File), which is what the shipped anchors (1 = "Definitely agree" ...
# 5 = "Definitely disagree") rely on -- and which CONTRADICTS the paper's Methods
# sentence "ranging from 1 point (strongly disagree) to 5 points (strongly
# agree)". That half is corroborative, not decisive; see the note printed below.

suppressMessages(library(irw))

TABLE <- "pang_2023_perceived_ease_use"
S1 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0285815.s001")

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(S1, tmp, quiet = TRUE, mode = "wb")
raw <- readxl::read_excel(tmp)
stopifnot(ncol(raw) == 45)

peou_cols <- 11:15   # 1-based: item_cols[6:10] of columns 6..45
cat("S1 columns used (positions 11-15):\n")
for (j in peou_cols) cat(sprintf("  col %2d  %s\n", j, substr(names(raw)[j], 1, 70)))

src <- lapply(peou_cols, function(j) suppressWarnings(as.numeric(raw[[j]])))
src <- lapply(src, function(v) v[!is.na(v)])
src_mean <- sapply(src, mean); src_n <- sapply(src, length); src_max <- sapply(src, max)

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
cat("(so the five items are mutually distinguishable by mean; a swap of any pair\n",
    " would move an item mean by at least that much)\n", sep = "")

ok_map <- max(abs(live_mean - src_mean)) < 1e-9 &&
          all(live_n == src_n) && all(live_max == src_max) && gap > 0.01

# ---- option-axis corroboration: the file's coding convention ----
age <- table(suppressWarnings(as.numeric(raw[[3]])))
edu <- table(suppressWarnings(as.numeric(raw[[4]])))
sex <- table(suppressWarnings(as.numeric(raw[[2]])))
n <- nrow(raw)
cat("\noption-axis corroboration (whole-file coding convention):\n")
cat(sprintf("  gender  1=%d 2=%d        vs paper Table 2: Male 172, Female 137 (listed in that order)\n",
            sex[["1"]], sex[["2"]]))
cat(sprintf("  age     codes 1+2 = %.1f%% vs paper text 'Most (88.5%%) of the respondents were aged between 20-40'\n",
            100 * (age[["1"]] + age[["2"]]) / n))
cat(sprintf("  educ    codes 3+4 = %.1f%% vs paper text '90.3%% of the respondents had a bachelor's degree or above'\n",
            100 * (edu[["3"]] + edu[["4"]]) / n))
cat("  => 3 of 4 demographic variables are coded in the S2 questionnaire's own option\n")
cat("     display order, which is the basis for shipping resp 1 = 'Definitely agree'\n")
cat("     (the first-listed option) .. 5 = 'Definitely disagree'.\n")
cat("  CAVEAT, printed deliberately: profession does NOT follow that order (data codes\n")
cat("     1..6 = 156/12/46/33/38/24 vs Table 2 156/38/46/33/12/24, i.e. codes 2 and 5 swapped),\n")
cat("     and the paper's Methods states the OPPOSITE Likert direction. The option axis is\n")
cat("     therefore NOT verified; only the item<->text axis is.\n")

cat("\nWhat this does NOT establish: the direction of the response scale (above), and\n")
cat("nothing about the words themselves -- the administered Chinese is unpublished, so\n")
cat("item_text is the study's own English rendering (S1 headers == S2 questionnaire).\n")

cat(if (ok_map) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
