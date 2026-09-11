# verify_schalet_2016_hrsa.R -- Step 5b mapping check for schalet_2016_hrsa.
#
# Claim: IRW item aNN (renamed from the .sav's hrsaNN / h08aNN by
# data/schalet_2016_paroxetine.py, a number-preserving rename) is Hamilton
# Anxiety Rating Scale item NN in the canonical Hamilton (1959) order, so
# a01 = Anxious mood ... a14 = Behavior at interview.
#
# Two routes, both using only live IRW data plus hard-coded published values:
#
#  (A) Route 3 -- published subscale totals. Schalet et al. (2016) PLOS ONE
#      Table 1 assigns HRSA items 1,3,5,6 to the psychological subscale and
#      2,4,7-14 to the somatic subscale (their SPSS syntax, S1 Data Syntax,
#      computes HRSAPSY = MEAN(HRSA01,HRSA03,HRSA05,HRSA06)). Table 2 prints
#      POMP mean/SD for total, psychological and somatic subscales, by arm and
#      wave, on the 131 completers (45 placebo, 86 paroxetine). We recompute all
#      12 cells x (mean, SD) and also try every single psych<->somatic swap to
#      show the table would reject it.
#
#  (B) Convergent validity against the sibling HRSD and BAI tables from the same
#      trial: for each of 10 HRSA items with an unambiguous content twin on the
#      other instruments, the twin must correlate more with the predicted HRSA
#      item than with any of the other 13 HRSA items.
#
# What this does NOT establish: route (A) pins subscale membership only, and
# route (B) has no discriminating partner for items 3 (Fears), 5 (Intellectual),
# 7 (Somatic muscular) and 8 (Somatic sensory). So the order WITHIN the pair
# {a03, a05} (both psychological) and WITHIN the pair {a07, a08} (both somatic)
# is not separated by any number here -- it rests on the paper's own item
# numbering and on semantic plausibility (a03 Fears intake mean 0.37 vs a05
# Intellectual 1.83; a07 muscular 1.04 vs a08 sensory 0.53).

suppressMessages(library(irw))

TABLE <- "schalet_2016_hrsa"
a  <- as.data.frame(irw::irw_fetch(TABLE))
d  <- as.data.frame(irw::irw_fetch("schalet_2016_hrsd"))
b  <- as.data.frame(irw::irw_fetch("schalet_2016_bai"))

wide <- function(x) {
    x$key <- paste(x$id, x$wave)
    w <- reshape(x[, c("key", "id", "wave", "item", "resp")], idvar = c("key", "id", "wave"),
                 timevar = "item", direction = "wide")
    names(w) <- sub("^resp\\.", "", names(w))
    w
}
A <- wide(a); D <- wide(d); B <- wide(b)
trt <- unique(a[, c("id", "treat")])

# ---- completer set: reproduces the .sav's all_have flag (131 = 45 + 86) ----
cnt <- function(x, w) { y <- x[x$wave == w, ]; tapply(!is.na(y$resp), y$id, sum) }
ids <- unique(a$id)
g <- function(x, w) { v <- cnt(x, w)[as.character(ids)]; v[is.na(v)] <- 0; v }
comp <- ids[g(a, 0) == 14 & g(a, 1) == 14 & g(d, 0) > 0 & g(d, 1) > 0 & g(b, 0) >= 10 & g(b, 1) >= 10]
cat(sprintf("completers: %d (placebo %d, paroxetine %d); published 131 (45, 86)\n",
            length(comp), sum(trt$treat[trt$id %in% comp] == 0), sum(trt$treat[trt$id %in% comp] == 1)))

# ---- (A) Table 2 POMP scores --------------------------------------------------
PUB <- data.frame(
    scale = rep(c("total", "psych", "somatic"), each = 4),
    arm   = rep(c(0, 1, 0, 1), 3),
    wave  = rep(c(0, 0, 1, 1), 3),
    mean  = c(30.8, 28.8, 20.7, 16.3,  40.7, 39.3, 26.3, 19.3,  26.9, 24.6, 18.4, 15.2),
    sd    = c(10.1,  9.3, 11.5, 10.0,  11.4, 10.7, 15.1, 14.6,  10.9, 10.8, 11.6, 10.0))
