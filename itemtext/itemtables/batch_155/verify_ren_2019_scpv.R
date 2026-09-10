# verify_ren_2019_scpv.R -- Step 5b re-runnable evidence.
#
# CLAIM UNDER TEST: item code SCPVn carries the wording of item n of the Fast Track
# Project's Social Competence Scale - Parent Version (CPPRG 1995). The study's own
# paper (Ren et al. 2019, Front. Psychol. 10:2550) never reproduces the items, so the
# code->wording tie is by the canonical form's printed numbering 1..12.
#
# Two falsifiable predictions, neither of which survives a permutation of item_text:
#
#  (A) SUBSCALE MEMBERSHIP. The Fast Track technical report fixes the split as
#      Emotional Regulation = items 1,2,3,5,6,8 and Prosocial/Communication =
#      items 4,7,9,10,11,12. Ren et al.'s own Table 5 reports r = 0.706 between those
#      two subscale scores IN THIS SAMPLE. So computing the two subscale means from
#      the live table under the canonical membership must reproduce 0.706.
#
#  (B) ITEM-MEAN PROFILE, CROSS-SAMPLE. The Year-3 technical report (Corrigan 2003,
#      scp3tech.pdf) prints per-item means for the US normative sample on the
#      original 0-4 metric. Ren et al. administered the same 12 items on 1-5, so
#      +1 puts them on a common metric. The two profiles should track.
#
# Neither route separates every item from every other -- see the ambiguity list the
# script prints at the end. The recorded status is PARTIAL, not VERIFIED.

suppressMessages(library(irw))
suppressMessages(library(stats))

TABLE <- "ren_2019_scpv"
ITEMS <- paste0("SCPV", 1:12)
EMO   <- paste0("SCPV", c(1, 2, 3, 5, 6, 8))          # Emotional Regulation
PRO   <- setdiff(ITEMS, EMO)                           # Prosocial/Communication

PUBLISHED_SUBSCALE_R <- 0.706   # Ren et al. 2019 Table 5, rows 5 x 6
TOL_R <- 0.02

# Corrigan (2003) Table VI, Cohort 1 Year 3 normative sample, items 1..12, 0-4 metric.
FT_NORM <- c(1.96, 1.89, 2.25, 2.27, 2.30, 2.66, 2.92, 2.09, 2.95, 3.27, 2.64, 2.42)
MIN_PEARSON <- 0.80

d <- irw::irw_fetch(TABLE)
d <- d[d$item %in% ITEMS, ]

# --- wide matrix, one row per respondent -------------------------------------
ids <- sort(unique(d$id))
W <- matrix(NA_real_, nrow = length(ids), ncol = length(ITEMS),
            dimnames = list(as.character(ids), ITEMS))
W[cbind(match(as.character(d$id), rownames(W)), match(d$item, ITEMS))] <- as.numeric(d$resp)

sub_r <- function(g) {
    o <- setdiff(ITEMS, g)
    suppressWarnings(cor(rowMeans(W[, g, drop = FALSE], na.rm = TRUE),
                         rowMeans(W[, o, drop = FALSE], na.rm = TRUE),
                         use = "complete.obs"))
}

# --- (A) subscale membership --------------------------------------------------
cat("=== (A) subscale correlation, canonical membership ===\n")
cat("  EmoReg = ", paste(EMO, collapse = " "), "\n", sep = "")
cat("  ProSoc = ", paste(PRO, collapse = " "), "\n", sep = "")
r_hyp <- sub_r(EMO)
cat(sprintf("  observed r(EmoReg, ProSoc) = %.4f   published (Ren Table 5) = %.3f   diff = %.4f\n",
            r_hyp, PUBLISHED_SUBSCALE_R, r_hyp - PUBLISHED_SUBSCALE_R))

all_splits <- combn(ITEMS, 6, simplify = FALSE)
rs <- vapply(all_splits, sub_r, numeric(1))
rk <- mean(rank(abs(rs - PUBLISHED_SUBSCALE_R))[vapply(all_splits, function(g) setequal(g, EMO), logical(1))])
cat(sprintf("  across all %d six/six splits r ranges %.3f-%.3f; the canonical split ranks %.1f closest to 0.706\n",
            length(rs), min(rs), max(rs), rk))

# --- (B) cross-sample item-mean profile ---------------------------------------
cat("\n=== (B) item-mean profile vs Fast Track Year-3 normative sample ===\n")
obs <- vapply(ITEMS, function(i) mean(as.numeric(d$resp[d$item == i]), na.rm = TRUE), numeric(1))
ft1 <- FT_NORM + 1   # 0-4 -> 1-5
cat(sprintf("%-8s %14s %10s\n", "item", "FastTrack+1", "live"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-8s %14.2f %10.2f\n", ITEMS[i], ft1[i], obs[i]))
pear <- cor(ft1, obs); spear <- cor(ft1, obs, method = "spearman")
cat(sprintf("\n  Pearson = %.3f   Spearman = %.3f   (threshold %.2f)\n", pear, spear, MIN_PEARSON))

# how discriminating is (B)? count transpositions that fit at least as well
worse <- 0; amb <- character(0)
for (i in 1:11) for (j in (i + 1):12) {
    v <- obs; v[c(i, j)] <- v[c(j, i)]
    if (cor(ft1, v) >= pear) amb <- c(amb, sprintf("%d<->%d", i, j)) else worse <- worse + 1
}
cat(sprintf("  %d of 66 single transpositions of item_text are strictly worse than the shipped mapping\n", worse))

cat("\n=== what this does NOT establish ===\n")
cat("  These transpositions fit as well or better, so the routes do not separate them:\n    ",
    paste(amb, collapse = ", "), "\n", sep = "")
cat("  (A) also fails to exclude 6<->12: that swap gives r = ",
    sprintf("%.4f", sub_r(union(setdiff(EMO, "SCPV6"), "SCPV12"))),
    ", marginally nearer 0.706 than the canonical 0.7017.\n", sep = "")
cat("  Hence PARTIAL: subscale membership and the overall difficulty ordering are pinned;\n")
cat("  the exact order within the Emotional-Regulation block is not.\n\n")

ok <- abs(r_hyp - PUBLISHED_SUBSCALE_R) <= TOL_R && pear >= MIN_PEARSON
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
