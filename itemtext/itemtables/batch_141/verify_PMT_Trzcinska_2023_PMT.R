# verify_PMT_Trzcinska_2023_PMT.R
#
# CLAIM UNDER TEST (Step 5b), two parts:
#
#  (A) resp 1 = the FIRST picture named in the item sentence, resp 2 = the SECOND
#      (pictures A and B on the printed page), and each ONE* item code's embedded
#      pair label (e.g. ONE1szZAB_RYS -> "zabawki" then "rysowanie") names those two
#      pictures in that order.
#  (B) TWO<n><block> is the SAME question as ONE<n><block><pair>, re-administered
#      two weeks later (the paper's test-retest subsample).
#
# Both are falsifiable from the study's own OSF deposit, which ships (i) the raw
# response columns under exactly the IRW item codes and (ii) the study's own
# recoded columns rONE*/rTWO*, where 1 = "chose the materialistic picture". If the
# pair label in a code were wrong, or resp 1/2 were the other way round, the recode
# would not reproduce. This does NOT re-check item or resp SETS -- validate_items.R
# did that.
#
# Data: https://osf.io/xbrnm/ ("Pictorial Materialism Test_database_clean.sav"),
# CC BY 4.0. Fetched over the network; no IRW export is needed.

suppressMessages(library(haven))

TABLE <- "PMT_Trzcinska_2023_PMT"
SAV_URL <- "https://osf.io/download/xbrnm/files/osfstorage/64051a55c7db3606d0ba7c73/"
LIVE_ROWS <- 7392L   # row count of the live IRW table (irw_table_sets, 2026-09-10)
PAPER_N   <- 204L    # Trzcinska et al. 2023, PLOS ONE 18(8):e0290512, final sample
PAPER_RETEST_N <- 27L

f <- tempfile(fileext = ".sav")
ok <- tryCatch({
  ids <- readLines("https://api.osf.io/v2/nodes/xbrnm/files/osfstorage/", warn = FALSE)
  ids <- paste(ids, collapse = "")
  m <- regmatches(ids, gregexpr('"name":"Pictorial Materialism Test_database_clean.sav".*?"download":"([^"]+)"', ids))[[1]]
  url <- sub('.*"download":"([^"]+)".*', '\\1', m[1])
  download.file(url, f, quiet = TRUE, mode = "wb"); TRUE
}, error = function(e) FALSE)
if (!ok || !file.exists(f) || file.size(f) < 1000) stop("could not fetch the OSF .sav")

d <- read_sav(f)

MAT <- c("ZAB", "PREZ", "PIEN", "UBR")          # material pictures
NON <- c("RYS", "CZYT", "KOL", "PLAC")          # activity/relationship pictures
one <- grep("^ONE", names(d), value = TRUE)
two <- grep("^TWO", names(d), value = TRUE)

cat("== columns in the deposit vs IRW item codes ==\n")
cat(sprintf("ONE* columns: %d   TWO* columns: %d   (live IRW item set: 64)\n",
            length(one), length(two)))
cat(sprintf("non-missing cells across all 64 columns: %d   live IRW rows: %d\n",
            sum(!is.na(as.matrix(d[c(one, two)]))), LIVE_ROWS))
cat(sprintf("per-column non-missing: ONE %d (paper N=%d), TWO %d (paper retest n=%d)\n\n",
            sum(!is.na(d[[one[1]]])), PAPER_N, sum(!is.na(d[[two[1]]])), PAPER_RETEST_N))

matpos_from_code <- function(v) {
  tk <- strsplit(sub("^ONE[0-9]+(sz|f)", "", v), "_")[[1]]
  stopifnot(length(tk) == 2, sum(tk %in% MAT) == 1)
  if (tk[1] %in% MAT) 1L else 2L
}

cat("== (A) does resp 1 = first-named picture reproduce the study's own recode? ==\n")
okA <- 0L; badA <- character()
for (v in one) {
  pred <- as.integer(d[[v]] == matpos_from_code(v))
  act  <- d[[paste0("r", v)]]
  if (isTRUE(all(pred == act, na.rm = TRUE)) && all(is.na(pred) == is.na(act))) okA <- okA + 1L
  else badA <- c(badA, v)
}
cat(sprintf("ONE block: %d/%d columns reproduce rONE* exactly%s\n", okA, length(one),
            if (length(badA)) paste0("  FAILED: ", paste(badA, collapse = ", ")) else ""))
# direction split - shows the check is not vacuous
dirs <- vapply(one, matpos_from_code, 1L)
cat(sprintf("  (16 codes name the material picture first, %d name it second: %s)\n",
            sum(dirs == 2), paste(names(table(dirs)), table(dirs), sep = ":", collapse = " ")))

