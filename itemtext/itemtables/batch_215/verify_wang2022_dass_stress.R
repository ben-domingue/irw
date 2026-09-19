# verify_wang2022_dass_stress.R
#
# CLAIM UNDER TEST (Step 5b), in two parts.
#
#  (a) WHICH DEPOSIT COLUMN EACH LIVE ITEM IS.  The shipped mapping says
#      dass_str_1..7 are, in order, columns DASS1, DASS6, DASS8, DASS11, DASS12,
#      DASS14, DASS18 of the study's own deposit (figshare 19158812,
#      Data Sheet 1 .xlsx, CC BY 4.0), i.e. the seven canonical DASS-21 STRESS
#      positions in ascending order.  That is falsifiable: each live item's
#      (n, mean, sd) must reproduce the claimed deposit column's, and must do so
#      more closely than any of the other 20 DASS columns.  Any permutation of
#      the seven live codes across those columns breaks it.
#
#  (b) WHICH SUBSCALE THE SEVEN ITEMS ARE.  The shipped item_text is the canonical
#      DASS-21 stress wording, which requires that {DASS1,6,8,11,12,14,18} really
#      is the stress block of this administration.  Two independent predictions:
#        (b1) Cronbach's alpha over the canonical depression / anxiety / stress
#             triples must reproduce the three alphas the paper publishes --
#             0.87 / 0.84 / 0.86 (Wang et al. 2022, Front. Psychiatry 13:827519,
#             Measures) -- each to its own value, the stress one to 0.86.
#        (b2) The paper's Table 1 prints the STRESS subscale item-mean +/- SD by
#             gender (0.62 +/- 0.67 male, 0.76 +/- 0.72 female) and by grade
#             (0.62 +/- 0.60 grade 7, 0.78 +/- 0.81 grade 8).  Computing the same
#             four cells from this block against the deposit's own demographic
#             columns must reproduce them.  A different 7-item block would not.
#
#  WHAT THIS DOES NOT ESTABLISH, hence PARTIAL: that the deposit's header numbers
#  DASS1..DASS21 follow the canonical DASS-21 item order WITHIN the stress
#  subscale.  (b) pins the block, (a) pins each live code to one deposit column,
#  but which canonical stress sentence "DASS6" carries (as against DASS8, DASS11,
#  ...) rests on the header's numbering convention, which nothing in the deposit
#  or the paper states, and the paper publishes no per-item statistics.  The
#  within-subscale content split (irritability {6,11,14,18} vs tension/relaxation
#  {1,8,12}) is printed for the record and is NOT part of the verdict: the block
#  is single-factor dominated (all within-block r are 0.33-0.58) and the content
#  split ranks 33rd of the 35 possible 4/3 splits -- no evidence either way.

suppressMessages({library(irw); library(readxl)})

TABLE <- "wang2022_dass_stress"
CLAIM <- c(dass_str_1 = 1, dass_str_2 = 6, dass_str_3 = 8, dass_str_4 = 11,
           dass_str_5 = 12, dass_str_6 = 14, dass_str_7 = 18)
PUB_ALPHA <- c(depression = 0.87, anxiety = 0.84, stress = 0.86)   # paper, Measures
CANON <- list(depression = c(3,5,10,13,16,17,21),
              anxiety    = c(2,4,7,9,15,19,20),
              stress     = c(1,6,8,11,12,14,18))
# paper Table 1, STRESS column: group item-mean +/- SD
PUB_GROUP <- list(male  = c(0.62, 0.67), female = c(0.76, 0.72),
                  g7    = c(0.62, 0.60), g8     = c(0.78, 0.81))
TOL_ALPHA <- 0.01
TOL_GROUP <- 0.02

## ---- deposit ---------------------------------------------------------------
cache <- file.path("itemtext", ".cache", TABLE)
if (!dir.exists(cache)) cache <- file.path(".cache", TABLE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)
xlsx <- file.path(cache, "data.xlsx")
if (!file.exists(xlsx))
    download.file("https://ndownloader.figshare.com/files/34038791", xlsx, quiet = TRUE)
raw <- suppressMessages(as.data.frame(read_excel(xlsx, sheet = 1)))
D <- sapply(1:21, function(k) suppressWarnings(as.numeric(raw[[paste0("DASS", k)]])))
colnames(D) <- paste0("DASS", 1:21)
cat(sprintf("deposit: %d respondents x 21 DASS columns\n", nrow(D)))

dep_stats <- data.frame(
    col  = colnames(D),
    n    = apply(D, 2, function(x) sum(!is.na(x))),
    mean = apply(D, 2, mean, na.rm = TRUE),
    sd   = apply(D, 2, sd,   na.rm = TRUE), stringsAsFactors = FALSE)

## ---- live ------------------------------------------------------------------
d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
live <- data.frame(
    item = names(CLAIM),
    n    = as.integer(tapply(d$resp, d$item, function(x) sum(!is.na(x)))[names(CLAIM)]),
    mean = as.numeric(tapply(d$resp, d$item, mean)[names(CLAIM)]),
    sd   = as.numeric(tapply(d$resp, d$item, sd)[names(CLAIM)]), stringsAsFactors = FALSE)

## ---- (a) nearest-column test ----------------------------------------------
cat("\n-- (a) live item vs deposit column: (n, mean, sd), and the nearest rival --\n")
cat(sprintf("%-11s %-7s %16s %16s   %-7s %8s  %s\n",
            "item", "claim", "live m (sd)", "dep m (sd)", "rival", "d_rival", "ok"))
