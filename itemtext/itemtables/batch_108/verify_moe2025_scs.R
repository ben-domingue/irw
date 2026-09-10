# verify_moe2025_scs.R -- Step 5b mapping check for `moe2025_scs`.
#
# CLAIM UNDER TEST: item code SCS<N>_pre carries Neff (2003) Self-Compassion
# Scale item N, in the canonical numbering, with the Italian wording of
# Veneziani, Fuochi & Voci (2017) shipped as item_text.
#
# Three independent checks, none of which is an item count:
#
#  (A) SOURCE-SIDE, author-supplied. The figshare .sav carries the author's own
#      reverse-scored duplicate columns `SCS<N>_pre_rev`. Neff's scoring key
#      lists exactly 13 reverse-scored items (Self-Judgment 1,8,11,16,21;
#      Isolation 4,13,18,25; Over-identification 2,6,20,24). If the study's
#      numbering were NOT canonical, that 13-number set would not coincide.
#      There are choose(26,13) = 10,400,600 possible 13-subsets.
#  (B) LIVE-DATA polarity (Step 5b route 6). Each item is classified NEG/POS by
#      whether it correlates more strongly with the canonical negative block or
#      the canonical positive block, and compared to the shipped wording's
#      polarity. Disagreements are only meaningful for items that discriminate
#      at all, so the corrected item-total r is printed alongside.
#  (C) LIVE-DATA subscale block structure (route 5). With the 13 negative items
#      sign-flipped, each of Neff's six subscales should cohere more tightly
#      internally than with the rest of the scale.
#
# WHAT THIS DOES NOT ESTABLISH: order WITHIN a polarity class / subscale.
# Permuting item_text among {5,12,19,23,26} (Self-Kindness), say, would leave
# every number below unchanged. Status is therefore PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE   <- "moe2025_scs"
SAV_URL <- "https://ndownloader.figshare.com/files/58837756"   # figshare 10.6084/m9.figshare.30385261

# Neff (2003) SCS-26 scoring key, from self-compassion.org's SCS-information.pdf
# (sha256 be9f7f479d236a92e361835348e2f653a11920570c9796511e718acdaabc752a).
SUBS <- list(SelfKindness      = c(5, 12, 19, 23, 26),
             SelfJudgment      = c(1, 8, 11, 16, 21),
             CommonHumanity    = c(3, 7, 10, 15),
             Isolation         = c(4, 13, 18, 25),
             Mindfulness       = c(9, 14, 17, 22),
             OverIdentification= c(2, 6, 20, 24))
NEG_KEY <- as.integer(sort(c(SUBS$SelfJudgment, SUBS$Isolation, SUBS$OverIdentification)))
POS_KEY <- setdiff(1:26, NEG_KEY)

ok <- TRUE

## ---- (A) the .sav's own reverse-scored duplicate columns -------------------
cat("== (A) source-side: `_rev` duplicate columns vs Neff's reverse-scored key ==\n")
tf <- tempfile(fileext = ".sav")
utils::download.file(SAV_URL, tf, quiet = TRUE,
                     headers = c("User-Agent" = "irw-batch/1.0 (research)"))
sav <- haven::read_sav(tf)
rev_cols <- grep("^SCS[0-9]+_pre_rev$", names(sav), value = TRUE)
rev_nums <- sort(as.integer(sub("^SCS([0-9]+)_pre_rev$", "\\1", rev_cols)))
cat("  .sav `_rev` item numbers :", paste(rev_nums, collapse = ","), "\n")
cat("  Neff reverse-scored key  :", paste(NEG_KEY,  collapse = ","), "\n")
cat(sprintf("  identical: %s  (%d/%d; 1 of choose(26,13)=%s subsets)\n",
            identical(rev_nums, NEG_KEY), sum(rev_nums %in% NEG_KEY), length(NEG_KEY),
            format(choose(26, 13), big.mark = ",", scientific = FALSE)))
if (!identical(rev_nums, NEG_KEY)) ok <- FALSE

