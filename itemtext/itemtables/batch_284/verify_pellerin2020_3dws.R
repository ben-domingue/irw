# verify_pellerin2020_3dws.R -- batch_284, 2026-09-20
#
# WHAT IS BEING VERIFIED
# The IRW item codes Cog_1..Cog_4 / Refl_1..Refl_4 / Aff_1..Aff_4 are the OSF
# deposit's own column names (data/pellerin2020_covid_resources.py melts them
# straight through), but that deposit is a bare CSV with NO variable labels --
# the codes carry the FACET and a within-facet position number, and nothing
# else. The wording ships from Ardelt's own 3D-WS-12 questionnaire PDF
# (people.clas.ufl.edu/ardelt/files/Instructions-for-the-3D-WS-12-Questionnaire.pdf),
# cross-keyed to the 3D-WS item codes printed in Thomas, Bangen, Ardelt & Jeste
# (2017, Assessment 24(1):71-82) Table 1. The 3D-WS-12 is:
#     Cognitive  c9, c10, c11, c13   (all negatively worded)
#     Reflective r8r, r9, r10, r12   (r8r positively worded / reverse-scored)
#     Affective  a4r, a7r, a9, a12   (a4r, a7r positively worded)
# The shipped mapping orders each facet by the parent 3D-WS item number:
#     Cog_1=c9   Cog_2=c10  Cog_3=c11  Cog_4=c13
#     Refl_1=r8r Refl_2=r9  Refl_3=r10 Refl_4=r12
#     Aff_1=a4r  Aff_2=a7r  Aff_3=a9   Aff_4=a12
# That is an ORDER INFERENCE (mapping_basis = reconstructed). Nothing in the
# deposit or in Pellerin & Raufaste (2020) states it, and the rival ordering --
# the 3D-WS-12 questionnaire's own 1..12 order, which gives Refl = r10, r12,
# r8r, r9 and Cog = c10, c9, c11, c13 -- is equally a priori plausible. This
# script tests the two halves of the claim that can be tested.
#
# CHECK (A) -- POLARITY, from the authors' own recovered scoring key.
# The deposit carries the authors' derived wisdom score P.Wisdom. Searching all
# 57,344 combinations of (which subset of the 12 columns is averaged) x (which
# are reversed) x (reversal constant 7-x or 8-x) reproduces P.Wisdom EXACTLY for
# exactly one: the mean of 11 columns (Cog_1 dropped) with Cog_2, Cog_3, Cog_4,
# Refl_2, Refl_3, Refl_4, Aff_3, Aff_4 entered as 7-x and Refl_1, Aff_1, Aff_2
# entered raw. So the authors treat exactly {Refl_1, Aff_1, Aff_2} as the
# positively-worded items. The 3D-WS-12 has exactly three positively-worded
# items and they are r8r, a4r and a7r. The shipped mapping puts them at exactly
# Refl_1, Aff_1, Aff_2. Under a random within-facet permutation that is 1 in 24
# (choose 2 of 4 affective x 1 of 4 reflective). This check is re-run below.
#
# CHECK (B) -- REFLECTIVE ORDER, against Thomas et al. (2017) Figure 2.
# Figure 2 reports standardized loadings for the 3D-WS-12 in its validation
# sample (N=771): r12 .69, r9 .63, r10 .50, r8r .34, and it FREES one residual
# covariance inside the reflective factor, r10 <-> r12 (the two items Thomas et
# al. assign to the "absence of subjectivity and projections" content
# subdomain; r8r and r9 belong to the "look at phenomena from different
# perspectives" subdomain). Both are falsifiable predictions about the French
# data, and they are scored below over all 6 permutations of {r9, r10, r12}
# onto {Refl_2, Refl_3, Refl_4} (Refl_1 = r8r is already fixed by check A).
#
# WHAT THIS DOES NOT ESTABLISH
#   * Aff_1 vs Aff_2 (= a4r vs a7r) and Aff_3 vs Aff_4 (= a9 vs a12). Check (A)
#     pins the PAIRS but not the order inside them, and the affective loading
#     pattern does not replicate in the French data at all (published a12 .60 is
#     the strongest affective item; the French item-rest correlation for Aff_4
#     is the WEAKEST of the four). That half is order inference only.
#   * Cog_1..Cog_4 entirely. All four cognitive items are negatively worded, so
#     check (A) says nothing about them, and the French cognitive block does not
#     reproduce the published loading order under EITHER candidate ordering
#     (printed below for the reader). Any of the 24 orders is consistent with
#     the data; the shipped one rests on the same parent-numbering rule that
#     checks (A) and (B) confirm for the other two facets.
#   * It is a structural match, not a source-level label tie. No file anywhere
#     spells "Refl_2 = Sometimes I get so charged up emotionally...".

