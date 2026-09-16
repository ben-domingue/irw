# verify_wang2022_dass_anxiety.R
#
# CLAIM UNDER TEST (Step 5b), in two parts.
#
#  (a) WHICH DEPOSIT COLUMN EACH LIVE ITEM IS.  The shipped mapping says
#      dass_anx_1..7 are, in order, columns DASS2, DASS4, DASS7, DASS9, DASS15,
#      DASS19, DASS20 of the study's own deposit (figshare 19158812, Data_Sheet_1
#      ....xlsx, CC BY 4.0), i.e. the seven canonical DASS-21 ANXIETY positions in
#      ascending order.  That is falsifiable: each live item's (n, mean, sd) must
#      reproduce the claimed deposit column's, and must do so more closely than
#      any of the other 20 DASS columns.  A permutation inside the subscale
#      breaks it.
#
#  (b) WHICH SUBSCALE THE SEVEN ITEMS ARE.  The shipped item_text is the canonical
#      DASS-21 anxiety wording, which requires that {DASS2,4,7,9,15,19,20} really
#      is the anxiety block of this administration.  Prediction: Cronbach's alpha
#      over the canonical depression / anxiety / stress triples must reproduce the
#      three alphas the paper publishes -- 0.87 / 0.84 / 0.86 (Wang et al. 2022,
#      Front. Psychiatry 13:827519, Measures) -- each to its own value.
#
#  WHAT THIS DOES NOT ESTABLISH, hence PARTIAL: that the deposit's header numbers
#  DASS1..DASS21 follow the canonical DASS-21 item order WITHIN a subscale.  (b)
#  pins the block, (a) pins live-item-to-column, but which canonical anxiety
#  sentence "DASS2" carries rests on the header's numbering convention, which
#  nothing in the deposit or the paper states.  The within-subscale facet test
#  (somatic {2,4,7,19} vs panic/affect {9,15,20}) is underpowered here and is
#  printed for the record, not used in the verdict: the DASS anxiety subscale is
#  dominated by one factor (all 35 possible 4/3 splits separate by < 0.07), and
#  the canonical split ranks 25th of 35 -- no evidence either way.

suppressMessages({library(irw); library(readxl)})

TABLE <- "wang2022_dass_anxiety"
CLAIM <- c(dass_anx_1 = 2, dass_anx_2 = 4, dass_anx_3 = 7, dass_anx_4 = 9,
           dass_anx_5 = 15, dass_anx_6 = 19, dass_anx_7 = 20)
PUB_ALPHA <- c(depression = 0.87, anxiety = 0.84, stress = 0.86)   # paper, Measures
CANON <- list(depression = c(3,5,10,13,16,17,21),
              anxiety    = c(2,4,7,9,15,19,20),
              stress     = c(1,6,8,11,12,14,18))
TOL_ALPHA <- 0.01

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
cat(sprintf("%-11s %-7s %11s %11s   %-7s %8s  %s\n",
            "item", "claim", "live m (sd)", "dep m (sd)", "rival", "d_rival", "ok"))
ok_a <- TRUE
for (i in seq_len(nrow(live))) {
    it <- live$item[i]; k <- CLAIM[[it]]
    dist <- abs(dep_stats$mean - live$mean[i]) + abs(dep_stats$sd - live$sd[i]) +
            ifelse(dep_stats$n == live$n[i], 0, 1)
    best <- order(dist)[1]; second <- order(dist)[2]
    pass <- dep_stats$col[best] == paste0("DASS", k)
    ok_a <- ok_a && pass
    cat(sprintf("%-11s %-7s %5.4f(%.4f) %5.4f(%.4f)   %-7s %8.4f  %s\n",
                it, paste0("DASS", k),
                live$mean[i], live$sd[i],
                dep_stats$mean[paste0("DASS", k) == dep_stats$col],
                dep_stats$sd[paste0("DASS", k) == dep_stats$col],
                dep_stats$col[second], dist[second],
                if (pass) "yes" else paste("NO -> nearest is", dep_stats$col[best])))
    if (!identical(live$n[i], dep_stats$n[paste0("DASS", k) == dep_stats$col]))
        cat(sprintf("    n mismatch: live %d vs deposit %d\n",
                    live$n[i], dep_stats$n[paste0("DASS", k) == dep_stats$col]))
}
cat(sprintf("all seven live items nearest their claimed column: %s\n", ok_a))

## ---- (b) subscale alphas ---------------------------------------------------
alpha <- function(M) {
    M <- M[complete.cases(M), , drop = FALSE]
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}
cat("\n-- (b) Cronbach's alpha of the canonical DASS-21 triples in this deposit --\n")
cat(sprintf("%-11s %9s %9s %8s\n", "subscale", "published", "observed", "diff"))
ok_b <- TRUE
for (nm in names(CANON)) {
    a <- alpha(D[, paste0("DASS", CANON[[nm]])])
    ok_b <- ok_b && abs(a - PUB_ALPHA[[nm]]) <= TOL_ALPHA
    cat(sprintf("%-11s %9.2f %9.4f %8.4f\n", nm, PUB_ALPHA[[nm]], a, a - PUB_ALPHA[[nm]]))
}
a_live <- {
    w <- tapply(d$resp, list(as.character(d$id), as.character(d$item)), mean)
    alpha(w[, names(CLAIM), drop = FALSE])
}
cat(sprintf("live wang2022_dass_anxiety table, alpha = %.4f (published anxiety 0.84)\n", a_live))
cat(sprintf("all three alphas within %.2f: %s\n", TOL_ALPHA, ok_b))

## ---- (c) the underpowered within-subscale test, for the record -------------
A <- D[, paste0("DASS", CANON$anxiety)]
C <- cor(A, use = "pairwise.complete.obs")
splits <- combn(7, 4, simplify = FALSE)
sep <- sapply(splits, function(g1) {
    g2 <- setdiff(1:7, g1)
    w <- c(C[g1, g1][upper.tri(C[g1, g1])], C[g2, g2][upper.tri(C[g2, g2])])
    mean(w) - mean(C[g1, g2])
})
canon_split <- which(sapply(splits, function(g) identical(sort(CANON$anxiety[g]), c(2,4,7,19))))
cat(sprintf("\n-- (c) within-anxiety facet split {2,4,7,19} vs {9,15,20}: rank %d of %d, separation %.4f (best %.4f) --\n",
            rank(-sep)[canon_split], length(sep), sep[canon_split], max(sep)))
cat("    Underpowered by design; NOT part of the verdict. See header.\n")

cat(if (ok_a && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