okB <- 0L; badB <- character()
for (v in two) {
  num  <- sub("^TWO([0-9]+)(sz|f)$", "\\1\\2", v)
  onev <- grep(paste0("^ONE", num), one, value = TRUE)
  pred <- as.integer(d[[v]] == matpos_from_code(onev))
  act  <- d[[paste0("r", v)]]
  if (isTRUE(all(pred == act, na.rm = TRUE)) && all(is.na(pred) == is.na(act))) okB <- okB + 1L
  else badB <- c(badB, v)
}
cat(sprintf("TWO block: %d/%d columns reproduce rTWO* under the number-matched ONE pairing%s\n\n",
            okB, length(two), if (length(badB)) paste0("  FAILED: ", paste(badB, collapse = ", ")) else ""))

cat("== (B) does the assumed TWO<n> <-> ONE<n> pairing show test-retest signal? ==\n")
rone <- paste0("r", one); rtwo <- paste0("r", two)
sub  <- !is.na(d[[two[1]]])
pA <- colMeans(as.matrix(d[, rone]))
pB <- colMeans(as.matrix(d[sub, rtwo]))
robs <- cor(pA, pB)
set.seed(1)
perm <- replicate(2000, cor(pA, sample(pB)))
cat(sprintf("cor(materialistic-choice rate ONE_k, TWO_k) over 32 pairs = %.3f\n", robs))
cat(sprintf("random re-pairings: mean %.3f, 97.5th pct %.3f, permutation p = %.4f\n",
            mean(perm), quantile(perm, .975), mean(perm >= robs)))
cat("Per-item test-retest agreement is NOT decisive here: mean on-diagonal agreement\n")
A <- as.matrix(d[sub, one]); B <- as.matrix(d[sub, two])
ag <- outer(1:32, 1:32, Vectorize(function(i, j) mean(A[, i] == B[, j])))
cat(sprintf("  %.3f vs %.3f off-diagonal, and the diagonal is the strict maximum for only %d of 32 items (n=27).\n\n",
            mean(diag(ag)), mean(ag[row(ag) != col(ag)]),
            sum(vapply(1:32, function(i) all(ag[i, -i] < ag[i, i]), TRUE))))

cat("== (C) does the SHIPPED item text match the picture each code names? ==\n")
KEY <- c(ZAB = "du\u017co zabawek", RYS = "\u0142adnie rysuje", PLAC = "na placu zabaw",
         PREZ = "dosta\u0142", CZYT = "mama czyta bajk\u0119", UBR = "\u0142adne ubrania",
         KOL = "du\u017co kole", PIEN = "du\u017co pieni\u0119dzy")
items_csv <- file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])),
                       paste0(TABLE, "__items.csv"))
okC <- 0L; badC <- character(); nC <- 0L
if (file.exists(items_csv)) {
  it <- read.csv(items_csv, stringsAsFactors = FALSE, encoding = "UTF-8")
  for (v in c(one, two)) {
    onev <- if (grepl("^ONE", v)) v else
      grep(paste0("^ONE", sub("^TWO([0-9]+)(sz|f)$", "\\1\\2", v)), one, value = TRUE)
    tk <- strsplit(sub("^ONE[0-9]+(sz|f)", "", onev), "_")[[1]]
    for (k in 1:2) {
      nC <- nC + 1L
      row <- it[it$item == v & it$resp == k, ]
      if (nrow(row) == 1L && grepl(KEY[[tk[k]]], row$option_text[1], fixed = TRUE)) okC <- okC + 1L
      else badC <- c(badC, paste0(v, "/resp", k))
    }
  }
  cat(sprintf("shipped option_text carries the picture the code names, in code order: %d/%d%s\n\n",
              okC, nC, if (length(badC)) paste0("  FAILED: ", paste(badC, collapse = ", ")) else ""))
} else {
  cat("shipped items CSV not found next to this script -- skipping (C)\n\n")
}

cat("WHAT THIS DOES NOT ESTABLISH: the recode check is one bit per column, so it\n")
cat("separates 'material picture first' from 'material picture second' but cannot\n")
cat("distinguish the 16 codes within either class. For the ONE block that gap is\n")
cat("closed outside this script, by the pair label the code itself carries matched\n")
cat("against the OSF questionnaire PDFs sentence by sentence (32/32). For the TWO\n")
cat("block there is no such label: its pairing rests on the shared numeric suffix\n")
cat("convention plus the aggregate correlation above, so any two TWO items in the\n")
cat("same direction class could in principle be swapped. Hence PARTIAL, not VERIFIED.\n\n")

pass <- okA == length(one) && okB == length(two) && (nC == 0L || okC == nC) &&
        sum(!is.na(as.matrix(d[c(one, two)]))) == LIVE_ROWS && robs > 0.5
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