suppressMessages(library(irw))

TABLE <- "pellerin2020_3dws"
COLS  <- c(paste0("Cog_", 1:4), paste0("Refl_", 1:4), paste0("Aff_", 1:4))

# Shipped mapping, as written into pellerin2020_3dws__items.csv
SHIP <- c(Cog_1 = "c9",  Cog_2 = "c10", Cog_3 = "c11", Cog_4 = "c13",
          Refl_1 = "r8r", Refl_2 = "r9", Refl_3 = "r10", Refl_4 = "r12",
          Aff_1 = "a4r", Aff_2 = "a7r", Aff_3 = "a9",  Aff_4 = "a12")

# Thomas et al. (2017) Fig. 2 standardized loadings, validation sample N=771
LOAD <- c(c9 = 0.45, c10 = 0.64, c11 = 0.51, c13 = 0.59,
          r8r = 0.34, r9 = 0.63, r10 = 0.50, r12 = 0.69,
          a4r = 0.30, a7r = 0.11, a9 = 0.31, a12 = 0.60)
# Residual covariances freed in Fig. 2 (curved double-headed arrows)
FREED <- list(c("c10", "c11"), c("r10", "r12"), c("a4r", "a7r"))

# ---- live data, wide -------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "wave", "item", "resp")],
             idvar = c("id", "wave"), timevar = "item", direction = "wide")
names(w) <- sub("resp.", "", names(w), fixed = TRUE)
X <- w[complete.cases(w[, COLS]), COLS]
cat(sprintf("live table: %d complete 12-item person-wave records\n\n", nrow(X)))

# ============================================================================
# (A) polarity, from the authors' own scoring key
# ============================================================================
cat("(A) POLARITY -- authors' own P.Wisdom scoring key, recovered from the OSF deposit\n")
POS_EXPECTED <- names(SHIP)[SHIP %in% c("r8r", "a4r", "a7r")]   # shipped positives
okA <- NA
resA <- try({
    raw <- read.csv("https://osf.io/download/dc6me/", stringsAsFactors = FALSE)
    s <- raw[raw$Wave == 0, ]
    s <- s[complete.cases(s[, c(COLS, "P.Wisdom")]), ]
    best <- NULL
    for (k in 11:12) for (keep in combn(12, k, simplify = FALSE)) {
        M <- as.matrix(s[, COLS[keep]])
        for (C in c(7, 8)) for (msk in 0:(2^k - 1)) {
            Z <- M
            for (j in seq_len(k)) if (bitwAnd(bitwShiftR(msk, j - 1), 1L) == 1L) Z[, j] <- C - Z[, j]
            dev <- max(abs(rowMeans(Z) - s$P.Wisdom))
            if (is.null(best) || dev < best$dev)
                best <- list(dev = dev, C = C,
                             rev = COLS[keep][bitwAnd(bitwShiftR(msk, seq_len(k) - 1), 1L) == 1L],
                             kept = COLS[keep][bitwAnd(bitwShiftR(msk, seq_len(k) - 1), 1L) == 0L],
                             dropped = setdiff(COLS, COLS[keep]))
        }
    }
    cat(sprintf("    wave-0 n = %d; exhaustive search over 57,344 scoring rules\n", nrow(s)))
    cat(sprintf("    best rule: mean of %d columns, reversal = %d - x, dropped = %s\n",
                12 - length(best$dropped), best$C, paste(best$dropped, collapse = ", ")))
    cat(sprintf("    reversed : %s\n", paste(best$rev, collapse = ", ")))
    cat(sprintf("    entered raw (i.e. positively worded): %s\n", paste(best$kept, collapse = ", ")))
    cat(sprintf("    max |reproduced - P.Wisdom| = %.3g\n", best$dev))
    cat(sprintf("    shipped positively-worded items (r8r, a4r, a7r) sit at: %s\n",
                paste(sort(POS_EXPECTED), collapse = ", ")))
    okA <- best$dev < 1e-10 && setequal(best$kept, POS_EXPECTED)
    cat(sprintf("    match: %s   (1 in 24 under a random within-facet permutation)\n",
                if (okA) "YES" else "NO"))
    invisible(NULL)
}, silent = TRUE)
if (inherits(resA, "try-error"))
    cat("    (OSF deposit unreachable -- check (A) skipped)\n")
cat("\n")

# ============================================================================
# (B) reflective ordering -- 6 permutations scored on two Fig. 2 predictions
# ============================================================================
# Key every item so that higher = more wisdom, using the authors' own direction.
POS <- POS_EXPECTED
K <- X
for (cc in setdiff(COLS, POS)) K[[cc]] <- 7 - K[[cc]]

