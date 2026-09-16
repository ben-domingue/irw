# verify_xiong_2025_dass21.R -- Step 5b re-runnable evidence.
#
# CLAIM UNDER TEST: item code DASS_n carries canonical DASS-21 item n's wording.
# The falsifiable consequence is the DASS-21's published, fixed item-number ->
# subscale assignment, which Xiong et al. (2025) restate for this very study:
#   Depression 3,5,10,13,16,17,21 | Anxiety 2,4,7,9,15,19,20 | Stress 1,6,8,11,12,14,18
# Two predictions follow, and both are checked here:
#   (a) Cronbach's alpha of each canonical subscale must reproduce the alphas the
#       paper publishes for the DASS-21 (Results: D=.826, A=.752, S=.849, total=.918).
#   (b) same-subscale items must intercorrelate more than cross-subscale items,
#       and the canonical partition must beat random 7/7/7 partitions of the same
#       21 items.
# A permuted item->text mapping breaks both. (This is NOT a re-check of item
# counts -- validate_items.R already did that.)

suppressMessages(library(irw))
set.seed(20260916)

TABLE <- "xiong_2025_dass21"
PUB <- c(D = 0.826, A = 0.752, S = 0.849)   # paper Results, DASS-21, combined n=864
PUB_TOTAL <- 0.918
GRP <- list(D = c(3,5,10,13,16,17,21), A = c(2,4,7,9,15,19,20), S = c(1,6,8,11,12,14,18))

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp); d$id <- as.character(d$id); d$item <- as.character(d$item)
ids <- sort(unique(d$id)); its <- paste0("DASS_", 1:21)
M <- matrix(NA_real_, length(ids), 21, dimnames = list(ids, its))
M[cbind(match(d$id, ids), match(d$item, its))] <- d$resp
M <- M[stats::complete.cases(M), , drop = FALSE]
cat("respondents with complete DASS-21:", nrow(M), "\n\n")

alpha <- function(cols) {
    X <- M[, cols, drop = FALSE]; k <- ncol(X)
    k/(k-1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
}

cat("-- (a) Cronbach's alpha, canonical subscales vs published --\n")
cat(sprintf("%-12s %10s %10s %8s\n", "subscale", "published", "observed", "diff"))
obs <- numeric(3); names(obs) <- names(GRP)
for (g in names(GRP)) {
    obs[g] <- alpha(paste0("DASS_", GRP[[g]]))
    cat(sprintf("%-12s %10.3f %10.3f %8.3f\n", g, PUB[g], obs[g], obs[g] - PUB[g]))
}
tot <- alpha(its)
cat(sprintf("%-12s %10.3f %10.3f %8.3f\n", "total(21)", PUB_TOTAL, tot, tot - PUB_TOTAL))
dev_can <- sum(abs(obs - PUB))
cat(sprintf("summed |deviation| for the canonical partition: %.4f\n\n", dev_can))

C <- stats::cor(M)
block <- function(parts) {
    lab <- integer(21); for (i in seq_along(parts)) lab[parts[[i]]] <- i
    w <- b <- c()
    for (i in 1:20) for (j in (i+1):21)
        if (lab[i] == lab[j]) w <- c(w, C[i,j]) else b <- c(b, C[i,j])
    mean(w) - mean(b)
}
blk_can <- block(GRP)
cat("-- (b) block structure: mean within-subscale r minus mean cross-subscale r --\n")
cat(sprintf("canonical partition: %.4f\n", blk_can))

B <- 5000; rb <- rd <- numeric(B)
for (s in 1:B) {
    p <- split(sample(1:21), rep(1:3, each = 7))
    rb[s] <- block(p)
    a <- sapply(p, function(g) alpha(paste0("DASS_", g)))
    rd[s] <- sum(abs(a - PUB))
}
cat(sprintf("%d random 7/7/7 partitions: block max %.4f, median %.4f; beating canonical: %d/%d\n",
            B, max(rb), median(rb), sum(rb >= blk_can), B))
cat(sprintf("%d random 7/7/7 partitions: alpha-dev min %.4f, median %.4f; matching published as well: %d/%d\n\n",
            B, min(rd), median(rd), sum(rd <= dev_can), B))

# Route 7, marker items: DASS-21 10 ("nothing to look forward to") and 21 ("life
# was meaningless") are the instrument's severest depression items and must sit at
# the floor in a non-clinical student sample.
mu <- colMeans(M)
cat("-- marker items: the two lowest item means of the 21 --\n")
print(round(sort(mu)[1:3], 3))
markers_ok <- all(names(sort(mu)[1:2]) %in% c("DASS_10", "DASS_21"))
cat("DASS_10 and DASS_21 are the two lowest:", markers_ok, "\n\n")

cat("Does NOT establish: the order of the seven items WITHIN each subscale.\n",
    "Those rest on the DASS-21's published item numbering carried by the code suffix,\n",
    "and single cross-subscale swaps of the key are not all excluded (4 of 147 score\n",
    "as well as the canonical key on both criteria). Nor does it touch the\n",
    "option_text<->resp axis, which follows the printed 0-3 anchors on the official\n",
    "DASS21 form and the paper's own 0/3 anchor quotations.\n\n", sep = "")

pass <- dev_can < 0.05 && sum(rd <= dev_can) == 0 && blk_can > 0 &&
        sum(rb >= blk_can) <= 5 && markers_ok
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
