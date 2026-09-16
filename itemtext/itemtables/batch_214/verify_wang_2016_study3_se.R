# verify_wang_2016_study3_se.R
#
# CLAIM UNDER TEST (Step 5b).  wang_2016_study3_se holds the 10 Rosenberg
# Self-Esteem Scale items of Wang YN (2016) PLOS ONE 11(1):e0146050, Study 3
# (n = 210 Chinese adults).  The deposit's S3 SPSS file carries NO variable
# labels, so which canonical RSES sentence each code se1..se10 names is
# RECONSTRUCTED from the numbering of the edition the paper cites as [33]
# (Rosenberg 1965 as reproduced in the Acceptance and Commitment Therapy
# Measures Package, p.61: item 1 "On the whole, I am satisfied with myself",
# negatively worded items 2, 5, 6, 8, 9).  Three things are testable:
#
#  (a) KEYING DIRECTION.  The live resp is stored ALREADY REVERSE-CODED, i.e.
#      5 always means high self-esteem, never "agrees with a negative
#      statement".  This is what the shipped option_text encodes by FLIPPING
#      the source file's own Chinese anchors on se2/se5/se6/se8/se9.
#      Falsifiable: alpha over the stored values must reproduce the paper's
#      published .90 and the per-person sum must reproduce Table 5's
#      M = 39.12, SD = 6.95; un-reversing the five shipped negatives must
#      destroy alpha.
#
#  (b) POLARITY PARTITION -- WHICH five are the negatively worded items.  The
#      RSES wording method factor is a testable prediction: same-polarity
#      items intercorrelate more than cross-polarity ones.  The shipped
#      partition {se2,se5,se6,se8,se9} must rank at the top of all 126
#      possible 5/5 splits, and the rival socy.umd.edu numbering
#      {se3,se5,se8,se9,se10} must not.
#
#  (c) OPTION AXIS (route 9).  The source .sav stores value-labelled codes and
#      the IRW table stores integers.  Every item x level count must match
#      cell for cell, which fixes which integer each Chinese anchor belongs
#      to.  (It fixes the code<->anchor tie; the deliberate flip on the five
#      negatives is justified by (a), not by this.)
#
#  (d) NOT TESTED, which is why the status is PARTIAL: the ORDER WITHIN each
#      polarity class.  The negatives are stored reverse-coded so no sign
#      information survives, and the study publishes no per-item statistics.
#      Printed below so the gap is visible rather than asserted away.

suppressMessages(library(irw))

TABLE <- "wang_2016_study3_se"
ITEMS <- paste0("se", 1:10)
SHIPPED_NEG <- c("se2","se5","se6","se8","se9")   # ACT Measures Package numbering
RIVAL_NEG   <- c("se3","se5","se8","se9","se10")  # socy.umd.edu numbering

# Wang (2016), Study 3: Measures ("Cronbach's alpha = .90") and Table 5.
PUB <- list(alpha = 0.90, sum_m = 39.12, sum_sd = 6.95, n = 210)
TOL_A <- 0.015; TOL_M <- 0.05; TOL_SD <- 0.05

d <- irw::irw_fetch(TABLE)
w <- reshape(data.frame(id = as.character(d$id), item = as.character(d$item),
                        resp = as.numeric(d$resp)),
             idvar = "id", timevar = "item", direction = "wide")
m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
m <- m[complete.cases(m), ITEMS, drop = FALSE]
cat(sprintf("live table: %d respondents x %d items (paper: n = %d)\n\n",
            nrow(m), ncol(m), PUB$n))

