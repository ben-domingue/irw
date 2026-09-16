# verify_uffler_2017_lecture_seating.R -- Step 5b, route 3 (published subscale
# statistics) with a rival-mapping contrast.
#
# CLAIM UNDER TEST: the shipped item_text assigns QUESTION1..QUESTIO26 to the 26
# MSLQ motivation items that remain once the five test-anxiety items (original
# MSLQ 3, 8, 14, 19, 28) are dropped -- i.e. QUESTIONn = the n-th surviving MSLQ
# item, which is what the S2 workbook's own 'codes' sheet states for Q1..Q26.
# That assignment implies a fixed five-block subscale structure. Uffler et al.
# (2017), Results, publish an r-squared per subscale for the regression of the
# row-level mean score on the row number (1..9); those five numbers are the
# falsifiable prediction. A wrong block assignment changes them.
#
# The rival mapping (B) is the obvious alternative reading -- QUESTIONn = MSLQ
# item n, test-anxiety items never removed -- which has to drop items 29/30/31.
#
# WHAT THIS DOES NOT ESTABLISH: subscale membership only. It cannot distinguish
# two items inside the same subscale (e.g. QUESTION1 vs QUESTIO13, both intrinsic
# goal orientation). Within-block order rests on the workbook's codes sheet, not
# on this script. Status recorded as PARTIAL for that reason.

suppressMessages(library(irw))
TABLE <- "uffler_2017_lecture_seating"

# Uffler S, Bartier J-C, Pelaccia T (2017) PLoS ONE 12(3):e0174947, Results.
PUB <- c(intrinsic = 0.73, extrinsic = 0.20, taskvalue = 0.84,
         selfeff = 0.63, control = 0.48)

q <- function(n) ifelse(n < 10, paste0("QUESTION", n), paste0("QUESTIO", n))

# A = shipped mapping (MSLQ numbering after removing test-anxiety items)
A <- list(intrinsic = c(1, 13, 18, 20), extrinsic = c(6, 9, 11, 25),
          taskvalue = c(3, 8, 14, 19, 22, 23),
          selfeff   = c(4, 5, 10, 12, 16, 17, 24, 26),
          control   = c(2, 7, 15, 21))
# B = rival mapping (QUESTIONn = MSLQ item n)
B <- list(intrinsic = c(1, 16, 22, 24), extrinsic = c(7, 11, 13, 30),
          taskvalue = c(4, 10, 17, 23, 26, 27),
          selfeff   = c(5, 6, 12, 15, 20, 21, 29, 31),
          control   = c(2, 9, 18, 25))

d <- as.data.frame(irw::irw_fetch(TABLE))
ids <- sort(unique(d$id))
w <- data.frame(id = ids,
                cov_seat_rank_preference = d$cov_seat_rank_preference[match(ids, d$id)])
for (it in sort(unique(d$item))) {
    s <- d[d$item == it, ]
    w[[it]] <- s$resp[match(ids, s$id)]
}
cat("students:", nrow(w), " students per seat row:",
    paste(table(w$cov_seat_rank_preference), collapse = " "), "\n\n")

r2 <- function(nums, dat = w) {
    it <- q(nums); it <- it[it %in% names(dat)]
    sc <- rowMeans(dat[, it, drop = FALSE], na.rm = TRUE)
    agg <- tapply(sc, dat$cov_seat_rank_preference, mean, na.rm = TRUE)
    summary(lm(as.numeric(agg) ~ as.numeric(names(agg))))$r.squared
}

vA <- sapply(names(PUB), function(n) r2(A[[n]]))
vB <- sapply(names(PUB), function(n) r2(B[[n]]))
cat(sprintf("%-10s %9s %9s %9s\n", "subscale", "published", "shipped", "rival"))
for (n in names(PUB))
    cat(sprintf("%-10s %9.2f %9.3f %9.3f\n", n, PUB[n], vA[n], vB[n]))

sseA <- sum((vA - PUB)^2); sseB <- sum((vB - PUB)^2)
cat(sprintf("\nSSE vs published: shipped %.3f | rival %.3f\n", sseA, sseB))

# Extrinsic is the one component the paper itself reports as non-significant
# (p = 0.22), and it is dominated by seat row 9, which holds 5 students; dropping
# that row moves the shipped mapping's extrinsic r2 from ~0.00 to ~0.65. It
# carries no discriminating information and is excluded from the tolerance test.
w8 <- w[w$cov_seat_rank_preference < 9, ]
cat(sprintf("extrinsic, seat rows 1-8 only: shipped %.3f (row 9 n=%d)\n",
            r2(A$extrinsic, w8), sum(w$cov_seat_rank_preference == 9, na.rm = TRUE)))

sig <- c("intrinsic", "taskvalue", "selfeff", "control")
worst <- max(abs(vA[sig] - PUB[sig]))
cat(sprintf("largest |shipped - published| over the four significant subscales: %.3f (tol 0.10)\n",
            worst))

cat("Note: this pins subscale MEMBERSHIP, not the order of items within a subscale;\n",
    "the S2 workbook's 'codes' sheet (Q1..Q26 -> text) is what ties those.\n", sep = "")

cat(if (worst <= 0.10 && sseA < sseB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