it <- function(k) sprintf("a%02d", k)
PSY <- c(1, 3, 5, 6); SOM <- setdiff(1:14, PSY)
Ac <- merge(A[A$id %in% comp, ], trt, by = "id")

pomp_dev <- function(psy, som, show = FALSE) {
    sets <- list(total = 1:14, psych = psy, somatic = som)
    worst <- 0
    for (r in seq_len(nrow(PUB))) {
        s <- Ac[Ac$treat == PUB$arm[r] & Ac$wave == PUB$wave[r], it(sets[[PUB$scale[r]]]), drop = FALSE]
        p <- rowMeans(s) * 100 / 4
        m <- round(mean(p), 1); sdv <- round(sd(p), 1)
        worst <- max(worst, abs(m - PUB$mean[r]), abs(sdv - PUB$sd[r]))
        if (show) cat(sprintf("%-8s arm=%d wave=%d  mean %5.1f (pub %5.1f)  SD %5.1f (pub %5.1f)\n",
                              PUB$scale[r], PUB$arm[r], PUB$wave[r], m, PUB$mean[r], sdv, PUB$sd[r]))
    }
    worst
}
cat("\n(A) Table 2 POMP, shipped subscale assignment psych = a01,a03,a05,a06\n")
wA <- pomp_dev(PSY, SOM, show = TRUE)
cat(sprintf("largest deviation (rounded to 0.1): %.2f\n", wA))

swaps <- expand.grid(x = PSY, y = SOM)
sw <- mapply(function(x, y) pomp_dev(replace(PSY, PSY == x, y), replace(SOM, SOM == y, x)), swaps$x, swaps$y)
cat(sprintf("all %d single psych<->somatic swaps: smallest max deviation %.2f (swap a%02d<->a%02d)\n",
            length(sw), min(sw), swaps$x[which.min(sw)], swaps$y[which.min(sw)]))
okA <- wA <= 0.15 && min(sw) > 0.15

# ---- (B) convergent twins on HRSD / BAI -----------------------------------------
Dc <- D[, c("id", "wave", "d01", "d04", "d05", "d06", "d09", "d10", "d14")]
Bc <- B[, c("id", "wave", sprintf("bai%02d", c(4, 7, 11, 15, 18, 20, 21)))]
M <- merge(merge(A, Dc, by = c("id", "wave")), Bc, by = c("id", "wave"))
twin <- list(
    a01 = "d10",                      # Anxious mood        <- HRSD Anxiety psychic
    a02 = "bai04",                    # Tension             <- BAI unable to relax
    a04 = c("d04", "d05", "d06"),     # Insomnia            <- HRSD insomnia early/middle/late
    a06 = "d01",                      # Depressed mood      <- HRSD Depressed mood
    a09 = "bai07",                    # Cardiovascular      <- BAI heart pounding/racing
    a10 = c("bai11", "bai15"),        # Respiratory         <- BAI choking, difficulty breathing
    a11 = "bai18",                    # Gastrointestinal    <- BAI indigestion
    a12 = "d14",                      # Genitourinary       <- HRSD Genital symptoms (libido)
    a13 = c("bai20", "bai21"),        # Autonomic           <- BAI face flushed, sweating
    a14 = "d09")                      # Behavior at interview <- HRSD Agitation
cat("\n(B) twin composite: r with predicted item vs best other HRSA item (pooled waves)\n")
hits <- 0
for (k in names(twin)) {
    comp_k <- rowSums(M[, twin[[k]], drop = FALSE])
    r <- sapply(it(1:14), function(j) cor(M[[j]], comp_k, use = "pairwise.complete.obs"))
    other <- r[names(r) != k]
    ok <- r[k] > max(other)
    hits <- hits + ok
    cat(sprintf("%-4s <- %-14s r=%.2f | best other %s r=%.2f  %s\n", k, paste(twin[[k]], collapse = "+"),
                r[k], names(other)[which.max(other)], max(other), if (ok) "ok" else "MISS"))
}
cat(sprintf("twin argmax hits: %d/%d\n", hits, length(twin)))
okB <- hits == length(twin)

cat("\nNot established: order within {a03 Fears, a05 Intellectual} and within {a07 Somatic muscular,\n",
    "a08 Somatic sensory}; those rest on the paper's item numbering (Table 1) only.\n", sep = "")
cat(if (okA && okB && length(comp) == 131) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
