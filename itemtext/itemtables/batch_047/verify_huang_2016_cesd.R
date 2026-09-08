# verify_huang_2016_cesd.R -- Step 5b re-runnable evidence.
#
# CLAIM 1 (option axis / direction): huang_2016_cesd stores CESD_4, CESD_8,
#   CESD_12 and CESD_16 ALREADY REVERSE SCORED, so the four positively worded
#   CES-D items ship their frequency anchors in reverse order (resp 0 = "Most or
#   all of the time"), while the other sixteen ship them ascending (resp 0 =
#   "Rarely or none of the time", per Huang et al. 2016 Measures).
#   FALSIFIABLE PREDICTION: the plain sum of the 20 stored items must reproduce
#   the authors' own CES-D total (the CESD variable in the S1 .sav) respondent by
#   respondent; if the items were stored raw, reversing 4/8/12/16 before summing
#   would be what reproduces it instead. Only one of the two can be right.
#
# CLAIM 2 (item axis): the codes CESD_1..CESD_20 are the canonical Radloff (1977)
#   item numbers, so CESD_4 = "I felt I was just as good as other people",
#   CESD_8 = "I felt hopeful about the future", CESD_12 = "I was happy",
#   CESD_16 = "I enjoyed life" -- the CES-D positive-affect factor -- and the
#   other sixteen are the negatively worded items.
#   FALSIFIABLE PREDICTION: the positive-affect quadruple carries a large,
#   well-replicated common factor (reinforced by a reverse-wording method
#   factor), so each of those four codes must have the other three as its three
#   strongest correlates in the live data. A permutation of the shipped text onto
#   other codes would move that signature off {4,8,12,16}.
#
# CLAIM 3 (marker item, route 7): CESD_17 = "I had crying spells" must be the
#   least endorsed item in a low-symptom community sample.
#
# WHAT THIS DOES NOT ESTABLISH: claims 2 and 3 separate the positive-affect
# quadruple from the other sixteen as SETS and pin one marker item. They do NOT
# order the four positively worded items among themselves, nor the sixteen
# negatively worded ones. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "huang_2016_cesd"
ALL   <- paste0("CESD_", 1:20)
POS   <- paste0("CESD_", c(4, 8, 12, 16))

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", ALL)]
w <- w[complete.cases(w), ]
cat(sprintf("complete cases in live data: %d\n", nrow(w)))

## ---- CLAIM 1: direction, against the authors' own total ----------------
SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0157238.s001")
tf <- tempfile(fileext = ".sav")
ok <- tryCatch({ download.file(SI, tf, quiet = TRUE); TRUE }, error = function(e) FALSE)
claim1 <- NA
if (ok) {
    sav <- as.data.frame(haven::read_sav(tf))
    sav$id <- suppressWarnings(as.integer(as.numeric(sav$Code)))
    key <- sav[!is.na(sav$id) & !is.na(sav$CESD), c("id", "CESD")]
    m <- merge(w, key, by = "id")
    as_stored <- rowSums(m[, ALL])
    flipped   <- as_stored + rowSums(3 - m[, POS]) - rowSums(m[, POS])
    n_stored  <- sum(as_stored == m$CESD)
    n_flipped <- sum(flipped   == m$CESD)
    cat(sprintf("\nCLAIM 1  respondents matched to the .sav CES-D total: %d\n", nrow(m)))
    cat(sprintf("  sum of items AS STORED equals the authors' total : %d\n", n_stored))
    cat(sprintf("  sum after reversing 4/8/12/16 equals it          : %d\n", n_flipped))
    cat(sprintf("  mean total as stored %.2f vs authors' %.2f (flipped reading %.2f)\n",
                mean(as_stored), mean(m$CESD), mean(flipped)))
    claim1 <- n_stored > n_flipped && n_stored >= 0.9 * nrow(m)
} else {
    cat("\nCLAIM 1  SKIPPED: could not download the PLOS S1 .sav\n")
}

## ---- CLAIM 2: positive-affect block structure --------------------------
# The CES-D is dominated by a general severity factor, so raw correlations alone
# are underpowered (route 5's known limitation). Remove the first principal
# component and test the residual structure, where the positive-affect /
# reverse-wording method factor is what is left.
Z <- scale(as.matrix(w[, ALL]))
sv <- svd(Z)
resid <- Z - sv$u[, 1] %o% sv$v[, 1] * sv$d[1]
R <- cor(resid)
dimnames(R) <- list(ALL, ALL)
cat("\nCLAIM 2  three strongest RESIDUAL correlates of each positive-affect code\n")
claim2a <- TRUE
for (it in POS) {
    s4 <- sort(R[it, setdiff(ALL, it)], decreasing = TRUE)
    top3 <- names(s4)[1:3]
    hit <- setequal(top3, setdiff(POS, it))
    claim2a <- claim2a && hit
    cat(sprintf("  %-8s %s | next %s=%.2f  %s\n", it,
                paste(sprintf("%s=%.2f", top3, s4[1:3]), collapse = "  "),
                names(s4)[4], s4[4],
                if (hit) "= the other three claimed positive items" else "MISS"))
}
subs <- combn(ALL, 4, simplify = FALSE)
sc <- sapply(subs, function(s) mean(R[s, s][upper.tri(R[s, s])]))
ord <- order(-sc)
rk <- which(sapply(subs[ord], function(s) setequal(s, POS)))
cat(sprintf("  mean residual r within {4,8,12,16}: %.3f\n",
            mean(R[POS, POS][upper.tri(R[POS, POS])])))
cat(sprintf("  best rival 4-subset {%s}: %.3f\n",
            paste(subs[[ord[if (rk == 1) 2 else 1]]], collapse = ","),
            sc[ord[if (rk == 1) 2 else 1]]))
cat(sprintf("  rank of {4,8,12,16} by mean residual within-r among all %d 4-subsets: %d\n",
            length(subs), as.integer(rk)))
claim2 <- claim2a && rk == 1

## ---- CLAIM 3: marker item ---------------------------------------------
mns <- colMeans(w[, ALL])
cat("\nCLAIM 3  per-item means (ascending)\n")
print(round(sort(mns), 3))
claim3 <- names(which.min(mns)) == "CESD_17"
cat(sprintf("  least endorsed item: %s (claim: CESD_17, 'I had crying spells')\n",
            names(which.min(mns))))

cat("\nNote: this pins the positive-affect quadruple as a SET, the storage direction,\n",
    "and one marker item; it does not order items within either polarity block.\n", sep = "")

pass <- isTRUE(claim2) && isTRUE(claim3) && (is.na(claim1) || isTRUE(claim1))
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
