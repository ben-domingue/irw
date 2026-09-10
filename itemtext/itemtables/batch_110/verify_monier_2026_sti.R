# verify_monier_2026_sti.R
#
# CLAIM UNDER TEST: item_text for STI1..STI10 is row 1..10 of Table 6 of Monier
# et al. (2026) PLOS ONE 21(7):e0352176, i.e. the numbered English wording of the
# 10-item Adult Self-Transcendence Inventory scale.
#
# Why that is falsifiable: Table 6 publishes, for each numbered item, its
# correlation with all seven passage-of-time (PoT) judgments -- a 10 x 7 matrix.
# The S1 Table deposit carries both the STI columns and the PoT columns, so the
# whole matrix can be recomputed. If item_text for any two items were swapped,
# the recomputed row would land on the wrong published row.
#
# Two independent links are checked:
#   (A) published Table 6 row k  <->  S1 Table column STIk_<French fragment>
#       (recomputed correlations, plus a full 10x10 nearest-row assignment so a
#        permutation could not survive)
#   (B) S1 Table column STIk     <->  live IRW item code STIk
#       (per-item n from irw_table_sets(), server-side, no export)
#
# Together they tie the published English wording to the live item code.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "monier_2026_sti"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0352176.s001")

# ---- Published Table 6 (rows = items 1..10; cols = Present, Week, Month,
#      Years, 5 years, Now-before, With aging), 10.1371/journal.pone.0352176.t006
PUB <- matrix(c(
   0.14,  0.08,  0.09,  0.10, 0.17, 0.16, 0.16,
  -0.02, -0.02, -0.02,  0.02, 0.12, 0.06, 0.02,
   0.01, -0.06, -0.02, -0.13, 0.04, 0.00, 0.02,
   0.05, -0.02,  0.01,  0.02, 0.12, 0.17, 0.16,
   0.15,  0.11,  0.11,  0.10, 0.22, 0.16, 0.23,
   0.19,  0.14,  0.17,  0.05, 0.27, 0.27, 0.16,
   0.12,  0.06,  0.06, -0.01, 0.26, 0.26, 0.29,
   0.28,  0.16,  0.19,  0.16, 0.29, 0.32, 0.36,
   0.04,  0.07,  0.10,  0.07, 0.31, 0.28, 0.16,
   0.16,  0.08,  0.09,  0.18, 0.34, 0.32, 0.33),
  nrow = 10, byrow = TRUE)
TOL <- 0.01   # Table 6 is printed to 2 dp

f <- tempfile(fileext = ".xlsx")
utils::download.file(URL, f, quiet = TRUE, mode = "wb",
                     headers = c("User-Agent" = "IRW-itemtext/1.0"))
d <- as.data.frame(readxl::read_excel(f, sheet = "Feuil1", skip = 1))

sti <- grep("^STI[0-9]+_", names(d), value = TRUE)
sti <- sti[order(as.integer(sub("^STI([0-9]+)_.*$", "\\1", sti)))]
pot <- c("PoTpresent_7vite", "PoTweek_7vite", "PoTmonth_7vite", "PoTyear_7vite",
         "PoT5yearago_7vite", "PoT_NowBefore_7vite", "PoTaging_7vite")
stopifnot(length(sti) == 10, all(pot %in% names(d)))

OBS <- matrix(NA_real_, 10, 7)
for (i in 1:10) for (j in 1:7)
  OBS[i, j] <- suppressWarnings(cor(as.numeric(d[[sti[i]]]), as.numeric(d[[pot[j]]]),
                                    use = "pairwise.complete.obs"))

cat("== (A) Table 6 correlations recomputed from S1 Table ==\n")
cat("     (published value / recomputed value), 10 items x 7 PoT judgments\n\n")
cat(sprintf("%-34s %s\n", "S1 column", paste(sprintf("%13s", c("Present","Week","Month","Years","5yrs","NowBef","Aging")), collapse = "")))
for (i in 1:10) {
  cells <- sprintf("%6.2f/%6.2f", PUB[i, ], OBS[i, ])
  cat(sprintf("%-34s %s\n", substr(sti[i], 1, 34), paste(cells, collapse = "")))
}
worst <- max(abs(OBS - PUB))
cat(sprintf("\nlargest |published - recomputed| over all 70 cells: %.4f (tolerance %.2f)\n",
            worst, TOL))

# Full assignment: is published row k really the BEST match for column STIk?
D <- matrix(NA_real_, 10, 10)
for (i in 1:10) for (k in 1:10) D[i, k] <- max(abs(OBS[i, ] - PUB[k, ]))
best <- apply(D, 1, which.min)
offdiag <- sapply(1:10, function(i) min(D[i, -i]))
cat("\nnearest published row for each S1 column (must be 1..10 in order):\n  ",
    paste(best, collapse = " "), "\n")
cat(sprintf("per-item max-deviation, correct row vs. best WRONG row:\n"))
for (i in 1:10)
  cat(sprintf("  %-24s correct %.3f   best wrong %.3f   margin %.0fx\n",
              substr(sti[i], 1, 24), D[i, i], offdiag[i], offdiag[i] / D[i, i]))
okA <- worst <= TOL && identical(as.integer(best), 1:10)

# ---- (B) S1 column -> live IRW item code, via per-item n (server-side) ----
cat("\n== (B) per-item n: S1 Table column vs live IRW table ==\n")
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live_n <- setNames(as.integer(pi$n), as.character(pi$item))
# data/monier_2026_sti.py drops rows with no group assignment, then keeps resp in 1..7
dd <- d[!is.na(d[["Group_1Parkison2_Control"]]), , drop = FALSE]
okB <- TRUE
cat(sprintf("%-8s %8s %8s %6s\n", "item", "raw n", "live n", ""))
for (i in 1:10) {
  code <- paste0("STI", i)
  v <- suppressWarnings(as.numeric(dd[[sti[i]]]))
  rawn <- sum(!is.na(v) & v >= 1 & v <= 7)
  hit <- identical(as.integer(rawn), live_n[[code]])
  okB <- okB && hit
  cat(sprintf("%-8s %8d %8d %6s\n", code, rawn, live_n[[code]], if (hit) "OK" else "MISMATCH"))
}

cat("\nWhat this does NOT establish: the words themselves are the paper's ENGLISH\n",
    "rendering; the instrument was administered in French and no full French text\n",
    "is published, so this verifies WHICH item each English string belongs to, not\n",
    "the exact sentence a respondent read. It also says nothing about the response\n",
    "anchors, which the paper never prints (option_text ships blank).\n", sep = "")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
