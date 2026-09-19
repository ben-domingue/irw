# verify_gillman_2023_pss.R -- Step 5b, route 6 (keying polarity) + route 3
# (published scale-level statistic).
#
# CLAIM UNDER TEST: the shipped item_text assigns the four POSITIVELY-worded
# PSS-10 stems (canonical items 4, 5, 7, 8 -- "felt confident...", "things were
# going your way", "able to control irritations", "on top of things") to exactly
# PS_4_R, PS_5_R, PS_7_R, PS_8_R, and the six negatively-worded stems to
# PS_1, PS_2, PS_3, PS_6, PS_9, PS_10 -- and that the live table stores those
# four items RAW (not reverse-scored), so the shipped 0-4 Never..Very Often
# anchors read as written for every item.
#
# If the polarity assignment were wrong for any single item, that item's
# correlations would flip sign relative to its assigned block. If the four _R
# items were stored already-reversed, the cross-block correlations would be
# POSITIVE and the paper's reported alpha would not reproduce from the raw sum.
#
# What this does NOT establish: the ORDER WITHIN each polarity class. Nothing
# here separates PS_4_R from PS_5_R/PS_7_R/PS_8_R, or PS_1 from PS_2/PS_3/
# PS_6/PS_9/PS_10. Those rest on the numeric correspondence between the source
# .sav column names (PS_<n>) and Cohen's own numbered PSS-10 form, which prints
# "Reversed Items: 4, 5, 7, 8".

suppressMessages(library(irw))

TABLE <- "gillman_2023_pss"
POS <- c("PS_4_R", "PS_5_R", "PS_7_R", "PS_8_R")   # positively-worded stems
NEG <- c("PS_1", "PS_2", "PS_3", "PS_6", "PS_9", "PS_10")
PUBLISHED_ALPHA <- 0.67   # Gillman et al. 2023, PLOS ONE 18(7):e0288563, Methods

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[stats::complete.cases(w[, c(POS, NEG)]), ]
cat(sprintf("complete cases: %d\n\n", nrow(w)))

R <- cor(w[, c(POS, NEG)])

cat("--- correlations of each assigned-POSITIVE item with each assigned-NEGATIVE item\n")
cat("    (all must be < 0 if the polarity assignment is right and data are raw)\n")
print(round(R[POS, NEG], 3))

cross <- as.vector(R[POS, NEG])
wp <- R[POS, POS][upper.tri(R[POS, POS])]
wn <- R[NEG, NEG][upper.tri(R[NEG, NEG])]
cat(sprintf("\ncross-block r  : min %.3f  max %.3f   (need max < 0)\n", min(cross), max(cross)))
cat(sprintf("within-POS r   : min %.3f  max %.3f   (need min > 0)\n", min(wp), max(wp)))
cat(sprintf("within-NEG r   : min %.3f  max %.3f   (need min > 0)\n", min(wn), max(wn)))

alpha <- function(x) { k <- ncol(x); k / (k - 1) * (1 - sum(apply(x, 2, var)) / var(rowSums(x))) }
X <- as.matrix(w[, c(POS, NEG)])
Xr <- X; Xr[, POS] <- 4 - Xr[, POS]
a_raw <- alpha(X); a_rev <- alpha(Xr)
cat(sprintf("\nalpha of the 10 items AS STORED (unreversed) : %.4f  (paper reports %.2f)\n",
            a_raw, PUBLISHED_ALPHA))
cat(sprintf("alpha after reversing PS_4_R/5_R/7_R/8_R     : %.4f\n", a_rev))

ok <- max(cross) < 0 && min(wp) > 0 && min(wn) > 0 &&
      abs(a_raw - PUBLISHED_ALPHA) < 0.01
cat("\nNote: this pins each item's POLARITY CLASS and the raw (unreversed) storage\n",
    "direction. It does NOT order items within a class.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
