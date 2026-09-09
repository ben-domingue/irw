# verify_gao2025_attachment_anxiety.R
#
# Claim under test: the three shipped worry statements (questionnaire Section I
# items 7-9 of the deposit's Questionnaire.doc) belong to the SPSS columns
# CAnxiety1-3, i.e. to the anxiety block rather than to the six avoidance
# statements shipped as gao2025_attachment_avoidance.
#
# Route: subscale block structure (Step 5b route 5) computed on the study's own
# data.sav, plus a means tie-back to the live IRW table so the source columns are
# demonstrably the ones behind the published item codes. Live per-item means are
# hard-coded from item_stats.R (2026-09-05) so this does not export the table.

TABLE <- "gao2025_attachment_anxiety"
SAV   <- "https://ndownloader.figshare.com/files/57648064"   # figshare 28737626

LIVE_MEAN <- c(CAnxiety1 = 3.50, CAnxiety2 = 3.99, CAnxiety3 = 3.45)  # item_stats.R
LIVE_N    <- 459

f <- tempfile(fileext = ".sav")
download.file(SAV, f, quiet = TRUE, mode = "wb")
suppressMessages(library(haven))
d <- haven::read_sav(f)

anx <- paste0("CAnxiety", 1:3)
avo <- paste0("CAvoidance", 1:6)

cat("--- source columns vs live IRW per-item means ---\n")
ok_mean <- TRUE
for (v in anx) {
    m <- mean(d[[v]], na.rm = TRUE); n <- sum(!is.na(d[[v]]))
    cat(sprintf("%-10s source mean %.2f (n=%d)   live mean %.2f (n=%d)\n",
                v, m, n, LIVE_MEAN[[v]], LIVE_N))
    if (abs(round(m, 2) - LIVE_MEAN[[v]]) > 0.005 || n != LIVE_N) ok_mean <- FALSE
}

cm <- cor(as.data.frame(d[, c(anx, avo)]), use = "pairwise.complete.obs")
within <- cm[anx, anx][upper.tri(diag(3))]
cross  <- as.vector(cm[anx, avo])

cat("\n--- block structure ---\n")
cat(sprintf("within-anxiety correlations : %s\n",
            paste(sprintf("%.2f", within), collapse = ", ")))
cat(sprintf("anxiety x avoidance         : min %.2f, max %.2f\n",
            min(cross), max(cross)))
cat(sprintf("min within (%.2f) > max cross (%.2f) ? %s\n",
            min(within), max(cross), min(within) > max(cross)))
ok_block <- min(within) > max(cross)

cat("\nWhat this does NOT establish: it pins the three worry statements to the\n",
    "CAnxiety block as a set, and nothing separates CAnxiety1, 2 and 3 from one\n",
    "another. All three share the 1-7 range and near-identical worry content, and\n",
    "the deposit publishes no per-item statistics. The within-block ordering is the\n",
    "questionnaire's own item order (7,8,9 -> CAnxiety1,2,3) and is unverified;\n",
    "note that r(CAnxiety1,CAnxiety3)=", sprintf("%.2f", cm["CAnxiety1","CAnxiety3"]),
    " exceeds r(CAnxiety2,CAnxiety3)=", sprintf("%.2f", cm["CAnxiety2","CAnxiety3"]),
    ", whereas the two child-regard\nitems (8,9) would on content grounds be expected to be the tightest pair.\n", sep = "")

cat(if (ok_mean && ok_block) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