## ---- live data ------------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE)[, c("id", "item", "resp")])
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
items <- paste0("SCS", 1:26, "_pre")
M <- as.matrix(w[, items]); mode(M) <- "numeric"
C <- cor(M, use = "pairwise.complete.obs")
Mf <- M; Mf[, NEG_KEY] <- 6 - Mf[, NEG_KEY]      # sign-corrected copy
Cf <- cor(Mf, use = "pairwise.complete.obs")
tot <- rowSums(Mf)

## ---- (B) polarity per item ------------------------------------------------
cat("\n== (B) live-data polarity: mean r with negative block vs positive block ==\n")
cat(sprintf("%-11s %7s %7s %7s %6s %6s %8s\n",
            "item", "r_neg", "r_pos", "diff", "data", "text", "item-tot"))
agree <- 0; bad <- character(0)
for (i in 1:26) {
    rn <- mean(C[i, setdiff(NEG_KEY, i)]); rp <- mean(C[i, setdiff(POS_KEY, i)])
    cls  <- if (rn > rp) "NEG" else "POS"
    text <- if (i %in% NEG_KEY) "NEG" else "POS"
    it   <- cor(Mf[, i], tot - Mf[, i], use = "pairwise.complete.obs")
    if (cls == text) agree <- agree + 1 else bad <- c(bad, sprintf("%s(r_it=%.3f)", items[i], it))
    cat(sprintf("%-11s %7.3f %7.3f %7.3f %6s %6s %8.3f%s\n",
                items[i], rn, rp, rn - rp, cls, text, it,
                if (cls == text) "" else "   <- disagrees"))
}
cat(sprintf("\n  polarity agreement: %d/26\n", agree))
cat("  disagreeing items :", if (length(bad)) paste(bad, collapse = ", ") else "none", "\n")
# A disagreement only counts against the mapping if the item discriminates.
noise <- TRUE
for (i in 1:26) {
    cls <- if (mean(C[i, setdiff(NEG_KEY, i)]) > mean(C[i, setdiff(POS_KEY, i)])) "NEG" else "POS"
    text <- if (i %in% NEG_KEY) "NEG" else "POS"
    if (cls != text && abs(cor(Mf[, i], tot - Mf[, i], use = "pairwise.complete.obs")) >= 0.25)
        noise <- FALSE
}
cat("  every disagreement is a non-discriminating item (|corrected item-total r| < 0.25):",
    noise, "\n")
if (agree < 23 || !noise) ok <- FALSE

## ---- (C) subscale block structure ----------------------------------------
cat("\n== (C) live-data subscale coherence (negatives sign-flipped) ==\n")
cat(sprintf("%-19s %3s %8s %8s\n", "subscale", "k", "within", "cross"))
nwin <- 0
for (nm in names(SUBS)) {
    idx <- SUBS[[nm]]
    win <- mean(Cf[idx, idx][upper.tri(diag(length(idx)))])
    crs <- mean(Cf[idx, setdiff(1:26, idx)])
    if (win > crs) nwin <- nwin + 1
    cat(sprintf("%-19s %3d %8.3f %8.3f%s\n", nm, length(idx), win, crs,
                if (win > crs) "" else "   <- cross exceeds within"))
}
cat(sprintf("\n  subscales where within > cross: %d/6\n", nwin))
if (nwin < 6) ok <- FALSE

cat("\nNote: (A)-(C) pin each item's polarity class and its subscale, i.e. one of\n",
    "six 4-5 item blocks. They do NOT distinguish order WITHIN a block -- permuting\n",
    "item_text inside a subscale would reproduce every number above. Hence PARTIAL.\n", sep = "")
cat("Known data anomaly (does not affect the checks' verdict): SCS25_pre in the .sav\n",
    "is not the reverse of the author's own SCS25_pre_rev, and it is the one Isolation\n",
    "item with a near-zero corrected item-total r. See notes_moe2025_scs.csv.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