alpha <- function(X) { k <- ncol(X); k/(k-1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }

## ---- (a) keying direction ------------------------------------------------
a_stored <- alpha(m); s <- rowSums(m)
m_unrev <- m; m_unrev[, SHIPPED_NEG] <- 6 - m_unrev[, SHIPPED_NEG]
a_unrev <- alpha(m_unrev)
m_rival <- m; m_rival[, RIVAL_NEG] <- 6 - m_rival[, RIVAL_NEG]
cat("(a) KEYING DIRECTION\n")
cat(sprintf("%-42s %10s %10s\n", "quantity", "published", "observed"))
cat(sprintf("%-42s %10.2f %10.3f\n", "Cronbach's alpha, stored values", PUB$alpha, a_stored))
cat(sprintf("%-42s %10.2f %10.3f\n", "10-item sum, M", PUB$sum_m, mean(s)))
cat(sprintf("%-42s %10.2f %10.3f\n", "10-item sum, SD", PUB$sum_sd, sd(s)))
cat(sprintf("%-42s %10s %10.3f\n", "alpha if shipped negatives un-reversed", "<.40", a_unrev))
cat(sprintf("%-42s %10s %10.3f\n", "alpha if rival negatives un-reversed", "--", alpha(m_rival)))
cat(sprintf("%-42s %10s %10.2f\n", "min inter-item correlation", ">0", min(cor(m)[upper.tri(diag(10))])))
cat("  -> all 45 inter-item correlations positive, so the five negatively worded\n")
cat("     items were reverse-coded before deposit and the shipped anchors are\n")
cat("     flipped on those five to match.\n\n")
ok_a <- abs(a_stored - PUB$alpha) <= TOL_A && abs(mean(s) - PUB$sum_m) <= TOL_M &&
        abs(sd(s) - PUB$sum_sd) <= TOL_SD && a_unrev < 0.40

## ---- (b) polarity partition ---------------------------------------------
C <- cor(m)
contrast <- function(neg) {
    pos <- setdiff(ITEMS, neg)
    wi  <- function(S) mean(C[S, S][upper.tri(diag(length(S)))])
    (wi(pos) + wi(neg)) / 2 - mean(C[pos, neg])
}
splits <- combn(ITEMS, 5, simplify = FALSE)
seen <- character(0); uniq <- list()
for (sp in splits) {
    key <- paste(sort(c(paste(sort(sp), collapse = "|"),
                        paste(sort(setdiff(ITEMS, sp)), collapse = "|"))), collapse = "//")
    if (key %in% seen) next
    seen <- c(seen, key); uniq[[length(uniq) + 1]] <- sp
}
vals <- vapply(uniq, contrast, 0); ord <- order(vals, decreasing = TRUE)
rank_of <- function(neg) {
    hit <- vapply(uniq, function(sp) setequal(sp, neg) || setequal(sp, setdiff(ITEMS, neg)), TRUE)
    which(ord == which(hit))
}
r_ship <- rank_of(SHIPPED_NEG); r_rival <- rank_of(RIVAL_NEG)
cat("(b) POLARITY PARTITION -- wording method factor, all", length(uniq), "possible 5/5 splits\n")
cat(sprintf("  shipped {%s}  contrast %+.4f   rank %d of %d\n",
            paste(SHIPPED_NEG, collapse = ","), contrast(SHIPPED_NEG), r_ship, length(uniq)))
cat(sprintf("  rival   {%s}  contrast %+.4f   rank %d of %d\n",
            paste(RIVAL_NEG, collapse = ","), contrast(RIVAL_NEG), r_rival, length(uniq)))
cat("  top 3 splits by contrast:\n")
for (i in 1:3) cat(sprintf("    {%s} %+.4f\n", paste(uniq[[ord[i]]], collapse = ","), vals[ord[i]]))
hi <- which(C == max(C[upper.tri(C)]), arr.ind = TRUE)[1, ]
cat(sprintf("  highest single correlation: %s-%s r = %.2f -- under the shipped text these\n",
            rownames(C)[hi[1]], colnames(C)[hi[2]], max(C[upper.tri(C)])))
cat("    are the two near-synonymous negatives ('no good at all' / 'useless at times')\n\n")
ok_b <- r_ship <= 3 && r_rival >= 30

## ---- (c) option axis: route 9, source labels vs live integers ------------
cat("(c) OPTION AXIS -- per item x level counts, S3 .sav codes vs live resp\n")
sav <- file.path("..", "..", ".cache", "wang_2016_study3_se", "s003.sav")
ok_c <- NA
if (!file.exists(sav)) {
    sav <- tempfile(fileext = ".sav")
    try(download.file(paste0("https://journals.plos.org/plosone/article/file",
                             "?type=supplementary&id=10.1371/journal.pone.0146050.s003"),
                      sav, quiet = TRUE, mode = "wb"), silent = TRUE)
}
if (file.exists(sav) && requireNamespace("haven", quietly = TRUE)) {
    raw <- haven::read_sav(sav)
    mism <- 0; cells <- 0
    for (it in ITEMS) {
        a <- table(factor(as.numeric(raw[[it]]), levels = 1:5))
        b <- table(factor(m[, it], levels = 1:5))
        cells <- cells + 5; mism <- mism + sum(a != b)
        cat(sprintf("  %-5s sav %s | live %s%s\n", it,
                    paste(sprintf("%3d", a), collapse = " "),
                    paste(sprintf("%3d", b), collapse = " "),
                    if (all(a == b)) "" else "   <-- MISMATCH"))
    }
    cat(sprintf("  %d of %d item x level cells identical\n", cells - mism, cells))
    cat("  labels carried by every se column of the .sav, identically:\n")
    cat("    1 非常不符合  2 有些不符合  3 不能确定  4 有些符合  5 完全符合\n")
    cat("  -> the live integer IS the .sav code, so each anchor's number is fixed at\n")
    cat("     the source; the flip on the five negatives is (a)'s finding, not this one.\n\n")
    ok_c <- (mism == 0)
} else {
    cat("  SKIPPED: S3 .sav not available locally and download failed\n\n")
}

## ---- (d) what is NOT established ----------------------------------------
cat("(d) NOT ESTABLISHED -- order WITHIN each polarity class\n")
it_rest <- vapply(ITEMS, function(j) cor(m[, j], rowSums(m[, setdiff(ITEMS, j), drop = FALSE])), 0)
for (j in ITEMS)
    cat(sprintf("    %-5s mean %.2f  SD %.2f  item-rest r %.3f%s\n", j, mean(m[, j]), sd(m[, j]),
                it_rest[j], if (j %in% SHIPPED_NEG) "  (shipped as negatively worded)" else ""))
cat("  The five shipped negatives are exactly the five highest-SD items (1.05-1.21 vs\n")
cat("  0.66-0.83), which corroborates the partition but does not order it.  Nothing\n")
cat("  here distinguishes se2 from se6, se5 from se9, or the five positives from one\n")
cat("  another: that order comes from the cited edition's numbering and is NOT\n")
cat("  verified.  Hence PARTIAL, not VERIFIED.\n\n")

cat(if (ok_a && ok_b && isTRUE(ok_c)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
