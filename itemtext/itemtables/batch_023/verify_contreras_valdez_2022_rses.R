# verify_contreras_valdez_2022_rses.R
#
# STATUS: this table is BLOCKED on the item-text rights rule (irw#1891); no
# __items.csv was written. This script therefore does not verify a shipped
# mapping -- it re-runs, so a later attempt does not have to rebuild it, the
# evidence that the IRW item codes rses_i01..rses_i10 correspond to items 1..10
# of the administered Mexican Spanish RSES as printed in Amaya Hernandez (2013),
# UNAM doctoral thesis, TESIUNAM 0704071, Apendice B -- and, separately, that the
# stored response scale runs OPPOSITE to the anchors the deposit's Keys sheet
# prints.
#
# THE CLAIM UNDER TEST
#   rses_iNN == item NN of Amaya's Apendice B, whose polarity structure is
#       positively worded : 1, 3, 4, 7, 10
#       negatively worded : 2, 5, 6, 9
#       deviant           : 8 ("Desearia respetarme mas a mi mismo(a)",
#                              loading -.011 on her positive factor, .224 on her
#                              negative factor)
#   and resp 4 == agreement, not disagreement.
#
# THE FALSIFIABLE PREDICTIONS
#   P1 (route 6, keying polarity). The correlation matrix must split into
#      exactly those two classes with no sign overlap, and rses_i08 must sit
#      outside both.
#   P2 (route 3, stored subscale totals). The S1 file carries rses_pse
#      ("Positive Self-Esteem factor score") and rses_nse ("Negative Self-Esteem
#      factor score"), both described in its Keys sheet as arithmetic sums, and
#      the paper says the 8-item two-factor model of Jurado Cardenas et al.
#      (5 + 3 items) was used. So exactly one of the choose(10,5)=252 five-column
#      subsets may reproduce rses_pse and exactly one of the choose(10,3)=120
#      three-column subsets may reproduce rses_nse, and they must be the Amaya
#      positive class and a subset of the Amaya negative class.
#   P3 (direction). The paper states the EDE-Q scores correlate negatively with
#      Positive Self-Esteem and positively with Negative Self-Esteem. Given P2,
#      that sign pattern holds only if a HIGH value on the positively worded
#      items means agreement -- i.e. 4 = totalmente de acuerdo, the reverse of
#      the Keys sheet.
#
# What it does NOT establish: order WITHIN either polarity class. Swapping
# rses_i03 with rses_i04 leaves every number below unchanged; that part of the
# mapping rests on Amaya's printed 1-10 numbering alone.
#
# Data: the PLOS ONE S1 file, which is the source the IRW table was built from
# (data/contreras_valdez_2022_edeq_battery.py). No Redivis export needed.

suppressMessages({library(readxl); library(utils)})

SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0266507.s001")
tmp <- tempfile(fileext = ".xlsx")
utils::download.file(SI, tmp, quiet = TRUE, mode = "wb")
d <- as.data.frame(readxl::read_excel(tmp, sheet = "Data"))
d <- d[d$study == 2, ]                       # the RSES was Study 2 only

R    <- sprintf("rses_i%02d", 1:10)
POS  <- sprintf("rses_i%02d", c(1, 3, 4, 7, 10))   # Amaya: positively worded
NEG  <- sprintf("rses_i%02d", c(2, 5, 6, 9))       # Amaya: negatively worded
DEV  <- "rses_i08"                                 # Amaya: the deviant item

X <- d[, R]
X[X == 8 | X == 9] <- NA                     # 8 = not in this study, 9 = missing
X <- X[stats::complete.cases(X), ]
cat(sprintf("complete cases: %d\n\n", nrow(X)))

## ---- P1: keying polarity -------------------------------------------------
C <- stats::cor(X)
rng <- function(a, b) {
    v <- C[a, b, drop = FALSE]
    v <- if (identical(a, b)) v[upper.tri(v)] else as.vector(v)
    sprintf("%+.3f to %+.3f", min(v), max(v))
}
cat("P1 keying polarity\n")
cat(sprintf("  within positive class {%s}: r %s\n",
            paste(sub("rses_i0?", "", POS), collapse = ","), rng(POS, POS)))
