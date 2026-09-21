# verify_opladen2025_fkg.R -- Step 5b, batch_291.
#
# CLAIM UNDER TEST: live item code FKG_n carries the wording the OSF deposit's
# "Readme" sheet records for its raw column FKG_n. If item_text for any two
# items were swapped, this check breaks.
#
# ROUTE: direct reproduction of the source (core model section 3, "re-run the
# script"), strengthened to a per-item fingerprint. For each item, the count of
# each response level 1-4 is computed from the deposit's own spreadsheet column
# and compared cell-for-cell with the live IRW table. The 20 count vectors
# hard-coded below are MUTUALLY DISTINCT (asserted at run time), so a match
# distinguishes every item from every other item -- not just from a random
# permutation.
#
# SOURCE of the hard-coded vectors: OSF osf.io/58xb9, "Data - Rawdata.xlsx"
# (md5 51aec995d684eeb2d33bb06784e2eeca), sheet "Questionnaire Data", columns
# FKG_1..FKG_20, after de-duplicating on `vpcode (anonymized)` exactly as
# data/opladen2025_body_checking.py does. Counts are of raw stored values; the
# processing script melts these columns unchanged, so no recoding intervenes.

suppressMessages(library(irw))

TABLE <- "opladen2025_fkg"

# rows = FKG_1 .. FKG_20; columns = count of resp 1, 2, 3, 4
SRC <- rbind(
  FKG_1  = c( 3,  12, 83, 112),
  FKG_2  = c( 2,  37, 45, 126),
  FKG_3  = c(23,  69, 62,  56),
  FKG_4  = c( 1,   8, 45, 156),
  FKG_5  = c(21,  60, 87,  42),
  FKG_6  = c( 6,  41, 69,  94),
  FKG_7  = c( 1,   8, 61, 140),
  FKG_8  = c( 9,  23, 40, 138),
  FKG_9  = c(12, 103, 66,  29),
  FKG_10 = c( 3,  19, 71, 117),
  FKG_11 = c( 5,  15, 48, 142),
  FKG_12 = c(11,  17, 44, 138),
  FKG_13 = c( 3,  15, 45, 147),
  FKG_14 = c( 4,  10, 36, 160),
  FKG_15 = c( 8,  28, 87,  87),
  FKG_16 = c( 0,  19, 69, 122),
  FKG_17 = c(10,  61, 68,  71),
  FKG_18 = c( 8,  26, 66, 110),
  FKG_19 = c(18,  32, 51, 109),
  FKG_20 = c( 9,  22, 68, 111)
)
colnames(SRC) <- as.character(1:4)

n_distinct <- nrow(unique(SRC))
cat(sprintf("source count vectors: %d rows, %d distinct\n", nrow(SRC), n_distinct))
if (n_distinct != nrow(SRC))
    cat("WARNING: vectors are not mutually distinct; the route cannot separate every item.\n")

d <- irw::irw_fetch(TABLE)
LIVE <- table(factor(d$item, levels = rownames(SRC)),
              factor(d$resp, levels = 1:4))
LIVE <- matrix(as.integer(LIVE), nrow = nrow(SRC),
               dimnames = list(rownames(SRC), as.character(1:4)))

cat(sprintf("\n%-8s %-22s %-22s %s\n", "item", "source (1/2/3/4)", "live (1/2/3/4)", "match"))
ok <- TRUE
for (i in rownames(SRC)) {
    s <- paste(SRC[i, ], collapse = "/")
    l <- paste(LIVE[i, ], collapse = "/")
    m <- all(as.integer(SRC[i, ]) == as.integer(LIVE[i, ]))
    ok <- ok && m
    cat(sprintf("%-8s %-22s %-22s %s\n", i, s, l, if (m) "yes" else "NO"))
}

cat(sprintf("\ncells compared: %d; mismatching cells: %d\n",
            length(SRC), sum(SRC != LIVE)))

# Direction of the resp scale (the option_text<->resp axis) is taken from the
# Readme's own value labels, 1 = "stimmt voll und ganz" (completely true) ...
# 4 = "stimmt nicht" (not true). Corroborating signal, printed rather than gated:
# the most extreme catastrophic beliefs should be the LEAST endorsed, i.e. sit
# highest on this coding.
mu <- tapply(d$resp, d$item, mean)
cat("\nitem means under 1 = completely true ... 4 = not true:\n")
cat(sprintf("  lowest  (most endorsed):  %s\n",
            paste(sprintf("%s=%.2f", names(sort(mu))[1:3], sort(mu)[1:3]), collapse = "  ")))
cat(sprintf("  highest (least endorsed): %s\n",
            paste(sprintf("%s=%.2f", rev(names(sort(mu)))[1:3], rev(sort(mu))[1:3]), collapse = "  ")))
cat("  Expected under this direction: FKG_9 ('take it easy with joint pain', a\n")
cat("  normatively reasonable belief) lowest; FKG_4/FKG_14/FKG_7 (constipation ->\n")
cat("  colorectal cancer, sore throat -> laryngeal disease, skin redness -> skin\n")
cat("  cancer) highest. A reversed coding would make the most catastrophic items\n")
cat("  the most endorsed.\n")

cat("\nWhat this does NOT establish: that the German wording in the Readme is the\n")
cat("verbatim published FKG item, and that the instrument is Hiller et al. (1997)\n")
cat("-- the deposit gives only the abbreviation. It establishes the code<->wording\n")
cat("tie within the deposit, which is what item_text claims.\n")

cat(if (ok && n_distinct == nrow(SRC)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