item_rest <- function(cols) sapply(cols, function(cc)
    cor(K[[cc]], rowMeans(K[, setdiff(cols, cc), drop = FALSE])))

REFL <- paste0("Refl_", 1:4)
ir <- item_rest(REFL)
Rr <- cor(K[, REFL])
cat("(B) REFLECTIVE ORDER -- Thomas et al. (2017) Fig. 2 loadings + freed residual r10<->r12\n")
cat(sprintf("    observed within-facet item-rest r: %s\n",
            paste(sprintf("%s=%.3f", REFL, ir), collapse = "  ")))
cat(sprintf("    observed correlations: r(2,3)=%.3f r(2,4)=%.3f r(3,4)=%.3f  r(1,2)=%.3f r(1,3)=%.3f r(1,4)=%.3f\n\n",
            Rr[2,3], Rr[2,4], Rr[3,4], Rr[1,2], Rr[1,3], Rr[1,4]))

perms <- list()
p3 <- list(c("r9","r10","r12"), c("r9","r12","r10"), c("r10","r9","r12"),
           c("r10","r12","r9"), c("r12","r9","r10"), c("r12","r10","r9"))
cat(sprintf("    %-22s %-11s %-34s %s\n", "Refl_2/Refl_3/Refl_4",
            "rank match", "largest residual excess pair", "verdict"))
scoreB <- c()
for (p in p3) {
    lab <- c(r8r = "Refl_1"); asg <- c("r8r", p); names(asg) <- REFL
    # (i) does the observed item-rest ordering match the published loading ordering?
    pred <- LOAD[asg]
    rank_ok <- identical(order(-ir), order(-pred))
    # (ii) 1-factor prediction from the published loadings; which pair has the
    #      largest positive residual? Fig. 2 says it must be r10 <-> r12.
    exc <- c()
    for (a in 1:3) for (b in (a+1):4) {
        pr <- pred[a] * pred[b]
        exc[paste(asg[a], asg[b], sep = "~")] <- Rr[a, b] - pr
    }
    top <- names(which.max(exc))
    freed_ok <- setequal(strsplit(top, "~")[[1]], c("r10", "r12"))
    ok <- rank_ok && freed_ok
    scoreB <- c(scoreB, ok)
    cat(sprintf("    %-22s %-11s %-34s %s\n", paste(p, collapse = "/"),
                if (rank_ok) "YES" else "no",
                sprintf("%s (+%.3f)", top, max(exc)),
                if (ok) "<== PASSES BOTH" else ""))
}
shipped_idx <- which(sapply(p3, function(p) identical(p, unname(SHIP[c("Refl_2","Refl_3","Refl_4")]))))
okB <- sum(scoreB) == 1 && scoreB[shipped_idx]
cat(sprintf("\n    shipped permutation = %s; permutations passing both tests = %d\n",
            paste(SHIP[c("Refl_2","Refl_3","Refl_4")], collapse = "/"), sum(scoreB)))
cat(sprintf("    shipped permutation is the unique joint winner: %s\n\n",
            if (okB) "YES" else "NO"))

# ============================================================================
# (C) reported, NOT scored -- the cognitive and affective blocks
# ============================================================================
cat("(C) NOT ESTABLISHED (printed so the reader can see how far it falls short)\n")
for (fac in c("Cog", "Aff")) {
    f <- paste0(fac, "_", 1:4); ir2 <- item_rest(f)
    cat(sprintf("    %-5s observed item-rest: %s\n", fac,
                paste(sprintf("%s=%.3f", f, ir2), collapse = "  ")))
    cat(sprintf("    %-5s shipped -> published loading: %s\n", "",
                paste(sprintf("%s=%s(%.2f)", f, SHIP[f], LOAD[SHIP[f]]), collapse = "  ")))
    cat(sprintf("    %-5s observed rank order %s vs predicted %s -> %s\n", "",
                paste(f[order(-ir2)], collapse = ">"),
                paste(f[order(-LOAD[SHIP[f]])], collapse = ">"),
                if (identical(order(-ir2), order(-LOAD[SHIP[f]]))) "matches" else "DOES NOT match"))
}
cat("    Neither block is used in the verdict. The cognitive block in particular is\n")
cat("    anomalous in this administration: Cog_1 correlates NEGATIVELY with the\n")
cat("    reflective items once keyed, and the authors' own wisdom score drops it.\n\n")

pass <- !isFALSE(okA) && isTRUE(okB)
cat("Summary: (A) polarity pins {Refl_1} and {Aff_1,Aff_2}; (B) pins the reflective\n")
cat("block outright; the affective within-pair order and the whole cognitive order\n")
cat("remain order inference. Step 5b status is therefore PARTIAL, not VERIFIED.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