cat(sprintf("  within negative class {%s}: r %s\n",
            paste(sub("rses_i0?", "", NEG), collapse = ","), rng(NEG, NEG)))
cat(sprintf("  across the two classes      : r %s\n", rng(POS, NEG)))
others <- setdiff(R, DEV)
dev_max <- max(abs(C[DEV, others]))
off <- abs(C[others, others]); off <- off[upper.tri(off)]
cat(sprintf("  rses_i08 largest |r| with any item: %.3f ; smallest |r| among all other pairs: %.3f\n",
            dev_max, min(off)))
p1 <- min(C[POS, POS][upper.tri(C[POS, POS])]) > 0 &&
      min(C[NEG, NEG][upper.tri(C[NEG, NEG])]) > 0 &&
      max(C[POS, NEG]) < 0 &&
      dev_max < min(off)
cat(sprintf("  P1: %s\n\n", if (p1) "PASS" else "FAIL"))

## ---- P2: stored subscale totals ------------------------------------------
Y <- d[, c(R, "rses_pse", "rses_nse")]
Y[, R][Y[, R] == 8 | Y[, R] == 9] <- NA
Y <- Y[stats::complete.cases(Y), ]
hits <- function(k, target) {
    out <- list()
    for (cmb in utils::combn(R, k, simplify = FALSE))
        if (all(rowSums(Y[, cmb, drop = FALSE]) == Y[[target]])) out[[length(out) + 1L]] <- cmb
    out
}
h5 <- hits(5, "rses_pse"); h3 <- hits(3, "rses_nse")
cat("P2 stored subscale totals\n")
cat(sprintf("  subsets of size 5 reproducing rses_pse: %d of %d  -> %s\n",
            length(h5), ncol(utils::combn(10, 5)),
            if (length(h5)) paste(h5[[1]], collapse = ", ") else "none"))
cat(sprintf("  subsets of size 3 reproducing rses_nse: %d of %d  -> %s\n",
            length(h3), ncol(utils::combn(10, 3)),
            if (length(h3)) paste(h3[[1]], collapse = ", ") else "none"))
p2 <- length(h5) == 1 && length(h3) == 1 &&
      setequal(h5[[1]], POS) && all(h3[[1]] %in% NEG)
cat(sprintf("  expected: pse == the Amaya positive class, nse subset of the Amaya negative class\n"))
cat(sprintf("  P2: %s\n\n", if (p2) "PASS" else "FAIL"))

## ---- P3: direction of the response scale ---------------------------------
Z <- d[, c(R, "edeq14_overall")]
Z[, R][Z[, R] == 8 | Z[, R] == 9] <- NA
Z <- Z[stats::complete.cases(Z), ]
pse <- rowSums(Z[, POS]); nse <- rowSums(Z[, sprintf("rses_i%02d", c(2, 6, 9))])
r_p <- stats::cor(pse, Z$edeq14_overall); r_n <- stats::cor(nse, Z$edeq14_overall)
cat("P3 direction (paper: EDE-Q correlates negatively with Positive Self-Esteem, positively with Negative)\n")
cat(sprintf("  cor(sum of positively worded items, edeq14_overall) = %+.3f\n", r_p))
cat(sprintf("  cor(sum of negatively worded items, edeq14_overall) = %+.3f\n", r_n))
cat(sprintf("  item means, positive class: %s\n",
            paste(sprintf("%s=%.2f", POS, colMeans(X[, POS])), collapse = "  ")))
cat(sprintf("  item means, negative class: %s\n",
            paste(sprintf("%s=%.2f", NEG, colMeans(X[, NEG])), collapse = "  ")))
p3 <- r_p < 0 && r_n > 0
cat("  Under the Keys sheet's printed anchors (1 = totalmente de acuerdo) these means would say a\n")
cat("  general-population sample agrees it is useless and a failure and denies having good qualities.\n")
cat(sprintf("  P3: %s -> stored scale is 1 = totalmente en desacuerdo .. 4 = totalmente de acuerdo\n\n",
            if (p3) "PASS" else "FAIL"))

cat("NOTE: none of the three routes orders items WITHIN a polarity class; that rests on\n")
cat("Amaya Hernandez (2013) Apendice B's printed 1-10 numbering. Status is PARTIAL, not VERIFIED.\n")
cat(if (p1 && p2 && p3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
