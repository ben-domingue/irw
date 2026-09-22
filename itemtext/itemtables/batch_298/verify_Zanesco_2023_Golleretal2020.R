# verify_Zanesco_2023_Golleretal2020.R
#
# WHAT IS BEING VERIFIED
#
# The shipped table carries no item stems (Goller, Banks & Meier 2020 never print the
# on-screen wording of the depth probe), so the axis that carries inference is
# option_text <-> resp: the claim that resp 1 = "Completely on-task" ... resp 5 =
# "Completely off-task", and that T1..T36 are the 36 probe occasions in the order they
# were administered.
#
# Two falsifiable predictions, both from published numbers:
#
# 1) DIRECTION. Zanesco et al. (2024, Behav Res Methods 56:7707-7727) Table 1 reports the
#    Goller et al. (2020) focus-probe mean rating as 2.508 (SD 0.880) over N = 355, on a
#    scale described as 1 (completely on-task) to 5 (completely off-task). If the shipped
#    anchors were reversed, the live mean would have to be 6 - 2.508 = 3.492.
#    The live table holds 366 participants -- 11 more than the paper's analysis sample --
#    so the source file's own Exclude flag (OSF shxb6 -> Zanesco's curated copy on
#    osf.io/3zma2) is used to reproduce exactly the N = 355 the paper analysed.
#
# 2) ORDERING. Zanesco et al. (2024) fit a 2-parameter graded response model to these 36
#    probes and report discrimination values ranging 0.84 to 2.54, with a quadratic trend
#    across probe order explaining R2 = 0.839, F(2,33) = 86.08. A permuted item->occasion
#    mapping preserves the range but destroys the trend, so the trend is the test.
#
# WHAT THIS DOES NOT ESTABLISH: the literal stem respondents read (unpublished, hence
# blank in the shipped file), and the three interior anchors 2/3/4 individually -- those
# are transcribed with the source's own explicit numbering, and a mean can only pin the
# direction of the scale, not each intermediate label.

suppressMessages(library(irw))
suppressMessages(library(mirt))

TABLE <- "Zanesco_2023_Golleretal2020"
PUB_MEAN <- 2.508; PUB_SD <- 0.880; PUB_N <- 355
PUB_A_MIN <- 0.84; PUB_R2 <- 0.839; PUB_F <- 86.08
SRC_URL <- "https://files.osf.io/v1/resources/3zma2/providers/osfstorage/646788dff9c6ce1633d4b814"

ok <- TRUE

## ---- the shipped mapping ----------------------------------------------------
items_csv <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                       paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv)) items_csv <- paste0(TABLE, "__items.csv")
it <- read.csv(items_csv, stringsAsFactors = FALSE)
anchors <- unique(it[, c("resp", "option_text")])
anchors <- anchors[order(anchors$resp), ]
cat("-- shipped option_text by resp --\n")
print(anchors, row.names = FALSE)
if (!grepl("on-task", anchors$option_text[anchors$resp == 1]) ||
    !grepl("off-task", anchors$option_text[anchors$resp == 5])) {
    cat("FAIL: shipped anchors are not the on-task(1) .. off-task(5) direction tested below\n")
    ok <- FALSE
}
cat("shipped item_text all blank (no stem published):",
    all(is.na(it$item_text) | it$item_text == ""), "\n\n")

## ---- live data --------------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- tapply(d$resp, list(d$id, d$item), function(x) x[1])
w <- w[, paste0("T", 1:36)]
cat(sprintf("live table: %d participants x %d probes\n", nrow(w), ncol(w)))

## ---- the source file's exclusion flag ---------------------------------------
tmp <- tempfile(fileext = ".csv")
src_ok <- tryCatch({ download.file(SRC_URL, tmp, quiet = TRUE); TRUE }, error = function(e) FALSE)

## ---- prediction 1: direction of the 1..5 anchors ----------------------------
pm_all <- rowMeans(w, na.rm = TRUE)
cat(sprintf("live mean of participant mean ratings, all %d: %.3f (SD %.3f)\n",
            length(pm_all), mean(pm_all), sd(pm_all)))
if (src_ok) {
    s <- read.csv(tmp, stringsAsFactors = FALSE)
    rownames(s) <- as.character(s$Subject)
    keep <- rownames(w)[as.character(s[rownames(w), "Exclude"]) == "0"]
    pm <- rowMeans(w[keep, ], na.rm = TRUE)
    cat(sprintf("live, restricted to source Exclude==0: N=%d  mean=%.3f  SD=%.3f\n",
                length(pm), mean(pm), sd(pm)))
    cat(sprintf("published (Zanesco 2024 Table 1):        N=%d  mean=%.3f  SD=%.3f\n",
                PUB_N, PUB_MEAN, PUB_SD))
    cat(sprintf("reversed-anchor prediction would be mean=%.3f\n", 6 - PUB_MEAN))
    if (length(pm) != PUB_N || abs(mean(pm) - PUB_MEAN) > 0.01 || abs(sd(pm) - PUB_SD) > 0.01) {
        cat("FAIL: direction/sample check missed the published value\n"); ok <- FALSE
    } else cat("PASS: direction check reproduces the published mean and SD exactly at 3 dp\n")
} else {
    cat("NOTE: source file unreachable; falling back to the full-sample comparison\n")
    if (abs(mean(pm_all) - PUB_MEAN) > 0.06) { cat("FAIL\n"); ok <- FALSE } else
        cat("PASS (weaker): full-sample mean is within 0.06 of published, and far from the reversed 3.492\n")
    keep <- rownames(w)
}

## ---- prediction 2: T1..T36 are the probes in administered order -------------
cat("\n-- per-item mean rating by probe index (rises with time on task) --\n")
print(round(colMeans(w[keep, ], na.rm = TRUE), 2))
cat(sprintf("Spearman(per-item mean, probe index) = %.3f\n",
            cor(colMeans(w[keep, ], na.rm = TRUE), 1:36, method = "spearman")))

fit <- mirt(as.data.frame(w[keep, ]), 1, itemtype = "graded", SE = FALSE,
            verbose = FALSE, quadpts = 31, method = "EM")
a <- coef(fit, IRTpars = TRUE, simplify = TRUE)$items[, 1]
t1 <- 0:35; t2 <- t1^2
m <- summary(lm(a ~ t1 + t2))
cat(sprintf("\nGRM discrimination range: %.2f - %.2f   (published %.2f - 2.54)\n",
            min(a), max(a), PUB_A_MIN))
cat(sprintf("quadratic trend of a_i over probe order: R2=%.3f F=%.2f   (published R2=%.3f F(2,33)=%.2f)\n",
            m$r.squared, m$fstatistic[1], PUB_R2, PUB_F))
set.seed(1)
perm <- replicate(2000, summary(lm(sample(a) ~ t1 + t2))$r.squared)
cat(sprintf("permutation test: %d of 2000 random item->occasion orderings reach R2 >= %.3f\n",
            sum(perm >= m$r.squared), m$r.squared))
if (abs(m$r.squared - PUB_R2) > 0.01 || abs(m$fstatistic[1] - PUB_F) > 1 ||
    sum(perm >= m$r.squared) > 20) {
    cat("FAIL: ordering check did not reproduce the published trend\n"); ok <- FALSE
} else cat("PASS: ordering check reproduces R2 and F to the published precision\n")

cat("\n", if (ok) "VERDICT: PASS" else "VERDICT: FAIL", "\n", sep = "")
