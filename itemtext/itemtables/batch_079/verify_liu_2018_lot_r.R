# verify_liu_2018_lot_r.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: the deposit's columns Optimism1..Optimism10 are numbered in
# the canonical LOT-R item order (Scheier, Carver & Bridges 1994), i.e. the six
# scored items sit at positions 1,3,4,7,9,10 (positive 1,4,10; negative 3,7,9)
# and the four unscored fillers at 2,5,6,8 -- and that the three negative items
# are stored ALREADY REVERSE-CODED, which is why their shipped option_text runs
# 1 = "strongly agree" .. 5 = "strongly disagree" while the other seven items run
# the paper's stated 1 = "strongly disagree" .. 5 = "strongly agree".
#
# Three independent checks, all computed from the LIVE IRW table (the S2 workbook
# is used only for the SEM parcel columns, which IRW does not carry):
#   A. parcel reconstruction -- LOT_R_1/2/3 in the authors' own workbook are the
#      pairwise means of {1,9}, {3,4}, {7,10}; that names the scored six exactly.
#   B. Cronbach's alpha of those six, live, against the paper's published .65.
#   C. polarity block structure -- of the 10 ways to split the six into two
#      triples, the canonical {1,4,10} / {3,7,9} split should maximise
#      (within-block r - cross-block r).
#
# What this does NOT establish: the order WITHIN each polarity class (1 vs 4 vs
# 10, and 3 vs 7 vs 9) and the order among the four fillers (2, 5, 6, 8). Those
# eight items are pinned only to a class, not to a position. Status is PARTIAL.

suppressMessages(library(irw))

TABLE <- "liu_2018_lot_r"
S2 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0194559.s002")
PUBLISHED_ALPHA <- 0.65   # Liu et al. 2018, Measures: "the Cronbach's alpha
                          # coefficient was .65 for the 6-item LOT-R"
items <- paste0("Optimism", 1:10)
scored <- paste0("Optimism", c(1, 3, 4, 7, 9, 10))
pos <- paste0("Optimism", c(1, 4, 10)); neg <- paste0("Optimism", c(3, 7, 9))

d <- irw::irw_fetch(TABLE)
W <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(W) <- sub("^resp\\.", "", names(W))
W <- W[order(W$id), ]
cat(sprintf("live table: %d respondents x %d items\n", nrow(W), length(items)))

tf <- tempfile(fileext = ".xlsx")
download.file(S2, tf, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tf))
raw <- raw[order(raw$Serial_number), ]
stopifnot(identical(as.integer(raw$Serial_number), as.integer(W$id)))

# --- A. parcel reconstruction -------------------------------------------------
pairs <- list(LOT_R_1 = c("Optimism1", "Optimism9"),
              LOT_R_2 = c("Optimism3", "Optimism4"),
              LOT_R_3 = c("Optimism7", "Optimism10"))
cat("\nA. SEM parcels in the authors' S2 workbook vs pairwise means of LIVE items\n")
worstA <- 0
for (p in names(pairs)) {
    got <- rowMeans(W[, pairs[[p]]])
    dev <- max(abs(got - raw[[p]]))
    worstA <- max(worstA, dev)
    cat(sprintf("  %-8s = mean(%s, %s)   max|deviation| over %d rows = %.2e\n",
                p, pairs[[p]][1], pairs[[p]][2], nrow(W), dev))
}
# and confirm no OTHER pair or triple reproduces a parcel (uniqueness)
alt <- 0
for (p in names(pairs)) for (k in 2:3)
    for (cmb in combn(items, k, simplify = FALSE))
        if (!setequal(cmb, pairs[[p]]) &&
            max(abs(rowMeans(W[, cmb]) - raw[[p]])) < 1e-6) alt <- alt + 1
cat(sprintf("  competing 2- or 3-item subsets that also reproduce a parcel: %d\n", alt))
okA <- worstA < 1e-6 && alt == 0

# --- B. alpha of the six parcelled items, live --------------------------------
X <- W[, scored]
k <- ncol(X)
alpha <- k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
Xr <- X; Xr[, neg] <- 6 - Xr[, neg]
alpha_unrev <- k / (k - 1) * (1 - sum(apply(Xr, 2, var)) / var(rowSums(Xr)))
cat(sprintf("\nB. alpha of {1,3,4,7,9,10} as stored = %.3f  (paper: %.2f)\n",
            alpha, PUBLISHED_ALPHA))
cat(sprintf("   same six with 3,7,9 un-reversed   = %.3f  -- i.e. the stored\n",
            alpha_unrev))
cat("   values are already reverse-coded, as S1 Table's caption states\n")
okB <- abs(alpha - PUBLISHED_ALPHA) <= 0.01 && alpha_unrev < 0.2

# --- C. polarity block structure ---------------------------------------------
C <- cor(X)
sep <- function(a, b) mean(c(C[a, a][upper.tri(C[a, a])], C[b, b][upper.tri(C[b, b])])) -
                      mean(C[a, b])
res <- do.call(rbind, lapply(combn(scored, 3, simplify = FALSE), function(tri) {
    if (!("Optimism1" %in% tri)) return(NULL)
    oth <- setdiff(scored, tri)
    data.frame(split = paste(sub("Optimism", "", tri), collapse = ","),
               vs = paste(sub("Optimism", "", oth), collapse = ","),
               sep = sep(tri, oth))
}))
res <- res[order(-res$sep), ]
cat("\nC. within-minus-cross mean r, all 10 splits of the scored six\n")
for (i in seq_len(nrow(res)))
    cat(sprintf("  {%s} vs {%s}: %+.3f%s\n", res$split[i], res$vs[i], res$sep[i],
                if (i == 1) "   <- best" else ""))
okC <- res$split[1] == "1,4,10" && (res$sep[1] - res$sep[2]) > 0.05

cat("\nNOT ESTABLISHED by any of the above: which of Optimism1/4/10 is which,\n",
    "which of Optimism3/7/9 is which, and the order of the fillers 2/5/6/8.\n", sep = "")
cat(sprintf("\nA=%s B=%s C=%s\n", okA, okB, okC))
cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