ok_a <- TRUE
for (i in seq_len(nrow(live))) {
    it <- live$item[i]; k <- CLAIM[[it]]; cl <- paste0("DASS", k)
    dist <- abs(dep_stats$mean - live$mean[i]) + abs(dep_stats$sd - live$sd[i]) +
            ifelse(dep_stats$n == live$n[i], 0, 1)
    best <- order(dist)[1]; second <- order(dist)[2]
    pass <- dep_stats$col[best] == cl
    ok_a <- ok_a && pass
    cat(sprintf("%-11s %-7s %7.4f(%.4f) %7.4f(%.4f)   %-7s %8.4f  %s\n",
                it, cl, live$mean[i], live$sd[i],
                dep_stats$mean[dep_stats$col == cl], dep_stats$sd[dep_stats$col == cl],
                dep_stats$col[second], dist[second],
                if (pass) "yes" else paste("NO -> nearest is", dep_stats$col[best])))
    if (!identical(live$n[i], dep_stats$n[dep_stats$col == cl]))
        cat(sprintf("    n mismatch: live %d vs deposit %d\n",
                    live$n[i], dep_stats$n[dep_stats$col == cl]))
}
cat(sprintf("all seven live items nearest their claimed column: %s\n", ok_a))

## ---- (b1) subscale alphas --------------------------------------------------
alpha <- function(M) {
    M <- M[complete.cases(M), , drop = FALSE]
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}
cat("\n-- (b1) Cronbach's alpha of the canonical DASS-21 triples in this deposit --\n")
cat(sprintf("%-11s %9s %9s %8s\n", "subscale", "published", "observed", "diff"))
ok_b1 <- TRUE
for (nm in names(CANON)) {
    a <- alpha(D[, paste0("DASS", CANON[[nm]])])
    ok_b1 <- ok_b1 && abs(a - PUB_ALPHA[[nm]]) <= TOL_ALPHA
    cat(sprintf("%-11s %9.2f %9.4f %8.4f\n", nm, PUB_ALPHA[[nm]], a, a - PUB_ALPHA[[nm]]))
}
a_live <- {
    w <- tapply(d$resp, list(as.character(d$id), as.character(d$item)), mean)
    alpha(w[, names(CLAIM), drop = FALSE])
}
cat(sprintf("live %s table, alpha = %.4f (published stress 0.86)\n", TABLE, a_live))
cat(sprintf("all three alphas within %.2f: %s\n", TOL_ALPHA, ok_b1))

## ---- (b2) paper Table 1 group means for the STRESS block -------------------
str_mean <- rowMeans(D[, paste0("DASS", CANON$stress)], na.rm = TRUE)
g  <- raw[["性别"]]      # gender; codes 1/2, labelling resolved below
gr <- raw[["年级"]]      # grade; codes 7/8
# The deposit does not say which gender code is male. Assign by the published
# ordering (male stress mean < female), then check BOTH cells reproduce.
m1 <- mean(str_mean[g == 1]); m2 <- mean(str_mean[g == 2])
male_code <- if (m1 < m2) 1 else 2
cells <- list(
    male   = c(mean(str_mean[g == male_code]),  sd(str_mean[g == male_code])),
    female = c(mean(str_mean[g != male_code]),  sd(str_mean[g != male_code])),
    g7     = c(mean(str_mean[gr == 7]),         sd(str_mean[gr == 7])),
    g8     = c(mean(str_mean[gr == 8]),         sd(str_mean[gr == 8])))
cat("\n-- (b2) paper Table 1, STRESS column: group item-mean +/- SD --\n")
cat(sprintf("(gender code %d read as male, by the published ordering)\n", male_code))
cat(sprintf("%-8s %14s %14s %8s\n", "group", "published", "observed", "d(mean)"))
ok_b2 <- TRUE
for (nm in names(cells)) {
    p <- PUB_GROUP[[nm]]; o <- cells[[nm]]
    ok_b2 <- ok_b2 && abs(o[1] - p[1]) <= TOL_GROUP && abs(o[2] - p[2]) <= TOL_GROUP
    cat(sprintf("%-8s %7.2f (%.2f) %7.2f (%.2f) %8.3f\n", nm, p[1], p[2], o[1], o[2], o[1] - p[1]))
}
cat(sprintf("all four stress cells within %.2f on mean and sd: %s\n", TOL_GROUP, ok_b2))

## ---- (c) the underpowered within-subscale test, for the record -------------
A <- D[, paste0("DASS", CANON$stress)]
C <- cor(A, use = "pairwise.complete.obs")
cat(sprintf("\n-- (c) within-stress correlations range %.2f to %.2f --\n",
            min(C[upper.tri(C)]), max(C[upper.tri(C)])))
splits <- combn(7, 4, simplify = FALSE)
sep <- sapply(splits, function(g1) {
    g2 <- setdiff(1:7, g1)
    w <- c(C[g1, g1][upper.tri(C[g1, g1])], C[g2, g2][upper.tri(C[g2, g2])])
    mean(w) - mean(C[g1, g2])
})
idx <- which(sapply(splits, function(g) identical(sort(CANON$stress[g]), c(6, 11, 14, 18))))
cat(sprintf("content split irritability {6,11,14,18} vs tension {1,8,12}: rank %d of %d, separation %.4f (best %.4f)\n",
            rank(-sep)[idx], length(sep), sep[idx], max(sep)))
cat("    Underpowered by design; NOT part of the verdict. See header.\n")

cat(if (ok_a && ok_b1 && ok_b2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
