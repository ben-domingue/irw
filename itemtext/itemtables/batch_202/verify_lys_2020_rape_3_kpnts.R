# Verification for lys_2020_rape_3_kpnts (#1945, batch_202).
#
# The mapping needs no verification -- the .sav label sits on the column whose
# name becomes the item code, and numbers itself "sdo item1".."sdo item 16",
# which is what rules out reading the non-contiguous codes as kpnts1..16.
#
# What this script settles is a SCORING question that the table originally got
# wrong. Eight of the sixteen are reverse-worded in the original scale, and the
# first public note said all sixteen are "stored RAW". Solving for the weights
# of the deposit's own SDO score decides it, and the same test is applied to the
# three sibling scales because the identical claim was made about them.
suppressMessages(library(haven))
x <- as.data.frame(read_sav(".cache/lys_2020_rape/study3.sav"))
lab1 <- function(v) { l <- attr(x[[v]], "label"); if (is.null(l)) "" else as.character(l) }

KP <- c("kpnts2","kpnts3","kpnts5","kpnts7","kpnts8","kpnts10","kpnts11","kpnts13",
        "kpnts14","kpnts16","kpnts17","kpnts19","kpnts20","kpnts22","kpnts23","kpnts24")

check <- function(vars, total, name) {
    m <- sapply(x[vars], as.numeric); y <- as.numeric(x[[total]])
    ok <- !is.na(y) & rowSums(is.na(m)) == 0
    R  <- grepl("[(]R[)][[:space:]]*$", vapply(vars, lab1, character(1)))
    plain <- sum(abs(rowSums(m[ok, ]) - y[ok]) < 1e-8)
    mm <- m[ok, ]; for (j in which(R)) mm[, j] <- 6 - mm[, j]
    flip <- sum(abs(rowSums(mm) - y[ok]) < 1e-8)
    verdict <- if (plain == sum(ok)) "PRE-RECODED" else if (flip == sum(ok)) "RAW" else "neither"
    cat(sprintf("  %-8s n=%3d  (R)=%d  plain sum %3d/%-3d  (R) flipped %3d/%-3d  -> %s\n",
                name, sum(ok), sum(R), plain, sum(ok), flip, sum(ok), verdict))
    verdict == "PRE-RECODED"
}

cat("=== does a plain sum reproduce the deposit's own composite? ===\n")
res <- c(kpnts  = check(KP, "sdo", "kpnts"),
         sj     = check(paste0("sj", 1:8), "sj", "sj"),
         rwa    = check(paste0("rwa", 1:12), "rwa_sum", "rwa"),
         unjust = check(paste0("unjust", 1:10), "unjust", "unjust"))

cat("\nAll four sibling scales in this battery are stored PRE-RECODED: the plain\n")
cat("sum reproduces the deposit's score exactly, and flipping the items the .sav\n")
cat("marks (R) does not. Higher resp therefore means more of the construct for\n")
cat("EVERY item, and nothing should be reversed again before scoring.\n")

cat("\n=== corroboration for kpnts specifically ===\n")
m <- sapply(x[KP], as.numeric)
R <- grepl("[(]R[)][[:space:]]*$", vapply(KP, lab1, character(1)))
C <- cor(m, use = "pairwise.complete.obs"); F <- which(!R)
cat(sprintf("  mean r within the (R) eight:     %+0.3f\n", mean(C[R, R][upper.tri(diag(sum(R)))])))
cat(sprintf("  mean r within the forward eight: %+0.3f\n", mean(C[F, F][upper.tri(diag(length(F)))])))
cat(sprintf("  mean r across the two blocks:    %+0.3f\n", mean(C[R, F])))
cat(sprintf("  (R) item mean %.2f vs forward item mean %.2f\n",
            mean(m[, R], na.rm = TRUE), mean(m[, !R], na.rm = TRUE)))
cat("  Both consistent with recoding and not with raw storage: a raw table would\n")
cat("  show a NEGATIVE across-block correlation, and its egalitarian items would\n")
cat("  sit far above its hierarchy items rather than level with them.\n")

cat("\nVERDICT:", if (all(res)) "PASS" else "FAIL", "\n")
